"""PHI — a research-grade platform for the falsifiable evaluation of Golden Ratio /
Fibonacci-derived features in financial markets.

This package is the modular monolith described in
``docs/03-architecture/SYSTEM_ARCHITECTURE.md``. Nothing in this package asserts
that Golden Ratio features are predictive; that is the open research question the
platform exists to answer (PRD §5-§8).
"""

from __future__ import annotations

__all__ = ["PHI", "__version__"]

__version__ = "0.2.0"

# The mathematical constant under investigation. Its presence here is a definition,
# not a claim of predictive value (PRD-GRF-012).
PHI: float = (1.0 + 5.0**0.5) / 2.0  # ≈ 1.6180339887498949
