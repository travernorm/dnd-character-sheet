# Data formats (version 2)

The ledger is moving from rules written into `index.html` to rules loaded from data. This page describes the two files that make that work:

- A **content pack** holds rules: classes, subclasses, races, backgrounds, feats, spells, items and creatures. Each book gets its own pack.
- A **character file** holds one character's choices: which class and subclass, which feats, which spells, what gear. It points at things in packs by id and doesn't repeat their rules.

The app works out everything else (proficiency bonus, AC, spell slots, feature uses, attacks) from the two together.

Both formats are 2014 fifth edition only. Every file says `"edition": "2014"`.

The JSON Schemas are `data/schema/content-pack.schema.json` and `data/schema/character.schema.json`. `data/examples/` has a sample pack built from the SRD and sample characters.

## Book text stays out of the repo

This repo is public. Packs made from books you own go in the `packs/` folder, which git ignores. Only SRD 5.1 material (Creative Commons) may be committed.

## Ids and references

- Every entry has an `id`: lowercase words joined by hyphens (`school-of-necromancy`, `toll-the-dead`). If an entry has no `id`, the app makes one from its `name`.
- Ids are unique within their collection (a spell and a feat can share an id).
- If two loaded packs define the same id, the one loaded later wins. To name a specific pack's version, write `packId:entryId`, for example `mpmm:kenku` for the Monsters of the Multiverse kenku instead of `vgm:kenku` from Volo's.
- Features, choices, resources and toggles are referred to as `ownerId/id`, where the owner is the class, subclass, race, background, feat or item that grants them: `wizard/arcane-recovery`, `bard/bardic-inspiration`.

## Amounts

Anywhere a number can change with level or ability scores, an **amount** is accepted. An amount is one of:

1. **A number**: `2`
2. **A formula** string: `"mod.cha"`, `"1d10 + classLevel"`, `"max(1, mod.int)"`, `"5 * classLevel"`
3. **A scale**: an object keyed by level, each value lasting until the next key. `{"1": "d6", "5": "d8", "10": "d10", "15": "d12"}`. Scales count the owner's class level for class and subclass features, and character level for everything else. Add `"by": "level"` to count character level instead.

### Formula words

| Word | Means |
|---|---|
| `mod.str` … `mod.cha` | Ability modifier |
| `score.str` … `score.cha` | Ability score |
| `prof` | Proficiency bonus |
| `level` | Character level |
| `level.<classId>` | Level in one class (`level.wizard`), 0 if none |
| `classLevel` | Level in the class that owns this feature |
| `col.<column>` | The owner class's table column at its class level (`col.sneakAttack`) |
| `spellMod` | Spellcasting modifier of the owner class (or the main caster) |
| `spellDC`, `spellAttack` | Same, as a save DC or attack bonus |
| `NdM` | Dice. A formula with dice is rolled, not added up. |
| `min()`, `max()`, `floor()`, `ceil()` | Functions |
| `+ - * /` and `( )` | Arithmetic. Results round down unless wrapped in `ceil()`. |
| `>= > <= < == and or` | Comparisons, for prerequisites (`score.str >= 13 or score.dex >= 13`) |

## Effects

Rules live in a feature's `effects` list. A feature without effects still shows its text. It just doesn't change any numbers. Each effect has a `type`:

