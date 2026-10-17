"""Player's Handbook (2014): races, backgrounds, feats, subclasses and option lists.

Structure and effects are written here from the rules. Each feature's text is looked up
in your extracted pages (packs/.text/phb); the short summary is used when it isn't found.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import *
import text as T

B = "phb"
CLASS_PAGES = {"barbarian": (46, 51), "bard": (51, 56), "cleric": (56, 64), "druid": (64, 71), "fighter": (70, 76), "monk": (76, 82),
               "paladin": (82, 89), "ranger": (89, 95), "rogue": (94, 99), "sorcerer": (99, 105), "warlock": (105, 113), "wizard": (112, 121)}
SKILLS = ["acrobatics", "animalHandling", "arcana", "athletics", "deception", "history", "insight", "intimidation", "investigation", "medicine",
          "nature", "perception", "performance", "persuasion", "religion", "sleightOfHand", "stealth", "survival"]
ABILS = ["str", "dex", "con", "int", "wis", "cha"]
LANG_ANY = {"list": ["any"]}
found = {"yes": 0, "no": []}


def with_text(feats, pages, after=None, extra_stops=()):
    """Fill each feature's text from the book; keep the summary if the lookup fails."""
    names = [f["name"] for f in feats] + list(extra_stops)
    for f in feats:
        stops = [n for n in names if n != f["name"]] + [n.split(": ", 1)[1] for n in names if ": " in n and n != f["name"]]
        t = T.section(B, pages[0], pages[1], f["name"], stops=stops, after=after)
        if not t and ": " in f["name"]:  # "Channel Divinity: Sacred Weapon" is a run-in "Sacred Weapon." in the book
            t = T.section(B, pages[0], pages[1], f["name"].split(": ", 1)[1], stops=stops, after=after)
        if t and len(t) > 40:
            f["text"] = t; found["yes"] += 1
        else:
            found["no"].append(f["name"])
    return feats


def sub(cls, name, feats, spells=None, next_title=None):
    e = {"id": slug(name), "name": name, "class": cls, "page": CLASS_PAGES[cls][0],
         "features": with_text(feats, CLASS_PAGES[cls], after=name, extra_stops=[next_title] if next_title else [])}
    if spells:
        e["spells"] = spells
    return e


def oath_spells(cls, table, levels):
    return GRANT([(s, lv) for lv, row in zip(levels, table) for s in row], cls=cls)


DOMAIN = (1, 3, 5, 7, 9)
OATH = (3, 5, 9, 13, 17)
CD = {"resource": "channel-divinity", "amount": 1}


def divine_strike(dtype):
    return F("Divine Strike", 8, "Once per turn, a weapon hit deals an extra 1d8 %s damage (2d8 at 14th level)." % dtype,
             [RIDER("divine-strike", "Divine Strike", damage={"8": "1d8", "14": "2d8"}, damageType=dtype, oncePer="turn", requires=["weapon", "hit"])])


def potent_spellcasting():
    return F("Potent Spellcasting", 8, "Add your Wisdom modifier to the damage of your cleric cantrips.", [BON("damage.spell", "mod.wis", note="Cleric cantrips")])


