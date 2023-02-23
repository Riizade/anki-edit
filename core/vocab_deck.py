from __future__ import annotations
from core.dictionaries.general import BasicDictionary
from core.dictionaries.frequency import FrequencySource
from dataclasses import dataclass
from core.deepl import translate_to_english
import sys
from pathlib import Path

@dataclass(frozen=False, slots=True)
class VocabularyCard:
    priority: int # the order the card should show up when studying
    term: str # the term/word
    reading: str | None # the pronunciation of the word (mostly for Japanese furigana/Chinese pinyin)
    native_definitions: list[str] # definitions for the word in its own language
    english_definitions: list[str] # English definitions for the word
    machine_translated_definitions: list[str] # definitions for the word machine translated to English from the native_definitions

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
            definition = f"<h2>{dictionary.name}</h2>\n\n{entry.definition}"
            cards[entry.term].native_definitions.append(definition)

            # translate the definition and do the same
            machine_translated_definition = translate_to_english(entry.definition)
            mt_def = f"<h2>{dictionary.name}</h2>\n\n{machine_translated_definition}"
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
            definition = f"<h2>{dictionary.name}</h2>\n\n{entry.definition}"
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


def load_deck_into_anki(deck: VocabularyDeck):
    # TODO: implement
    raise NotImplementedError()

