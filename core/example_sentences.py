from core.utils import *

from enum import Enum
from dataclasses import dataclass
from tqdm import tqdm

@dataclass(frozen=True)
class ParallelSentence:
    japanese: str
    english: str

class CharType(Enum):
    OTHER = 0
    KANJI = 1
    HIRAGANA = 2
    KATAKANA = 3

def sentence_map() -> dict[str, list[ParallelSentence]]:
    sentences = read_sentences()
    return create_sentence_map(sentences)

def read_sentences() -> list[ParallelSentence]:
    sentences = []
    with open('./data/sentence_corpus_tatoeba_org.txt') as f:
        print_utf8("reading sentences from file...")
        for line in tqdm(f.readlines()):
            split = line.split("\t")
            sentence = ParallelSentence(japanese=split[1], english=split[0])
            sentences.append(sentence)
    return sentences


def create_sentence_map(sentences: list[ParallelSentence]) -> dict[str, list[ParallelSentence]]:
    result: dict[str, list[ParallelSentence]] = {}
    print_utf8("creating index of n-grams in sentences...")
    for sentence in tqdm(sentences):
        sentence: ParallelSentence
        keys = sentence_keys(sentence.japanese)
        for key in keys:
            if key not in result:
                result[key] = []
            result[key].append(sentence)

    return result

def sentence_keys(sentence: str) -> list[str]:
    MAX_NGRAMS = 15
    keys = []
    for i in range(1, MAX_NGRAMS+1):
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
def sentence_to_n_grams(sentence: str, n: int) -> list[str]:
    # ensure that we don't go out-of-bounds
    if len(sentence) < n:
        return []
    # get a list of n grams
    ngrams = [sentence[i:i+n] for i in range(len(sentence)-n+1)]
    return ngrams

