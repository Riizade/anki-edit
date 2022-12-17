from jamdict import Jamdict
import sys
from dataclasses import dataclass
from pprint import pformat

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

# the "...Data" classes below represent the raw data structure of the vocabulary database (JMDict)

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
class EtymData:
    idseq: str
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
    etym: list[EtymData]
    audit: list[AuditData]
    kanji: list[KanjiData]
    kana: list[KanaData]
    senses: list[SenseData]

def load_all_vocab():
    # initialize SQLite context
    jam = Jamdict()
    sqlite_context = jam.kd2.ctx()

    # fetch ids for each entry
    entry_rows = sqlite_context.select("SELECT * FROM Entry")
    entry_ids = [row['idseq'] for row in entry_rows]

    # build the raw VocabData object for each entry
    # TODO
    for id in entry_ids:
        pass

        # self.add_table('Link', ['ID', 'idseq', 'tag', 'desc', 'uri'])
        # self.add_table('Bib', ['ID', 'idseq', 'tag', 'text'])
        # self.add_table('Etym', ['idseq', 'text'])
        # self.add_table('Audit', ['idseq', 'upd_date', 'upd_detl'])
        # # Kanji
        # self.add_table('Kanji', ['ID', 'idseq', 'text'])
        # self.add_table('KJI', ['kid', 'text'])
        # self.add_table('KJP', ['kid', 'text'])
        # # Kana
        # self.add_table('Kana', ['ID', 'idseq', 'text', 'nokanji'])
        # self.add_table('KNI', ['kid', 'text'])
        # self.add_table('KNP', ['kid', 'text'])
        # self.add_table('KNR', ['kid', 'text'])
        # # Senses
        # self.add_table('Sense', ['ID', 'idseq'])
        # self.add_table('stagk', ['sid', 'text'])
        # self.add_table('stagr', ['sid', 'text'])
        # self.add_table('pos', ['sid', 'text'])
        # self.add_table('xref', ['sid', 'text'])
        # self.add_table('antonym', ['sid', 'text'])
        # self.add_table('field', ['sid', 'text'])
        # self.add_table('misc', ['sid', 'text'])
        # self.add_table('SenseInfo', ['sid', 'text'])
        # self.add_table('SenseSource', ['sid', 'text', 'lang', 'lstype', 'wasei'])
        # self.add_table('dialect', ['sid', 'text'])
        # self.add_table('SenseGloss', ['sid', 'lang', 'gend', 'text'])
