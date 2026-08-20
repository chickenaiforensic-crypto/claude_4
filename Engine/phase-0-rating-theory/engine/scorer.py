"""
scorer.py — Phase 0 rating engine, scoring logic.

Zero hardcoding: every rule value (points table, reduction pairs) is read from
config/scoring_rules.json at call time. This module contains no player names,
tournament names, or embedded point/game numbers.

Set-completion is judged using the standard tennis rule (winning margin of >=2
games once either side reaches 6+ games), which is generic tennis-scoring
logic, not a per-dataset hardcoded value.
"""

import re
import json
from pathlib import Path

SET_RE = re.compile(r"^(\d+)-(\d+)(?:\((\d+)\))?$")


def load_scoring_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_score(score_str):
    """
    Parse a raw score string, e.g. "2-6 7-6(2) 6-3", into a list of sets:
    [{"gamesA": int, "gamesB": int, "tiebreak": int|None}, ...]
    Tokens that don't match the expected set pattern are returned with
    "unparsed": True and raw text preserved, rather than guessed at.
    """
    sets = []
    if not score_str:
        return sets
    for token in score_str.strip().split():
        m = SET_RE.match(token)
        if not m:
            sets.append({"raw": token, "unparsed": True})
            continue
        gA, gB, tb = m.groups()
        sets.append({
            "gamesA": int(gA),
            "gamesB": int(gB),
            "tiebreak": int(tb) if tb is not None else None,
        })
    return sets


def is_set_complete(gA, gB, reduction_rules):
    """
    A set is complete if it matches a configured reduction pair, or if either
    side has reached 6+ games with a winning margin of at least 2.
    Anything else (e.g. a retirement stub like "3-3" or "4-1") is incomplete.
    """
    pair_sorted = tuple(sorted([gA, gB], reverse=True))
    for rule in reduction_rules:
        if tuple(rule["pair"]) == pair_sorted:
            return True
    hi, lo = pair_sorted
    return hi >= 6 and (hi - lo) >= 2


def apply_reduction(gA, gB, reduction_rules):
    """
    Returns (gA_resolved, gB_resolved) after applying any matching reduction
    rule from config. Order (which side is winner) is preserved.
    """
    winner_is_a = gA > gB
    hi, lo = (gA, gB) if winner_is_a else (gB, gA)
    for rule in reduction_rules:
        if tuple(rule["pair"]) == (hi, lo):
            hi, lo = rule["resolved"]
            break
    return (hi, lo) if winner_is_a else (lo, hi)


def lookup_points(games, points_table):
    """
    Returns points for a given game count using the config points table.
    Returns None (flagged, not guessed) if no tier matches.
    """
    for tier in points_table:
        if tier["min"] <= games <= tier["max"]:
            return tier["points"]
    return None


def score_match(score_str, config):
    """
    Computes per-set and total points for both sides of a single match's raw
    score string. Sets that are incomplete (e.g. retirement stubs) or
    unparsed are excluded from points and reported separately — never
    silently scored under a guessed rule.

    Returns:
    {
      "pointsA": int, "pointsB": int,
      "sets_scored": [ {gamesA, gamesB, resolved (bool), pointsA, pointsB} ],
      "sets_excluded": [ {reason, raw/gamesA/gamesB} ]
    }
    """
    reduction_rules = config["reduction_rules"]
    points_table = config["points_table"]
    parsed = parse_score(score_str)

    pointsA = 0
    pointsB = 0
    sets_scored = []
    sets_excluded = []

    for s in parsed:
        if s.get("unparsed"):
            sets_excluded.append({"reason": "unparsed_token", "raw": s["raw"]})
            continue

        gA, gB = s["gamesA"], s["gamesB"]

        if not is_set_complete(gA, gB, reduction_rules):
            sets_excluded.append({
                "reason": "incomplete_set_not_covered_by_rules",
                "gamesA": gA, "gamesB": gB
            })
            continue

        rA, rB = apply_reduction(gA, gB, reduction_rules)
        pA = lookup_points(rA, points_table)
        pB = lookup_points(rB, points_table)

        if pA is None or pB is None:
            sets_excluded.append({
                "reason": "no_points_tier_match_after_reduction",
                "gamesA": gA, "gamesB": gB, "resolved": [rA, rB]
            })
            continue

        pointsA += pA
        pointsB += pB
        sets_scored.append({
            "gamesA": gA, "gamesB": gB,
            "resolved": [rA, rB] if [rA, rB] != [gA, gB] else None,
            "pointsA": pA, "pointsB": pB
        })

    return {
        "pointsA": pointsA,
        "pointsB": pointsB,
        "sets_scored": sets_scored,
        "sets_excluded": sets_excluded,
    }
