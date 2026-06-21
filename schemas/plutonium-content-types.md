# Plutonium Content Type Reference

This is a working authoring reference for Plutonium/5etools homebrew content used by Veiled Omens. It is based on the uploaded Foundry VTT journal export named `Plutonium Schemas`.

These notes are practical schema notes, not strict JSON Schema validator files. Always compare against a live official Plutonium/5etools entry of the same type before treating a shape as final.

## Shared source block

Use this `_meta` source block for Veiled Omens content:

```json
{
  "_meta": {
    "sources": [
      {
        "json": "VeiledOmens",
        "abbreviation": "VO",
        "full": "Veiled Omens Campaign Setting",
        "authors": ["Daxiongmao87"],
        "version": "0.1.0"
      }
    ]
  }
}
```

All Veiled Omens entries should normally use:

```json
"source": "VeiledOmens"
```

## Race / species

Top-level array: `race`

Entry discriminator:

```json
"__prop": "race"
```

Core fields:

```json
{
  "name": "string",
  "source": "VeiledOmens",
  "page": 0,
  "edition": "classic",
  "size": ["M"],
  "speed": 30,
  "ability": [{"dex": 2, "wis": 1}],
  "heightAndWeight": {
    "baseHeight": 56,
    "heightMod": "2d10",
    "baseWeight": 110,
    "weightMod": "2d4"
  },
  "age": {"mature": 20, "max": 180},
  "darkvision": 60,
  "resist": ["necrotic"],
  "immune": ["poison"],
  "vulnerable": ["fire"],
  "conditionImmune": ["poisoned"],
  "languageProficiencies": [{"common": true, "elvish": true}],
  "skillProficiencies": [{"perception": true}],
  "traitTags": ["Skill Proficiency", "Language Proficiency"],
  "creatureTypes": ["humanoid"],
  "foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/icons/example.png",
  "entries": [
    {
      "name": "Trait Name",
      "type": "entries",
      "entries": ["Trait rules text."]
    }
  ],
  "__prop": "race"
}
```

Race traits belong in the race object's `entries` array. Do not use class-style feature references for race traits.

## Race subspecies / subrace

Top-level array: usually `race` for the flattened Plutonium cache shape, or `subrace` when using canonical 5etools homebrew split files. Match the style used by the target importer.

Additional identifiers:

```json
{
  "_isSubRace": true,
  "_baseName": "Parent Race",
  "_baseSource": "VeiledOmens",
  "_subraceName": "Subrace Name",
  "raceName": "Parent Race",
  "raceSource": "VeiledOmens"
}
```

Subspecies otherwise use the same fields as races/species.

## Class

Top-level array: `class`

Entry discriminator:

```json
"__prop": "class"
```

Core fields:

```json
{
  "name": "Class Name",
  "source": "VeiledOmens",
  "page": 0,
  "edition": "classic",
  "hd": {"number": 1, "faces": 8},
  "proficiency": ["wis", "cha"],
  "spellcastingAbility": "wis",
  "casterProgression": "full",
  "preparedSpells": "<$level$> + <$wis_mod$>",
  "cantripProgression": [2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4],
  "startingProficiencies": {
    "armor": ["light"],
    "weapons": ["simple"],
    "tools": [],
    "skills": [
      {
        "choose": {
          "from": ["arcana", "history", "insight", "religion"],
          "count": 2
        }
      }
    ]
  },
  "startingEquipment": {
    "additionalFromBackground": true,
    "default": [],
    "goldAlternative": "{@dice 5d4 × 10|5d4 × 10|Starting Gold}",
    "defaultData": []
  },
  "multiclassing": {
    "requirements": {"wis": 13},
    "proficienciesGained": {
      "armor": ["light"],
      "weapons": ["simple"]
    }
  },
  "classTableGroups": [],
  "classFeatures": [
    "First Feature|Class Name|VeiledOmens|1"
  ],
  "subclassTitle": "Subclass Category",
  "hasFluff": true,
  "hasFluffImages": false,
  "__prop": "class"
}
```

Class feature reference format:

```text
Feature Name|Class Name|Class Source|Level
```

Subclass choice features use:

