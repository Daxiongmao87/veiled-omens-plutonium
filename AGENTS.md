# Veiled Omens Plutonium Instructions

## Source-Package Convention

- Follow TheGiddyLimit/homebrew package/source conventions.
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
- Classes must retain advancement-producing 5etools fields such as `hd`, `proficiency`, and `startingProficiencies`.
- Subclasses with `subclassFeatures` must include `foundryAdvancement` `ItemGrant` rows for every subclass feature level.
- `tools/validate-foundry-advancements.py` is the commit-blocking invariant for this rule and must be updated when a new character-option content type is added.

## Assets

- Current package assets live under `img/VeiledOmens/icons/`.
- Active JSON must reference package assets through raw GitHub URLs that include `/img/VeiledOmens/icons/`.
