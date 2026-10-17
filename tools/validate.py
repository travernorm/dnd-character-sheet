#!/usr/bin/env python3
"""Check content packs and character files against the version 2 formats.

Checks each file against data/schema/*.json, then checks references the schema can't
see: col.* columns, resource and option-set ids, choice keys, formula words.

Usage: python3 tools/validate.py <file.json> [more files...]
       Character files are checked against every pack given on the same command line.
Needs: pip3 install --user jsonschema
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(ROOT, "data", "schema")
FORMULA_WORDS = re.compile(r"^(mod|score)\.(str|dex|con|int|wis|cha)$|^(prof|level|classLevel|spellMod|spellDC|spellAttack|min|max|floor|ceil|and|or)$|^level\.[a-z0-9-]+$|^col\.[A-Za-z0-9]+$|^\d*d\d+$")


def load_validators():
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError:
        sys.exit("Needs jsonschema: pip3 install --user jsonschema")
    schemas = {}
    for name in ("content-pack", "character"):
        with open(os.path.join(SCHEMA_DIR, name + ".schema.json")) as f:
            schemas[name] = json.load(f)
    reg = Registry().with_resources([(s["$id"], Resource.from_contents(s)) for s in schemas.values()])
    return {k: jsonschema.Draft202012Validator(v, registry=reg) for k, v in schemas.items()}


def entries(coll):
    if isinstance(coll, dict):
        return [dict(v, id=v.get("id", k)) for k, v in coll.items() if isinstance(v, dict)]
    return coll or []


def slug(t):
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", str(t).lower().replace("'", "").replace("’", "")))


def formula_words(v):
    if isinstance(v, (int, float)) or v is None:
        return []
    if isinstance(v, dict):
        return [w for x in v.values() if x != v.get("by") for w in formula_words(x)]
    return re.findall(r"[A-Za-z][A-Za-z0-9.\-]*", re.sub(r"\b\d*d\d+\b", "", str(v)))


class Index:
    """Everything the loaded packs define, for reference checks."""
    def __init__(self):
        self.ids = {k: set() for k in ("classes", "subclasses", "races", "backgrounds", "feats", "optionSets", "spells", "items", "creatures")}
        self.resources, self.toggles, self.choices = {"pact"}, set(), set()  # the app makes the pact-slot resource itself
        self.columns = {}

    def add_pack(self, pack):
        for k in self.ids:
            if k == "subclasses" and isinstance(pack.get(k), dict):
                continue
            for e in entries(pack.get(k)):
                self.ids[k].add(e.get("id") or slug(e.get("name", "")))
        for c in entries(pack.get("classes")):
            self.columns[c.get("id") or slug(c["name"])] = set((c.get("table") or {}).keys())
        for owner, feats in owners(pack):
            for f in feats:
                for e in f.get("effects") or []:
                    if e.get("type") == "resource":
                        self.resources.add(e["id"])
                    if e.get("type") == "toggle":
                        self.toggles.add(e["id"])
                    if e.get("type") in ("choice", "asi"):
                        self.choices.add(owner + "/" + e["id"])


def owners(pack):
    """(ownerId, features) for everything in a pack that holds features."""
    out = []
    for k in ("classes", "races", "backgrounds", "feats", "items"):
        for e in entries(pack.get(k)):
            oid = e.get("id") or slug(e.get("name", ""))
            feats = list(e.get("features") or [])
            if e.get("effects"):
                feats.append({"name": e["name"], "effects": e["effects"]})
            out.append((oid, feats))
            for sr in e.get("subraces") or []:
                out.append((sr.get("id") or slug(sr["name"]), sr.get("features") or []))
    if isinstance(pack.get("subclasses"), list):
        for e in pack["subclasses"]:
            feats = list(e.get("features") or [])
            if e.get("spells"):
                feats.append({"name": "spells", "effects": [e["spells"]]})
            out.append((e.get("id") or slug(e["name"]), feats))
    for s in entries(pack.get("optionSets")):
        for o in s.get("options") or []:
            out.append((o.get("id") or slug(o["name"]), [o]))
    for s in entries(pack.get("spells")):
        if s.get("effects"):
            out.append((s.get("id") or slug(s["name"]), [{"name": s["name"], "effects": s["effects"]}]))
    return out


def check_pack(pack, idx, problems):
    class_of = {}
    for c in entries(pack.get("classes")):
        class_of[c.get("id") or slug(c["name"])] = c.get("id") or slug(c["name"])
    if isinstance(pack.get("subclasses"), list):
        for s in pack["subclasses"]:
            class_of[s.get("id") or slug(s["name"])] = s.get("class")
            if s.get("class") not in idx.ids["classes"]:
                problems.append("subclass %s: class '%s' isn't in any loaded pack" % (s.get("id"), s.get("class")))
    for c in entries(pack.get("classes")):
        for f in c.get("features") or []:
            if "level" not in f:
                problems.append("class %s: feature '%s' has no level" % (c.get("id"), f.get("name")))
    for owner, feats in owners(pack):
        cls = class_of.get(owner)
        for f in feats:
            for e in f.get("effects") or []:
                where = "%s/%s (%s)" % (owner, f.get("id") or slug(f.get("name", "")), e.get("type"))
                for key in ("max", "value", "roll", "heal", "tempHp", "damage", "choose", "cantrips", "known", "prepared", "die", "formula"):
                    v = e.get(key)
                    if isinstance(v, dict) and "dice" in v:
                        v = v["dice"]
                    if isinstance(v, list) or (e.get("type") == "speed" and v == "walk"):
                        continue
                    for w in formula_words(v):
                        if not FORMULA_WORDS.match(w):
                            problems.append("%s: unknown formula word '%s' in %s" % (where, w, key))
                        elif w.startswith("col."):
                            col = w[4:]
                            if cls is None:
                                problems.append("%s: col.%s used outside a class or subclass" % (where, col))
                            elif col not in idx.columns.get(cls, set()):
                                problems.append("%s: class '%s' has no table column '%s'" % (where, cls, col))
                cost = e.get("cost") or {}
                if "resource" in cost and cost["resource"] not in idx.resources:
                    problems.append("%s: cost uses unknown resource '%s'" % (where, cost["resource"]))
                gain = e.get("gain") or {}
                if "resource" in gain and gain["resource"] not in idx.resources:
                    problems.append("%s: gain uses unknown resource '%s'" % (where, gain["resource"]))
                if e.get("type") == "resourceMod" and e["resource"] not in idx.resources:
                    problems.append("%s: unknown resource '%s'" % (where, e["resource"]))
                if e.get("toggle") and e["toggle"] not in idx.toggles:
                    problems.append("%s: unknown toggle '%s'" % (where, e["toggle"]))
                for cond in re.findall(r"toggle:([a-z0-9-]+)", e.get("when") or ""):
                    if cond not in idx.toggles:
                        problems.append("%s: when uses unknown toggle '%s'" % (where, cond))
                fr = e.get("from") or {}
                if "optionSet" in fr and fr["optionSet"] not in idx.ids["optionSets"]:
                    problems.append("%s: unknown option set '%s'" % (where, fr["optionSet"]))
                if e.get("type") == "grantSpells":
                    for s in e.get("spells") or []:
                        if s["id"] not in idx.ids["spells"]:
                            problems.append("%s: spell '%s' isn't in any loaded pack" % (where, s["id"]))


def check_character(ch, idx, problems, warnings):
    ch = ch.get("character", ch)
    custom_spells = {s["id"] for s in ch.get("customSpells") or []}
    for k in ch.get("classes") or []:
        if k["class"] not in idx.ids["classes"]:
            warnings.append("class '%s' isn't in any loaded pack" % k["class"])
        if k.get("subclass") and k["subclass"] not in idx.ids["subclasses"]:
            warnings.append("subclass '%s' isn't in any loaded pack" % k["subclass"])
    total = sum(k["level"] for k in ch.get("classes") or [])
    if ch.get("levelHistory") and len(ch["levelHistory"]) != total:
        problems.append("levelHistory has %d entries but the class levels add up to %d" % (len(ch["levelHistory"]), total))
    rolls = (ch.get("hp") or {}).get("rolls")
    if rolls and len(rolls) != total:
        problems.append("hp.rolls has %d entries but the character is level %d" % (len(rolls), total))
    for field, coll in (("race", "races"), ("background", "backgrounds")):
        v = ch.get(field)
        if v and v not in idx.ids[coll]:
            warnings.append("%s '%s' isn't in any loaded pack (shown as text only)" % (field, v))
    for cls, lists in (ch.get("spells") or {}).items():
        for lst, ids in lists.items():
            for s in ids:
                if s not in idx.ids["spells"] and s not in custom_spells:
                    warnings.append("spells.%s.%s: '%s' isn't in any loaded pack or customSpells" % (cls, lst, s))
        book, prep = set(lists.get("spellbook") or []), lists.get("prepared") or []
        if book:
            for s in prep:
                if s not in book:
                    problems.append("spells.%s.prepared: '%s' isn't in the spellbook" % (cls, s))
    for inv in ch.get("inventory") or []:
        if inv.get("item") and inv["item"] not in idx.ids["items"]:
            warnings.append("inventory: item '%s' isn't in any loaded pack" % inv["item"])
        if not inv.get("item") and not inv.get("name"):
            problems.append("inventory: an entry has neither item nor name")
    for comp in ch.get("companions") or []:
        if comp.get("creature") and comp["creature"] not in idx.ids["creatures"]:
            warnings.append("companion %s: creature '%s' isn't in any loaded pack" % (comp.get("name"), comp["creature"]))
    owners_in_use = {k["class"] for k in ch.get("classes") or []} | {k.get("subclass") for k in ch.get("classes") or []}
    owners_in_use |= {ch.get("race"), ch.get("subrace"), ch.get("background")}
    for key in ch.get("choices") or {}:
        owner, cid = key.split("/", 1)
        if cid == "skills" and owner in idx.ids["classes"]:
            continue
        if key not in idx.choices:
            (problems if owner in owners_in_use and owner in set().union(*idx.ids.values()) else warnings).append(
                "choices: '%s' doesn't match any choice in the loaded packs" % key)


def main(paths):
    if not paths:
        sys.exit(__doc__)
    v = load_validators()
    docs = []
    for p in paths:
        with open(p) as f:
            d = json.load(f)
        kind = "content-pack" if d.get("format") == "dnd-content-pack" else "character"
        docs.append((p, kind, d))
    idx = Index()
    # The app always loads the SRD spell and item lists, so their ids count as defined.
    for coll, name in (("spells", "srd-spells.json"), ("items", "srd-items.json")):
        with open(os.path.join(ROOT, "data", name)) as f:
            srd = json.load(f)
        idx.ids[coll] |= set(srd) if isinstance(srd, dict) else {slug(x["name"]) for x in srd}
    for p, kind, d in docs:
        if kind == "content-pack":
            idx.add_pack(d)
    bad = False
    for p, kind, d in docs:
        problems, warnings = [], []
        if kind == "character" and d.get("character", d).get("schema") != 2:
            print("skip %s (version 1 character; the app converts it on load)" % os.path.relpath(p))
            continue
        for err in sorted(v[kind].iter_errors(d), key=lambda e: list(e.absolute_path)):
            # oneOf/anyOf failures hide the real cause in err.context; report the deepest one.
            while err.context:
                err = max(err.context, key=lambda c: len(c.absolute_path))
            problems.append("schema: %s at /%s" % (err.message[:200], "/".join(map(str, err.absolute_path))))
        try:
            if kind == "content-pack":
                check_pack(d, idx, problems)
            else:
                check_character(d, idx, problems, warnings)
        except Exception as ex:  # malformed data the schema already flagged
            if not problems:
                problems.append("couldn't check references: %r" % ex)
        print("%s %s (%s)" % ("FAIL" if problems else "ok  ", os.path.relpath(p), kind))
        for m in problems:
            print("   error:", m)
        for m in warnings:
            print("   warn: ", m)
        bad = bad or bool(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
