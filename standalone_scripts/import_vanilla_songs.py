"""
import_vanilla_songs.py
=========================
Script de UNA SOLA CORRIDA para generar el "songs" de vanilla_songs.json
usando la API de DivaModArchive. Standalone a propósito -- no vive dentro
de diva_editor/, no se importa desde ningún lado de core/ ni ui/, y no se
bundlea en el build. Lo corres tú una vez (o cada vez que quieras
regenerar/ampliar el catálogo) y después copias el resultado a
diva_editor/data/vanilla_songs.json a mano.

*** NO PUDE PROBAR LA LLAMADA REAL A LA API ***
Este entorno no tiene salida a internet hacia divamodarchive.com, así que
escribí esto según el curl y los parámetros que diste, pero no pude
confirmar en vivo que la sintaxis del filtro (`pv_id IN [...]`, estilo
meilisearch) o el límite real de resultados por página funcionen tal
cual. Si falla, revisa primero eso -- corre con un solo ID de prueba
antes de lanzarlo con la lista completa.

Qué SÍ automatiza (confirmado con tus datos de muestra):
- song_name, song_name_en
- songinfo (créditos JP/EN, los 7 campos -- 'ex_info' se descarta, no
  tiene equivalente en mod_pv_db.txt)
- difficulties -- orden inferido [easy, normal, hard, extreme,
  extreme_extra] a partir del array "levels" (verificado contra los
  rangos válidos de tu guía en las 10 canciones de muestra, pero
  igual conviene que revises un par a ojo). null = esa dificultad no
  existe para esa canción, se omite.

Qué NO trae la API (confirmado contigo, se llenan con tus defaults o
quedan como placeholder para llenar a mano):
- date -> fijo en DEFAULT_DATE (fecha de lanzamiento que definas)
- sabi_start / sabi_play -> fijos en DEFAULT_SABI_START / DEFAULT_SABI_PLAY
- song_name_reading (hiragana) -> placeholder "FILL_ME", a mano
- bpm -> placeholder "FILL_ME", a mano
- performers -> placeholder ["FILL_ME"], a mano (la API no dice quién canta)

Uso:
    1. pip install requests   (si no lo tienes ya)
    2. Llena VANILLA_PV_IDS abajo (pega tu lista de excluded_ids, por ejemplo)
    3. python import_vanilla_songs.py
    4. Revisa vanilla_songs_output.json, reemplaza los "FILL_ME", y copia
       el resultado a diva_editor/data/vanilla_songs.json
"""
from __future__ import annotations

import json
import os
import time

import requests

# ============================================================
# EDITA ESTO: pega aquí los PV IDs vanilla que quieres traer de la API
# (por ejemplo, los mismos que ya tienes en tu lista de excluded_ids).
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
# Configuración
# ============================================================
API_BASE_URL = "https://divamodarchive.com/api/v1/ids/pvs"
BATCH_SIZE = 50           # cuántos IDs pedir por llamada (ver nota sobre límites no confirmados arriba)
REQUEST_DELAY_SECONDS = 2   # pausa entre llamadas, para no golpear la API de golpe
REQUEST_TIMEOUT_SECONDS = 15

OUTPUT_FILE = "vanilla_songs_output.json"
EXISTING_FILE_TO_MERGE = "vanilla_songs_output.json"  # si ya existe, se actualiza en vez de empezar de cero

# Confirmados contigo:
DEFAULT_DATE = "20220526"       # fecha de lanzamiento de Mega Mix+ -- cámbiala si prefieres otra
DEFAULT_SABI_START = "0.0"
DEFAULT_SABI_PLAY = "20.0"
PLACEHOLDER_BPM = "FILL_ME"
PLACEHOLDER_READING = "FILL_ME"
PLACEHOLDER_PERFORMERS = ["FILL_ME"]

DIFFICULTY_ORDER = ["easy", "normal", "hard", "extreme", "extreme_extra"]
DEFAULT_LEVEL_SORT_INDEX = {"easy": 50, "normal": 50, "hard": 80, "extreme": 20, "extreme_extra": 50}