```json
{
  "classFeature": "Subclass Category|Class Name|VeiledOmens|3",
  "gainSubclassFeature": true
}
```

## Class feature

Top-level array: `classFeature`

Entry discriminator:

```json
"__prop": "classFeature"
```

Core fields:

```json
{
  "name": "Feature Name",
  "source": "VeiledOmens",
  "className": "Class Name",
  "classSource": "VeiledOmens",
  "level": 1,
  "entries": ["Feature rules text."],
  "__prop": "classFeature"
}
```

## Subclass

Top-level array: `subclass`

Entry discriminator:

```json
"__prop": "subclass"
```

Core fields:

```json
{
  "name": "Subclass Name",
  "shortName": "SubclassShortName",
  "source": "VeiledOmens",
  "className": "Class Name",
  "classSource": "VeiledOmens",
  "page": 0,
  "edition": "classic",
  "additionalSpells": [],
  "subclassFeatures": [
    "Subclass Feature|Class Name|VeiledOmens|SubclassShortName|VeiledOmens|3|VeiledOmens"
  ],
  "hasFluffImages": false,
  "__prop": "subclass"
}
```

Subclass feature reference format:

```text
Feature Name|Class Name|Class Source|Subclass Short Name|Subclass Source|Level|Feature Source
```

## Subclass feature

Top-level array: `subclassFeature`

Entry discriminator:

```json
"__prop": "subclassFeature"
```

Core fields:

```json
{
  "name": "Subclass Feature",
  "source": "VeiledOmens",
  "className": "Class Name",
  "classSource": "VeiledOmens",
  "subclassShortName": "SubclassShortName",
  "subclassSource": "VeiledOmens",
  "level": 3,
  "entries": ["Subclass feature rules text."],
  "__prop": "subclassFeature"
}
```

## Spell

Top-level array: `spell`

Entry discriminator:

```json
"__prop": "spell"
```

Core fields:

```json
{
  "name": "Spell Name",
  "source": "VeiledOmens",
  "page": 0,
  "level": 1,
  "school": "evocation",
  "time": "1 action",
  "range": "60 feet",
  "components": {
    "verbal": true,
    "somatic": true,
    "material": "a component"
  },
  "duration": "Concentration, up to 1 minute",
  "entries": [
    {
      "name": "",
      "type": "entries",
      "entries": ["Spell description."]
    }
  ],
  "entriesHigherLevel": [],
  "miscTags": [],
  "classes": ["wizard"],
  "feats": [],
  "rewards": [],
  "__prop": "spell"
}
```

## Item

Top-level array: `item`

Entry discriminator:

```json
"__prop": "item"
```

Core fields:

```json
{
  "name": "Item Name",
  "source": "VeiledOmens",
  "page": 0,
  "rarity": "uncommon",
  "reqAttune": true,
  "reqAttuneTags": [],
  "wondrous": true,
  "bonusSpellAttack": 1,
  "bonusSpellSaveDc": 1,
  "focus": true,
  "foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/icons/item.png",
  "entries": [
    {
      "name": "",
      "type": "entries",
      "entries": ["Item description."]
    }
  ],
  "__prop": "item"
}
```

## Feat

Top-level array: `feat`

Entry discriminator:

```json
"__prop": "feat"
```

Core fields:

```json
{
  "name": "Feat Name",
  "source": "VeiledOmens",
  "entries": [
    {
      "name": "",
      "type": "entries",
      "entries": ["Feat rules text."]
    }
  ],
  "activities": [],
  "migrationVersion": 3,
  "__prop": "feat"
}
```

## Optional feature

Top-level array: `optionalfeature`

Entry discriminator:

```json
"__prop": "optionalfeature"
```

Core fields:

```json
{
  "name": "Optional Feature Name",
  "source": "VeiledOmens",
  "entries": ["Feature text."],
  "effects": [],
  "migrationVersion": 3,
  "__prop": "optionalfeature"
}
```

## Background

Top-level array: `background`

Entry discriminator:

```json
"__prop": "background"
```

Core fields:

