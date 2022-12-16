from jamdict import Jamdict
import sys

def generate():
    jam = Jamdict()
    for kanji in jam.kd2.all_ne_type():
        sys.stdout.buffer.write(kanji)
        sys.stdout.buffer.write("\n".encode("utf8"))

    for kanji in jam.kd2.all_pos():
        sys.stdout.buffer.write(kanji)
        sys.stdout.buffer.write("\n".encode("utf8"))