"""
add_lyrics_fields.py
====================

One-time standalone script (similar to import_vanilla_songs.py).

Adds the "lyrics": [] and "lyrics_en": [] fields to every song in
vanilla_songs.json that does not already contain them.

This script DOES NOT modify any other data. Everything you have already
edited manually (such as bpm, song_name_reading, performers, etc.)
remains exactly as it is.

If a song already contains "lyrics" and/or "lyrics_en", those fields are
left untouched and will not be overwritten.

Usage:
    1. Set INPUT_FILE to your actual JSON file (by default it assumes the
       file is located in the same directory as this script).
    2. Run:
           python add_lyrics_fields.py
    3. Review the generated OUTPUT_FILE before replacing your original
       file. For safety, this script never overwrites the original file.
"""

from __future__ import annotations

import json
import os
import shutil

INPUT_FILE = "vanilla_songs_output.json"
OUTPUT_FILE = "vanilla_songs_output_with_lyrics.json"

# In addition to creating a separate output file, also create a backup
# of the original file.
MAKE_BACKUP = True


def main():
    """Add empty lyrics fields to songs that do not already have them."""

    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} was not found. Update INPUT_FILE at the top of this script and try again.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    songs = data.get("songs", [])
    added = 0
    already_had = 0

    for song in songs:
        changed = False

        if "lyrics" not in song:
            song["lyrics"] = []
            changed = True

        if "lyrics_en" not in song:
            song["lyrics_en"] = []
            changed = True

        if changed:
            added += 1
        else:
            already_had += 1

    if MAKE_BACKUP:
        backup_path = INPUT_FILE + ".backup"
        shutil.copy2(INPUT_FILE, backup_path)
        print(f"Original file backup saved to: {backup_path}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{added} song(s) received empty lyrics/lyrics_en fields, ready to be filled.")
    print(f"{already_had} song(s) already contained those fields and were left unchanged.")
    print(f"Output written to: {OUTPUT_FILE}")
    print("Review the generated file, then replace your original vanilla_songs.json whenever you're ready.")


if __name__ == "__main__":
    main()
