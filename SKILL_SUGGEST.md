---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package to current player-options source material and verify it through repo validators plus the real Foundry/Plutonium import harness.
---

Run context
- Work path: `/home/agent/projects/veiled-omens-plutonium`
- Governing docs read: `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`
- Canonical package file: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Source symlink: `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options`
- Source target and `reference/` were treated as read-only

Source discovery
- Discovery commands used: `readlink -f`, `find -L`, `rg --files -L`, and direct reads of substantive source files
- No narrower player-options discovery root was found
- Discovered represented material matched the same source regions as prior alignment runs (`Classes/`, `Races/`, `Species/`, `Items/`, and metadata under `Races/_race_metadata/`)

Package representation audit
- Package inventory on 2026-07-02: `race 12`, `class 2`, `classFeature 30`, `subclass 7`, `subclassFeature 39`, `spell 23`, `item 4`, `magicvariant 3`
- `_generated/index-sources.json`: `VeiledOmens` mapped to `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- `_generated/index-props.json`: `class`, `classFeature`, `item`, `magicvariant`, `race`, `spell`, `subclass`, `subclassFeature` all mapped to `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`

Represented mechanics confirmed in package
- Ghost Elf
- Nesherim (Beneshite, Nephilite, Seraphite)
- Goliath (Ogre-Blooded, Troll-Blooded)
- Onihan (Oni-zu, Go-zu, Me-zu)
- Vaetyr (Hearthbound, Runebound)
- Wyrmblooded
- Occultist
- Thaumaphage
- Rite of Haunts
- Rite of Omens
- Rite of Servitude
- Art of the Ether
- Art of the Flesh
- Pale Touched
- Path of the Shaman
- Occultist package spells plus Occultist-specific spell list, `Convert Essence`, and `Ether Burn`
- Items and magic variants: Arcavene Ring, Arcavene Wondrous Item, Mana Crystal, Shadesilver Armor, Arcavene Armor, Arcavene Weapon, Shadesilver Weapon

Evidence-backed exclusions / classifications
- `Classes/druid_circle_of_the_veil.md` is a stub (`STUB - Mechanics to be developed`)
- `Classes/monk_way_of_the_mists.md` is a stub (`STUB - Mechanics to be developed`)
- `Classes/paladin_oath_of_the_lantern.md` is a stub (`STUB - Mechanics to be developed`)
- `Classes/occultist_rite_of_haunts_invocation_draft.md` is a design draft (`Status: design draft`, not canon text)
- `Classes/sorcerer_veil_touched.txt` is legacy/defunct (`Veil Touched` is a defunct name for `Pale Touched`)
- `Races/half_troll.txt` is legacy/defunct (playable replacement noted as `goliath_troll_blooded.md`)
- `Races/rimeheart_dwarves.md` is lore/pending mechanics (`no distinct mechanical racial writeup is preserved`)
- `Species/Elves/ghost_elf.md` is GM-facing stub (player-facing mechanics are in `Races/ghost_elf.md`)
- `Races/_race_metadata/*.yaml` are non-diegetic naming/content guidance only, except Wyrmblooded metadata which corroborates but does not replace `Races/wyrmblooded.md`

PDF handling and source-corpus ambiguity
- All three occultist PDFs had identical `pdftotext` hashes but no extractable text from direct extraction
- OCR was run on `occultist-phb-v1.0-lite.pdf` with `pdftoppm + tesseract` in `/dev/shm`
- OCR produced 1,342 lines
- OCR identified `occultist-phb-v1.0-lite.pdf` as a full Occultist v1.0 supplement
- OCR showed `Bonecasting` for the Rite of Omens feature name
- Newer text-source files and package use `Cast the Lots`
- Source timestamps: `occultist_rite_of_omens.txt` and `occultist_homebrew_spells.md` at 2026-06-30, package at 2026-07-01, PDF at 2026-06-28
- Future runs must report this as unresolved source-corpus authority ambiguity

Validation commands run
- `python3 tools/generate-plutonium-indexes.py` -> pass, indexes already up to date
- `python3 tools/validate-content-json.py` -> pass, `1` content file checked, `14` repository JSON files parsed
- `python3 tools/generate-plutonium-indexes.py --check` -> pass
- `python3 tools/validate-plutonium-datasource.py` -> pass
- `python3 tools/validate-plutonium-links.py` -> pass
- `python3 tools/validate-prose-mechanics.py` -> pass, `1` content file scanned
- `python3 tools/validate-foundry-advancements.py` -> pass
- `python3 -m unittest discover -s tests -v` -> pass, `5 tests OK`

Stale/reference scans
- Active package scan for stale split source IDs, fake `WONDROUS` type, and type-specific package paths returned no active matches
- Broad scan reported hits only in docs/reference examples and a negative fixture, not in active package data

Foundry/Plutonium harness (2026-07-02)
- Command:

```sh
TMPDIR=/dev/shm FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome node tools/validate-foundry-plutonium-import.mjs
```

- Harness preflight: Foundry `14.364.0`, dnd5e `5.3.3`, Plutonium `2.15.10`, lib-wrapper `1.13.5.1`, Chromium present
- Reported: `tmp/foundry-plutonium-import-result.json` (repo-local)
- Status: `passed`
- `sourceLoaded: true`
- `failures: 0`
- `imported`: `21` actors (`12` races, `2` classes, `7` subclasses)
- `malformedAdvancementRows: 0`
- Representative evidence included race advancement rows and class/subclass real actor-path import verification

Run artifacts and scope outcome
- Working tree after 2026-07-02 validation had no package JSON/source/index edits
- `SKILL_SUGGEST.md` is the only file updated by this task
- JSON validators and index checks are not substitutes for Foundry harness evidence; real harness evidence is required and was included above

Required report fields for next run
- Source paths inspected
- Represented mechanics checked
- Missing source mechanics
- Evidence-backed exclusions
- Not fully inspected files
- Files changed
- Exact commands run with pass/fail
- Foundry evidence
- Discrepancies fixed
- Unresolved blockers
- Residual risk
- Commit/push result

Discrepancies fixed
- Replaced the prior 2026-07-01 run narrative with 2026-07-02 authoritative execution and evidence set
- Preserved package inventory and indexing facts updated to the checked 2026-07-02 state

Unresolved blockers and residual risk
- Source-corpus ambiguity remains for `Rite of Omens` naming when PDF and text sources disagree
- No unresolved content validation failures
- Commit/push status: not performed
