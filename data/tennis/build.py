"""
Compiles data/tennis/editions/**/*.json into data/tennis/master_store_tennis_SSoT.json.

This is the single build step between the editable per-edition source files
and the app-facing compiled store. Run this after adding, editing, or
removing any editions/**/*.json file, and after any MANIFEST.json change.

Usage:
    python3 build.py

Reads:  MANIFEST.json, editions/**/*.json
Writes: master_store_tennis_SSoT.json
"""
import json
import hashlib
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(BASE_DIR, "MANIFEST.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "master_store_tennis_SSoT.json")


def main():
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    all_matches = []
    errors = []

    for edition in manifest["editions"]:
        file_path = os.path.join(BASE_DIR, edition["file_path"])
        if not os.path.exists(file_path):
            errors.append(f"MISSING FILE: {edition['file_path']} listed in manifest but not found")
            continue

        with open(file_path) as f:
            raw = f.read()

        actual_checksum = hashlib.sha256(raw.encode()).hexdigest()
        if actual_checksum != edition["checksum_sha256"]:
            errors.append(
                f"CHECKSUM MISMATCH: {edition['file_path']} "
                f"(manifest={edition['checksum_sha256'][:12]}..., actual={actual_checksum[:12]}...)"
            )
            continue

        edition_data = json.loads(raw)
        matches = edition_data.get("matches", [])

        if len(matches) != edition["match_count"]:
            errors.append(
                f"COUNT MISMATCH: {edition['file_path']} "
                f"(manifest={edition['match_count']}, actual={len(matches)})"
            )
            continue

        all_matches.extend(matches)

    if errors:
        print("BUILD FAILED — integrity errors found:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    output = {
        "schema_version": "2.0",
        "description": "Compiled tennis master store — built from data/tennis/editions/ via build.py. Do not edit directly; edit source files in editions/ and rerun build.py.",
        "count": len(all_matches),
        "matches": all_matches,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Build OK: {len(manifest['editions'])} editions, {len(all_matches)} matches -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
