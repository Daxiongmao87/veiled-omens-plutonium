# 5etools Homebrew Conventions (Plutonium)

This document records the upstream 5etools homebrew conventions this repository follows and the local rules needed for Plutonium imports.

## Reference Sources

- TheGiddyLimit/homebrew repository: `https://github.com/TheGiddyLimit/homebrew`
- TheGiddyLimit/homebrew README and conventions: `https://raw.githubusercontent.com/TheGiddyLimit/homebrew/master/README.md`
- TheGiddyLimit/homebrew root tree: `https://github.com/TheGiddyLimit/homebrew/tree/master`
- TheGiddyLimit/homebrew `_generated/index-props.json`: `https://raw.githubusercontent.com/TheGiddyLimit/homebrew/master/_generated/index-props.json`
- Upstream mixed collection example: `collection/Matthew Mercer; TalDorei Campaign Guide.json`
- TheGiddyLimit/homebrew image repository: `https://github.com/TheGiddyLimit/homebrew-img`
- Upstream schemas: `https://github.com/TheGiddyLimit/5etools-utils/tree/master/schema/brew`
- 5etools homebrew helpers: `https://wiki.tercept.net/en/5eTools/HelpPages/makebrew`

## Adopted Upstream Rules

- Homebrew JSON files are compatible with 5etools and are loaded through the 5etools Brew Manager or by direct raw JSON.
- Repository content is organized by top-level package/content directories such as `collection`, `race`, `class`, `subclass`, `feat`, `optionalfeature`, `spell`, `item`, and `background`.
- `collection/` is used when one source material package spans multiple content types.
- Type-specific directories are used when the source package is a single-type package or a true type-specific collection.
- Filenames identify the source material/package. Upstream contribution filenames use `Author Name; Homebrew Name.json`.
- `_meta.sources[].json` values are unique source IDs across homebrew.
- Source IDs model source material/package identity, not individual mechanical options.
- Content authors belong in source `author` / `authors` fields; conversion credit belongs in `convertedBy`.
- File metadata includes `dateAdded` as a Unix timestamp in seconds.

## Local Rules For This Repository

- Current canonical source package: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Current canonical source ID: `VeiledOmens`
- Current canonical source author: `Patrick Richardson`
- Current package images live under `img/VeiledOmens/icons/` and are referenced through raw GitHub URLs.
- Current Veiled Omens player-facing content remains one collection package/source unless a future source material is a separate publication/package.
- Individual classes, subclasses, species, spells, items, and features inside the current package must not receive separate source IDs.
- Plutonium URL Source fields need raw JSON files. Do not use GitHub HTML pages or raw GitHub directory roots as URL Sources.
- Plutonium Base Homebrew Repository URL uses a branch root in the form `https://raw.githubusercontent.com/<user>/<repo>/<branch>/`.

## Foundry Advancement Source Data

- Plutonium's bundled 5etools source data uses race entries, class feature records, subclass feature records, and references as the source-data shape for feature grants.
- Normal class and subclass feature references use 5etools string refs. Class feature objects are reserved for reference metadata such as `gainSubclassFeature`, `gainSubclassFeatureHasContent`, or `tableDisplayName`.
- Plutonium class data and TheGiddyLimit homebrew class examples put a subclass-named header `subclassFeature` first in each subclass's `subclassFeatures` list. Plutonium imports that first feature into the subclass item and marks it ignored as a separate feature item at the actor import level.
- Real mechanical subclass features gained at the same level as the subclass choice are referenced from the header feature's `entries` as `refSubclassFeature` entries. Later-level mechanical subclass features are listed as sibling `subclassFeatures` after the header.
- Class tool-proficiency grants use strings, including free-choice strings like `one type of {@item artisan's tools|PHB} of your choice`; class tool arrays do not use object `choose` blocks.
- Bundled Plutonium side-data uses `advancement` rows for non-item values such as `ScaleValue`; it does not source-author `ItemGrant` rows for class, subclass, or race feature grants.
- Do not add source-authored `ItemGrant` rows for feature grants. Verify those grants through the real Plutonium actor import path, where the importer creates actor-owned `ItemGrant` rows from the concrete feature records.
- Class/subclass spellcasting progression arrays require a caster-table path in either `casterProgression` or `cantripProgression`.
  - `casterProgression` is for real spell-slot/pact/artificer table classes.
  - `cantripProgression` is valid for cantrip-table and slotless mana designs, including with `spellsKnownProgression`.
  - `reference/plutonium/js/Bundle.js` `UtilEntityClassSubclass.isClassSubclassHasCasterTable` accepts either `casterProgression` or `cantripProgression`.
  - Progression arrays without either field do not create a caster table in the Plutonium importer.
  - `reference/TheGiddyLimit-homebrew/class/LaserLlama; Vessel.json` uses `cantripProgression` and `spellsKnownProgression` with `additionalSpells` and no fake `casterProgression`.
