"""
Generates data/tennis/editions/{Tournament}/{Year}.txt for every edition in MANIFEST.json.

This is a rendering step, not a data-sourcing step. Every value written to a .txt file is
derived from that edition's own JSON file and its MANIFEST.json row — nothing is fetched,
inferred, or asserted beyond what those two sources already contain.

Run this after build.py, any time an edition file or its manifest entry changes.

Usage:
    python3 generate_summaries.py

Reads:  MANIFEST.json, editions/**/*.json
Writes: editions/{Tournament}/summaries/{Year}.txt
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(BASE_DIR, "MANIFEST.json")

TOURNAMENT_FULL_NAMES = {
    "Rotterdam": "ABN AMRO Open",
    "Dubai": "Dubai Tennis Championships",
    "Halle": "Halle Open",
    "Queen's Club": "Queen's Club Championships",
}

ROUND_ORDER = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]


def round_coverage_string(by_round):
    parts = []
    for r in ROUND_ORDER:
        if r in by_round:
            parts.append(f"{r}({len(by_round[r])})")
    return " ".join(parts)


def main():
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    errors = []
    written = 0

    for ed in manifest["editions"]:
        file_path = os.path.join(BASE_DIR, ed["file_path"])
        if not os.path.exists(file_path):
            errors.append(f"MISSING: {ed['file_path']}")
            continue

        with open(file_path) as f:
            edata = json.load(f)
        matches = edata["matches"]

        if len(matches) != ed["match_count"]:
            errors.append(
                f"COUNT MISMATCH before summary generation: {ed['file_path']} "
                f"(manifest={ed['match_count']}, actual={len(matches)}) — run build.py first"
            )
            continue

        by_round = {}
        for m in matches:
            by_round.setdefault(m["round"], []).append(m)

        final_matches = by_round.get("F", [])
        if len(final_matches) == 1:
            f = final_matches[0]
            champion = f["playerA"] if f["winner"] == "A" else f["playerB"]
            runner_up = f["playerB"] if f["winner"] == "A" else f["playerA"]
            champ_line = f"Champion: {champion}"
            runner_line = f"Runner-up: {runner_up}"
        else:
            champ_line = "Champion: (no single Final record on file)"
            runner_line = "Runner-up: (no single Final record on file)"

        full_name = TOURNAMENT_FULL_NAMES.get(ed["tournament"], ed["tournament"])
        checksum_short = ed["checksum_sha256"][:12]

        lines = [
            f"{ed['tournament']} — {full_name} ({ed['tier']})",
            f"Edition: {ed['year']}",
            f"Draw size: {ed['draw_size']}",
            f"Status: {ed['status']}",
            f"Match count: {ed['match_count']}",
            f"Round coverage: {round_coverage_string(by_round)}",
            champ_line,
            runner_line,
            f"Source: {ed['source']}",
            f"Checksum: {checksum_short}... (full value in MANIFEST.json)",
        ]

        tournament_dir = os.path.dirname(file_path)
        summaries_dir = os.path.join(tournament_dir, "summaries")
        os.makedirs(summaries_dir, exist_ok=True)
        out_path = os.path.join(summaries_dir, f"{ed['year']}.txt")
        with open(out_path, "w") as f:
            f.write("\n".join(lines) + "\n")
        written += 1

    if errors:
        print("SUMMARY GENERATION HAD ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Generated {written} .txt summaries.")


if __name__ == "__main__":
    main()