def build():
    subclasses = []
    # ---------------- Barbarian ----------------
    subclasses.append(sub("barbarian", "Path of the Berserker", [
        F("Frenzy", 3, "While raging you can frenzy: a melee weapon attack as a bonus action each turn. Gain a level of exhaustion when the rage ends.", [ACT("frenzy-attack", "Frenzy attack", "bonus", when="toggle:raging")]),
        F("Mindless Rage", 6, "You can't be charmed or frightened while raging.", [{"type": "conditionImmunity", "conditions": ["Charmed", "Frightened"], "when": "toggle:raging"}]),
        F("Intimidating Presence", 10, "Action: frighten a creature within 30 ft (Wisdom save, DC 8 + prof + Cha).", [ACT("intimidating-presence", "Intimidating Presence", "action", save={"ability": "wis", "dc": "8 + prof + mod.cha"})]),
        F("Retaliation", 14, "Reaction when a creature within 5 ft damages you: make a melee weapon attack against it.", [ACT("retaliation", "Retaliation", "reaction")]),
    ], next_title="Path of the Totem Warrior"))
    totem = lambda pre, lv, opts: CHOICE(pre, {"totem-spirit": "Totem Spirit", "totem-aspect": "Aspect of the Beast", "totem-attunement": "Totemic Attunement"}[pre], "option", 1, {"optionSet": pre + "s"})
    subclasses.append(sub("barbarian", "Path of the Totem Warrior", [
        F("Spirit Seeker", 3, "Cast beast sense and speak with animals, but only as rituals.", [GRANT([{"id": "beast-sense", "noSlot": True}, {"id": "speak-with-animals", "noSlot": True}])]),
        F("Totem Spirit", 3, "Choose a totem spirit: bear, eagle or wolf.", [totem("totem-spirit", 3, None)]),
        F("Aspect of the Beast", 6, "Choose a totem animal's aspect.", [totem("totem-aspect", 6, None)]),
        F("Spirit Walker", 10, "Cast commune with nature, but only as a ritual.", [GRANT([{"id": "commune-with-nature", "noSlot": True}])]),
        F("Totemic Attunement", 14, "Choose a totem animal's attunement.", [totem("totem-attunement", 14, None)]),
    ]))
    # ---------------- Bard ----------------
    subclasses.append(sub("bard", "College of Lore", [
        F("Bonus Proficiencies", 3, "Proficiency with three skills of your choice.", [CHOICE("lore-skills", "Bonus Proficiencies", "skill", 3, {"skills": "any"})], id="lore-bonus-proficiencies"),
        F("Cutting Words", 3, "Reaction: spend a Bardic Inspiration to subtract the die from a creature's attack roll, ability check or damage roll.", [ACT("cutting-words", "Cutting Words", "reaction", cost={"resource": "bardic-inspiration", "amount": 1})]),
        F("Additional Magical Secrets", 6, "Learn two spells from any class list; they count as bard spells.", [CHOICE("additional-magical-secrets", "Additional Magical Secrets", "spell", 2, {"spells": {"list": "any", "maxLevel": "slot"}}, grants={"class": "bard"})]),
        F("Peerless Skill", 14, "When you make an ability check, spend a Bardic Inspiration and add the die.", [ACT("peerless-skill", "Peerless Skill", "free", cost={"resource": "bardic-inspiration", "amount": 1})]),
    ], next_title="College of Valor"))
    subclasses.append(sub("bard", "College of Valor", [
        F("Bonus Proficiencies", 3, "Proficiency with medium armor, shields and martial weapons.", [PROF("armor", ["Medium armor", "Shields"]), PROF("weapon", ["Martial weapons"])], id="valor-bonus-proficiencies"),
        F("Combat Inspiration", 3, "A creature with your Bardic Inspiration can add the die to a weapon damage roll, or to its AC against one attack as a reaction."),
        F("Extra Attack", 6, "Attack twice when you take the Attack action.", [SET("attacksPerAction", 2)]),
        F("Battle Magic", 14, "After you use your action to cast a bard spell, make one weapon attack as a bonus action.", [ACT("battle-magic", "Battle Magic attack", "bonus")]),
    ]))
    # ---------------- Cleric ----------------
    def domain(name, spells, feats, nxt):
        return sub("cleric", name, feats, spells=oath_spells("cleric", spells, DOMAIN), next_title=nxt)
    heavy = lambda pre: F("Bonus Proficiency", 1, "Proficiency with heavy armor.", [PROF("armor", ["Heavy armor"])], id=pre + "-bonus-proficiency")
    martial_heavy = lambda pre: F("Bonus Proficiencies", 1, "Proficiency with martial weapons and heavy armor.", [PROF("weapon", ["Martial weapons"]), PROF("armor", ["Heavy armor"])], id=pre + "-bonus-proficiencies")
    subclasses.append(domain("Knowledge Domain", [["command", "identify"], ["augury", "suggestion"], ["nondetection", "speak-with-dead"], ["arcane-eye", "confusion"], ["legend-lore", "scrying"]], [
        F("Blessings of Knowledge", 1, "Learn two languages, and gain proficiency and expertise in two of Arcana, History, Nature or Religion.",
          [CHOICE("knowledge-languages", "Two languages", "language", 2, LANG_ANY), CHOICE("knowledge-skills", "Knowledge skills", "skill", 2, {"skills": ["arcana", "history", "nature", "religion"]}),
           CHOICE("knowledge-expertise", "Knowledge expertise", "expertise", 2, {"skills": ["arcana", "history", "nature", "religion"]})]),
        F("Channel Divinity: Knowledge of the Ages", 2, "Action: proficiency with one skill or tool for 10 minutes.", [ACT("knowledge-of-the-ages", "Knowledge of the Ages", "action", cost=CD)]),
        F("Channel Divinity: Read Thoughts", 6, "Action: read the surface thoughts of a creature within 60 ft (Wisdom save), and cast suggestion on it without a slot.", [ACT("read-thoughts", "Read Thoughts", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
        potent_spellcasting(),
        F("Visions of the Past", 17, "Meditate to see visions of an object's or area's past."),
    ], "Life Domain"))
    subclasses.append(domain("Life Domain", [["bless", "cure-wounds"], ["lesser-restoration", "spiritual-weapon"], ["beacon-of-hope", "revivify"], ["death-ward", "guardian-of-faith"], ["mass-cure-wounds", "raise-dead"]], [
        heavy("life"),
        F("Disciple of Life", 1, "Healing spells of 1st level or higher restore an extra 2 + the spell's level.", [REM("cast", "Disciple of Life: healing spells restore an extra 2 + spell level HP.")]),
        F("Channel Divinity: Preserve Life", 2, "Action: divide HP equal to five times your cleric level among creatures within 30 ft, up to half each one's maximum.", [ACT("preserve-life", "Preserve Life", "action", cost=CD, roll="5 * classLevel")]),
        F("Blessed Healer", 6, "When a spell of yours heals another creature, you regain 2 + the spell's level HP.", [REM("cast", "Blessed Healer: healing someone else heals you 2 + spell level.")]),
        divine_strike("radiant"),
        F("Supreme Healing", 17, "Healing dice from your spells are maximized."),
    ], "Light Domain"))
    subclasses.append(domain("Light Domain", [["burning-hands", "faerie-fire"], ["flaming-sphere", "scorching-ray"], ["daylight", "fireball"], ["guardian-of-faith", "wall-of-fire"], ["flame-strike", "scrying"]], [
        F("Bonus Cantrip", 1, "You know the light cantrip.", [GRANT([("light", 1)], cls="cleric")], id="light-bonus-cantrip"),
        F("Warding Flare", 1, "Reaction when attacked by a creature you can see within 30 ft: impose disadvantage. Wis modifier uses per long rest.",
          [RES("warding-flare", "Warding Flare", "max(1, mod.wis)", {"1": "long", "6": "long"}), ACT("use-warding-flare", "Warding Flare", "reaction", cost={"resource": "warding-flare", "amount": 1})]),
        F("Channel Divinity: Radiance of the Dawn", 2, "Action: dispel magical darkness within 30 ft; hostile creatures there take 2d10 + cleric level radiant (Con save for half).",
          [ACT("radiance-of-the-dawn", "Radiance of the Dawn", "action", cost=CD, damage={"dice": "2d10 + classLevel", "type": "radiant"}, save={"ability": "con", "dc": "spellDC"})]),
        F("Improved Flare", 6, "Warding Flare can protect another creature."),
        potent_spellcasting(),
        F("Corona of Light", 17, "Action: emit sunlight for 1 minute; enemies in it have disadvantage on saves against fire and radiant spells.", [ACT("corona-of-light", "Corona of Light", "action")]),
    ], "Nature Domain"))
    subclasses.append(domain("Nature Domain", [["animal-friendship", "speak-with-animals"], ["barkskin", "spike-growth"], ["plant-growth", "wind-wall"], ["dominate-beast", "grasping-vine"], ["insect-plague", "tree-stride"]], [
        F("Acolyte of Nature", 1, "Learn one druid cantrip, and gain proficiency in Animal Handling, Nature or Survival.",
          [CHOICE("nature-cantrip", "Druid cantrip", "spell", 1, {"spells": {"list": "druid", "level": 0}}, grants={"class": "cleric"}), CHOICE("nature-skill", "Nature skill", "skill", 1, {"skills": ["animalHandling", "nature", "survival"]})]),
        heavy("nature"),
        F("Channel Divinity: Charm Animals and Plants", 2, "Action: beasts and plant creatures within 30 ft make a Wisdom save or are charmed for 1 minute.", [ACT("charm-animals-and-plants", "Charm Animals and Plants", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
        F("Dampen Elements", 6, "Reaction when you or a creature within 30 ft takes acid, cold, fire, lightning or thunder damage: grant resistance to it.", [ACT("dampen-elements", "Dampen Elements", "reaction")]),
        divine_strike("cold, fire or thunder"),
        F("Master of Nature", 17, "Bonus action: command creatures charmed by your Charm Animals and Plants."),
    ], "Tempest Domain"))
    subclasses.append(domain("Tempest Domain", [["fog-cloud", "thunderwave"], ["gust-of-wind", "shatter"], ["call-lightning", "sleet-storm"], ["control-water", "ice-storm"], ["destructive-wave", "insect-plague"]], [
        martial_heavy("tempest"),
        F("Wrath of the Storm", 1, "Reaction when a creature within 5 ft hits you: 2d8 lightning or thunder damage (Dex save for half). Wis modifier uses per long rest.",
          [RES("wrath-of-the-storm", "Wrath of the Storm", "max(1, mod.wis)", "long"), ACT("use-wrath-of-the-storm", "Wrath of the Storm", "reaction", cost={"resource": "wrath-of-the-storm", "amount": 1}, damage={"dice": "2d8", "type": "lightning or thunder"}, save={"ability": "dex", "dc": "spellDC"})]),
        F("Channel Divinity: Destructive Wrath", 2, "When you roll lightning or thunder damage, deal maximum damage instead.", [ACT("destructive-wrath", "Destructive Wrath", "free", cost=CD)]),
        F("Thunderbolt Strike", 6, "Your lightning damage can push a Large or smaller creature 10 ft away."),
        divine_strike("thunder"),
        F("Stormborn", 17, "Flying speed equal to your walking speed when not underground or indoors.", [SPEED("fly", "walk")]),
    ], "Trickery Domain"))
    subclasses.append(domain("Trickery Domain", [["charm-person", "disguise-self"], ["mirror-image", "pass-without-trace"], ["blink", "dispel-magic"], ["dimension-door", "polymorph"], ["dominate-person", "modify-memory"]], [
        F("Blessing of the Trickster", 1, "Action: a willing creature has advantage on Stealth checks for 1 hour.", [ACT("blessing-of-the-trickster", "Blessing of the Trickster", "action")]),
        F("Channel Divinity: Invoke Duplicity", 2, "Action: create an illusory duplicate for 1 minute (concentration). Cast spells from its space; advantage on attacks against creatures next to it.", [ACT("invoke-duplicity", "Invoke Duplicity", "action", cost=CD)]),
        F("Channel Divinity: Cloak of Shadows", 6, "Action: become invisible until the end of your next turn.", [ACT("cloak-of-shadows", "Cloak of Shadows", "action", cost=CD)]),
        divine_strike("poison"),
        F("Improved Duplicity", 17, "Invoke Duplicity makes up to four duplicates."),
    ], "War Domain"))
    subclasses.append(domain("War Domain", [["divine-favor", "shield-of-faith"], ["magic-weapon", "spiritual-weapon"], ["crusaders-mantle", "spirit-guardians"], ["freedom-of-movement", "stoneskin"], ["flame-strike", "hold-monster"]], [
        martial_heavy("war"),
        F("War Priest", 1, "When you take the Attack action, make one weapon attack as a bonus action. Wis modifier uses per long rest.",
          [RES("war-priest", "War Priest", "max(1, mod.wis)", "long"), ACT("use-war-priest", "War Priest attack", "bonus", cost={"resource": "war-priest", "amount": 1})]),
        F("Channel Divinity: Guided Strike", 2, "When you make an attack roll, gain +10 to it.", [ACT("guided-strike", "Guided Strike", "free", cost=CD)]),
        F("Channel Divinity: War God's Blessing", 6, "Reaction when a creature within 30 ft attacks: give it +10 to the roll.", [ACT("war-gods-blessing", "War God's Blessing", "reaction", cost=CD)]),
        divine_strike("weapon"),
        F("Avatar of Battle", 17, "Resistance to bludgeoning, piercing and slashing damage from nonmagical weapons.", [RESIST("bludgeoning", "piercing", "slashing", note="Nonmagical weapons")]),
    ], None))
    # ---------------- Druid ----------------
    land_feats = [
        F("Bonus Cantrip", 2, "Learn one more druid cantrip.", [CHOICE("land-cantrip", "Bonus cantrip", "spell", 1, {"spells": {"list": "druid", "level": 0}}, grants={"class": "druid"})], id="land-bonus-cantrip"),
        F("Natural Recovery", 2, "Once a day during a short rest, recover slots totalling up to half your druid level (rounded up), none 6th level or higher.",
          [RES("natural-recovery", "Natural Recovery", 1, "long"), ACT("use-natural-recovery", "Natural Recovery", "special", cost={"resource": "natural-recovery", "amount": 1}, gain={"slots": {"total": "ceil(classLevel / 2)", "maxLevel": 5}})]),
        F("Circle Spells", 3, "Your terrain grants always-prepared circle spells.", [CHOICE("circle-terrain", "Circle terrain", "option", 1, {"optionSet": "land-circles"})]),
        F("Land's Stride", 6, "Nonmagical difficult terrain costs no extra movement; advantage on saves against magically impeding plants."),
        F("Nature's Ward", 10, "Can't be charmed or frightened by elementals or fey; immune to poison and disease.", [{"type": "immunity", "damage": ["poison"]}, {"type": "conditionImmunity", "conditions": ["Poisoned"]}]),
        F("Nature's Sanctuary", 14, "Beasts and plants must make a Wisdom save to attack you."),
    ]
    subclasses.append(sub("druid", "Circle of the Land", land_feats, next_title="Circle of the Moon"))
    subclasses.append(sub("druid", "Circle of the Moon", [
        F("Combat Wild Shape", 2, "Wild Shape as a bonus action. While transformed, spend a spell slot as a bonus action to regain 1d8 HP per slot level.", [ACT("combat-wild-shape", "Wild Shape (bonus action)", "bonus", cost={"resource": "wild-shape", "amount": 1})]),
        F("Circle Forms", 2, "Wild Shape into beasts up to CR 1 (higher at 6th level: druid level ÷ 3)."),
        F("Primal Strike", 6, "Attacks in beast form count as magical."),
        F("Elemental Wild Shape", 10, "Spend two uses of Wild Shape to become an air, earth, fire or water elemental.", [ACT("elemental-wild-shape", "Elemental Wild Shape", "action", cost={"resource": "wild-shape", "amount": 2})]),
        F("Thousand Forms", 14, "Cast alter self at will.", [GRANT([{"id": "alter-self", "noSlot": True}])]),
    ]))
    # ---------------- Fighter ----------------
    subclasses.append(sub("fighter", "Champion", [
        F("Improved Critical", 3, "Weapon attacks score a critical hit on a 19 or 20.", [SET("critRange", {"3": 19, "15": 18}, mode="min")]),
        F("Remarkable Athlete", 7, "Add half your proficiency bonus (rounded up) to Str, Dex and Con checks you aren't proficient in.", [PROF("check", ["str", "dex", "con"], level="halfUp", onlyIfNotProficient=True)]),
        F("Additional Fighting Style", 10, "Choose a second Fighting Style.", [CHOICE("fighting-style-2", "Additional Fighting Style", "option", 1, {"optionSet": "fighting-styles"})]),
        F("Superior Critical", 15, "Weapon attacks score a critical hit on 18-20."),
        F("Survivor", 18, "At the start of each turn, regain 5 + Con modifier HP if you're at half HP or less and above 0.", [REM("turnStart", "Survivor: regain 5 + Con modifier HP if at half HP or less.")]),
    ], next_title="Battle Master"))
    sup = {"resource": "superiority-dice", "amount": 1}
    subclasses.append(sub("fighter", "Battle Master", [
        F("Combat Superiority", 3, "Learn maneuvers fuelled by superiority dice (d8s, four of them, regained on a short rest).",
          [RES("superiority-dice", "Superiority dice", {"3": 4, "7": 5, "15": 6}, "short", die={"3": "d8", "10": "d10", "18": "d12"}, color="gold"),
           CHOICE("maneuvers", "Maneuvers", "option", {"3": 3, "7": 5, "10": 7, "15": 9}, {"optionSet": "maneuvers"})]),
        F("Student of War", 3, "Proficiency with one type of artisan's tools.", [CHOICE("student-of-war", "Artisan's tools", "tool", 1, LANG_ANY)]),
        F("Know Your Enemy", 7, "Study a creature for 1 minute to learn how it compares to you."),
        F("Improved Combat Superiority", 10, "Superiority dice become d10s (d12s at 18th level)."),
        F("Relentless", 15, "If you roll initiative with no superiority dice, regain one.", [REM("initiative", "Relentless: regain one superiority die if you have none.")]),
    ], next_title="Eldritch Knight"))
    third_known = {"3": 3, "4": 4, "7": 5, "8": 6, "10": 7, "11": 8, "13": 9, "14": 10, "16": 11, "19": 12, "20": 13}
    subclasses.append(sub("fighter", "Eldritch Knight", [
        F("Spellcasting", 3, "Learn wizard spells, mostly abjuration and evocation. Intelligence is your spellcasting ability.",
          [{"type": "spellcasting", "ability": "int", "progression": "third", "list": "wizard", "cantrips": {"3": 2, "10": 3}, "known": third_known, "ritual": "none"}], id="ek-spellcasting"),
        F("Weapon Bond", 3, "Bond with up to two weapons; you can't be disarmed of them and can summon one as a bonus action."),
        F("War Magic", 7, "After casting a cantrip as an action, make one weapon attack as a bonus action.", [ACT("war-magic", "War Magic attack", "bonus")]),
        F("Eldritch Strike", 10, "A creature you hit with a weapon has disadvantage on its next save against your spells before the end of your next turn."),
        F("Arcane Charge", 15, "When you Action Surge, teleport up to 30 ft."),
        F("Improved War Magic", 18, "After casting a spell as an action, make one weapon attack as a bonus action."),
    ]))
    # ---------------- Monk ----------------
    subclasses.append(sub("monk", "Way of the Open Hand", [
        F("Open Hand Technique", 3, "When you hit with Flurry of Blows, knock the target prone (Dex save), push it 15 ft (Str save), or deny its reactions.", [REM("hit", "Open Hand Technique: prone (Dex), push 15 ft (Str), or no reactions.")]),
        F("Wholeness of Body", 6, "Action: regain HP equal to three times your monk level. Once per long rest.",
          [RES("wholeness-of-body", "Wholeness of Body", 1, "long"), ACT("use-wholeness-of-body", "Wholeness of Body", "action", cost={"resource": "wholeness-of-body", "amount": 1}, heal="3 * classLevel")]),
        F("Tranquility", 11, "At the end of a long rest, gain the effect of a sanctuary spell until your next long rest."),
        F("Quivering Palm", 17, "Spend 3 ki on a hit to set up lethal vibrations; later end them for a Con save or drop to 0 HP (10d10 necrotic on a success).", [ACT("quivering-palm", "Quivering Palm", "special", cost={"resource": "ki", "amount": 3})]),
    ], next_title="Way of Shadow"))
    subclasses.append(sub("monk", "Way of Shadow", [
        F("Shadow Arts", 3, "Spend 2 ki to cast darkness, darkvision, pass without trace or silence without components. You know minor illusion.",
          [GRANT([{"id": "minor-illusion"}, {"id": "darkness", "noSlot": True}, {"id": "darkvision", "noSlot": True}, {"id": "pass-without-trace", "noSlot": True}, {"id": "silence", "noSlot": True}], ability="wis"),
           REM("cast", "Shadow Arts: these spells cost 2 ki.")]),
        F("Shadow Step", 6, "Bonus action in dim light or darkness: teleport up to 60 ft to another dim or dark space and gain advantage on your next melee attack.", [ACT("shadow-step", "Shadow Step", "bonus")]),
        F("Cloak of Shadows", 11, "Action in dim light or darkness: become invisible until you attack, cast a spell, or enter bright light.", [ACT("cloak-of-shadows-monk", "Cloak of Shadows", "action")]),
        F("Opportunist", 17, "Reaction when a creature within 5 ft is hit by someone else: make a melee attack against it.", [ACT("opportunist", "Opportunist", "reaction")]),
    ], next_title="Way of the Four Elements"))
    subclasses.append(sub("monk", "Way of the Four Elements", [
        F("Disciple of the Elements", 3, "Learn elemental disciplines fuelled by ki; you learn more at 6th, 11th and 17th level.",
          [CHOICE("elemental-disciplines", "Elemental disciplines", "option", {"3": 2, "6": 3, "11": 4, "17": 5}, {"optionSet": "elemental-disciplines"})]),
    ]))
    # ---------------- Paladin ----------------
    subclasses.append(sub("paladin", "Oath of Devotion", [
        F("Channel Divinity: Sacred Weapon", 3, "Action: for 1 minute add your Charisma modifier to attack rolls with a weapon, which sheds bright light.",
          [{"type": "toggle", "id": "sacred-weapon", "name": "Sacred Weapon", "endsOn": ["combatEnd", "manual"]}, ACT("sacred-weapon", "Sacred Weapon", "action", cost=CD, toggle="sacred-weapon"),
           BON("attack.weapon", "max(1, mod.cha)", when="toggle:sacred-weapon")]),
        F("Channel Divinity: Turn the Unholy", 3, "Action: fiends and undead within 30 ft make a Wisdom save or are turned for 1 minute.", [ACT("turn-the-unholy", "Turn the Unholy", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
        F("Aura of Devotion", 7, "You and friends within 10 ft can't be charmed while you're conscious (30 ft at 18th level).", [{"type": "conditionImmunity", "conditions": ["Charmed"]}]),
        F("Purity of Spirit", 15, "You're always under the effects of protection from evil and good."),
        F("Holy Nimbus", 20, "Action: emanate sunlight for 1 minute; enemies starting their turn in it take 10 radiant. Once per long rest.", [RES("holy-nimbus", "Holy Nimbus", 1, "long"), ACT("use-holy-nimbus", "Holy Nimbus", "action", cost={"resource": "holy-nimbus", "amount": 1})]),
    ], spells=oath_spells("paladin", [["protection-from-evil-and-good", "sanctuary"], ["lesser-restoration", "zone-of-truth"], ["beacon-of-hope", "dispel-magic"], ["freedom-of-movement", "guardian-of-faith"], ["commune", "flame-strike"]], OATH), next_title="Oath of the Ancients"))
    subclasses.append(sub("paladin", "Oath of the Ancients", [
        F("Channel Divinity: Nature's Wrath", 3, "Action: spectral vines restrain a creature within 10 ft (Str or Dex save).", [ACT("natures-wrath", "Nature's Wrath", "action", cost=CD)]),
        F("Channel Divinity: Turn the Faithless", 3, "Action: fey and fiends within 30 ft make a Wisdom save or are turned for 1 minute.", [ACT("turn-the-faithless", "Turn the Faithless", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
        F("Aura of Warding", 7, "You and friends within 10 ft resist damage from spells.", [RESIST("spell damage")]),
        F("Undying Sentinel", 15, "When reduced to 0 HP and not killed, drop to 1 HP instead. Once per long rest.", [RES("undying-sentinel", "Undying Sentinel", 1, "long")]),
        F("Elder Champion", 20, "Action: transform for 1 minute: regain 10 HP each turn, cast paladin spells as a bonus action, enemies have disadvantage on saves against your spells. Once per long rest.",
          [RES("elder-champion", "Elder Champion", 1, "long"), ACT("use-elder-champion", "Elder Champion", "action", cost={"resource": "elder-champion", "amount": 1})]),
    ], spells=oath_spells("paladin", [["ensnaring-strike", "speak-with-animals"], ["misty-step", "moonbeam"], ["plant-growth", "protection-from-energy"], ["ice-storm", "stoneskin"], ["commune-with-nature", "tree-stride"]], OATH), next_title="Oath of Vengeance"))
    subclasses.append(sub("paladin", "Oath of Vengeance", [
        F("Channel Divinity: Abjure Enemy", 3, "Action: a creature within 60 ft makes a Wisdom save or is frightened and its speed is 0 for 1 minute.", [ACT("abjure-enemy", "Abjure Enemy", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
        F("Channel Divinity: Vow of Enmity", 3, "Bonus action: advantage on attack rolls against a creature within 10 ft for 1 minute.", [ACT("vow-of-enmity", "Vow of Enmity", "bonus", cost=CD)]),
        F("Relentless Avenger", 7, "When you hit with an opportunity attack, move up to half your speed without provoking."),
        F("Soul of Vengeance", 15, "Reaction when the target of your Vow of Enmity attacks: make a melee weapon attack against it.", [ACT("soul-of-vengeance", "Soul of Vengeance", "reaction")]),
        F("Avenging Angel", 20, "Action: wings (60 ft fly) and a frightening aura for 1 hour. Once per long rest.", [RES("avenging-angel", "Avenging Angel", 1, "long"), ACT("use-avenging-angel", "Avenging Angel", "action", cost={"resource": "avenging-angel", "amount": 1})]),
    ], spells=oath_spells("paladin", [["bane", "hunters-mark"], ["hold-person", "misty-step"], ["haste", "protection-from-energy"], ["banishment", "dimension-door"], ["hold-monster", "scrying"]], OATH)))
    # ---------------- Ranger ----------------
    subclasses.append(sub("ranger", "Hunter", [
        F("Hunter's Prey", 3, "Choose Colossus Slayer, Giant Killer or Horde Breaker.", [CHOICE("hunters-prey", "Hunter's Prey", "option", 1, {"optionSet": "hunters-prey"})]),
        F("Defensive Tactics", 7, "Choose Escape the Horde, Multiattack Defense or Steel Will.", [CHOICE("defensive-tactics", "Defensive Tactics", "option", 1, {"optionSet": "defensive-tactics"})]),
        F("Multiattack", 11, "Choose Volley or Whirlwind Attack.", [CHOICE("multiattack", "Multiattack", "option", 1, {"optionSet": "hunter-multiattack"})]),
        F("Superior Hunter's Defense", 15, "Choose Evasion, Stand Against the Tide or Uncanny Dodge.", [CHOICE("superior-defense", "Superior Hunter's Defense", "option", 1, {"optionSet": "superior-hunters-defense"})]),
    ], next_title="Beast Master"))
    subclasses.append(sub("ranger", "Beast Master", [
        F("Ranger's Companion", 3, "A beast companion (CR 1/4 or lower, Medium or smaller) adds your proficiency bonus to its AC, attacks, damage, saves and skills; its HP max is four times your ranger level or its normal max."),
        F("Exceptional Training", 7, "Your companion can Dash, Disengage, Dodge or Help as a bonus action when it doesn't attack."),
        F("Bestial Fury", 11, "Your companion makes two attacks when you command it to Attack."),
        F("Share Spells", 15, "A spell targeting only you can also affect your companion within 30 ft."),
    ]))
    # ---------------- Rogue ----------------
    subclasses.append(sub("rogue", "Thief", [
        F("Fast Hands", 3, "Cunning Action can also make a Sleight of Hand check, use thieves' tools, or take the Use an Object action."),
        F("Second-Story Work", 3, "Climbing costs no extra movement, and running jumps go farther by your Dex modifier in feet.", [SPEED("climb", "walk")]),
        F("Supreme Sneak", 9, "Advantage on Stealth checks if you move no more than half your speed.", [ADV("Stealth if you move half speed or less")]),
        F("Use Magic Device", 13, "Ignore class, race and level requirements on magic items."),
        F("Thief's Reflexes", 17, "Take two turns in the first round of combat (the second at initiative minus 10).", [REM("initiative", "Thief's Reflexes: a second turn at initiative minus 10 this round.")]),
    ], next_title="Assassin"))
    subclasses.append(sub("rogue", "Assassin", [
        F("Bonus Proficiencies", 3, "Proficiency with the disguise kit and the poisoner's kit.", [PROF("tool", ["Disguise kit", "Poisoner's kit"])], id="assassin-bonus-proficiencies"),
        F("Assassinate", 3, "Advantage on attacks against creatures that haven't acted yet; hits against surprised creatures are critical hits.", [REM("initiative", "Assassinate: advantage against creatures that haven't acted; hits on surprised creatures are crits.")]),
        F("Infiltration Expertise", 9, "Spend seven days and 25 gp to create a false identity."),
        F("Impostor", 13, "Mimic another person's speech, writing and behavior after three hours of study."),
        F("Death Strike", 17, "When you hit a surprised creature, it makes a Con save or takes double damage."),
    ], next_title="Arcane Trickster"))
    subclasses.append(sub("rogue", "Arcane Trickster", [
        F("Spellcasting", 3, "Learn wizard spells, mostly enchantment and illusion. Intelligence is your spellcasting ability. You know mage hand.",
          [{"type": "spellcasting", "ability": "int", "progression": "third", "list": "wizard", "cantrips": {"3": 3, "10": 4}, "known": third_known, "ritual": "none"}, GRANT([("mage-hand", 3)], cls="rogue")], id="at-spellcasting"),
        F("Mage Hand Legerdemain", 3, "Your mage hand is invisible and can stow, retrieve, pick locks and disarm traps; control it with Cunning Action."),
        F("Magical Ambush", 9, "If you're hidden when you cast a spell, the target has disadvantage on its save."),
        F("Versatile Trickster", 13, "Bonus action: your mage hand gives you advantage on attacks against a creature within 5 ft of it."),
        F("Spell Thief", 17, "Reaction when a creature casts a spell targeting you: steal it on a failed save. Once per long rest.", [RES("spell-thief", "Spell Thief", 1, "long"), ACT("use-spell-thief", "Spell Thief", "reaction", cost={"resource": "spell-thief", "amount": 1})]),
    ]))
    # ---------------- Sorcerer ----------------
    subclasses.append(sub("sorcerer", "Draconic Bloodline", [
        F("Dragon Ancestor", 1, "Choose a dragon type. You speak Draconic, and double proficiency on Charisma checks with dragons.", [PROF("language", ["Draconic"]), CHOICE("dragon-ancestor", "Dragon ancestor", "text", 1)]),
        F("Draconic Resilience", 1, "+1 HP per sorcerer level, and AC 13 + Dex without armor.", [BON("hp.max", "classLevel"), AC("13 + mod.dex", when="unarmored")]),
        F("Elemental Affinity", 6, "Add your Cha modifier to damage of your ancestry's type; spend 1 sorcery point for resistance to it for 1 hour.", [BON("damage.spell", "mod.cha", note="Your dragon ancestor's damage type")]),
        F("Dragon Wings", 14, "Bonus action: sprout wings for a flying speed equal to your walking speed.", [ACT("dragon-wings", "Dragon Wings", "bonus"), SPEED("fly", "walk")]),
        F("Draconic Presence", 18, "Spend 5 sorcery points: charm or frighten creatures within 60 ft for 1 minute (Wisdom save).", [ACT("draconic-presence", "Draconic Presence", "action", cost={"resource": "sorcery-points", "amount": 5})]),
    ], next_title="Wild Magic"))
    subclasses.append(sub("sorcerer", "Wild Magic", [
        F("Wild Magic Surge", 1, "After you cast a sorcerer spell of 1st level or higher, the DM can have you roll a d20; on a 1, roll on the Wild Magic Surge table.", [REM("cast", "Wild Magic Surge: on the DM's call, a d20 roll of 1 triggers a surge.")]),
        F("Tides of Chaos", 1, "Gain advantage on one attack, check or save. Regained on a long rest or after a wild magic surge.", [RES("tides-of-chaos", "Tides of Chaos", 1, "long"), ACT("use-tides-of-chaos", "Tides of Chaos", "free", cost={"resource": "tides-of-chaos", "amount": 1})]),
        F("Bend Luck", 6, "Reaction: spend 2 sorcery points to add or subtract 1d4 from a creature's attack, check or save.", [ACT("bend-luck", "Bend Luck", "reaction", cost={"resource": "sorcery-points", "amount": 2}, roll="1d4")]),
        F("Controlled Chaos", 14, "Roll twice on the Wild Magic Surge table and choose."),
        F("Spell Bombardment", 18, "When you roll the maximum on a damage die, roll it again and add it, once per turn."),
    ]))
    # ---------------- Warlock ----------------
    subclasses.append(sub("warlock", "The Archfey", [
        F("Fey Presence", 1, "Action: creatures in a 10-foot cube make a Wisdom save or are charmed or frightened until your next turn ends. Once per short rest.",
          [RES("fey-presence", "Fey Presence", 1, "short"), ACT("use-fey-presence", "Fey Presence", "action", cost={"resource": "fey-presence", "amount": 1}, save={"ability": "wis", "dc": "spellDC"})]),
        F("Misty Escape", 6, "Reaction when you take damage: turn invisible and teleport up to 60 ft. Once per short rest.", [RES("misty-escape", "Misty Escape", 1, "short"), ACT("use-misty-escape", "Misty Escape", "reaction", cost={"resource": "misty-escape", "amount": 1})]),
        F("Beguiling Defenses", 10, "Immune to being charmed; reflect charm attempts.", [{"type": "conditionImmunity", "conditions": ["Charmed"]}]),
        F("Dark Delirium", 14, "Action: plunge a creature into an illusory realm for 1 minute (Wisdom save). Once per short rest.", [RES("dark-delirium", "Dark Delirium", 1, "short"), ACT("use-dark-delirium", "Dark Delirium", "action", cost={"resource": "dark-delirium", "amount": 1}, save={"ability": "wis", "dc": "spellDC"})]),
    ], next_title="The Fiend"))
    subclasses.append(sub("warlock", "The Fiend", [
        F("Dark One's Blessing", 1, "When you reduce a hostile creature to 0 HP, gain temporary HP equal to your Cha modifier + warlock level.", [REM("kill", "Dark One's Blessing: temp HP = Cha modifier + warlock level.")]),
        F("Dark One's Own Luck", 6, "Add a d10 to an ability check or save. Once per short rest.", [RES("dark-ones-own-luck", "Dark One's Own Luck", 1, "short"), ACT("use-dark-ones-own-luck", "Dark One's Own Luck", "free", cost={"resource": "dark-ones-own-luck", "amount": 1}, roll="1d10")]),
        F("Fiendish Resilience", 10, "After a rest, choose a damage type to resist until you choose another.", [CHOICE("fiendish-resilience", "Resisted damage type", "text", 1)]),
        F("Hurl Through Hell", 14, "When you hit, send the creature through the lower planes: 10d10 psychic. Once per long rest.", [RES("hurl-through-hell", "Hurl Through Hell", 1, "long"), RIDER("hurl-through-hell", "Hurl Through Hell", damage="10d10", damageType="psychic", cost={"resource": "hurl-through-hell", "amount": 1}, requires=["hit"])]),
    ], next_title="The Great Old One"))
    subclasses.append(sub("warlock", "The Great Old One", [
        F("Awakened Mind", 1, "Speak telepathically to a creature within 30 ft."),
        F("Entropic Ward", 6, "Reaction when attacked: impose disadvantage; if it misses, advantage on your next attack against it. Once per short rest.", [RES("entropic-ward", "Entropic Ward", 1, "short"), ACT("use-entropic-ward", "Entropic Ward", "reaction", cost={"resource": "entropic-ward", "amount": 1})]),
        F("Thought Shield", 10, "Your thoughts can't be read; resistance to psychic damage.", [RESIST("psychic")]),
        F("Create Thrall", 14, "Action: touch an incapacitated humanoid to charm it until remove curse is cast on it."),
    ]))
    # ---------------- Wizard ----------------
    def school(name, feats, nxt):
        sav = name.split()[-1]
        return sub("wizard", "School of " + sav, [F(sav + " Savant", 2, "Copying %s spells into your spellbook takes half the gold and time." % sav.lower())] + feats, next_title=nxt)
    subclasses.append(school("School of Abjuration", [
        F("Arcane Ward", 2, "When you cast an abjuration spell of 1st level or higher, create a ward with HP equal to twice your wizard level + Int modifier.", [RES("arcane-ward", "Arcane Ward (HP)", "2 * classLevel + mod.int", "long")]),
        F("Projected Ward", 6, "Reaction when a creature within 30 ft takes damage: your ward absorbs it.", [ACT("projected-ward", "Projected Ward", "reaction")]),
        F("Improved Abjuration", 10, "Add your proficiency bonus to ability checks made as part of abjuration spells."),
        F("Spell Resistance", 14, "Advantage on saves against spells and resistance to their damage.", [ADV("Saves against spells"), RESIST("spell damage")]),
    ], "School of Conjuration"))
    subclasses.append(school("School of Conjuration", [
        F("Minor Conjuration", 2, "Action: conjure a nonmagical object up to 3 ft on a side for 1 hour.", [ACT("minor-conjuration", "Minor Conjuration", "action")]),
        F("Benign Transposition", 6, "Action: teleport up to 30 ft, or swap places with a willing creature. Once per long rest or after a conjuration spell.", [RES("benign-transposition", "Benign Transposition", 1, "long"), ACT("use-benign-transposition", "Benign Transposition", "action", cost={"resource": "benign-transposition", "amount": 1})]),
        F("Focused Conjuration", 10, "Damage can't break your concentration on a conjuration spell."),
        F("Durable Summons", 14, "Creatures you summon with conjuration spells have 30 temporary HP."),
    ], "School of Divination"))
    subclasses.append(school("School of Divination", [
        F("Portent", 2, "After a long rest, roll two d20s; replace any attack, save or check with one of them before the roll.", [RES("portent", "Portent dice", {"2": 2, "14": 3}, "long", color="psy"), REM("longRest", "Portent: roll your portent d20s and note them.")]),
        F("Expert Divination", 6, "Casting a divination spell of 2nd level or higher regains a lower-level slot (up to 5th)."),
        F("The Third Eye", 10, "Action: gain darkvision, ethereal sight, greater comprehension or see invisibility until your next rest.", [RES("the-third-eye", "The Third Eye", 1, "short"), ACT("use-the-third-eye", "The Third Eye", "action", cost={"resource": "the-third-eye", "amount": 1})]),
        F("Greater Portent", 14, "Roll three d20s for Portent."),
    ], "School of Enchantment"))
    subclasses.append(school("School of Enchantment", [
        F("Hypnotic Gaze", 2, "Action: charm a creature within 5 ft (Wisdom save), incapacitating it while you maintain the gaze.", [ACT("hypnotic-gaze", "Hypnotic Gaze", "action", save={"ability": "wis", "dc": "spellDC"})]),
        F("Instinctive Charm", 6, "Reaction when attacked: the attacker makes a Wisdom save or targets someone else.", [ACT("instinctive-charm", "Instinctive Charm", "reaction", save={"ability": "wis", "dc": "spellDC"})]),
        F("Split Enchantment", 10, "Single-target enchantment spells of 1st level or higher can target a second creature."),
        F("Alter Memories", 14, "A creature you charm doesn't know it was charmed; you can make it forget some of the time."),
    ], "School of Evocation"))
    subclasses.append(school("School of Evocation", [
        F("Sculpt Spells", 2, "Choose 1 + the spell's level creatures to automatically succeed on saves against your evocation spells and take no damage.", [REM("cast", "Sculpt Spells: protect 1 + spell level creatures from your evocation spells.")]),
        F("Potent Cantrip", 6, "Creatures that succeed on saves against your cantrips still take half damage."),
        F("Empowered Evocation", 10, "Add your Int modifier to one damage roll of any wizard evocation spell.", [BON("damage.spell", "mod.int", note="Wizard evocation spells")]),
        F("Overchannel", 14, "Deal maximum damage with a wizard spell of 5th level or lower; using it again before a long rest hurts you.", [RES("overchannel", "Overchannel (safe use)", 1, "long")]),
    ], "School of Illusion"))
    subclasses.append(school("School of Illusion", [
        F("Improved Minor Illusion", 2, "You know minor illusion and can make sound and image together.", [GRANT([("minor-illusion", 2)], cls="wizard")]),
        F("Malleable Illusions", 6, "Action: change an illusion spell of 1 minute or longer you're maintaining."),
        F("Illusory Self", 10, "Reaction when attacked: an illusory duplicate makes the attack miss. Once per short rest.", [RES("illusory-self", "Illusory Self", 1, "short"), ACT("use-illusory-self", "Illusory Self", "reaction", cost={"resource": "illusory-self", "amount": 1})]),
        F("Illusory Reality", 14, "Bonus action: make one inanimate object in an illusion real for 1 minute.", [ACT("illusory-reality", "Illusory Reality", "bonus")]),
    ], "School of Necromancy"))
    subclasses.append(school("School of Necromancy", [
        F("Grim Harvest", 2, "When a spell of 1st level or higher you cast kills a creature, regain HP equal to twice the spell's level (three times for necromancy). Not undead or constructs.", [REM("kill", "Grim Harvest: regain 2 × spell level HP (3 × for necromancy).")]),
        F("Undead Thralls", 6, "Add animate dead to your spellbook. It animates one extra target, and your undead get extra HP (your wizard level) and add your proficiency bonus to damage.", [REM("cast", "Undead Thralls: animate dead raises one more; undead gain +wizard level HP and +prof damage.")]),
        F("Inured to Undeath", 10, "Resistance to necrotic damage, and your HP maximum can't be reduced.", [RESIST("necrotic")]),
        F("Command Undead", 14, "Action: an undead within 60 ft makes a Charisma save or obeys you.", [ACT("command-undead", "Command Undead", "action", save={"ability": "cha", "dc": "spellDC"})]),
    ], "School of Transmutation"))
    subclasses.append(school("School of Transmutation", [
        F("Minor Alchemy", 2, "Spend 10 minutes to change an object's material for 1 hour."),
        F("Transmuter's Stone", 6, "Create a stone granting darkvision, +10 speed, Con save proficiency, or a damage resistance."),
        F("Shapechanger", 10, "Add polymorph to your spellbook; cast it on yourself without a slot once per short rest.", [GRANT([{"id": "polymorph", "uses": 1, "recharge": "short", "noSlot": True}], cls="wizard")]),
        F("Master Transmuter", 14, "Destroy your stone for a major transformation, restoration, panacea or youth. Once per long rest.", [RES("master-transmuter", "Master Transmuter", 1, "long")]),
    ], None))

    return {"subclasses": subclasses, "optionSets": option_sets(), "races": races(), "backgrounds": backgrounds(), "feats": feats()}


def option_sets():
    sup = {"resource": "superiority-dice", "amount": 1}
    die = {"3": "1d8", "10": "1d10", "18": "1d12"}
    def man(name, text, **rider):
        if rider.get("reaction"):
            return F(name, text=text, effects=[ACT(slug(name), name, "reaction", cost=sup, roll=die)])
        if rider.get("bonus") or rider.get("free"):
            return F(name, text=text, effects=[ACT(slug(name), name, "bonus" if rider.get("bonus") else "free", cost=sup, roll=die)])
        return F(name, text=text, effects=[RIDER(slug(name), name, damage=die, cost=sup, requires=rider.get("req", ["weapon", "hit"]))])
    maneuvers = [
        man("Commander's Strike", "Forgo one attack; a companion uses its reaction to attack, adding the superiority die to damage.", bonus=True),
        man("Disarming Attack", "On a hit, add the die to damage; the target makes a Str save or drops an item."),
        man("Distracting Strike", "On a hit, add the die to damage; the next attack against the target by someone else has advantage."),
        man("Evasive Footwork", "When you move, add the die to your AC until you stop.", free=True),
        man("Feinting Attack", "Bonus action: advantage on your next attack against a creature within 5 ft; add the die to damage on a hit.", bonus=True),
        man("Goading Attack", "On a hit, add the die to damage; the target makes a Wis save or has disadvantage attacking others."),
        man("Lunging Attack", "Increase your reach by 5 ft for one melee attack; add the die to damage on a hit.", req=["melee", "hit"]),
        man("Maneuvering Attack", "On a hit, add the die to damage; an ally can move half its speed without provoking."),
        man("Menacing Attack", "On a hit, add the die to damage; the target makes a Wis save or is frightened."),
        man("Parry", "Reaction when hit by a melee attack: reduce the damage by the die + Dex modifier.", reaction=True),
        man("Precision Attack", "Add the die to an attack roll.", free=True),
        man("Pushing Attack", "On a hit, add the die to damage; the target makes a Str save or is pushed 15 ft."),
        man("Rally", "Bonus action: an ally gains temporary HP equal to the die + your Cha modifier.", bonus=True),
        man("Riposte", "Reaction when a creature misses you with a melee attack: attack it and add the die to damage.", reaction=True),
        man("Sweeping Attack", "On a melee hit, another creature within 5 ft takes the die in damage if your roll would hit it.", req=["melee", "hit"]),
        man("Trip Attack", "On a hit, add the die to damage; a Large or smaller target makes a Str save or falls prone."),
    ]
    with_text(maneuvers, (73, 75), after="Maneuvers")
    land = {"Arctic": [["hold-person", "spike-growth"], ["sleet-storm", "slow"], ["freedom-of-movement", "ice-storm"], ["commune-with-nature", "cone-of-cold"]],
            "Coast": [["mirror-image", "misty-step"], ["water-breathing", "water-walk"], ["control-water", "freedom-of-movement"], ["conjure-elemental", "scrying"]],
            "Desert": [["blur", "silence"], ["create-food-and-water", "protection-from-energy"], ["blight", "hallucinatory-terrain"], ["insect-plague", "wall-of-stone"]],
            "Forest": [["barkskin", "spider-climb"], ["call-lightning", "plant-growth"], ["divination", "freedom-of-movement"], ["commune-with-nature", "tree-stride"]],
            "Grassland": [["invisibility", "pass-without-trace"], ["daylight", "haste"], ["divination", "freedom-of-movement"], ["dream", "insect-plague"]],
            "Mountain": [["spider-climb", "spike-growth"], ["lightning-bolt", "meld-into-stone"], ["stone-shape", "stoneskin"], ["passwall", "wall-of-stone"]],
            "Swamp": [["darkness", "acid-arrow"], ["water-walk", "stinking-cloud"], ["freedom-of-movement", "locate-creature"], ["insect-plague", "scrying"]],
            "Underdark": [["spider-climb", "web"], ["gaseous-form", "stinking-cloud"], ["greater-invisibility", "stone-shape"], ["cloudkill", "insect-plague"]]}
    circles = [F(t, text="Circle spells at druid levels 3, 5, 7 and 9.", effects=[oath_spells("druid", rows, (3, 5, 7, 9))]) for t, rows in land.items()]
    totem = lambda pre, opts: [F(n, text=t, effects=fx, id=pre + "-" + slug(n)) for n, t, fx in opts]
    sets = [
        {"id": "maneuvers", "name": "Maneuvers", "options": maneuvers},
        {"id": "land-circles", "name": "Circle of the Land terrains", "options": circles},
        {"id": "totem-spirits", "name": "Totem Spirit", "options": totem("spirit", [
            ("Bear", "While raging, resistance to all damage except psychic.", [RESIST("all but psychic", when="toggle:raging")]),
            ("Eagle", "While raging (without heavy armor), opportunity attacks against you have disadvantage and you can Dash as a bonus action.", []),
            ("Wolf", "While raging, friends have advantage on melee attacks against hostile creatures within 5 ft of you.", [])])},
        {"id": "totem-aspects", "name": "Aspect of the Beast", "options": totem("aspect", [
            ("Bear", "Double carrying capacity; advantage on Strength checks to push, pull, lift or break.", []),
            ("Eagle", "See up to 1 mile clearly; dim light doesn't impose disadvantage on Perception.", []),
            ("Wolf", "Track at a fast pace and move stealthily at a normal pace.", [])])},
        {"id": "totem-attunements", "name": "Totemic Attunement", "options": totem("attunement", [
            ("Bear", "While raging, hostile creatures within 5 ft have disadvantage attacking anyone but you.", []),
            ("Eagle", "While raging, fly at your walking speed (you fall if you end your turn in the air).", []),
            ("Wolf", "While raging, a bonus action after a melee hit can knock a Large or smaller creature prone.", [])])},
        {"id": "hunters-prey", "name": "Hunter's Prey", "options": [
            F("Colossus Slayer", text="Once per turn, a weapon hit on a creature below its HP maximum deals an extra 1d8.", effects=[RIDER("colossus-slayer", "Colossus Slayer", damage="1d8", oncePer="turn", requires=["weapon", "hit"])]),
            F("Giant Killer", text="Reaction when a Large or larger creature within 5 ft attacks you: attack it.", effects=[ACT("giant-killer", "Giant Killer", "reaction")]),
            F("Horde Breaker", text="Once per turn, make another attack against a different creature within 5 ft of the first target.")]},
        {"id": "defensive-tactics", "name": "Defensive Tactics", "options": [
            F("Escape the Horde", text="Opportunity attacks against you have disadvantage."),
            F("Multiattack Defense", text="After a creature hits you, +4 AC against its other attacks this turn."),
            F("Steel Will", text="Advantage on saves against being frightened.", effects=[ADV("Saves against being frightened")])]},
        {"id": "hunter-multiattack", "name": "Multiattack", "options": [
            F("Volley", text="Action: a ranged attack against every creature within 10 ft of a point you can see."),
            F("Whirlwind Attack", text="Action: a melee attack against every creature within 5 ft of you.")]},
        {"id": "superior-hunters-defense", "name": "Superior Hunter's Defense", "options": [
            F("Evasion", text="Take no damage on a successful Dex save for half, and half on a failure.", id="hunter-evasion"),
            F("Stand Against the Tide", text="Reaction when a hostile creature misses you with a melee attack: make it attack another creature."),
            F("Uncanny Dodge", text="Reaction when an attacker you can see hits you: halve the damage.", effects=[ACT("hunter-uncanny-dodge", "Uncanny Dodge", "reaction")], id="hunter-uncanny-dodge")]},
        {"id": "elemental-disciplines", "name": "Elemental Disciplines", "options": [
            F(n, text=t, effects=[ACT(slug(n), n, e, cost={"resource": "ki", "amount": k})] if k else [])
            for n, t, e, k in [
                ("Elemental Attunement", "Use your action to make a small harmless elemental effect.", "action", 0),
                ("Breath of Winter", "6 ki: cast cone of cold. (17th level)", "action", 6),
                ("Clench of the North Wind", "3 ki: cast hold person. (6th level)", "action", 3),
                ("Eternal Mountain Defense", "5 ki: cast stoneskin on yourself. (17th level)", "action", 5),
                ("Fangs of the Fire Snake", "1 ki: unarmed strikes reach 10 ft and deal fire damage; +1d10 fire for another ki.", "free", 1),
                ("Fist of Four Thunders", "2 ki: cast thunderwave.", "action", 2),
                ("Fist of Unbroken Air", "2 ki: a creature within 30 ft takes 3d10 bludgeoning (Str save), pushed 20 ft and knocked prone.", "action", 2),
                ("Flames of the Phoenix", "4 ki: cast fireball. (11th level)", "action", 4),
                ("Gong of the Summit", "3 ki: cast shatter. (6th level)", "action", 3),
                ("Mist Stance", "4 ki: cast gaseous form on yourself. (11th level)", "action", 4),
                ("Ride the Wind", "4 ki: cast fly on yourself. (11th level)", "action", 4),
                ("River of Hungry Flame", "5 ki: cast wall of fire. (17th level)", "action", 5),
                ("Rush of the Gale Spirits", "2 ki: cast gust of wind.", "action", 2),
                ("Shape the Flowing River", "1 ki: shape ice and water in a 30-foot cube.", "action", 1),
                ("Sweeping Cinder Strike", "2 ki: cast burning hands.", "action", 2),
                ("Water Whip", "2 ki: 3d10 bludgeoning (Dex save) and pull or knock prone a creature within 30 ft.", "action", 2),
                ("Wave of Rolling Earth", "6 ki: cast wall of stone. (17th level)", "action", 6)]]},
        {"id": "eldritch-invocations", "name": "Eldritch Invocations", "options": invocations()},
        {"id": "draconic-ancestries", "name": "Draconic Ancestry", "options": [
            F(c + " dragon", text="%s breath (%s); resistance to %s." % (dt.title(), shape, dt), effects=[RESIST(dt)], id=slug(c))
            for c, dt, shape in [("Black", "acid", "5 by 30 ft line, Dex save"), ("Blue", "lightning", "5 by 30 ft line, Dex save"), ("Brass", "fire", "5 by 30 ft line, Dex save"),
                                 ("Bronze", "lightning", "5 by 30 ft line, Dex save"), ("Copper", "acid", "5 by 30 ft line, Dex save"), ("Gold", "fire", "15 ft cone, Dex save"),
                                 ("Green", "poison", "15 ft cone, Con save"), ("Red", "fire", "15 ft cone, Dex save"), ("Silver", "cold", "15 ft cone, Con save"), ("White", "cold", "15 ft cone, Con save")]]},
    ]
    return sets


def invocations():
    nos = lambda sid: [GRANT([{"id": sid, "noSlot": True}], cls="warlock")]
    inv = [
        ("Agonizing Blast", "Add your Cha modifier to eldritch blast damage. (Prerequisite: eldritch blast)", []),
        ("Armor of Shadows", "Cast mage armor on yourself at will without a slot.", nos("mage-armor")),
        ("Ascendant Step", "Cast levitate on yourself at will without a slot. (9th level)", nos("levitate")),
        ("Beast Speech", "Cast speak with animals at will without a slot.", nos("speak-with-animals")),
        ("Beguiling Influence", "Proficiency in Deception and Persuasion.", [PROF("skill", ["deception", "persuasion"])]),
        ("Bewitching Whispers", "Cast compulsion once with a warlock slot; once per long rest. (7th level)", []),
        ("Book of Ancient Secrets", "Inscribe rituals in your Book of Shadows and cast them as rituals. (Pact of the Tome)", []),
        ("Chains of Carceri", "Cast hold monster at will on a celestial, fiend or elemental. (15th level, Pact of the Chain)", []),
        ("Devil's Sight", "See normally in darkness, magical and nonmagical, to 120 ft.", []),
        ("Dreadful Word", "Cast confusion once with a warlock slot; once per long rest. (7th level)", []),
        ("Eldritch Sight", "Cast detect magic at will without a slot.", nos("detect-magic")),
        ("Eldritch Spear", "Eldritch blast range becomes 300 ft. (Prerequisite: eldritch blast)", []),
        ("Eyes of the Rune Keeper", "Read all writing.", []),
        ("Fiendish Vigor", "Cast false life on yourself at will as a 1st-level spell without a slot.", nos("false-life")),
        ("Gaze of Two Minds", "Action: perceive through a willing humanoid's senses.", []),
        ("Lifedrinker", "Pact weapon hits deal extra necrotic damage equal to your Cha modifier. (12th level, Pact of the Blade)", []),
        ("Mask of Many Faces", "Cast disguise self at will without a slot.", nos("disguise-self")),
        ("Master of Myriad Forms", "Cast alter self at will without a slot. (15th level)", nos("alter-self")),
        ("Minions of Chaos", "Cast conjure elemental once with a warlock slot; once per long rest. (9th level)", []),
        ("Mire the Mind", "Cast slow once with a warlock slot; once per long rest. (5th level)", []),
        ("Misty Visions", "Cast silent image at will without a slot.", nos("silent-image")),
        ("One with Shadows", "Action in dim light or darkness: become invisible until you move or act. (5th level)", [ACT("one-with-shadows", "One with Shadows", "action")]),
        ("Otherworldly Leap", "Cast jump on yourself at will without a slot. (9th level)", nos("jump")),
        ("Repelling Blast", "Eldritch blast pushes a creature it hits up to 10 ft. (Prerequisite: eldritch blast)", []),
        ("Sculptor of Flesh", "Cast polymorph once with a warlock slot; once per long rest. (7th level)", []),
        ("Sign of Ill Omen", "Cast bestow curse once with a warlock slot; once per long rest. (5th level)", []),
        ("Thief of Five Fates", "Cast bane once with a warlock slot; once per long rest.", []),
        ("Thirsting Blade", "Attack twice with your pact weapon when you take the Attack action. (5th level, Pact of the Blade)", [SET("attacksPerAction", 2, note="Pact weapon only")]),
        ("Visions of Distant Realms", "Cast arcane eye at will without a slot. (15th level)", nos("arcane-eye")),
        ("Voice of the Chain Master", "Talk through and perceive through your familiar at any distance on the same plane. (Pact of the Chain)", []),
        ("Whispers of the Grave", "Cast speak with dead at will without a slot. (9th level)", nos("speak-with-dead")),
        ("Witch Sight", "See the true form of shapechangers and illusions within 30 ft. (15th level)", []),
    ]
    out = [F(n, text=t, effects=fx) for n, t, fx in inv]
    return with_text(out, (110, 112), after="Eldritch Invocations")


def races():
    D = lambda r=60: F("Darkvision", text="See in dim light within %d ft as if bright, and darkness as dim." % r, effects=[SENSE("darkvision", r)])
    L = lambda *l, extra=0: F("Languages", text=", ".join(l) + (" and %d more" % extra if extra else "") + ".", effects=[PROF("language", list(l))] + ([CHOICE("languages", "Extra language", "language", extra, LANG_ANY)] if extra else []))
    def race(name, size, speed, page, feats, subs=()):
        r = {"id": slug(name), "name": name, "size": size, "speed": speed, "page": page, "features": feats}
        if subs:
            r["subraces"] = [{"id": slug(n), "name": n, "features": fs} for n, fs in subs]
        return r
    def asi(rid, *pairs):
        return F("Ability Score Increase", text=", ".join("+%d %s" % (n, a.upper()) for a, n in pairs) + ".", effects=[ASC(a, n) for a, n in pairs], id=rid + "-asi")
    out = [
        race("Dwarf", "Medium", 25, 18, [asi("dwarf", ("con", 2)), F("Speed", text="25 ft; heavy armor doesn't slow you.", id="dwarf-speed"), D(),
            F("Dwarven Resilience", text="Advantage on saves against poison, and resistance to poison damage.", effects=[RESIST("poison"), ADV("Saves against poison")]),
            F("Dwarven Combat Training", text="Proficiency with battleaxe, handaxe, light hammer and warhammer.", effects=[PROF("weapon", ["Battleaxes", "Handaxes", "Light hammers", "Warhammers"])]),
            F("Tool Proficiency", text="One of smith's tools, brewer's supplies or mason's tools.", effects=[CHOICE("tool", "Tool proficiency", "tool", 1, {"list": ["Smith's tools", "Brewer's supplies", "Mason's tools"]})], id="dwarf-tool"),
            F("Stonecunning", text="Double proficiency on History checks about stonework."), L("Common", "Dwarvish")],
            [("Hill Dwarf", [asi("hill-dwarf", ("wis", 1)), F("Dwarven Toughness", text="+1 HP per level.", effects=[BON("hp.perLevel", 1)])]),
             ("Mountain Dwarf", [asi("mountain-dwarf", ("str", 2)), F("Dwarven Armor Training", text="Proficiency with light and medium armor.", effects=[PROF("armor", ["Light armor", "Medium armor"])])])]),
        race("Elf", "Medium", 30, 21, [asi("elf", ("dex", 2)), D(), F("Keen Senses", text="Proficiency in Perception.", effects=[PROF("skill", ["perception"])]),
            F("Fey Ancestry", text="Advantage on saves against being charmed; magic can't put you to sleep.", effects=[ADV("Saves against being charmed")]),
            F("Trance", text="Meditate 4 hours instead of sleeping 8."), L("Common", "Elvish")],
            [("High Elf", [asi("high-elf", ("int", 1)), F("Elf Weapon Training", text="Proficiency with longsword, shortsword, shortbow and longbow.", effects=[PROF("weapon", ["Longswords", "Shortswords", "Shortbows", "Longbows"])], id="high-elf-weapons"),
                F("Cantrip", text="One wizard cantrip; Intelligence is its ability.", effects=[CHOICE("cantrip", "High elf cantrip", "spell", 1, {"spells": {"list": "wizard", "level": 0}}, grants={"class": "wizard"})], id="high-elf-cantrip"),
                F("Extra Language", text="One extra language.", effects=[CHOICE("language", "Extra language", "language", 1, LANG_ANY)], id="high-elf-language")]),
             ("Wood Elf", [asi("wood-elf", ("wis", 1)), F("Elf Weapon Training", text="Proficiency with longsword, shortsword, shortbow and longbow.", effects=[PROF("weapon", ["Longswords", "Shortswords", "Shortbows", "Longbows"])], id="wood-elf-weapons"),
                F("Fleet of Foot", text="Base walking speed 35 ft.", effects=[SPEED("walk", 35)]), F("Mask of the Wild", text="Hide when only lightly obscured by natural phenomena.")]),
             ("Drow", [asi("drow", ("cha", 1)), F("Superior Darkvision", text="Darkvision 120 ft.", effects=[SENSE("darkvision", 120)]),
                F("Sunlight Sensitivity", text="Disadvantage on attacks and sight-based Perception in direct sunlight.", effects=[ADV("Attacks and sight Perception in direct sunlight", disadvantage=True)]),
                F("Drow Magic", text="You know dancing lights; faerie fire at 3rd level and darkness at 5th, each once per long rest. Charisma is the ability.",
                  effects=[GRANT([{"id": "dancing-lights"}, {"id": "faerie-fire", "minLevel": 3, "uses": 1, "recharge": "long", "noSlot": True}, {"id": "darkness", "minLevel": 5, "uses": 1, "recharge": "long", "noSlot": True}], ability="cha")]),
                F("Drow Weapon Training", text="Proficiency with rapiers, shortswords and hand crossbows.", effects=[PROF("weapon", ["Rapiers", "Shortswords", "Hand crossbows"])])])]),
        race("Halfling", "Small", 25, 26, [asi("halfling", ("dex", 2)), F("Lucky", text="Reroll a 1 on an attack roll, ability check or saving throw.", id="halfling-lucky"),
            F("Brave", text="Advantage on saves against being frightened.", effects=[ADV("Saves against being frightened")]), F("Halfling Nimbleness", text="Move through the space of any larger creature."), L("Common", "Halfling")],
            [("Lightfoot", [asi("lightfoot", ("cha", 1)), F("Naturally Stealthy", text="Hide when obscured only by a creature at least one size larger.")]),
             ("Stout", [asi("stout", ("con", 1)), F("Stout Resilience", text="Advantage on saves against poison, and resistance to poison damage.", effects=[RESIST("poison"), ADV("Saves against poison")])])]),
        race("Human", "Medium", 30, 29, [L("Common", extra=1)],
            [("Standard Human", [F("Ability Score Increase", text="+1 to every ability score.", effects=[ASC(a, 1) for a in ABILS], id="human-asi")]),
             ("Variant Human", [F("Ability Score Increase", text="+1 to two scores of your choice.", effects=[ABIL_CHOICE("variant-abilities", "Two +1 increases", ABILS, 2)], id="variant-human-asi"),
                F("Skills", text="Proficiency in one skill.", effects=[CHOICE("variant-skill", "Skill", "skill", 1, {"skills": "any"})], id="variant-human-skill"),
                F("Feat", text="One feat of your choice.", effects=[CHOICE("variant-feat", "Feat", "feat", 1)], id="variant-human-feat")])]),
        race("Dragonborn", "Medium", 30, 32, [asi("dragonborn", ("str", 2), ("cha", 1)),
            F("Draconic Ancestry", text="Choose a dragon type; it sets your breath weapon and damage resistance.", effects=[CHOICE("ancestry", "Draconic ancestry", "option", 1, {"optionSet": "draconic-ancestries"})]),
            F("Breath Weapon", text="Action: exhale destructive energy (2d6, 3d6 at 6th, 4d6 at 11th, 5d6 at 16th). DC 8 + Con modifier + proficiency. Once per short rest.",
              effects=[RES("breath-weapon", "Breath Weapon", 1, "short"), ACT("use-breath-weapon", "Breath Weapon", "action", cost={"resource": "breath-weapon", "amount": 1}, damage={"dice": {"1": "2d6", "6": "3d6", "11": "4d6", "16": "5d6"}}, save={"ability": "dex", "dc": "8 + mod.con + prof"})]),
            L("Common", "Draconic")]),
        race("Gnome", "Small", 25, 35, [asi("gnome", ("int", 2)), D(), F("Gnome Cunning", text="Advantage on Int, Wis and Cha saves against magic.", effects=[ADV("Int, Wis and Cha saves against magic")]), L("Common", "Gnomish")],
            [("Forest Gnome", [asi("forest-gnome", ("dex", 1)), F("Natural Illusionist", text="You know minor illusion; Intelligence is its ability.", effects=[GRANT([{"id": "minor-illusion"}], ability="int")]),
                F("Speak with Small Beasts", text="Communicate simple ideas with Small or smaller beasts.")]),
             ("Rock Gnome", [asi("rock-gnome", ("con", 1)), F("Artificer's Lore", text="Double proficiency on History checks about magic items, alchemical objects or technology."),
                F("Tinker", text="Proficiency with tinker's tools; build tiny clockwork devices.", effects=[PROF("tool", ["Tinker's tools"])])])]),
        race("Half-Elf", "Medium", 30, 38, [F("Ability Score Increase", text="+2 Charisma, and +1 to two other scores.", effects=[ASC("cha", 2), ABIL_CHOICE("abilities", "Two +1 increases", ["str", "dex", "con", "int", "wis"], 2)], id="half-elf-asi"),
            D(), F("Fey Ancestry", text="Advantage on saves against being charmed; magic can't put you to sleep.", effects=[ADV("Saves against being charmed")], id="half-elf-fey-ancestry"),
            F("Skill Versatility", text="Proficiency in two skills of your choice.", effects=[CHOICE("skills", "Skill Versatility", "skill", 2, {"skills": "any"})]), L("Common", "Elvish", extra=1)]),
        race("Half-Orc", "Medium", 30, 40, [asi("half-orc", ("str", 2), ("con", 1)), D(), F("Menacing", text="Proficiency in Intimidation.", effects=[PROF("skill", ["intimidation"])]),
            F("Relentless Endurance", text="Drop to 1 HP instead of 0, once per long rest.", effects=[RES("relentless-endurance", "Relentless Endurance", 1, "long")]),
            F("Savage Attacks", text="Roll one extra weapon damage die on a melee critical hit."), L("Common", "Orc")]),
        race("Tiefling", "Medium", 30, 42, [asi("tiefling", ("cha", 2), ("int", 1)), D(), F("Hellish Resistance", text="Resistance to fire damage.", effects=[RESIST("fire")]),
            F("Infernal Legacy", text="You know thaumaturgy. At 3rd level cast hellish rebuke as a 2nd-level spell, and at 5th darkness, each once per long rest. Charisma is the ability.",
              effects=[GRANT([{"id": "thaumaturgy"}, {"id": "hellish-rebuke", "minLevel": 3, "uses": 1, "recharge": "long", "noSlot": True}, {"id": "darkness", "minLevel": 5, "uses": 1, "recharge": "long", "noSlot": True}], ability="cha")]),
            L("Common", "Infernal")]),
    ]
    looked_up = lambda fs: [f for f in fs if f["name"] != "Ability Score Increase"]  # the summaries are exact; the book's lines match the wrong race
    titles = [x["name"] for x in out] + [s["name"] for x in out for s in x.get("subraces", [])]
    for r in out:  # book text for each trait, found under the race's heading
        with_text(looked_up(r["features"]), (17, 44), after=r["name"], extra_stops=titles)
        for s in r.get("subraces", []):
            with_text(looked_up(s["features"]), (17, 44), after=s["name"], extra_stops=titles)
    return out


def backgrounds():
    def bg(name, page, skills, feature, tools=(), langs=0, tool_choice=None):
        fx = [PROF("skill", skills)]
        if tools:
            fx.append(PROF("tool", list(tools)))
        if tool_choice:
            fx.append(CHOICE("tool", "Tool proficiency", "tool", 1, {"list": tool_choice}))
        if langs:
            fx.append(CHOICE("languages", "Languages", "language", langs, LANG_ANY))
        feats = [F("Proficiencies", text="Skills: %s." % ", ".join(skills), effects=fx, id=slug(name) + "-proficiencies"), F("Feature: " + feature, id=slug(feature))]
        with_text(feats[1:], (127, 142), after=name)
        return {"id": slug(name), "name": name, "page": page, "features": feats}
    return [
        bg("Acolyte", 127, ["insight", "religion"], "Shelter of the Faithful", langs=2),
        bg("Charlatan", 128, ["deception", "sleightOfHand"], "False Identity", tools=["Disguise kit", "Forgery kit"]),
        bg("Criminal", 129, ["deception", "stealth"], "Criminal Contact", tools=["Thieves' tools"], tool_choice=["Dice set", "Dragonchess set", "Playing card set", "Three-Dragon Ante set"]),
        bg("Entertainer", 130, ["acrobatics", "performance"], "By Popular Demand", tools=["Disguise kit"], tool_choice=["One musical instrument"]),
        bg("Folk Hero", 131, ["animalHandling", "survival"], "Rustic Hospitality", tools=["Vehicles (land)"], tool_choice=["One type of artisan's tools"]),
        bg("Guild Artisan", 132, ["insight", "persuasion"], "Guild Membership", langs=1, tool_choice=["One type of artisan's tools"]),
        bg("Hermit", 134, ["medicine", "religion"], "Discovery", tools=["Herbalism kit"], langs=1),
        bg("Noble", 135, ["history", "persuasion"], "Position of Privilege", langs=1, tool_choice=["One type of gaming set"]),
        bg("Outlander", 136, ["athletics", "survival"], "Wanderer", langs=1, tool_choice=["One musical instrument"]),
        bg("Sage", 137, ["arcana", "history"], "Researcher", langs=2),
        bg("Sailor", 139, ["athletics", "perception"], "Ship's Passage", tools=["Navigator's tools", "Vehicles (water)"]),
        bg("Soldier", 140, ["athletics", "intimidation"], "Military Rank", tools=["Vehicles (land)"], tool_choice=["One type of gaming set"]),
        bg("Urchin", 141, ["sleightOfHand", "stealth"], "City Secrets", tools=["Disguise kit", "Thieves' tools"]),
    ]


def feats():
    half = lambda fid, abils: [ABIL_CHOICE(fid + "-ability", "+1 ability score", abils, 1)] if len(abils) > 1 else [ASC(abils[0], 1, 20)]
    P = lambda formula, text: {"formula": formula, "text": text}
    fs = [
        ("Alert", None, "+5 to initiative; you can't be surprised while conscious; hidden attackers don't gain advantage against you.", [BON("initiative", 5)]),
        ("Athlete", None, "+1 Str or Dex; standing up costs 5 ft; climbing doesn't cost extra; running jumps after 5 ft.", half("athlete", ["str", "dex"])),
        ("Actor", None, "+1 Cha; advantage on Deception and Performance when passing as someone else; mimic speech.", half("actor", ["cha"]) + [ADV("Deception and Performance while disguised")]),
        ("Charger", None, "After you Dash, a bonus action melee attack (+5 damage) or shove."),
        ("Crossbow Expert", None, "Ignore loading; no disadvantage at 5 ft; bonus action hand crossbow attack after attacking with a one-handed weapon.", [ACT("crossbow-expert", "Hand crossbow attack", "bonus")]),
        ("Defensive Duelist", P("score.dex >= 13", "Dexterity 13"), "Reaction when hit by a melee attack while wielding a finesse weapon: +prof to AC against it.", [ACT("defensive-duelist", "Defensive Duelist", "reaction")]),
        ("Dual Wielder", None, "+1 AC while wielding two melee weapons; two-weapon fighting with non-light weapons.", [BON("ac", 1, note="Wielding a melee weapon in each hand")]),
        ("Dungeon Delver", None, "Advantage on checks to find secret doors and saves against traps; resistance to trap damage.", [ADV("Finding secret doors; saves against traps")]),
        ("Durable", None, "+1 Con; hit dice spent heal at least twice your Con modifier.", half("durable", ["con"])),
        ("Elemental Adept", P("1", "The ability to cast at least one spell"), "Choose a damage type; your spells ignore resistance to it and treat 1s on damage dice as 2s.", [CHOICE("elemental-adept", "Damage type", "text", 1)]),
        ("Grappler", P("score.str >= 13", "Strength 13"), "Advantage on attacks against a creature you're grappling; you can try to pin it.", [ADV("Attacks against a creature you're grappling")]),
        ("Great Weapon Master", None, "Bonus action attack after a melee crit or kill; take -5 to hit for +10 damage with heavy weapons.", [ACT("gwm-attack", "Great Weapon Master attack", "bonus"), REM("attack", "Great Weapon Master: -5 to hit for +10 damage with a heavy weapon.")]),
        ("Healer", None, "Healer's kit stabilizes to 1 HP; action to heal 1d6 + 4 + target's HD count, once per creature per rest.", [ACT("healer", "Healer's kit", "action", roll="1d6 + 4")]),
        ("Heavily Armored", P("1", "Proficiency with medium armor"), "+1 Str; proficiency with heavy armor.", half("heavily-armored", ["str"]) + [PROF("armor", ["Heavy armor"])]),
        ("Heavy Armor Master", P("1", "Proficiency with heavy armor"), "+1 Str; in heavy armor, nonmagical bludgeoning, piercing and slashing damage is reduced by 3.", half("heavy-armor-master", ["str"])),
        ("Inspiring Leader", P("score.cha >= 13", "Charisma 13"), "10 minutes: up to six creatures gain temp HP equal to your level + Cha modifier.", [ACT("inspiring-leader", "Inspiring Leader", "minute", roll="level + mod.cha")]),
        ("Keen Mind", None, "+1 Int; always know north, the hours until sunrise or sunset, and recall anything from the past month.", half("keen-mind", ["int"])),
        ("Lightly Armored", None, "+1 Str or Dex; proficiency with light armor.", half("lightly-armored", ["str", "dex"]) + [PROF("armor", ["Light armor"])]),
        ("Linguist", None, "+1 Int; learn three languages; create ciphers.", half("linguist", ["int"]) + [CHOICE("linguist-languages", "Languages", "language", 3, LANG_ANY)]),
        ("Lucky", None, "Three luck points per long rest: roll an extra d20 for an attack, check or save, or for an attack against you.", [RES("luck-points", "Luck points", 3, "long", color="gold")]),
        ("Mage Slayer", None, "Reaction attack against a nearby caster; your hits impose disadvantage on concentration saves; advantage on saves against spells cast within 5 ft.", [ACT("mage-slayer", "Mage Slayer", "reaction")]),
        ("Magic Initiate", None, "Learn two cantrips and one 1st-level spell from one class list; cast the spell once per long rest.",
         [CHOICE("magic-initiate-cantrips", "Two cantrips", "spell", 2, {"spells": {"list": "any", "level": 0}}),
          CHOICE("magic-initiate-spell", "1st-level spell", "spell", 1, {"spells": {"list": "any", "level": 1}}, grants={"uses": 1, "recharge": "long", "noSlot": True})]),
        ("Martial Adept", None, "Learn two maneuvers and gain one d6 superiority die per short rest.", [CHOICE("martial-adept-maneuvers", "Maneuvers", "option", 2, {"optionSet": "maneuvers"}), RES("superiority-dice", "Superiority dice", 1, "short", die="d6", color="gold")]),
        ("Medium Armor Master", P("1", "Proficiency with medium armor"), "No Stealth disadvantage in medium armor; Dex bonus to AC up to +3."),
        ("Mobile", None, "+10 ft speed; Dash ignores difficult terrain; no opportunity attacks from creatures you attacked.", [BON("speed", 10)]),
        ("Moderately Armored", P("1", "Proficiency with light armor"), "+1 Str or Dex; proficiency with medium armor and shields.", half("moderately-armored", ["str", "dex"]) + [PROF("armor", ["Medium armor", "Shields"])]),
        ("Mounted Combatant", None, "Advantage on melee attacks against unmounted creatures smaller than your mount; redirect attacks to you; mount evasion."),
        ("Observant", None, "+1 Int or Wis; read lips; +5 to passive Perception and Investigation.", half("observant", ["int", "wis"]) + [BON("passive.perception", 5), BON("passive.investigation", 5)]),
        ("Polearm Master", None, "Bonus action butt-end attack (1d4); opportunity attacks when creatures enter your reach.", [ACT("polearm-master", "Polearm butt attack", "bonus", roll="1d4")]),
        ("Resilient", None, "+1 to one ability score and proficiency in saves with it.", [ABIL_CHOICE("resilient-ability", "Ability", ABILS, 1), REM("levelUp", "Resilient: add the matching saving throw to your sheet's proficiencies.")]),
        ("Ritual Caster", P("score.int >= 13 or score.wis >= 13", "Intelligence or Wisdom 13"), "A ritual book with two 1st-level rituals from one class; copy more as you find them.", [CHOICE("ritual-caster", "Rituals", "spell", 2, {"spells": {"list": "any", "level": 1, "ritual": True}}, grants={"noSlot": True})]),
        ("Savage Attacker", None, "Once per turn, reroll a melee weapon's damage dice and use either total."),
        ("Sentinel", None, "Opportunity attacks stop movement; reaction attack when a creature attacks someone else nearby.", [ACT("sentinel", "Sentinel attack", "reaction")]),
        ("Sharpshooter", None, "No disadvantage at long range; ignore half and three-quarters cover; -5 to hit for +10 damage with ranged weapons.", [REM("attack", "Sharpshooter: -5 to hit for +10 damage with a ranged weapon.")]),
        ("Shield Master", None, "Bonus action shove after attacking; add shield AC to Dex saves against single targets; evasion-like reaction.", [ACT("shield-master-shove", "Shield shove", "bonus")]),
        ("Skilled", None, "Proficiency in any three skills or tools.", [CHOICE("skilled", "Skills", "skill", 3, {"skills": "any"})]),
        ("Skulker", P("score.dex >= 13", "Dexterity 13"), "Hide when lightly obscured; misses don't reveal you; dim light doesn't hinder Perception."),
        ("Spell Sniper", P("1", "The ability to cast at least one spell"), "Double range for attack spells; ignore half and three-quarters cover; learn an attack cantrip.", [CHOICE("spell-sniper-cantrip", "Attack cantrip", "spell", 1, {"spells": {"list": "any", "level": 0}})]),
        ("Tavern Brawler", None, "+1 Str or Con; proficiency with improvised weapons; unarmed strikes deal 1d4; bonus action grapple.", half("tavern-brawler", ["str", "con"])),
        ("Tough", None, "Your HP maximum increases by 2 per level.", [BON("hp.perLevel", 2)]),
        ("War Caster", P("1", "The ability to cast at least one spell"), "Advantage on concentration saves; somatic components with hands full; cast a spell as an opportunity attack.", [ADV("Con saves to keep concentration")]),
        ("Weapon Master", None, "+1 Str or Dex; proficiency with four weapons.", half("weapon-master", ["str", "dex"]) + [CHOICE("weapon-master-weapons", "Four weapons", "text", 1)]),
    ]
    names = [f[0] for f in fs]
    out = []
    for name, pre, summary, *fx in fs:
        t = T.section(B, 165, 171, name, stops=[n for n in names if n != name])
        e = {"id": slug(name), "name": name, "page": 165, "text": t if t and len(t) > 40 else summary, "effects": fx[0] if fx else []}
        if t:
            found["yes"] += 1
        else:
            found["no"].append(name)
        if pre:
            e["prerequisite"] = pre
        out.append(e)
    print("feature text found for %d; missing: %s" % (found["yes"], ", ".join(found["no"]) or "none"))
    return out
