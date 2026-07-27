# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 2.0 BETA (in development) | ✅ |
| 1.1 | ⚠️ Best-effort only |
| 1.0 | ❌ |

## Reporting a Vulnerability

If you find a security issue — for example, something related to the `.pdpack` encryption scheme, the online PV ID validation requests, or a way to execute unintended code through a malformed pack file — please **do not open a public Issue**.

Instead, report it privately using one of these options:

1. **GitHub Private Vulnerability Reporting:** go to the **Security** tab of this repository → **Report a vulnerability**. This creates a private advisory only visible to the maintainer.
2. If that isn't available for any reason, reach out directly via [Discord/contact method you prefer] with the details.

Please include:
- A description of the issue and its potential impact.
- Steps to reproduce, or a proof-of-concept file (`.pdpack`, `mod_pv_db.txt`, etc.) if relevant.
- Your suggested severity, if you have one in mind.

I'll do my best to acknowledge reports within a few days and follow up once there's a fix or mitigation. Credit will be given in the release notes unless you'd prefer to stay anonymous.

## Scope

This policy covers the MikuMikuDB Editor application itself (encryption, file parsing, network requests it makes). It does not cover third-party dependencies (PySide6, cryptography, requests, madmom, etc.) — please report those directly to their own maintainers.
