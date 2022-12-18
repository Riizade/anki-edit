from core.kanji import load_all_kanji_uncached, Kanji
import core.anki_connect as anki
from tqdm import tqdm


# replaces the examples field with examples taken from JMDict
def augment_examples(deck_name: str, kanji_field: str, examples_field: str):

    response = anki.get_deck_names_and_ids()
    deck_id = response.get(deck_name, None)
    if deck_id is None:
        raise RuntimeError(f"No deck with name {deck_name}")


    print("fetching note info via API...")
    note_ids = anki.get_notes_in_deck(deck_name)
    note_infos = anki.get_note_info(note_ids)

    all_kanji: list[Kanji] = load_all_kanji_uncached()

    # build lookup map for kanji
    kanji_map: dict[str, Kanji] = {}
    for kanji in all_kanji:
        kanji_map[kanji.character] = kanji

    # update note values with additional examples
    print("updating notes...")
    for note in tqdm(note_infos):
        kanji_char = note['fields'][kanji_field]['value']
        kanji_data = kanji_map.get(kanji_char, None)
        if kanji_data is not None:
            new_text = new_examples_text(kanji_data)
            old_text = note['fields'][examples_field]['value']
            updated_text = "----- new examples -----\n</br>\n</br>" + new_text + "\n</br>\n</br>----- old examples -----\n</br>\n</br>" + old_text
            anki.update_note_field(note['noteId'], examples_field, updated_text)

def new_examples_text(kanji_data: Kanji) -> str:
    str = ""
    # for each example
    for example in kanji_data.example_words:
        # look at each kanji form
        for idx, form in enumerate(example.kanji_forms):
            # if the relevant kanji is in the given form, add that writing as an example entry
            if kanji_data.character in form.text:
                # collect glossary entries (potential translations)
                glosses: list[str] = []
                for sense in example.senses:
                    for gloss in sense.gloss:
                        glosses.append(gloss.text)
                gloss_text = ", ".join(glosses)
                kana_idx = idx
                # TODO: this is probably wrong; the relationship between kana and kanji forms is unclear
                if kana_idx >= len(example.kana_forms):
                    kana_idx = 0
                str += f"{example.kanji_forms[idx]} ({example.kana_forms[kana_idx]}): {gloss_text}\n</br>"
    return str
