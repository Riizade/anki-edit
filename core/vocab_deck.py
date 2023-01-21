from ankisync2 import Apkg
import genanki
import sys
import core.anki_connect as anki_connect
from core.utils import print_utf8, pprint_data
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class VocabCard:
    vocab: str
    reading: str
    definitions: list[str]
    grammar: list[str]
    example_sentences: list[str]

def read_decks():
    vocab_10k = read_deck("* Japanese Core 10k Recognition", note_info_10k_to_card)
    vocab_18k = read_deck("Japanese Core 18k Recognition", note_info_18k_to_card)

    set_10k = set([i.vocab for i in vocab_10k])
    set_18k = set([i.vocab for i in vocab_18k])

    total_number = len(set_10k.union(set_18k))
    set_10k_not_in_18k = len(set_10k.difference(set_18k))
    set_18k_not_in_10k = len(set_18k.difference(set_10k))
    intersection = len(set_10k.intersection(set_18k))
    print(f"total: {total_number}\n10k -> 18k missing: {set_10k_not_in_18k}\n18k -> 10k missing: {set_18k_not_in_10k}\nintersection: {intersection}")


def read_deck(name: str, conversion_function: Callable[[dict], VocabCard]) -> list[VocabCard]:
    note_ids = anki_connect.get_notes_in_deck(name)
    note_infos = anki_connect.get_note_info(note_ids)

    cards = [conversion_function(info) for info in note_infos]
    cards = [c for c in cards if c is not None]

    return cards


def extract_value(fields: dict, field_name: str) -> str:
    if isinstance(fields[field_name], dict):
        return fields[field_name]['value']
    elif isinstance(fields[field_name], str):
        return fields[field_name]
    else:
        raise ValueError(f"cannot extract type from field {field_name} for info {fields}")

def note_info_10k_to_card(info: dict) -> VocabCard | None:
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


    if not isinstance(vocab, str):
        print("10k")
        pprint_data(info)
    return VocabCard(
        vocab=vocab,
        reading=reading,
        definitions=definitions,
        grammar=grammar,
        example_sentences=example_sentences,
    )

def note_info_18k_to_card(info: dict) -> VocabCard | None:
        fields = info['fields']
        vocab = fields['Expression']['value']
        reading = fields['Reading']['value']
        definitions = [fields['English definition'], fields["Additional definitions"]]
        grammar = [fields['Grammar']]
        example_sentences = []
        if not isinstance(vocab, str):
            print("18k")
            pprint_data(info)
        return VocabCard(
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


