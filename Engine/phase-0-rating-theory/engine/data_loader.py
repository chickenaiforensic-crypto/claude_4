"""
data_loader.py — Phase 0 rating engine, data access.

Zero hardcoding: no tournament names, years, or player names are embedded
here. All editions are discovered from MANIFEST.json (the repo's own
single source of truth), and match data is read from the edition JSON files
it points to.
"""

import json
from pathlib import Path


def load_manifest(tennis_data_root):
    manifest_path = Path(tennis_data_root) / "MANIFEST.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_editions(manifest, tournament, year=None):
    """
    Returns manifest edition entries matching the given tournament name
    (case-insensitive exact match against the manifest 'tournament' field),
    optionally narrowed to a single year.
    """
    matches = []
    for ed in manifest["editions"]:
        if ed["tournament"].strip().lower() != tournament.strip().lower():
            continue
        if year is not None and str(ed["year"]) != str(year):
            continue
        matches.append(ed)
    return matches


def load_edition_matches(tennis_data_root, edition_entry):
    """
    Loads the full match list for one manifest edition entry, from its
    file_path field.
    """
    file_path = Path(tennis_data_root) / edition_entry["file_path"]
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("matches", [])


def load_matches_for_tournament(tennis_data_root, tournament, year=None):
    """
    Returns a flat list of (edition_entry, match) tuples for every match in
    every edition matching the tournament filter (and year, if given).
    """
    manifest = load_manifest(tennis_data_root)
    editions = find_editions(manifest, tournament, year)
    result = []
    for ed in editions:
        for m in load_edition_matches(tennis_data_root, ed):
            result.append((ed, m))
    return result, editions
