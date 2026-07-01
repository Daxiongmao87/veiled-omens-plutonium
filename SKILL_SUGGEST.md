---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package to current player-options source and verify it through repo validators plus the real Foundry/Plutonium import harness.
---

Work from `/home/agent/projects/veiled-omens-plutonium`. Treat `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, and repo validators as governing requirements. The canonical package is `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`; the player-options source is the symlink `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options`.

Start at the symlink root each run and discover source files live with `find -L veiled-omens-player-options-source -maxdepth 4 -type f` or `rg --files -L veiled-omens-player-options-source`. Treat the symlink target and `reference/` as read-only. For the 2026-07-01 run, rules-bearing source files inspected included `Races/ghost_elf.md`, `Races/nesherim.md`, `Races/goliath_ogre_blooded.md`, `Races/goliath_ogre_blooded.local.md`, `Races/goliath_troll_blooded.md`, `Races/onihan.md`, `Races/vaetyr.md`, `Races/wyrmblooded.md`, `Classes/occultist.txt`, `Classes/occultist_spell_list.md`, `Classes/occultist_homebrew_spells.md`, `Classes/occultist_rite_of_haunts.txt`, `Classes/occultist_rite_of_omens.txt`, `Classes/occultist_rite_of_servitude.txt`, `Classes/thaumaphage.md`, `Classes/sorcerer_pale_touched.md`, `Classes/barbarian_path_of_the_shaman.md`, `Items/README.md`, `Items/shadesilver_weapons.md`, and `Items/shadesilver_armor.md`.

Classify source status before treating absent package entries as discrepancies. During the 2026-07-01 run, `Classes/sorcerer_veil_touched.txt` was legacy for current `sorcerer_pale_touched.md`, `Races/half_troll.txt` was legacy for current Troll-Blooded Goliath, `Classes/occultist_rite_of_haunts_invocation_draft.md` was non-canon draft text, `Races/rimeheart_dwarves.md` had no recovered distinct mechanics, and `Species/Elves/ghost_elf.md` was a GM-facing stub with player mechanics moved to `Races/ghost_elf.md`.

Inventory the package with parsed JSON, not loose text matching. Extract represented `race`, `class`, `classFeature`, `subclass`, `subclassFeature`, `spell`, and `item` entries. Compare each represented mechanic to source for names, prerequisites, level gates, granted features, spell lists, uses, recovery, DCs, damage, scaling, charges, attunement, rarity, item type, activities, proficiencies, languages, size, movement, senses, and rules-affecting text.

Use same-class audits for drift classes. On 2026-07-01, a damage-type drift audit found unsupported psychic/choice variants where source text said necrotic: Occultist `multiclassing.requirements`, `Spectral Weapon`, `Spirit Lantern`, `Spectral Brand`, `Soulfire`, Rite of Omens `Cast the Lots` and `Shadow Withers`, Rite of Servitude `Spirit Conduit`, Sorcerer `Harrowing Tide`, and Barbarian `Spirit Vessel`. The correction changed only the canonical package and preserved source-authored psychic mechanics such as `Haunting Presence`, `Wail of the Banshee`, `Death Knell`, `Mourning Glimpse`, and `Egregore`.

Check high-risk Plutonium conversion fields directly: `additionalSpells` for racial and fixed spell grants, string tool proficiencies for classes, `classFeatures` and `subclassFeatures` references, subclass header `refSubclassFeature` wiring, absence of source-authored `ItemGrant` rows, absence of source feature-grant `foundryAdvancement` rows, item `wondrous: true`, item charge/recharge fields, and `_generated/index-sources.json` mapping one `VeiledOmens` source to the canonical collection file.

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

Audit `_generated/index-sources.json` and `_generated/index-props.json` after regeneration. On 2026-07-01, `index-sources.json` mapped `VeiledOmens` to `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`, `index-props.json` mapped all represented content props to `collection`, and a stale-reference scan for removed source IDs or type-specific package paths returned no matches.

Run the real Foundry import harness after verifying paths are live:

```sh
test -d /home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry
test -d /home/agent/tmp/veiled-omens-foundry-import-1782310453848/data
test -x /home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome

TMPDIR=/dev/shm \
FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry \
FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data \
CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node tools/validate-foundry-plutonium-import.mjs
```

Read `tmp/foundry-plutonium-import-result.json` after the harness. Report `status`, `sourceLoaded`, Foundry/dnd5e/Plutonium versions, package source, import plan, imported labels, failures, malformed advancement row counts, item advancement row counts, and import count. On 2026-07-01 the report status was `passed`, `sourceLoaded` was `true`, versions were Foundry `14.364.0`, dnd5e `5.3.3`, Plutonium `2.15.10`, package source was `VeiledOmens`, imported count was 21, failures were empty, and malformed advancement rows were empty.

Final report format: source paths inspected, Plutonium files changed, exact commands run with pass/fail results, FoundryVTT/Plutonium evidence, alignment discrepancies fixed, unresolved blockers, residual risk, and commit/push result. Do not claim Foundry verification from JSON validators, generated indexes, process exit, or summaries without the real report evidence.
