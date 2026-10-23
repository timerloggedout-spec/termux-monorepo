#!/usr/bin/env python3
"""Encrypt a private archive with age and JIT-stream it without plaintext files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

ARCHIVE_SCHEMA_VERSION = 1
TELEMETRY_SCHEMA_VERSION = 1
MAX_HEADER_BYTES = 4096
SHA256_RE = re.compile(r'[0-9a-f]{64}\Z')


class ArchiveError(Exception):
    pass


def _private_output(path):
    path = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags, 0o600)
    return os.fdopen(fd, 'wb')


def _regular_file(path, *, identity=False):
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ArchiveError('expected a regular non-symlink file')
    if identity and stat.S_IMODE(info.st_mode) & 0o077:
        raise ArchiveError('identity file permissions must be private')
    return path


def _outside_git(path):
    resolved = Path(path).resolve()
    for parent in (resolved.parent, *resolved.parents):
        marker = parent / '.git'
        if marker.exists() or marker.is_symlink():
            raise ArchiveError('archive output must be outside Git worktrees')
    return resolved


def _identity_outside_git(path):
    resolved = Path(path).resolve(strict=True)
    try:
        _outside_git(resolved)
    except ArchiveError as error:
        raise ArchiveError('identity file must be outside Git worktrees') from error
    return resolved


def _terminate(process):
    if process.stdin is not None and not process.stdin.closed:
        try:
            process.stdin.close()
        except OSError:
            pass
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def _header_for(source):
    digest = hashlib.sha256()
    size = 0
    source.seek(0)
    while True:
        chunk = source.read(65536)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    source.seek(0)
    return {'archive_schema_version': ARCHIVE_SCHEMA_VERSION,
            'telemetry_schema_version': TELEMETRY_SCHEMA_VERSION,
            'payload_sha256': digest.hexdigest(), 'payload_bytes': size}


def encrypt_archive(source_path, output_path, *, recipient, age_binary='age'):
    """Encrypt a file; the authenticated plaintext starts with a schema/hash header."""
    if not isinstance(recipient, str) or not recipient.strip():
        raise ArchiveError('AGE_RECIPIENT is required')
    source_path = _regular_file(source_path)
    output_path = _outside_git(output_path)
    if source_path.resolve() == output_path.resolve():
        raise ArchiveError('source and output must differ')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    created_identity = None
    success = False
    process = None
    try:
        with source_path.open('rb') as source:
            header = _header_for(source)
            encoded_header = (json.dumps(header, sort_keys=True, separators=(',', ':')) + '\n').encode('ascii')
            with _private_output(output_path) as encrypted:
                info = os.fstat(encrypted.fileno())
                created_identity = (info.st_dev, info.st_ino)
                process = subprocess.Popen([age_binary, '-r', recipient], stdin=subprocess.PIPE,
                                           stdout=encrypted, stderr=subprocess.DEVNULL)
                try:
                    process.stdin.write(encoded_header)
                    streamed_digest = hashlib.sha256()
                    streamed_size = 0
                    while True:
                        chunk = source.read(65536)
                        if not chunk:
                            break
                        streamed_digest.update(chunk)
                        streamed_size += len(chunk)
                        process.stdin.write(chunk)
                    process.stdin.close()
                    if (streamed_size != header['payload_bytes']
                            or streamed_digest.hexdigest() != header['payload_sha256']):
                        raise ArchiveError('source changed during encryption')
                    code = process.wait()
                except BaseException:
                    _terminate(process)
                    raise
                encrypted.flush()
                os.fsync(encrypted.fileno())
                if code != 0:
                    raise ArchiveError('age encryption failed')
        success = True
        return header
    except BaseException:
        if process is not None and process.poll() is None:
            _terminate(process)
        if not success and created_identity is not None:
            try:
                current = output_path.lstat()
                if (current.st_dev, current.st_ino) == created_identity:
                    output_path.unlink()
            except FileNotFoundError:
                pass
        raise


def _read_archive_header(stream):
    line = stream.readline(MAX_HEADER_BYTES + 1)
    if len(line) > MAX_HEADER_BYTES or not line.endswith(b'\n'):
        raise ArchiveError('invalid or oversized archive header')
    try:
        header = json.loads(line.decode('ascii'),
                            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise ArchiveError('invalid archive header') from error
    if not isinstance(header, dict) or set(header) != {
            'archive_schema_version', 'telemetry_schema_version', 'payload_sha256', 'payload_bytes'}:
        raise ArchiveError('invalid archive header fields')
    if header.get('archive_schema_version') != ARCHIVE_SCHEMA_VERSION:
        raise ArchiveError('unsupported archive schema version')
    telemetry_version = header.get('telemetry_schema_version')
    if type(telemetry_version) is not int or telemetry_version < 1 or telemetry_version > 2**31 - 1:
        raise ArchiveError('invalid telemetry schema version')
    if not isinstance(header.get('payload_sha256'), str) or not SHA256_RE.fullmatch(header['payload_sha256']):
        raise ArchiveError('invalid payload digest')
    if type(header.get('payload_bytes')) is not int or not 0 <= header['payload_bytes'] <= 2**63 - 1:
        raise ArchiveError('invalid payload size')
    return header


def _write_all(sink, chunk):
    view = memoryview(chunk)
    while view:
        written = sink(view)
        if written is None:
            return
        if written <= 0:
            raise ArchiveError('consumer stopped accepting plaintext')
        view = view[written:]


def decrypt_archive(input_path, identity_path, sink, *, age_binary='age'):
    """Decrypt through pipes, validate the encrypted envelope, and stream only payload bytes."""
    input_path = _regular_file(input_path)
    identity_path = _regular_file(identity_path, identity=True)
    identity_path = _identity_outside_git(identity_path)
    process = subprocess.Popen([age_binary, '-d', '-i', str(identity_path), str(input_path)],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    digest = hashlib.sha256()
    size = 0
    try:
        header = _read_archive_header(process.stdout)
        while True:
            chunk = process.stdout.read(65536)
            if not chunk:
                break
            size += len(chunk)
            if size > header['payload_bytes']:
                raise ArchiveError('archive payload exceeds declared size')
            digest.update(chunk)
            _write_all(sink, chunk)
        code = process.wait()
        if code != 0:
            raise ArchiveError('age decryption or authentication failed')
        if size != header['payload_bytes'] or digest.hexdigest() != header['payload_sha256']:
            raise ArchiveError('archive payload integrity check failed')
        return header
    except BaseException:
        if process.poll() is None:
            try:
                process.stdout.close()
            except OSError:
                pass
            _terminate(process)
        raise
    finally:
        if process.stdout is not None and not process.stdout.closed:
            process.stdout.close()


def compare_archive_headers(left, right):
    """Compare local-only metadata after both encrypted archives were verified."""
    same_payload = (left['payload_sha256'] == right['payload_sha256']
                    and left['payload_bytes'] == right['payload_bytes'])
    return {'left_archive_schema_version': left['archive_schema_version'],
            'right_archive_schema_version': right['archive_schema_version'],
            'left_telemetry_schema_version': left['telemetry_schema_version'],
            'right_telemetry_schema_version': right['telemetry_schema_version'],
            'telemetry_schema_changed': left['telemetry_schema_version'] != right['telemetry_schema_version'],
            'payload_bytes_equal': left['payload_bytes'] == right['payload_bytes'],
            'payload_sha256_equal': left['payload_sha256'] == right['payload_sha256'],
            'payload_equal': same_payload}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='operation', required=True)
    encrypt = commands.add_parser('encrypt', help='Encrypt a private file using AGE_RECIPIENT')
    encrypt.add_argument('--input', required=True)
    encrypt.add_argument('--output', required=True)
    decrypt = commands.add_parser('decrypt', help='JIT-decrypt using AGE_IDENTITY_FILE without plaintext files')
    decrypt.add_argument('--input', required=True)
    decrypt.add_argument('--consumer', nargs=argparse.REMAINDER,
                         help='Optional exact command to receive plaintext on stdin')
    compare = commands.add_parser('compare', help='Verify and compare two archives without storing plaintext')
    compare.add_argument('--left', required=True)
    compare.add_argument('--right', required=True)
    args = parser.parse_args()
    age_binary = os.environ.get('AGE_BINARY', 'age')
    try:
        if args.operation == 'encrypt':
            recipient = os.environ.get('AGE_RECIPIENT')
            encrypt_archive(args.input, args.output, recipient=recipient, age_binary=age_binary)
            print('Encrypted archive created; no plaintext copy was removed.')
            return 0
        identity = os.environ.get('AGE_IDENTITY_FILE')
        if not identity:
            raise ArchiveError('AGE_IDENTITY_FILE is required')
        if args.operation == 'compare':
            discard = lambda chunk: len(chunk)
            left = decrypt_archive(args.left, identity, discard, age_binary=age_binary)
            right = decrypt_archive(args.right, identity, discard, age_binary=age_binary)
            print(json.dumps(compare_archive_headers(left, right), sort_keys=True))
            return 0
        consumer = list(args.consumer or [])
        if consumer and consumer[0] == '--':
            consumer = consumer[1:]
        if consumer:
            target = subprocess.Popen(consumer, stdin=subprocess.PIPE,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                decrypt_archive(args.input, identity, target.stdin.write, age_binary=age_binary)
                target.stdin.close()
                return_code = target.wait()
            except BaseException:
                if target.poll() is None:
                    target.stdin.close()
                    _terminate(target)
                raise
            if return_code != 0:
                raise ArchiveError('consumer exited unsuccessfully')
            print('Archive streamed to consumer; no plaintext file was created.')
        else:
            decrypt_archive(args.input, identity, sys.stdout.buffer.write, age_binary=age_binary)
            sys.stdout.buffer.flush()
        return 0
    except (OSError, ValueError, ArchiveError, subprocess.SubprocessError) as error:
        print(f'Archive operation failed: {error.__class__.__name__}', file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main())
