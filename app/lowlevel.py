"""Fixed frame writer and durable tail repair for the local journal."""
import hashlib
import json
import os
import struct

MAX_PAYLOAD = 1024 * 1024

def encode_frame(value):
    payload = json.dumps(value, ensure_ascii=True, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    if not 0 < len(payload) <= MAX_PAYLOAD:
        raise ValueError("frame size")
    return struct.pack(">I", len(payload)) + payload + hashlib.sha256(payload).digest()

def append_frame(path, value, hook=None):
    frame = encode_frame(value)
    created = not path.exists()
    with path.open("ab", buffering=0) as stream:
        if hook:
            hook("before_write")
        view = memoryview(frame)
        while view:
            count = stream.write(view)
            if count is None or count <= 0:
                raise OSError("short write")
            view = view[count:]
        if hook:
            hook("after_write")
        os.fsync(stream.fileno())
        if created and os.name == "posix":
            descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        if hook:
            hook("after_sync")

def trim_tail(path, length):
    with path.open("r+b", buffering=0) as stream:
        stream.truncate(length)
        os.fsync(stream.fileno())
