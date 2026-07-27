"""
import_vanilla_songs.py
=======================

One-time standalone script that generates the "songs" section of
vanilla_songs.json using the DivaModArchive API.

This script is intentionally standalone—it does not live inside
diva_editor/, is not imported by any module under core/ or ui/, and is
not bundled with application builds.

Run it once (or whenever you want to regenerate or expand the catalog),
then manually copy the generated output into:

    diva_editor/data/vanilla_songs.json

What IS automated:

- song_name
- song_name_en
- songinfo (Japanese/English credits, all seven supported fields.
  'ex_info' is intentionally ignored because it has no equivalent
  in mod_pv_db.txt.)
- difficulties
  Difficulty order is assumed to be:
      [easy, normal, hard, extreme, extreme_extra]
  based on the "levels" array.

  This mapping was verified against the valid ranges shown in your guide
  using the ten sample songs you provided, but it is still recommended to
  manually verify a few songs.

  A null value means that the corresponding difficulty does not exist for
  that song, so it is omitted.

What the API DOES NOT provide:

- date
    Uses DEFAULT_DATE.
- sabi_start
    Uses DEFAULT_SABI_START.
- sabi_play
    Uses DEFAULT_SABI_PLAY.
- song_name_reading
    Uses the placeholder "FILL_ME".
- bpm
    Uses the placeholder "FILL_ME".
- performers
    Uses ["FILL_ME"] because the API does not indicate who performs
    the song.

Usage:

    1. pip install requests
    2. Fill VANILLA_PV_IDS below with the PV IDs you want to retrieve.
    3. Run:

           python import_vanilla_songs.py

    4. Review vanilla_songs_output.json, replace every "FILL_ME"
       placeholder, then copy the result into:

           diva_editor/data/vanilla_songs.json
"""

from __future__ import annotations

import json
import os
import time

import requests

# ============================================================
# EDIT THIS SECTION:
# Paste the vanilla PV IDs you want to retrieve from the API.
# For example, you can paste the same IDs used in your
# excluded_ids list.
# ============================================================
VANILLA_PV_IDS: list[int] = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    27,
    28,
    29,
    30,
    31,
    32,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    79,
    81,
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    101,
    102,
    103,
    104,
    201,
    202,
    203,
    204,
    205,
    206,
    207,
    208,
    209,
    210,
    211,
    212,
    213,
    214,
    215,
    216,
    218,
    219,
    220,
    221,
    222,
    223,
    224,
    225,
    226,
    227,
    228,
    231,
    232,
    233,
    234,
    235,
    236,
    238,
    239,
    240,
    241,
    242,
    243,
    244,
    246,
    247,
    248,
    249,
    250,
    251,
    253,
    254,
    255,
    257,
    259,
    260,
    261,
    262,
    263,
    265,
    266,
    267,
    268,
    269,
    270,
    271,
    272,
    273,
    274,
    275,
    276,
    277,
    278,
    279,
    280,
    281,
    401,
    402,
    403,
    404,
    405,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    419,
    420,
    421,
    422,
    423,
    424,
    425,
    426,
    427,
    428,
    429,
    430,
    431,
    432,
    433,
    434,
    435,
    436,
    437,
    438,
    439,
    440,
    441,
    442,
    443,
    600,
    601,
    602,
    603,
    604,
    605,
    607,
    608,
    609,
    610,
    611,
    612,
    613,
    614,
    615,
    616,
    617,
    618,
    619,
    620,
    621,
    622,
    623,
    624,
    625,
    626,
    627,
    628,
    629,
    630,
    631,
    637,
    638,
    639,
    640,
    641,
    642,
    710,
    722,
    723,
    724,
    725,
    726,
    727,
    728,
    729,
    730,
    731,
    732,
    733,
    734,
    736,
    737,
    738,
    739,
    740,
    832,
]

# ============================================================
# Configuration
# ============================================================

API_BASE_URL = "https://divamodarchive.com/api/v1/ids/pvs"

# Number of PV IDs requested per API call.
# (See the note above regarding unverified API limits.)
BATCH_SIZE = 50

# Delay between requests to avoid sending too many requests at once.
REQUEST_DELAY_SECONDS = 2

REQUEST_TIMEOUT_SECONDS = 15

OUTPUT_FILE = "vanilla_songs_output.json"

# If this file already exists, its contents will be merged instead of
# generating a completely new catalog.
EXISTING_FILE_TO_MERGE = "vanilla_songs_output.json"

# Default values confirmed with the project.
DEFAULT_DATE = "20220526"       # Mega Mix+ release date
DEFAULT_SABI_START = "0.0"
DEFAULT_SABI_PLAY = "20.0"

PLACEHOLDER_BPM = "FILL_ME"
PLACEHOLDER_READING = "FILL_ME"
PLACEHOLDER_PERFORMERS = ["FILL_ME"]

DIFFICULTY_ORDER = [
    "easy",
    "normal",
    "hard",
    "extreme",
    "extreme_extra",
]

DEFAULT_LEVEL_SORT_INDEX = {
    "easy": 50,
    "normal": 50,
    "hard": 80,
    "extreme": 20,
    "extreme_extra": 50,
}


# ============================================================
# API calls
# ============================================================

