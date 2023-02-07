from dataclasses import dataclass
import json

@dataclass(frozen=True)
class ShinwaeiEntry:
    term: str
    reading: str | None
    definition: str