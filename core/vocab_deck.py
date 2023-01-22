from ankisync2 import Apkg
import genanki
import sys
import core.anki_connect as anki_connect
from core.utils import *
from dataclasses import dataclass
from typing import Callable
from core.example_sentences import sentence_map, ParallelSentence
from tqdm import tqdm

@dataclass(frozen=True)
class VocabInfo:
    vocab: str
    reading: str
    definitions: list[str]
    grammar: list[str]
    example_sentences: list[str]

@dataclass(frozen=True)
class CardReviewInfo:
    interval: int
    due: int
    reps: int
    lapses: int
    left: int

@dataclass(frozen=True)
class VocabCard:
    card_info: VocabInfo
    review_info: CardReviewInfo

@static_vars(sentence_index=None)
def get_example_sentences(vocab: str) -> list[ParallelSentence]:
    if get_example_sentences.sentence_index is None:
        get_example_sentences.sentence_index = sentence_map()

    return get_example_sentences.sentence_index.get(vocab, [])

def count_example_sentences(vocab: set[str]):
    print_utf8("counting example sentences...")
    count = 0
    for v in tqdm(vocab):
        if len(get_example_sentences(v)) > 0:
            count += 1
    total = len(v)
    print_utf8(f"number of examples with sentences {count}")
    print_utf8(f"number of examples without sentences {total - count}")
    print_utf8(f"total cards: {total}")

def read_decks():
    vocab_10k = read_deck("* Japanese Core 10k Recognition", note_info_10k_to_card)
    vocab_18k = read_deck("Japanese Core 18k Recognition", note_info_18k_to_card)

    set_10k = set([i.card_info.vocab for i in vocab_10k])
    set_18k = set([i.card_info.vocab for i in vocab_18k])

    total_number = len(set_10k.union(set_18k))
    set_10k_not_in_18k = len(set_10k.difference(set_18k))
    set_18k_not_in_10k = len(set_18k.difference(set_10k))
    intersection = len(set_10k.intersection(set_18k))
    print_utf8(f"total: {total_number}\n10k -> 18k missing: {set_10k_not_in_18k}\n18k -> 10k missing: {set_18k_not_in_10k}\nintersection: {intersection}")
    print_utf8(f"10k stats")
    count_example_sentences(set_10k)
    print_utf8(f"18k stats")
    count_example_sentences(set_18k)


def read_deck(name: str, conversion_function: Callable[[dict], VocabInfo | None]) -> list[VocabCard]:
    print_utf8(f"loading data from deck {name}...")
    infos = anki_connect.get_cards_and_notes_in_deck(name)

    print_utf8(f"reading deck {name}...")
    cards = [info_to_card(card_info, note_info, conversion_function) for card_info, note_info in tqdm(infos)]
    cards = [c for c in cards if c is not None]

    return cards

def info_to_card(card_info: dict, note_info: dict, conversion_function: Callable[[dict], VocabInfo | None]) -> VocabCard:
    vocab_info = conversion_function(note_info)
    review_info = card_info_to_review_info(card_info)
    return VocabCard(
        card_info=vocab_info,
        review_info=review_info
    )

def card_info_to_review_info(info: dict) -> CardReviewInfo:
    return CardReviewInfo(
        interval=info['interval'],
        due=info['due'],
        reps=info['reps'],
        lapses=info['lapses'],
        left=info['left'],
    )

def extract_value(fields: dict, field_name: str) -> str:
    if isinstance(fields[field_name], dict):
        return fields[field_name]['value']
    elif isinstance(fields[field_name], str):
        return fields[field_name]
    else:
        raise ValueError(f"cannot extract type from field {field_name} for info {fields}")

def note_info_10k_to_card(info: dict) -> VocabInfo | None:
    fields = info['fields']
    if 'Expression' in fields: # some cards in this deck are malformed and do not contain the same standard field set as the others
        vocab = extract_value(fields, 'Expression')
        reading = extract_value(fields, 'Reading')
        grammar = []
        example_sentences = []
        definitions = extract_value(fields, 'Meaning')
    else:
        vocab = extract_value(fields, 'vocab')
        reading = extract_value(fields, 'vocab-furigana')
        definitions = [extract_value(fields, 'vocab-translation')]
        grammar = [extract_value(fields, 'part-of-speech')]
        example_sentences = [extract_value(fields, 'sentence') + " " + extract_value(fields, 'sentence-translation'), extract_value(fields, 'examples')]

    return VocabInfo(
        vocab=vocab,
        reading=reading,
        definitions=definitions,
        grammar=grammar,
        example_sentences=example_sentences,
    )

def note_info_18k_to_card(info: dict) -> VocabInfo | None:
        fields = info['fields']
        vocab = fields['Expression']['value']
        reading = fields['Reading']['value']
        definitions = [fields['English definition'], fields["Additional definitions"]]
        grammar = [fields['Grammar']]
        example_sentences = []

        return VocabInfo(
            vocab=vocab,
            reading=reading,
            definitions=definitions,
            grammar=grammar,
            example_sentences=example_sentences,
        )

def transfer():
    # load the deck that contains user progress (source)

    # load the deck to transfer to (destination)

    # match notes from source to destination

    # convert progress from each note

    # save the updated destination deck

    # ---
    apkg = Apkg("scratch/N0.apkg")
    count = 0
    for note in apkg.db.Notes:
        count += 1
    print(count)
    for note in apkg.db.Notes:
        sys.stdout.buffer.write(str(note.tags).encode("utf-8"))
        sys.stdout.buffer.write("\n".encode('utf-8'))
        if note.tags == None:
            note.tags.null = False

    apkg.export("scratch/N0-updated.apkg")


