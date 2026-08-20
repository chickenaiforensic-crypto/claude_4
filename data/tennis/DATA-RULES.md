# DATA RULES — Tennis Dataset (arena/01a015bb-the-creation-2)

Binding standard for anyone sourcing, editing, or fixing data under `data/tennis/`. Applies to
the Director, any Auditor, any Engineer, and any AI worker touching this branch. If a rule here
conflicts with a workorder, this file wins — flag the conflict, don't silently resolve it either
way.

## 1. Player names must be full and clear

- No initials, no abbreviations, no shortened first names. "J.J. Wolf" is not acceptable;
  "Jeffrey Wolf" is.
- Full legal or commonly-attributed full name only, sourced from an official or checkable
  reference (ATP/WTA Tour bio, Wikipedia, ITF profile) — never assumed from the abbreviation
  itself.
- Legitimate short surnames (e.g. "Lu", "Wu") and naming particles ("de", "van de", "van der")
  are not abbreviations and must not be "fixed."
- Before any name correction, check `player_canonical_names.json` (if present on this branch)
  or the equivalent canonical table for an existing adjudicated spelling before introducing a
  new one — do not fork an identity that's already been resolved elsewhere.

## 2. No incomplete data fetch

- A tournament edition is not "done" until every match from R32 (or R64, for draws that size)
  through the Final is present, or the absence of a round is confirmed structural (the edition
  didn't reach that round) rather than a missing record.
- Draw size must be confirmed from an edition-specific source before determining what "complete"
  means for that edition — do not assume a category default (e.g. "32 is standard for ATP500")
  without checking the specific year, per the precedent already found (Dubai 2021 = 48-draw
  against every other year's 32).
- Every edition migrated onto this branch must pass the round-transition gap check
  (`build.py`-adjacent method: R32-onward, byefree, every round-N+1 participant must have a
  traceable win in round N) before being marked `closed_verified_gapless` in `MANIFEST.json`.
  A status of `closed_verified_gapless` without having run this check is a false claim.

## 3. Nothing self-authored

- No result, date, score, round, or player name may be inferred, estimated, or filled from
  general knowledge. Every fact must trace to a named, checkable source recorded in that row's
  `provenance` field.
- If a source cannot be found for a required fact, the record stays absent and the gap stays
  open and documented — it is never filled with a plausible guess to make an edition look
  complete.
- Provenance must be per-row and specific to what was actually checked for that row. Copying a
  provenance block from a different row or a different edition is a fabrication, not a citation.

## 4. Rank fields excluded

- `rankA` / `rankB` are not part of this dataset's schema. Do not add them. If a source file
  being migrated from elsewhere carries them, drop them on import.

## 5. Manifest and checksum integrity

- Any edit to an edition file requires recomputing that file's `match_count` and
  `checksum_sha256` in `MANIFEST.json` in the same change. A file and its manifest entry must
  never be allowed to drift.
- `build.py` must run clean (no checksum or count mismatch) after any change, before the change
  is considered finished. A red `build.py` run means the work isn't done yet, not that the build
  script is wrong.
- `master_store_tennis_SSoT.json` is a compiled output. Never hand-edit it — edit the source file
  in `editions/` and rerun `build.py`.

## 6. Per-edition .txt summaries must stay in sync

- Every `editions/{Tournament}/{Year}.json` has a matching
  `editions/{Tournament}/summaries/{Year}.txt` — a human-readable summary derived entirely from
  that file's own match data plus its `MANIFEST.json` entry, kept in its own `summaries/`
  subfolder so rendered output stays visually separate from source data. It is a rendering, not
  a new source: nothing in the `.txt` may assert a fact absent from the `.json` and the manifest
  row.
- Regenerate via `generate_summaries.py` whenever the edition file or its manifest entry
  changes. Never hand-edit a `.txt` file — the same discipline as `master_store_tennis_SSoT.json`
  in Rule 5. A stale `.txt` (not matching current match_count/checksum/status) is a defect.
- Any time an edition's `.json` or its `MANIFEST.json` row is edited, run both, in order, as
  part of that same change:
  ```
  python3 build.py
  python3 generate_summaries.py
  ```
  `build.py` must run first — `generate_summaries.py` checks each edition's live match count
  against its manifest entry and fails loudly if they're out of sync, which is the signal the
  manifest wasn't updated yet.
- Do not add new derived fields to `generate_summaries.py` (e.g. total sets played, longest
  match) without the Director's sign-off — an unreviewed addition just creates another field
  that can silently drift out of sync with its source.

## 7. Verification before acceptance

- Claims of "closed," "gapless," "verified," or "complete" from any contributor (human or AI)
  are re-checked independently before being accepted — rerun the gap-detection script, rerun
  `build.py`, re-open the cited source. A report of work done is not itself evidence the work
  was done correctly.
