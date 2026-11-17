# Gestalt — class draft

**For:** Patrick · **Date:** 2026-11-16 · **Revision:** 3 (cleaned up)
**Status:** Design complete for the 2014 PHB classes and the Veiled Omens homebrew (Occultist, Thaumaphage, Path of the Shaman, Pale Touched). It hasn't been written into the Plutonium data or tested on a Foundry character sheet.

**Where each rule comes from** (full list in *Decision record*):
- **[Patrick]**: your brief or your rulings in this session.
- **[ratified]**: gaps Claude filled. You delegated ratification on 2026-11-16, so these are ratified on that authority rather than by you directly.

**Sources:** the 2014 PHB data bundled at `reference/plutonium/data/`, and the homebrew in `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`.

---

# Gestalt

*Some minds refuse to choose. A Gestalt trains two disciplines at once and follows both to their summit, at the price of everything they never had time to learn along the way.*

## The Gestalt

| Level | Proficiency Bonus | Selections | Features |
| :---: | :---: | :---: | :--- |
| 1st | +2 | 2 | Convergence, Full Progression, Feature Selection (one from each Practice) |
| 2nd | +2 | 1 | Feature Selection |
| 3rd | +2 | 1 | Feature Selection |
| 4th | +2 | — | Ability Score Improvement |
| 5th | +3 | 1 | Feature Selection |
| 6th | +3 | 1 | Feature Selection |
| 7th | +3 | 1 | Feature Selection |
| 8th | +3 | — | Ability Score Improvement |
| 9th | +4 | 1 | Feature Selection |
| 10th | +4 | 1 | Feature Selection |
| 11th | +4 | — | — |
| 12th | +4 | — | Ability Score Improvement |
| 13th | +5 | — | — |
| 14th | +5 | 1 | Feature Selection |
| 15th | +5 | 1 | Feature Selection |
| 16th | +5 | — | Ability Score Improvement |
| 17th | +6 | — | — |
| 18th | +6 | — | — |
| 19th | +6 | — | Ability Score Improvement |
| 20th | +6 | 1 | Feature Selection |

You get **12 selections** and **5 Ability Score Improvements**. Levels with no selection still matter, because both of your classes keep scaling at every level.

## Class Features

### Hit Points
- **Hit Dice:** Under Dual Class, average your two classes' Hit Dice and round down to the nearest standard die. Under Dual Specialization, use the class's Hit Die.

  | Pair | Gestalt Hit Die |
  |---|---|
  | d12 + d10, or d12 + d8 | d10 |
  | d12 + d6, d10 + d8, or d10 + d6 | d8 |
  | d8 + d6 | d6 |
  | two of the same die | that die |
- **Hit Points at 1st Level:** the maximum of your Gestalt Hit Die + your Constitution modifier.
- **Hit Points at Higher Levels:** your Gestalt Hit Die (or its average) + your Constitution modifier per Gestalt level after 1st.

### Proficiencies
- **Saving Throws:** Choose two from your classes' saving throws: one from Dexterity, Constitution or Wisdom, and one from Strength, Intelligence or Charisma. Under Dual Specialization, use the class's saving throws.
- **Skills:** Average your two classes' starting skill counts, rounding down, and choose from either class's list. If either class lets you choose any skill, you can choose any skill. Under Dual Specialization, use the class's skills.
- **Armor, Weapons and Tools:** Choose one of your classes as your *Proficiency Practice*:
  - From that class, gain its full 1st-level armor, weapon and tool proficiencies.
  - From the other class, gain only the proficiencies it grants when you multiclass into it.

  Under Dual Specialization, use the class's proficiencies.

