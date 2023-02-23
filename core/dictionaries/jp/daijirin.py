from dataclasses import dataclass
import json

@dataclass(frozen=True)
class DaijirinEntry:
    term: str
    reading: str
    entry_text: str