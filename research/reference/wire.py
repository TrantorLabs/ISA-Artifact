"""Strict, dependency-free ISA/1 interchange. No inference lives here."""
from __future__ import annotations
import hashlib
import re
from collections.abc import Mapping

MAX_BYTES = 1_048_576
MAX_FIELDS = 4096
KEY = re.compile(r"[a-z][a-z0-9_.-]{0,159}\Z")
CHANNELS = ('decision', 'source', 'authority', 'effect', 'evaluation', 'program', 'admission', 'execution', 'lineage')
QUERIES = ('path', 'source', 'authority', 'effect', 'control', 'eligibility')
KINDS = ('recipient', 'transaction', 'dual', 'channel')
REQUIRES = {
    'path': ('decision', 'admission', 'execution'),
    'source': ('source',), 'authority': ('authority',), 'effect': ('effect', 'admission'),
    'control': ('evaluation', 'program', 'admission'),
    'eligibility': ('evaluation', 'program', 'admission'),
}

class WireError(ValueError):
    pass

def dump(doc: Mapping[str, str]) -> bytes:
    rows = ['ISA/1']
    if len(doc) > MAX_FIELDS:
        raise WireError('too many fields')
    for key, value in sorted(doc.items()):
        if not KEY.fullmatch(key) or not isinstance(value, str):
            raise WireError('invalid key or value type')
        rows.append(key + '\t' + value.encode('utf-8').hex())
    rows.append('END')
    result = ('\n'.join(rows) + '\n').encode('ascii')
    if len(result) > MAX_BYTES:
        raise WireError('document too large')
    return result

def load(data: bytes) -> dict[str, str]:
    if len(data) > MAX_BYTES:
        raise WireError('document too large')
    try:
        lines = data.decode('ascii').splitlines()
    except UnicodeError as exc:
        raise WireError('wire envelope must be ASCII') from exc
    if len(lines) < 2 or lines[0] != 'ISA/1' or lines[-1] != 'END':
        raise WireError('missing framing')
    if len(lines) - 2 > MAX_FIELDS:
        raise WireError('too many fields')
    result: dict[str, str] = {}
    for line in lines[1:-1]:
        parts = line.split('\t')
        if len(parts) != 2 or not KEY.fullmatch(parts[0]) or parts[0] in result:
            raise WireError('invalid or duplicate field')
        key, encoded = parts
        if len(encoded) % 2 or not re.fullmatch('[0-9a-f]*', encoded):
            raise WireError('noncanonical hexadecimal value')
        try:
            result[key] = bytes.fromhex(encoded).decode('utf-8')
        except UnicodeError as exc:
            raise WireError('invalid UTF-8 value') from exc
    return result

def digest(doc: Mapping[str, str]) -> str:
    return hashlib.sha256(dump(doc)).hexdigest()

def channel(doc: Mapping[str, str], name: str) -> dict[str, str]:
    return {k: v for k, v in doc.items() if k.startswith(name + '.')}

def csv(value: str) -> tuple[str, ...]:
    return tuple(x for x in value.split(',') if x)

def bool_value(value: str) -> bool:
    if value not in ('0', '1'):
        raise WireError('invalid Boolean')
    return value == '1'

def integer(value: str, upper: int = 1_000_000_000) -> int:
    if not re.fullmatch(r'0|[1-9][0-9]*', value):
        raise WireError('invalid unsigned integer')
    number = int(value)
    if number > upper:
        raise WireError('integer outside declared bound')
    return number