- Fixed named spell grants in spellcasting text must still use `additionalSpells`.
- Do not add fake `casterProgression` for Thaumaphage-style mana classes or other cantrip-table designs.
- Fixed named spell grants in spellcasting text must be represented via `additionalSpells`:
  - Character level grants in `additionalSpells` use `known` keys like `"1"` or `"2"`; numeric keys are character levels, not spell levels. For example, 1st-level cantrips go under `known["1"]`, not `known["0"]`.
  - Cantrips are denoted as source-qualified spell UIDs with `#c`, such as `Convert Essence|VeiledOmens#c`.
  - Custom-source fixed spell grants use source-qualified spell UIDs in `additionalSpells`, such as `Convert Essence|VeiledOmens#c` for a cantrip and `Ether Burn|VeiledOmens` for a leveled spell.
  - Source examples with this convention include `reference/TheGiddyLimit-homebrew/class/LaserLlama; Psion.json` and `reference/TheGiddyLimit-homebrew/class/LaserLlama; Shaman.json`.
  - Source-authored `ItemGrant` rows are not used for spell grants in this surface.
- Custom class spell lists use `classSpells` arrays on class objects.
  - Upstream examples include `reference/TheGiddyLimit-homebrew/class/KibblesTasty; Occultist.json` and `reference/TheGiddyLimit-homebrew/class/LaserLlama; Alternate Paladin.json`.
  - Local homebrew entries in `classSpells` are source-qualified with `|VeiledOmens` and must resolve against local `spell` entities.
  - Official or non-`VeiledOmens` `classSpells` UIDs are not treated as local-missing in link validation.
- If a class references a class feature with the same name and source as a top-level item record, class grants must include that item in `startingEquipment.defaultData`.

## Item Prose-To-Mechanics Source Data

- Item prose that grants, casts, contains, uses, or expends named `{@spell ...}` tags must have matching source-side `attachedSpells` data. TheGiddyLimit/homebrew and bundled Plutonium item data use `attachedSpells` as either a list or a frequency bucket object.
- Item charge prose must be backed by source-side charge fields. Prose that says an item has charges, maximum charges, regains charges, recharges at dawn, or recharges on rest requires `charges` plus `recharge` and/or `rechargeAmount`.
- Long-rest recharge uses the 5etools/Plutonium token `recharge: "restLong"`, not prose text such as `recharge: "long rest"`.
- Full-restore prose such as "regains all charges", "regains all expended charges", "regaining all spent uses", or "all charges are restored" is valid with `recharge: "restLong"` and no `rechargeAmount`, or with numeric `charges` and matching numeric `rechargeAmount`.
- Nonnumeric dice `rechargeAmount` values such as `{@dice 1d4}` represent partial or random recharge and must not be paired with prose that says all charges or uses are restored.
- Static item bonuses in prose require their structured item fields: `bonusWeapon` for attack/damage roll bonuses, `bonusAc` for AC bonuses, `bonusSpellAttack` for spell attack bonuses, and `bonusSpellSaveDc` for spell save DC bonuses.
- Persistent worn, wielded, held, carried, or attuned damage defenses in prose require structured defense fields: `resist`, `immune`, and `conditionImmune`.
- Wondrous magic items use `wondrous: true`; do not add fake item type values such as `type: "WONDROUS"` or `type: "wondrous item"`.
- Material/equipment families that should generate player-facing base-item variants use top-level `magicvariant` entries (for example `reference/plutonium/data/magicvariants.json` entries `Adamantine Weapon`, `Silvered Weapon`, and `Adamantine Armor`).
- Do not use top-level `variantrule` as a substitute for material/equipment families when they should appear in the item browser.
- Use concrete item records for categories that are not cleanly generated by base-item family variants and need visible named-category boundaries, including rings (`type: "RG|DMG"` in `reference/plutonium/data/items.json`) and wondrous items (`wondrous: true` in `reference/plutonium/data/items.json`).
- For magicvariant base families, preserve the Plutonium convention of inheritance (`type`, `requires`, `inherits.namePrefix`/`nameSuffix`, `inherits.source`, `inherits.entries`) and include item-level entries only where structure is insufficient.

