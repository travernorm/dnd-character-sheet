"""Clean up OCR slips in scanned book text.

A word that isn't in the dictionary is retried with the swaps these scans make
(l for t or I, e for c, o for n, rn for m, 0 for o...), and glued words like
"ofyou" are split. Uses the system word list plus the game words below.
"""
import functools, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# A running footer on its own line: "PART 1 | CLASSES", "56 CHAPTER 1 | CHARACTER OPTIONS", "APPENDIX B: NONPLAYER
# CHARACTERS", including scans that read the digit or the bar as I ("PART I I CLASSES").
FOOTER_LINE = re.compile(r"^(\d{1,3}\s+)?(CHAPTER\s*[\dIl]{1,2}|PART\s*[\dIl]{1,2}|APPENDIX\s*[A-Z]{1,2})\b(\s*[|I/:]?\s*[A-Z][A-Z ,'’&-]*)?(\s*\d{1,3})?$")


def page_file(book, p):
    """packs/.text/<book>/pNNNN.txt. PACK_TEXT="xge=xge-ocr,phb=phb-ocr" reads another folder
    instead, to compare a re-extraction with the current text before replacing it."""
    alt = dict(x.split("=", 1) for x in os.environ.get("PACK_TEXT", "").split(",") if "=" in x)
    return os.path.join(ROOT, "packs", ".text", alt.get(book, book), "p%04d.txt" % p)

GAME_WORDS = """
cantrip cantrips spellcasting spellcaster spellcasters ritual rituals concentration darkvision blindsight tremorsense truesight
d4 d6 d8 d10 d12 d20 1d4 1d6 1d8 1d10 1d12 1d20 2d6 hp ac dc gp sp cp pp ep str dex con int wis cha
abjuration conjuration divination enchantment evocation illusion necromancy transmutation
warlock warlocks sorcerer sorcerers paladin paladins ranger rangers druid druids cleric clerics bard bards wizard wizards fighter fighters
rogue rogues monk monks barbarian barbarians artificer artificers multiclass multiclassing subclass subclasses
humanoid humanoids undead fiend fiends fey celestial celestials elemental elementals aberration aberrations construct constructs ooze oozes
dragonborn tiefling tieflings gnome gnomes halfling halflings dwarf dwarves dwarven elf elves elven half-elf half-orc kenku tabaxi firbolg aasimar genasi goliath
ki psionic infusion infusions invocation invocations metamagic eldritch arcana feywild shadowfell
multiattack shapechanger teleport echolocation flyby antimagic goblinoid goblinoids coven covens
longsword shortsword greatsword greataxe greatclub battleaxe warhammer morningstar shortbow longbow handaxe
""".split()


# Preferred when a scan slip could become more than one real word ("leet" is feet, not teet).
COMMON = set("""
a an and any are as at be been but by can cannot can't creature creatures damage day days each end ends every feet foot for from
hit points if you on a of the to the
gain half has have hit hour hours if in into is it its level light minute minutes more must no not of on one only or other point
points range round rounds save saving see slot spell spells take takes target targets that the their them then there they this
throw time to turn until up upon use when which while who with within you your action actions attack bonus reaction ability check
""".split())


@functools.lru_cache(maxsize=None)
def words():
    w = set(GAME_WORDS)
    for path in ("/usr/share/dict/words", "/usr/share/dict/web2"):
        if os.path.exists(path):
            with open(path) as f:
                w.update(x.strip().lower() for x in f if x.strip())
            break
    return w


SWAPS = [("l", "t"), ("l", "i"), ("i", "l"), ("e", "c"), ("c", "e"), ("o", "n"), ("n", "o"), ("rn", "m"), ("m", "rn"), ("0", "o"),
         ("1", "l"), ("1", "i"), ("5", "s"), ("ii", "ll"), ("h", "b"), ("a", "o"), ("o", "a"), ("u", "n"), ("tl", "ti"), ("f", "t")]
SHORT = {"a", "an", "of", "to", "if", "by", "or", "at", "in", "on", "as", "is", "it", "be", "the", "and", "you", "your"}


CONTRACTIONS = {"can't", "don't", "doesn't", "isn't", "aren't", "won't", "wasn't", "weren't", "hasn't", "haven't", "didn't", "couldn't", "wouldn't", "shouldn't", "it's", "you're", "you've", "they're"}


