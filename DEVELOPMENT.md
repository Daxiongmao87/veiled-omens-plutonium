# Veiled Omens Plutonium Development Guide

This repository is the public raw-content source for Veiled Omens player-facing homebrew used by Plutonium/5etools in Foundry VTT.

Use this repository for JSON homebrew data, source images, and repeatable validation notes. Keep canonical lore and campaign-development prose in the main `venoure` repository; keep only Plutonium-ready data here.

## Plutonium configuration

Set Plutonium's Base Homebrew Repository URL to:

```text
https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/
```

Use `index.json` at the repository root to control which homebrew files Plutonium loads.

Example:

```json
{
  "toImport": [
    "races/ghost-elf.json"
  ]
}
```

## Source identity

Use this source block for Veiled Omens content unless a file has a specific reason to do otherwise:

```json
{
  "_meta": {
    "sources": [
      {
        "json": "VeiledOmens",
        "abbreviation": "VO",
        "full": "Veiled Omens Campaign Setting",
        "authors": ["Patrick Richardson"],
        "version": "0.1.0"
      }
    ]
  }
}
```

Rules:

- `json` is the stable machine source ID. Do not rename it casually.
- `abbreviation` is the compact label shown in lists.
- `full` is the human-readable campaign setting/source name.
- All entries in the file should use `"source": "VeiledOmens"` unless importing third-party material.

## Recommended repository layout

```text
/
├─ index.json
├─ DEVELOPMENT.md
├─ README.md
├─ races/
│  └─ ghost-elf.json
├─ subraces/
├─ classes/
├─ subclasses/
├─ feats/
├─ spells/
├─ items/
├─ backgrounds/
├─ optionalfeatures/
└─ img/
   └─ icons/
```

Git does not preserve empty directories, so add `.gitkeep` files when needed.

## Core references

Primary public references:

- Plutonium landing page: `https://5e.tools/plutonium.html`
- 5etools homebrew help: `https://wiki.tercept.net/en/5eTools/HelpPages/makebrew`
- 5etools homebrew table of reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference`
- Race reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference/Race`
- Class reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference/Class`
- Subclass reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference/Subclass`
- Lexicon / Foundry fields: `https://wiki.tercept.net/en/Homebrew/Lexicon`

Schema repositories and examples may move. When in doubt, inspect the live 5etools/Plutonium data cache and compare against an official race, class, feat, spell, or item that behaves the way the new content should behave.

## Race/species format

Races/species define traits directly in the race object's `entries` array. Do not use class-style feature references for species.

Minimal pattern:

```json
{
  "_meta": {
    "sources": [
      {
        "json": "VeiledOmens",
        "abbreviation": "VO",
        "full": "Veiled Omens Campaign Setting",
        "authors": ["Patrick Richardson"],
        "version": "0.1.0"
      }
    ]
  },
  "race": [
    {
      "name": "Example Species",
      "source": "VeiledOmens",
      "size": ["M"],
      "speed": 30,
      "ability": [{"dex": 2, "wis": 1}],
      "darkvision": 60,
      "languageProficiencies": [{"common": true}],
      "skillProficiencies": [{"perception": true}],
      "creatureTypes": ["humanoid"],
      "foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/icons/example.png",
      "entries": [
        {
          "name": "Darkvision",
          "type": "entries",
          "entries": [
            "You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light. You can't discern color in darkness, only shades of gray."
          ]
        },
        {
          "name": "Example Trait",
          "type": "entries",
          "entries": [
            "Trait text goes here."
          ]
        }
      ],
      "__prop": "race"
    }
  ]
}
```

Notes:

- Plutonium may not convert every `entries` trait into a separate Foundry dnd5e Advancement row. Exact Foundry item preservation may require direct Foundry item JSON rather than 5etools race JSON.
- Use `foundryImg` for the imported item image.
- Prefer full raw GitHub image URLs while testing; relative paths can be tested after the base repository URL is confirmed.

## Subrace/subspecies format

Subspecies generally follow the race format but include parent identifiers:

```json
{
  "name": "Example Species (Subspecies)",
  "source": "VeiledOmens",
  "raceName": "Example Species",
  "raceSource": "VeiledOmens",
  "_baseName": "Example Species",
  "_baseSource": "VeiledOmens",
  "_subraceName": "Subspecies",
  "_isSubRace": true,
  "size": ["M"],
  "speed": 30,
  "ability": [{"dex": 2, "cha": 1}],
  "entries": []
}
```

