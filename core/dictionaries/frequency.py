from dataclasses import dataclass
import json
from pathlib import Path
from dataclasses_serialization.json import JSONSerializer
import csv

@dataclass(frozen=True)
class FrequencyEntry:
    term: str
    reading: str | None
    ranking: int # lower number means more frequent

@dataclass(frozen=True)
class FrequencySource:
    name: str
    entries: list[FrequencyEntry]

def load_bccwj(filename: Path) -> FrequencySource:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            entries.append(FrequencyEntry(entry[0], None, entry[2]))

    return FrequencySource(
        name="BCCWJ",
        entries=entries,
    )

def load_cc100(filename: Path) -> list[FrequencyEntry]:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            entries.append(FrequencyEntry(entry[0], entry[2]['reading'], entry[2]['frequency']))

    return FrequencySource(
        name="CC100",
        entries=entries,
    )

def load_jpdb(filename: Path) -> list[FrequencyEntry]:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            if 'reading' in entry[2]:
                reading = entry[2]['reading']
            else:
                reading = None
            entries.append(FrequencyEntry(entry[0], reading, entry[2]['value']))

    return FrequencySource(
        name="JPDB",
        entries=entries,
    )

def load_wikipedia(filename: Path) -> list[FrequencyEntry]:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            entries.append(FrequencyEntry(entry[0], None, entry[2]))

    return FrequencySource(
        name="Wikipedia",
        entries=entries,
    )

def load_sublex_csv(filename: Path) -> list[FrequencyEntry]:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for idx, row in enumerate(reader):
            entries.append(FrequencyEntry(
                term=row["Word"],
                reading=row["Pinyin"],
                ranking=idx,
            ))

    return FrequencySource(
        name="subtlex",
        entries=entries,
    )

def load_sublex_tsv(filename: Path) -> list[FrequencyEntry]:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for idx, row in enumerate(reader):
            entries.append(FrequencyEntry(
                term=row["Word"],
                reading=None,
                ranking=idx,
            ))

    return FrequencySource(
        name="subtlex",
        entries=entries,
    )

def save_frequency(source: FrequencySource, path: Path):
    with open(path, 'w', encoding='utf8') as f:
        jsons = JSONSerializer.serialize(source)
        f.write(jsons)