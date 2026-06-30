---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package with live player-options source and verify through repo validators plus the real Foundry/Plutonium import harness.
---

Work from `/home/agent/projects/veiled-omens-plutonium`. Treat `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, and the repo validators as governing instructions. The canonical package file is `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`; the source material is the symlink `veiled-omens-player-options-source`.

Start by discovering source files under `veiled-omens-player-options-source` and following source cross-references. For this run, the decisive source files were `Races/nesherim.md`, `Races/wyrmblooded.md`, `Races/ghost_elf.md`, `Races/goliath_ogre_blooded.md`, `Classes/.changelog`, and the represented class/race spell files under `Classes/` and `Races/`. Treat the symlink target and `reference/` as read-only.

Inventory the package with parsed JSON, not loose text matching. Extract represented `race`, `class`, `subclass`, `classFeature`, `subclassFeature`, `spell`, `item`, `feat`, and `background` entries. Compare every represented mechanic to source for names, prerequisites, level gates, granted features, spell lists, uses, recovery, DCs, damage, scaling, charges, attunement, rarity, item type, activities, proficiencies, languages, size, movement, senses, and rules-affecting text.

Apply fixes through entity predicates such as race name, subclass name, class name, and feature name. Do not patch the first matching `Speed` or feature string. This run fixed Nesherim rules text, Wyrmblooded displayed speed, and removed unsupported package-only Occult Knight Fighter subclass records after source search found no current Occult Knight source or cross-reference. Verify edits with parsed extraction and stale-reference scans before validators.

Run the exact validator sequence:

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

Audit `_generated/index-sources.json` for the single `VeiledOmens` source mapping and `_generated/index-props.json` for collection mappings. Run stale-reference scans for removed terms.

Run the real Foundry import harness with live path checks first:

```sh
env TMPDIR=/dev/shm \
FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry \
FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data \
CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node tools/validate-foundry-plutonium-import.mjs
```

Read `tmp/foundry-plutonium-import-result.json` after the harness. Report `status`, `sourceLoaded`, Foundry/dnd5e/Plutonium versions, imported label count, malformed advancement row count, total item advancement rows, and labels for changed entities. Do not claim Foundry verification from JSON validators or exit status alone.

Final report format: source paths inspected, Plutonium files changed, exact commands run with pass/fail results, Foundry evidence, discrepancies fixed, unresolved blockers, residual risk, and commit/push result when changes were made.
