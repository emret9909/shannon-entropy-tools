# shannon-entropy-tools

A small, dependency-free library for computing the Shannon entropy of strings and byte sequences, and for flagging data that looks compressed, encrypted, or random.

## Usage

```python
from shannon_entropy_tools import (
    shannon_entropy,
    normalized_entropy,
    is_likely_compressed,
)

# Bits per symbol
shannon_entropy("abcd")          # 2.0
shannon_entropy(b"\x00\xff")     # 1.0

# Entropy scaled to [0, 1] against the observed alphabet
normalized_entropy(b"hello")     # well below 1.0
normalized_entropy(bytes(range(256)))  # 1.0

# Heuristic check
is_likely_compressed(bytes(range(256)))  # True
is_likely_compressed(b"hello world")     # False
```

## Why this exists

When you are scanning file contents or network payloads, one of the fastest signals that a chunk is compressed, encrypted, or random is that its byte distribution is nearly uniform. Shannon entropy measures exactly that. This library gives you the raw entropy in bits per symbol, a normalized version for comparing inputs of different alphabet sizes, and a one-line threshold check.

The trade-off: entropy is a statistical property, not a proof. A base64-encoded text file can look nearly uniform without being compressed, and a short compressed payload may not have enough bytes to push the entropy high. The library therefore exposes the threshold and leaves the decision to the caller, rather than hard-coding a classification.

## Edge cases

- Empty input and single-symbol input both return `0.0` entropy.
- Strings are measured over Unicode code points, bytes over byte values (0–255). This means the same textual content encoded as `str` and as UTF-8 `bytes` can produce different entropy values for non-ASCII text.
- `normalized_entropy` divides by `log2(k)` where `k` is the number of distinct symbols actually observed, so a two-character string like `"ab"` normalizes to `1.0`.
