from dataclasses import dataclass
import json
from pathlib import Path

@dataclass(frozen=True)
class FrequencyEntry:
    term: str
    reading: str | None
    frequency: int
    source: str

def load_bccwj(filename: Path) -> list[FrequencyEntry]:
    result = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            result.append(FrequencyEntry(entry[0], None, entry[2], 'BCCWJ'))

    return result

def load_cc100(filename: Path) -> list[FrequencyEntry]:
    result = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            result.append(FrequencyEntry(entry[0], entry[2]['reading'], entry[2]['frequency'], 'CC100'))

    return result

def load_jpdb(filename: Path) -> list[FrequencyEntry]:
    result = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            if 'reading' in entry[2]:
                reading = entry[2]['reading']
            else:
                reading = None
            result.append(FrequencyEntry(entry[0], reading, entry[2]['value'], 'JPDB'))

    return result

def load_wikipedia(filename: Path) -> list[FrequencyEntry]:
    result = []
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            result.append(FrequencyEntry(entry[0], None, entry[2], 'Wikipedia'))

    return result