```json
{
  "name": "Background Name",
  "source": "VeiledOmens",
  "page": 0,
  "skills": ["ins", "rel"],
  "toolProficiencies": [],
  "languages": ["common", "one of your choice"],
  "equipment": [],
  "feature": "Feature Name",
  "featureDescription": ["Feature description."],
  "entries": [],
  "activities": [],
  "migrationVersion": 3,
  "__prop": "background"
}
```

## Monster / creature

Top-level array: `monster`

Entry discriminator:

```json
"__prop": "monster"
```

Core fields:

```json
{
  "name": "Creature Name",
  "source": "VeiledOmens",
  "size": "M",
  "type": "undead",
  "alignment": "neutral evil",
  "ac": 13,
  "hp": 45,
  "speed": 30,
  "str": 10,
  "dex": 14,
  "con": 12,
  "int": 8,
  "wis": 10,
  "cha": 10,
  "senses": "darkvision 60 ft.",
  "passive": 10,
  "resist": [],
  "immune": [],
  "conditionImmune": [],
  "languages": [],
  "cr": 2,
  "trait": [],
  "action": [],
  "traitTags": [],
  "actionTags": [],
  "languageTags": [],
  "damageTags": [],
  "miscTags": [],
  "hasToken": false,
  "hasFluff": false,
  "__prop": "monster"
}
```

## Reward

Top-level array: `reward`

Entry discriminator:

```json
"__prop": "reward"
```

Core fields:

```json
{
  "name": "Reward Name",
  "source": "VeiledOmens",
  "entries": [],
  "effects": [],
  "migrationVersion": 3,
  "__prop": "reward"
}
```

## Action

Top-level array: `action`

Entry discriminator:

```json
"__prop": "action"
```

Core fields:

```json
{
  "name": "Action Name",
  "source": "VeiledOmens",
  "activities": [],
  "migrationVersion": 3,
  "__prop": "action"
}
```

## Vehicle and vehicle upgrade

Vehicle top-level array: `vehicle`

Vehicle upgrade top-level array: `vehicleUpgrade`

Vehicle core fields:

```json
{
  "name": "Vehicle Name",
  "source": "VeiledOmens",
  "size": "L",
  "speed": 30,
  "ac": 15,
  "hp": 100,
  "hd": "10d10",
  "crew": 4,
  "passengers": 10,
  "cargo": 1,
  "entries": [],
  "traits": [],
  "actions": [],
  "__prop": "vehicle"
}
```

Vehicle upgrade core fields:

```json
{
  "name": "Upgrade Name",
  "source": "VeiledOmens",
  "effects": [],
  "migrationVersion": 3,
  "__prop": "vehicleUpgrade"
}
```

## Table

Top-level array: `table`

Entry discriminator:

```json
"__prop": "table"
```

Core fields:

```json
{
  "name": "Table Name",
  "source": "VeiledOmens",
  "page": 0,
  "chapter": "1",
  "caption": ["Table caption"],
  "colLabels": ["Roll", "Result"],
  "colStyles": {"widths": "20%,80%"},
  "rows": [["1", "Result text"]],
  "__prop": "table"
}
```

## Deck and card

Deck top-level array: `deck`

Card top-level array: `card`

Deck core fields:

```json
{
  "name": "Deck Name",
  "source": "VeiledOmens",
  "page": 0,
  "cards": 10,
  "back": ["Back text"],
  "entries": [],
  "hasCardArt": false,
  "__prop": "deck"
}
```

Card core fields:

```json
{
  "name": "Card Name",
  "source": "VeiledOmens",
  "set": "Deck Name",
  "page": 0,
  "face": ["Face text"],
  "entries": [],
  "__prop": "card"
}
```

## Variant rule

Top-level array: `variantrule`

Entry discriminator:

```json
"__prop": "variantrule"
```

Core fields:

```json
{
  "name": "Rule Name",
  "source": "VeiledOmens",
  "page": 0,
  "ruleType": "rule",
  "entries": [],
  "__prop": "variantrule"
}
```

## Adventure and book

Adventure top-level array: `adventure`

Book top-level array: `book`

Adventure core fields:

