# MikuMikuDB Editor

🌐 **Language:** English | [Español](./README_ES.md) | [日本語](./README_JA.md)

> A GUI application for generating `mod_pv_db.txt` files for custom Project Diva song packs.
>
> **Version 2.0 BETA** — rebuilt from scratch on PySide6 (Qt), with a modular codebase, a single trilingual build (English/Spanish/Japanese), and a large set of new tools and bug fixes over the original Tkinter version.
 
---
 
## Table of Contents
 
1. [Overview](#overview)
2. [What's New in 2.0](#whats-new-in-20)
3. [Core Features](#core-features)
4. [Technical Requirements](#technical-requirements)
5. [Installation](#installation)
6. [Step-by-Step Usage](#step-by-step-usage)
7. [Configuration & Auto-Save](#configuration--auto-save)
8. [Exporting `mod_pv_db.txt`](#exporting-mod_pv_dbtxt)
9. [Project Structure](#project-structure)
10. [License](#license)
11. [Acknowledgments](#acknowledgments)
---
 
## Overview
 
MikuMikuDB Editor streamlines the creation of `mod_pv_db.txt` — the configuration file powering custom song packs in Project Diva. With an intuitive interface, modders can define pack metadata, song details, difficulty levels, credits, lyrics, sound effects, performers, and multiple audio variants per track, all without writing code.
 
* **Interface:** English, Spanish, and Japanese, switchable at any time from Settings (no more separate language builds).
* **Packaging:** Single executable for Windows 10/11 — no Python or dependencies needed.
* **Output:** Encrypted `.pdpack` project saves plus a final `mod_pv_db.txt` in UTF-8.
---
 
## What's New in 2.0
 
This version is a full rewrite of the application, not just a feature update:
 
* **New UI toolkit:** migrated from Tkinter to **PySide6 (Qt)** — native dark theme, native drag & drop, and HiDPI scaling that no longer needs a manual scaling system.
* **Instant audio preview:** the old engine exported every preview to a temporary WAV file and played it through a subprocess; the new one uses `QMediaPlayer` directly, so previews and seeking are instant with no temp files.
* **True trilingual interface:** English, Spanish, and Japanese now live in a single build and can be swapped from Settings at any time.
* **Two new tabs in the Song Editor:**
  * **Lyrics** — import from `.txt`, `.srt`, `.vtt`, `.ass`, `.ssa`, or `.lrc`, with line syncing between Japanese and English.
  * **SFX** — configure Button, Slide, Chain Slide, Slider Touch, and Chance sound effects per song.
* **BPM Calculator** — tap-tempo (with outlier rejection and averaging) plus optional automatic detection from the audio file.
* **New Song Info field:** Illustrator.
* **New optional field:** Song Name Reading (EN).
* **Installed Mods Browser** — scans your mods folder, lets you search songs by name/ID/artist across all of them, and import or export songs between an installed mod and your current project. Vanilla songs are excluded from the count so totals are accurate.
* **Missing Media Validator** — checks that every song's audio, video, and variant files actually exist on disk.
* **Create Missing Folders** — generates `sound/song`, `movie`, `script`, and `2d`, plus a default `config.toml` if one is missing.
* **Online PV ID validation** — checks whether a PV ID is already used or reserved before you commit to it.
* A standalone **`.pdpack` Decryptor Tool** is now included separately for diagnostics.
* A long list of correctness fixes came out of the rewrite, among them: a broken encryption format that could never be reopened, filename collisions in autosaves, a severe freeze on startup, a hardcoded mods folder path, and incorrect difficulty level ranges.
---
 
## Core Features
 
1. **Pack Metadata**
   * Enter **Pack Name** (Roman letters) and optional **Japanese Name**.
2. **Song Library**
   * Manage multiple songs via a table view: **PV ID**, **Original Name**, **English Name**.
   * Add, edit, or delete songs with dedicated buttons.
3. **Song Editor** (7-tab dialog)
   * **Basic Information:** PV ID, original & English titles, Hiragana reading, Romanized title, BPM (with tap/auto-detect calculator), date (YYYYMMDD), chorus (Sabi) start & duration.
   * **Difficulties:** Enable Easy/Normal/Hard/Extreme/Extra Extreme; assign each a valid `PV_LV_XX_X` code within the correct range for that difficulty.
   * **Performers:** Choose up to six vocalists from Hatsune Miku, Kagamine Rin/Len, Megurine Luka, KAITO, MEIKO, Yowane Haku, Akita Neru, Sakine Meiko, and Kasane Teto.
   * **Song Info:** Optional fields for arranger, lyricist, composer/artist, manipulator, guitar player, illustrator, and PV editor — each in original and English.
   * **Lyrics:** Type or import Japanese/English lyrics, with subtitle-format import and line syncing.
   * **Audio Variants:** Define alternate mixes or duets with their own name, artist, suffix, and performer list; Hiragana-only readings are enforced where required.
   * **SFX:** Configure Button, Slide, Chain Slide, Slider Touch, and Chance sound effects.
4. **Auto-Save & Manual Save**
   * Automatic `.pdpack` backups every 5 minutes (up to 60 files).
   * Manual **Save Configuration** and **Load Configuration** for encrypted project files, with automatic migration from legacy formats.
5. **Mods & PV IDs**
   * Browse installed mods and their songs, search across all of them, and move songs between mods and your current project.
   * Validate PV IDs against the online used/reserved database.
6. **Final Export**
   * Click **Generate File** to create a UTF-8 `mod_pv_db.txt` ready for a Project Diva pack.
   * Import an existing `mod_pv_db.txt` back into the editor at any time.
---
 
## Technical Requirements
 
* **Windows 10 or 11** (64-bit recommended).
* **Standalone build:** no installation of Python or libraries required — just run the executable.
* **Running from source:** Python 3.12+, plus `PySide6`, `cryptography`, and `requests`. Optional: `pykakasi` (automatic Hiragana generation), `toml` (reading `config.toml`), and `numpy` + `madmom` (automatic BPM detection).
---
 
## Installation
 
### Quick Installation (GitHub)
 
1. Visit the [GitHub Releases](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases) page.
2. Download the latest `MikuMikuDB Editor.exe`.
3. Double-click to run; if Windows warns about an unknown publisher, right-click → **Properties** → check **Unblock** → **Apply**, then run again.
### Alternative Installation (GameBanana)
 
1. Go to this tool's [GameBanana page](https://gamebanana.com/tools/19907).
2. Download the latest version of the editor.
3. Double-click `Editor.exe` to launch it — no installation required.
   * If Windows shows a security warning: right-click the file → **Properties** → check **Unblock** at the bottom → **Apply** → **OK**.
### Running from Source
 
1. Clone the repository:
```bash
   git clone https://github.com/Nyx-Gleam/MikuMikuDB-Editor.git
   cd MikuMikuDB-Editor
```
2. Create a virtual environment (use whichever command works on your system — `py` or `python`):
```bash
   py -m venv venv
   # or
   python -m venv venv
```
3. Activate it:
```bash
   .\venv\Scripts\activate
```
4. Install dependencies:
```bash
   pip install -r requirements.txt
```
5. Run the app:
```bash
   py main.py
```
 
> **Note:** `pykakasi`, `toml`, and `numpy`+`madmom` are optional (see [requirements.txt](./requirements.txt)) — the app runs without them, just with automatic Hiragana generation and BPM auto-detect disabled.
 
---
 
## Step-by-Step Usage
 
1. **Launch** the application and pick your interface language from **Settings** if needed.
2. Enter **Pack Name** and optional **Japanese Name**.
3. **Add Songs:**
   * Click **Add Song** to open the editor.
   * Fill in **Basic Information** (use the BPM calculator if you don't know the tempo).
   * Configure **Difficulties** and valid level codes.
   * Assign **Performers**.
   * Fill in **Song Info** and **Lyrics** (optional).
   * Define **Audio Variants** and **SFX** if needed.
   * Click **Accept** to save the song entry.
4. **Manage** the list: select a song and use **Edit** or **Delete**.
5. Optionally, browse **Installed Mods** to reuse or check songs from other packs.
6. Run **Validate Media Files** to make sure nothing is missing, and **Create Missing Folders** to scaffold your mod's folder structure.
7. Save your project anytime via **Save Configuration** (`.pdpack`).
8. When ready, click **Generate File** to export `mod_pv_db.txt`.
---
 
## Configuration & Auto-Save
 
* **Auto-Save:** every 5 minutes, an encrypted `.pdpack` is saved to the `Autosaves/` folder (max 60 files).
* **Manual Save/Load:** use **Save Configuration** / **Load Configuration** for encrypted project files; older `.pdpack` formats are migrated automatically.
* **Load Autosave:** quickly restore from a recent backup.
---
 
## Exporting `mod_pv_db.txt`
 
1. Make sure **Pack Name** is set and at least one song exists.
2. Click **Generate File**.
3. Choose a filename (default `mod_pv_db.txt`) and destination.
4. A UTF-8 `mod_pv_db.txt` with the full pack definition is created.
5. You can re-import that same file later with **Import mod_pv_db.txt** to keep editing it.
---
 
## Project Structure
 
```text
MikuMikuDB-Editor/
├── main.py                  # Entry point
├── core/                    # App logic: encryption, PV IDs, playback, pv_db format, etc.
├── ui/
│   ├── dialogs/              # Song editor, BPM calculator, mods browser, etc.
│   ├── widgets/               # Playback/seek bar and other shared widgets
│   └── main_window.py
├── localization/             # Language loading (data/lang.json)
├── data/                     # Settings, vanilla song catalog, language strings
├── pv_ids/                   # Used/reserved/free PV ID cache
├── standalone_scripts/        # Standalone .pdpack Decryptor Tool, misc tools
├── docs/guide.md              # In-app user guide
├── tests/                     # Regression test suite
└── Autosaves/                 # Auto-saved .pdpack files
```
 
---
 
## License
 
This project is released under the **MIT License**. See [LICENSE](./LICENSE) for details.
 
This project bundles third-party components under their own licenses (including one LGPLv3 and one GPLv3 dependency). See [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) for the full list.
 
---
 
## Acknowledgments
 
* Inspired by the vibrant Project Diva modding community.
* Developed and maintained by **NyxC**.
* Special thanks to all beta testers and contributors, especially for their patience through the 2.0 rewrite.
![Rin Fuwapuchi](images/rin_fuwapuchi.png)
