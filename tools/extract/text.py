"""Find a heading in a book's extracted pages and return the text under it.

Headings in the scans are their own short lines ("Spell Thief", "COLLEGE OF VALOR").
section() takes the paragraphs after the heading until the next heading it's told
about, a line in capitals, or a length limit.
"""
import difflib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ocr

_cache = {}


def lines(book, first, last):
    key = (book, first, last)
    if key not in _cache:
        out = []
        for p in range(first, last + 1):
            f = ocr.page_file(book, p)
            if os.path.exists(f):
                for ln in open(f, encoding="utf-8").read().split("\n"):
                    s = ln.strip()
                    if not s or re.fullmatch(r"\d{1,3}", s) or re.match(r"^(\d{1,3}\s+)?(CHAPTER \d|PART \d)", s, re.I) or ocr.FOOTER_LINE.match(s):
                        continue
                    out.append((p, s))
        _cache[key] = out
    return _cache[key]


def norm(t):
    return re.sub(r"[^a-z]", "", t.lower().replace("1", "l").replace("0", "o"))


def is_heading(s, names):
    if re.match(r"^\s*\d{1,2}\s*(st|nd|rd|th)\b", s):  # a row of a level table ("10th Zealous Presence")
        return False
    n = norm(s)
    return bool(n) and len(s) <= 48 and any(n == norm(x) or difflib.SequenceMatcher(None, n, norm(x)).ratio() > 0.86 for x in names)


def run_in(s, names):
    """For a line like 'Darkvision. Accustomed to ...', the heading it starts with and the rest."""
    m = re.match(r"^([A-Z][^\W\d_]?[^\W\d_' :,-]*(?:[ '’:,-]+[^\W\d_]+){0,7})[.:]\s+(.*)$", s)
    if m and is_heading(m.group(1), names):
        return m.group(2)
    return None


def section(book, first, last, heading, stops=(), limit=2400, after=None):
    """Text under `heading`; `after` is a heading that should come first (the subclass title).
    Scanned columns sometimes put a feature above its title, so a heading that appears only
    once in the pages is also accepted from anywhere."""
    t = _section(book, first, last, heading, stops, limit, after)
    if t is None and after:
        ls = lines(book, first, last)
        hits = [i for i, (_, s) in enumerate(ls) if is_heading(s, [heading]) or run_in(s, [heading]) is not None]
        if len(hits) == 1:
            t = _section(book, first, last, heading, stops, limit, None)
    return t


def _section(book, first, last, heading, stops=(), limit=2400, after=None):
    ls = lines(book, first, last)
    start = 0
    if after:
        for i, (_, s) in enumerate(ls):
            if is_heading(s, [after]):
                start = i + 1
                break
    hits = [i for i in range(start, len(ls)) if is_heading(ls[i][1], [heading]) or run_in(ls[i][1], [heading]) is not None]
    runin = [i for i in hits if not is_heading(ls[i][1], [heading]) and (i == 0 or not re.search(r"[a-z,;]$", ls[i - 1][1]))]  # not a wrapped sentence ("... ki point for / Hand of Harm. You")
    caps = [i for i in hits if i not in runin and ls[i][1].isupper()]
    hits = runin + caps + [i for i in hits if i not in runin and i not in caps]  # "Draconic Ancestry. You ..." or the heading, before a table row or title
    for i in hits:
        rest = None
        if not is_heading(ls[i][1], [heading]):
            rest = run_in(ls[i][1], [heading])
        body = [rest] if rest else []
        for k in range(i + 1, len(ls)):
            s = ls[k][1]
            if body and capitals(s):
                after = next((x for _, x in ls[k + 1:k + 4] if not capitals(x)), "")
                if after.startswith("•") or (after[:1].islower() and not re.search(r"[.!?:]$", body[-1])):
                    continue  # a caption in capitals between a sentence and its next words, or between list items
            if is_heading(s, list(stops)) or run_in(s, list(stops)) is not None or (s.isupper() and len(s) > 4 and not re.search(r"\d", s)):
                break
            if body and new_heading(s, body[-1]):  # the next section ("Arcane Shot Options", a table title, lore)
                break
            if body and re.match(r"^\s*(d\s?\d{1,3}\b|\d{1,3}\s*[-–]\s*\d{1,3}\b)", s):
                break  # a table row ("01-02 Roll on this table...")
            letters = [c for c in s if c.isalpha()]
            if body and len(letters) >= 6 and sum(c.isupper() for c in letters) >= 0.75 * len(letters) and not re.search(r"\d{2,}", s):
                break  # a heading in capitals the scan garbled ("A REA ne S H OT 0PT10 N S")
            body.append(s)
            if sum(len(x) for x in body) > limit:
                break
        text = trim(strip_footers(join(body)), limit)
        if len(text) > 40 or (rest and len(text) > 20):  # a short hit is a table entry, unless it's a run-in ("Necrotic Resistance. You ...")
            return ocr.clean(text).strip()
    return None


def capitals(s):
    letters = [c for c in s if c.isalpha()]
    return len(letters) >= 4 and sum(c.isupper() for c in letters) >= 0.75 * len(letters)


FOOTER = re.compile(r"\s*\b\d{0,3}\s*(?i:chapter|part|appendix)\s*\d*\s*[|I/\\:]\s*[A-Z][A-Z,'’&-]*(?: [A-Z][A-Z,'’&-]*)*\b(?:\s*\d{1,3}\b)?")


SMALL = {"of", "the", "and", "in", "with", "a", "an", "to", "or", "on", "from", "for"}


def new_heading(s, prev):
    """A short title-case line after a finished sentence: a heading the caller didn't list."""
    words = s.strip().split()
    if not (0 < len(words) <= 6 and len(s) < 40 and re.search(r"[.!?:]$", prev.strip())):
        return False
    if re.search(r"[.,;:]$", s.strip()) or not words[0][:1].isupper():
        return False
    return all(w[:1].isupper() or w.lower() in SMALL or not w[:1].isalpha() for w in words)


def trim(t, limit):
    """Past the limit, end at the last paragraph break so a run-on doesn't keep the next section."""
    if len(t) <= limit * 0.66:
        return t
    cut = t.rfind("\n\n", 0, int(limit * 0.66))
    return t[:cut].strip() if cut > 200 else t


def strip_footers(t):
    """Page footers that land mid-text: '24 CHAPTER 1 | FANTASTICAL RACES'."""
    return re.sub(r"\s{2,}", " ", FOOTER.sub(" ", t)).strip()


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
