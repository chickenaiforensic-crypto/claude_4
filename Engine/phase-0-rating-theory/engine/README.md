# Phase 0 Engine

Pluggable compute engine. Input: player name + tournament filter. Output: total rating points earned by that player in that tournament, computed live from `data/tennis/`.

## Zero hardcoding

- No player name, tournament name, or year is embedded in code. Both are runtime arguments.
- Scoring rules (points table, reduction pairs) live in `config/scoring_rules.json`, not in code. Change the formula by editing that file — no code change required.
- Tournament/edition discovery comes from `data/tennis/MANIFEST.json` (the dataset's own source of truth), not from a hardcoded file list.

## Files

| File | Role |
|---|---|
| `config/scoring_rules.json` | Points table + reduction rules (editable, drives all scoring) |
| `data_loader.py` | Reads MANIFEST.json, loads matching edition files |
| `scorer.py` | Parses score strings, applies reduction, looks up points |
| `compute.py` | Entry point: player + tournament → total points |

## Usage

```
python3 compute.py --player "Andy Murray" --tournament "Rotterdam" \
    --data-root /path/to/data/tennis
```

Optional `--year 2021` narrows to a single edition. Without it, points are summed across every edition of that tournament found in MANIFEST.json.

## Verified against real data

Andy Murray, Rotterdam 2021 (from `data/tennis/editions/Rotterdam/2021.json`):
- R32 vs Robin Haase, score `2-6 7-6(2) 6-3` → 22 pts (hand-verified)
- R16 vs Andrey Rublev, score `7-5 6-2`, Murray as playerB → 6 pts (hand-verified)
- Engine output matches both by independent calculation.

## Design decision flagged — not covered by formula.md

Retired matches contain incomplete final sets (e.g. `"3-3"`, `"4-1"`, `"2-0"` — see `data/tennis/editions/Dubai/2021.json`, `data/tennis/editions/US_Open/2021.json`). The Phase 0 rules define points only for completed sets (0-2, 3-4, 5, 6 game tiers reached through play or the defined reduction rules). No rule exists for an incomplete/retirement-stub set.

**Current behaviour:** incomplete sets are excluded from points entirely and reported per-match under `sets_excluded`, rather than scored under a guessed rule. This is a flagged gap, not a resolved rule — confirm with Director_2 if incomplete sets should score differently.
