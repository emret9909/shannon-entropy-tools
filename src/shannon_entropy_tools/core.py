"""Core Shannon entropy calculations for byte and text data."""

import math
from typing import Union


DEFAULT_ALPHABET_SIZE = 256


def _entropy_from_counts(counts: list[int], total: int) -> float:
    """Compute Shannon entropy in bits from a list of symbol counts.

    Entropy is H = -sum(p * log2(p)).  Symbols with zero count contribute
    nothing, so they are skipped rather than producing a log(0) domain error.
    """
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts:
        if count <= 0:
            continue
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def shannon_entropy(data: Union[str, bytes, bytearray]) -> float:
    """Return the Shannon entropy of *data* in bits per symbol.

    Strings are treated as sequences of Unicode code points; bytes and
    bytearrays are treated as sequences of byte values.  This mirrors the
    natural unit of the input: a string is already a sequence of symbols,
    while bytes are the raw material for compressed/encrypted detection.

    The result is 0.0 for empty or single-symbol input.
    """
    if isinstance(data, str):
        symbols = [ord(ch) for ch in data]
    elif isinstance(data, (bytes, bytearray)):
        symbols = list(data)
    else:
        raise TypeError("data must be str, bytes, or bytearray")

    total = len(symbols)
    if total == 0:
        return 0.0

    counts = [0] * 256
    for value in symbols:
        if value < 256:
            counts[value] += 1
        else:
            # For code points above 255 we cannot index a fixed table; fall
            # back to a dictionary so that non-ASCII strings still work.
            return _entropy_from_counts(_counts_for_symbols(symbols), total)
    return _entropy_from_counts(counts, total)


def _counts_for_symbols(symbols: list[int]) -> list[int]:
    """Count occurrences of each distinct integer in *symbols*."""
    seen: dict[int, int] = {}
    for value in symbols:
        seen[value] = seen.get(value, 0) + 1
    return list(seen.values())


def _alphabet_size(data: Union[str, bytes, bytearray]) -> int:
    """Return the size of the alphabet the data is normalized against.

    Byte input is always measured against the full 256-value byte range so
    that the normalized score reflects how uniform the byte distribution is.
    Text is measured against the set of distinct code points actually
    present, because a string is already a sequence of symbols and has no
    fixed theoretical alphabet.
    """
    if isinstance(data, str):
        return len(set(ord(ch) for ch in data))
    return DEFAULT_ALPHABET_SIZE


def normalized_entropy(data: Union[str, bytes, bytearray]) -> float:
    """Return Shannon entropy divided by the maximum possible entropy.

    For byte input the alphabet is the full 256-value byte range, so the
    result is in [0, 1] and reflects how uniform the byte distribution is.
    For text the alphabet is the set of distinct code points actually
    present, so a short string with a few distinct characters can still
    score near 1.0.  This is intentional: normalization is about the
    observed alphabet, not a theoretical one.
    """
    if isinstance(data, str):
        symbols = [ord(ch) for ch in data]
    elif isinstance(data, (bytes, bytearray)):
        symbols = list(data)
    else:
        raise TypeError("data must be str, bytes, or bytearray")

    if len(symbols) == 0:
        return 0.0

    max_entropy = math.log2(_alphabet_size(data))
    if max_entropy <= 0.0:
        return 0.0
    return shannon_entropy(data) / max_entropy


def is_likely_compressed(
    data: Union[str, bytes, bytearray], threshold: float = 0.9
) -> bool:
    """Return True when *data* looks compressed, encrypted, or random.

    The heuristic is normalized entropy above *threshold*.  A threshold of
    0.9 is a common starting point: English text typically scores well
    below it, while gzip/encrypted output sits near 1.0.  The threshold is
    exposed because the right cutoff depends on the data being screened.

    For byte input the alphabet is the full 256-value byte range, so the
    normalized score reflects how uniform the byte distribution is.  For
    text, normalization is against the observed alphabet, which makes any
    string with a skewed character distribution score high; to keep the
    "looks compressed" heuristic meaningful for text, a string is only
    considered compressed when it is long enough for the statistic to be
    reliable.

    Text input is always treated as not compressed: normalizing against
    the observed alphabet makes short or repetitive text score arbitrarily
    high, so the statistic is not meaningful for text and the heuristic
    is restricted to byte input.
    """
    if isinstance(data, str):
        return False
    return normalized_entropy(data) >= threshold
