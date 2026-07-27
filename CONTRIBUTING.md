# Contributing to MikuMikuDB Editor

Thanks for considering contributing! This project is still in active development (2.0 BETA), so a few things work a little differently than a typical stable repo.

You can write issues, PRs, and discussions in **English, Spanish, or Japanese** — whichever is easiest for you.

---

## Branch structure

- **`main`** — the latest **stable, released** version only. Don't target this branch with a PR unless you're submitting a hotfix for an already-released version.
- **`V2.0-dev`** — active development branch for the upcoming 2.0 release. **This is where almost all pull requests should be targeted.**
- Other `VX.Y-dev` branches may exist for future versions once 2.0 ships.

If you're not sure which branch to target, open a Discussion first or just ask in your PR description — it's not a big deal to redirect it.

---

## Getting set up

1. Fork the repository and clone your fork.
2. Follow the **[Running from Source](./README.md#running-from-source)** instructions in the README (clone → virtual environment → `pip install -r requirements.txt` → `py main.py`).
3. Note that `madmom` (optional, used for BPM auto-detection) is **not** installed via `requirements.txt` — see the README for why and how to get it manually if you need that feature for your change.
4. Create your branch off of `V2.0-dev`, not `main`.

---

## Before opening a Pull Request

- Make sure the app still runs from source without errors.
- Don't commit `config.toml`, `Autosaves/`, `.pdpack` files, `venv/`, or `__pycache__/` — these are covered by `.gitignore`, but double-check if you added anything manually.
- If you added a new dependency, add it to `requirements.txt` (or explain why not, following the `madmom` precedent).
- If you changed any user-facing text, flag which language(s) in `data/lang.json` still need the equivalent update — translations for all three languages aren't required from you, just flag what's missing so it can be tracked.
- Fill out the PR template — it has a short checklist covering the points above.

---

## Reporting bugs / requesting features

Please use the Issue templates rather than a blank issue — they ask for the specific information (OS, whether you're running the `.exe` or from source, reproduction steps, `editor_crash.log`) that makes bugs actually fixable. There's also a dedicated template for translation issues if the problem is text-related rather than a functional bug.

For general questions, ideas you haven't fully fleshed out, or wanting to help test the 2.0 BETA, use **Discussions** instead of an Issue.

---

## Code style

- Python, following the existing structure under `core/`, `ui/`, `localization/` — try to match the module a change belongs to rather than adding new top-level files for small additions.
- An `.editorconfig` is included; most editors pick it up automatically for indentation and line endings.

---

## Licensing

By contributing, you agree your contribution is licensed under the project's [MIT License](./LICENSE). Please don't submit code you don't have the rights to license this way (e.g. copied from a differently-licensed project).
