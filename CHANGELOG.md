# Changelog
 
All notable changes to MikuMikuDB Editor are documented here. Dates and full details for each release are in the [Releases](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases) page — this file is a quick, single-page overview of what changed between versions.
 
Format loosely based on [Keep a Changelog](https://keepachangelog.com/).
 
---
 
## [Unreleased] — 2.0 BETA (in development)
 
No downloadable build yet — see the [2.0 BETA release notes](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases) for the full write-up.
 
### Added
- Full rewrite of the UI from Tkinter to PySide6 (Qt) — native dark theme, native drag & drop, proper HiDPI scaling.
- Single trilingual build (English/Spanish/Japanese), switchable anytime from Settings.
- Instant audio preview via `QMediaPlayer` (no more temp WAV files).
- Two new Song Editor tabs: **Lyrics** (import from `.txt`/`.srt`/`.vtt`/`.ass`/`.ssa`/`.lrc`) and **SFX** (Button/Slide/Chain Slide/Slider Touch/Chance).
- BPM Calculator: tap-tempo with outlier rejection, plus optional automatic detection via `madmom`.
- New `Illustrator` field in Song Info; new optional `Song Name Reading (EN)` field.
- Installed Mods Browser (search/import/export songs across installed mods, with vanilla songs excluded from counts).
- Missing Media Validator and Create Missing Folders tool.
- Online PV ID validation against the used/reserved database.
- Standalone `.pdpack` Decryptor Tool (kept internal, not distributed).
- Modular codebase (`core/`, `ui/`, `localization/`) replacing the single-file structure.
### Fixed
- V3 encryption format that could never be reopened once saved.
- Startup routine that attempted to build a ~4.29 billion-integer set, causing freezes/OOM.
- Filename collisions in autosaves and PV ID fragments (moved to nanosecond-resolution timestamps).
- Hardcoded mods folder path.
- Incorrect difficulty level ranges.
- Several silent roundtrip bugs in `mod_pv_db.txt` parsing.
- Global crash handler that wasn't actually wired up.
---
 
## [1.1] — BETA
 
### Added
- Audio Variants now support multiple performers (up to 6 per variant).
- Custom file suffix for variant audio files, for finer control over `.ogg` output naming.
- Hiragana-only input validation for song and variant reading fields.
- Encrypted `.pdpack` configuration files (custom AES-256 + password-derived encryption).
- Drag & drop support for loading files into the editor window.
- Improved auto-save system, rotating up to 60 files in `Autosaves/`.
- Import of existing `mod_pv_db.txt` files to restore song lists and settings.
### Changed
- Scrollable GUI layout for better screen adaptability.
- Additional validation and error checking for performer counts, difficulty settings, and song metadata.
- Improved error handling around file operations and encryption.
### Distribution
- Distributed as a single `.exe` (no `.py` script), separate builds for English and Japanese.
---
 
## [1.0] — Initial release
 
The first public version of the editor.
 
> ⚠️ The source code for v1.0 was lost during development and could not be recovered in full. Only the compiled `.exe` builds remain, available on the [Releases](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases) page. Source code tracking begins formally with v1.1.
