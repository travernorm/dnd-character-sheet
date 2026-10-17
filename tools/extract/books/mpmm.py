"""Mordenkainen Presents: Monsters of the Multiverse (2022, 2014 rules): the 33 races of chapter 1.

Every race gets the book's flexible ability increase (+2 and +1, or +1 to three scores),
Common plus one language, and its traits with effects. Trait text is looked up in your
extracted pages (packs/.text/mpmm); the summary is kept when it isn't found.
Racial spells use Charisma here; the book lets you pick Int, Wis or Cha.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import *
import text as T

B, PAGES = "mpmm", (5, 37)
ALL = ["str", "dex", "con", "int", "wis", "cha"]
found = {"yes": 0, "no": []}
PB_USES = lambda id, name, rec="long": RES(id, name, "prof", rec)


def natural(id, name, die="1d6", dtype="slashing", ability="str"):
    return ACT(id, name, "action", damage={"dice": "%s + mod.%s" % (die, ability), "type": dtype}, text="Unarmed strike.")


def spells(*rows, ab="cha"):
    """rows: (spellId, minLevel or None for a cantrip known at will)."""
    return GRANT([{"id": s} if lv is None else {"id": s, "minLevel": lv, "uses": 1, "recharge": "long", "noSlot": True} for s, lv in rows], ability=ab)


def race(name, traits, size="Medium", speed=30, kind="Humanoid"):
    rid = slug(name)
    base = [F("Ability Score Increase", text="Increase one score by 2 and another by 1, or three scores by 1.",
              effects=[ABIL_CHOICE("asi-plus2", "+2 to one score", ALL, 1, 2), ABIL_CHOICE("asi-plus1", "+1 to another score", ALL, 1, 1)], id=rid + "-asi"),
            F("Creature Type", text="You are a %s." % kind, id=rid + "-type"),
            F("Languages", text="Common and one other language you and your DM agree on.", effects=[PROF("language", ["Common"]), CHOICE("languages", "One more language", "language", 1, {"list": ["any"]})], id=rid + "-languages")]
    feats = [F(n, text=t, effects=fx, id=rid + "-" + slug(n)) for n, t, fx in traits]
    return {"id": rid, "name": name, "size": size, "speed": speed, "source": "MPMM", "features": base + feats, "_traits": feats}


def fill(races):
    """Trait text from the book. Every race's name is a stop, so the last trait doesn't run on into the next race."""
    titles = [r["name"] for r in races]
    for r in races:
        feats = r.pop("_traits")
        names = [f["name"] for f in feats]
        for f in feats:
            t = T.section(B, PAGES[0], PAGES[1], f["name"], stops=[n for n in names if n != f["name"]] + ["Ability Score Increase"] + [x for x in titles if x != r["name"]], after=r["name"], limit=1500)
            if t and len(t) > 20:
                f["text"] = t; found["yes"] += 1
            else:
                found["no"].append(r["name"] + ": " + f["name"])


DV = ("Darkvision", "See in dim light within 60 ft as if bright, and darkness as dim.", [SENSE("darkvision", 60)])
DV120 = ("Darkvision", "Darkvision 120 ft.", [SENSE("darkvision", 120)])
FEY = ("Fey Ancestry", "Advantage on saves against being charmed.", [ADV("Saves against being charmed")])
TRANCE = ("Trance", "Four hours of trance instead of sleep; gain a weapon or tool proficiency after it.", [])
KEEN = ("Keen Senses", "Proficiency in Perception.", [PROF("skill", ["perception"])])
POWER = ("Powerful Build", "Count as one size larger for carrying, pushing, dragging and lifting.", [])


def build():
    races = [
        race("Aarakocra", [("Flight", "Flying speed equal to your walking speed, not in medium or heavy armor.", [SPEED("fly", "walk")]),
                           ("Talons", "Unarmed strikes deal 1d6 + Str slashing damage.", [natural("talons", "Talons")]),
                           ("Wind Caller", "Cast gust of wind once per long rest without a slot from 3rd level.", [spells(("gust-of-wind", 3))])], kind="Humanoid"),
        race("Aasimar", [DV, ("Celestial Resistance", "Resistance to necrotic and radiant damage.", [RESIST("necrotic", "radiant")]),
                         ("Healing Hands", "Action: touch a creature to restore d4s equal to your proficiency bonus. Once per long rest.",
                          [RES("healing-hands", "Healing Hands", 1, "long"), ACT("use-healing-hands", "Healing Hands", "action", cost={"resource": "healing-hands", "amount": 1}, roll={"1": "2d4", "5": "3d4", "9": "4d4", "13": "5d4", "17": "6d4", "by": "level"})]),
                         ("Light Bearer", "You know the light cantrip.", [spells(("light", None))]),
                         ("Celestial Revelation", "From 3rd level, a bonus action transformation for 1 minute once per long rest: Heavenly Wings, Inner Radiance or Necrotic Shroud; once per turn add your proficiency bonus to damage.",
                          [RES("celestial-revelation", "Celestial Revelation", 1, "long"), ACT("use-celestial-revelation", "Celestial Revelation", "bonus", cost={"resource": "celestial-revelation", "amount": 1})])], size="Small or Medium"),
        race("Bugbear", [DV, FEY, ("Long-Limbed", "Your melee reach is 5 ft longer on your turn.", []), POWER, ("Sneaky", "Proficiency in Stealth; squeeze through Small spaces.", [PROF("skill", ["stealth"])]),
                         ("Surprise Attack", "Hitting a creature that hasn't taken a turn in this combat deals an extra 2d6.", [RIDER("surprise-attack", "Surprise Attack", damage="2d6", oncePer="combat", when="firstRound", requires=["hit"])])]),
        race("Centaur", [("Charge", "After moving 30 ft straight toward a target and hitting it with a melee weapon, a bonus action hooves attack.", [ACT("centaur-charge", "Charge (hooves)", "bonus")]),
                         ("Equine Build", "Count as one size larger for carrying; climbing costs 4 ft per foot.", []), ("Hooves", "Unarmed strikes deal 1d6 + Str bludgeoning.", [natural("hooves", "Hooves", dtype="bludgeoning")]),
                         ("Natural Affinity", "Proficiency in Animal Handling, Medicine, Nature or Survival.", [CHOICE("natural-affinity", "Natural Affinity", "skill", 1, {"skills": ["animalHandling", "medicine", "nature", "survival"]})])], speed=40, kind="Fey"),
        race("Changeling", [("Changeling Instincts", "Proficiency in two of Deception, Insight, Intimidation, Performance and Persuasion.", [CHOICE("changeling-instincts", "Changeling Instincts", "skill", 2, {"skills": ["deception", "insight", "intimidation", "performance", "persuasion"]})]),
                            ("Shapechanger", "Action: change your appearance and voice.", [ACT("shapechanger", "Shapechanger", "action")])], size="Small or Medium", kind="Fey"),
        race("Deep Gnome", [DV120, ("Gift of the Svirfneblin", "Disguise self from 3rd level and nondetection from 5th, each once per long rest without a slot.", [spells(("disguise-self", 3), ("nondetection", 5), ab="int")]),
                            ("Gnomish Magic Resistance", "Advantage on Int, Wis and Cha saves against spells.", [ADV("Int, Wis and Cha saves against spells")]),
                            ("Svirfneblin Camouflage", "Advantage on a Stealth check, proficiency bonus times per long rest.", [PB_USES("svirfneblin-camouflage", "Svirfneblin Camouflage")])], size="Small"),
        race("Duergar", [DV120, ("Duergar Magic", "Enlarge/reduce (enlarge only) from 3rd level and invisibility from 5th, each once per long rest without a slot.", [spells(("enlarge-reduce", 3), ("invisibility", 5), ab="int")]),
                         ("Dwarven Resilience", "Advantage on saves against poison, and resistance to poison damage.", [RESIST("poison"), ADV("Saves against poison")]),
                         ("Psionic Fortitude", "Advantage on saves against being charmed or stunned.", [ADV("Saves against being charmed or stunned")])]),
        race("Eladrin", [DV, FEY, ("Fey Step", "Bonus action: teleport 30 ft, proficiency bonus times per long rest; from 3rd level it gains a seasonal effect.", [PB_USES("fey-step", "Fey Step"), ACT("use-fey-step", "Fey Step", "bonus", cost={"resource": "fey-step", "amount": 1})]),
                         KEEN, TRANCE], kind="Humanoid"),
        race("Fairy", [("Fairy Magic", "You know druidcraft; faerie fire from 3rd level and enlarge/reduce from 5th, each once per long rest without a slot.", [spells(("druidcraft", None), ("faerie-fire", 3), ("enlarge-reduce", 5))]),
                       ("Flight", "Flying speed equal to your walking speed, not in medium or heavy armor.", [SPEED("fly", "walk")])], size="Small", kind="Fey"),
        race("Firbolg", [("Firbolg Magic", "Cast detect magic and disguise self once each per long rest without a slot.", [spells(("detect-magic", 1), ("disguise-self", 1), ab="wis")]),
                         ("Hidden Step", "Bonus action: turn invisible until your next turn, proficiency bonus times per long rest.", [PB_USES("hidden-step", "Hidden Step"), ACT("use-hidden-step", "Hidden Step", "bonus", cost={"resource": "hidden-step", "amount": 1})]),
                         POWER, ("Speech of Beast and Leaf", "Beasts and plants can understand you; advantage on Charisma checks to influence them.", [])]),
        race("Air Genasi", [DV, ("Unending Breath", "Hold your breath indefinitely.", []), ("Lightning Resistance", "Resistance to lightning damage.", [RESIST("lightning")]),
                            ("Mingle with the Wind", "You know shocking grasp; feather fall from 3rd level and levitate from 5th, each once per long rest without a slot.", [spells(("shocking-grasp", None), ("feather-fall", 3), ("levitate", 5))])], speed=35, size="Small or Medium"),
        race("Earth Genasi", [DV, ("Earth Walk", "Ignore difficult terrain made of earth or stone.", []),
                              ("Merge with Stone", "You know blade ward and can cast it as a bonus action, proficiency bonus times per long rest. From 5th level, pass without trace once per long rest without a slot.",
                               [GRANT([{"id": "blade-ward"}, {"id": "blade-ward", "uses": "prof", "recharge": "long", "noSlot": True, "econ": "bonus"}, {"id": "pass-without-trace", "minLevel": 5, "uses": 1, "recharge": "long", "noSlot": True}], ability="cha")])], size="Small or Medium"),
        race("Fire Genasi", [DV, ("Fire Resistance", "Resistance to fire damage.", [RESIST("fire")]),
                             ("Reach to the Blaze", "You know produce flame; burning hands from 3rd level and flame blade from 5th, each once per long rest without a slot.", [spells(("produce-flame", None), ("burning-hands", 3), ("flame-blade", 5))])], size="Small or Medium"),
        race("Water Genasi", [("Acid Resistance", "Resistance to acid damage.", [RESIST("acid")]), ("Amphibious", "Breathe air and water.", []), DV,
                              ("Call to the Wave", "You know acid splash; create or destroy water from 3rd level and water walk from 5th, each once per long rest without a slot.", [spells(("acid-splash", None), ("create-or-destroy-water", 3), ("water-walk", 5))]),
                              ("Swim Speed", "Swimming speed equal to your walking speed.", [SPEED("swim", "walk")])], size="Small or Medium"),
        race("Githyanki", [("Astral Knowledge", "After a long rest, gain proficiency with one skill and one weapon or tool until your next long rest.", []),
                           ("Githyanki Psionics", "You know mage hand (invisible); jump from 3rd level and misty step from 5th, each once per long rest without a slot.", [spells(("mage-hand", None), ("jump", 3), ("misty-step", 5), ab="int")]),
                           ("Psychic Resilience", "Resistance to psychic damage.", [RESIST("psychic")])]),
        race("Githzerai", [("Githzerai Psionics", "You know mage hand (invisible); shield from 3rd level and detect thoughts from 5th, each once per long rest without a slot.", [spells(("mage-hand", None), ("shield", 3), ("detect-thoughts", 5), ab="wis")]),
                           ("Mental Discipline", "Advantage on saves against being charmed or frightened.", [ADV("Saves against being charmed or frightened")]),
                           ("Psychic Resilience", "Resistance to psychic damage.", [RESIST("psychic")])]),
        race("Goblin", [DV, FEY, ("Fury of the Small", "When you damage a creature larger than you, add your proficiency bonus to the damage, proficiency bonus times per long rest.",
                                  [PB_USES("fury-of-the-small", "Fury of the Small"), RIDER("fury-of-the-small", "Fury of the Small", damage="prof", cost={"resource": "fury-of-the-small", "amount": 1}, oncePer="turn", requires=["hit"])]),
                        ("Nimble Escape", "Disengage or Hide as a bonus action.", [ACT("nimble-escape", "Nimble Escape", "bonus")])], size="Small"),
        race("Goliath", [("Little Giant", "Proficiency in Athletics; count as one size larger for carrying.", [PROF("skill", ["athletics"])]), ("Mountain Born", "Resistance to cold damage; acclimated to high altitude.", [RESIST("cold")]),
                         ("Stone's Endurance", "Reaction when damaged: reduce it by 1d12 + Con modifier, proficiency bonus times per long rest.",
                          [PB_USES("stones-endurance", "Stone's Endurance"), ACT("use-stones-endurance", "Stone's Endurance", "reaction", cost={"resource": "stones-endurance", "amount": 1}, roll="1d12 + mod.con")])]),
        race("Harengon", [("Hare-Trigger", "Add your proficiency bonus to initiative.", [BON("initiative", "prof")]), ("Leporine Senses", "Proficiency in Perception.", [PROF("skill", ["perception"])]),
                          ("Lucky Footwork", "Reaction when you fail a Dex save: add 1d4, possibly turning it into a success.", [ACT("lucky-footwork", "Lucky Footwork", "reaction", roll="1d4")]),
                          ("Rabbit Hop", "Bonus action: jump 5 × proficiency bonus feet without opportunity attacks, proficiency bonus times per long rest.", [PB_USES("rabbit-hop", "Rabbit Hop"), ACT("use-rabbit-hop", "Rabbit Hop", "bonus", cost={"resource": "rabbit-hop", "amount": 1})])], size="Small or Medium"),
        race("Hobgoblin", [DV, ("Fey Gift", "Help as a bonus action, proficiency bonus times per long rest; from 3rd level it adds a hospitality, passage or spite benefit.", [PB_USES("fey-gift", "Fey Gift"), ACT("use-fey-gift", "Fey Gift (Help)", "bonus", cost={"resource": "fey-gift", "amount": 1})]),
                           ("Fortune from the Many", "After missing or failing, add up to +3 for allies within 30 ft, proficiency bonus times per long rest.", [PB_USES("fortune-from-the-many", "Fortune from the Many")])]),
        race("Kenku", [("Expert Duplication", "Advantage on checks to copy writing or craftwork.", []),
                       ("Kenku Recall", "Proficiency in two skills of your choice. Give yourself advantage on a check with a proficient skill, proficiency bonus times per long rest.",
                        [CHOICE("kenku-recall", "Kenku Recall skills", "skill", 2, {"skills": "any"}), PB_USES("kenku-recall", "Kenku Recall")]),
                       ("Mimicry", "Mimic sounds and voices you've heard; Insight against DC 8 + prof + Cha to tell they're fake.", [])], size="Small or Medium"),
        race("Kobold", [DV, ("Draconic Cry", "Bonus action: allies have advantage on attacks against enemies within 10 ft that can hear you, proficiency bonus times per long rest.", [PB_USES("draconic-cry", "Draconic Cry"), ACT("use-draconic-cry", "Draconic Cry", "bonus", cost={"resource": "draconic-cry", "amount": 1})]),
                        ("Kobold Legacy", "Choose Craftiness (a skill), Defiance (advantage against being frightened) or Draconic Sorcery (a sorcerer cantrip).", [CHOICE("kobold-legacy", "Kobold Legacy", "option", 1, {"optionSet": "kobold-legacies"})])], size="Small"),
        race("Lizardfolk", [("Bite", "Unarmed strikes deal 1d6 + Str slashing.", [natural("bite", "Bite")]), ("Hold Breath", "Hold your breath for 15 minutes.", []),
                            ("Hungry Jaws", "Bonus action bite; on a hit gain temp HP equal to your proficiency bonus, proficiency bonus times per long rest.", [PB_USES("hungry-jaws", "Hungry Jaws"), ACT("use-hungry-jaws", "Hungry Jaws", "bonus", cost={"resource": "hungry-jaws", "amount": 1})]),
                            ("Natural Armor", "Without armor, your AC is 13 + Dex modifier. A shield still counts.", [AC("13 + mod.dex", when="unarmored")]),
                            ("Nature's Intuition", "Proficiency in two of Animal Handling, Medicine, Nature, Perception, Stealth and Survival.", [CHOICE("natures-intuition", "Nature's Intuition", "skill", 2, {"skills": ["animalHandling", "medicine", "nature", "perception", "stealth", "survival"]})])]),
        race("Minotaur", [("Horns", "Unarmed strikes deal 1d6 + Str piercing.", [natural("horns", "Horns", dtype="piercing")]),
                          ("Goring Rush", "After you Dash 20 ft, a bonus action horn attack.", [ACT("goring-rush", "Goring Rush", "bonus")]),
                          ("Hammering Horns", "After hitting with a melee attack in the Attack action, a bonus action shove.", [ACT("hammering-horns", "Hammering Horns", "bonus")]),
                          ("Labyrinthine Recall", "Always know north; advantage on Survival to navigate or track.", [])]),
        race("Orc", [DV, ("Adrenaline Rush", "Dash as a bonus action and gain temp HP equal to your proficiency bonus, proficiency bonus times per long rest.", [PB_USES("adrenaline-rush", "Adrenaline Rush"), ACT("use-adrenaline-rush", "Adrenaline Rush", "bonus", cost={"resource": "adrenaline-rush", "amount": 1})]),
                     POWER, ("Relentless Endurance", "Drop to 1 HP instead of 0, once per long rest.", [RES("relentless-endurance", "Relentless Endurance", 1, "long")])]),
        race("Satyr", [("Ram", "Unarmed strikes deal 1d6 + Str bludgeoning.", [natural("ram", "Ram", dtype="bludgeoning")]), ("Magic Resistance", "Advantage on saves against spells.", [ADV("Saves against spells")]),
                       ("Mirthful Leaps", "Add 1d8 to long and high jumps.", []), ("Reveler", "Proficiency in Performance and Persuasion and one musical instrument.", [PROF("skill", ["performance", "persuasion"])])], speed=35, kind="Fey"),
        race("Sea Elf", [("Child of the Sea", "Swimming speed equal to your walking speed; breathe air and water.", [SPEED("swim", "walk")]), DV, FEY,
                         ("Friend of the Sea", "Speak simply with beasts that have a swimming speed.", []), KEEN, TRANCE]),
        race("Shadar-kai", [("Blessing of the Raven Queen", "Bonus action: teleport 30 ft, proficiency bonus times per long rest; from 3rd level you resist all damage until your next turn.",
                             [PB_USES("blessing-of-the-raven-queen", "Blessing of the Raven Queen"), ACT("use-blessing-of-the-raven-queen", "Blessing of the Raven Queen", "bonus", cost={"resource": "blessing-of-the-raven-queen", "amount": 1})]),
                            DV, FEY, KEEN, ("Necrotic Resistance", "Resistance to necrotic damage.", [RESIST("necrotic")]), TRANCE]),
        race("Shifter", [("Bestial Instincts", "Proficiency in Acrobatics, Athletics, Intimidation or Survival.", [CHOICE("bestial-instincts", "Bestial Instincts", "skill", 1, {"skills": ["acrobatics", "athletics", "intimidation", "survival"]})]),
                         DV, ("Shifting", "Bonus action: shift for 1 minute, gaining 2 × proficiency bonus temp HP and your shifting feature. Proficiency bonus times per long rest.",
                              [PB_USES("shifting", "Shifting"), ACT("use-shifting", "Shift", "bonus", cost={"resource": "shifting", "amount": 1}, tempHp="2 * prof"), CHOICE("shifting-feature", "Shifting option", "option", 1, {"optionSet": "shifting-options"})])]),
        race("Tabaxi", [DV, ("Cat's Claws", "Climbing speed equal to your walking speed; unarmed strikes deal 1d6 + Str slashing.", [SPEED("climb", "walk"), natural("cats-claws", "Cat's Claws")]),
                        ("Cat's Talent", "Proficiency in Perception and Stealth.", [PROF("skill", ["perception", "stealth"])]),
                        ("Feline Agility", "Double your speed until the end of the turn; again only after a turn where you don't move.", [RES("feline-agility", "Feline Agility", 1, "never", note="Comes back after a turn you don't move")])], size="Small or Medium"),
        race("Tortle", [("Claws", "Unarmed strikes deal 1d6 + Str slashing.", [natural("claws", "Claws")]), ("Hold Breath", "Hold your breath for 1 hour.", []),
                        ("Natural Armor", "Your AC is 17; armor doesn't help, but a shield does.", [AC("17", when="unarmored")]),
                        ("Nature's Intuition", "Proficiency in one of Animal Handling, Medicine, Nature, Perception, Stealth or Survival.", [CHOICE("natures-intuition", "Nature's Intuition", "skill", 1, {"skills": ["animalHandling", "medicine", "nature", "perception", "stealth", "survival"]})]),
                        ("Shell Defense", "Action: withdraw into your shell for +4 AC and advantage on Str and Con saves, but you're prone and speed 0.", [ACT("shell-defense", "Shell Defense", "action")])]),
        race("Triton", [("Amphibious", "Breathe air and water.", []), ("Control Air and Water", "Fog cloud, then gust of wind from 3rd level and water walk from 5th, each once per long rest without a slot.", [spells(("fog-cloud", 1), ("gust-of-wind", 3), ("water-walk", 5))]),
                        DV, ("Emissary of the Sea", "Communicate simple ideas with water-breathing beasts.", []), ("Guardian of the Depths", "Resistance to cold damage.", [RESIST("cold")]),
                        ("Swim Speed", "Swimming speed equal to your walking speed.", [SPEED("swim", "walk")])]),
        race("Yuan-ti", [DV, ("Magic Resistance", "Advantage on saves against spells.", [ADV("Saves against spells")]), ("Poison Resilience", "Advantage on saves against poison, and resistance to poison damage.", [RESIST("poison"), ADV("Saves against being poisoned")]),
                         ("Serpentine Spellcasting", "You know poison spray; animal friendship on snakes at will; suggestion once per long rest from 3rd level.", [spells(("poison-spray", None), ("suggestion", 3)), GRANT([{"id": "animal-friendship", "noSlot": True}], ability="cha")])],
             size="Small or Medium"),
    ]
    sets = [
        {"id": "kobold-legacies", "name": "Kobold Legacy", "options": [
            F("Craftiness", text="Proficiency in Arcana, Investigation, Medicine, Sleight of Hand or Survival.", effects=[CHOICE("craftiness", "Craftiness", "skill", 1, {"skills": ["arcana", "investigation", "medicine", "sleightOfHand", "survival"]})]),
            F("Defiance", text="Advantage on saves against being frightened.", effects=[ADV("Saves against being frightened")]),
            F("Draconic Sorcery", text="One sorcerer cantrip.", effects=[CHOICE("draconic-sorcery", "Sorcerer cantrip", "spell", 1, {"spells": {"list": "sorcerer", "level": 0}})])]},
        {"id": "shifting-options", "name": "Shifting", "options": [
            F("Beasthide", text="Extra 1d6 temp HP and +1 AC while shifted.", effects=[BON("ac", 1, note="While shifted")]),
            F("Longtooth", text="Bonus action fang attack (1d6 + Str piercing) while shifted.", effects=[natural("longtooth", "Longtooth bite", dtype="piercing")]),
            F("Swiftstride", text="+10 ft walking speed while shifted; reaction move 10 ft.", effects=[BON("speed", 10, note="While shifted")]),
            F("Wildhunt", text="Advantage on Wisdom checks while shifted; no advantage against you.", effects=[])]},
    ]
    fill(races)
    print("trait text found for %d; missing %d: %s" % (found["yes"], len(found["no"]), ", ".join(found["no"][:20])))
    return {"races": races, "optionSets": sets}
