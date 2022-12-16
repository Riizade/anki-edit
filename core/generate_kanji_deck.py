from jamdict import Jamdict
import sys

def generate():
    jam = Jamdict()
    sqlite_context = jam.kd2.ctx()
    rows = sqlite_context.select("SELECT * FROM character")
    for row in rows:
        if row['freq'] is not None:
            for field in ['ID', 'literal', 'stroke_count', 'grade', 'freq', 'jlpt']:
                    sys.stdout.buffer.write((str(row[field]) + " ").encode("utf8"))
            sys.stdout.buffer.write("\n".encode("utf8"))