Reference audit evidence from the 2026-06-24 TheGiddyLimit/homebrew clone:

- 1,294 JSON files parsed with zero JSON errors.
- `classFeatures`: 6,526 string refs and 1,527 object refs; object refs carried metadata such as `gainSubclassFeature` or `tableDisplayName`.
- `subclassFeatures`: 20,585 string refs, zero object refs.
- Official Plutonium examples inspected: `reference/plutonium/data/class/class-fighter.json`, `reference/plutonium/data/class/class-sorcerer.json`, `reference/plutonium/data/class/class-barbarian.json`, and `reference/plutonium/data/class/class-cleric.json`; each sample subclass starts with a subclass-named header feature such as `Battle Master|Fighter||Battle Master||3`.
- Homebrew examples inspected: `reference/TheGiddyLimit-homebrew/class/KibblesTasty; Occultist.json`, `reference/TheGiddyLimit-homebrew/class/LaserLlama; Shaman.json`, and `reference/TheGiddyLimit-homebrew/class/Middle Finger of Vecna; Witch.json`; each sample subclass starts with a subclass-named header feature such as `Tradition of the Hedge Mage|Occultist|KT:O|Hedge Mage|KT:O|1`.
- Plutonium importer evidence inspected: `reference/plutonium/js/Bundle.js` `_tagFirstSubclassLoaded`, which marks the first subclass feature ignored because it expects a header.
- Class `startingProficiencies.tools` and `multiclassing.proficienciesGained.tools`: 278 string entries, zero object entries.
- `foundryAdvancement`: 194 rows, all `ScaleValue`; zero source-authored `ItemGrant` rows.
- Items: 6,884 `wondrous: true` entries and zero `type: "WONDROUS"` entries.
- Item spell attachments are represented through `attachedSpells` in both TheGiddyLimit/homebrew item JSON and `reference/plutonium/data/items.json`; inspected examples include `reference/TheGiddyLimit-homebrew/item/DMsGuild Community; Artifacts of the Guild.json`, `reference/TheGiddyLimit-homebrew/item/CaelReader; All the Weapons.json`, and bundled Plutonium items.
- Long-rest charge examples use `recharge: "restLong"`:
  - `reference/TheGiddyLimit-homebrew/item/DMsGuild Community; Artifacts of the Guild.json` `Charred Cloak` has `wondrous: true`, `recharge: "restLong"`, `charges: 3`, and prose that it is "regaining all spent uses" at the end of a long rest, with no `rechargeAmount`.
  - `reference/TheGiddyLimit-homebrew/item/hakr14; Weave of Karo - Items.json` `Elemental Salve` has `wondrous: true`, `recharge: "restLong"`, `charges: 5`, and dice recharge prose for partial charge recovery.