```json
{
  "name": "Adventure Name",
  "id": "VOADVENTURE",
  "source": "VeiledOmens",
  "group": "Veiled Omens",
  "cover": "",
  "published": "2026",
  "author": ["Daxiongmao87"],
  "storyline": "Veiled Omens",
  "level": "1-5",
  "contents": {"chapters": []},
  "__prop": "adventure"
}
```

Book core fields:

```json
{
  "name": "Book Name",
  "id": "VOBOOK",
  "source": "VeiledOmens",
  "group": "Veiled Omens",
  "cover": "",
  "published": "2026",
  "author": ["Daxiongmao87"],
  "contents": {"chapters": []},
  "__prop": "book"
}
```

## Condition, disease, and status

Top-level arrays: `condition`, `disease`, or `status`

Entry discriminator examples:

```json
"__prop": "condition"
```

Core fields:

```json
{
  "name": "Condition Name",
  "source": "VeiledOmens",
  "page": 0,
  "entries": [],
  "effects": [],
  "activities": [],
  "migrationVersion": 3,
  "__prop": "condition"
}
```

## Deity

Top-level array: `deity`

Entry discriminator:

```json
"__prop": "deity"
```

Core fields:

```json
{
  "name": "Deity Name",
  "source": "VeiledOmens",
  "page": 0,
  "alignment": "Neutral",
  "domain": ["Knowledge"],
  "entries": [],
  "hasFluff": true,
  "__prop": "deity"
}
```

## Language

Top-level array: `language`

Entry discriminator:

```json
"__prop": "language"
```

Core fields:

```json
{
  "name": "Language Name",
  "source": "VeiledOmens",
  "page": 0,
  "script": "Common",
  "type": "standard",
  "entries": [],
  "__prop": "language"
}
```

## Recipe

Top-level array: `recipe`

Entry discriminator:

```json
"__prop": "recipe"
```

Core fields:

```json
{
  "name": "Recipe Name",
  "source": "VeiledOmens",
  "page": 0,
  "entries": [],
  "ingredients": [],
  "craftingTime": "8 hours",
  "goldCost": 50,
  "dc": 10,
  "tool": "alchemist's supplies",
  "__prop": "recipe"
}
```

## Trap and hazard

Top-level arrays: `trap` or `hazard`

Entry discriminator examples:

```json
"__prop": "trap"
```

Core fields:

```json
{
  "name": "Trap Name",
  "source": "VeiledOmens",
  "page": 0,
  "size": "M",
  "dc": 13,
  "damage": "1d6",
  "entries": [],
  "activities": [],
  "__prop": "trap"
}
```

## Psionic

Top-level array: `psionic`

Entry discriminator:

```json
"__prop": "psionic"
```

Core fields:

```json
{
  "name": "Psionic Name",
  "source": "VeiledOmens",
  "page": 0,
  "psionicPower": "",
  "discipline": "psychic",
  "psiPoints": 1,
  "activities": [],
  "entries": [],
  "migrationVersion": 3,
  "__prop": "psionic"
}
```

## Cult, supernatural gift, object, and bastion/facility

Cult/supernatural gift top-level arrays: `cult` or `supernaturalGift`

Object top-level array: `object`

Bastion/facility top-level array: `bastion`

Cult core fields:

```json
{
  "name": "Cult Name",
  "source": "VeiledOmens",
  "page": 0,
  "entries": [],
  "activities": [],
  "migrationVersion": 3,
  "__prop": "cult"
}
```

Object core fields:

```json
{
  "name": "Object Name",
  "source": "VeiledOmens",
  "size": "M",
  "ac": 15,
  "hp": 20,
  "entries": [],
  "activities": [],
  "__prop": "object"
}
```

Bastion/facility core fields:

```json
{
  "name": "Facility Name",
  "source": "VeiledOmens",
  "entries": [],
  "effects": [],
  "__prop": "bastion"
}
```

## Practical validation checklist

Before committing a new content file:

1. Confirm the JSON parses.
2. Confirm the top-level array name matches the content type.
3. Confirm every entry has the expected `source`.
4. Confirm `__prop` matches the entry type.
5. Confirm feature-reference strings exactly match the names and source IDs of their target records.
6. Confirm `index.json` includes the file if Plutonium should auto-load it.
7. Import into a disposable Foundry world before relying on it in campaign play.