| `type` | What it does | Main fields |
|---|---|---|
| `resource` | A pool of uses or points shown as pips | `id`, `name`, `max`, `recharge`, `die` |
| `resourceMod` | Changes another resource | `resource`, `max` (added), `recharge` |
| `action` | A button on the Play tab | `id`, `name`, `econ`, `cost`, `roll`, `heal`, `tempHp`, `damage`, `save`, `gain`, `toggle` |
| `toggle` | An on/off state like raging | `id`, `name`, `endsOn` |
| `attackRider` | An option in the attack window | `name`, `damage`, `damageType`, `cost`, `oncePer`, `perSlotLevel`, `maxDice`, `requires` |
| `bonus` | Adds to a number | `target`, `value`, `when` |
| `set` | Sets a number | `target`, `value`, `mode` (`max`, `min`, `override`) |
| `acFormula` | An alternative way to work out AC | `formula`, `when`, `allowShield` |
| `proficiency` | Grants proficiency | `kind`, `values`, `level` |
| `expertise` | Doubles proficiency | `kind`, `values` |
| `abilityScore` | Raises a score | `ability`, `add`, `max` |
| `spellcasting` | Makes the owner class a caster | `ability`, `progression`, `list`, `cantrips`, `known`, `prepared`, `spellbook`, `ritual` |
| `grantSpells` | Adds spells you always have | `spells`, `alwaysPrepared`, `countsAgainst`, `ability`, `class` |
| `choice` | Something the player picks | `id`, `name`, `kind`, `choose`, `from` |
| `asi` | Ability Score Improvement or a feat | `id` |
| `sense` | Darkvision and the like | `sense`, `range` |
| `speed` | A movement speed | `mode`, `value` |
| `resistance`, `immunity`, `vulnerability` | Damage types | `damage`, `when` |
| `conditionImmunity` | Conditions | `conditions` |
| `advantage` | Shown as a reminder, not rolled | `on`, `note` |
| `reminder` | A note shown at a moment in play | `on`, `text` |

### Fields used by several effects

- **`recharge`**: `short` (short or long rest), `long`, `dawn` (resets with your long rest), `turn`, or `never` (only by hand). Can be a scale, as with Bardic Inspiration: `{"1": "long", "5": "short"}`.
- **`econ`**: `action`, `bonus`, `reaction`, `free`, `minute` (a minute or longer) or `special`. The combat tracker uses it.
- **`cost`**: `{"resource": "rage", "amount": 1}` spends from a resource. `{"slot": 1}` spends a spell slot of at least that level.
- **`gain`**: what an action gives back. `{"resource": "bardic-inspiration", "amount": 1}` refills a resource. `{"slots": {"total": "ceil(classLevel / 2)", "maxLevel": 5}}` restores slots (Arcane Recovery). `{"slots": {"total": 3, "maxLevel": 3, "count": 1}}` restores one slot of up to 3rd level (Pearl of Power).
- **`when`**: limits an effect. The app checks these words: `unarmored` (no armor), `noShield`, `wearingArmor`, `lightArmor`, `noHeavyArmor`, `firstRound` (the first round of combat), `concentrating`, `toggle:<id>` (that toggle is on), `attuned`, `equipped`. Anything else goes in `note`. An effect that only has a `note` is shown but not added in.

### Targets for `bonus` and `set`

`ac`, `initiative`, `speed`, `hp.max`, `hp.perLevel`, `save.all`, `save.<ability>`, `check.all`, `check.<ability>`, `skill.<skillId>`, `passive.<skillId>`, `attack.all`, `attack.melee`, `attack.ranged`, `attack.spell`, `attack.weapon`, `damage.melee`, `damage.ranged`, `damage.weapon`, `damage.spell`, `spell.dc`, `spell.attack` (add `.<classId>` for one class only, as in `spell.dc.bard`), `attacksPerAction`, `critRange`, `ability.<ability>`.

Examples:

```json
{"type": "set", "target": "attacksPerAction", "value": 2, "mode": "max"}
{"type": "bonus", "target": "initiative", "value": "mod.wis"}
{"type": "bonus", "target": "attacksPerAction", "value": 1, "when": "firstRound"}
{"type": "set", "target": "ability.str", "value": 19, "mode": "max", "when": "attuned"}
```

### Proficiency kinds

`save`, `skill`, `tool`, `armor`, `weapon`, `language`, and `check` (ability checks in general). `level` is `full` (the default), `half` or `halfUp`. Jack of All Trades is:

```json
{"type": "proficiency", "kind": "check", "values": ["all"], "level": "half", "onlyIfNotProficient": true}
```

