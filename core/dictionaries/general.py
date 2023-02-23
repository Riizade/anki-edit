from __future__ import annotations
from core.dictionaries.stardict import Stardict
from core.dictionaries.yomichan import YomichanDictionary
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class DictionaryType(Enum):
    UNKNOWN = 0
    YOMICHAN = 1
    STARDICT = 2

@dataclass(frozen=True)
class BasicDictionaryEntry:
    term: str
    reading: str | None
    definition: str

@dataclass(frozen=True)
class BasicDictionary:
    name: str
    entries: list[BasicDictionaryEntry]

    @staticmethod
    def from_dir(path: Path) -> BasicDictionary:
        return load_dictionary_from_path(path)

    @staticmethod
    def from_dictionary(d: Stardict | YomichanDictionary) -> BasicDictionary:
        return load_dictionary_from_other(d)

def load_dictionary_from_path(path: Path) -> BasicDictionary:
    dictionary_type = detect_dictionary_type(path)
    if dictionary_type == DictionaryType.STARDICT:
        d = Stardict.from_dir(path)
    elif dictionary_type == DictionaryType.YOMICHAN:
        d = YomichanDictionary.from_dir(path)
    else:
        raise ValueError(f"Could not determine dictionary type for path {path}, are you sure this path contains a valid dictionary?")

    return load_dictionary_from_other(d)

def load_dictionary_from_other(d: Stardict | YomichanDictionary) -> BasicDictionary:
    if d.__class__ == Stardict:
        return load_dictionary_from_stardict(d)
    elif d.__class__ == YomichanDictionary:
        return load_dictionary_from_yomichan(d)
    else:
        raise ValueError(f"Dictionary has unknown class type: {d.__class__}")

def load_dictionary_from_stardict(d: Stardict) -> BasicDictionary:
    entries: list[BasicDictionaryEntry] = []
    for entry in d.entries:
        entries.append(BasicDictionaryEntry(
            term=entry.term,
            reading=None,
            definition=entry.entry,
        ))

    BasicDictionary(
        name=d.name,
        entries=entries,
    )

def load_dictionary_from_yomichan(d: YomichanDictionary) -> BasicDictionary:
    entries: list[BasicDictionaryEntry] = []
    for entry in d.entries:
        entries.append(BasicDictionaryEntry(
            term=entry.term,
            reading=entry.reading,
            definition='\n\n'.join(entry.definitions),
        ))

    BasicDictionary(
        name=d.name,
        entries=entries,
    )

def detect_dictionary_type(path: Path) -> DictionaryType:
    yomichan_extensions = set('.json')
    stardict_extensions = set('.dict', '.dict.dz', '.ifo', '.idx')

    yomichan_count = 0
    stardict_count = 0
    for entry in path.iterdir():
        if entry.suffix in yomichan_extensions:
            yomichan_count += 1
        elif entry.suffix in stardict_extensions:
            stardict_count += 1

    if yomichan_count > stardict_count:
        return DictionaryType.YOMICHAN
    elif stardict_count > yomichan_count:
        return DictionaryType.STARDICT
    else:
        return DictionaryType.UNKNOWN
