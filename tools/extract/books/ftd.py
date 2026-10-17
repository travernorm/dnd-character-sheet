"""Fizban's Treasury of Dragons (2014 rules): chromatic, metallic and gem dragonborn,
the Drakewarden ranger and Way of the Ascendant Dragon monk.
Structure and effects are written here; feature text comes from your extracted pages."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import *
from kit import Book

X = Book("ftd", 1, 227, body=8)
ALL = ["str", "dex", "con", "int", "wis", "cha"]
KI = lambda n: {"resource": "ki", "amount": n}


def dragonborn(kind, ancestries, extra, page_title):
    rid = slug(kind + " dragonborn")
    base = [
        F("Ability Score Increase", text="Increase one score by 2 and another by 1, or three scores by 1.",
          effects=[ABIL_CHOICE("asi-plus2", "+2 to one score", ALL, 1, 2), ABIL_CHOICE("asi-plus1", "+1 to another score", ALL, 1, 1)], id=rid + "-asi"),
        F("Languages", text="Common and one other language.", effects=[PROF("language", ["Common"]), CHOICE("languages", "One more language", "language", 1, {"list": ["any"]})], id=rid + "-languages"),
    ]
    feats = [
        F(kind + " Ancestry", text="Choose a %s dragon; it sets your damage type." % kind.lower(), effects=[CHOICE("ancestry", kind + " Ancestry", "option", 1, {"optionSet": slug(kind) + "-ancestries"})], id=rid + "-ancestry"),
        F("Breath Weapon", text="Replace one attack with a 15-ft cone or 5 by 30 ft line: 1d10 of your damage type (2d10 at 5th, 3d10 at 11th, 4d10 at 17th), Dex save DC 8 + Con + proficiency. Proficiency-bonus uses per long rest.",
          effects=[RES("breath-weapon", "Breath Weapon", "prof", "long"), ACT("use-breath-weapon", "Breath Weapon", "special", cost={"resource": "breath-weapon", "amount": 1},
                   damage={"dice": {"1": "1d10", "5": "2d10", "11": "3d10", "17": "4d10"}}, save={"ability": "dex", "dc": "8 + mod.con + prof"})], id=rid + "-breath-weapon"),
        F("Draconic Resistance", text="Resistance to your ancestry's damage type.", id=rid + "-resistance"),
    ] + extra
    X.fill(feats, page_title, span=2)
    e = {"id": rid, "name": kind + " Dragonborn", "size": "Medium", "speed": 30, "features": base + feats}
    if X.locate(page_title):
        e["page"] = X.locate(page_title)
    return e


def ancestry_set(kind, rows):
    return {"id": slug(kind) + "-ancestries", "name": kind + " Ancestry",
            "options": [F(n, text="Damage type: %s." % d, effects=[RESIST(d)], id=slug(kind) + "-" + slug(n)) for n, d in rows]}


def build():
    races = [
        dragonborn("Chromatic", None, [F("Chromatic Warding", 5, "Action: immunity to your ancestry's damage type for 1 minute. Once per long rest.",
                                         [RES("chromatic-warding", "Chromatic Warding", 1, "long"), ACT("use-chromatic-warding", "Chromatic Warding", "action", cost={"resource": "chromatic-warding", "amount": 1})])], "Chromatic Dragonborn"),
        dragonborn("Gem", None, [F("Psionic Mind", text="Speak telepathically with a creature within 30 ft."),
                                 F("Gem Flight", 5, "Bonus action: flying speed equal to your walking speed for 1 minute. Once per long rest.",
                                   [RES("gem-flight", "Gem Flight", 1, "long"), ACT("use-gem-flight", "Gem Flight", "bonus", cost={"resource": "gem-flight", "amount": 1})])], "Gem Dragonborn"),
        dragonborn("Metallic", None, [F("Metallic Breath Weapon", 5, "A second breath, once per long rest: an enervating breath (Con save or incapacitated) or a repulsion breath (Str save or pushed and prone).",
                                        [RES("metallic-breath", "Metallic Breath Weapon", 1, "long"), ACT("use-metallic-breath", "Metallic Breath Weapon", "action", cost={"resource": "metallic-breath", "amount": 1}, save={"ability": "con", "dc": "8 + mod.con + prof"})])], "Metallic Dragonborn"),
    ]
    sets = [
        ancestry_set("Chromatic", [("Black", "acid"), ("Blue", "lightning"), ("Green", "poison"), ("Red", "fire"), ("White", "cold")]),
        ancestry_set("Gem", [("Amethyst", "force"), ("Crystal", "radiant"), ("Emerald", "psychic"), ("Sapphire", "thunder"), ("Topaz", "necrotic")]),
        ancestry_set("Metallic", [("Brass", "fire"), ("Bronze", "lightning"), ("Copper", "acid"), ("Gold", "fire"), ("Silver", "cold")]),
        {"id": "drake-essences", "name": "Drake essence", "options": [F(d.title(), text="Your drake's damage type and resistance: %s." % d, id="drake-" + d) for d in ("acid", "cold", "fire", "lightning", "poison")]},
        {"id": "draconic-dispositions", "name": "Draconic Disciple ancestry", "options": [F(d.title(), text="Your monk features deal %s damage." % d, id="disposition-" + d) for d in ("acid", "cold", "fire", "lightning", "poison")]},
    ]
    subs = [
        X.subclass("ranger", "Drakewarden", [
            F("Draconic Gift", 3, "You learn thaumaturgy and speak Draconic.", [GRANT([("thaumaturgy", 3)], cls="ranger"), PROF("language", ["Draconic"])]),
            F("Drake Companion", 3, "Action: summon a drake companion that obeys you; bonus action to command it. Once per long rest without a slot.",
              [CHOICE("drake-essence", "Drake essence", "option", 1, {"optionSet": "drake-essences"}), RES("drake-companion", "Drake Companion", 1, "long"),
               ACT("summon-drake", "Summon drake", "action", cost={"resource": "drake-companion", "amount": 1}), ACT("command-drake", "Command drake", "bonus")]),
            F("Bond of Fang and Scale", 7, "Your drake grows to Medium and can carry you as a mount; it gains wings and +1d6 damage of its type; you resist its damage type."),
            F("Drake's Breath", 11, "Action: exhale a 30-ft cone of your drake's damage type, 8d6 (Dex save for half; 10d6 at 15th). Once per long rest.",
              [RES("drakes-breath", "Drake's Breath", 1, "long"), ACT("use-drakes-breath", "Drake's Breath", "action", cost={"resource": "drakes-breath", "amount": 1}, damage={"dice": {"11": "8d6", "15": "10d6"}}, save={"ability": "dex", "dc": "spellDC"})]),
            F("Perfected Bond", 15, "Your drake grows to Large and gains a reflexive resistance reaction; its bite deals 1d6 more."),
        ]),
        X.subclass("monk", "Way of the Ascendant Dragon", [
            F("Draconic Disciple", 3, "Change unarmed strike damage to acid, cold, fire, lightning or poison; reroll a failed Cha check (Intimidation or Persuasion) once per long rest; learn Draconic or another language.",
              [CHOICE("draconic-disposition", "Damage type", "option", 1, {"optionSet": "draconic-dispositions"}), PROF("language", ["Draconic"])]),
            F("Breath of the Dragon", 3, "Replace an attack with a 20-ft cone or 30-ft line: two martial arts dice of your type (Dex save for half). Proficiency-bonus uses per long rest, or 2 ki.",
              [RES("breath-of-the-dragon", "Breath of the Dragon", "prof", "long"), ACT("use-breath-of-the-dragon", "Breath of the Dragon", "special", cost={"resource": "breath-of-the-dragon", "amount": 1},
                                                                                         damage={"dice": {"3": "2d4", "5": "2d6", "11": "2d8", "17": "2d10"}}, save={"ability": "dex", "dc": "8 + prof + mod.wis"})]),
            F("Wings Unfurled", 6, "When you use Step of the Wind, gain a flying speed equal to your walking speed until the turn ends. Proficiency-bonus uses per long rest.", [RES("wings-unfurled", "Wings Unfurled", "prof", "long")]),
            F("Aspect of the Wyrm", 11, "Bonus action, 3 ki: a 10-ft aura for 1 minute, frightening (Wis save) or granting resistance to your type.", [ACT("aspect-of-the-wyrm", "Aspect of the Wyrm", "bonus", cost=KI(3))]),
            F("Ascendant Aspect", 17, "Blindsight 10 ft; Breath of the Dragon grows; Aspect of the Wyrm deals damage.", [SENSE("blindsight", 10)]),
        ]),
    ]
    X.report()
    return {"races": races, "subclasses": subs, "optionSets": sets}
