# D&D Ledger: notes for Claude

A character sheet and play log for 2014 fifth edition D&D. The whole app is `index.html`, served by `tools/serve.py`. Rules come from content packs. A character file holds only the player's choices. Read `docs/data-formats.md` before changing either format. It is the spec, and `data/schema/*.json` enforce it.

## Ground rules

- **2014 rules only.** That means the 2014 Player's Handbook and Dungeon Master's Guide, plus the books that use those rules: Xanathar's, Tasha's, Monster Manual, Volo's, Tome of Foes, Monsters of the Multiverse, Fizban's and Bigby's. No 2024 books, adventures, or third-party content. Every file says `"edition": "2014"`.
- **No book text in git.** The repo is public. Packs built from book PDFs go in `packs/`, which git ignores. Only SRD 5.1 material (`data/srd-*.json`, `data/base-pack.json`) is committed. The extraction tools and the name and definition tables in `tools/extract/` hold names and mechanics, not book prose.
- Personal character files (for example `data/bok-bok-character*.json`) stay uncommitted.

## How it fits together (version 2)

- **Content pack** (`"format": "dnd-content-pack", "schema": 2`): classes, subclasses, races, backgrounds, feats, option sets (invocations, maneuvers, fighting styles…), spells, items, creatures and `spellEffects`. Features carry **effects**, the vocabulary in `docs/data-formats.md#effects`: resource, action, toggle, attackRider, bonus, set, acFormula, proficiency, expertise, abilityScore, spellcasting, grantSpells, choice, asi, sense, speed, resistance, advantage, reminder, and more.
- **Character file** (`"format": "dnd-character", "schema": 2`): ids that point into packs (`"class": "wizard", "subclass": "school-of-necromancy"`), plus `choices` keyed `ownerId/choiceId`, `spells`, `inventory`, `custom.features`, and `overrides`. The app works out AC, HP, saves, slots, resource uses and attacks. Don't store derived numbers in the file.
- **Amounts** can be a number, a formula (`"max(1, mod.cha)"`, `"1d10 + classLevel"`, `col.X` for class table columns) or a level scale (`{"1": "d6", "5": "d8"}`).
- **Load order** (`loadLibrary` in `index.html`): `data/srd-spells.json` → `data/srd-items.json` → `data/base-pack.json` → every pack in `packs/`, sorted by `loadOrder` (default 50; MPMM is 60 so its reprints win, VGM/MTF are 10) → packs uploaded in the app. A later pack replaces an entry with the same id, except option sets, whose options merge. `packId:id` picks one pack's version (`mpmm:kenku`).
- **Engine** (`index.html`): `addPack` indexes packs into `R`. `ref(coll, id)` looks entries up. `derive(c, st)` walks every owner (classes, subclasses, race, subrace, background, feats and option choices, equipped and attuned items, custom features, active spells), applies their effects, and returns the computed sheet. `D()` caches it. `statBlock` renders creatures and companions.
- **Spells** (`index.html`, "SPELL DETAILS"): packs store spell text, not dice, so `spellMath(spell, slotLevel)` reads damage, healing, attack or save, upcasting and cantrip scaling from `sum` and `up`. `durRounds` reads durations (concentration and spell effects cast in combat end on their own in `nextRound`), and `spellMaterial` reads costly components. If a spell's numbers come out wrong, the fix is usually its text in the pack, not the parser.
- **Storage**: `Store` (the artifact db capability or localStorage, key prefix `dnd-ledger:`). The character is `app/character` (`C`). Play state such as current HP, spent slots and conditions is separate (`ST`).

## Version 1 files still load

Characters without `"schema": 2` are converted by `migrateCharacter` and `migrateState` when they're opened. The original is kept at `app/character-v1`. The conversion table is in `docs/data-formats.md#moving-from-version-1`. `data/character-template.json` and `data/example-character.json` are still version 1 files. `data/examples/fighter-rogue-v2.json` is a version 2 example. Version 1 packs (old `hd`/`feats` class tables) are also converted in `addPack` (`v1Class`).

## Adapting a character to version 2

1. Start from `data/examples/fighter-rogue-v2.json` and the field list in `docs/data-formats.md#character-file`.
2. Use ids from the loaded packs. To find them, search `packs/*.json` and `data/base-pack.json` for the name and copy its `id`. List the packs the character needs in `packs`.
3. Choices (fighting style, expertise, ASIs, invocations, cantrips…) go in `choices` under `ownerId/choiceId`. The choice ids are the `choice` effects in the owning class, subclass, race, background or feat.
4. Anything homebrew or missing from the packs goes in `custom.features` with effects, not in code.
5. Check the file against the packs: `python3 tools/validate.py data/base-pack.json packs/*.json <character>.json`. A warning that a choice key matches nothing usually means a typo or a missing pack.
6. Load it in the app (start page → **Import a character sheet (JSON)**) and compare the sheet with the book by hand.

## Running and checking

- `python3 tools/serve.py` serves the app at http://localhost:8790. It also lists `packs/` at `/api/packs` and commits session backups through `POST /api/backup`. The Mac app (`mac/D&D Ledger.app`) runs the same server. Its `launch` script calls the Python.app interpreter directly because macOS blocks the `python3` stub from an unsigned app. On a Mac, keep the repo out of Documents, Desktop and Downloads.
- `python3 tools/validate.py data/base-pack.json packs/*.json` checks packs against the schemas and their references. It needs `pip3 install --user jsonschema`.
- There is no automated test suite yet. After engine changes, load a few characters (single-class caster, multiclass with pact magic, Monk or Barbarian unarmored AC, a companion) and compare them against the books.

## Building packs from book PDFs (`tools/extract/`)

```
tools/extract/ocr_pdf.sh "<book>.pdf" <id>     # macOS Vision OCR → packs/.text/<id>/
python3 tools/extract/build_pack.py <id>       # → packs/<id>.json
python3 tools/validate.py data/base-pack.json packs/<id>.json
```

- Book ids: `phb xge tce dmg mm vgm mtf mpmm ftd bgg`. `BOOKS` in `build_pack.py` sets the page ranges and `loadOrder`. `books/<id>.py` defines races, feats, subclasses and their effects (using the builders in `fx.py` and `books/kit.py`). The text for each entry is looked up in the OCR output.
- `ocr.py` repairs OCR slips using a dictionary. `text.py` finds sections and stops at the next heading, table row, footer, or all-caps line. `spells.py`, `items.py` and `creatures.py` parse those blocks. The name tables (`spell-classes.json`, `item-names.json`, `creature-names*.json`) tie the parsed blocks to the right ids.
- `fixes.json` holds per-book hand corrections: field values, `textEnd` (cuts a feature's text where it runs into the next section) and `spellText` (find/replace for a few words the scan skipped).
- `ocr.py` treats any word that appears 3+ times across all the books' OCR text as real (`corpus()`), so monster names and game terms aren't "corrected". Rebuild every pack after changing it.
- Off a Mac, `pdf_text.py` reads the PDF text layer instead. That text is noisier.

## Known gaps

- SRD magic items (`data/srd-items.json`) have no effects yet. For example, Gauntlets of Ogre Power don't set Strength. An item-effects map like `spellEffects` would fix this.
- `abilityMode` defaults to `"final"`: the scores in the file already include racial bonuses and ASIs. Use `"base"` for rolled or point-buy scores, and the app adds racial bonuses, ASIs and feats. Item effects like a Belt of Giant Strength apply in both modes.