def _chunks(lst: list, size: int):
    """Yield successive chunks from a list."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def fetch_pvs_by_ids(pv_ids: list[int]) -> list[dict]:
    """Retrieve data for multiple PV IDs from the API in batches of BATCH_SIZE."""
    all_pvs = []
    batches = list(_chunks(pv_ids, BATCH_SIZE))

    for n, batch in enumerate(batches, 1):
        filter_str = "pv_id IN [" + ", ".join(str(i) for i in batch) + "]"
        params = {"filter": filter_str, "limit": len(batch), "offset": 0}

        print(f"[{n}/{len(batches)}] Requesting {len(batch)} IDs ({batch[0]}..{batch[-1]})...")
        try:
            resp = requests.get(
                API_BASE_URL, params=params,
                headers={"accept": "application/json"},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()
            pvs = data.get("pvs", [])
            print(f"    -> {len(pvs)} result(s)")
            all_pvs.extend(pvs)
        except Exception as e:
            print(f"    !! ERROR while processing this batch, continuing with the next one: {e}")

        if n < len(batches):
            time.sleep(REQUEST_DELAY_SECONDS)

    return all_pvs


# ============================================================
# Conversion to vanilla_songs.json format
# ============================================================
def _convert_songinfo(song_info: dict | None, song_info_en: dict | None) -> dict:
    result = {}
    song_info = song_info or {}
    song_info_en = song_info_en or {}
    for field in ("arranger", "guitar_player", "illustrator", "lyrics", "manipulator", "music", "pv_editor"):
        jp_val = song_info.get(field)
        if jp_val:
            result[field] = jp_val
        en_val = song_info_en.get(field)
        if en_val:
            result[f"{field}_en"] = en_val
    return result


def _convert_difficulties(levels: list | None) -> dict:
    """A null value in 'levels' means the song does not have that difficulty, so it is omitted."""
    result = {}
    if not levels:
        return result
    for i, level in enumerate(levels):
        if level is None or i >= len(DIFFICULTY_ORDER):
            continue
        diff_name = DIFFICULTY_ORDER[i]
        result[diff_name] = {"level": level, "level_sort_index": DEFAULT_LEVEL_SORT_INDEX.get(diff_name, 50)}
    return result


def convert_pv(pv: dict) -> dict:
    return {
        "pv_id": str(pv.get("id", "")),
        "song_name": pv.get("name", "") or "",
        "song_name_en": pv.get("name_en", "") or "",
        "song_name_reading": PLACEHOLDER_READING,
        "song_name_reading_en": "",
        "bpm": PLACEHOLDER_BPM,
        "date": DEFAULT_DATE,
        "sabi_start": DEFAULT_SABI_START,
        "sabi_play": DEFAULT_SABI_PLAY,
        "difficulties": _convert_difficulties(pv.get("levels")),
        "performers": list(PLACEHOLDER_PERFORMERS),
        "songinfo": _convert_songinfo(pv.get("song_info"), pv.get("song_info_en")),
        "audio_variants": [],
        "sfx": {},
        "is_valid": True,
        "invalid_fields": [],
    }


# ============================================================
def main():
    if not VANILLA_PV_IDS:
        print("VANILLA_PV_IDS is empty. Paste your PV IDs above before running this script.")
        return

    print(f"Querying {len(VANILLA_PV_IDS)} PV IDs from the DivaModArchive API...\n")
    raw_pvs = fetch_pvs_by_ids(VANILLA_PV_IDS)
    print(f"\nRetrieved {len(raw_pvs)} out of {len(VANILLA_PV_IDS)} requested PV IDs.")

    found_ids = {str(pv.get("id")) for pv in raw_pvs}
    missing = [i for i in VANILLA_PV_IDS if str(i) not in found_ids]
    if missing:
        print(f"WARNING: {len(missing)} PV IDs were not found in the API: {missing}")

    songs = [convert_pv(pv) for pv in raw_pvs]

    # If a previous output file already exists (for example, from an earlier
    # run with fewer PV IDs), merge the new data instead of starting from scratch.
    existing_by_id = {}
    if os.path.exists(EXISTING_FILE_TO_MERGE):
        try:
            with open(EXISTING_FILE_TO_MERGE, "r", encoding="utf-8") as f:
                prev = json.load(f)
            existing_by_id = {s["pv_id"]: s for s in prev.get("songs", [])}
            print(f"Found an existing {EXISTING_FILE_TO_MERGE} containing {len(existing_by_id)} songs — merging data.")
        except Exception as e:
            print(f"Could not read the existing {EXISTING_FILE_TO_MERGE}; ignoring it: {e}")

    for song in songs:
        existing_by_id[song["pv_id"]] = song  # Overwrite existing entries or add new ones.

    all_songs = sorted(existing_by_id.values(), key=lambda s: int(s["pv_id"]))

    output = {"excluded_ids": VANILLA_PV_IDS, "songs": all_songs}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(all_songs)} song(s) written to {OUTPUT_FILE}")
    print("The following placeholders still need to be filled manually: song_name_reading, bpm, performers.")
    print(f"date/sabi values were set to the requested defaults: {DEFAULT_DATE} / {DEFAULT_SABI_START} / {DEFAULT_SABI_PLAY}")


if __name__ == "__main__":
    main()
