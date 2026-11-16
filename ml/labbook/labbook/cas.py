"""Content-addressed store (ledger row 1).

Artifacts live as bytes in a SHA-256 content-addressed store, prefix-sharded
`store/<sha256[0:2]>/<sha256>` (Metaflow's 2-hex sharding, DVC's cache
layout — both validated). Records reference hashes; bytes never enter git.

Durability rule (§2.3): the CAS is a first-class store, not a cache. A read
whose bytes are missing or whose hash does not verify fails loudly, by hash.
"""

import hashlib
import os
import tempfile

from .errors import IntegrityError, MissingBytesError


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class CAS:
    """SHA-256 content-addressed byte store on the local filesystem.

    The interface is a path-mapping: an object store can replace the
    filesystem behind the same three operations without semantic change.
    """

    def __init__(self, root: str):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def path(self, content_hash: str) -> str:
        return os.path.join(self.root, content_hash[:2], content_hash)

    def has(self, content_hash: str) -> bool:
        return os.path.exists(self.path(content_hash))

    def put(self, data: bytes) -> str:
        """Store bytes, returning their SHA-256. Idempotent (dedup falls
        out of content addressing — row 1)."""
        content_hash = sha256_bytes(data)
        dest = self.path(content_hash)
        if not os.path.exists(dest):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            # Write-then-rename so a killed writer never leaves a partial
            # object under a final hash name.
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dest))
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                os.replace(tmp, dest)
            except BaseException:
                if os.path.exists(tmp):
                    os.unlink(tmp)
                raise
        return content_hash

    def get(self, content_hash: str) -> bytes:
        """Read bytes, verifying the hash on every read. Missing bytes and
        hash mismatches are loud failures, named by hash."""
        dest = self.path(content_hash)
        if not os.path.exists(dest):
            raise MissingBytesError(
                "content-addressed bytes are missing from the store",
                value=content_hash,
                expected="bytes present at store/<sha256[0:2]>/<sha256>",
                fix="restore the object from a bundle or backup; a pointer "
                "without bytes is a broken record, never a silent skip",
            )
        with open(dest, "rb") as f:
            data = f.read()
        actual = sha256_bytes(data)
        if actual != content_hash:
            raise IntegrityError(
                "stored bytes do not match their content hash",
                value={"recorded": content_hash, "actual": actual},
                expected="sha256(bytes) == recorded hash",
                fix="treat the object as corrupt; restore from a bundle or backup",
            )
        return data
