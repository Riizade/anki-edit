from jamdict import Jamdict
import sys
from dataclasses import dataclass

@dataclass(frozen=True)
class ExampleSentence:
    japanese_sentence: str
    english_translation: str

@dataclass(frozen=True)
class VocabWord:
    kanji: str | None
    kana: str
    alternative_writings: list[str]
    english_meanings: list[str]
    example_sentences: list[str]