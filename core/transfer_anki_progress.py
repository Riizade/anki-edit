from __future__ import annotations
import core.anki_connect as anki_connect
from tqdm import tqdm
from core.utils import pprint_data
import genanki

def transfer_progress_anki_connect(source_deck: str, source_field: str, destination_deck: str, destination_field: str) -> None:
    print(f"transferring progress from {source_deck} to {destination_deck}", flush=True)
    print(f"fetching source deck {source_deck}", flush=True)
    source_cards = anki_connect.get_cards_info(source_deck)
    print(f"fetching destination deck {destination_deck}", flush=True)
    destination_cards = anki_connect.get_cards_info(destination_deck)

    print("looking through destination deck", flush=True)
    # build a map of key -> card for destination cards
    destination_cards_map = {}
    for destination_card in destination_cards:
        key = destination_card["fields"][destination_field]["value"]
        destination_cards_map[key] = destination_card

    progress_fields = ['reps', 'lapses', 'left', 'type', 'due', 'factor', 'queue', 'ivl']

    print("transferring progress via ankiconnect", flush=True)
    count = 0
    # look through the source deck
    for source_card in tqdm(source_cards):
        # skip non-well-formed cards
        if source_field not in source_card['fields']:
            continue
        # skip 'new' cards
        if source_card['type'] == 0:
            continue
        key = source_card["fields"][source_field]["value"]
        # if a card in the source deck matches a card in the destination deck
        if key in destination_cards_map:
            count += 1
            # get destination card id
            card_id = destination_cards_map[key]['cardId']
            # build a map of updated field values
            updated_fields = {}
            for field in progress_fields:
                # need to special case ivl because the name differs between AnkiConnect and the underlying Anki Python library
                if field == 'ivl':
                    internal_field = 'interval'
                else:
                    internal_field = field
                updated_fields[field] = source_card[internal_field]

            # use anki connect to update the progress fields in the destination deck
            anki_connect.set_card_values(card_id, updated_fields)

    print(f"updated {count} cards", flush=True)






