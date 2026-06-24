# Veiled Omens Plutonium Instructions

## Source-Package Convention

- Follow TheGiddyLimit/homebrew package/source conventions.
- Before changing or troubleshooting a content convention, inspect corresponding TheGiddyLimit/homebrew examples and record the reference files or search result that governs the change.
- Source IDs model source material/package identity, not individual classes, subclasses, species, spells, items, or features.
- Current canonical package file: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Current canonical source ID: `VeiledOmens`
- Current canonical source author: `Patrick Richardson`
- Current Veiled Omens player-facing material is one mixed collection package/source unless a future source material is a separate publication/package.
- Do not split the current Veiled Omens package into source IDs for individual mechanical options.
- Use `collection/` when one source material package spans multiple content types.
- Use type-specific directories when the source package is a single-type package or a true type-specific collection.

## Required Validation

Before reporting content or source organization work complete:

1. Regenerate indexes with `python3 tools/generate-plutonium-indexes.py`.
2. Run `python3 tools/validate-content-json.py`; this parses every repository JSON file and checks every JSON file under recognized content directories.
3. Run `python3 tools/generate-plutonium-indexes.py --check`.
4. Run `python3 tools/validate-plutonium-datasource.py`.
5. Run `python3 tools/validate-plutonium-links.py`.
6. Run `python3 tools/validate-foundry-advancements.py`.
7. Audit `_generated/index-sources.json` for one source ID per source package.
8. Audit `_generated/index-props.json` for correct content-directory mappings.
9. Run stale-reference scans for removed source IDs and removed package paths.

The tracked pre-commit hook at `.githooks/pre-commit` enforces steps 2-6 before commits. Configure local clones with `git config core.hooksPath .githooks`.

## Foundry Character-Option Advancement Rule

- Character option completion requires Foundry dnd5e advancement coverage, not only valid 5etools JSON, Plutonium source indexes, or linked-entity resolution.
- Races/species must retain advancement-producing 5etools fields such as ability, size, language, skill, and tool proficiency fields.
- Drow-style racial spellcasting traits must be encoded in `additionalSpells`; do not model spell availability at later character levels as separate race feature `ItemGrant` rows unless the source has separate named feature entries at those levels.
- Classes must retain advancement-producing 5etools fields such as `hd`, `proficiency`, and `startingProficiencies`.
- Classes and subclasses must retain `classFeatures` and `subclassFeatures` references that resolve to real feature records; Plutonium's actor import path creates feature `ItemGrant` links from those references.
- Do not add source-authored `ItemGrant` placeholders. A source-authored `ItemGrant` row is valid only when `configuration.items` contains real item UUID entries, `value.added` maps the granted item IDs to the same UUIDs, and the Foundry path is verified.
- For standalone class, subclass, race, species, subrace, feat, optional feature, or item-grant surfaces whose Advancement tab is expected to grant named features, source data must create or retain concrete feature/item records and wire non-empty `ItemGrant` rows unless direct Foundry output proves Plutonium generated those rows. Removing empty rows is not a fix by itself.
- Relative UUID grants require stable child feature/item IDs. Missing child feature targets, missing child IDs, or blank `configuration.items` are blockers.
- Plutonium item conversion fields are part of player-option completion. Follow TheGiddyLimit/homebrew item conventions for fields such as `type`, `wondrous`, attunement, rarity, and charges. Wondrous magic items use `wondrous: true` and omit fake item type values such as `type: "WONDROUS"`.
- TheGiddyLimit/homebrew `foundryAdvancement` examples use concrete non-item advancement data such as `ScaleValue`; they are not evidence for empty `ItemGrant` rows.
- `tools/validate-foundry-advancements.py` is the commit-blocking invariant for this rule and must be updated when a new character-option content type is added.

## Assets

- Current package assets live under `img/VeiledOmens/icons/`.
- Active JSON must reference package assets through raw GitHub URLs that include `/img/VeiledOmens/icons/`.
