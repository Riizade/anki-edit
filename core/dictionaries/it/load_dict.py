from pystardict import Dictionary

from pathlib import Path
from core.utils import print_utf8



def build_it_deck():
    it_it = Dictionary(Path('./scratch/Italian Dictionaries/dict-it-en/Italian - English'))
    it_en = Dictionary(Path('./scratch/Italian Dictionaries/dict-it-it/dict-data'))

    count = 0
    for key in it_en.keys():
        count += 1
        print_utf8('-' * 80)
        print_utf8(key)
        print_utf8('-' * 80)
        print_utf8(it_en[key])
    print(count)

    count = 0
    for key in it_it.keys():
        count += 1
        # print_utf8('-' * 80)
        # print_utf8(key)
        # print_utf8('-' * 80)
        # print_utf8(it_it[key])
    print(count)