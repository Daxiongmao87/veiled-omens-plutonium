---
name: veiled-omens-plutonium-daily-alignment
description: Align the Veiled Omens Plutonium package to current player-options source material and verify it through repo validators plus the real Foundry/Plutonium import harness.
---

Work from `/home/agent/projects/veiled-omens-plutonium`. Treat `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, `docs/5etools-homebrew-conventions.md`, repo validators, and `collection/Patrick Richardson; Veiled Omens Campaign Setting.json` as governing requirements. Inspect the player-options source through the symlink `veiled-omens-player-options-source -> /home/agent/projects/venoure/Veiled_Omens/Player_Options`; the symlink target and `reference/` are read-only.

Start by discovering source files live from the symlink root. On 2026-07-01, `find -L veiled-omens-player-options-source -maxdepth 5 -type f | sort` found rules-bearing files under `Classes/`, `Races/`, `Species/Elves/`, and `Items/`, plus metadata YAML under `Races/_race_metadata/`. No inspected file documented a narrower player-options discovery root.

Inventory the canonical package through parsed JSON before comparing source text. After the 2026-07-01 fix, the package contained 12 races/species, 2 classes, 30 class features, 7 subclasses, 39 subclass features, 23 spells, 1 item, and 6 `variantrule` equipment-rule entries. Compare represented mechanics against source for names, prerequisites, level gates, granted features, spell lists, uses, recovery, DCs, damage, scaling, charges, attunement, rarity, item type, activities, proficiencies, languages, size, movement, senses, and rules-affecting text.

Treat `Items/README.md` as a player-facing mechanics index. On 2026-07-01 it listed six active equipment-rule files: `Items/shadesilver_weapons.md`, `Items/shadesilver_armor.md`, `Items/arcavene_weapons.md`, `Items/arcavene_armor.md`, `Items/arcavene_rings.md`, and `Items/arcavene_wondrous_items.md`. Those files describe base material and equipment-category rules, not named magic items. Reference evidence from `schemas/plutonium-content-types.md`, `reference/plutonium/data/variantrules.json`, and TheGiddyLimit homebrew `variantrule` examples governed the representation: add broad equipment/material rules as top-level `variantrule` entries with `ruleType: "rule"` and `__prop: "variantrule"`, then regenerate `_generated/index-props.json`.

Use the executor wrapper for package, validator, code, or documentation edits. The 2026-07-01 implementation added these six `variantrule` entries: Shadesilver Weapons, Shadesilver Armor, Arcavene Weapons, Arcavene Armor, Arcavene Rings, and Arcavene Wondrous Items. Do not edit `reference/` or the symlink target.

Classify source files with inspected text evidence. Current 2026-07-01 classifications: `Classes/druid_circle_of_the_veil.md`, `Classes/monk_way_of_the_mists.md`, and `Classes/paladin_oath_of_the_lantern.md` are draft stubs because they state mechanics are to be developed; `Classes/occultist_rite_of_haunts_invocation_draft.md` is a design draft because it states it is not canon text; `Classes/sorcerer_veil_touched.txt` and `Races/half_troll.txt` are legacy or defunct because each file says the current playable material lives under the replacement source; `Species/Elves/ghost_elf.md` is a setting-agnostic stub with mechanics moved to `Races/ghost_elf.md`; `Races/rimeheart_dwarves.md` is lore without a distinct mechanical racial writeup; race metadata YAML files are non-diegetic generation guidance except where they corroborate represented source.

OCR image-only PDFs when source authority conflicts with text files. The 2026-07-01 run used `pdfinfo`, `pdftotext`, `pdfimages`, `pdftoppm`, and `tesseract` on `Classes/Occultist/occultist-phb-v1.0-lite.pdf`. OCR proved the PDF is an Occultist v1.0 rules supplement dated May 4, 2026 and showed a Rite of Omens feature named `BONECASTING`, while `Classes/occultist_rite_of_omens.txt` and the package use `Cast the Lots`. Report that text/PDF conflict as residual risk until source authority resolves it. The full and compressed Occultist PDFs share page count/date/producer with the lite PDF but were not fully OCRed in that run.

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

The 2026-07-01 post-fix run passed all eight commands. Key output: index generation reported already up to date; content validation checked 1 content file and parsed 14 repository JSON files; prose mechanics scanned 1 content file; Foundry advancement validation passed; unittest discovery ran 5 tests with `OK`.

Verify live harness paths before Foundry import:

```sh
test -d /home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry
test -d /home/agent/tmp/veiled-omens-foundry-import-1782310453848/data
test -x /home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome
```

Then run the real harness with actual FoundryVTT, dnd5e, Plutonium, lib-wrapper, and Chromium:

```sh
env TMPDIR=/dev/shm FOUNDRY_APP_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/foundry FOUNDRY_DATA_DIR=/home/agent/tmp/veiled-omens-foundry-import-1782310453848/data CHROMIUM_EXECUTABLE_PATH=/home/agent/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome node tools/validate-foundry-plutonium-import.mjs
```

Read `tmp/foundry-plutonium-import-result.json` after the harness. On 2026-07-01 the harness exited 0, wrote the report, and the report status was `passed`; `sourceLoaded` was `true`; `packageSource` was `VeiledOmens`; versions were Foundry `14.364.0`, dnd5e `5.3.3`, and Plutonium `2.15.10`; preflight output identified lib-wrapper `1.13.5.1`; imported count was 21 covering 12 races, 2 classes, and 7 subclasses; totals were 259 items, 137 item advancement rows, 43 advancement-origin links, and zero malformed advancement rows. The harness validates the actor-import path for races/classes/subclasses; `variantrule` equipment rules are covered by source audit, JSON validation, datasource validation, link/prose checks, and index mapping rather than actor import.

Final reports must include source paths inspected, represented mechanics checked, missing mechanics, evidence-backed exclusions, source files not fully inspected, Plutonium files changed, exact commands run with pass/fail results, Foundry evidence from the report, discrepancies fixed, unresolved blockers, residual risk, and commit/push result. Do not report "no discrepancies" until source-to-package coverage has zero missing current player-facing mechanics, or each missing source mechanic has an inspected exclusion classification.
