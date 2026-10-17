#!/usr/bin/env python3
"""Turn a book's spell chapter (text from ocr_pdf.sh or pdf_text.py) into content-pack spells.

Reads packs/.text/<book>/pNNNN.txt for the given pages, finds each spell block
(name, level and school, Casting Time, Range, Components, Duration, text), fixes the
common OCR slips, and matches names against known spell names. Prints a JSON list.

Class lists come from data/srd-spells.json and tools/extract/spell-classes.json
(names and classes only).

Usage: python3 tools/extract/spells.py <book> <first page> <last page> > out.json
"""
import difflib, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ocr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHOOLS = ["Abjuration", "Conjuration", "Divination", "Enchantment", "Evocation", "Illusion", "Necromancy", "Transmutation"]
ABIL = {"strength": "Str", "dexterity": "Dex", "constitution": "Con", "intelligence": "Int", "wisdom": "Wis", "charisma": "Cha"}

FIXES = [  # common OCR slips in these scans
    (r"(?<=[a-z])I(?=[a-z])", "l"), (r"\bI(?=[a-z]{2,})", "l"), (r"\bVou\b", "You"), (r"\bVour\b", "Your"), (r"\bali\b", "all"), (r"\bAli\b", "All"),
    (r"\bI (hour|minute|action|round|day|bonus|reaction)", r"1 \1"), (r"\b(\d+)(feet|foot|minutes?|hours?|rounds?|days?|actions?|mile)", r"\1 \2"),
    (r"\bV,\s*5\b", "V, S"), (r"\bS,\s*5\b", "S"), (r"(?<=[ ,])5(?=, M\b)", "S"), (r"\bspeIl", "spell"), (r"\bIevel", "level"),
    (r"\bISO\b", "150"), (r"\bfeel\b", "feet"), (r"\bminule", "minute"), (r"(?<=\d)lh\b", "th"), (r"\bId(\d)", r"1d\1"), (r"(?<=\d)d(?=\d)", "d"),
    (r"\bthe target's speed drops to O\b", "the target's speed drops to 0"), (r"\bto O\b", "to 0"), (r"[ \t]+", " "),
]
def fix(t):
    for a, b in FIXES:
        t = re.sub(a, b, t)
    return ocr.clean(t).strip()

LEVEL_RE = re.compile(r"^\s*([1-9lI])\s*(?:st|nd|rd|th|s1|n d|lh)[\s.-]*[lI1]e[vy]e[lI1i]\s*([A-Za-z]{5,})\s*(\(\s*ritual\s*\))?", re.I)
CANTRIP_RE = re.compile(r"^\s*([A-Za-z]{5,})\s+c[a-z]{3,6}p\b", re.I)
FIELD_RE = re.compile(r"^\s*(Ca[a-z ]{2,7}Time|Ra[nm]ge|Co[mn]p[a-z]{4,7}|Dur[a-z;]{3,6})\s*[:;.]\s*(.*)$", re.I)
GLUED_RE = re.compile(r"(?<=\S)\s+(?=(?:Ra[nm]ge|Co[mn]p[a-z]{4,7}|Dur[a-z;]{3,6})\s*[:;])")


def level_line(t):
    """Level, school and ritual from a scanned line like '3rd~evelevoeaUon', '5th-leveI iIIusion' or 'Evoeation eantrip'."""
    t = t.strip(); low = t.lower()
    ritual = bool(re.search(r"\(\s*r[a-z0-9]{3,5}\s*\)", low))
    low = re.sub(r"\(\s*r[a-z0-9]{3,5}\s*\)", "", low).strip()
    tight = re.sub(r"\s+", "", low)  # "cantr ip"
    cm = re.search(r"[ce]?a?n?t?r[il1]p$", tight)
    if cm and not re.search(r"[lI1i/]?e[vy]e[il1]", tight):
        word = re.sub(r"[^a-z]", "", tight[:cm.start()])
        sch = school_of(word)
        return (0, sch, False) if sch else None
    m = re.match(r"^\s*([0-9lIi/!|S])\s*[~./-]?\s*(st|nd|rd|th|s|n|r|t)", t)
    if not m:
        return None
    d = m.group(1)
    lv = int(d) if d.isdigit() else 5 if d == "S" else 1
    km = list(re.finditer(r"e[vy]e[il1]", low))
    rest = re.sub(r"[^a-z]", "", low[km[-1].end():] if km else low[m.end():])
    sch = school_of(rest)
    return (lv, sch, ritual) if sch and 1 <= lv <= 9 else None


def school_of(word):
    m = difflib.get_close_matches(word.lower().capitalize(), SCHOOLS, n=1, cutoff=0.5)
    return m[0] if m else None


