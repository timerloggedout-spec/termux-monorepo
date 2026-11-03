"""Artifact formats (ledger row 2).

Formats are *declared* in the catalog/record, never inferred silently.
Native, inspectable formats are the default: CSV stays CSV, arrays stay
.npz, metrics stay JSON. Every artifact version names the code that reads
it (`reader`, a module+attribute path — ZenML's materializer take).

`pickle-class` is an explicit, flagged exception (settled default, §4.4
option (a)): allowed, but the ledger records the flag and `verify` checks
for it. It is never a silent default (Metaflow/Dagster's pickle default is
the refused half of row 2).
"""

import csv
import io
import json
import pickle
import struct
import zipfile

from .errors import LabbookError

# ---------------------------------------------------------------- csv
# Value shape: list of dicts (column -> scalar). Numbers are written with
# repr() so they parse back to the identical double; the reader converts
# numeric-looking cells back to int/float. Documented reader behavior.


def write_csv(value) -> bytes:
    rows = list(value)
    if not rows:
        raise LabbookError(
            "cannot write an empty csv artifact",
            expected="at least one row",
            fix="csv artifacts need a header row's worth of data",
        )
    fieldnames = list(rows[0].keys())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for row in rows:
        w.writerow(
            {k: (repr(v) if isinstance(v, float) else v) for k, v in row.items()}
        )
    return buf.getvalue().encode("utf-8")


def _num(cell):
    try:
        return int(cell)
    except (TypeError, ValueError):
        pass
    try:
        return float(cell)
    except (TypeError, ValueError):
        return cell


def read_csv(data: bytes):
    text = data.decode("utf-8")
    rdr = csv.DictReader(io.StringIO(text))
    return [{k: _num(v) for k, v in row.items()} for row in rdr]


# ---------------------------------------------------------------- json


def write_json(value) -> bytes:
    return json.dumps(value, sort_keys=True).encode("utf-8")


def read_json(data: bytes):
    return json.loads(data.decode("utf-8"))


# ---------------------------------------------------------------- text


def write_text(value) -> bytes:
    return str(value).encode("utf-8")


def read_text(data: bytes):
    return data.decode("utf-8")


# ---------------------------------------------------------------- npz
# Minimal .npy/.npz for 1-D float64 arrays, stdlib-only. Value shape:
# {array_name: [float, ...]}. The .npy v1.0 header is a plain dict literal,
# so the artifact stays inspectable without numpy present.


def _npy_bytes(values) -> bytes:
    header = "{'descr': '<f8', 'fortran_order': False, 'shape': (%d,), }" % len(values)
    # Header must pad to a 64-byte-aligned total (magic 6 + ver 2 + len 2).
    total = 10 + len(header) + 1
    pad = (64 - total % 64) % 64
    header = header + " " * pad + "\n"
    return (
        b"\x93NUMPY\x01\x00"
        + struct.pack("<H", len(header))
        + header.encode("latin1")
        + struct.pack("<%dd" % len(values), *values)
    )


def _read_npy(buf: bytes):
    if buf[:6] != b"\x93NUMPY":
        raise LabbookError("npz member is not a .npy payload", value=buf[:6])
    (hlen,) = struct.unpack("<H", buf[8:10])
    header = eval(buf[10 : 10 + hlen].decode("latin1"), {"__builtins__": {}}, {})
    if header.get("descr") != "<f8" or header.get("fortran_order"):
        raise LabbookError(
            "unsupported .npy payload",
            value=header,
            expected="descr '<f8', fortran_order False (the labbook npz subset)",
        )
    (n,) = header["shape"]
    off = 10 + hlen
    return list(struct.unpack("<%dd" % n, buf[off : off + 8 * n]))


def write_npz(value) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, values in value.items():
            z.writestr(name + ".npy", _npy_bytes([float(v) for v in values]))
    return buf.getvalue()


def read_npz(data: bytes):
    out = {}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            out[name[: -len(".npy")]] = _read_npy(z.read(name))
    return out


# ---------------------------------------------------------------- pickle-class
# FLAGGED EXCEPTION. Bytes are opaque and Python-locked by construction;
# the format exists so legacy/model objects can cross a boundary *loudly*:
# the catalog must declare it, the ledger flags it, verify reports it.


def write_pickle(value) -> bytes:
    return pickle.dumps(value, protocol=4)


def read_pickle(data: bytes):
    return pickle.loads(data)


# ---------------------------------------------------------------- registry

FORMATS = {
    "csv": (write_csv, read_csv),
    "json": (write_json, read_json),
    "text": (write_text, read_text),
    "npz": (write_npz, read_npz),
    "pickle-class": (write_pickle, read_pickle),
}

# Formats whose bytes are not inspectable outside Python. Membership here
# is the flag the ledger stamps and verify checks (row 2).
PICKLE_CLASS = {"pickle-class"}


def is_pickle_class(fmt: str) -> bool:
    return fmt in PICKLE_CLASS


_READER_FUNCS = {
    "csv": "read_csv",
    "json": "read_json",
    "text": "read_text",
    "npz": "read_npz",
    "pickle-class": "read_pickle",
}


def reader_path(fmt: str) -> str:
    """The self-description stamped on every materialization (row 2):
    the module+attribute that reads this format."""
    if fmt not in FORMATS:
        raise LabbookError(
            "unknown artifact format",
            value=fmt,
            expected=f"one of {sorted(FORMATS)}",
            fix="declare a supported format in the catalog, or extend "
            "labbook.formats in a new contract version",
        )
    return f"labbook.formats:{_READER_FUNCS[fmt]}"


def write(fmt: str, value) -> bytes:
    if fmt not in FORMATS:
        raise LabbookError(
            "unknown artifact format",
            value=fmt,
            expected=f"one of {sorted(FORMATS)}",
        )
    return FORMATS[fmt][0](value)


def read(fmt: str, data: bytes):
    if fmt not in FORMATS:
        raise LabbookError(
            "unknown artifact format",
            value=fmt,
            expected=f"one of {sorted(FORMATS)}",
        )
    return FORMATS[fmt][1](data)
