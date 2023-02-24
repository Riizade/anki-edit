from dataclasses_serialization.json import JSONSerializer
from pathlib import Path
import sys
from pprint import pformat
from typing import Any

# takes basic collections (e.g., list, dict) and dataclasses as data
def save_to_cache(data, cache_path: Path):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    bytes = JSONSerializer.serialize(data)
    with open(cache_path, 'wb') as f:
        f.write(bytes)

def load_from_cache(type, cache_path: Path) -> any:
    with open(cache_path, 'rb') as f:
        return JSONSerializer.deserialize(type, f.read())

def cached_load(load_function: callable, type, cache_path: Path) -> any:
    if cache_path.exists() and cache_path.is_file():
        return load_from_cache(type, cache_path)
    else:
        data = load_function()
        save_to_cache(data, cache_path)
        return data

def pprint_data(data: Any) -> None:
    sys.stdout.buffer.write(pformat(data).encode("utf8"))
    sys.stdout.buffer.write("\n".encode("utf8"))

def print_utf8(d: Any) -> None:
    sys.stdout.buffer.write(str(d).encode("utf8") + "\n".encode("utf8"))

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

# define sets of characters to ignore
hiragana = 'あいうえおかきくけこがぎぐげごさしすせそざじずぜぞたちつてとだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよらりるれろわを'
katakana = 'アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨラリルレロワヲ'
small_hiragana = 'っぁぃぅぇぉょゅゃ'
small_katakana = 'ッァィゥェォョュャ'
punctuation = './?!:;<>[]-_+=~`ー\'\"|`'
alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '1234567890'

hiragana_set = set(hiragana + small_hiragana)
katakana_set = set(katakana + small_katakana)
non_kanji_set = set(hiragana + katakana + punctuation + small_hiragana + small_katakana + alphabet + numbers)

# this is not meant to be a foolproof solution
# this just ignores common characters in Japanese that are not kanji so that when we store a kanji -> word mapping, we don't store extra data mapping vocab words to each kana that appears
# this can definitely be improved
def is_probably_kanji(character: str) -> bool:
    return character not in non_kanji_set

def is_hiragana(character: str) -> bool:
    return character in hiragana_set

def is_katakana(character: str) -> bool:
    return character in katakana_set

def is_kana(character: str) -> bool:
    return character in hiragana_set or character in katakana_set