def known_names():
    """Known spells as {name: {lvl, school, classes, id}}: the SRD list plus spell-classes.json."""
    srd = json.load(open(os.path.join(ROOT, "data", "srd-spells.json")))
    out = {v["name"]: {"lvl": v["lvl"], "school": v["school"], "classes": [c.lower() for c in v.get("classes", [])], "id": k} for k, v in srd.items()}
    extra = os.path.join(ROOT, "tools", "extract", "spell-classes.json")
    if os.path.exists(extra):
        for name, e in json.load(open(extra)).items():
            alias = e.get("srd")
            if alias:  # the SRD calls it something else; the book's name wins, under the SRD id
                out.pop(next((n for n, v in out.items() if v["id"] == alias), None), None)
            out[name] = {"lvl": e["lvl"], "school": e["school"], "classes": e["classes"], "id": alias}
    return out


# Short fields have few real values, so they snap to the nearest one instead of being spell-checked.
UNITS = ["1 round", "6 rounds", "1 minute", "10 minutes", "1 hour", "2 hours", "8 hours", "12 hours", "24 hours", "1 day", "7 days", "10 days", "30 days", "1 year"]
TIMES = ["1 action", "1 bonus action", "1 reaction", "1 minute", "10 minutes", "1 hour", "8 hours", "12 hours", "24 hours", "1 action or 8 hours"]
DURS = ["Instantaneous", "Special", "Until dispelled", "Until dispelled or triggered"] + UNITS + ["Up to " + u for u in UNITS] + ["Concentration, up to " + u for u in UNITS]
def squash(t):
    t = t.lower().replace(" ", "")
    t = re.sub(r"^[il|]", "1", t)
    return re.sub(r"(?<=\d)[oO]", "0", t)
def snap(raw, options, cutoff=0.75):
    m = difflib.get_close_matches(squash(raw), [squash(o) for o in options], n=1, cutoff=cutoff)
    return options[[squash(o) for o in options].index(m[0])] if m else None
def canon_time(raw):
    raw = " ".join(raw.split())
    head, _, rest = raw.partition(",")
    t = snap(head, TIMES) or fix(head)
    return t + (", " + ocr.clean(rest.strip()) if rest.strip() else "")
def canon_dur(raw):
    return snap(" ".join(raw.split()), DURS) or fix(raw)
def canon_range(raw):
    t = " ".join(raw.split())
    t = re.sub(r"\b[iIl]\s?[sS5][oO0]\b", "150", t)
    t = re.sub(r"\b[lI][O0]{1,2}\b", lambda m: "1" + "0" * (len(m.group(0)) - 1), t)
    word = snap(t, ["Self", "Touch", "Sight", "Special", "Unlimited"], 0.6) if not re.search(r"\d", t) else None
    if word:
        return word
    m = re.match(r"^\s*(\d+)\s*([a-z!]+)", t, re.I)
    if m and not re.match(r"^\s*s", t, re.I):
        return m.group(1) + (" mile" + ("s" if m.group(1) != "1" else "") if m.group(2).lower().startswith("mi") else " feet")
    sm = re.match(r"^\s*S[a-z\]]{1,3}\s*\f?\(?\s*(\d+)\s*-?\s*(foot|mile)[- ]?(radius)?\s*([a-z]*)", t, re.I)
    if sm:
        shape = (sm.group(3) or "") + (" " + sm.group(4) if sm.group(4) else "")
        return "Self (%s-%s %s)" % (sm.group(1), sm.group(2).lower(), shape.strip().lower() or "radius")
    return fix(t)


def canon_comp(raw):
    t = " ".join(raw.split())
    m = re.match(r"^([VvSs5,.;:\s]*)(M\s*\(?.*)?$", t)
    if not m:
        return fix(t)
    letters = ["S" if c in "Ss5" else "V" for c in m.group(1) if c in "VvSs5"]
    mat = m.group(2) or ""
    if mat:
        inner = re.sub(r"^M\s*\(?", "", mat).rstrip(")")
        letters.append("M (" + ocr.clean(inner).strip() + ")" if inner.strip() else "M")
    return ", ".join(letters)


def paragraphs(lines):
    """Join wrapped lines back into paragraphs."""
    out, cur = [], ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if cur.endswith("-") and not cur.endswith(" -"):
            cur = cur[:-1] + ln
        elif cur and (re.search(r"[.!?:]$", cur) and (ln[:1].isupper() or ln.startswith("•"))):
            out.append(cur); cur = ln
        else:
            cur = (cur + " " + ln).strip()
    if cur:
        out.append(cur)
    return out


