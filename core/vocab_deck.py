from __future__ import annotations
from core.dictionaries.general import BasicDictionary
from core.dictionaries.frequency import FrequencySource
from dataclasses import dataclass
from core.deepl import translate_to_english
import sys
from pathlib import Path
import core.anki_connect as anki_connect

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
    native_dictionaries = []
    english_dictionaries = []
    frequency_sources = []

    for native_dir in (path / 'native').iterdir():
        native_dictionaries.append(BasicDictionary.from_dir(native_dir))

    for english_dir in (path / 'english').iterdir():
        english_dictionaries.append(BasicDictionary.from_dir(english_dir))

    for frequency_source in (path / 'frequency').iterdir():
        frequency_sources.append(FrequencySource.from_file(frequency_source))


    return create_deck(native_dictionaries=native_dictionaries, english_dictionaries=english_dictionaries, frequency_sources=frequency_sources)

def create_deck(native_dictionaries: list[BasicDictionary], english_dictionaries: list[BasicDictionary], frequency_sources: list[FrequencySource]) -> VocabularyDeck:
    # cards by term
    cards: dict[str, VocabularyCard] = {}

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
            machine_translated_definition = translate_to_english(entry.definition)
            mt_def = Definition(dictionary.name, machine_translated_definition)
            cards[entry.term].machine_translated_definitions.append(mt_def)


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


def load_deck_into_anki(deck: VocabularyDeck, deck_name: str):
    anki_connect.create_deck(deck_name)
    create_model(deck, deck_name)
    load_notes_into_anki(deck, deck_name)

def create_model(deck: VocabularyDeck, deck_name: str):
    # count how many fields we need for each set of definitions
    max_native_definitions = 0
    max_english_definitions = 0
    max_machine_translated_definitions = 0
    for card in deck.cards:
        if len(card.native_definitions) > max_native_definitions:
            max_native_definitions = len(card.native_definitions)
        if len(card.english_definitions) > max_english_definitions:
            max_english_definitions = len(card.english_definitions)
        if len(card.machine_translated_definitions) > max_machine_translated_definitions:
            max_machine_translated_definitions = len(card.machine_translated_definitions)

    # enumerate the fields needed in the model to hold all of our definitions
    field_names: list[str] = ["order", "term", "reading"]

    for i in max_native_definitions:
        field_names.append(f"native_definition_source_{i}")
        field_names.append(f"native_definition_text_{i}")
    for i in max_english_definitions:
        field_names.append(f"english_definition_source_{i}")
        field_names.append(f"english_definition_text_{i}")
    for i in max_machine_translated_definitions:
        field_names.append(f"machine_translated_definition_source_{i}")
        field_names.append(f"machine_translated_definition_text_{i}")

    front_html = "<h1>{{term}}</h1>\n"
    back_html = "<h1>{{term}}[{{reading}}]</h1>\n"
    back_html += "<h1>Native Definitions</h1>\n"
    for i in max_native_definitions:
        back_html += "<h2>{{native_definition_source_" + i + "}}</h2>\n"
        back_html += "<p>{{hint:native_definition_text_" + i + "}}</p>\n"
    back_html += "<h1>English Definitions</h1>\n"
    for i in max_english_definitions:
        back_html += "<h2>{{english_definition_source_" + i + "}}</h2>\n"
        back_html += "<p>{{hint:english_definition_text_" + i + "}}</p>\n"
    back_html += "<h1>Machine-Translated Definitions</h1>\n"
    for i in max_machine_translated_definitions:
        back_html += "<h2>{{machine_translated_definition_source_" + i + "}}</h2>\n"
        back_html += "<p>{{hint:machine_translated_definition_text_" + i + "}}</p>\n"

    anki_connect.create_model({
        "modelName": f"{deck_name}::vocab",
        "inOrderFields": field_names,
        "isCloze": False,
        "cardTemplates": [
            {
                "Name": f"{deck_name} Vocab Recogniton",
                "Front": front_html,
                "Back": back_html,
            }
        ]
    })


def load_notes_into_anki(deck: VocabularyDeck, deck_name: str):
    model_name = f"{deck_name}::vocab"

    for card in deck.cards:
        fields = {
            "term": card.term,
            "order": card.priority,
        }

        if card.reading is not None:
            fields["reading"] = card.reading

        for i, definition in enumerate(card.native_definitions):
            fields[f"native_definition_source_{i}"] = definition.source
            fields[f"native_definition_text_{i}"] = definition.definition

        for i, definition in enumerate(card.english_definitions):
            fields[f"english_definition_source_{i}"] = definition.source
            fields[f"english_definition_text_{i}"] = definition.definition

        for i, definition in enumerate(card.machine_translated_definitions):
            fields[f"machine_translated_definition_source_{i}"] = definition.source
            fields[f"machine_translated_definition_text_{i}"] = definition.definition

        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": ["anki-edit", "generated"]
        }