## Class format

Classes use explicit feature references. The class object has a `classFeatures` array. Each referenced feature must exist in the top-level `classFeature` array.

Feature string format:

```text
Feature Name|Class Name|Class Source|Level
```

Example:

```json
{
  "class": [
    {
      "name": "Example Class",
      "source": "VeiledOmens",
      "hd": {"number": 1, "faces": 8},
      "proficiency": ["wis", "cha"],
      "startingProficiencies": {
        "armor": ["light"],
        "weapons": ["simple"],
        "skills": [
          {
            "choose": {
              "from": ["arcana", "history", "insight", "religion"],
              "count": 2
            }
          }
        ]
      },
      "classFeatures": [
        "First Feature|Example Class|VeiledOmens|1"
      ],
      "subclassTitle": "Example Path",
      "__prop": "class"
    }
  ],
  "classFeature": [
    {
      "name": "First Feature",
      "source": "VeiledOmens",
      "className": "Example Class",
      "classSource": "VeiledOmens",
      "level": 1,
      "entries": ["Feature text goes here."]
    }
  ]
}
```

Subclass choice features use an object in `classFeatures`:

```json
{
  "classFeature": "Example Path|Example Class|VeiledOmens|3",
  "gainSubclassFeature": true
}
```

## Subclass format

Subclass feature reference format:

```text
Feature Name|Class Name|Class Source|Subclass Short Name|Subclass Source|Level|Feature Source
```

Example:

```json
{
  "subclass": [
    {
      "name": "Path of Omens",
      "shortName": "Omens",
      "source": "VeiledOmens",
      "className": "Example Class",
      "classSource": "VeiledOmens",
      "subclassFeatures": [
        "Omen Reading|Example Class|VeiledOmens|Omens|VeiledOmens|3|VeiledOmens"
      ]
    }
  ],
  "subclassFeature": [
    {
      "name": "Omen Reading",
      "source": "VeiledOmens",
      "className": "Example Class",
      "classSource": "VeiledOmens",
      "subclassShortName": "Omens",
      "subclassSource": "VeiledOmens",
      "level": 3,
      "entries": ["Subclass feature text goes here."]
    }
  ]
}
```

## Images

Recommended image policy:

- Put icons under `img/icons/`.
- Use lowercase hyphenated or snake_case names.
- Reference images with full raw URLs until Plutonium import is confirmed.
- Keep image dimensions reasonable for Foundry item icons, typically square PNG or WebP.

Example:

```json
"foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/icons/ghost_elf.png"
```

## Validation checklist

Before committing content:

1. Confirm the JSON parses with `jq` or an equivalent validator.
2. Confirm `_meta.sources[].json` matches every entry's `source` field.
3. Confirm feature reference strings exactly match the target feature names, class names, source IDs, subclass short names, and levels.
4. Confirm `index.json` lists the new file.
5. Import into a disposable Foundry world first.
6. Confirm Plutonium shows the content under the expected importer.
7. Confirm item image resolution works.
8. Confirm rules text appears in the Description tab.
9. Confirm mechanical choices apply correctly to a test actor.
10. For races/species, confirm whether Plutonium generated the desired Advancement rows; if not, decide whether direct Foundry item JSON is required.

## Git workflow

Use small commits by content type.

Suggested commit messages:

```text
Add ghost elf species
Add occultist class shell
Fix Veiled Omens source metadata
Add item icons
```

## Plutonium troubleshooting

If content does not appear:

- Check that `index.json` is valid JSON.
- Check that `index.json` paths are relative to the repository root.
- Check the Base Homebrew Repository URL ends with `/main/`.
- Try loading the exact raw JSON URL in a browser.
- Clear/reload Plutonium homebrew data.
- Restart Foundry after changing source metadata.
- Search by source abbreviation and by item name.

If icons do not appear:

- Open the raw image URL in a browser.
- Confirm `foundryImg` points to the image, not to a GitHub HTML page.
- Prefer `raw.githubusercontent.com`, not `github.com/.../blob/...`.

If race/species traits appear in Description but not Advancement:

- This is likely a Plutonium-to-dnd5e-system import behavior, not a malformed 5etools race entry.
- Use direct Foundry item JSON if exact Advancement tab preservation is required.