def parse(book, first, last):
    lines = []
    for p in range(first, last + 1):
        f = ocr.page_file(book, p)
        if not os.path.exists(f):
            continue
        for ln in open(f, encoding="utf-8").read().split("\n"):
            ln = re.sub(r"\s*PART \d+\s*[I|]\s*SPELLS\s*", " ", ln)
            s = ln.strip()
            s = re.sub(r"\s*PART \d+\s*[I|]\s*SPELLS\s*", " ", s).strip()
            if re.fullmatch(r"\d{1,3}", s) or re.match(r"^(\d{1,3}\s+)?CHAPTER \d+", s, re.I) or ocr.FOOTER_LINE.match(s) or not s:
                continue
            lines.extend(GLUED_RE.split(ln))  # "Range: 60 feet Components: V" becomes two lines
    names = known_names()
    canon = list(names)
    # A spell starts where a name line is followed by its level line and, within a few lines, Casting Time.
    starts = []
    for i in range(len(lines) - 2):
        letters = [c for c in lines[i] if c.isalpha()]
        if len(letters) < 2 or sum(c.isupper() for c in letters) < 0.7 * len(letters) or len(lines[i + 1].strip()) > 45:
            continue
        if re.match(r"^\s*Ca[a-z ]{2,7}Time", lines[i + 2], re.I) and level_line(lines[i + 1]):
            starts.append(i)
    spells, misses = [], []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        raw_name = fix(lines[i])
        lv, school, ritual = level_line(lines[i + 1])
        fields, j, last_key = {}, i + 2, None
        while j < end:
            fm = FIELD_RE.match(lines[j])
            if fm:
                w = fm.group(1).lower(); last_key = "casti" if w.startswith("ca") else "range" if w.startswith("ra") else "compo" if w.startswith("co") else "durat"; fields[last_key] = fm.group(2); j += 1
                if last_key == "durat":
                    break
                continue
            if last_key:  # casting time and components wrap onto the next lines
                fields[last_key] += " " + lines[j].strip(); j += 1; continue
            break
        body = paragraphs(lines[j:end])
        up = ""
        for k, para in enumerate(body):
            hm = re.match(r"^At\s*Higher\s*Levels?\s*[.:]\s*(.*)", para, re.I)
            if hm:
                up = " ".join([hm.group(1)] + body[k + 1:]); body = body[:k]; break
        text = fix("\n\n".join(body))
        title = re.sub(r"\s+", " ", raw_name.title().replace("'S ", "'s ").replace("’S ", "'s "))
        prev = [fix(x) for x in lines[max(0, i - 2):i] if re.search(r"[A-Z]{3,}", x)]  # a long name can break across lines
        same = [n for n in canon if names[n]["lvl"] == lv]  # only spells of the same level can match
        sq = lambda x: re.sub(r"[^a-z]", "", x.lower().replace("1", "l").replace("0", "o"))  # scans scatter spaces
        keys = {sq(n): n for n in same}
        hit = difflib.get_close_matches(sq(title), list(keys), n=1, cutoff=0.72)
        match = [keys[hit[0]]] if hit else None
        for k in range(1, len(prev) + 1):
            if match:
                break
            joined = " ".join(prev[-k:] + [raw_name])
            hit = difflib.get_close_matches(sq(joined), list(keys), n=1, cutoff=0.72)
            match = [keys[hit[0]]] if hit else None
        name = match[0] if match else title
        if not match:
            misses.append(raw_name)
        sys.stderr.write("" if not os.environ.get("SPELLS_DEBUG") else "%s <- %s\n" % (name, raw_name))
        dur = canon_dur(fields.get("durat", ""))
        save = None
        sm = re.search(r"\b(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw", text)
        if sm:
            save = ABIL[sm.group(1).lower()]
        kn = names.get(name) or {}
        sp = {"id": kn.get("id") or re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", ""))), "name": name, "lvl": lv, "school": school or "",
              "time": canon_time(fields.get("casti", "1 action")), "range": canon_range(fields.get("range", "")), "comp": canon_comp(fields.get("compo", "")), "dur": dur,
              "conc": dur.lower().startswith("concentration"), "ritual": ritual, "sum": text}
        if up:
            sp["up"] = fix(up)
        if save:
            sp["save"] = save
        if kn.get("classes"):
            sp["classes"] = kn["classes"]
        if kn.get("school") and kn["school"] != sp["school"]:
            sp["school"] = kn["school"]
        if re.search(r"\b(ranged|melee) spell attack\b", text):
            sp["attack"] = re.search(r"\b(ranged|melee) spell attack\b", text).group(1)
        spells.append(sp)
    return spells, misses


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    spells, misses = parse(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    json.dump(spells, sys.stdout, indent=1, ensure_ascii=False)
    sys.stderr.write("%d spells, %d names not matched: %s\n" % (len(spells), len(misses), ", ".join(misses)))
