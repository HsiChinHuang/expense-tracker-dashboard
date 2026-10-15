# Screenshots

This document is the relocation home for the reviewer-facing screenshot
prose that `README.md` carried until t66. The image files themselves did not
move: they stay in `screenshots/`.

## Sections absorbed from README.md

| README section absorbed | What moved here |
|---|---|
| `Screenshots` | The capture provenance, the inventory descriptions and the evidence-artifact caveats |

## Provenance

Four reviewer-facing images captured from one measured local run of the
merged stack (uvicorn on 127.0.0.1:8000 with the SQLite fallback engaged, the
Vite dev server on 127.0.0.1:5173, Playwright Chromium at a 1440x900 viewport,
no Docker daemon anywhere). Every figure in every image is fictional demo data
seeded through the public API - no real personal data appears in any image.

## Inventory

| File | What it shows |
|---|---|
| `screenshots/dashboard.png` | The four KPI cards, the five charts, the budget progress bar and the recent list for a seeded month |
| `screenshots/expense-form.png` | The Add expense form on the expenses page, filled with one demo entry |
| `screenshots/budget-page.png` | The budget page: the month budget, the progress surface and the set-month history |
| `screenshots/health-check.png` | The `/api/v1/health` payload as served through the dev-server proxy |

## Capture recipe and size policy

The capture recipe and the exact seed shape are pinned in the t52 grooming
card under `docs/issues/`. Each file is a PNG under 500 KB. The images are
evidence artifacts, not test fixtures, and no gate hashes their pixels (the
phase_8 ruling is that screenshots are measured artifacts gated on presence,
magic bytes, viewport width and size).
