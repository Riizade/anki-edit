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

def load_all_vocab():
    # initialize SQLite context
    jam = Jamdict()
    sqlite_context = jam.kd2.ctx()

    # fetch ids for each entry
    entry_rows = sqlite_context.select("SELECT * FROM Entry")
    entry_ids = [row['idseq'] for row in entry_rows]

    # build the raw VocabData object for each entry
    # TODO
    for idseq in entry_ids:
        # fetch LinkData
        link_rows = sqlite_context.select(f"SELECT * FROM Link WHERE idseq='{idseq}'")
        links: list[LinkData] = []
        for row in link_rows:
            links.append(
                LinkData(
                    id=row['ID'],
                    idseq=row['idseq'],
                    tag=row['tag'],
                    desc=row['desc'],
                    uri=row['uri'],
                )
            )

        # fetch BibData
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

        # fetch Etym
        etym_rows = sqlite_context.select(f"SELECT * FROM Etym WHERE idseq='{idseq}'")
        etyms = [row['text'] for row in etym_rows]

        # fetch AuditData
        audit_rows = sqlite_context.select(f"SELECT * FROM Audit WHERE idseq='{idseq}'")
        audits: list[AuditData] = []
        for row in audit_rows:
            audits.append(AuditData(
                idseq=row['idseq'],
                upd_date=row['upd_date'],
                upd_detl=row['upd_detl'],
            ))

        # fetch KanjiData
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

        # fetch KanaData
        kana_rows = sqlite_context.select(f"SELECT * FROM Kana WHERE idseq='{idseq}'")
        # TODO

        # fetch SenseData
        sense_rows = sqlite_context.select(f"SELECT * FROM Sense where idseq='{idseq}'")
        senses: list[SenseData] = []
        for sense_row in sense_rows:
            sid = sense_row['ID']
            # TODO




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
