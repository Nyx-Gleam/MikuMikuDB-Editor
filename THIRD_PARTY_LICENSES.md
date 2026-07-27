# Third-Party Licenses / Avisos de terceros

MikuMikuDB Editor is distributed under the MIT License (see [LICENSE](./LICENSE)).
It uses the following third-party components, each under its own license.

---

## Required dependencies

**PySide6** (Qt for Python)
License: **LGPLv3** (or commercial, from Qt Company)
https://www.qt.io/licensing/
The Qt libraries are linked dynamically and distributed as separate,
replaceable files alongside the application executable, as required by
the LGPL. Source code for this application is available in full at:
https://github.com/Nyx-Gleam/MikuMikuDB-Editor

**cryptography**
License: Apache License 2.0 / BSD (dual-licensed)
https://github.com/pyca/cryptography

**requests**
License: Apache License 2.0
https://github.com/psf/requests

---

## Optional dependencies (degrade gracefully if absent)

**pykakasi** (automatic Hiragana generation)
License: **GPL-3.0-only**. Bundles a relicensed portion of the UniDic
dictionary under GPL-3.0+.
https://github.com/miurahr/pykakasi
This dependency is optional; the application functions without it
(automatic Hiragana generation is simply unavailable).

**toml**
License: MIT
https://github.com/uiri/toml

**numpy**
License: BSD-3-Clause
https://numpy.org/

**madmom** (optional BPM auto-detection)
License:
- Source code: BSD-style permissive license, Copyright (c) Department of
  Computational Perception, Johannes Kepler University Linz, and OFAI.
- Pre-trained models: **Creative Commons Attribution-NonCommercial-ShareAlike
  4.0 (CC BY-NC-SA 4.0)**.
https://github.com/CPJKU/madmom
Because the bundled models are **non-commercial**, this project — and any
redistribution of it — must remain non-commercial for as long as these
models are included.

---

## Notes

* This file is generated for transparency and is not a substitute for
  reading each project's actual license text, which is included with
  the respective library where applicable.
* If you strip out `standalone_scripts/` or any optional dependency when
  redistributing your own build, you may remove the corresponding entry
  above, provided you are not shipping that code/model.
