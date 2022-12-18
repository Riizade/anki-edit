from core.kanji import load_all_kanji
from core.vocab import load_all_vocab
from core.utils import cached_load
from pathlib import Path

def main():
    cached_load(load_all_kanji, Path('./cache/kanji.bin'))

if __name__ == "__main__":
    main()