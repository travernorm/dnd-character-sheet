"""Bigby Presents: Glory of the Giants (2023, 2014 rules): Path of the Giant, the giant
backgrounds and feats, its magic items and stat blocks.

The PDF is scanned images, so run tools/extract/ocr_pdf.sh on it first. Structure and
effects are written here; text comes from the OCR'd pages."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import *
from kit import Book
import creatures, items as itemparser

X = Book("bgg", 1, 200, body=6)
GIANT_ABILS = lambda third: ["str", "con", third]


def half(fid, abils):
    return [ABIL_CHOICE(fid + "-ability", "+1 ability score", abils, 1)]


def pb_action(id, name, econ, **kw):
    return [RES(id, name, "prof", "long"), ACT("use-" + id, name, econ, cost={"resource": id, "amount": 1}, **kw)]


def build():
    sub = X.subclass("barbarian", "Path of the Giant", [
        F("Giant Power", 3, "You learn Giant and either druidcraft or thaumaturgy (Wisdom is its ability).",
          [PROF("language", ["Giant"]), CHOICE("giant-power-cantrip", "Cantrip (druidcraft or thaumaturgy)", "spell", 1, {"spells": {"list": "any", "level": 0}})]),
        F("Giant's Havoc", 3, "While raging, your reach grows 5 ft and you can become Large; Crushing Throw adds your Rage damage to thrown weapon hits.",
          [BON("damage.ranged", "col.rageDamage", when="toggle:raging", note="Thrown weapons only")]),
        F("Elemental Cleaver", 6, "Bonus action while raging: infuse a weapon with acid, cold, fire, lightning or thunder; it gains thrown (20/60), returns to you, and deals an extra 1d6 of that type (2d6 at 14th).",
          [ACT("elemental-cleaver", "Elemental Cleaver", "bonus", when="toggle:raging"),
           RIDER("elemental-cleaver", "Elemental Cleaver", damage={"6": "1d6", "14": "2d6"}, damageType="acid, cold, fire, lightning or thunder", when="toggle:raging", requires=["weapon", "hit"])]),
        F("Mighty Impel", 10, "Bonus action while raging: move a Medium or smaller creature within reach up to 30 ft (Strength save if unwilling).",
          [ACT("mighty-impel", "Mighty Impel", "bonus", when="toggle:raging", save={"ability": "str", "dc": "8 + prof + mod.str"})]),
        F("Demiurgic Colossus", 14, "While raging you can become Large or Huge with 10 ft more reach; Elemental Cleaver deals 2d6 and Mighty Impel can move Large creatures."),
    ])
    feats = [
        ("Strike of the Giants", "Proficiency with a martial weapon", "Choose a giant; once per turn when you hit with a melee or thrown weapon, add its effect. Proficiency-bonus uses per long rest.",
         [CHOICE("giant-strike", "Giant", "option", 1, {"optionSet": "strike-of-the-giants"}), RES("strike-of-the-giants", "Strike of the Giants", "prof", "long", color="gold")]),
        ("Ember of the Fire Giant", "4th level, Strike of the Giants (fire)", "+1 Str, Con or Wis; resistance to fire; replace an attack with Searing Ignition: teleport 30 ft and burn nearby creatures (1d8 + prof fire, Dex save). Proficiency-bonus uses per long rest.",
         half("ember", GIANT_ABILS("wis")) + [RESIST("fire")] + pb_action("searing-ignition", "Searing Ignition", "special", damage={"dice": "1d8 + prof", "type": "fire"}, save={"ability": "dex", "dc": "8 + prof + mod.con"})),
        ("Fury of the Frost Giant", "4th level, Strike of the Giants (frost)", "+1 Str, Con or Wis; resistance to cold; reaction when hit by a creature within 30 ft: 1d8 + prof cold and speed 0 (Con save). Proficiency-bonus uses per long rest.",
         half("fury", GIANT_ABILS("wis")) + [RESIST("cold")] + pb_action("frigid-retaliation", "Frigid Retaliation", "reaction", damage={"dice": "1d8 + prof", "type": "cold"}, save={"ability": "con", "dc": "8 + prof + mod.con"})),
        ("Guile of the Cloud Giant", "4th level, Strike of the Giants (cloud)", "+1 Str, Con or Cha; reaction when hit: resistance to the damage, then turn invisible and teleport 30 ft. Proficiency-bonus uses per long rest.",
         half("guile", GIANT_ABILS("cha")) + pb_action("cloudy-escape", "Cloudy Escape", "reaction")),
        ("Keenness of the Stone Giant", "4th level, Strike of the Giants (stone)", "+1 Str, Con or Wis; darkvision 60 ft; bonus action Stone Throw (1d10 + Con force, ranged spell-like attack, knock prone on a failed Str save). Proficiency-bonus uses per long rest.",
         half("keenness", GIANT_ABILS("wis")) + [SENSE("darkvision", 60)] + pb_action("stone-throw", "Stone Throw", "bonus", damage={"dice": "1d10 + mod.con", "type": "force"})),
        ("Soul of the Storm Giant", "4th level, Strike of the Giants (storm)", "+1 Str, Con or Wis; bonus action Maelstrom Aura for 1 minute: resistance to lightning and thunder, and enemies near you have disadvantage on attacks. Proficiency-bonus uses per long rest.",
         half("soul", GIANT_ABILS("wis")) + pb_action("maelstrom-aura", "Maelstrom Aura", "bonus")),
        ("Vigor of the Hill Giant", "4th level, Strike of the Giants (hill)", "+1 Str, Con or Wis; can't be knocked prone or moved against your will by Large or smaller creatures; add your Con modifier again when you spend Hit Dice or eat to heal.",
         half("vigor", GIANT_ABILS("wis"))),
        ("Rune Shaper", None, "Learn comprehend languages; inscribe runes after a long rest that each let you cast a spell once without a slot (more runes as your proficiency grows).",
         [GRANT([{"id": "comprehend-languages", "uses": 1, "recharge": "long", "noSlot": True}], ability="int"), CHOICE("rune-shaper-runes", "Runes known", "text", 1)]),
    ]
    fobjs = [F(n) for n, _, _, _ in feats]
    X.fill(fobjs, "Feats", span=8)
    feat_out = []
    for (name, pre, summary, fx), f in zip(feats, fobjs):
        e = {"id": slug(name), "name": name, "text": f.get("text") or summary, "effects": fx}
        if pre:
            e["prerequisite"] = {"formula": "1", "text": pre}
        feat_out.append(e)
    def bg(name, skills, feat_id, tools=None, langs=1, giant=True):
        fx = [PROF("skill", skills), CHOICE("languages", "Languages", "language", langs, {"list": ["any"]})]
        if giant:
            fx.append(PROF("language", ["Giant"]))
        if tools:
            fx.append(CHOICE("tool", "Tool proficiency", "tool", 1, {"list": tools}))
        feats = [F("Proficiencies", text="Skills: %s." % ", ".join(skills), effects=fx, id=slug(name) + "-proficiencies"),
                 F("Feat", text="You gain the %s feat." % feat_id.replace("-", " ").title(), effects=[CHOICE("background-feat", "Background feat", "feat", 1, {"ids": [feat_id]})], id=slug(name) + "-feat")]
        X.fill(feats[1:], name, span=2)
        return {"id": slug(name), "name": name, "features": feats}
    backgrounds = [bg("Giant Foundling", ["intimidation", "survival"], "strike-of-the-giants"),
                   bg("Rune Carver", ["history", "perception"], "rune-shaper", tools=["One type of artisan's tools"], giant=False)]
    strikes = [F(n + " Strike", text=t, effects=[RIDER(slug(n) + "-strike", n + " Strike", damage=d, damageType=dt, cost={"resource": "strike-of-the-giants", "amount": 1}, oncePer="turn", requires=["weapon", "hit"])] if d else
               [RIDER(slug(n) + "-strike", n + " Strike", cost={"resource": "strike-of-the-giants", "amount": 1}, oncePer="turn", requires=["weapon", "hit"])], id="strike-" + slug(n))
               for n, t, d, dt in [("Cloud", "The target makes a Wis save or you're invisible to it until your next turn.", None, ""),
                                   ("Fire", "An extra 1d10 fire damage.", "1d10", "fire"),
                                   ("Frost", "An extra 1d6 cold damage; Con save or speed 0 until your next turn.", "1d6", "cold"),
                                   ("Hill", "Str save or knocked prone.", None, ""),
                                   ("Stone", "An extra 1d8 force damage; Str save or pushed 10 ft.", "1d8", "force"),
                                   ("Storm", "An extra 1d6 thunder damage; Con save or disadvantage on checks and attacks until your next turn.", "1d6", "thunder")]]
    cs = creatures.parse("bgg", 1, 200)
    it = itemparser.parse("bgg", 1, 200)
    # Proper names the OCR cleanup splits because they aren't dictionary words.
    fix = {"Maw of Yee Nog Hu": "Maw of Yeenoghu", "Re Gi Saur": "Regisaur", "Scion of St Ron Maus": "Scion of Stronmaus",
           "Big by's Beneficent Bracelet": "Bigby's Beneficent Bracelet", "Glow rune Pigment": "Glowrune Pigment", "Thunder buss": "Thunderbuss"}
    for e in cs + it:
        if e["name"] in fix:
            e["name"] = fix[e["name"]]; e["id"] = slug(e["name"])
    X.report()
    print("creatures: %d (%d with all six scores); items: %d" % (len(cs), sum("abilities" in c for c in cs), len(it)))
    return {"subclasses": [sub], "feats": feat_out, "backgrounds": backgrounds,
            "optionSets": [{"id": "strike-of-the-giants", "name": "Strike of the Giants", "options": strikes}],
            "creatures": sorted(cs, key=lambda c: c["name"]), "items": it}
