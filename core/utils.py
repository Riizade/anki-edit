from dataclasses_serialization.json import JSONSerializer
from pathlib import Path
import sys
from pprint import pformat

# takes basic collections (e.g., list, dict) and dataclasses as data
def save_to_cache(data, cache_path: Path):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    bytes = JSONSerializer.serialize(data)
    with open(cache_path, 'wb') as f:
        f.write(bytes)

def load_from_cache(type, cache_path: Path) -> any:
    with open(cache_path, 'rb') as f:
        return JSONSerializer.deserialize(type, f.read())

def cached_load(load_function: callable, type, cache_path: Path) -> any:
    if cache_path.exists() and cache_path.is_file():
        return load_from_cache(type, cache_path)
    else:
        data = load_function()
        save_to_cache(data, cache_path)
        return data

def pprint_data(data):
    sys.stdout.buffer.write(pformat(data).encode("utf8"))
    sys.stdout.buffer.write("\n".encode("utf8"))