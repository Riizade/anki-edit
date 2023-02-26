from __future__ import annotations
from core.dictionaries.general import BasicDictionary
from core.dictionaries.frequency import FrequencySource
from dataclasses import dataclass
import sys
from pathlib import Path
import core.anki_connect as anki_connect
from tqdm import tqdm
import genanki
import random
from typing import Tuple

@dataclass(frozen=True, slots=True)
class Definition:
    source: str
    definition: str

@dataclass(frozen=False, slots=True)
class VocabularyCard:
    priority: int # the order the card should show up when studying
    term: str # the term/word
    reading: str | None # the pronunciation of the word (mostly for Japanese furigana/Chinese pinyin)
    native_definitions: list[Definition] # definitions for the word in its own language
    english_definitions: list[Definition] # English definitions for the word
    machine_translated_definitions: list[Definition] # definitions for the word machine translated to English from the native_definitions

    @staticmethod
    def new() -> VocabularyCard:
        return VocabularyCard(
            priority=sys.maxsize,
            term="",
            reading=None,
            native_definitions=[],
            english_definitions=[],
            machine_translated_definitions=[],
        )

@dataclass(frozen=True, slots=True)
class VocabularyDeck:
    cards: list[VocabularyCard]

def load_deck_from_directory(path: Path) -> VocabularyDeck:
    print(f"loading deck from directory {path}", flush=True)
    native_dictionaries = []
    english_dictionaries = []
    frequency_sources = []

    print("loading native dictionaries", flush=True)
    for native_dir in (path / 'native').iterdir():
        native_dictionaries.append(BasicDictionary.from_dir(native_dir))

    print("loading english dictionaries", flush=True)
    for english_dir in (path / 'english').iterdir():
        english_dictionaries.append(BasicDictionary.from_dir(english_dir))

    print("loading frequency dictionaries", flush=True)
    for frequency_source in (path / 'frequency').iterdir():
        frequency_sources.append(FrequencySource.from_file(frequency_source))


    return create_deck(native_dictionaries=native_dictionaries, english_dictionaries=english_dictionaries, frequency_sources=frequency_sources)

def create_deck(native_dictionaries: list[BasicDictionary], english_dictionaries: list[BasicDictionary], frequency_sources: list[FrequencySource]) -> VocabularyDeck:
    print("creating deck from sources", flush=True)
    # cards by term
    cards: dict[str, VocabularyCard] = {}

    print("organizing native dictionaries", flush=True)
    for dictionary in native_dictionaries:
        # for each entry in a native dictionary
        for entry in dictionary.entries:
            # create the card if it does not already exist
            if entry.term not in cards:
                cards[entry.term] = VocabularyCard.new()
            # update the card's data
            cards[entry.term].term = entry.term
            cards[entry.term].reading = entry.reading,
            definition = Definition(dictionary.name, entry.definition)
            cards[entry.term].native_definitions.append(definition)

            # translate the definition and do the same
            # TODO: implement in a cost-effective way
            # machine_translated_definition = translate_to_english(entry.definition)
            # mt_def = Definition(dictionary.name, machine_translated_definition)
            # cards[entry.term].machine_translated_definitions.append(mt_def)

    print("organizing english dictionaries", flush=True)
    for dictionary in english_dictionaries:
        # for each entry in an English dictionary
        for entry in dictionary.entries:
            # create the card if it does not already exist
            if entry.term not in cards:
                cards[entry.term] = VocabularyCard.new()
            # update the card's data
            cards[entry.term].term = entry.term
            cards[entry.term].reading = entry.reading,
            definition = Definition(dictionary.name, entry.definition)
            cards[entry.term].english_definitions.append(definition)


    print("determining term frequency", flush=True)
    # dict from term -> frequency ranking
    frequency: dict[str, float] = {}
    # the number of sources contributing to the frequency ranking
    frequency_num_sources: dict[str, float] = {}
    for source in frequency_sources:
        for entry in source.entries:
            if entry.term not in frequency:
                frequency_num_sources[entry.term] = 1
                frequency[entry.term] = float(entry.ranking)
            else:
                # update num_sources
                num_sources = frequency_num_sources[entry.term] + 1
                # average the previous frequency with the new frequency
                previous_frequency = frequency[entry.term]
                new_frequency = float(entry.ranking)
                # this weights the previous frequency by the number of sources which contributed to it
                # e.g., if we had 2 sources before and we add a 3rd
                # (previous_freq * 2 + new_frequency) / 3
                averaged_frequency = ((previous_frequency * (num_sources-1)) + new_frequency) / float(num_sources)

                # save data back to maps
                frequency_num_sources[entry.term] = num_sources
                frequency[entry.term] = averaged_frequency


    # store the frequency rating inside the cards, if we can find one in the frequency list
    for term in cards.keys():
        if term in frequency:
            cards[term].priority = frequency[term]

    # sort the cards by their frequency rating (stored in .priority), then tiebreak by length, then lexicographically
    cards_list: list[VocabularyCard] = list(cards.values())
    cards_list.sort(key=lambda c: (c.priority, len(c.term), c.term), reverse=False)

    # replace the priority of the cards with their order in the list
    for i, card in enumerate(cards_list):
        card.priority = i + 1 # start at 1 (1-indexed)

    return VocabularyDeck(cards_list)


