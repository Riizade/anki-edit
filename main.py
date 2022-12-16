from ankisync2 import Apkg
import sys


def main():
    apkg = Apkg("scratch/N0.apkg")
    print("bleh")
    for note in apkg.db.Notes:
        sys.stdout.buffer.write(str(note.data).encode("utf-8"))

    apkg.export("scratch/N0-updated.apkg")

if __name__ == "__main__":
    main()