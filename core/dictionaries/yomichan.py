from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass

# fields with "fieldX" names are fields where I have no idea what it's supposed to contain
class YomichanDictionaryEntry:
    term: str
    reading: str
    field3: str
    field4: str
    field5: float
    definitions: list[str]
    entry_order: int
    field8: str

class YomichanDictionary:
    name: str
    revision: str
    entries: list[YomichanDictionaryEntry]

    @staticmethod
    def from_dir(path: Path) -> YomichanDictionary:
        return load_dictionary(path)



# Path must point to the directory containing the dictionary's JSON files
def load_dictionary(path: Path):
    pass