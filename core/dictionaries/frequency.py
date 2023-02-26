from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from dataclasses_serialization.json import JSONSerializer
import csv
import dacite

@dataclass(frozen=True)
class FrequencyEntry:
    term: str
    reading: str | None
    ranking: int # lower number means more frequent

@dataclass(frozen=True)
class FrequencySource:
    name: str
    entries: list[FrequencyEntry]

    @staticmethod
    def from_file(path: Path) -> FrequencySource:
        return load_frequency(path)

def load_yomichan(filename: Path, source_name: str) -> FrequencySource:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for i, entry in enumerate(data):
            # term
            term = entry[0]

            # reading
            if isinstance(entry[2], int):
                reading  = None
            elif 'reading' in entry[2]:
                reading = entry[2]['reading']
            else:
                reading = None

            # ranking
            if isinstance(entry[2], int):
                freq = entry[2]
            elif 'value' in entry[2]:
                freq = entry[2]['value']
            elif 'frequency' in entry[2]:
                if isinstance(entry[2]['frequency'], int):
                    freq = entry[2]['frequency']
                else:
                    freq = entry[2]['frequency']['value']
            else:
                raise ValueError(f"Could not parse frequency data for {entry}")

            entries.append(FrequencyEntry(term, reading, freq))

    return FrequencySource(
        name=source_name,
        entries=entries,
    )

def load_subtlex_csv(filename: Path, source_name: str = "subtlex") -> FrequencySource:
    entries: list[FrequencyEntry] = []
    stored_lemmas = set()
    with open(filename, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for idx, row in enumerate(reader):
            term = row['dom_lemma']
            # only store the term the first time we see it (because the frequency list contains one entry for each conjugation seen)
            if term in stored_lemmas:
                continue
            stored_lemmas.add(term)
            entries.append(FrequencyEntry(
                term=row["dom_lemma"],
                reading=None,
                ranking=idx,
            ))

    return FrequencySource(
        name=source_name,
        entries=entries,
    )

def load_subtlex_tsv(filename: Path, source_name: str = "subtlex") -> FrequencySource:
    entries: list[FrequencyEntry] = []
    with open(filename, 'r', encoding='utf8') as f:
        reader = csv.reader(f, delimiter='\t', quotechar='"')
        for idx, row in enumerate(reader):
            entries.append(FrequencyEntry(
                term=row[0],
                reading=row[2],
                ranking=idx,
            ))

    return FrequencySource(
        name=source_name,
        entries=entries,
    )

def save_frequency(source: FrequencySource, path: Path) -> None:
    with open(path, 'w', encoding='utf8') as f:
        jsons = json.dumps(JSONSerializer.serialize(source))
        f.write(jsons)

def load_frequency(path: Path) -> FrequencySource:
    with open(path, 'r', encoding='utf8') as f:
        s = f.read()
        json_data = json.loads(s)
        deserialized: FrequencySource = dacite.from_dict(FrequencySource, json_data)
        return deserialized