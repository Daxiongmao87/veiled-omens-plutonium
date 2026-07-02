---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package to current player-options source material and verify it through repo validators plus the real Foundry/Plutonium import harness.
---

Run context
- Work path: `/home/agent/projects/veiled-omens-plutonium`
- Governing docs read: `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`
- Canonical package file: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Source symlink: `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options` (treated read-only)
- `reference/` was treated as read-only

Source discovery and evidence
- Source discovery covered `Classes`, `Races`, `Species`, `Items`, `Races/_race_metadata`, and Occultist PDF OCR artifacts.
- `druid_circle_of_the_veil.md` — `STUB` mechanics-to-be-developed
- `monk_way_of_the_mists.md` — `STUB` mechanics-to-be-developed
- `paladin_oath_of_the_lantern.md` — `STUB` mechanics-to-be-developed
- `occultist_rite_of_haunts_invocation_draft.md` — design draft, explicitly stated not canon text
- `sorcerer_veil_touched.txt` — `Veil Touched` is a defunct name for current `Pale Touched`
- `half_troll.txt` — legacy and not a current playable race
- `rimeheart_dwarves.md` — no distinct mechanical racial writeup preserved
- `Species/Elves/ghost_elf.md` — setting-agnostic GM-facing stub; active player mechanics are in `Races/ghost_elf.md`
- `Races/_race_metadata` YAMLs are non-mechanical naming/source guidance except `wyrmblooded` metadata, which corroborates active `Races/wyrmblooded.md`

Package inventory and index evidence
- Inventory: `race 12`, `class 2`, `classFeature 30`, `subclass 7`, `subclassFeature 39`, `spell 23`, `item 4`, `magicvariant 3`
- `_generated/index-sources.json`: maps `VeiledOmens` to `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- `_generated/index-props.json`: maps `class`, `classFeature`, `item`, `magicvariant`, `race`, `spell`, `subclass`, `subclassFeature` to `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`

Discrepancy fixed
- Changed Arcavene rarity inheritance from fixed `rare` to `varies` where source category is variable:
  - `arcavene_rings.md` category Ring (rare or very rare)
  - `arcavene_wondrous_items.md` category Wondrous item (rare or very rare)
  - `arcavene_armor.md` category Armor (rare or very rare)
  - `arcavene_weapons.md` category Weapon (rare or very rare)
- This resolved the package entries:
  - `Arcavene Ring`
  - `Arcavene Wondrous Item`
  - `Arcavene Armor`
  - `Arcavene Weapon`

PDF handling and source-corpus conflict
- Tools present: `/usr/bin/pdftotext`, `/usr/bin/pdftoppm`, `/usr/bin/tesseract`
- `occultist-phb-v1.0-lite.pdf` direct `pdftotext` produced no usable text.
- Binary hashes were recorded for all three Occultist PDFs.
- OCR was run on all 20 pages of `occultist-phb-v1.0-lite.pdf` with `pdftoppm + tesseract` in `/dev/shm`.
- OCR output length: `2707` lines.
- `occultist_rite_of_omens.txt` states current feature text as `Cast the Lots` and notes: `Working mechanical draft. The current structure treats subclass spells as part of the feature budget`.
- OCR source still surfaced older Rite of Omens naming (`Bonecasting`), creating a source-corpus authority conflict.

Official 2014 reference and homebrew convention checks
- Sampled reference/prose review rows were checked from `reference/5etools-live-2014/raw/data`:
  - `Elf|PHB`, `Tiefling|PHB`
  - `Ring of Protection|DMG`
  - `Robe of the Archmagi|DMG`
  - `Bracers of Defense|DMG`
  - `Spiritual Weapon|PHB`
  - `False Life|PHB`
  - `Bestow Curse|PHB`
  - `Warding Bond|PHB`
  - `Speak with Dead|PHB`
- The `Rarity varies` convention was verified against `TheGiddyLimit/homebrew` examples for magic variants.

Validation and harness evidence
- `python3 tools/generate-plutonium-indexes.py` (pass; indexes already up to date)
- `python3 tools/validate-content-json.py` (pass; `1` content file checked, `14` repository JSON files parsed)
- `python3 tools/generate-plutonium-indexes.py --check` (pass)
- `python3 tools/validate-plutonium-datasource.py` (pass)
- `python3 tools/validate-plutonium-links.py` (pass)
- `python3 tools/validate-prose-mechanics.py` (pass; `1` content file scanned)
- `python3 tools/validate-foundry-advancements.py` (pass)
- `python3 -m unittest discover -s tests -v` (pass; `5 tests OK`)
- `tmp/foundry-plutonium-import-result.json` generated from this run; command:

```sh
TMPDIR=/dev/shm \
FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry \
FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data \
CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node tools/validate-foundry-plutonium-import.mjs
```

- Foundry preflight: Foundry `14.364.0`, dnd5e `5.3.3`, Plutonium `2.15.10`, lib-wrapper `1.13.5.1`, Chromium present.
- Reported `tmp/foundry-plutonium-import-result.json` values:
  - `status: passed`
  - `sourceLoaded: true`
  - `packageSource: VeiledOmens`
  - `importedCount: 21`
  - `failuresCount: 0`
  - `malformedRows: 0`
  - `timestamp: 2026-07-02T12:54:43.319Z`
  - breakdown: `12` races, `2` classes, `7` subclasses

Stale/reference scan and residual risk
- Scan covered removed source IDs, fake `WONDROUS` type paths, and type-specific package paths for the active package and generated indexes.
- No active matches were returned.
- Residual risk remains: `occultist-phb-v1.0-lite.pdf` conflicts with newer text source for Rite of Omens naming; this run keeps package content aligned to the newer text source and requires explicit reporting until source authority is resolved.

Required future-run pattern
- Create explicit coverage inventory.
- Classify every source file with evidence.
- Never treat not represented as an exclusion.
- Fix package discrepancies.
- Re-run exact validators in this order.
- Run the real Foundry/Plutonium harness.
- Inspect the report JSON.
- Update this file with execution results.
