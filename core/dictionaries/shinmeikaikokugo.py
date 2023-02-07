from dataclasses import dataclass
import json

@dataclass(frozen=True)
class JMDictEntry:
    term: str
    reading: str | None
    entry_text: str