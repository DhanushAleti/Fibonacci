"""Rational harmonic-fraction controls (Repair Contract Part 3).

phi-specialness is tested against a **pre-specified set of market-microstructure
rational fractions**, not a dense uniform grid (the "top 1% of (0,1)" rule is
REJECTED as it tests optimization, not specialness, and ignores tick clustering).

The decisive comparison is phi (0.618) vs **5/8 = 0.625**: if phi cannot out-proximate
5/8, the apparent effect is a tick-discretization artefact, not a property of nature.
"""

from __future__ import annotations

from phi import PHI

#: q_phi = 1/phi, the focal constant under test.
Q_PHI: float = 1.0 / PHI

#: Market-microstructure rational fractions (Part 3): 1/2, 3/5, 5/8, 2/3.
RATIONAL_CONSTANTS: dict[str, float] = {
    "1/2": 1.0 / 2.0,
    "3/5": 3.0 / 5.0,
    "5/8": 5.0 / 8.0,
    "2/3": 2.0 / 3.0,
}

#: 5/8 = 0.625, the discretization-adjacent fraction phi must specifically beat.
FIVE_EIGHTHS: float = 5.0 / 8.0
