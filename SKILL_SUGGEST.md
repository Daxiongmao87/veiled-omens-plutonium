---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package to current player-options source and verify it through repo validators plus the real Foundry/Plutonium import harness.
---

Work from `/home/agent/projects/veiled-omens-plutonium`. Treat `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, and repo validators as governing requirements. The canonical package is `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`; the player-options source is the symlink `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options`.

Start at the symlink root each run and discover source files live with `find -L veiled-omens-player-options-source -maxdepth 4 -type f` or `rg --files -L veiled-omens-player-options-source`. Treat the symlink target and `reference/` as read-only. For the 2026-07-01 run, rules-bearing source files inspected included `Races/ghost_elf.md`, `Races/nesherim.md`, `Races/onihan.md`, `Races/vaetyr.md`, `Races/wyrmblooded.md`, `Races/goliath_ogre_blooded.md`, `Races/goliath_ogre_blooded.local.md`, `Races/goliath_troll_blooded.md`, `Races/rimeheart_dwarves.md`, `Races/half_troll.txt`, `Races/_race_metadata/wyrmblooded.yaml`, `Species/Elves/ghost_elf.md`, `Classes/occultist.txt`, `Classes/occultist_spell_list.md`, `Classes/occultist_homebrew_spells.md`, `Classes/occultist_rite_of_haunts.txt`, `Classes/occultist_rite_of_omens.txt`, `Classes/occultist_rite_of_servitude.txt`, `Classes/thaumaphage.md`, `Classes/sorcerer_pale_touched.md`, `Classes/sorcerer_veil_touched.txt`, `Classes/barbarian_path_of_the_shaman.md`, and `Items/README.md`.

Inventory the package with parsed JSON. Extract represented `race`, `class`, `classFeature`, `subclass`, `subclassFeature`, `spell`, and `item` entries, then compare each represented mechanic to source for names, prerequisites, level gates, granted features, spell lists, uses, recovery, DCs, damage, scaling, charges, attunement, rarity, item type, activities, proficiencies, languages, size, movement, senses, and rules-affecting text. On 2026-07-01 the represented mechanics were 12 races, 2 classes, 30 class features, 7 subclasses, 39 subclass features, 23 spells, and 1 item.

Inspect matching TheGiddyLimit/homebrew and Plutonium reference examples before changing content conventions. For class spell lists, the 2026-07-01 governing examples were `reference/TheGiddyLimit-homebrew/class/KibblesTasty; Occultist.json` and `reference/TheGiddyLimit-homebrew/class/LaserLlama; Alternate Paladin.json`, which use class-level `classSpells`. Source-local spell UIDs use `Name|VeiledOmens`; official spells keep their official sources such as `|GGR`, `|TCE`, `|EGW`, `|SCC`, `|SatO`, and `|BMT`.

Use same-class audits for drift classes. On 2026-07-01, the discrepancy was missing class spell-list wiring: `Classes/occultist_spell_list.md` defined the Occultist spell list, but the package had no Occultist `classSpells`; Thaumaphage source spells also lacked `classSpells`. The correction added 89 Occultist `classSpells` entries matching source order, added Thaumaphage `Convert Essence|VeiledOmens` and `Ether Burn|VeiledOmens`, documented the convention, and added `validate_class_spells` coverage plus regression tests.

Check high-risk Plutonium conversion fields directly: `additionalSpells` for racial and fixed spell grants, string tool proficiencies for classes, `classFeatures` and `subclassFeatures` references, subclass header `refSubclassFeature` wiring, absence of source-authored `ItemGrant` rows, absence of source feature-grant `foundryAdvancement` rows, item `wondrous: true`, item charge/recharge fields, and `_generated/index-sources.json` mapping one `VeiledOmens` source to the canonical collection file.

Use the executor wrapper for code or validator edits, then independently inspect the diff and run verification. Regenerate indexes after JSON changes and run this exact validator sequence:

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

Audit `_generated/index-sources.json` and `_generated/index-props.json` after regeneration. On 2026-07-01, `index-sources.json` mapped `VeiledOmens` to `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`, `index-props.json` mapped `class`, `classFeature`, `item`, `race`, `spell`, `subclass`, and `subclassFeature` to `collection`, and the package source-field audit returned the single source ID `VeiledOmens`.

Run the real Foundry import harness after verifying paths are live:

```sh
test -d /home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry
test -d /home/agent/tmp/veiled-omens-foundry-import-1782310453848/data
test -f /home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome

TMPDIR=/dev/shm \
FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry \
FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data \
CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node tools/validate-foundry-plutonium-import.mjs
```

Read `tmp/foundry-plutonium-import-result.json` after the harness. Report `status`, `sourceLoaded`, Foundry/dnd5e/Plutonium versions, package source, import plan, imported labels, failures, malformed advancement row counts, item advancement row counts, and import count. On 2026-07-01 the report status was `passed`, `sourceLoaded` was `true`, versions were Foundry `14.364.0`, dnd5e `5.3.3`, Plutonium `2.15.10`, package source was `VeiledOmens`, imported count was 21, failures were empty, and malformed advancement rows were empty.

Final report format: source paths inspected, Plutonium files changed, exact commands run with pass/fail results, FoundryVTT/Plutonium evidence, alignment discrepancies fixed, unresolved blockers, residual risk, and commit/push result. Do not claim Foundry verification from JSON validators, generated indexes, process exit, or summaries without the real report evidence.
