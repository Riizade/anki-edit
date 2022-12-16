from jamdict import Jamdict
import sys
from dataclasses import dataclass
from core.vocab import VocabWord
from pprint import pformat


@dataclass(frozen=True)
class Reading:
    reading_type: str
    on_type: str
    value: str
    r_status: str

@dataclass(frozen=True)
class Meaning:
    value: str
    language: str

@dataclass(frozen=True)
class ReadingMeaningGroup:
    readings: list[Reading]
    meanings: list[Meaning]

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
    meanings: str | None
    example_words: list[VocabWord]


def load_all_kanji():
    # initialize SQLite context
    jam = Jamdict()
    sqlite_context = jam.kd2.ctx()

    # fetch each kanji
    kanji_rows = sqlite_context.select("SELECT * FROM character")
    for kanji_row in kanji_rows:
        # record character id
        cid = kanji_row['ID']

        # fetch all radicals for this kanji
        radical_rows = sqlite_context.select(f"SELECT * FROM radical WHERE cid='{cid}'")
        radicals: list[Radical] = []
        for radical in radical_rows:
            radicals.append(Radical(radical['value'], radical['rad_type']))

        # fetch all variants for this kanji
        variant_rows = sqlite_context.select(f"SELECT * FROM variant WHERE cid='{cid}'")
        variants: list[Variant] = []
        for variant in variant_rows:
            variants.append(Variant(variant['value'], variant['var_type']))

        # fetch RM groups for this kanji
        rm_groups = sqlite_context.select(f"SELECT * FROM rm_group WHERE cid='{cid}'")
        group_ids = [group['ID'] for group in rm_groups]

        # use group ids to fetch meanings and readings
        for group_id in group_ids:
            # fetch meaning
            pass

        # kanji fields: ['ID', 'literal', 'stroke_count', 'grade', 'freq', 'jlpt']
        for field in ['ID', 'literal', 'stroke_count', 'grade', 'freq', 'jlpt']:
                sys.stdout.buffer.write((str(kanji_row[field]) + " ").encode("utf8"))
        kanji = Kanji(
            character=kanji_row['literal'],
            stroke_count=kanji_row['stroke_count'],
            grade=kanji_row['grade'],
            frequency=kanji_row['freq'],
            jlpt_level=kanji_row['jlpt'],
            radicals=radicals,
            variants=variants,
            example_words=[],
            meanings='',
        )
        s = pformat(kanji)
        sys.stdout.buffer.write(s.encode("utf8"))
        sys.stdout.buffer.write("\n".encode("utf8"))