# ============================================================
# Llamadas a la API
# ============================================================
def _chunks(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def fetch_pvs_by_ids(pv_ids: list[int]) -> list[dict]:
    """Trae los datos de varios PV IDs de la API, en tandas de BATCH_SIZE."""
    all_pvs = []
    batches = list(_chunks(pv_ids, BATCH_SIZE))

    for n, batch in enumerate(batches, 1):
        filter_str = "pv_id IN [" + ", ".join(str(i) for i in batch) + "]"
        params = {"filter": filter_str, "limit": len(batch), "offset": 0}

        print(f"[{n}/{len(batches)}] Pidiendo {len(batch)} IDs ({batch[0]}..{batch[-1]})...")
        try:
            resp = requests.get(
                API_BASE_URL, params=params,
                headers={"accept": "application/json"},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()
            pvs = data.get("pvs", [])
            print(f"    -> {len(pvs)} resultados")
            all_pvs.extend(pvs)
        except Exception as e:
            print(f"    !! ERROR en esta tanda, se sigue con la siguiente: {e}")

        if n < len(batches):
            time.sleep(REQUEST_DELAY_SECONDS)

    return all_pvs


# ============================================================
# Conversión al formato de vanilla_songs.json
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
    """null en 'levels' = esa dificultad no existe para la canción -> se omite."""
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
        print("VANILLA_PV_IDS está vacío -- pega tus IDs arriba antes de correr esto.")
        return

    print(f"Consultando {len(VANILLA_PV_IDS)} PV IDs en la API de DivaModArchive...\n")
    raw_pvs = fetch_pvs_by_ids(VANILLA_PV_IDS)
    print(f"\nTotal traído: {len(raw_pvs)} de {len(VANILLA_PV_IDS)} pedidos")

    found_ids = {str(pv.get("id")) for pv in raw_pvs}
    missing = [i for i in VANILLA_PV_IDS if str(i) not in found_ids]
    if missing:
        print(f"AVISO: {len(missing)} IDs no se encontraron en la API: {missing}")

    songs = [convert_pv(pv) for pv in raw_pvs]

    # Si ya existe un output previo (de una corrida anterior con menos IDs),
    # se actualiza en vez de empezar de cero.
    existing_by_id = {}
    if os.path.exists(EXISTING_FILE_TO_MERGE):
        try:
            with open(EXISTING_FILE_TO_MERGE, "r", encoding="utf-8") as f:
                prev = json.load(f)
            existing_by_id = {s["pv_id"]: s for s in prev.get("songs", [])}
            print(f"Se encontró {EXISTING_FILE_TO_MERGE} previo con {len(existing_by_id)} canciones -- se combina.")
        except Exception as e:
            print(f"No se pudo leer {EXISTING_FILE_TO_MERGE} previo, se ignora: {e}")

    for song in songs:
        existing_by_id[song["pv_id"]] = song  # sobrescribe si ya existía, agrega si es nuevo

    all_songs = sorted(existing_by_id.values(), key=lambda s: int(s["pv_id"]))

    output = {"excluded_ids": [], "songs": all_songs}
    # NOTA: excluded_ids queda vacío aquí a propósito -- ese campo ya lo
    # tienes armado en tu vanilla_songs.json real. Este script solo genera
    # la lista de "songs"; copia solo esa parte a tu archivo final, o pega
    # tu excluded_ids ya armado en el output antes de copiarlo.

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nListo. {len(all_songs)} canciones escritas en {OUTPUT_FILE}")
    print("Pendiente de llenar a mano (marcado 'FILL_ME'): song_name_reading, bpm, performers.")
    print(f"date/sabi quedaron con los defaults que pediste: {DEFAULT_DATE} / {DEFAULT_SABI_START} / {DEFAULT_SABI_PLAY}")


if __name__ == "__main__":
    main()