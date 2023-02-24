from __future__ import annotations
from core.pystardict import Dictionary
from pathlib import Path
from dataclasses import dataclass

# refer to https://github.com/lig/pystardict/blob/ce2bd7b4289411c2ac1536a4d186ade9c3a79aba/pystardict.py for details of stardict.Dictionary

@dataclass(frozen=True)
class StardictEntry:
    term: str
    entry: str

@dataclass(frozen=True)
class Stardict:
    name: str
    entries: list[StardictEntry]

    @staticmethod
    def from_dir(path: Path) -> Stardict:
        return load_dictionary(path)


# point to the directory containing the dictionary
def load_dictionary(path: Path) -> Stardict:
    file_suffixes = set(['.dict', '.dict.dz', '.idx', '.ifo'])

    print(f"loading stardict from path {path}", flush=True)
    filestem = None

    # TODO: currently just grabs the first name it finds, should probably check that all present files with applicable extensions share the same name
    for directory_entry in path.iterdir():
        if directory_entry.is_file() and directory_entry.suffix in file_suffixes:
            filestem = directory_entry.stem

    if filestem is None:
        raise ValueError(f"Could not find the common filestem name for path {path}, which is required to load the Stardict dictionary. Please check that the .dict/.dict.dz, .ifo, and .idx files all share the same filestem (the part of the filename before the file extension)")
    else:
        d = Dictionary(path / filestem)

        entries = []
        for key in d.keys():
            entry = d[key]
            obj = StardictEntry(term=key, entry=entry)
            entries.append(obj)

        return Stardict(name = d.ifo.bookname, entries=entries)