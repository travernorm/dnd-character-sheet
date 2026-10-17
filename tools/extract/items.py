#!/usr/bin/env python3
"""Turn a book's magic item chapter (text from ocr_pdf.sh or pdf_text.py) into content-pack items.

An item starts where a name line in capitals is followed by its type line
("Wondrous item, uncommon (requires attunement)"). Names are matched against
data/srd-items.json where possible. Prints a JSON list.

Usage: python3 tools/extract/items.py <book> <first page> <last page> > out.json
"""
import difflib, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ocr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KINDS = [("wondrous", "wondrous"), ("ring", "ring"), ("rod", "rod"), ("staff", "staff"), ("wand", "wand"), ("potion", "potion"),
         ("scroll", "scroll"), ("weapon", "weapon"), ("armor", "armor"), ("ammunition", "ammunition")]
TYPE_RE = re.compile(r"^\s*(wondrous\s*item|ring|rod|staff|wand|potion|scroll|weapon|armor|ammunition)\b(.*)$", re.I)
RARITY_RE = re.compile(r"\b(very\s*rare|uncommon|common|rare|legendary|artifact|rarity\s*varies)\b", re.I)


TYPE_WORDS = {"wondrous": "wondrous", "ring": "ring", "rod": "rod", "staff": "staff", "wand": "wand", "potion": "potion", "scroll": "scroll",
              "weapon": "weapon", "armor": "armor", "ammunition": "ammunition"}


def kind_of(line):
    """Kind from a type line, allowing for letters clipped off the page edge ('and, uncommon' is a wand)."""
    if len(line) > 150 or not RARITY_RE.search(line):
        return None
    first = re.sub(r"[^a-z]", "", (re.split(r"[,(]", line.lower())[0].split() or [""])[0])
    if not first:
        return None
    if first in TYPE_WORDS:
        return TYPE_WORDS[first]
    if len(first) < 3:
        return None
    score = lambda w: 1.0 if w.endswith(first) else difflib.SequenceMatcher(None, first, w).ratio()
    best = max(TYPE_WORDS, key=score)
    return TYPE_WORDS[best] if score(best) >= 0.6 else None


# The SRD renames some items; the book's name is kept under the SRD id so the book's entry replaces it.
ALIAS = {"Heward's Handy Haversack": "handy-haversack", "Daern's Instant Fortress": "instant-fortress", "Nolzur's Marvelous Pigments": "marvelous-pigments",
         "Apparatus of Kwalish": "apparatus-of-the-crab", "Quaal's Feather Token": "feather-token", "Iron Bands of Bilarro": "iron-bands-of-binding",
         "Keoghtom's Ointment": "restorative-ointment", "Glamoured Studded Leather": "glamoured-studded-leather-armor"}


def slug(t):
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", t.lower().replace("'", "").replace("’", "")))


def capsy(s):
    letters = [c for c in s if c.isalpha()]
    return len(letters) >= 3 and sum(c.isupper() for c in letters) >= 0.75 * len(letters) and len(s) <= 60


def join(body):
    out = ""
    for s in body:
        if out.endswith("-"):
            out = out[:-1] + s
        elif out and re.search(r"[.!?:]$", out) and s[:1].isupper():
            out += "\n\n" + s
        else:
            out = (out + " " + s).strip()
    return out


