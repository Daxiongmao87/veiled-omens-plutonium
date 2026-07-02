---
name: veiled-omens-plutonium-daily-alignment
description: Run the daily Veiled Omens Plutonium source/package alignment with full validators and Foundry import evidence.
---

Use this skill for the Veiled Omens Plutonium Daily Alignment task in `/home/agent/projects/veiled-omens-plutonium`.

Start by reading `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, and the repo validators as governing instructions. Treat `collection/Patrick Richardson; Veiled Omens Campaign Setting.json` as the canonical package and `veiled-omens-player-options-source` as read-only source material. Do not use Venoure testing, mounted-Foundry, SSHFS, object-manager, or VTT data-management instructions.

Discover source material from the symlink root each run. Inspect substantive text files under `Classes/`, `Items/`, `Races/`, and `Species/`; follow cross-references. For image-only PDFs, run OCR when source text is otherwise unavailable, then classify conflicts against newer text files by source date and content. In the July 2, 2026 run, the Occultist PDFs were May 4 image PDFs that conflicted with June text sources, so the current `.txt` and `.md` sources controlled.

Inventory the package from the canonical JSON and `_generated` indexes. List represented races/species, classes, subclasses, spells, items, and magic variants. Independently classify every source file as represented, missing, draft/legacy/lore-only/non-mechanical, or blocked/ambiguous, with exact source evidence. Do not classify a mechanic as excluded because it is absent from the package.

Compare both directions. Package-to-source must check names, prerequisites, level gates, granted features, spell lists, uses, recovery, DCs, damage, scaling, charges, attunement, rarity, item type, activities, proficiencies, languages, size, movement, senses, and rules-affecting prose. Source-to-package must prove every current player-facing mechanic is represented or evidence-backed as draft, legacy, lore-only, non-mechanical, or blocked.

Fix discrepancies in this repo only. Preserve `VeiledOmens` as the single source ID. Use TheGiddyLimit/homebrew and Plutonium bundled data for source-shape conventions. Keep source-authored `ItemGrant` rows out of package JSON. Add stable 16-character `_foundryId` values to race feature entries that flatten into Foundry feature items. When validator behavior conflicts with its documented invariant, repair the validator with a regression test rather than weakening source-accurate package text.

Run the exact validation command list after every package/tool/test fix:

```sh
python3 tools/generate-plutonium-indexes.py
python3 tools/validate-content-json.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
python3 tools/validate-plutonium-links.py
python3 tools/validate-prose-mechanics.py
python3 tools/validate-foundry-advancements.py
python3 -m unittest discover -s tests -v
```

Audit `_generated/index-sources.json` for one source ID per source package and `_generated/index-props.json` for collection mappings. Run stale-reference scans when source IDs or package paths change; record "none changed" when no such surface changed.

Run the real FoundryVTT/dnd5e + Plutonium path, not a JSON substitute. Verify `FOUNDRY_APP_DIR`, `FOUNDRY_DATA_DIR`, and `CHROMIUM_EXECUTABLE_PATH` exist. Use `TMPDIR=/dev/shm` on this host:

```sh
env TMPDIR=/dev/shm \
  FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry \
  FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data \
  CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
  node tools/validate-foundry-plutonium-import.mjs
```

Inspect `tmp/foundry-plutonium-import-result.json` for `status: "passed"`, `sourceLoaded: true`, package source `VeiledOmens`, imported race/class/subclass labels, no malformed advancement rows, and actor item evidence for changed mechanics. In the July 2 run, the harness used Foundry 14.364.0, dnd5e 5.3.3, Plutonium 2.15.10, imported 21 actor paths, and proved the flattened Goliath feature items imported with the added `_foundryId` values.

Report with these sections: inspected source paths, represented package mechanics checked, source mechanics missing from package, draft/legacy/lore-only/non-mechanical classifications with evidence, source files not fully inspected, changed files, exact commands run with pass/fail, Foundry/Plutonium evidence, discrepancies fixed, unresolved blockers, residual risk, and commit/push result. Commit and push verified fixes by default; if push fails, report the exact blocker and leave the local commit intact.
