from jamdict import Jamdict
import sys
from dataclasses import dataclass
from core.vocab import VocabWord
from pprint import pformat

@dataclass(frozen=True)
class Radical:
    radical: str
    radical_type: str

@dataclass(frozen=True)
class Variant:
    variant: str
    variant_type: str

@dataclass(frozen=True)
class Kanji:
    character: str
    radicals: list[Radical]
    variants: list[Variant]
    stroke_count: int
    grade: str | None
    jlpt_level: str | None
    frequency: str | None
    meanings: list[str]
    on_yomi: list[str]
    kun_yomi: list[str]
    nanori: list[str]
    example_words: list[VocabWord]


def load_all_kanji() -> list[Kanji]:
    # initialize SQLite context
    jam = Jamdict()
    sqlite_context = jam.kd2.ctx()

    # fetch each kanji
    all_kanji: list[Kanji] = []
    kanji_rows = sqlite_context.select("SELECT * FROM character")
    for kanji_row in kanji_rows:
        # record character id
        cid = kanji_row['ID']

        # TODO: variants and radicals are given numerical identifiers, we need to grab the actual character instead
        # fetch all radicals for this kanji
        # BUG: this seems to only fetch one radical for each kanji
        radical_rows = sqlite_context.select(f"SELECT * FROM radical WHERE cid='{cid}'")
        radicals: list[Radical] = []
        for radical in radical_rows:
            radicals.append(Radical(radical['value'], radical['rad_type']))

        # fetch all variants for this kanji
        variant_rows = sqlite_context.select(f"SELECT * FROM variant WHERE cid='{cid}'")
        variants: list[Variant] = []
        for variant in variant_rows:
            variants.append(Variant(variant['value'], variant['var_type']))

        # fetch nanori (unconventional readings)
        nanori_rows = sqlite_context.select(f"SELECT * FROM nanori WHERE cid='{cid}'")
        nanori: list[str] = []
        for nanori_row in nanori_rows:
            nanori.append(nanori_row['value'])

        # fetch RM groups for this kanji
        rm_groups = sqlite_context.select(f"SELECT * FROM rm_group WHERE cid='{cid}'")
        group_ids = [group['ID'] for group in rm_groups]

        # use group ids to fetch meanings and readings
        # as of 2022/12/17, there is no kanji that has more than one group
        # the group distinction seems completely unused and is a meaningless layer of indirection
        # as a result, we won't track meanings/readings as being part of a group, we'll just add them directly to the kanji
        # additionally, I don't know what the 'on_type' and 'r_status' fields are, they're empty for most (maybe all) kanji, so I'll just ignore them
        meanings: list[str] = []
        on_yomi: list[str] = []
        kun_yomi: list[str] = []
        for group_id in group_ids:
            # fetch meanings
            meaning_rows = sqlite_context.select(f"SELECT * FROM meaning WHERE gid='{group_id}'")
            for meaning in meaning_rows:
                # select only English meanings
                if meaning['m_lang'] == '': # english meanings have an m_lang of the empty string
                    meanings.append(meaning['value'])

            # fetch readings
            reading_rows = sqlite_context.select(f"SELECT * FROM reading WHERE gid='{group_id}'")
            for reading in reading_rows:
                if reading['r_type'] == 'ja_on':
                    on_yomi.append(reading['value'])
                if reading['r_type'] == 'ja_kun':
                    kun_yomi.append(reading['value'])


        kanji = Kanji(
            character=kanji_row['literal'],
            stroke_count=kanji_row['stroke_count'],
            grade=kanji_row['grade'],
            frequency=kanji_row['freq'],
            jlpt_level=kanji_row['jlpt'],
            radicals=radicals,
            variants=variants,
            example_words=[],
            meanings=meanings,
            on_yomi=on_yomi,
            kun_yomi=kun_yomi,
            nanori=nanori,
        )
        all_kanji.append(kanji)

        s = pformat(kanji)
        sys.stdout.buffer.write(s.encode("utf8"))
        sys.stdout.buffer.write("\n".encode("utf8"))

    return all_kanji
