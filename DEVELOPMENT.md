# Veiled Omens Plutonium Development Guide

This repository is the public raw-content source for Veiled Omens player-facing homebrew used by Plutonium/5etools in Foundry VTT.

Use this repository for JSON homebrew data, source images, and repeatable validation notes. Keep canonical lore and campaign-development prose in the main `venoure` repository; keep only Plutonium-ready data here.

## Plutonium configuration

Set Plutonium's Base Homebrew Repository URL to:

```text
https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/
```

This repository is an indexed Plutonium datasource and must publish these generated files at the root `_generated/` directory:

```text
_generated/index-sources.json
_generated/index-props.json
_generated/index-meta.json
_generated/index-timestamps.json
```

In Plutonium config/data sources, the **Base Homebrew Repository URL** must be the raw repository root shown above.

`URL Sources` and `Additional Homebrew Files` fields are direct JSON file inputs.
Do not point these fields at the repository root URL. A raw repo root fetch returns HTTP 400.

Direct-file examples:

```text
https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/collection/Patrick%20Richardson%3B%20Veiled%20Omens%20Campaign%20Setting.json
```

## Contributor workflow for changes

After changing file paths, content type paths, source metadata, or file names:

```bash
python3 tools/generate-plutonium-indexes.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
```

Then parse each JSON file to confirm it remains valid.

Conventions validation step before merge:

- Compare package filenames and source IDs against corresponding TheGiddyLimit/homebrew example files in the same directory. Use `collection/` examples when a source material package spans multiple content types.
- Do not treat index/json checks as sufficient if naming and source identity do not match package-level conventions.

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
        "version": "1.0.0-foundry-mechanics"
      }
    ]
  }
}
```

Rules:

- `json` is the stable machine source ID. Do not rename it casually.
- `abbreviation` is the compact label shown in lists.
- `full` is the human-readable campaign setting/source name.
- All entries in the file use `"source": "VeiledOmens"` unless importing third-party material.

### File naming and metadata class rule

Content file names describe source material/package identity inside the directory that matches the package shape.

- Current canonical source package: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Use `collection/` when one source material package spans multiple content types.
- Use a type-specific directory when the source package is a single-type package or a true type-specific collection.
- Author and account attribution belongs in `_meta.sources[].authors` and adventure/book `author` fields.
- Follow the upstream author-name filename segment for package files when the package convention requires it.

Source IDs follow the package/homebrew identity, not the content bucket or individual mechanical option.

- Current canonical source ID: `VeiledOmens`
- Current Veiled Omens player-facing content remains one collection source unless a future source material is a separate publication/package.
- Do not create split source IDs for individual classes, subclasses, species, spells, items, or features inside the same source material.

## Recommended repository layout

```text
/
  +--- DEVELOPMENT.md
  +--- README.md
  +--- tools/
  |    +--- generate-plutonium-indexes.py
  |    +--- validate-plutonium-datasource.py
  +--- _generated/
  |    +--- index-meta.json
  |    +--- index-props.json
  |    +--- index-sources.json
  |    +--- index-timestamps.json
  +--- collection/
  |    +--- Patrick Richardson; Veiled Omens Campaign Setting.json
  +--- img/
       +--- VeiledOmens/
            +--- icons/
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

## Homebrew conventions reference

Use this repository's conventions document for a full crosswalk to TheGiddyLimit/homebrew and Plutonium ingest behavior:

- [5etools homebrew conventions](./docs/5etools-homebrew-conventions.md)

That document covers:

- The adopted and adapted 5etools/homebrew conventions for this repository.
- content-type directory to top-level `__prop` / array mapping.
- `_generated` index file semantics.
- foundry asset transplant workflow (world-relative paths to repo-hosted `img/` files).

Schema repositories and examples may move. When in doubt, inspect the live 5etools/Plutonium data cache and compare against an official race, class, feat, spell, or item that behaves the way the new content is expected to behave.

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
        "version": "1.0.0-foundry-mechanics"
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
      "foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/VeiledOmens/icons/example.png",
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

- Put icons under the package asset directory, currently `img/VeiledOmens/icons/`.
- Use lowercase hyphenated or snake_case names.
- Reference images with full raw URLs until Plutonium import is confirmed.
- Keep image dimensions reasonable for Foundry item icons, typically square PNG or WebP.

Example:

```text
"foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/VeiledOmens/icons/ghost_elf.png"
```

## Validation checklist

Before committing content:

1. Confirm the JSON parses with `jq` or an equivalent validator.
2. Confirm `_meta.sources[].json` matches every entry's `source` field.
3. Confirm feature reference strings exactly match the names and source IDs of their target records.
4. Confirm `_generated/index-sources.json` includes the content file path for each source.
5. Confirm `_generated/index-props.json` includes top-level arrays for every content property in each file.
6. Confirm each generated path resolves to a file in the repository.
7. Import into a disposable Foundry world before relying on it in campaign play.
8. Confirm Plutonium shows the content under the expected importer.
9. Confirm item image resolution works.
10. Confirm rules text appears in the Description tab.
11. Confirm mechanical choices apply correctly to a test actor.
12. Confirm `python3 tools/validate-plutonium-datasource.py` passes before release.
13. Confirm generated indexes were produced with `python3 tools/generate-plutonium-indexes.py --check`.

## Plutonium troubleshooting

If content does not appear:

- Confirm `_generated/index-sources.json` exists.
- Confirm `_generated/index-props.json` exists.
- Confirm `_generated/index-meta.json` exists.
- Confirm `_generated/index-timestamps.json` exists.
- Confirm the target files are present and paths are relative to the repository root.
- Check that the Base Homebrew Repository URL ends with `/main/`.
- For local testing, check that `index.json` import mode works if you are explicitly using local `index.json` file import.
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
