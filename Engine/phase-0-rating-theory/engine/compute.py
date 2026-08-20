"""
compute.py — Phase 0 rating engine, main entry point.

Given a player name and a tournament filter, computes total rating points
earned by that player across every match found in the dataset for that
tournament (optionally narrowed to one year).

Zero hardcoding: player name and tournament are runtime inputs. Scoring
rules come from config/scoring_rules.json. Data comes from MANIFEST.json and
the edition files it references. Nothing here is specific to any single
player, tournament, or year.

Usage (CLI):
    python3 compute.py --player "Andy Murray" --tournament "Rotterdam" \
        --data-root /path/to/data/tennis

    Optional: --year 2021 to narrow to a single edition.
"""

import argparse
import json
from pathlib import Path

from data_loader import load_matches_for_tournament
from scorer import load_scoring_config, score_match

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "scoring_rules.json"


def compute_player_tournament_points(player, tournament, tennis_data_root,
                                      year=None, config_path=DEFAULT_CONFIG_PATH):
    config = load_scoring_config(config_path)
    matches, editions = load_matches_for_tournament(tennis_data_root, tournament, year)

    total_points = 0
    matches_included = []
    matches_skipped = []

    for edition, m in matches:
        pA, pB = m.get("playerA"), m.get("playerB")
        if player == pA:
            side = "A"
        elif player == pB:
            side = "B"
        else:
            continue  # player not in this match

        result = score_match(m.get("score", ""), config)
        earned = result["pointsA"] if side == "A" else result["pointsB"]
        total_points += earned

        matches_included.append({
            "edition_year": edition["year"],
            "round": m.get("round"),
            "opponent": pB if side == "A" else pA,
            "score": m.get("score"),
            "player_side": side,
            "points_earned": earned,
            "sets_excluded": result["sets_excluded"],
        })

    return {
        "player": player,
        "tournament": tournament,
        "year_filter": year,
        "editions_found": [{"year": e["year"], "file_path": e["file_path"]} for e in editions],
        "total_points": total_points,
        "matches_included": matches_included,
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 0 rating engine — player/tournament points")
    parser.add_argument("--player", required=True, help="Full player name, exact match")
    parser.add_argument("--tournament", required=True, help="Tournament name, per MANIFEST.json")
    parser.add_argument("--year", default=None, help="Optional: narrow to one edition year")
    parser.add_argument("--data-root", required=True, help="Path to data/tennis directory")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to scoring_rules.json")
    args = parser.parse_args()

    result = compute_player_tournament_points(
        args.player, args.tournament, args.data_root,
        year=args.year, config_path=args.config
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
