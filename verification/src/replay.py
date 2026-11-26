#!/usr/bin/env python3
"""Enumerate exact truth sets, prefix maxcons, and guarded literal queries."""
from itertools import product


def ranks(row, sources):
    return tuple(0 if s <= row else 2 if s.isdisjoint(row) else 1 for s in sources)


def maxcons(rows, sources, ranking):
    """Retain each truth set whose projection is maximal at every prefix."""
    kept = set(rows)
    prefix = set()
    for tier in range(3):
        prefix.update(*(s for s, level in zip(sources, ranking) if level == tier))
        candidates = {row & prefix for row in rows}
        kept = {row for row in kept if not any(row & prefix < other for other in candidates)}
    return kept


def stable(rows, sources):
    result = {}
    for ranking in {ranks(row, sources) for row in rows}:
        choices = maxcons(rows, sources, ranking)
        assert choices
        if all(ranks(row, sources) == ranking for row in choices):
            result[ranking] = choices
    return result


def truth_gadget(matrix, padded):
    xbits = tuple(product((0, 1), repeat=2 if padded else 1))
    ybits = tuple(product((0, 1), repeat=2 if padded else 1))
    singleton_sources = [{("X", i, b)} for i in range(len(xbits[0])) for b in (0, 1)]
    paired_sources = [{("Y", i, b) for b in (0, 1)} for i in range(len(ybits[0]))]
    sources = singleton_sources + paired_sources + [{"A", "A'", "C"}, {"B0", "B1"}]
    rows = set()
    for x, y, z, mode in product(xbits, ybits, (0, 1), ("good", "bad0", "bad1", "repair")):
        padding = x[1] and y[1] if padded else 0
        valid = mode != "repair" or matrix(x[0], y[0], z) or padding
        if not valid:
            rows.add(frozenset())
            continue
        bits = {("X", i, b) for i, b in enumerate(x)} | {("Y", i, b) for i, b in enumerate(y)}
        markers = {"good": {"A'"}, "bad0": {"A", "B0"}, "bad1": {"A", "B1"}, "repair": {"A", "C"}}[mode]
        rows.add(frozenset(bits | markers))
    return rows, sources


def guarded(rows, sources, middle):
    old = frozenset().union(*sources)
    new_rows = {old | {"q"}} | {row | {"not-q"} for row in rows}
    new_sources = sources + [{"q"}, {"not-q"}]
    if middle:
        new_rows = {row | {u} for row in new_rows for u in ("u", "not-u")}
        new_sources += [{"u", "not-u"}]
    return new_rows, new_sources


def check_preserved(rows, sources, middle):
    old = stable(rows, sources)
    new_rows, new_sources = guarded(rows, sources, middle)
    current = stable(new_rows, new_sources)
    tail = (1,) if middle else ()
    fallback = (0,) * len(sources) + (0, 2) + tail
    assert fallback in current
    assert all("q" in row for row in current[fallback])
    assert len(current[fallback]) == (2 if middle else 1)
    assert set(current) == {fallback} | {ranking + (2, 0) + tail for ranking in old}
    marker_labels = {"q", "not-q", "u", "not-u"}
    for ranking, choices in old.items():
        projected = {row - marker_labels for row in current[ranking + (2, 0) + tail]}
        assert projected == choices
    assert all("q" in row for choices in current.values() for row in choices) == (not old)
    if middle:
        assert all(set(ranking) == {0, 1, 2} for ranking in current)
    return old, current


def check_all_matrices():
    for f in product((False, True), repeat=8):
        matrix = lambda x, y, z: f[4*x + 2*y + z]
        truth = any(all(any(matrix(x, y, z) for z in (0, 1)) for y in (0, 1)) for x in (0, 1))
        for padded in (False, True):
            rows, sources = truth_gadget(matrix, padded)
            for middle in (False, True):
                existence, _ = check_preserved(rows, sources, middle)
                assert bool(existence) == truth
    print("256 Boolean matrices, both padding choices and both guard variants checked")


def check_illustration():
    for label, matrix, expected, expected_repairs in (
        ("y or z", lambda x, y, z: y or z, (4, 5), (True, True, True, True)),
        ("y", lambda x, y, z: y, (0, 1), (False, True, True, True)),
    ):
        # Fix x=0 and the padding bit s=1, as in the picture, and vary y,t.
        repairs = tuple(any(matrix(0, y, z) or t for z in (0, 1)) for y, t in product((0, 1), repeat=2))
        assert repairs == expected_repairs
        rows, sources = truth_gadget(matrix, padded=True)
        old, current = check_preserved(rows, sources, middle=True)
        assert (len(old), len(current)) == expected
        print(f"matrix {label}: repairs {tuple(int(b) for b in repairs)}, "
              f"{len(old)} false-marker stable orders, 1 true-marker stable order, "
              f"skeptical q = {not old}")


if __name__ == "__main__":
    check_all_matrices()
    check_illustration()