Skill ids: `acrobatics`, `animalHandling`, `arcana`, `athletics`, `deception`, `history`, `insight`, `intimidation`, `investigation`, `medicine`, `nature`, `perception`, `performance`, `persuasion`, `religion`, `sleightOfHand`, `stealth`, `survival`. Ability ids: `str`, `dex`, `con`, `int`, `wis`, `cha`.

### Spellcasting

```json
{
  "type": "spellcasting",
  "ability": "int",
  "progression": "full",
  "list": "wizard",
  "cantrips": "col.cantrips",
  "prepared": "max(1, mod.int + classLevel)",
  "spellbook": {"start": 6, "perLevel": 2},
  "ritual": "spellbook",
  "focus": "Arcane focus"
}
```

- `progression` is `full`, `half`, `third`, `artificer` or `pact`. The app combines them with the 2014 multiclass rules and keeps Pact Magic slots separate. The slot tables are core rules and stay in the app.
- Use `known` for classes that know a fixed number (`"col.spellsKnown"`), `prepared` for classes that prepare each day, and both `spellbook` and `prepared` for wizards.
- `ritual` is `spellbook` (cast any ritual in your book), `prepared` (only prepared ones), `known`, or `none`.
- A subclass that makes a third-caster (Eldritch Knight, Arcane Trickster) adds this effect from its own feature.

### Spells you get for free

```json
{
  "type": "grantSpells",
  "class": "ranger",
  "alwaysPrepared": true,
  "countsAgainst": false,
  "spells": [
    {"id": "disguise-self", "minLevel": 3},
    {"id": "rope-trick", "minLevel": 5}
  ]
}
```

For racial or feat spells that don't use slots, give each spell `uses`, `recharge` and `noSlot: true`. `econ` changes how it's cast (Merge with Stone casts *blade ward* as a bonus action). `ability` sets the casting ability when it isn't the class's.

### Choices

A choice is anything the player picks once: a fighting style, expertise skills, invocations, metamagic, maneuvers, a Magical Secrets spell.

```json
{"type": "choice", "id": "fighting-style", "name": "Fighting Style", "kind": "option", "choose": 1, "from": {"optionSet": "fighting-styles"}}
{"type": "choice", "id": "expertise-1", "name": "Expertise", "kind": "expertise", "choose": 2, "from": {"skills": "proficient"}}
{"type": "choice", "id": "invocations", "name": "Eldritch Invocations", "kind": "option", "choose": "col.invocations", "from": {"optionSet": "eldritch-invocations"}}
{"type": "choice", "id": "magical-secrets-10", "name": "Magical Secrets", "kind": "spell", "choose": 2, "from": {"spells": {"list": "any", "maxLevel": "slot"}}}
```

`kind` is `option`, `skill`, `expertise`, `tool`, `language`, `ability`, `spell`, `feat` or `text`. `from` names an option set, a list of ids (`{"ids": [...]}`), skills (a list, or `"any"`, or `"proficient"`), or spells (`list`, `maxLevel`, `school`). An option set's entries are features, so their effects apply once chosen.

`asi` is a shortcut for the Ability Score Improvement choice: +2 to one score, +1 to two, or a feat.

The character file stores answers under `choices`, keyed by `ownerId/choiceId`.

## Content pack

```json
{
  "format": "dnd-content-pack",
  "schema": 2,
  "edition": "2014",
  "id": "phb",
  "name": "Player's Handbook",
  "source": {"abbr": "PHB", "title": "Player's Handbook"},
  "requires": [],
  "classes": [],
  "subclasses": [],
  "races": [],
  "backgrounds": [],
  "feats": [],
  "optionSets": [],
  "spells": [],
  "items": [],
  "creatures": [],
  "spellEffects": {}
}
```

Every collection is optional. Every entry can carry `page` (and `source` when it isn't the pack's book).