def create_anki_deck(deck: VocabularyDeck, deck_name: str) -> genanki.Deck:
    print("creating anki deck", flush=True)
    deck_id = random.randrange(1 << 30, 1 << 31)
    anki_deck = genanki.Deck(deck_id, deck_name, "a vocabulary memorization deck generated from several electronic dictionaries")
    notes = create_notes(deck, deck_name)
    print("adding cards to the deck", flush=True)
    for note in tqdm(notes):
        anki_deck.add_note(note)
    return anki_deck

# counts how many fields we need for each set of definitions
# returns max definitions for (native, english)
def count_definitions(deck: VocabularyDeck) -> Tuple[int, int]:
    max_native_definitions = 0
    max_english_definitions = 0
    for card in deck.cards:
        if len(card.native_definitions) > max_native_definitions:
            max_native_definitions = len(card.native_definitions)
        if len(card.english_definitions) > max_english_definitions:
            max_english_definitions = len(card.english_definitions)

    return (max_native_definitions, max_english_definitions)

def create_model(deck: VocabularyDeck, deck_name: str) -> genanki.Model:
    # enumerate the fields needed in the model to hold all of our definitions
    field_names: list[str] = ["order", "term", "reading"]

    # count max definitions per type
    (max_native_definitions, max_english_definitions) = count_definitions(deck)

    for i in range(max_native_definitions):
        field_names.append(f"native_definition_source_{i}")
        field_names.append(f"native_definition_text_{i}")
    for i in range(max_english_definitions):
        field_names.append(f"english_definition_source_{i}")
        field_names.append(f"english_definition_text_{i}")

    front_html = "<h1 class=\"term\">{{term}}</h1>\n"
    back_html = "<h1 class=\"term\">{{term}}</h1>\n<p>{{reading}}</p>\n"
    back_html += "<h1 class=\"section_header\">Native Definitions</h1>\n"
    for i in range(max_native_definitions):
        back_html += "<h2 class=\"source_name\">{{native_definition_source_" + str(i) + "}}</h2>\n"
        back_html += "<p class=\"definition\">{{native_definition_text_" + str(i) + "}}</p>\n"
    back_html += "<h1 class=\"section_header\">English Definitions</h1>\n"
    for i in range(max_english_definitions):
        back_html += "<h2 class=\"source_name\">{{english_definition_source_" + str(i) + "}}</h2>\n"
        back_html += "<p class=\"definition\">{{english_definition_text_" + str(i) + "}}</p>\n"

    # TODO: test if this css works as intended
    css = """
    .card {
        text-align: center;
    }

    .term {
        text-size: 45pt;
    }

    .section_header {}

    .source_name {}

    .definition {}
    """

    model_id = random.randrange(1 << 30, 1 << 31)
    return genanki.Model(
        model_id=model_id,
        name=f"{deck_name}::vocab",
        fields=[{"name": field} for field in field_names],
        templates=[
            {
                "name": f"{deck_name} Vocab Recogniton",
                "qfmt": front_html,
                "afmt": back_html,
            }
        ],
        css=css,
    )

# loads the top N cards into Anki (limit = N)
def create_notes(deck: VocabularyDeck, deck_name: str, limit: int = 40000) -> list[genanki.Note]:
    print("creating cards into anki", flush=True)

    # create the model for the notes
    model = create_model(deck, deck_name)

    # count max definitions per type
    # this is because genanki assigns fields by index, not by name
    # since every card has a different number of definitions, we need to track the offsets for the fields
    # we can use these numbers to determine how many empty fields to add to pad the field array to get to the correct offset
    (max_native_definitions, max_english_definitions) = count_definitions(deck)

    notes = []

    for card in tqdm(deck.cards[:limit]):
        # define common fields
        order = str(card.priority)
        term = card.term
        # TODO: at some point before this, card.reading becomes a (None,) for some decks, and I'm not sure why
        reading = card.reading if isinstance(card.reading, str) else ""

        # add definitions to an array for native definitions
        native_definition_fields = []
        for definition in card.native_definitions:
            native_definition_fields.append(definition.source)
            native_definition_fields.append(definition.definition)

        # pad the native definitions array to 2x the number of max possible definitions
        # (because there's one field for the source, and one for the definition, so the length of the array should be 2x the max possible)
        while len(native_definition_fields) < 2 * max_native_definitions:
            native_definition_fields.append("")

        # repeat the above process for english definitions (although the padding may not matter since no fields come after the english definition fields)
        english_definition_fields = []
        for definition in card.english_definitions:
            english_definition_fields.append(definition.source)
            english_definition_fields.append(definition.definition)
        while len(english_definition_fields) < 2 * max_english_definitions:
            english_definition_fields.append("")

        # combine all fields together
        fields = [order, term, reading]
        fields.extend(native_definition_fields)
        fields.extend(english_definition_fields)
        from core.utils import pprint_data
        for f in fields:
            if not isinstance(f, str):
                pprint_data(fields)
                pprint_data(f)

        notes.append(genanki.Note(
            model=model,
            fields=fields,
        ))

    return notes



