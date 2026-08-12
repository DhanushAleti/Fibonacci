"""Determinism and reproducibility (contract §5A, §11 items 2 and 10)."""

from __future__ import annotations

import hashlib
import subprocess
import sys

import pytest

from phi.config import repo_root
from phi.features.candidate import f_A
from phi.features.constants import G_PHI
from phi.features.engine import FeatureRow, compute_phi_retracement_features
from phi.features.pipeline import compute_window
from tests.features.conftest import make_bar, make_synthetic_bars


def _canonical_digest(rows: list[FeatureRow]) -> str:
    """A stable SHA-256 over the full feature output, at float ``repr`` precision.

    Ordering, alignment keys, and every scalar (or ``None``) are folded in, so
    any change in value, order, or NULL mask changes the digest.
    """
    lines = [
        "|".join(
            [
                r.symbol,
                r.event_time.isoformat(),
                r.availability_time.isoformat(),
                *(
                    "None" if v is None else repr(v)
                    for v in (r.p, r.f_a, r.f_b, r.f_c1, r.f_c2, r.f_d, r.f_e, r.f_f)
                ),
            ]
        )
        for r in rows
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _digest_of_default_features() -> str:
    """Digest of the canonical synthetic-fixture feature output.

    Importable at module top level (no test-collection side effects) so a child
    interpreter can call exactly this code path — see the cross-process test.
    """
    return _canonical_digest(compute_phi_retracement_features(make_synthetic_bars()))


@pytest.mark.reproducibility
class TestSingleImplementationDeterminism:
    def test_repeated_calls_on_same_input_are_bitwise_identical(self) -> None:
        bars = make_synthetic_bars()
        first = compute_phi_retracement_features(bars)
        second = compute_phi_retracement_features(bars)
        assert first == second

    def test_ordering_support_and_null_mask_are_stable_across_runs(self) -> None:
        bars = make_synthetic_bars()
        first = compute_phi_retracement_features(bars)
        second = compute_phi_retracement_features(bars)

        first_keys = [(r.symbol, r.event_time, r.availability_time) for r in first]
        second_keys = [(r.symbol, r.event_time, r.availability_time) for r in second]
        assert first_keys == second_keys

        first_null_mask = [
            (
                r.f_a is None,
                r.f_b is None,
                r.f_c1 is None,
                r.f_c2 is None,
                r.f_d is None,
                r.f_e is None,
                r.f_f is None,
            )
            for r in first
        ]
        second_null_mask = [
            (
                r.f_a is None,
                r.f_b is None,
                r.f_c1 is None,
                r.f_c2 is None,
                r.f_d is None,
                r.f_e is None,
                r.f_f is None,
            )
            for r in second
        ]
        assert first_null_mask == second_null_mask

    def test_category_b_seeded_rotation_is_itself_deterministic(self) -> None:
        # Explicitly named in §5A as part of the determinism requirement.
        bars = make_synthetic_bars()
        first = [row.f_b for row in compute_phi_retracement_features(bars)]
        second = [row.f_b for row in compute_phi_retracement_features(bars)]
        assert first == second

    def test_different_seed_changes_only_b_not_the_other_six(self) -> None:
        bars = make_synthetic_bars()
        rows_seed_1 = compute_phi_retracement_features(bars, seed=1)
        rows_seed_2 = compute_phi_retracement_features(bars, seed=2)

        for r1, r2 in zip(rows_seed_1, rows_seed_2, strict=True):
            assert r1.p == r2.p
            assert r1.f_a == r2.f_a
            assert r1.f_c1 == r2.f_c1
            assert r1.f_c2 == r2.f_c2
            assert r1.f_d == r2.f_d
            assert r1.f_e == r2.f_e
            assert r1.f_f == r2.f_f
        # The seed is the only source of randomness in the whole contract
        # (§9); different seeds should (for this fixture) draw a different
        # rotation offset and hence a different f_b series.
        assert [r.f_b for r in rows_seed_1] != [r.f_b for r in rows_seed_2]


@pytest.mark.reproducibility
class TestCrossImplementationToleranceIsMeaningful:
    """§5A's tolerance (atol=1e-12, rtol=1e-9) covers float rounding order,
    not definitional drift — this asserts our own output is exact enough
    that the tolerance has real headroom, not that it is being relied upon.
    """

    def test_worked_example_matches_hand_computation_far_inside_tolerance(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
        ]
        target_close = 99.0 + G_PHI * 2.0
        bars.append(make_bar(3, open_=100, high=101, low=99, close=target_close))
        window = compute_window(bars, 3, window=3)
        value = f_A(window)
        assert value is not None
        assert abs(value - 0.0) < 1e-12


@pytest.mark.reproducibility
class TestCrossProcessDeterminism:
    """§5A item 2 requires determinism "across repeated runs and process restarts."

    The same-process repetition tests above cannot prove that — pure functions
    are trivially repeatable within one interpreter. This runs the identical
    computation in a *fresh* interpreter (with its own randomized hash seed) and
    asserts a bit-for-bit identical output digest, which genuinely exercises
    process-restart determinism and would catch any latent hash-seed / set- or
    dict-ordering dependence in the pipeline or the seeded synthetic fixture.
    """

    def test_output_digest_is_identical_in_a_fresh_interpreter(self) -> None:
        in_process = _digest_of_default_features()

        # A separate process: sys.executable is the venv interpreter; cwd at the
        # repo root makes the `tests` package importable via `-c`. PYTHONHASHSEED
        # is deliberately NOT pinned, so hash randomization differs from this
        # process — any reliance on it would surface as a digest mismatch.
        child = subprocess.run(
            [
                sys.executable,
                "-c",
                "from tests.features.test_determinism import _digest_of_default_features as d;"
                "print(d())",
            ],
            capture_output=True,
            text=True,
            cwd=repo_root(),
            check=True,
        )
        assert child.stdout.strip() == in_process, (
            "feature output digest differs across process restart\n"
            f"in-process: {in_process}\nchild stdout: {child.stdout!r}\n"
            f"child stderr: {child.stderr!r}"
        )