def parse(book, first, last):
    lines = []
    for p in range(first, last + 1):
        f = ocr.page_file(book, p)
        if not os.path.exists(f):
            continue
        for ln in open(f, encoding="utf-8").read().split("\n"):
            s = ln.strip()
            if not s or re.fullmatch(r"\d{1,3}", s) or re.match(r"^(\d{1,3}\s+)?(CHAPTER \d|PART \d)", s, re.I) or ocr.FOOTER_LINE.match(s):
                continue
            lines.append((p, s))
    srd = json.load(open(os.path.join(ROOT, "data", "srd-items.json")))
    srd = srd if isinstance(srd, list) else list(srd.values())
    sq = lambda x: re.sub(r"[^a-z]", "", x.lower().replace("1", "l").replace("0", "o"))
    keys = {sq(x["name"]): x["name"] for x in srd}
    extra = os.path.join(os.path.dirname(os.path.abspath(__file__)), "item-names.json")  # names only, for matching
    if os.path.exists(extra):
        for n in json.load(open(extra)):
            keys.setdefault(sq(n), n)
    starts = []
    for i in range(len(lines) - 1):
        name, nxt = lines[i][1], lines[i + 1][1]
        both = nxt + " " + (lines[i + 2][1] if i + 2 < len(lines) else "")
        if capsy(name) and not kind_of(name) and (kind_of(nxt) or (kind_of(both) and len(nxt) < 60 and "(" in nxt)):
            starts.append(i)
    # Second pass: a known name whose type line is pushed a few lines down by the other column.
    found = {difflib.get_close_matches(sq(lines[i][1]), list(keys), n=1, cutoff=0.8)[0] for i in starts if difflib.get_close_matches(sq(lines[i][1]), list(keys), n=1, cutoff=0.8)}
    gap = {}
    for k in set(keys) - found:
        for i, (_, s) in enumerate(lines):
            if capsy(s) and difflib.SequenceMatcher(None, sq(s), k).ratio() > 0.9:
                t = next((j for j in range(i + 1, min(len(lines), i + 9)) if kind_of(lines[j][1])), None)
                if t:
                    gap[i] = t
                    break
    starts = sorted(set(starts) | set(gap))
    items = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        raw = lines[i][1]
        prev = lines[i - 1][1] if i > 0 and capsy(lines[i - 1][1]) and (i - 1) not in starts and not kind_of(lines[i - 1][1]) else None
        t0 = gap.get(i, i + 1)
        tline, j = lines[t0][1], t0 + 1
        while j < end and "(" in tline and ")" not in tline:  # attunement note wraps
            tline += " " + lines[j][1]; j += 1
        if not RARITY_RE.search(tline) and j < end:
            tline += " " + lines[j][1]; j += 1
        name = None
        for cand in [raw] + ([prev + " " + raw] if prev else []):  # a long name can break over two lines
            hit = difflib.get_close_matches(sq(cand), list(keys), n=1, cutoff=0.8)
            if hit:
                name = keys[hit[0]]; break
        if not name:  # not in the SRD: rebuild words the scan split apart ("M Ac E Of Terror")
            core = re.sub(r"[^A-Za-z',+ 0-9]", "", raw)
            words = core.split()
            if sum(len(w) <= 2 for w in words) > len(words) / 3:
                parts = ocr.segment(re.sub(r"[^a-z]", "", core.lower()))
                core = " ".join(parts) if parts else core
            name = re.sub(r"\s+", " ", ocr.clean(core.title())).replace("'S ", "'s ").replace(" Of ", " of ").replace(" The ", " the ").replace(" And ", " and ").strip()
        kind = kind_of(tline) or "wondrous"
        rm = RARITY_RE.search(tline)
        rarity = re.sub(r"\s+", " ", rm.group(1)).capitalize() if rm else ""
        am = re.search(r"requires\s*attunement(\s*by\s*([^)]+))?", tline, re.I)
        attune = (am.group(2).strip() if am and am.group(2) else True) if am else False
        text = ocr.clean(join([s for _, s in lines[j:end]]))
        items.append({"id": ALIAS.get(name, slug(name)), "name": name, "kind": kind, "type": ocr.clean(re.sub(r"\s+", " ", tline)).strip(),
                      "rarity": rarity, "attune": attune, "page": lines[i][0], "text": text})
    best = {}
    for it in items:  # the same item can show up twice (a table or sidebar); keep the full entry
        if it["id"] not in best or len(it["text"]) > len(best[it["id"]]["text"]):
            best[it["id"]] = it
    return list(best.values())


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    it = parse(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    json.dump(it, sys.stdout, indent=1, ensure_ascii=False)
    sys.stderr.write("%d items\n" % len(it))