`spellEffects` adds effects to spells defined elsewhere, keyed by spell id, so a pack can make the SRD's *mage armor* change AC without repeating its text: `{"mage-armor": [{"type": "acFormula", "formula": "13 + mod.dex", "when": "unarmored"}]}`.

The app always loads `data/srd-spells.json`, `data/srd-items.json` and `data/base-pack.json` (the built-in classes, races and gear), then every `.json` pack in `packs/` (in `loadOrder`, default 50), then packs loaded on the *Backup & level up* tab. A later pack overrides an earlier one with the same id, except option sets, which merge: a book that adds invocations or maneuvers lists only its new options.

### Feature

Classes, subclasses, races, backgrounds, feats, items and option sets all hold features:

```json
{"id": "arcane-recovery", "name": "Arcane Recovery", "level": 1, "text": "Once a day during a short rest, regain spell slots totalling up to half your wizard level (rounded up), none higher than 5th.", "effects": [ ... ]}
```

`level` is the class level it arrives at (for races, character level). `text` is a short description. It's shown on the sheet and in level-up.

### Class

| Field | Notes |
|---|---|
| `id`, `name` | |
| `hitDie` | `6`, `8`, `10` or `12` |
| `primaryAbility` | List of ability ids |
| `saves` | The two save proficiencies (first class only) |
| `proficiencies` | `armor`, `weapons`, `tools` (lists of text) and `skills` (`{"choose": 2, "from": [...]}`) |
| `multiclass` | `requires` (a formula), `proficiencies` (what you get when multiclassing into it) |
| `subclassLevel` | Level the subclass is picked |
| `subclassTitle` | What the book calls it ("Arcane Tradition") |
| `table` | Per-level columns. Each is a list of 20 values, level 1 first: `{"cantrips": [3,3,3,4,...], "sneakAttack": ["1d6","1d6","2d6",...]}` |
| `features` | Features with `level` |
| `startingEquipment` | Text |

### Subclass

`id`, `name`, `class` (the class id), `features` (levels are class levels), and an optional `spells` shortcut for domain, oath and patron lists, written as a `grantSpells` effect.

### Race

