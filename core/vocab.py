from jamdict import Jamdict
from jamdict.jmdict import JMDEntry
from dataclasses import dataclass
from puchikarui import ExecutionContext
from tqdm import tqdm
from core.utils import cached_load, pprint_data
from pathlib import Path

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

def load_all_vocab_cached() -> list[JMDEntry]:
    return cached_load(load_all_vocab_uncached, list[JMDEntry], Path('./cache/vocab.bson'))

def load_all_vocab_uncached() -> list[JMDEntry]:
    # initialize SQLite context
    jam = Jamdict()
    sqlite_context = jam.kd2.ctx()
    print("loading vocab...")

    # fetch ids for each entry
    entry_rows = sqlite_context.select("SELECT * FROM Entry")
    entry_ids = [row['idseq'] for row in entry_rows]

    # load the JMDEntry object for each entry
    vocab: list[JMDEntry] = []
    # TODO: remove debug limit
    for idseq in tqdm(entry_ids):
        vocab_data = load_vocab_data(idseq)
        vocab.append(vocab_data)

    # return the entire list
    return vocab

def load_kanji_to_vocab_mapping_cached() -> dict[str, list[JMDEntry]]:
    cached_load(load_kanji_to_vocab_mapping_internal_cached, dict[str, list[JMDEntry]], Path('./cache/kanji_to_vocab_mapping.bson'))

def load_kanji_to_vocab_mapping_internal_cached() -> dict[str, list[JMDEntry]]:
    vocab_list = load_all_vocab_cached()
    return build_kanji_to_vocab_mapping(vocab_list)

def load_kanji_to_vocab_mapping_uncached() -> dict[str, list[JMDEntry]]:
    vocab_list = load_all_vocab_uncached()
    return build_kanji_to_vocab_mapping(vocab_list)


def build_kanji_to_vocab_mapping(vocab_list: list[JMDEntry]) -> dict[str, list[JMDEntry]]:
    print("building kanji -> vocab mapping")
    mapping: dict[str, list[JMDEntry]] = {}
    for vocab in tqdm(vocab_list):
        for k in vocab.kanji_forms:
            for char in k.text:
                if is_probably_kanji(char):
                    if char not in mapping:
                        mapping[char] = []
                    mapping[char].append(vocab)
    return mapping

def load_vocab_data(idseq: str) -> JMDEntry:
    entry: JMDEntry = Jamdict().get_entry(idseq)
    return entry

# define sets of characters to ignore
hiragana = 'あいうえおかきくけこがぎぐげごさしすせそざじずぜぞたちつてとだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよらりるれろわを'
katakana = 'アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨラリルレロワヲ'
small_hiragana = 'っぁぃぅぇぉょゅゃ'
small_katakana = 'ッァィゥェォョュャ'
punctuation = './?!:;<>[]-_+=~`ー\'\"|`'
alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '1234567890'
ignore_set = set(hiragana + katakana + punctuation + small_hiragana + small_katakana + alphabet + numbers)
# this is not meant to be a foolproof solution
# this just ignores common characters in Japanese that are not kanji so that when we store a kanji -> word mapping, we don't store extra data mapping vocab words to each kana that appears
# this can definitely be improved
def is_probably_kanji(character: str) -> bool:
    return character not in ignore_set