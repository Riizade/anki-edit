import requests
import json

anki_connect_host = "http://localhost:8765"
anki_connect_version = 6

# documentation: https://foosoft.net/projects/anki-connect/index.html#note-actions

def get_deck_names_and_ids() -> dict[str, int]:
    return ankiconnect_action("deckNamesAndIds")['result']

# deck name to list of note ids
def get_notes_in_deck(deck_name: str) -> list[int]:
    return ankiconnect_action(
        action="findNotes",
        params={
            "query": f"deck:\"{deck_name}\""
        }
    )['result']

# note ids to note info
def get_note_info(note_ids: list[int]) -> list[dict]:
    return ankiconnect_action(
        action="notesInfo",
        params={
            "notes": note_ids,
        }
    )['result']


def update_note_field(note_id: int, field_name: str, new_value: str):
    ankiconnect_action(
        action="updateNoteFields",
        params={
            "note": {
                "id": note_id,
                "fields": {
                    field_name: new_value,
                }
            }
        }
    )


def ankiconnect_action(action: str, params: dict | None = None) -> dict:
    if params is None:
        data = {
            "action": action,
            "version": anki_connect_version,
        }
    else:
        data = {
            "action": action,
            "version": anki_connect_version,
            "params": params,
        }
    response = requests.post(url=anki_connect_host, json=data)
    return json.loads(response.text)