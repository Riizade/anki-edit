from jamdict import Jamdict
from dataclasses import dataclass
from pprint import pformat
from puchikarui import ExecutionContext
from tqdm import tqdm
from core.utils import cached_load
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

# the "...Data" classes below represent the raw data structure of the vocabulary database (from JMDict)

@dataclass(frozen=True)
class LinkData:
    id: str
    idseq: str
    tag: str
    desc: str
    uri: str

@dataclass(frozen=True)
class BibData:
    id: str
    idseq: str
    tag: str
    text: str

@dataclass(frozen=True)
class AuditData:
    idseq: str
    upd_date: str
    upd_detl: str

@dataclass(frozen=True)
class KanjiData:
    id: str
    idseq: str
    text: str
    kji: list[str]
    kjp: list[str]

@dataclass(frozen=True)
class KanaData:
    id: str
    idseq: str
    text: str
    nokanji: str
    kni: list[str]
    knp: list[str]
    knr: list[str]

@dataclass(frozen=True)
class SenseSourceData:
    sid: str
    text: str
    lang: str
    lstype: str
    wasei: str

@dataclass(frozen=True)
class SenseGlossData:
    sid: str
    lang: str
    gend: str
    text: str

@dataclass(frozen=True)
class SenseData:
    id: str
    idseq: str
    stagk: list[str]
    stagr: list[str]
    pos: list[str]
    xref: list[str]
    antonym: list[str]
    field: list[str]
    misc: list[str]
    sense_info: list[str]
    dialect: list[str]
    source: list[SenseSourceData]
    gloss: list[SenseGlossData]

@dataclass(frozen=True)
class VocabData:
    link: list[LinkData]
    bib: list[BibData]
    etym: list[str]
    audit: list[AuditData]
    kanji: list[KanjiData]
    kana: list[KanaData]
    senses: list[SenseData]

def load_all_vocab_cached() -> list[VocabData]:
    return cached_load(load_all_vocab_uncached, list[VocabData], Path('./cache/vocab.bson'))

def load_all_vocab_uncached() -> list[VocabData]:
    # initialize SQLite context
    jam = Jamdict()
    sqlite_context = jam.kd2.ctx()
    print("loading vocab...")

    # fetch ids for each entry
    entry_rows = sqlite_context.select("SELECT * FROM Entry")
    entry_ids = [row['idseq'] for row in entry_rows]

    # build the raw VocabData object for each entry
    vocab: list[VocabData] = []
    for idseq in tqdm(entry_ids):
        vocab_data = load_vocab_data(idseq, sqlite_context)
        vocab.append(vocab_data)

    # return the entire list
    return vocab

def load_kanji_to_vocab_mapping_cached() -> dict[str, list[VocabData]]:
    cached_load(load_kanji_to_vocab_mapping_internal_cached, dict[str, list[VocabData]], Path('./cache/kanji_to_vocab_mapping.bson'))

def load_kanji_to_vocab_mapping_internal_cached() -> dict[str, list[VocabData]]:
    vocab_list = load_all_vocab_cached()
    return build_kanji_to_vocab_mapping(vocab_list)

def load_kanji_to_vocab_mapping_uncached() -> dict[str, list[VocabData]]:
    vocab_list = load_all_vocab_uncached()
    return build_kanji_to_vocab_mapping(vocab_list)


def build_kanji_to_vocab_mapping(vocab_list: list[VocabData]) -> dict[str, list[VocabData]]:
    print("building kanji -> vocab mapping")
    mapping: dict[str, list[VocabData]] = {}
    for vocab in tqdm(vocab_list):
        for k in vocab.kanji:
            for char in k.text:
                if is_probably_kanji(char):
                    if char not in mapping:
                        mapping[char] = []
                    mapping[char].append(vocab)
    return mapping


def load_link_data(idseq: str, sqlite_context: ExecutionContext) -> list[LinkData]:
    link_rows = sqlite_context.select(f"SELECT * FROM Link WHERE idseq='{idseq}'")
    links: list[LinkData] = []
    for row in link_rows:
        links.append(LinkData(
                id=row['ID'],
                idseq=row['idseq'],
                tag=row['tag'],
                desc=row['desc'],
                uri=row['uri'],
        ))

    return links


def load_bib_data(idseq: str, sqlite_context: ExecutionContext) -> list[BibData]:
    bib_rows = sqlite_context.select(f"SELECT * FROM Bib WHERE idseq='{idseq}'")
    bibs: list[BibData] = []
    for row in bib_rows:
        bibs.append(
            BibData(
                id=row['ID'],
                idseq=row['idseq'],
                tag=row['tag'],
                text=row['text'],
            )
        )
    return bibs

def load_etym_data(idseq, sqlite_context: ExecutionContext) -> list[str]:
    etym_rows = sqlite_context.select(f"SELECT * FROM Etym WHERE idseq='{idseq}'")
    etyms = [row['text'] for row in etym_rows]

def load_audit_data(idseq, sqlite_context: ExecutionContext) -> list[AuditData]:
    audit_rows = sqlite_context.select(f"SELECT * FROM Audit WHERE idseq='{idseq}'")
    audits: list[AuditData] = []
    for row in audit_rows:
        audits.append(AuditData(
            idseq=row['idseq'],
            upd_date=row['upd_date'],
            upd_detl=row['upd_detl'],
        ))
    return audits

