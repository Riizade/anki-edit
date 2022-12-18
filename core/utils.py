from dataclasses_serialization.bson import BSONSerializer
from pathlib import Path

# takes basic collections (e.g., list, dict) and dataclasses as data
def save_to_cache(data, cache_path: Path):
    bytes = BSONSerializer.serialize(data)
    with open(cache_path, 'wb') as f:
        f.write(bytes)

def load_from_cache(cache_path: Path) -> any:
    with open(cache_path, 'rb') as f:
        return BSONSerializer.deserialize(f.read())

def cached_load(load_function: callable, cache_path: Path) -> any:
    if cache_path.exists() and cache_path.is_file():
        return load_from_cache(cache_path)
    else:
        data = load_function()
        save_to_cache(data, cache_path)
        return data