`id`, `name`, `size`, `speed`, `features` (traits), `subraces` (each with `id`, `name`, `features`). Ability bonuses are `abilityScore` effects, and languages are `proficiency` effects. Races with flexible bonuses (Tasha's or Monsters of the Multiverse) use a `choice` of kind `ability`.

### Background

`id`, `name`, `features` (proficiencies as effects, plus the background feature), `equipment` (text).

### Feat

`id`, `name`, `prerequisite` (`{"formula": "score.str >= 13", "text": "Strength 13 or higher"}`), `features` or `effects`, `text`.

### Option set

`id`, `name`, `options` (a list of features). For fighting styles, invocations, metamagic, maneuvers, infusions, pact boons, and so on. An option can have a `prerequisite` like a feat.

### Spell

The version 1 fields stay the same so existing packs and `srd-spells.json` keep working: `name`, `lvl` (0 for cantrips), `school`, `time` (`action`, `bonus`, `reaction`, or text like `"10 minutes"`), `range`, `comp`, `dur`, `conc`, `ritual`, `save`, `sum`, `up`, `scale`, `classes` (class ids or names).

New, all optional:

- `id`, `page`
- `attack`: `melee` or `ranged` (a spell attack roll)
- `damage`: `{"dice": "1d10", "type": "fire"}`, `scaling` for cantrips (`{"5": "2d10", "11": "3d10", "17": "4d10"}`), `perSlot` for upcasting (`"1d6"`)
- `heal`: an amount (`"1d4 + spellMod"`)
- `effects`: applied while the spell is marked active on you (Mage Armor's `acFormula`, Shield's `bonus` to `ac`)

### Item

The version 1 fields stay (`name`, `rarity`, `type`, `attune`, `text`). New:

- `id`, `page`
- `kind`: `weapon`, `armor`, `shield`, `gear`, `tool`, `wondrous`, `potion`, `scroll`, `wand`, `ring`, `ammunition`
- `weapon`: `category` (`simple` or `martial`), `ranged`, `dmg`, `damageType`, `versatile`, `range`, `props` (list), `ammo`
- `armor`: `category` (`light`, `medium`, `heavy`), `base`, `dexCap`, `strength`, `stealthDisadvantage`. Shields use `kind: "shield"` and `armor.base: 2`.
- `magic`: the +1/+2/+3 bonus for weapons and armor
- `charges`: `{"max": 7, "recharge": "dawn", "regain": "1d6 + 1"}`
- `effects`: active while the item is equipped, or attuned if it needs attunement. Actions here use the item's charges or resources.

### Creature

For familiars, summons, animated dead and wild shapes. The app shows a compact stat block; only the basics are read.

`id`, `name`, `size`, `type`, `alignment`, `ac` (and `acNote`, like "natural armor"), `hp` (`{"average": 13, "dice": "2d8 + 4"}`), `speed`, `abilities`, `saves`, `skills`, `vulnerabilities`, `resistances`, `immunities`, `conditionImmunities`, `senses`, `languages`, `cr`, and `traits`, `actions`, `bonusActions`, `reactions`, `legendary` (each a list of `{"name", "text"}`).

## Character file

```json
{
  "format": "dnd-character",
  "schema": 2,
  "edition": "2014",
  "packs": ["srd", "phb", "xge"],

  "name": "Bok-Bok",
  "player": "",
  "alias": "",
  "race": "kenku",
  "subrace": "",
  "background": "",
  "size": "Small",
  "alignment": "",
  "age": "",
  "look": "",
  "backstory": "",
  "cover": "",
  "campaign": {"name": "", "dm": "", "start": "", "notes": ""},

  "abilityMode": "final",
  "abilities": {"str": 8, "dex": 13, "con": 15, "int": 17, "wis": 12, "cha": 10},

  "classes": [{"class": "wizard", "subclass": "school-of-necromancy", "level": 3}],
  "levelHistory": ["wizard", "wizard", "wizard"],
  "hp": {"rolls": [6, 4, 4], "max": null},
  "xp": 1200,

  "choices": {},
  "proficiencies": {},
  "spells": {},
  "customSpells": [],
  "inventory": [],
  "attacks": [],
  "gold": {"pp": 0, "gp": 10, "ep": 0, "sp": 0, "cp": 0},
  "companions": [],
  "custom": {"features": [], "resources": []},
  "overrides": {},
  "levelPlan": []
}
```

Only `name`, `abilities` and `classes` are required.

### Fields

- **`packs`**: the pack ids this character needs. The app warns if one isn't loaded. It doesn't refuse to load.
- **`cover`**: the cover image shown above the sheet, as an image URL or a `data:image/...` URL. The Sheet tab's Upload button stores the image here as a JPEG data URL under about 500 KB, so character files and backups carry it.
- **`race`, `subrace`, `background`**: ids from packs. Text that matches no id still shows on the sheet, without rules.
- **`abilityMode`**:
  - `final` (the default): `abilities` are the scores on your sheet, with racial bonuses and ASIs already in. The app won't add them again. A level-up ASI changes the stored scores.
  - `base`: `abilities` are rolled or point-buy scores, and the app adds racial bonuses, ASI choices and feats.
- **`classes`**: `class` and `subclass` are ids, `level` is 1-20. The first entry is your starting class (save proficiencies, full hit die at level 1).
- **`levelHistory`**: optional. Lists the class taken at each character level in order, so HP rolls and multiclass order line up. Without it the app assumes `classes` order.
- **`hp`**: `rolls` has one entry per level (the first is the full hit die). Leave it out to use averages. `max` overrides the calculation entirely, as `maxHP` did in version 1.
- **`choices`**: answers to `choice` and `asi` effects, keyed `ownerId/choiceId`:
  ```json
  {
    "fighter/fighting-style": ["archery"],
    "rogue/expertise-1": ["stealth", "thievesTools"],
    "wizard/asi-4": {"abilities": {"int": 2}},
    "wizard/asi-8": {"feat": "war-caster"},
    "kenku/kenku-recall": ["history", "perception"],
    "wizard/skills": ["arcana", "investigation"]
  }
  ```
  `<classId>/skills` holds the class's starting skill picks from `proficiencies.skills` (first class only, or the multiclass pick).
- **`proficiencies`**: extra proficiencies not from any pack entry: `saves`, `skills`, `expertise`, `tools`, `armor`, `weapons`, `languages` (lists). They're added to the ones the app works out.
- **`spells`**: keyed by class id. The lists hold spell ids or ids from `customSpells`.
  ```json
  {
    "wizard": {
      "cantrips": ["fire-bolt", "minor-illusion", "toll-the-dead"],
      "spellbook": ["mage-armor", "shield", "magic-missile", "absorb-elements", "false-life", "ray-of-sickness"],
      "prepared": ["mage-armor", "shield", "magic-missile", "absorb-elements", "false-life"]
    },
    "bard": {"cantrips": ["vicious-mockery"], "known": ["healing-word", "dissonant-whispers"]}
  }
  ```
  Spells granted by effects (domain spells, racial spells) aren't listed here.
- **`customSpells`**: full spell objects with an `id`, for spells not in any loaded pack. If a pack has a spell with the same id, the character's copy wins.
- **`inventory`**: every item, mundane or magic.
  ```json
  {"item": "pearl-of-power", "name": "Egg-shaped pearl", "qty": 1, "equipped": false, "attuned": true, "charges": 1, "note": "Found in the vault"}
  ```
  `item` is a pack id. `magic` (1 to 3) makes it a +1, +2 or +3 weapon, armor or shield. `name` is optional (a display name, or the name of something not in any pack). Equipped armor and shields set AC. Equipped weapons become attacks.
- **`attacks`**: extra attacks that don't come from an equipped weapon. Version 1 fields: `name`, `ability` (`str`, `dex`, `finesse`, or `spell`), `prof`, `dmg`, `type`, `range`, `props`, `ammo`, `magic`.
- **`companions`**: `{"creature": "skeleton", "name": "Milton", "hp": 13, "note": ""}`. `creature` is a pack id.
- **`custom.features`**: homebrew or anything a pack doesn't cover, in the same feature format, effects included. That's how a character file can be complete without a pack.
- **`custom.resources`**: plain counters (`id`, `name`, `max`, `recharge`).
- **`overrides`**: final numbers that replace the calculation, as a last resort: `ac`, `maxHP`, `initiative`, `speed`, `spellDC.<classId>`, `spellAttack.<classId>`, `save.<ability>`, `skill.<skillId>`.

### What isn't in the character file

Play state (current HP, spent slots and uses, conditions, concentration, combat round) stays in the ledger's state, as before. A full backup still bundles the character, state, sessions, notes and log.

## Moving from version 1

Version 1 files (no `schema`, or `"schema": 1`) still load. The app converts them:

| Version 1 | Version 2 |
|---|---|
| `classes[].cls` / `.sub` (names) | `classes[].class` / `.subclass` (ids, by slug) |
| `hpRolls`, `hpBonus`, `maxHP` | `hp.rolls`, `hp.max` |
| `saveProfs`, `skillProfs`, `expertise` | `proficiencies` |
| `armorProf`, `weapons`, `tools`, `languages` (text) | `proficiencies` lists |
| `armor` object | An inventory armor item, or `custom.features` with an `acFormula` |
| `spells` (refs and objects) | `spells.<mainClass>.known` plus `customSpells` |
| `magicItems` | `inventory` entries |
| `customFeatures`, `customResources` | `custom.features`, `custom.resources` |
| `fightingStyle`, `favoredEnemy`, `favoredTerrain` | `choices` |
| `drum` | An inventory item with effects |

The converted file keeps `"abilityMode": "final"`, so no scores change.
