from core.kanji import load_all_kanji_uncached, Kanji
from jamdict.jmdict import JMDEntry
from core.vocab import load_all_vocab_uncached
from pathlib import Path
from core.utils import pprint_data
from core.modify_kanji_deck import augment_examples
from core.merge_jp_decks import read_decks
from core.dictionaries.frequency import *

def main():
    convert_frequency_dictionaries()

def convert_frequency_dictionaries():
    # list of tuples of (source name, filename, parsing function, destination filename)
    raw_dictionaries = [
        ("subtlex", Path('./scratch/Chinese/subtlex-ch.utf8'), load_subtlex_tsv, Path('./scratch/Chinese/frequency/subtlex.json')),
        ("subtlex", Path('./scratch/Italian/subtlex-it.csv'), load_subtlex_csv, Path('./scratch/Italian/frequency/subtlex.json')),
        ("BCCWJ", Path('./scratch/Japanese/Yomichan Dictionaries/[Freq] BCCWJ/term_meta_bank_1.json'), load_yomichan, Path('./scratch/Japanese/frequency/bccwj.json')),
        ("JPDB", Path('./scratch/Japanese/Yomichan Dictionaries/[Freq] JPDB (Recommended)/term_meta_bank_1.json'), load_yomichan, Path('./scratch/Japanese/frequency/jpdb.json')),
        ("CC100", Path('./scratch/Japanese/Yomichan Dictionaries/[Freq] CC100/term_meta_bank_1.json'), load_yomichan, Path('./scratch/Japanese/frequency/cc100.json')),
        ("Wikipedia", Path('./scratch/Japanese/Yomichan Dictionaries/[Freq] Wikipedia v2/term_meta_bank_1.json'), load_yomichan, Path('./scratch/Japanese/frequency/wikipedia.json')),
    ]

    for d in raw_dictionaries:
        print_utf8(f"converting {d[1]}")
        source_name = d[0]
        source_file = d[1]
        function = d[2]
        destination: Path = d[3]
        parsed_dict = function(source_file, source_name)
        destination.parent.mkdir(exist_ok=True, parents=True)
        save_frequency(parsed_dict, destination)

def augment_kanji_examples():
    augment_examples(deck_name="* JLPT N0 Recognition", kanji_field="Kanji", examples_field="Examples")
    augment_examples(deck_name="* JLPT N1 Recognition", kanji_field="Kanji", examples_field="Examples")

def analyze_vocab(vocab_list: list[JMDEntry]):
    total = len(vocab_list)
    for vocab in vocab_list:
        pprint_data(vocab)


def analyze_kanji(all_kanji: list[Kanji]):
    total = len(all_kanji)
    no_examples = 0
    no_examples_jlpt = 0
    no_kunyomi = 0
    no_kunyomi_jlpt = 0
    no_onyomi = 0
    no_onyomi_jlpt = 0
    no_meaning = 0
    no_meaning_jlpt = 0
    has_frequency = 0
    for kanji in all_kanji:
        if len(kanji.example_words) == 0:
            no_examples += 1
        if len(kanji.example_words) == 0 and kanji.jlpt_level is not None:
            no_examples_jlpt += 1
        if len(kanji.kun_yomi) == 0:
            no_kunyomi += 1
        if len(kanji.kun_yomi) == 0 and kanji.jlpt_level is not None:
            no_kunyomi_jlpt += 1
        if len(kanji.on_yomi) == 0:
            no_onyomi += 1
        if len(kanji.on_yomi) == 0 and kanji.jlpt_level is not None:
            no_onyomi_jlpt += 1
        if len(kanji.meanings) == 0:
            no_meaning += 1
        if len(kanji.meanings) == 0 and kanji.jlpt_level is not None:
            no_meaning_jlpt += 1
        if kanji.frequency is not None:
            has_frequency += 1
    print(f"total kanji: {total}")
    print(f"no examples: {no_examples}")
    print(f"no examples JLPT: {no_examples_jlpt}")
    print(f"no kunyomi: {no_kunyomi}")
    print(f"no kunyomi JLPT: {no_kunyomi_jlpt}")
    print(f"no onyomi: {no_onyomi}")
    print(f"no onyomi JLPT: {no_onyomi_jlpt}")
    print(f"no meaning: {no_meaning}")
    print(f"no meaning JLPT: {no_meaning_jlpt}")
    print(f"has frequency: {has_frequency}")

if __name__ == "__main__":
    main()