from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass
import os
import re
from core.utils import print_utf8

# fields with "fieldX" names are fields for which I have no idea what it's supposed to contain
@dataclass(frozen=True)
class YomichanDictionaryEntry:
    term: str
    reading: str
    field3: str
    field4: str
    field5: float
    definitions: list[str]
    entry_order: int
    field8: str

@dataclass(frozen=True)
class YomichanDictionary:
    name: str
    revision: str
    entries: list[YomichanDictionaryEntry]

    @staticmethod
    def from_dir(path: Path) -> YomichanDictionary:
        return load_dictionary(path)

# Path must point to the directory containing the dictionary's JSON files
def load_dictionary(path: Path) -> YomichanDictionary:
    print_utf8(f"loading Yomichan dict from {path}")

    term_bank_re = re.compile(r"term_bank_[0-9]+")

    term_banks: list[Path] = []
    index: Path | None = None

    # list all files in the directory
    for directory_entry in path.iterdir():
        # find all JSON files in the path
        if directory_entry.is_file() and directory_entry.suffix == '.json':
            filestem = directory_entry.stem
            # determine if the file is an index.json or a term_bank_*.json file and behave accordingly
            if filestem == "index":
                index = directory_entry
            elif term_bank_re.match(filestem):
                term_banks.append(directory_entry)

    # extract data from the index
    with open(index, 'r', encoding='utf8') as index_file:
        index_data = json.load(index_file)
        name = index_data['title']
        revision = index_data['revision']

        # parse all terms from the term bank
        terms: list[YomichanDictionaryEntry] = []

        for term_bank in term_banks:
            with open(term_bank, 'r', encoding='utf8') as term_bank_file:
                bank_data = json.load(term_bank_file)
                # the term bank is an array of terms
                for term_data in bank_data:
                    # clean definitions
                    raw_definitions = term_data[5]
                    definitions = [clean_definition(d) for d in raw_definitions]

                    # each term is an array of fields (0-7, 8 total fields)
                    term = YomichanDictionaryEntry(
                        term=term_data[0],
                        reading=term_data[1],
                        field3=term_data[2],
                        field4=term_data[3],
                        field5=term_data[4],
                        definitions=definitions,
                        entry_order=term_data[6],
                        field8=term_data[7]
                    )
                    terms.append(term)

        return YomichanDictionary(
            name=name,
            revision=revision,
            entries=terms,
        )

def clean_definition(definition: str | dict) -> str:
    if isinstance(definition, str):
        return definition
    elif isinstance(definition, dict):
        return '\n'.join([d for d in definition['content'] if isinstance(d, str)])
    else:
        raise ValueError(f"Cannot clean definition {definition}")
