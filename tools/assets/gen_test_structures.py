"""Writes the GameTest arena structure (gzipped NBT): a 41x24x41 box with a Void Stone Brick floor.

    python3 tools/assets/gen_test_structures.py
"""
import gzip
import os
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src", "main", "resources", "data", "aetherfall", "structures", "gametest", "arena.nbt")
DATA_VERSION = 3465  # Minecraft 1.20.1

TAG_END, TAG_INT, TAG_STRING, TAG_LIST, TAG_COMPOUND = 0, 3, 8, 9, 10


def name(n):
    b = n.encode()
    return struct.pack(">H", len(b)) + b


def payload(tag, value):
    if tag == TAG_INT:
        return struct.pack(">i", value)
    if tag == TAG_STRING:
        return name(value)
    if tag == TAG_LIST:
        elem_tag, items = value
        return struct.pack(">bi", elem_tag if items else TAG_END, len(items)) + b"".join(payload(elem_tag, i) for i in items)
    if tag == TAG_COMPOUND:
        return b"".join(struct.pack(">b", t) + name(k) + payload(t, v) for k, (t, v) in value.items()) + b"\x00"
    raise ValueError(tag)


def main(size=(41, 24, 41)):
    sx, sy, sz = size
    blocks = [{"pos": (TAG_LIST, (TAG_INT, [x, 0, z])), "state": (TAG_INT, 0)} for x in range(sx) for z in range(sz)]
    root = {
        "DataVersion": (TAG_INT, DATA_VERSION),
        "size": (TAG_LIST, (TAG_INT, list(size))),
        "palette": (TAG_LIST, (TAG_COMPOUND, [{"Name": (TAG_STRING, "aetherfall:void_stone_bricks")}])),
        "blocks": (TAG_LIST, (TAG_COMPOUND, blocks)),
        "entities": (TAG_LIST, (TAG_COMPOUND, [])),
    }
    data = struct.pack(">b", TAG_COMPOUND) + name("") + payload(TAG_COMPOUND, root)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.open(OUT, "wb") as f:
        f.write(data)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
