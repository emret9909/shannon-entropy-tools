"""shannon-entropy-tools: Shannon entropy calculation for detecting compressed or random data."""

from .core import shannon_entropy, normalized_entropy, is_likely_compressed

__all__ = ["shannon_entropy", "normalized_entropy", "is_likely_compressed"]
