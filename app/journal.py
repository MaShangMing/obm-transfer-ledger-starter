"""Current snapshot journal reader; used by Store at startup."""
import json
import struct
from lowlevel import append_frame

def read_records(path):
    if not path.exists():
        return []
    records = []
    with path.open("rb") as stream:
        while header := stream.read(4):
            if len(header) != 4:
                break
            size = struct.unpack(">I", header)[0]
            payload = stream.read(size)
            trailer = stream.read(32)
            if len(payload) != size or len(trailer) != 32:
                break
            records.append(json.loads(payload))
    return records

def save(path, record, hook=None):
    append_frame(path, record, hook)
