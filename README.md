# D&D Ledger

A character sheet and play log for 2014 fifth edition D&D that runs on your own computer. It tracks hit points, spell slots, class resources, conditions, coins, XP and gear while you play, and keeps a history of every session.

What's in it:

- All 12 classes from the 2014 rules plus the Artificer, with slots, resources and multiclassing worked out from your class levels.
- The free D&D rules (SRD 5.1): about 320 spells and 240 magic items, searchable when you add a spell or item.
- Rules loaded from data, not code: classes, subclasses, races, feats, spells, items and creatures come from content packs, and their features (resources, actions, AC formulas, bonus damage, spell grants, choices) are worked out on the sheet. Build packs from books you own with `tools/extract/` (see below).
- Spells: compact rows with damage and DCs worked out, filters, pinned quick-casts, upcast damage and dice rolls when you cast, concentration saves and spell durations in combat, saved prepared lists, and spellbook copying costs.
- Sessions: open a session, log what happens, close it to get a session entry with totals. Any logged action can be edited or crossed out, and the trackers follow.
- Backups: export everything to one file, restore it later, and (when you run it with the local server) a dated backup is committed to your repo each time you close a session.

## Get your own copy

1. Fork this repo on GitHub (the **Fork** button at the top right).
2. Install [GitHub Desktop](https://desktop.github.com), sign in, and clone your fork. On a Mac, clone it into `~/GitHub/` (for example `/Users/you/GitHub/dnd-character-sheet`), not into Documents, Desktop or Downloads. macOS blocks Python from reading those folders.
3. Start it one of these ways:
   - **Mac app:** open the `mac` folder and double-click **D&D Ledger**. The first time, right-click it and pick **Open**, because the app isn't signed. To put it in your Dock or Applications, drag it there while holding Option and Command, which makes an alias.
   - **Any computer with Python 3:** in a terminal, from the repo folder, run `python3 tools/serve.py` and open http://localhost:8790.
4. On the start screen, create your character or load a file (see below).

Your data is saved in the browser that opens the ledger. The Mac app uses its own Chrome window, so its data is separate from your normal browser. Use **Export backup** on the *Backup & level up* tab to keep a copy or move it to another computer.

## Loading a character from a file

Choose a character file with **Or load a file** on the start screen. Only `name`, `abilities` and `classes` are required. The file can also be a backup exported from the ledger.

Character files use version 2 of the format: they name your class, subclass, race, feats, spells and gear by id and record your choices, and the ledger works out the rest from the loaded packs. `data/examples/fighter-rogue-v2.json` is an example, and [docs/data-formats.md](docs/data-formats.md#character-file) lists every field. To check a file before loading it:

```
python3 tools/validate.py data/base-pack.json packs/*.json my-character.json
```

Older files still load and are converted when opened; the original is kept. `data/character-template.json` and `data/example-character.json` are in the older format, and the start screen can load the example (a finished level 1 Fighter).

## Backups to GitHub

When the ledger runs through `tools/serve.py` (the Mac app does this), closing a session saves `backups/<date>-session-<n>.json` and commits it. If your terminal git isn't signed in to GitHub, the commit stays on your computer; push it from GitHub Desktop with **Push origin**.

## Spells, items and subclasses from other books

Only the SRD is built in, because the other books (Xanathar's, Tasha's and so on) are copyrighted and this repo is public. The Artificer's class features and the expansion subclass names are included as mechanics and names only.

To add content from books you own, use a content pack: a JSON file with `"format": "dnd-content-pack"` holding any of `classes`, `subclasses`, `races`, `backgrounds`, `feats`, `optionSets`, `spells`, `items` and `creatures`, with features described as effects. [docs/data-formats.md](docs/data-formats.md#content-pack) is the full format and `data/examples/srd-sample-pack.json` is an example. Put packs in `packs/` (the local server loads them all) or load one on the *Backup & level up* tab under **Content packs**. Don't commit book text. Older packs like `data/content-pack-example.json` still load.

## Packs from your own books

`tools/extract/` turns PDFs of books you own into content packs in `packs/`, which git ignores, so book text never reaches the repo. It needs `pip3 install --user pypdf jsonschema`.

```
tools/extract/ocr_pdf.sh "Player's Handbook.pdf" phb            # page text into packs/.text/phb
python3 tools/extract/build_pack.py phb                         # packs/phb.json
python3 tools/validate.py data/base-pack.json packs/phb.json    # check it
```

The local server loads every pack in `packs/` on start. Books with a definitions file in `tools/extract/books/` (races, feats, subclasses and their mechanics) get those too; the others get their spells.

`ocr_pdf.sh` reads the pages with macOS's built-in text recognition, so there's nothing to install, and takes about a second a page. It gives much cleaner text than the PDFs' own text layers, which split words apart ("magi ca l") and mix up digits and letters. It leaves out handwritten margin notes and sideways art credits, and lists them in `packs/.text/<book>/dropped.txt`. Off a Mac, `python3 tools/extract/pdf_text.py "<book>.pdf" <book-id>` pulls the text layer instead. To compare two extractions, write the new one to another folder (`ocr_pdf.sh "<book>.pdf" phb-new`) and build from it with `PACK_TEXT=phb=phb-new python3 tools/extract/build_pack.py phb`.

## Files

- `index.html`: the whole app.
- `CLAUDE.md`: how the app, formats and pack tools fit together, for anyone (or any AI assistant) changing them.
- `data/srd-spells.json`, `data/srd-items.json`: SRD content.
- `tools/serve.py`: the local server (static files plus the backup endpoint).
- `data/base-pack.json`: the built-in rules (classes, subclass names, SRD races, armor and weapons) as a content pack.
- `docs/data-formats.md`, `data/schema/`: the content pack and character formats. `data/examples/` has a sample pack and character. `tools/validate.py` checks files against them.
- `packs/`: content packs made from your own books. Git ignores this folder, and the local server loads every `.json` in it.
- `mac/D&D Ledger.app`: the Mac launcher. It starts the server and opens Chrome, Edge or Brave as an app window, or your default browser.

## Credits and license

This work includes material taken from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 is licensed under the Creative Commons Attribution 4.0 International License available at https://creativecommons.org/licenses/by/4.0/legalcode.

The SRD spell and item data was converted from [5e-bits/5e-database](https://github.com/5e-bits/5e-database). Class feature descriptions in the app are short original summaries, not book text.