### Equipment
You start with the following, in addition to your background's equipment:
- studded leather armor
- a spear (or a quarterstaff, if you aren't proficient with spears)
- a light crossbow and 20 bolts (or a sling and 20 sling bullets, if you aren't proficient with light crossbows)
- two daggers
- an explorer's pack
- a component pouch, if either of your classes casts spells

If you aren't proficient with an item, you can take its price in gold instead. Studded leather armor is 45 gp.

### Convergence
At 1st level, choose your Convergence. It determines your two **Practices**, the sources your features come from. The choice is permanent.

**Dual Class.** Choose two different classes. Each class is one of your Practices.
- *Divided Power.* Your spell slots come from the **Gestalt Spell Slots** table (see Spellcasting). Every **resource pool** your Practices give you is halved, rounded up.
  - A resource pool is any number of uses, points or charges that you spend and regain on a rest. Examples: Rage uses, ki points, sorcery points, superiority dice, Bardic Inspiration, Channel Divinity uses, Wild Shape uses, Lay on Hands hit points, the slot levels Arcane Recovery restores, Consume Magic uses, and a Thaumaphage's mana.
  - A pool of 1 stays 1.
  - Not halved: die sizes, damage, dice that apply per hit or per turn (Sneak Attack, Rage damage, Martial Arts), numbers of attacks, and anything that isn't spent.

**Dual Specialization.** With the DM's permission, choose one class and two of its subclasses. Each subclass is one of your Practices, and the class itself is shared by both.
- *One Class.* You have that class's normal spell slots and resource pools at your Gestalt level, exactly as a single-classed member of it. Your only breadth limit is the selection budget, which has to cover the base class's features and both subclasses.

### Full Progression
You advance in both Practices as if you were a single-classed member of each, at your **Gestalt level** (your level in this class).

Whenever a class feature, class table or feature text refers to your level in one of your Practices' classes, use your Gestalt level. This covers:
- spell levels, cantrips, and spells known or prepared
- Rage damage
- Sneak Attack dice
- the Martial Arts die
- a Thaumaphage's Mana Exertion Limit
- formulas such as Lay on Hands

Anything that uses your *character* level, such as cantrip damage, keeps doing so.

### Feature Selection
Each time the Gestalt table grants a selection, gain one feature from either Practice's class.

**Eligibility.** A feature is eligible if all of the following are true:
1. Your Gestalt level is at least the class level at which the feature normally appears.
2. You have every feature it depends on (see *Dependencies*).
3. You don't already have it, unless it says you can take it more than once.

**Subclasses.**
- Your first subclass selection from a Practice's class must be that subclass's earliest level, and it fixes your subclass for that class.
- All the subclass features granted at one class level count as a single selection.

**Dependencies.** A feature depends on another feature if it can't function without it:
- it spends that feature's resource
- it works only while that feature is active
- it uses that class's spell attack or spell save DC

Some examples:
- Path of the Berserker, Totem Warrior and Shaman (3rd and 10th) depend on **Rage**.
- Domain Channel Divinity options depend on **Channel Divinity**.
- Ki-based monastic traditions and Shadow Arts depend on **Ki**.
- Circle of the Moon depends on **Wild Shape**.
- Cutting Words, Combat Inspiration and Peerless Skill depend on **Bardic Inspiration**.
- Draconic 6th and 18th, and Bend Luck, depend on **Font of Magic**.
- Arcane Charge depends on **Action Surge**.
- Every Occultist Rite level depends on Occultist **Spellcasting**.
- Art of the Ether depends on Thaumaphage **Spellcasting**.
- Pale Touched 14th and 18th depend on Sorcerer **Spellcasting**.

How dependencies apply:
- A subclass level depends on everything any part of it needs.
- A passing mention of another feature isn't a dependency.
- If only *part* of a feature uses another feature (such as spending a sorcery point for an extra use), you can take it, and that part starts working once you have the other feature.
- A dependency can be met by a same-named feature from either Practice. For example, a Paladin // Cleric's Domain options can use the Channel Divinity from its Paladin oath.
- Paladin oaths *grant* Channel Divinity rather than depending on it.

**Bonus Ability Score Improvements.** The extra ones some classes grant (Fighter at 6th and 14th, Rogue at 10th) are selections belonging to that class.

**Investment.**
- At least 25% of your selections, rounded down, must belong to each Practice at all times.
- At 1st level under Dual Class, take one selection from each Practice.
- Under Dual Specialization, the rule counts subclass selections only, and each subclass must hold at least a quarter of them.

**No eligible feature.** If no feature from either Practice is eligible, take an Ability Score Improvement (or a feat) instead. It belongs to neither Practice.

### Improvements
Features that only strengthen a feature you already have don't cost a selection. You gain each one automatically at its normal level, as long as you have the feature it improves.

| Class | Improvements (level) |
|---|---|
| Barbarian | Brutal Critical (2 dice) 13, (3 dice) 17 |
| Bard | Bardic Inspiration d8 5, d10 10, d12 15; Song of Rest d8 9, d10 13, d12 17; Expertise 10; Magical Secrets 14, 18 |
| Cleric | Channel Divinity 6, 18; Destroy Undead CR 1 8, CR 2 11, CR 3 14, CR 4 17; Divine Intervention Improvement 20 |
| Druid | Wild Shape Improvement 4, 8 |
| Fighter | Extra Attack (2) 11, (3) 20; Indomitable (two uses) 13, (three uses) 17; Action Surge (two uses) 17 |
| Monk | Unarmored Movement improvement 9 |
| Paladin | Aura improvements 18 |
| Ranger | Favored Enemy and Natural Explorer improvements 6; Natural Explorer improvement 10; Favored Enemy improvement 14 |
| Rogue | Expertise 6 |
| Sorcerer | Metamagic 10, 17 |
| Warlock | Mystic Arcanum (7th) 13, (8th) 15, (9th) 17 |
| Wizard, Occultist, Thaumaphage | — |

### Ability Score Improvement
At 4th, 8th, 12th, 16th and 19th level, increase one ability score by 2, or two ability scores by 1 each. You can't raise a score above 20 this way. If your table uses feats, you can take a feat instead. These don't use selections.

### Spellcasting
**Spells.** For each class whose Spellcasting you have selected, you know and prepare spells as a single-classed member of that class at your Gestalt level. That class level sets the highest spell level you can learn.

**Spell slots under Dual Specialization.** Use the class's own slot table at your Gestalt level.

**Spell slots under Dual Class.** Use the **Gestalt Spell Slots** table, whether one Practice casts spells or both.
- **Your Gestalt caster level** depends on the best caster among the Practices whose Spellcasting you have:
  - your Gestalt level if it's a full caster (Bard, Cleric, Druid, Sorcerer, Wizard, Occultist)
  - half your Gestalt level, rounded down, if it's Paladin or Ranger
  - one third, rounded down, if it's a one-third-caster subclass (Eldritch Knight, Arcane Trickster, Path of the Shaman)
- You can cast spells from either Practice with these slots. A slot above the highest spell level you know can only be used to cast a lower-level spell at a higher level.

**Pact Magic under Dual Class.** A Warlock Practice's pact slots use your Gestalt level, halved and rounded up: 1 slot from 1st to 10th level, 2 from 11th. They're kept alongside any Gestalt Spell Slots, as Pact Magic is in multiclassing.

**Thaumaphage mana under Dual Class.**
- You gain Mana Capacity free with your first Thaumaphage feature that spends or regains mana. It isn't a selection.
- Your mana maximum is halved, rounded up, **but never below your current Mana Exertion Limit**, so you can always cast at least one spell of your highest level. That matches the Gestalt Spell Slots table, which always keeps one top-level slot.
- Your Mana Crystal's charges follow your mana maximum.
- Mana and spell slots stay separate: Thaumaphage spells use mana, and other spells use slots.

#### Gestalt Spell Slots (Dual Class)
*(The PHB Multiclass Spellcaster table with each entry halved and rounded up. The normal total is in brackets.)*

| Caster level | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | — | — | — | — | — | — | — | — | 1 (2) |
| 2 | 2 | — | — | — | — | — | — | — | — | 2 (3) |
| 3 | 2 | 1 | — | — | — | — | — | — | — | 3 (6) |
| 4 | 2 | 2 | — | — | — | — | — | — | — | 4 (7) |
| 5 | 2 | 2 | 1 | — | — | — | — | — | — | 5 (9) |
| 6 | 2 | 2 | 2 | — | — | — | — | — | — | 6 (10) |
| 7 | 2 | 2 | 2 | 1 | — | — | — | — | — | 7 (11) |
| 8 | 2 | 2 | 2 | 1 | — | — | — | — | — | 7 (12) |
| 9 | 2 | 2 | 2 | 2 | 1 | — | — | — | — | 9 (14) |
| 10 | 2 | 2 | 2 | 2 | 1 | — | — | — | — | 9 (15) |
| 11 | 2 | 2 | 2 | 2 | 1 | 1 | — | — | — | 10 (16) |
| 12 | 2 | 2 | 2 | 2 | 1 | 1 | — | — | — | 10 (16) |
| 13 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | — | — | 11 (17) |
| 14 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | — | — | 11 (17) |
| 15 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | — | 12 (18) |
| 16 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | — | 12 (18) |
| 17 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 13 (19) |
| 18 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 14 (20) |
| 19 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 14 (21) |
| 20 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 14 (22) |

### Overlapping Features
When both Practices grant the same feature, use the PHB multiclassing rules:
- **Extra Attack:** versions from different classes don't add together. Only the Fighter's own Improvements add attacks.
- **Unarmored Defense:** you can have it from only one class.
- **Channel Divinity:** you gain the second class's effects but no extra uses. Use whichever class grants more uses.

### Multiclassing
Gestalt follows the PHB multiclassing rules, with these additions:
- **Prerequisites.** To multiclass into or out of Gestalt, you must meet the multiclassing prerequisites of **both** of your Practices' classes.
- **No class twice.** You can't take levels in a class that is one of your Practices, and you can't choose a Practice from a class you already have levels in. Under Dual Specialization, the shared class counts as a Practice class.
- **Gestalt level gates everything.** Selections, Improvements and scaling all use your Gestalt level, never your character level.
- **Joining later.** You choose your Convergence at your first Gestalt level. If Gestalt isn't your first class, you don't get its saving throws, skills, Proficiency Practice or equipment. Instead, choose one of your Practices and gain the proficiencies that class grants when you multiclass into it.
- **Spell slots with another casting class.**
  - **Dual Class:** add **half** your Gestalt caster level, rounded up, to your other classes' caster levels, and use the normal Multiclass Spellcaster table.
  - **Dual Specialization:** counts as its class, with levels equal to your Gestalt level.
- **Overlapping features** between Gestalt and your other classes follow the PHB multiclassing rules, the same as between your two Practices.

---

## Worked example: Fighter // Rogue (Dual Class), levels 1–5

**Setup:**
- Proficiency Practice: Fighter, so all armor, shields, and simple and martial weapons.
- Skills: 3, from either class's list.
- Hit Die: d8 (d10 and d8 average to 9, which rounds down).
- Saves: one from Dexterity/Constitution/Wisdom and one from Strength/Intelligence/Charisma.

| Level | Selection | Scaling |
|---|---|---|
| 1 | Fighting Style (Fighter) + Sneak Attack (Rogue) | Sneak Attack 1d6 |
| 2 | Action Surge (Fighter) | |
| 3 | Cunning Action (Rogue) | Sneak Attack 2d6 |
| 4 | — (Ability Score Improvement) | |
| 5 | Extra Attack (Fighter) | Sneak Attack 3d6 |

At 5th level this character has Extra Attack, Action Surge and full Sneak Attack dice. That's the depth. It has no Second Wind, Expertise, Thieves' Cant, Uncanny Dodge or subclass. That's the breadth it gave up. At 20th level it would have 10d6 Sneak Attack, Extra Attack (3) and Action Surge, but only 12 features in total.

---

# Designer's notes

## Decision record

**Your rulings (2026-11-16):**
- Gestalt is a class with two feature sources.
- Depth over breadth, with features matching a single class: 12 selections.
- Selections follow a standard cadence.
- 25% of total selections from each Practice.
- "Practice" names the two sources.
- Multiclassing is allowed, and everything uses Gestalt level.
- Dual Class halves spell slots, from the multiclass table halved and rounded up, even with one casting Practice.
- Dual Class halves resource pools, which also takes care of Font of Magic.
- Dual Specialization keeps one class's normal slots and pools.
- The equipment direction: best light armor and the most effective simple weapons.
- The Barbarian // Rogue damage premium is accepted.
- Ratification is delegated to Claude.

**Ratified by Claude under that delegation:**

| Rule | Reason |
|---|---|
| Standard ASIs on the chassis, not selections | All 12 PHB classes share 4/8/12/16/19. Charging them would leave 7 features, below every class. |
| Improvements are automatic | They're depth. The data is also inconsistent: Sneak Attack dice are a table column, while Brutal Critical dice are separate features. |
| Saving throws: one from each group | Every PHB class follows that split (12 of 12). |
| Proficiency Practice + the other class's multiclass proficiencies | Your "choose a package" idea, using the published multiclass grants. |
| Equipment list | Studded leather is the best light armor (AC 12 + Dex). The spear, light crossbow and dagger are the most effective simple weapons on the classes' lists. |
| Fallback ASI or feat when nothing is eligible | Only happens for Dual Specialization casters, about 1–2 by 10th level. |
| Dual Specialization investment counts subclass selections only | The Bard has only 3 subclass levels, so 25% of 12 couldn't be met. |
| Dependency rule (functional, partial, either Practice) | Read against the text of 27 PHB and 20+ homebrew subclass levels. Passing mentions excluded. |
| Multiclass restrictions | Each one closes a specific double-count. Checked by working through Gestalt (Wizard // Cleric) 10 / Druid 10. |
| Pact Magic kept alongside slots, both halved | Replaces the earlier "choose one set" rule, so Warlock is handled the same way as Thaumaphage mana now that everything is halved. |
| Thaumaphage: free Mana Capacity; mana floor at the Exertion Limit | Mana Capacity is just the pool's size. Without the floor, halving would put 5th-level spells out of reach at 10th level (8 mana against a cost of 10). |
| Path of the Shaman is a one-third caster | Its data record says 1/3. |
| Names: Convergence, Dual Class, Dual Specialization | "Path" (Barbarian) and "Discipline" (Monk) are taken. "Convergence" doesn't appear in the corpus, your collection or your source files. "Specialization" is your own word for subclasses (`wyrmblooded.md`). |

## Depth vs. breadth (measured across all 66 PHB class pairs)

| | Features at 20th | Depth |
|---|---|---|
| Single class | 8–21, median **12** | one class to 20 |
| Multiclass 10/10 | median **17** (range 10–25) | both classes stop at 10 |
| Gestalt | **12** | both classes to 20; Dual Class pays with halved slots and pools |

The Selections column follows the median single class's cumulative feature count and stays within one feature of it at every level. At 20th, the PHB class totals are:

| Class | Features |
|---|---|
| Sorcerer, Wizard | 8 |
| Cleric, Warlock | 9 |
| Druid | 10 |
| Bard, Fighter | 12 |
| Paladin, Ranger | 15 |
| Barbarian, Rogue | 16 |
| Monk | 21 |

Occultist and Thaumaphage (either Devouring Art) have 10 each.

## Simulation summary
The scripts are in `tmp/gestalt-sim/` in this repo: `rules_sim.py`, `builds10.py`, `deps_check.py`, `homebrew_sim.py` and `fullday.py`. They read the corpus and the collection JSON directly.

**Legality:** do the rules always produce a legal character?

| Test | Builds | Dead ends | Fallbacks |
|---|---|---|---|
| Dual Class, all 66 PHB pairs, to 20th | 19,932 | 0 | 0 |
| Dual Class, 46 pairs involving homebrew | 13,892 | 0 | 0 |
| Dual Specialization, PHB | 6,969 | 0 | casters only |
| Dual Specialization, homebrew | 1,608 | 0 | Sorcerer (with Pale Touched) 2 by 10th; Thaumaphage 0 after the Art of the Ether fix (was 1) |

- A dead end is a selection that's due, with eligible features available, where the 25% rule forbids all of them.
- The subclass dependencies were added after the first run. Before that, the simulator allowed 24,337 illegal subclass picks, such as Berserker without Rage.

Controls (checks that the tests can actually fail):
- An impossible floor flags every build.
- Planted illegal builds are rejected: Divine Smite without Spellcasting, Shaman without Rage, Art of the Ether without Thaumaphage Spellcasting.
- The legal versions of those builds pass.

**Damage at 10th level** (+9 to hit against AC 16):

| Build | 3-round fight | Full day | Best single class, day | Multiclass 5/5, day |
|---|---|---|---|---|
| Barbarian // Rogue | 152 | 730 | 525 (Barbarian) | 589 |
| Fighter // Rogue | 124 | 690 | 478 (Rogue) | 557 |
| Monk // Rogue | 125 | 711 | 441 (Monk) | 589 |
| Fighter // Paladin | 117 | 424 | 445 (Paladin) | 424 |
| Paladin // Sorcerer | 112 | 441 | 384 (Paladin) | 437 (6/4) |

- A full day is 6 encounters of 3 rounds each, with short rests after the 2nd and 4th.
- In every build, Frenzy is used in one fight a day and smites go in every round while slots last.

**Reading:**
- Dual Class halving brings builds that depend on slots down to multiclass level over a day. Without halving, Paladin // Sorcerer would deal 538 instead of 441.
- **Rogue pairs keep a 25–60% lead over the best single class.** Sneak Attack is a once-per-turn bonus, not a pool, so halving never touches it.
- You accepted the Barbarian // Rogue premium. The same reasoning covers every Rogue pair, so this is a known, accepted property, not a bug.

**Casters at 10th level:**
- Wizard // Cleric (Dual Class): 9 slots against 15 for a Wizard 10. It has spells up to 5th level from both lists, and Arcane Recovery restores 3 slot levels instead of 5.
- Dual Specialization casters have normal slots.

## Homebrew compatibility (checked 2026-11-16)
- **Occultist** is a full caster with spells known. It fits the standard rules with no special handling.
  - Ritualist, Master of the Grey, Eternal Spirit and every Rite level depend on Occultist Spellcasting.
  - Your Token and Spectral Awareness are standalone.
- **Thaumaphage** needed three rulings, all under *Spellcasting*: free Mana Capacity, halved mana with a floor at the Exertion Limit, and mana kept separate from slots. Art of the Ether depends on Thaumaphage Spellcasting; Art of the Flesh only needs mana.
- **Path of the Shaman** is a one-third caster. It depends on Rage at 3rd level (Trance Casting only works while raging) and at 10th.
- **Pale Touched**: Deathly Eyes, Ghostwalk and Haunting Strikes use sorcery points only for extra uses, so those are partial dependencies. Haunting Strikes (14th) and Harrowing Tide (18th) depend on Sorcerer Spellcasting.
- **Art of the Ether gap: fixed 2026-11-16 (Patrick authorized).** The Thaumaphage table promised a Devouring Art feature at 6th level, but Art of the Ether had none, and its 14th-level Conversion was cut off partway.
  - No missing text exists anywhere: every commit since the first 2025-06-11 draft, all 13 remote branches and the Anthology copy were searched.
  - The fix uses Patrick's own material:
    - **Conversion** (the spell-recycling ability) moves from 14th to **6th** level. It's a mana-recovery feature on the same scale as Arcane Recovery.
    - **Spell Theft**, the 14th-level capstone from the 2025 draft, is restored at **14th**, with one guard added: you can only recast a stolen spell if its mana cost fits within your Mana Exertion Limit. Otherwise it could recast Wish.
  - Applied to `venoure/Veiled_Omens/Player_Options/Classes/thaumaphage.md` and to the collection JSON. Your uncommitted mana wording is untouched, and Foundry ids are recomputed by the repo's MD5 scheme.
  - Checks: all six pre-commit validators and the 16 repo tests pass.
  - `venoure/known_terms.txt` entries 270 (Mana Overflow) and 271 (Mana Shaping) were also corrected. They had described the wrong features at the wrong levels.
  - Nothing is committed in either repo.
- **Not checked:** the homebrew subclasses that exist only as source text and aren't in the collection yet: Circle of the Veil, Way of the Mists, Oath of the Lantern and Veil Touched.

## Known properties and watch list
1. **Rogue pairs are strong in every kind of fight.** Accepted. If it ever needs a lever: only one Practice's once-per-turn damage bonus (Sneak Attack, Rage damage, Divine Smite) applies on a given turn.
2. **Thaumaphage mana floor:** at high levels the Exertion Limit floor cancels most of the halving, because the pool is small compared with the limit (at 20th: 10 mana halved against a limit of 18).
3. **Dual Specialization casters** get 1–2 bonus ASIs or feats by 10th level, because their base classes have empty levels.
4. **Not simulated:** spellcasting power beyond slot counts, and Gestalt-plus-multiclass builds (only worked through by hand).

## Data format notes
- **Encodes as an ordinary class record, like Thaumaphage:** the chassis and a table with a Selections column.
- **One class per Hit Die (2026-11-16):** Plutonium's Charactermancer computes level-up hit points from the class record's single Hit Die, so the class ships as **Gestalt (d6), (d8), (d10) and (d12)**. They are generated from one hand-edited template (`templates/gestalt-class.json`) by `tools/generate-gestalt-variants.py`, and the pre-commit hook checks they are current. Players import the variant matching their Gestalt Hit Die. A dnd5e Enchant activity was tested as an alternative and works in Foundry, but Charactermancer's Roll, Min and Max hit point modes ignore it.
- **Prose that the importer won't enforce:** Convergence, selections, dependencies, Improvements, halving and the slot table. The format has no construct for picking features.
- **Verified in Charactermancer (2026-11-16, Foundry 14.364, dnd5e 5.3.3, Plutonium 2.15.10, Gestalt (d6) via Custom URL import):** level 1 asks "Choose two" saves from all six and "Choose two" skills from all 18; both land on the sheet. HP 6 at level 1. Starting equipment imports. Levelling to 4 with Dual Class gives HP 18 (Take Average), 9 (Minimum), 24 (Maximum), and 6 plus three d6 rolls (Roll); current HP rises with max. Armor and weapon proficiencies are not granted (the class lists none); players set them by hand from their two classes.
- **Untested:** how a Foundry sheet should represent a Gestalt character.

## Sources
- **Class chassis, feature levels, subclass levels, multiclass grants and prerequisites:** `reference/plutonium/data/class/class-*.json`.
- **Multiclass Spellcaster table and overlap rules:** `variantrules.json`, Multiclassing, PHB p.163.
- **Armor and weapon stats:** `items-base.json`.
- **Homebrew:** the collection JSON, plus `Classes/thaumaphage.md` for the Art of the Ether check.
- **Proficiency bonus ladder:** the house table in `Classes/thaumaphage.md`. The corpus has no proficiency-bonus table.
- **Correction recorded during this work:** "averaging Hit Dice equals taking the lower die" (project log #14) is false for d12 + d8, d12 + d6 and d10 + d6. The `veiled-omens-5e-benchmark-sourcing` skill has been corrected.