@functools.lru_cache(maxsize=None)
def known(w):
    """In the word list, allowing plurals, -ed, -ing, -er, -ly and possessives."""
    w = w.lower().strip("'")
    if w in CONTRACTIONS or w in COMMON or w in words():
        return True
    if w.endswith("'s"):
        return known(w[:-2])
    W = words()
    for suf, add in (("s", ""), ("es", ""), ("ies", "y"), ("ed", ""), ("ed", "e"), ("d", ""), ("ing", ""), ("ing", "e"), ("er", ""), ("ers", ""), ("ly", ""), ("ness", ""), ("al", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            base = w[:-len(suf)] + add
            if base in W or base in COMMON or (len(base) > 3 and base[-1] == base[-2] and base[:-1] in W):
                return True
    return False


def segment(low):
    """Split glued words ("onasuccessful" -> "on a successful"), fewest pieces first."""
    best = {0: []}
    for i in range(len(low)):
        if i not in best:
            continue
        for j in range(i + 1, len(low) + 1):
            piece = low[i:j]
            if (len(piece) > 1 or piece in ("a", "i")) and known(piece):
                cand = best[i] + [piece]
                if j not in best or len(cand) < len(best[j]):
                    best[j] = cand
    out = best.get(len(low))
    return out if out and 1 < len(out) <= 9 else None


@functools.lru_cache(maxsize=None)
def fix_word(w):
    if not w.isalpha() and not re.fullmatch(r"[A-Za-z0-9;']+", w):
        return w
    core = w.replace(";", "i")
    if known(core):
        return core
    if re.fullmatch(r"[Vv]ou(r|rs)?|[Vv]ou'(re|ve)", core):
        return "Y" + core[1:] if core[0] == "V" else "y" + core[1:]
    if len(core) < 3 or re.fullmatch(r"\d+[a-z]{0,2}|\d*d\d+", core.lower()):
        return w
    low = core.lower()
    cands = [low]
    for a, b in SWAPS:  # one swap, then two
        for m in re.finditer(re.escape(a), low):
            cands.append(low[:m.start()] + b + low[m.end():])
    for c in list(cands[1:]):
        for a, b in SWAPS:
            for m in re.finditer(re.escape(a), c):
                cands.append(c[:m.start()] + b + c[m.end():])
    for c in sorted(cands, key=lambda c: c not in COMMON):
        if c.isalpha() and known(c):
            return restore_case(core, c)
    for c in [low, re.sub(r"^v", "y", low), re.sub(r"^l", "i", low)] + cands[1:]:  # glued words: "voucan", "lfyou", "onasuccessful"
        parts = segment(c)
        if parts:
            return restore_case(core, parts[0]) + " " + " ".join(parts[1:])
    return w


def restore_case(orig, new):
    if orig[:1].isupper() and orig[1:2].islower():
        return new[:1].upper() + new[1:]
    if orig.isupper() and len(orig) > 1:
        return new.upper()
    return new


def clean(text):
    text = re.sub(r"\b[lI][O0]{1,2}(?=[- ]?(foot|feet|ft|mile))", lambda m: "1" + "0" * (len(m.group(0)) - 1), text)  # IO-foot, lOO-foot
    text = re.sub(r"\b(\d+)\s*fe[e]?[ltI!]\b", r"\1 feet", text)
    text = re.sub(r"\bSe\]f\b", "Self", text)
    lev = r"[lI1i!/]\s?e\s?[vy]\s?e\s?[lI1i]"
    text = re.sub(r"\b([0-9]{1,2}|[lIi])\s?(st|nd|rd|th|lh|tb)\s*-?\s*" + lev + r"\b", lambda m: (m.group(1) if m.group(1).isdigit() else "1") + {"lh": "th", "tb": "th"}.get(m.group(2), m.group(2)) + " level", text)
    text = re.sub(r"\b([0-9]{1,2}|[lIi])\s?(st|nd|rd|th)\s*-\s*(?=level)", lambda m: (m.group(1) if m.group(1).isdigit() else "1") + m.group(2) + "-", text)
    text = re.sub(r"\b" + lev + r"\b", "level", text)
    text = re.sub(r"\b(At|at|of|by|to|In|in)(\d)", r"\1 \2", text)  # At2nd
    text = re.sub(r"(?<=[a-z]),(?=[A-Za-z])", ", ", text)  # level,you
    text = re.sub(r"\bVou\b", "You", text)
    text = re.sub(r"\bl(?=n[a-z]{3,})", "I", text)  # lnstantaneous, lntelligence
    text = re.sub(r"\b([Il]|1)d(\d)", r"1d\2", text)  # Id6
    return re.sub(r"[A-Za-z0-9;']+", lambda m: fix_word(m.group(0)), text)
