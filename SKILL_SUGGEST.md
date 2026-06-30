---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package with current player-options source and verify it through repo validators plus the real Foundry/Plutonium import harness.
---

Work from `/home/agent/projects/veiled-omens-plutonium`. Treat `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, and the repo validators as governing instructions. The canonical package is `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`; the player-options source is the symlink `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options`.

Start at the symlink root each run and discover live source files with `rg --files` or `find -L`. Treat the symlink target and `reference/` as read-only. For the 2026-06-30 run, represented rules-bearing source files inspected were `Races/ghost_elf.md`, `Races/nesherim.md`, `Races/goliath_ogre_blooded.md`, `Races/goliath_ogre_blooded.local.md`, `Races/goliath_troll_blooded.md`, `Races/onihan.md`, `Races/vaetyr.md`, `Races/wyrmblooded.md`, `Classes/occultist.txt`, `Classes/occultist_spell_list.md`, `Classes/occultist_homebrew_spells.md`, `Classes/occultist_rite_of_haunts.txt`, `Classes/occultist_rite_of_omens.txt`, `Classes/occultist_rite_of_servitude.txt`, `Classes/thaumaphage.md`, `Classes/sorcerer_pale_touched.md`, and `Classes/barbarian_path_of_the_shaman.md`.

Classify source status before treating missing package entries as discrepancies. In the 2026-06-30 run, `Classes/druid_circle_of_the_veil.md`, `Classes/monk_way_of_the_mists.md`, and `Classes/paladin_oath_of_the_lantern.md` were mechanics stubs; `Classes/sorcerer_veil_touched.txt` was a defunct legacy source for current `Pale Touched`; `Classes/occultist_rite_of_haunts_invocation_draft.md` was non-canon draft text; `Races/half_troll.txt` was defunct legacy source for `Goliath (Troll-Blooded)`; `Races/rimeheart_dwarves.md` had no recovered mechanical writeup; `Species/Elves/ghost_elf.md` was a setting-agnostic stub while `Races/ghost_elf.md` held the rules text.

Inventory the package with parsed JSON, not loose text matching. Extract represented `race`, `class`, `classFeature`, `subclass`, `subclassFeature`, `spell`, and `item` entries. Compare every represented mechanic to source for names, prerequisites, level gates, granted features, spell lists, uses, recovery, DCs, damage, scaling, charges, attunement, rarity, item type, activities, proficiencies, languages, size, movement, senses, and rules-affecting text.

Check high-risk Plutonium conversion fields directly: `additionalSpells` for racial and fixed spell grants, string tool proficiencies for classes, `classFeatures` and `subclassFeatures` references, subclass header `refSubclassFeature` wiring, absence of source-authored `ItemGrant` rows, absence of source `foundryAdvancement` feature-grant rows, item `wondrous: true`, item charge/recharge fields, and `_generated/index-sources.json` mapping a single `VeiledOmens` source to the canonical collection file. On 2026-06-30 these checks found no source-controlled package discrepancies.

Run the exact validator sequence and record pass/fail results:

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

Run the real Foundry import harness after verifying paths are live:

```sh
TMPDIR=/dev/shm \
FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry \
FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data \
CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node tools/validate-foundry-plutonium-import.mjs
```

Read `tmp/foundry-plutonium-import-result.json` after the harness. Report `status`, `sourceLoaded`, Foundry/dnd5e/Plutonium versions, import plan counts, imported labels, malformed advancement row counts, item advancement row counts, and failures. On 2026-06-30 the report status was `passed`, `sourceLoaded` was `true`, versions were Foundry `14.364.0`, dnd5e `5.3.3`, Plutonium `2.15.10`, and the import covered 12 races, 2 classes, and 7 subclasses with `failures: []`.

Final report format: source paths inspected, Plutonium files changed, exact commands run with pass/fail results, FoundryVTT/Plutonium evidence, alignment discrepancies fixed, unresolved blockers, residual risk, and commit/push result when repository changes were made. Do not claim Foundry verification from JSON validators or exit status alone.
