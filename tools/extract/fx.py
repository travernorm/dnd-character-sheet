"""Small builders for content-pack entries and effects (docs/data-formats.md)."""
import re


def slug(t):
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", t.lower().replace("'", "").replace("’", "")))


def F(name, level=None, text="", effects=None, id=None):
    f = {"id": id or slug(name), "name": name}
    if level is not None:
        f["level"] = level
    if text:
        f["text"] = text
    if effects:
        f["effects"] = effects
    return f


def RES(id, name, mx, rec, **kw): return dict({"type": "resource", "id": id, "name": name, "max": mx, "recharge": rec}, **kw)
def ACT(id, name, econ, **kw): return dict({"type": "action", "id": id, "name": name, "econ": econ}, **kw)
def BON(target, value, **kw): return dict({"type": "bonus", "target": target, "value": value}, **kw)
def SET(target, value, mode="max", **kw): return dict({"type": "set", "target": target, "value": value, "mode": mode}, **kw)
def PROF(kind, values, **kw): return dict({"type": "proficiency", "kind": kind, "values": values}, **kw)
def EXP(values, kind="skill"): return {"type": "expertise", "kind": kind, "values": values}
def ASC(ab, n, mx=None):
    e = {"type": "abilityScore", "ability": ab, "add": n}
    if mx:
        e["max"] = mx
    return e
def CHOICE(id, name, kind, choose=1, frm=None, **kw):
    d = {"type": "choice", "id": id, "name": name, "kind": kind, "choose": choose}
    if frm:
        d["from"] = frm
    d.update(kw)
    return d
def REM(on, text): return {"type": "reminder", "on": on, "text": text}
def ADV(on, **kw): return dict({"type": "advantage", "on": on}, **kw)
def RESIST(*types, **kw): return dict({"type": "resistance", "damage": list(types)}, **kw)
def SENSE(sense, rng): return {"type": "sense", "sense": sense, "range": rng}
def SPEED(mode, value): return {"type": "speed", "mode": mode, "value": value}
def RIDER(id, name, **kw): return dict({"type": "attackRider", "id": id, "name": name}, **kw)
def AC(formula, when=None, shield=True):
    e = {"type": "acFormula", "formula": formula, "allowShield": shield}
    if when:
        e["when"] = when
    return e
def GRANT(spells, cls=None, always=True, ability=None):
    """spells: list of (id, minLevel) or dicts."""
    e = {"type": "grantSpells", "alwaysPrepared": always, "countsAgainst": False,
         "spells": [s if isinstance(s, dict) else {"id": s[0], "minLevel": s[1]} for s in spells]}
    if cls:
        e["class"] = cls
    if ability:
        e["ability"] = ability
    return e
def ABIL_CHOICE(id, name, abilities, n=1, add=1):
    return CHOICE(id, name, "ability", n, {"abilities": abilities, "add": add})
