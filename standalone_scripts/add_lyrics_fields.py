"""
add_lyrics_fields.py
======================
Script de UNA SOLA CORRIDA, standalone (igual que import_vanilla_songs.py):
agrega "lyrics": [] y "lyrics_en": [] a cada canción de tu
vanilla_songs.json que todavía no los tenga. NO TOCA nada más -- todo lo
que ya llenaste a mano (bpm, song_name_reading, performers, etc.) se
queda exactamente igual. Si una canción YA tiene "lyrics"/"lyrics_en",
se deja tal cual (no se sobrescribe).

Uso:
    1. Pon INPUT_FILE apuntando a tu archivo real (por defecto asume que
       está en la misma carpeta que este script).
    2. python add_lyrics_fields.py
    3. Revisa el resultado en OUTPUT_FILE antes de reemplazar tu archivo
       real, por seguridad (el script no sobreescribe el original solo).
"""
from __future__ import annotations

import json
import os
import shutil

INPUT_FILE = "vanilla_songs_output.json"
OUTPUT_FILE = "vanilla_songs_output_with_lyrics.json"
MAKE_BACKUP = True  # además del archivo de salida separado, hace un .backup del original


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"No se encontró {INPUT_FILE}. Ajusta INPUT_FILE arriba y vuelve a correr.")
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
        print(f"Backup del original guardado en: {backup_path}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{added} canciones recibieron lyrics/lyrics_en vacíos (listos para llenar).")
    print(f"{already_had} canciones ya los tenían, sin tocar.")
    print(f"Resultado en: {OUTPUT_FILE}")
    print("Revísalo y, cuando quieras, reemplaza tu vanilla_songs.json real con este contenido.")


if __name__ == "__main__":
    main()