- Structured item bonus and defense fields appear in TheGiddyLimit/homebrew item examples, including `bonusWeapon`, `bonusAc`, `bonusSpellAttack`, `resist`, `immune`, and `conditionImmune` in `reference/TheGiddyLimit-homebrew/item/CaelReader; All the Weapons.json` and other item files.

## Directory To Top-Level Property Mapping

- `collection/` -> mixed top-level arrays from one source package
- `race/` -> `race`
- `subrace/` -> `subrace`
- `class/` -> `class`
- `subclass/` -> `subclass`
- `feat/` -> `feat`
- `optionalfeature/` -> `optionalfeature`
- `spell/` -> `spell`
- `item/` -> `item`
- `baseitem/` -> `baseitem`
- `magicvariant/` -> `magicvariant`
- `background/` -> `background`
- `adventure/` -> `adventure`
- `book/` -> `book`
- `monster/` -> `monster`
- Other object-specific directories map to matching top-level array keys in the same pattern, including `action`, `reward`, `vehicle`, `object`, `deity`, `language`, `trap`, `hazard`, `cult`, `boon`, `condition`, `disease`, `variantrule`, `table`, and `psionic`.

## Source Inventory Gate

Before accepting any source organization change:

1. Inspect the source material scope.
2. Classify whether the content is one mixed package, one single-type package, a true type-specific collection, or a separate publication/package.
3. Map each `_meta.sources[].json` value to exactly one package file.
4. Confirm source IDs are not split by individual mechanical options inside the same source material.
5. Regenerate indexes.
6. Run `python3 tools/validate-content-json.py` to parse every repository JSON file and check every content JSON file.
7. Run the datasource validator.
8. Run the Plutonium link validator.
9. Run stale-reference scans for removed source IDs and removed file paths.

## Commit-Time Validation

The tracked hook at `.githooks/pre-commit` enforces the non-mutating validation suite before every commit:

```bash
git config core.hooksPath .githooks
```

The hook runs:

```bash
python3 tools/validate-content-json.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
python3 tools/validate-plutonium-links.py
python3 tools/validate-prose-mechanics.py
python3 tools/validate-foundry-advancements.py
```

`tools/validate-content-json.py` uses the shared content discovery helper in `tools/plutonium_content.py`, so generator and validator tooling use the same definition of content JSON files.

## `_generated` Index Workflow

`_generated/` files are expected to be present for a valid Plutonium datasource:

- `_generated/index-sources.json`
- `_generated/index-props.json`
- `_generated/index-meta.json`
- `_generated/index-timestamps.json`

`python3 tools/generate-plutonium-indexes.py` regenerates these files.

`python3 tools/generate-plutonium-indexes.py --check` verifies index consistency.

`python3 tools/validate-content-json.py` parses every repository JSON file and checks every repository content JSON file.

`python3 tools/validate-plutonium-datasource.py` validates the generated datasource maps against repository content.

`python3 tools/validate-plutonium-links.py` validates Plutonium linked-entity references such as class feature, subclass feature, spell, and item references.

## Asset Transplant Workflow

Use the workflow below for any Foundry-path image references that originate from a local world directory:

1. Locate the Foundry-relative path in source objects, such as `worlds/the-star-of-wintercrest/assets/images/Vaetyr_3.png`.
2. Download from the Foundry base URL: `https://foundry.instance3.astralkeep.com/worlds/the-star-of-wintercrest/assets/images/<image>.png`.
3. Save each image into the package asset directory, currently `img/VeiledOmens/icons/`.
4. Reference the image from repo JSON via raw GitHub URL, for example `https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/VeiledOmens/icons/vaetyr.png`.
5. For Foundry paths that are global module/system references, such as `modules/plutonium/...` or `icons/...`, keep external references when the dependency is intentionally external and valid at runtime.
6. Do not create packed-name aliases unless the source JSON contains that path and the server serves it.

## Distinction: World Paths Vs External Paths

- Custom world paths must be fetched and transplanted into the repo when used in this datasource.
- Core/module paths remain external when the dependency is stable runtime content.
