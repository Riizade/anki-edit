from ankisync2 import Apkg
import sys

def transfer():
    # load the deck that contains user progress (source)

    # load the deck to transfer to (destination)

    # match notes from source to destination

    # convert progress from each note

    # save the updated destination deck

    # ---
    apkg = Apkg("scratch/N0.apkg")
    count = 0
    for note in apkg.db.Notes:
        count += 1
    print(count)
    for note in apkg.db.Notes:
        sys.stdout.buffer.write(str(note.tags).encode("utf-8"))
        sys.stdout.buffer.write("\n".encode('utf-8'))
        if note.tags == None:
            note.tags.null = False

    apkg.export("scratch/N0-updated.apkg")