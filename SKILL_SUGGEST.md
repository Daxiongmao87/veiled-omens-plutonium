---
name: veiled-omens-plutonium-daily-alignment
description: Run the Veiled Omens Plutonium daily source-to-package alignment audit and real Foundry validation.
---

Use this pattern for the daily Veiled Omens Plutonium alignment run.

Start with the Patrick gates required by the active AGENTS.md: first-action retrieval of `/home/agent/.codex/AGENTS.md` and `/home/agent/.codex/patrick-correction-ledger.md`, the Patrick Reality Check counts, an Exact-Request Allowlist, a Same-Class Contract, and a Power and Authority Gate. Do not replace source-to-package alignment with JSON validity, generated indexes, summaries, or partial samples.

Read the governing repo surfaces before touching data: `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`, `_generated/index-sources.json`, and `_generated/index-props.json`. Keep the canonical source package as one collection file with source ID `VeiledOmens`.

Discover current player-facing source material from the symlink `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options`. Treat the symlink target and `reference/` as read-only. Inspect all substantive source files, including image-only PDFs through OCR when needed. In this run, the Occultist PDFs were image PDFs; OCR classified them as the current Occultist v1.0 supplement containing the Occultist class, three rites, spell list, and original spells.

Build a two-way alignment table:
- Package represented mechanics: races/species, classes, subclasses, class features, subclass features, spells, items, magic variants, feats/backgrounds if present.
- Source mechanics: every substantive `.md`, `.txt`, `.yaml`, and `.pdf` source file under the symlink.
- Evidence-backed exclusions: stubs with "Mechanics to be developed"; legacy files marked "Legacy Source / Defunct"; lore-only files that state no current mechanical writeup; non-diegetic metadata YAML files.

Use TheGiddyLimit/homebrew and Plutonium bundled data as convention controls before changing source shape. For this run, relevant controls were official/bundled race, class, subclass, item, and magicvariant examples. Keep source-authored `ItemGrant` rows out of source JSON. Preserve existing `_foundryId` values and 5etools tags.

When fixing discrepancies, update the canonical package JSON, then inspect the actual resulting entries with `jq` and `git diff`. Do not accept an executor summary or validator pass if the diff reverts a prior source-aligned correction. In this run the repaired discrepancies were the Ghost Elf quote and Vaetyr shared and trait prose, aligned to `Races/ghost_elf.md` and `Races/vaetyr.md` while preserving mechanics.

Run the exact validator sequence after all JSON changes:
1. `python3 tools/generate-plutonium-indexes.py`
2. `python3 tools/validate-content-json.py`
3. `python3 tools/generate-plutonium-indexes.py --check`
4. `python3 tools/validate-plutonium-datasource.py`
5. `python3 tools/validate-plutonium-links.py`
6. `python3 tools/validate-prose-mechanics.py`
7. `python3 tools/validate-foundry-advancements.py`
8. `python3 -m unittest discover -s tests -v`

Audit `_generated/index-sources.json` for one source ID per source package and `_generated/index-props.json` for collection mappings. Run stale-reference checks for deleted package paths or removed source IDs; if no source IDs or package paths were removed, record that evidence.

Run the real FoundryVTT/dnd5e + Plutonium harness, not a substitute:

```sh
TMPDIR=/dev/shm \
FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry \
FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data \
CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node tools/validate-foundry-plutonium-import.mjs
```

Verify those three environment paths live before running. Read `tmp/foundry-plutonium-import-result.json` after the harness and report `status`, versions, imported labels, malformed advancement row count, and item advancement row count. A clean run in this execution reported Foundry 14.364.0, dnd5e 5.3.3, Plutonium 2.15.10, `status: passed`, 21 imported race/class/subclass labels, 0 malformed rows, and 137 item advancement rows.

Final reporting must include: source paths inspected, represented mechanics checked, missing source mechanics, excluded source files with evidence, uninspected files, package files changed, exact commands run with pass/fail results, Foundry evidence, discrepancies fixed, unresolved blockers, residual risk, and commit/push result.
