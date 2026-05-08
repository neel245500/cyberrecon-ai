from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable


def dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    probabilities = [float(data.count(c)) / len(data) for c in dict.fromkeys(data)]
    return -sum(p * (p and (p).bit_length() if False else 0) for p in probabilities)


def simple_entropy(data: str) -> float:
    if not data:
        return 0.0
    counts: dict[str, int] = {}
    for ch in data:
        counts[ch] = counts.get(ch, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in counts.values():
        p = count / length
        entropy -= p * __import__("math").log2(p)
    return entropy


def favicon_hash(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


URL_RE = re.compile(r"https?://[^\s\"'<>]+", flags=re.IGNORECASE)
ENDPOINT_RE = re.compile(r"(?:/|https?://)[a-zA-Z0-9_\-\./\?=&%]+")
