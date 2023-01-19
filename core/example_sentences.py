from utils import *

from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class ParallelSentence:
    japanese: str
    english: str

class CharType(Enum):
    OTHER = 0
    KANJI = 1
    HIRAGANA = 2
    KATAKANA = 3

def sentence_map(sentences: iter[ParallelSentence]) -> dict[str, list[ParallelSentence]]:
    result: dict[str, list[ParallelSentence]] = {}
    for sentence in sentences:
        sentence: ParallelSentence
        keys = sentence_keys(sentence.japanese)
        for key in keys:
            if key not in result:
                result[key] = []
            result[key].append(sentence)

    return result

def sentence_keys(sentence: str) -> list[str]:
    keys = []
    for i in [1, 2, 3, 4]:
        igrams = sentence_to_n_grams(sentence, i)
        keys.extend(igrams)
    return keys

def classify_character(c: str) -> CharType:
    if is_hiragana(c):
        return CharType.HIRAGANA
    elif is_katakana(c):
        return CharType.KATAKANA
    elif is_probably_kanji(c):
        return CharType.KANJI
    else:
        return CharType.OTHER

def uniform_type(s: str) -> bool:
    possible_type = classify_character(s[0])
    for c in s:
        if classify_character(c) != possible_type:
            return False

    return True

# converts a Japanese sentence to n-grams
# n-grams will only contain one of kanji, katakana, or hiragana, never two or more
def sentence_to_n_grams(sentence: str, n: int) -> list[str]:
    # get a list of n grams
    ngrams = [sentence[i:i+n] for i in range(len(sentence)-n+1)]
    # filter to only ngrams that are made of the same type of character
    ngrams = ["".join(g) for g in ngrams if uniform_type(g)]
    return ngrams