def load_kanji_data(idseq, sqlite_context: ExecutionContext) -> list[KanjiData]:
    kanji_rows = sqlite_context.select(f"SELECT * FROM Kanji WHERE idseq='{idseq}'")
    kanji: list[KanjiData] = []
    for row in kanji_rows:
        # record kanji id
        kid = row['ID']
        # fetch dependent data from kanji id
        kji_rows = sqlite_context.select(f"SELECT * FROM KJI WHERE kid='{kid}'")
        kji = [r['text'] for r in kji_rows]
        kjp_rows = sqlite_context.select(f"SELECT * FROM KJP WHERE kid='{kid}'")
        kjp = [r['text'] for r in kjp_rows]

        # append kanji data
        kanji.append(KanjiData(
            id=kid,
            idseq=row['idseq'],
            text=row['text'],
            kji=kji,
            kjp=kjp,
        ))
    return kanji

def load_kana_data(idseq, sqlite_context: ExecutionContext) -> list[KanaData]:
    kana_rows = sqlite_context.select(f"SELECT * FROM Kana WHERE idseq='{idseq}'")
    kana: list[KanaData] = []
    for kana_row in kana_rows:
        kid = kana_row['ID']
        kni = [r['text'] for r in sqlite_context.select(f"SELECT * FROM KNI WHERE kid='{kid}'")]
        knp = [r['text'] for r in sqlite_context.select(f"SELECT * FROM KNP WHERE kid='{kid}'")]
        knr = [r['text'] for r in sqlite_context.select(f"SELECT * FROM KNR WHERE kid='{kid}'")]
        kana.append(KanaData(
            id=kid,
            idseq=kana_row['idseq'],
            text=kana_row['text'],
            nokanji=kana_row['nokanji'],
            kni=kni,
            knp=knp,
            knr=knr,
        ))
    return kana

def load_sense_data(idseq, sqlite_context: ExecutionContext) -> list[SenseData]:
    sense_rows = sqlite_context.select(f"SELECT * FROM Sense where idseq='{idseq}'")
    senses: list[SenseData] = []
    for sense_row in sense_rows:
        sid = sense_row['ID']
        # grab simple text fields
        stagk = [r['text'] for r in sqlite_context.select(f"SELECT * FROM stagk WHERE sid='{sid}'")]
        stagr = [r['text'] for r in sqlite_context.select(f"SELECT * FROM stagr WHERE sid='{sid}'")]
        pos = [r['text'] for r in sqlite_context.select(f"SELECT * FROM pos WHERE sid='{sid}'")]
        xref = [r['text'] for r in sqlite_context.select(f"SELECT * FROM xref WHERE sid='{sid}'")]
        antonym = [r['text'] for r in sqlite_context.select(f"SELECT * FROM antonym WHERE sid='{sid}'")]
        field = [r['text'] for r in sqlite_context.select(f"SELECT * FROM field WHERE sid='{sid}'")]
        misc = [r['text'] for r in sqlite_context.select(f"SELECT * FROM misc WHERE sid='{sid}'")]
        sense_info = [r['text'] for r in sqlite_context.select(f"SELECT * FROM SenseInfo WHERE sid='{sid}'")]
        dialect = [r['text'] for r in sqlite_context.select(f"SELECT * FROM dialect WHERE sid='{sid}'")]

        # grab SenseSource
        source_rows = sqlite_context.select(f"SELECT * FROM SenseSource WHERE sid='{sid}'")
        sources: list[SenseSourceData] = []
        for source_row in source_rows:
            sources.append(SenseSourceData(
                sid=sid,
                text=source_row['text'],
                lang=source_row['lang'],
                lstype=source_row['lstype'],
                wasei=source_row['wasei'],
            ))

        # grab SenseGloss
        gloss_rows = sqlite_context.select(f"SELECT * FROM SenseGloss WHERE sid='{sid}'")
        glosses: list[SenseGlossData] = []
        for gloss_row in gloss_rows:
            glosses.append(SenseGlossData(
                sid=sid,
                text=gloss_row['text'],
                lang=gloss_row['lang'],
                gend=gloss_row['gend'],
            ))

        # form object and append
        senses.append(SenseData(
            id=sid,
            idseq=idseq,
            stagk=stagk,
            stagr=stagr,
            pos=pos,
            xref=xref,
            antonym=antonym,
            field=field,
            misc=misc,
            sense_info=sense_info,
            dialect=dialect,
            gloss=glosses,
            source=sources
        ))
    return senses

def load_vocab_data(idseq: str, sqlite_context: ExecutionContext) -> VocabData:
    # fetch data from each set of tables
    links = load_link_data(idseq, sqlite_context)
    bibs = load_bib_data(idseq, sqlite_context)
    etyms = load_etym_data(idseq, sqlite_context)
    audits = load_audit_data(idseq, sqlite_context)
    kanji = load_kanji_data(idseq, sqlite_context)
    kana = load_kana_data(idseq, sqlite_context)
    senses = load_sense_data(idseq, sqlite_context)

    # build final object
    return VocabData(
        link=links,
        bib=bibs,
        etym=etyms,
        audit=audits,
        kanji=kanji,
        kana=kana,
        senses=senses,
    )

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