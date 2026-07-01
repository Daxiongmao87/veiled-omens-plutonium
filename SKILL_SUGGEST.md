---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package to current player-options source material and verify it through repo validators plus the real Foundry/Plutonium import harness.
---

Work from `/home/agent/projects/veiled-omens-plutonium`. Treat `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, repo validators, and the canonical package `collection/Patrick Richardson; Veiled Omens Campaign Setting.json` as governing requirements. The player-options source is the symlink `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options`; inspect through the symlink and treat the symlink target plus `reference/` as read-only.

Start each run by discovering source material live from the symlink root. In the 2026-07-01 run, `find -L veiled-omens-player-options-source -maxdepth 4 -type f` found source files under `Classes/`, `Races/`, `Races/_race_metadata/`, `Species/Elves/`, and `Items/`. No source file documented a narrower discovery root. The represented-package comparison inspected these rules-bearing source paths: `Classes/occultist.txt`, `Classes/occultist_spell_list.md`, `Classes/occultist_homebrew_spells.md`, `Classes/occultist_rite_of_haunts.txt`, `Classes/occultist_rite_of_omens.txt`, `Classes/occultist_rite_of_servitude.txt`, `Classes/thaumaphage.md`, `Classes/sorcerer_pale_touched.md`, `Classes/barbarian_path_of_the_shaman.md`, `Races/ghost_elf.md`, `Species/Elves/ghost_elf.md`, `Races/nesherim.md`, `Races/goliath_ogre_blooded.md`, `Races/goliath_ogre_blooded.local.md`, `Races/goliath_troll_blooded.md`, `Races/onihan.md`, `Races/vaetyr.md`, `Races/wyrmblooded.md`, and `Races/_race_metadata/wyrmblooded.yaml`.

Inventory the canonical package with parsed JSON before comparing source text. For the 2026-07-01 run, the package represented 12 races/species, 2 classes, 7 subclasses, 30 class features, 39 subclass features, 23 spells, and 1 item. Compare represented mechanics against source for names, prerequisites, level gates, granted features, spell lists, uses, recovery, DCs, damage, scaling, charges, attunement, rarity, item type, activities, proficiencies, languages, size, movement, senses, and rules-affecting text. Use structured JSON parsing for package fields such as `ability`, `size`, `speed`, `languageProficiencies`, `skillProficiencies`, `toolProficiencies`, `resist`, `vulnerable`, `additionalSpells`, `classSpells`, `classFeatures`, `subclassFeatures`, and item charge/recharge fields.

High-risk checks from this execution: Occultist `classSpells` matched `Classes/occultist_spell_list.md` exactly at 89 entries with no missing or extra UIDs; all 21 Occultist homebrew spell records existed; Thaumaphage had the Constitution 13 and Wisdom 13 multiclass requirements, string tool proficiencies, `Convert Essence|VeiledOmens` and `Ether Burn|VeiledOmens` class spell entries, and Mana Crystal starting equipment; races matched source mechanics for ability changes, size, speed, languages, darkvision, skill/tool proficiencies, resistances, vulnerability, and racial spell grants; Mana Crystal used `wondrous: true`, rarity `uncommon`, attunement, variable charges, and `recharge: "restLong"`. No content discrepancy was established and no Plutonium JSON/tool/doc fix was made in this execution.

If a discrepancy requires code, validator, JSON, or doc edits, use the executor wrapper for implementation, then independently inspect the diff and rerun the full validation path. Do not edit `reference/` or the symlink target. Regenerate indexes after JSON changes.

Run this validator sequence exactly and record pass/fail output:

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

In the 2026-07-01 run, all eight commands passed. Index generation reported already up to date; content validation checked 1 content file and parsed 14 repository JSON files; prose mechanics scanned 1 content file; unittest discovery ran 5 tests with `OK`.

Audit `_generated/index-sources.json` and `_generated/index-props.json` after validation. In this execution, `index-sources.json` mapped `VeiledOmens` to `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`; `index-props.json` mapped `class`, `classFeature`, `item`, `race`, `spell`, `subclass`, and `subclassFeature` to `collection`; active content source fields contained only `VeiledOmens`.

Verify the real Foundry harness paths live before running the browser-driven import:

```sh
ls -ld /home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry
ls -ld /home/agent/tmp/veiled-omens-foundry-import-1782310453848/data
ls -l /home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome
df -h / /dev/shm
```

Then run the real harness with actual FoundryVTT, dnd5e, Plutonium, lib-wrapper, and Chromium:

```sh
env TMPDIR=/dev/shm FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome node tools/validate-foundry-plutonium-import.mjs
```

Read `tmp/foundry-plutonium-import-result.json` after the harness. In this execution, the harness exited 0, wrote the report, and the report status was `passed`; `sourceLoaded` was `true`; package source was `VeiledOmens`; versions were Foundry `14.364.0`, dnd5e `5.3.3`, Plutonium `2.15.10`, and lib-wrapper `1.13.5.1` from preflight output; the import plan covered 12 races, 2 classes, and 7 subclasses at levels `1,2,3`; imported count was 21 and failures count was 0.

Final report format: source paths inspected, Plutonium files changed, exact commands run with pass/fail results, FoundryVTT/Plutonium evidence from the report, alignment discrepancies fixed, unresolved blockers, residual risk, and commit/push result. Do not claim Foundry verification from JSON validators, generated indexes, process exit, or package parsing without report evidence from the real harness.
