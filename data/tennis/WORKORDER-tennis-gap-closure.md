# WORKORDER — Gap Closure for the 20 Migrated ATP500 Editions

**Repo:** chickenaiforensic-crypto/the_creation_2
**Branch:** arena/01a015bb-the-creation-2
**Source of gaps:** `data/tennis/gap_report.json`
**Manifest:** `data/tennis/MANIFEST.json`

## Background

The 20 editions migrated to this branch (Rotterdam, Dubai, Halle, Queen's Club, ATP500, 2021–2025)
were verified for source/draw-size/identity, but had not been checked for round-transition
completeness. That check has now been run using the same validated method Phase 1B applied to
M1000 (`data/tennis/phase1-audit/reproduce_m1000_gaps.py`): for each round transition from
R32 onward (R32→R16→QF→SF→F, byefree at this draw depth), every player appearing in round N+1
must have a traceable win recorded in round N within the same edition file.

**Result: 8 of 20 editions are gapless. 12 editions carry 18 total gap instances.**

A "gap" here means: a named player appears in a later round with no match record showing they
won the round before it. This does not mean the player didn't actually win that match in real
life — it means the record of that specific match is absent from this edition's file.

## Task

For each of the 18 gaps listed in `data/tennis/gap_report.json`, determine what actually happened
and close the gap with an evidenced, sourced correction. For each gap:

1. **Identify the missing match.** Using the tournament, year, and the two rounds bracketing the
   gap, find the actual result of the named player's match in the missing round. Use a
   named, checkable source (Wikipedia tournament-edition page, ATP Tour official draw archive,
   or equivalent) — not general knowledge.
2. **Confirm it's a genuine missing record, not a data-entry quirk.** Check whether the match
   exists elsewhere in the edition file under a different round label or misspelled player name
   before concluding it's absent. If it's a mislabeling rather than a true gap, document that
   finding instead of adding a new row.
3. **Add the missing match record** to the correct `editions/{Tournament}/{Year}.json` file,
   using the exact same schema as the existing rows in that file (date, tournament, tier, round,
   surface, indoor, tour, playerA, playerB, setsA, setsB, gamesA, gamesB, score, bestOf,
   duration_min, retired, walkover, source, status, defaulted, winner, provenance, edition_year).
   Populate `provenance` with the real source used for this specific addition — never copy
   provenance from an unrelated row.
4. **Update `gap_report.json`**: set that gap's `status` to `closed`, and add a `resolution`
   field naming the source and what was found.
5. **Update `MANIFEST.json`**: recompute `match_count` and `checksum_sha256` for the edited
   edition file, decrement `gap_count`, and if it reaches 0, set `status` to
   `closed_verified_gapless`.
6. **Run `data/tennis/build.py`** after all edits — it will fail loudly (checksum/count mismatch)
   if any manifest entry doesn't match its file. Do not hand-edit `master_store_tennis_SSoT.json`;
   it is a compiled output.

## The 18 gaps to close

See `data/tennis/gap_report.json` for the authoritative list (gap_id G001–G018). Do not
retype the list here — this workorder references it so the two can't drift out of sync.

## Standard

Every closure must carry a named, checkable source per Rule 13-equivalent discipline: no
inferred or assumed match results. If a gap cannot be resolved with an available source, leave
it open and say so — do not fill it with a plausible guess.

## Acceptance

A gap is closed only when: the new match record is in the edition file, `gap_report.json` shows
`status: closed` with a named source, `MANIFEST.json` counts/checksums are updated, and
`build.py` runs clean.
