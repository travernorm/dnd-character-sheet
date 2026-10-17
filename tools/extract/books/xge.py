"""Xanathar's Guide to Everything (2014): subclasses, racial feats and new invocations.
Structure and effects are written here; feature text comes from your extracted pages."""
import copy, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import *
from kit import Book

X = Book("xge", 1, 195, body=8)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BASE = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "data", "base-pack.json")))["subclasses"]}
CD = {"resource": "channel-divinity", "amount": 1}
BI = {"resource": "bardic-inspiration", "amount": 1}
KI = lambda n: {"resource": "ki", "amount": n}
SP = lambda n: {"resource": "sorcery-points", "amount": n}
BI_DIE = {"1": "1d6", "5": "1d8", "10": "1d10", "15": "1d12"}
ALL = ["str", "dex", "con", "int", "wis", "cha"]


def spells(cls, rows, levels):
    return GRANT([(s, lv) for lv, row in zip(levels, rows) for s in row], cls=cls)


def from_base(sid, cls, name, nxt=None):
    """Subclasses the base pack already builds (with their effects): keep those, add the book's text."""
    e = copy.deepcopy(BASE[sid])
    e["features"] = X.fill(e["features"], name, stops=[nxt] if nxt else [])
    e["page"] = X.locate(name)
    for k in ("text", "_pack", "_src"):
        e.pop(k, None)
    return e


def divine_strike(dtype):
    return F("Divine Strike", 8, "Once per turn, a weapon hit deals an extra 1d8 %s damage (2d8 at 14th level)." % dtype,
             [RIDER("divine-strike", "Divine Strike", damage={"8": "1d8", "14": "2d8"}, damageType=dtype, oncePer="turn", requires=["weapon", "hit"])])


def build():
    S = X.subclass
    subs = [
        S("barbarian", "Path of the Ancestral Guardian", [
            F("Ancestral Protectors", 3, "While raging, the first creature you hit each turn has disadvantage on attacks against others, and those others resist its damage.", [REM("hit", "Ancestral Protectors: first hit while raging hampers that creature's attacks on others.")]),
            F("Spirit Shield", 6, "Reaction while raging when a creature within 30 ft takes damage: reduce it by 2d6 (3d6 at 10th, 4d6 at 14th).", [ACT("spirit-shield", "Spirit Shield", "reaction", when="toggle:raging", roll={"6": "2d6", "10": "3d6", "14": "4d6"})]),
            F("Consult the Spirits", 10, "Cast augury or clairvoyance without a slot, once per short rest.", [RES("consult-the-spirits", "Consult the Spirits", 1, "short")]),
            F("Vengeful Ancestors", 14, "Damage Spirit Shield prevents is dealt back to the attacker as force damage."),
        ], nxt="Path of the Storm Herald"),
        S("barbarian", "Path of the Storm Herald", [
            F("Storm Aura", 3, "While raging you emanate a desert, sea or tundra aura; activate it as a bonus action.", [CHOICE("storm-aura", "Storm environment", "option", 1, {"optionSet": "storm-auras"}), ACT("storm-aura", "Storm Aura", "bonus", when="toggle:raging")]),
            F("Storm Soul", 6, "Resistance from your environment (fire, lightning or cold) and a minor utility."),
            F("Shielding Storm", 10, "Creatures in your aura gain your Storm Soul resistance."),
            F("Raging Storm", 14, "Your aura gains a reaction effect for your environment."),
        ], nxt="Path of the Zealot"),
        S("barbarian", "Path of the Zealot", [
            F("Divine Fury", 3, "While raging, the first creature you hit each turn takes extra 1d6 + half your barbarian level necrotic or radiant damage.",
              [RIDER("divine-fury", "Divine Fury", damage="1d6 + floor(classLevel / 2)", damageType="necrotic or radiant", oncePer="turn", when="toggle:raging", requires=["weapon", "hit"])]),
            F("Warrior of the Gods", 3, "Spells that raise you from the dead need no material components."),
            F("Fanatical Focus", 6, "Once per rage, reroll a failed saving throw."),
            F("Zealous Presence", 10, "Bonus action: up to ten creatures within 60 ft get advantage on attacks and saves until your next turn. Once per long rest.", [RES("zealous-presence", "Zealous Presence", 1, "long"), ACT("use-zealous-presence", "Zealous Presence", "bonus", cost={"resource": "zealous-presence", "amount": 1})]),
            F("Rage Beyond Death", 14, "While raging, dropping to 0 HP doesn't knock you unconscious until the rage ends."),
        ]),
        S("bard", "College of Glamour", [
            F("Mantle of Inspiration", 3, "Bonus action: spend a Bardic Inspiration; Cha-modifier creatures within 60 ft gain temp HP (5, rising to 14) and can move without provoking.", [ACT("mantle-of-inspiration", "Mantle of Inspiration", "bonus", cost=BI, roll={"3": "5", "5": "8", "10": "11", "15": "14"})]),
            F("Enthralling Performance", 3, "After performing for 1 minute, charm up to Cha-modifier listeners (Wisdom save). Once per short rest.", [RES("enthralling-performance", "Enthralling Performance", 1, "short"), ACT("use-enthralling-performance", "Enthralling Performance", "minute", cost={"resource": "enthralling-performance", "amount": 1}, save={"ability": "wis", "dc": "spellDC"})]),
            F("Mantle of Majesty", 6, "Bonus action: cast command, then command again as a bonus action each turn for 1 minute (concentration). Once per long rest.", [RES("mantle-of-majesty", "Mantle of Majesty", 1, "long"), ACT("use-mantle-of-majesty", "Mantle of Majesty", "bonus", cost={"resource": "mantle-of-majesty", "amount": 1})]),
            F("Unbreakable Majesty", 14, "Bonus action: attackers must make a Charisma save or choose another target, for 1 minute. Once per short rest.", [RES("unbreakable-majesty", "Unbreakable Majesty", 1, "short"), ACT("use-unbreakable-majesty", "Unbreakable Majesty", "bonus", cost={"resource": "unbreakable-majesty", "amount": 1})]),
        ], nxt="College of Swords"),
        S("bard", "College of Swords", [
            F("Bonus Proficiencies", 3, "Proficiency with medium armor and the scimitar; use any simple or martial melee weapon you're proficient with as a spellcasting focus.", [PROF("armor", ["Medium armor"]), PROF("weapon", ["Scimitars"])], id="swords-bonus-proficiencies"),
            F("Fighting Style", 3, "Choose Dueling or Two-Weapon Fighting.", [CHOICE("fighting-style", "Fighting Style", "option", 1, {"optionSet": "fighting-styles"})], id="swords-fighting-style"),
            F("Blade Flourish", 3, "When you take the Attack action, +10 ft speed; on a hit, spend a Bardic Inspiration for a Defensive, Slashing or Mobile Flourish that adds the die to damage. Once per turn.",
              [RIDER("blade-flourish", "Blade Flourish", damage=BI_DIE, cost=BI, oncePer="turn", requires=["weapon", "hit"])]),
            F("Extra Attack", 6, "Attack twice when you take the Attack action.", [SET("attacksPerAction", 2)], id="swords-extra-attack"),
            F("Master's Flourish", 14, "Use a d6 instead of spending Bardic Inspiration for a flourish.", [RIDER("masters-flourish", "Master's Flourish (d6)", damage="1d6", oncePer="turn", requires=["weapon", "hit"])]),
        ], nxt="College of Whispers"),
        from_base("college-of-whispers", "bard", "College of Whispers"),
        S("cleric", "Forge Domain", [
            F("Bonus Proficiencies", 1, "Proficiency with heavy armor and smith's tools.", [PROF("armor", ["Heavy armor"]), PROF("tool", ["Smith's tools"])], id="forge-bonus-proficiencies"),
            F("Blessing of the Forge", 1, "After a long rest, make a weapon or armor +1 until your next long rest.", [RES("blessing-of-the-forge", "Blessing of the Forge", 1, "long")]),
            F("Channel Divinity: Artisan's Blessing", 2, "Hour-long ritual to craft a metal item worth up to 100 gp.", [ACT("artisans-blessing", "Artisan's Blessing", "minute", cost=CD)]),
            F("Soul of the Forge", 6, "Resistance to fire damage; +1 AC while wearing heavy armor.", [RESIST("fire"), BON("ac", 1, note="In heavy armor")]),
            divine_strike("fire"),
            F("Saint of Forge and Fire", 17, "Immune to fire; in heavy armor, resist nonmagical bludgeoning, piercing and slashing.", [{"type": "immunity", "damage": ["fire"]}]),
        ], spells=spells("cleric", [["identify", "searing-smite"], ["heat-metal", "magic-weapon"], ["elemental-weapon", "protection-from-energy"], ["fabricate", "wall-of-fire"], ["animate-objects", "creation"]], (1, 3, 5, 7, 9)), nxt="Grave Domain"),
        S("cleric", "Grave Domain", [
            F("Circle of Mortality", 1, "Healing a creature at 0 HP uses the maximum dice; you know spare the dying and cast it as a bonus action at 30 ft.", [GRANT([{"id": "spare-the-dying", "econ": "bonus"}], cls="cleric")]),
            F("Eyes of the Grave", 1, "Action: sense undead within 60 ft. Wis modifier uses per long rest.", [RES("eyes-of-the-grave", "Eyes of the Grave", "max(1, mod.wis)", "long"), ACT("use-eyes-of-the-grave", "Eyes of the Grave", "action", cost={"resource": "eyes-of-the-grave", "amount": 1})]),
            F("Channel Divinity: Path to the Grave", 2, "Action: curse a creature within 30 ft; the next attack against it deals vulnerable damage.", [ACT("path-to-the-grave", "Path to the Grave", "action", cost=CD)]),
            F("Sentinel at Death's Door", 6, "Reaction: turn a critical hit within 30 ft into a normal hit. Wis modifier uses per long rest.", [RES("sentinel-at-deaths-door", "Sentinel at Death's Door", "max(1, mod.wis)", "long"), ACT("use-sentinel-at-deaths-door", "Sentinel at Death's Door", "reaction", cost={"resource": "sentinel-at-deaths-door", "amount": 1})]),
            F("Potent Spellcasting", 8, "Add your Wisdom modifier to the damage of your cleric cantrips.", [BON("damage.spell", "mod.wis", note="Cleric cantrips")]),
            F("Keeper of Souls", 17, "When an enemy dies within 60 ft, you or an ally regains HP equal to its Hit Dice, once per turn."),
        ], spells=spells("cleric", [["bane", "false-life"], ["gentle-repose", "ray-of-enfeeblement"], ["revivify", "vampiric-touch"], ["blight", "death-ward"], ["antilife-shell", "raise-dead"]], (1, 3, 5, 7, 9))),
        S("druid", "Circle of Dreams", [
            F("Balm of the Summer Court", 2, "A pool of d6s equal to your druid level; bonus action to heal a creature within 120 ft with some of them (plus 1 temp HP each).", [RES("balm-of-the-summer-court", "Balm of the Summer Court (d6s)", "classLevel", "long"), ACT("use-balm", "Balm of the Summer Court", "bonus", cost={"resource": "balm-of-the-summer-court", "amount": 1}, roll="1d6")]),
            F("Hearth of Moonlight and Shadow", 6, "During a rest, a 30-ft sphere gives +5 to Stealth and Perception and hides light."),
            F("Hidden Paths", 10, "Bonus action: teleport 60 ft (or a willing creature 30 ft as an action). Wis modifier uses per long rest.", [RES("hidden-paths", "Hidden Paths", "max(1, mod.wis)", "long"), ACT("use-hidden-paths", "Hidden Paths", "bonus", cost={"resource": "hidden-paths", "amount": 1})]),
            F("Walker in Dreams", 14, "After a short rest, cast dream, scrying or teleportation circle without a slot. Once per long rest.", [RES("walker-in-dreams", "Walker in Dreams", 1, "long")]),
        ], nxt="Circle of the Shepherd"),
        S("druid", "Circle of the Shepherd", [
            F("Speech of the Woods", 2, "You speak Sylvan and can understand beasts.", [PROF("language", ["Sylvan"])]),
            F("Spirit Totem", 2, "Bonus action: summon a bear, hawk or unicorn spirit aura for 1 minute. Once per short rest.", [RES("spirit-totem", "Spirit Totem", 1, "short"), ACT("use-spirit-totem", "Spirit Totem", "bonus", cost={"resource": "spirit-totem", "amount": 1})]),
            F("Mighty Summoner", 6, "Beasts and fey you summon have 2 extra HP per Hit Die and magical natural weapons."),
            F("Guardian Spirit", 10, "Your summoned beasts and fey in your totem aura regain HP equal to half your druid level each turn."),
            F("Faithful Summons", 14, "When you drop to 0 HP or are incapacitated, gain the effect of conjure animals at 9th level. Once per long rest.", [RES("faithful-summons", "Faithful Summons", 1, "long")]),
        ]),
        S("fighter", "Arcane Archer", [
            F("Arcane Archer Lore", 3, "Proficiency in Arcana or Nature, and learn prestidigitation or druidcraft.", [CHOICE("arcane-archer-skill", "Arcane Archer skill", "skill", 1, {"skills": ["arcana", "nature"]}), CHOICE("arcane-archer-cantrip", "Cantrip (prestidigitation or druidcraft)", "spell", 1, {"spells": {"list": "any", "level": 0}})]),
            F("Arcane Shot", 3, "Two Arcane Shot uses per short rest; learn Arcane Shot options (more at 7th, 10th, 15th and 18th level). Once per turn.",
              [RES("arcane-shot", "Arcane Shot", 2, "short", color="psy"), CHOICE("arcane-shots", "Arcane Shot options", "option", {"3": 2, "7": 3, "10": 4, "15": 5, "18": 6}, {"optionSet": "arcane-shots"})]),
            F("Magic Arrow", 7, "Nonmagical arrows you fire count as magical."),
            F("Curving Shot", 7, "Bonus action after a miss with a magic arrow: reroll against another target within 60 ft.", [ACT("curving-shot", "Curving Shot", "bonus")]),
            F("Ever-Ready Shot", 15, "Regain one Arcane Shot use when you roll initiative with none.", [REM("initiative", "Ever-Ready Shot: regain one Arcane Shot if you have none.")]),
        ], nxt="Cavalier"),
        S("fighter", "Cavalier", [
            F("Bonus Proficiency", 3, "One of Animal Handling, History, Insight, Performance or Persuasion, or a language.", [CHOICE("cavalier-skill", "Bonus Proficiency", "skill", 1, {"skills": ["animalHandling", "history", "insight", "performance", "persuasion"]})], id="cavalier-bonus-proficiency"),
            F("Born to the Saddle", 3, "Advantage on saves to avoid falling off; mount and dismount for 5 ft of movement."),
            F("Unwavering Mark", 3, "Mark creatures you hit; if a marked creature attacks someone else, make a bonus action attack with advantage and extra damage. Str modifier uses per long rest.",
              [RES("unwavering-mark", "Unwavering Mark", "max(1, mod.str)", "long"), ACT("use-unwavering-mark", "Unwavering Mark attack", "bonus", cost={"resource": "unwavering-mark", "amount": 1}, roll="floor(classLevel / 2)")]),
            F("Warding Maneuver", 7, "Reaction when a creature within 5 ft is hit: add 1d8 to its AC, and it resists the damage if still hit. Con modifier uses per long rest.",
              [RES("warding-maneuver", "Warding Maneuver", "max(1, mod.con)", "long"), ACT("use-warding-maneuver", "Warding Maneuver", "reaction", cost={"resource": "warding-maneuver", "amount": 1}, roll="1d8")]),
            F("Hold the Line", 10, "Creatures moving within your reach provoke opportunity attacks; a hit reduces their speed to 0."),
            F("Ferocious Charger", 15, "After moving 10 ft straight, a hit can knock the target prone (Str save). Once per turn."),
            F("Vigilant Defender", 18, "A special reaction for opportunity attacks on every other creature's turn."),
        ], nxt="Samurai"),
        S("fighter", "Samurai", [
            F("Bonus Proficiency", 3, "One of History, Insight, Performance or Persuasion, or a language.", [CHOICE("samurai-skill", "Bonus Proficiency", "skill", 1, {"skills": ["history", "insight", "performance", "persuasion"]})], id="samurai-bonus-proficiency"),
            F("Fighting Spirit", 3, "Bonus action: advantage on weapon attacks this turn and temp HP (5, 10 at 10th, 15 at 15th). Three times per long rest.",
              [RES("fighting-spirit", "Fighting Spirit", 3, "long", color="gold"), ACT("use-fighting-spirit", "Fighting Spirit", "bonus", cost={"resource": "fighting-spirit", "amount": 1}, tempHp={"3": 5, "10": 10, "15": 15})]),
            F("Elegant Courtier", 7, "Add your Wis modifier to Persuasion checks; proficiency in Wisdom saves (or Int or Cha).", [BON("skill.persuasion", "mod.wis"), PROF("save", ["wis"])]),
            F("Tireless Spirit", 10, "Regain one Fighting Spirit use when you roll initiative with none.", [REM("initiative", "Tireless Spirit: regain one Fighting Spirit if you have none.")]),
            F("Rapid Strike", 15, "Once per turn, trade advantage on an attack for an extra attack."),
            F("Strength before Death", 18, "Reaction when reduced to 0 HP: take an extra turn first. Once per long rest.", [RES("strength-before-death", "Strength before Death", 1, "long"), ACT("use-strength-before-death", "Strength before Death", "reaction", cost={"resource": "strength-before-death", "amount": 1})]),
        ]),
        S("monk", "Way of the Drunken Master", [
            F("Bonus Proficiencies", 3, "Proficiency in Performance and with brewer's supplies.", [PROF("skill", ["performance"]), PROF("tool", ["Brewer's supplies"])], id="drunken-bonus-proficiencies"),
            F("Drunken Technique", 3, "Flurry of Blows also gives Disengage and +10 ft speed."),
            F("Tipsy Sway", 6, "Stand up for 5 ft; reaction when missed in melee to redirect the attack.", [ACT("tipsy-sway", "Redirect Attack", "reaction", cost=KI(1))]),
            F("Drunkard's Luck", 11, "Spend 2 ki to cancel disadvantage on a check, attack or save.", [ACT("drunkards-luck", "Drunkard's Luck", "free", cost=KI(2))]),
            F("Intoxicated Frenzy", 17, "Flurry of Blows can make up to three extra attacks against different targets."),
        ], nxt="Way of the Kensei"),
        S("monk", "Way of the Kensei", [
            F("Path of the Kensei", 3, "Choose kensei weapons; +2 AC after an unarmed strike while holding one; extra 1d4 damage on a hit as a bonus action.", [CHOICE("kensei-weapons", "Kensei weapons", "text", 1), ACT("agile-parry", "Agile Parry (+2 AC)", "free"), ACT("kensei-shot", "Kensei's Shot", "bonus")]),
            F("One with the Blade", 6, "Kensei weapons count as magical; spend 1 ki for extra martial arts die damage once per turn.", [RIDER("deft-strike", "Deft Strike", damage="col.martialArts", cost=KI(1), oncePer="turn", requires=["weapon", "hit"])]),
            F("Sharpen the Blade", 11, "Bonus action: spend up to 3 ki for that bonus to attacks and damage with a kensei weapon for 1 minute.", [ACT("sharpen-the-blade", "Sharpen the Blade", "bonus", cost=KI(1))]),
            F("Unerring Accuracy", 17, "Once per turn, reroll a missed monk weapon attack."),
        ], nxt="Way of the Sun Soul"),
        S("monk", "Way of the Sun Soul", [
            F("Radiant Sun Bolt", 3, "A 30-ft ranged spell attack dealing martial arts die + Dex radiant; spend 1 ki to make two as a bonus action.",
              [ACT("radiant-sun-bolt", "Radiant Sun Bolt", "action", damage={"dice": "col.martialArts + mod.dex", "type": "radiant"}), ACT("sun-bolt-flurry", "Sun bolts (bonus)", "bonus", cost=KI(1))]),
            F("Searing Arc Strike", 6, "After the Attack action, spend 2 ki to cast burning hands as a bonus action.", [ACT("searing-arc-strike", "Searing Arc Strike", "bonus", cost=KI(2))]),
            F("Searing Sunburst", 11, "Action: a 20-ft sphere of light; creatures take 2d6 radiant (Con save).", [ACT("searing-sunburst", "Searing Sunburst", "action", damage={"dice": "2d6", "type": "radiant"}, save={"ability": "con", "dc": "8 + prof + mod.wis"})]),
            F("Sun Shield", 17, "Shed bright light; reaction when hit in melee to deal 5 + Wis modifier radiant.", [ACT("sun-shield", "Sun Shield", "reaction", damage={"dice": "5 + mod.wis", "type": "radiant"})]),
        ]),
        S("paladin", "Oath of Conquest", [
            F("Channel Divinity: Conquering Presence", 3, "Action: creatures within 30 ft make a Wisdom save or are frightened for 1 minute.", [ACT("conquering-presence", "Conquering Presence", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
            F("Channel Divinity: Guided Strike", 3, "Gain +10 to an attack roll.", [ACT("conquest-guided-strike", "Guided Strike", "free", cost=CD)], id="conquest-guided-strike"),
            F("Aura of Conquest", 7, "Frightened creatures within 10 ft have speed 0 and take psychic damage equal to half your paladin level."),
            F("Scornful Rebuke", 15, "When a creature hits you, it takes psychic damage equal to your Cha modifier."),
            F("Invincible Conqueror", 20, "Action: for 1 minute, resistance to all damage, an extra attack, and crits on 19-20. Once per long rest.", [RES("invincible-conqueror", "Invincible Conqueror", 1, "long"), ACT("use-invincible-conqueror", "Invincible Conqueror", "action", cost={"resource": "invincible-conqueror", "amount": 1})]),
        ], spells=spells("paladin", [["armor-of-agathys", "command"], ["hold-person", "spiritual-weapon"], ["bestow-curse", "fear"], ["dominate-beast", "stoneskin"], ["cloudkill", "dominate-person"]], (3, 5, 9, 13, 17)), nxt="Oath of Redemption"),
        S("paladin", "Oath of Redemption", [
            F("Channel Divinity: Emissary of Peace", 3, "Bonus action: +5 to Persuasion checks for 10 minutes.", [ACT("emissary-of-peace", "Emissary of Peace", "bonus", cost=CD)]),
            F("Channel Divinity: Rebuke the Violent", 3, "Reaction when a creature within 30 ft deals damage: it takes radiant damage equal to what it dealt (Wisdom save for half).", [ACT("rebuke-the-violent", "Rebuke the Violent", "reaction", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
            F("Aura of the Guardian", 7, "Reaction when a creature within 10 ft takes damage: take it instead.", [ACT("aura-of-the-guardian", "Aura of the Guardian", "reaction")]),
            F("Protective Spirit", 15, "At the end of your turn below half HP, regain 1d6 + half your paladin level.", [REM("turnStart", "Protective Spirit: below half HP, regain 1d6 + half paladin level at the end of your turn.")]),
            F("Emissary of Redemption", 20, "Resistance to damage from creatures; they take radiant damage equal to half what they deal you."),
        ], spells=spells("paladin", [["sanctuary", "sleep"], ["calm-emotions", "hold-person"], ["counterspell", "hypnotic-pattern"], ["resilient-sphere", "stoneskin"], ["hold-monster", "wall-of-force"]], (3, 5, 9, 13, 17))),
        from_base("gloom-stalker", "ranger", "Gloom Stalker", nxt="Horizon Walker"),
        S("ranger", "Horizon Walker", [
            F("Detect Portal", 3, "Action: sense the nearest planar portal within 1 mile. Once per short rest.", [RES("detect-portal", "Detect Portal", 1, "short")]),
            F("Planar Warrior", 3, "Bonus action: your next hit on a creature this turn deals force damage plus 1d8 (2d8 at 11th).", [ACT("planar-warrior", "Planar Warrior", "bonus"), RIDER("planar-warrior", "Planar Warrior", damage={"3": "1d8", "11": "2d8"}, damageType="force", oncePer="turn", requires=["weapon", "hit"])]),
            F("Ethereal Step", 7, "Bonus action: cast etherealness until the end of the turn. Once per short rest.", [RES("ethereal-step", "Ethereal Step", 1, "short"), ACT("use-ethereal-step", "Ethereal Step", "bonus", cost={"resource": "ethereal-step", "amount": 1})]),
            F("Distant Strike", 11, "When you take the Attack action, teleport 10 ft before each attack; attack a third creature if you hit two."),
            F("Spectral Defense", 15, "Reaction when hit: gain resistance to that attack's damage.", [ACT("spectral-defense", "Spectral Defense", "reaction")]),
        ], spells=spells("ranger", [["protection-from-evil-and-good"], ["misty-step"], ["haste"], ["banishment"], ["teleportation-circle"]], (3, 5, 9, 13, 17)), nxt="Monster Slayer"),
        S("ranger", "Monster Slayer", [
            F("Hunter's Sense", 3, "Action: learn a creature's immunities, resistances and vulnerabilities. Wis modifier uses per long rest.", [RES("hunters-sense", "Hunter's Sense", "max(1, mod.wis)", "long"), ACT("use-hunters-sense", "Hunter's Sense", "action", cost={"resource": "hunters-sense", "amount": 1})]),
            F("Slayer's Prey", 3, "Bonus action: designate a creature; the first hit on it each turn deals an extra 1d6.", [ACT("slayers-prey", "Slayer's Prey", "bonus"), RIDER("slayers-prey", "Slayer's Prey", damage="1d6", oncePer="turn", requires=["weapon", "hit"])]),
            F("Supernatural Defense", 7, "Add 1d6 to saves and grapple escapes against your Slayer's Prey."),
            F("Magic-User's Nemesis", 11, "Reaction when a creature casts or teleports within 60 ft: it makes a Wisdom save or the attempt is wasted. Once per short rest.", [RES("magic-users-nemesis", "Magic-User's Nemesis", 1, "short"), ACT("use-magic-users-nemesis", "Magic-User's Nemesis", "reaction", cost={"resource": "magic-users-nemesis", "amount": 1}, save={"ability": "wis", "dc": "spellDC"})]),
            F("Slayer's Counter", 15, "Reaction when your prey forces a save: attack it, and succeed on the save if you hit.", [ACT("slayers-counter", "Slayer's Counter", "reaction")]),
        ], spells=spells("ranger", [["protection-from-evil-and-good"], ["zone-of-truth"], ["magic-circle"], ["banishment"], ["hold-monster"]], (3, 5, 9, 13, 17))),
        S("rogue", "Inquisitive", [
            F("Ear for Deceit", 3, "Treat a roll of 7 or lower as 8 on Insight checks to detect lies."),
            F("Eye for Detail", 3, "Bonus action: Perception to spot a hidden creature or Investigation to find clues.", [ACT("eye-for-detail", "Eye for Detail", "bonus")]),
            F("Insightful Fighting", 3, "Bonus action: Insight against a creature's Deception; on a success you can Sneak Attack it without advantage for 1 minute.", [ACT("insightful-fighting", "Insightful Fighting", "bonus")]),
            F("Steady Eye", 9, "Advantage on Perception and Investigation if you move half speed or less.", [ADV("Perception and Investigation if you move half speed or less")]),
            F("Unerring Eye", 13, "Action: sense illusions and shapechangers within 30 ft. Wis modifier uses per long rest.", [RES("unerring-eye", "Unerring Eye", "max(1, mod.wis)", "long"), ACT("use-unerring-eye", "Unerring Eye", "action", cost={"resource": "unerring-eye", "amount": 1})]),
            F("Eye for Weakness", 17, "Sneak Attack deals an extra 3d6 against your Insightful Fighting target.", [RIDER("eye-for-weakness", "Eye for Weakness", damage="3d6", oncePer="turn", requires=["hit"])]),
        ], nxt="Mastermind"),
        S("rogue", "Mastermind", [
            F("Master of Intrigue", 3, "Proficiency with the disguise kit, forgery kit and a gaming set; two languages; mimic speech.", [PROF("tool", ["Disguise kit", "Forgery kit"]), CHOICE("mastermind-languages", "Two languages", "language", 2, {"list": ["any"]})]),
            F("Master of Tactics", 3, "Help as a bonus action, at 30 ft when the target can see or hear you.", [ACT("master-of-tactics", "Help (Master of Tactics)", "bonus")]),
            F("Insightful Manipulator", 9, "Study a creature for 1 minute to compare its mental scores to yours."),
            F("Misdirection", 13, "Reaction when targeted while a creature gives you cover: it's targeted instead.", [ACT("misdirection", "Misdirection", "reaction")]),
            F("Soul of Deceit", 17, "Your thoughts can't be read, and magic can't compel you to tell the truth."),
        ], nxt="Scout"),
        S("rogue", "Scout", [
            F("Skirmisher", 3, "Reaction when an enemy ends its turn within 5 ft: move half your speed without provoking.", [ACT("skirmisher", "Skirmisher", "reaction")]),
            F("Survivalist", 3, "Proficiency and expertise in Nature and Survival.", [PROF("skill", ["nature", "survival"]), EXP(["nature", "survival"])]),
            F("Superior Mobility", 9, "+10 ft to your walking, climbing and swimming speeds.", [BON("speed", 10)]),
            F("Ambush Master", 13, "Advantage on initiative; allies get advantage against the first creature you hit in the first round.", [ADV("Initiative")]),
            F("Sudden Strike", 17, "Make a second Sneak Attack against a different target with the Cunning Action bonus attack."),
        ], nxt="Swashbuckler"),
        S("rogue", "Swashbuckler", [
            F("Fancy Footwork", 3, "Creatures you attack in melee can't make opportunity attacks against you this turn."),
            F("Rakish Audacity", 3, "Add your Cha modifier to initiative; Sneak Attack a lone creature within 5 ft without advantage.", [BON("initiative", "mod.cha")]),
            F("Panache", 9, "Action: Persuasion against Insight to goad an enemy or charm a creature for 1 minute.", [ACT("panache", "Panache", "action")]),
            F("Elegant Maneuver", 13, "Bonus action: advantage on your next Acrobatics or Athletics check this turn.", [ACT("elegant-maneuver", "Elegant Maneuver", "bonus")]),
            F("Master Duelist", 17, "Reroll a missed attack with advantage. Once per short rest.", [RES("master-duelist", "Master Duelist", 1, "short")]),
        ]),
        S("sorcerer", "Divine Soul", [
            F("Divine Magic", 1, "Choose spells from the cleric list as sorcerer spells, and an affinity (good, evil, law, chaos or neutrality) that grants a spell.", [CHOICE("divine-affinity", "Affinity", "option", 1, {"optionSet": "divine-affinities"})]),
            F("Favored by the Gods", 1, "Add 2d4 to a failed save or missed attack. Once per short rest.", [RES("favored-by-the-gods", "Favored by the Gods", 1, "short"), ACT("use-favored-by-the-gods", "Favored by the Gods", "free", cost={"resource": "favored-by-the-gods", "amount": 1}, roll="2d4")]),
            F("Empowered Healing", 6, "Spend 1 sorcery point to reroll healing dice for a creature within 5 ft, once per turn."),
            F("Otherworldly Wings", 14, "Bonus action: spectral wings for a 30-ft flying speed.", [ACT("otherworldly-wings", "Otherworldly Wings", "bonus"), SPEED("fly", 30)]),
            F("Unearthly Recovery", 18, "Bonus action below half HP: regain HP equal to half your maximum. Once per long rest.", [RES("unearthly-recovery", "Unearthly Recovery", 1, "long"), ACT("use-unearthly-recovery", "Unearthly Recovery", "bonus", cost={"resource": "unearthly-recovery", "amount": 1})]),
        ], nxt="Shadow Magic"),
        S("sorcerer", "Shadow Magic", [
            F("Eyes of the Dark", 1, "Darkvision 120 ft; from 3rd level, cast darkness for 2 sorcery points and see through it.", [SENSE("darkvision", 120), GRANT([{"id": "darkness", "minLevel": 3, "noSlot": True}], cls="sorcerer")]),
            F("Strength of the Grave", 1, "When damage drops you to 0 HP, Charisma save (DC 5 + damage) to drop to 1 instead. Once per long rest.", [RES("strength-of-the-grave", "Strength of the Grave", 1, "long")]),
            F("Hound of Ill Omen", 6, "Bonus action, 3 sorcery points: summon a dire-wolf hound that hounds a target, giving it disadvantage on saves against your spells.", [ACT("hound-of-ill-omen", "Hound of Ill Omen", "bonus", cost=SP(3))]),
            F("Shadow Walk", 14, "Bonus action in dim light or darkness: teleport up to 120 ft to another such space.", [ACT("shadow-walk", "Shadow Walk", "bonus")]),
            F("Umbral Form", 18, "Bonus action, 6 sorcery points: become shadow for 1 minute, resisting all but force and radiant damage.", [ACT("umbral-form", "Umbral Form", "bonus", cost=SP(6))]),
        ], nxt="Storm Sorcery"),
        S("sorcerer", "Storm Sorcery", [
            F("Wind Speaker", 1, "Speak Primordial and its dialects.", [PROF("language", ["Primordial"])]),
            F("Tempestuous Magic", 1, "After casting a spell of 1st level or higher, bonus action: fly 10 ft without provoking.", [ACT("tempestuous-magic", "Tempestuous Magic", "bonus")]),
            F("Heart of the Storm", 6, "Resistance to lightning and thunder; casting a lightning or thunder spell deals half your sorcerer level to nearby creatures.", [RESIST("lightning", "thunder")]),
            F("Storm Guide", 6, "Action: calm rain or change the wind's direction around you."),
            F("Storm's Fury", 14, "Reaction when hit in melee: deal lightning damage equal to your sorcerer level and push the attacker 20 ft (Str save).", [ACT("storms-fury", "Storm's Fury", "reaction", damage={"dice": "classLevel", "type": "lightning"})]),
            F("Wind Soul", 18, "Immune to lightning and thunder; 60-ft flying speed.", [{"type": "immunity", "damage": ["lightning", "thunder"]}, SPEED("fly", 60)]),
        ]),
        S("warlock", "The Celestial", [
            F("Bonus Cantrips", 1, "You know light and sacred flame.", [GRANT([("light", 1), ("sacred-flame", 1)], cls="warlock")], id="celestial-bonus-cantrips"),
            F("Healing Light", 1, "A pool of d6s equal to 1 + your warlock level; bonus action to heal a creature within 60 ft with up to Cha-modifier dice.",
              [RES("healing-light", "Healing Light (d6s)", "1 + classLevel", "long"), ACT("use-healing-light", "Healing Light", "bonus", cost={"resource": "healing-light", "amount": 1}, roll="1d6")]),
            F("Radiant Soul", 6, "Resistance to radiant damage; add your Cha modifier to one radiant or fire damage roll of your spells.", [RESIST("radiant"), BON("damage.spell", "mod.cha", note="Radiant or fire spells")]),
            F("Celestial Resilience", 10, "After a rest, you gain temp HP equal to your warlock level + Cha modifier, and up to five allies half that."),
            F("Searing Vengeance", 14, "When you make a death save, instead regain half your HP, stand, and blind nearby enemies with radiant damage. Once per long rest.", [RES("searing-vengeance", "Searing Vengeance", 1, "long")]),
        ], nxt="The Hexblade"),
        S("warlock", "The Hexblade", [
            F("Hexblade's Curse", 1, "Bonus action: curse a creature for 1 minute; add your proficiency bonus to damage against it, crit on 19-20, and heal when it dies. Once per short rest.",
              [RES("hexblades-curse", "Hexblade's Curse", 1, "short", color="psy"), ACT("use-hexblades-curse", "Hexblade's Curse", "bonus", cost={"resource": "hexblades-curse", "amount": 1}),
               RIDER("hexblades-curse", "Hexblade's Curse", damage="prof", requires=["hit"])]),
            F("Hex Warrior", 1, "Proficiency with medium armor, shields and martial weapons; use Charisma for attacks with one chosen weapon.", [PROF("armor", ["Medium armor", "Shields"]), PROF("weapon", ["Martial weapons"])]),
            F("Accursed Specter", 6, "When you slay a humanoid, raise a specter servant until your next long rest. Once per long rest.", [RES("accursed-specter", "Accursed Specter", 1, "long")]),
            F("Armor of Hexes", 10, "Reaction when your cursed target hits you: roll a d6; on 4 or higher, it misses.", [ACT("armor-of-hexes", "Armor of Hexes", "reaction", roll="1d6")]),
            F("Master of Hexes", 14, "When your cursed target dies, move the curse to another creature within 30 ft."),
        ]),
        S("wizard", "War Magic", [
            F("Arcane Deflection", 2, "Reaction when hit or failing a save: +2 AC or +4 to the save; then only cantrips until your next turn ends.", [ACT("arcane-deflection", "Arcane Deflection", "reaction")]),
            F("Tactical Wit", 2, "Add your Intelligence modifier to initiative.", [BON("initiative", "mod.int")]),
            F("Power Surge", 6, "Store power surges (up to your Int modifier); spend one to add half your wizard level as force damage to a spell, once per turn.",
              [RES("power-surge", "Power Surge", "max(1, mod.int)", "long", color="psy")]),
            F("Durable Magic", 10, "+2 AC and +2 to all saves while concentrating on a spell.", [BON("ac", 2, when="concentrating"), BON("save.all", 2, when="concentrating")]),
            F("Deflecting Shroud", 14, "Arcane Deflection also deals half your wizard level force damage to up to three creatures within 60 ft."),
        ]),
    ]
    feats = racial_feats()
    sets = option_sets()
    X.report()
    return {"subclasses": subs, "feats": feats, "optionSets": sets}


def option_sets():
    arcane = lambda n, t, dmg, dt: F(n, text=t, effects=[RIDER(slug(n), n, damage=dmg, damageType=dt, cost={"resource": "arcane-shot", "amount": 1}, oncePer="turn", requires=["ranged", "hit"])])
    shots = [
        arcane("Banishing Arrow", "Cha save or banished to the Feywild until your next turn; 2d6 force at 18th level.", {"18": "2d6"}, "force"),
        arcane("Beguiling Arrow", "2d6 psychic; Wis save or charmed by an ally.", {"3": "2d6", "18": "4d6"}, "psychic"),
        arcane("Bursting Arrow", "2d6 force to creatures within 10 ft of the target.", {"3": "2d6", "18": "4d6"}, "force"),
        arcane("Enfeebling Arrow", "2d6 necrotic; Con save or its weapon damage is halved.", {"3": "2d6", "18": "4d6"}, "necrotic"),
        arcane("Grasping Arrow", "2d6 poison; brambles slow it and hurt it as it moves.", {"3": "2d6", "18": "4d6"}, "poison"),
        arcane("Piercing Arrow", "A 30-ft line of creatures make Dex saves; 1d6 extra piercing.", {"3": "1d6", "18": "2d6"}, "piercing"),
        arcane("Seeking Arrow", "Ignores cover and finds a creature you've seen in the last minute; 1d6 force.", {"3": "1d6", "18": "2d6"}, "force"),
        arcane("Shadow Arrow", "2d6 psychic; Wis save or can't see beyond 5 ft.", {"3": "2d6", "18": "4d6"}, "psychic"),
    ]
    X.fill(shots, "Arcane Shot Options")
    auras = [F("Desert", text="Creatures in your aura take fire damage (2, rising with level); Storm Soul: fire resistance.", id="storm-desert"),
             F("Sea", text="Lightning strike on one creature (1d6, rising); Storm Soul: lightning resistance, breathe underwater.", id="storm-sea"),
             F("Tundra", text="Allies in your aura gain temp HP (2, rising); Storm Soul: cold resistance.", id="storm-tundra")]
    affinity = [F(n, text="Affinity grants %s." % s.replace("-", " "), effects=[GRANT([(s, 1)], cls="sorcerer")], id="affinity-" + slug(n))
                for n, s in [("Good", "cure-wounds"), ("Evil", "inflict-wounds"), ("Law", "bless"), ("Chaos", "bane"), ("Neutrality", "protection-from-evil-and-good")]]
    pact = {"resource": "pact", "amount": 1}
    inv = [
        F("Aspect of the Moon", text="You don't need sleep and can rest while keeping watch. (Pact of the Tome)"),
        F("Cloak of Flies", text="Bonus action: an aura deals poison damage (Cha modifier) to creatures ending their turn in it; advantage on Intimidation. Once per short rest. (5th level)", effects=[ACT("cloak-of-flies", "Cloak of Flies", "bonus")]),
        F("Eldritch Smite", text="Once per turn, spend a pact slot on a pact weapon hit: +1d8 force plus 1d8 per slot level, and knock Huge or smaller prone. (5th level, Pact of the Blade)",
          effects=[RIDER("eldritch-smite", "Eldritch Smite", damage="1d8 + 1d8", damageType="force", cost=pact, oncePer="turn", requires=["weapon", "hit"])]),
        F("Ghostly Gaze", text="Action: see through solid objects to 30 ft for 1 minute. Once per short rest. (7th level)"),
        F("Gift of the Depths", text="Breathe underwater and swim at your walking speed; water breathing once per long rest. (5th level)", effects=[SPEED("swim", "walk")]),
        F("Gift of the Ever-Living Ones", text="Healing your familiar can reach is maximized. (Pact of the Chain)"),
        F("Grasp of Hadar", text="Once per turn, eldritch blast can pull a creature 10 ft. (Prerequisite: eldritch blast)"),
        F("Improved Pact Weapon", text="Your pact weapon is a +1 weapon and can be a bow or crossbow. (Pact of the Blade)"),
        F("Lance of Lethargy", text="Once per turn, eldritch blast reduces a creature's speed by 10 ft. (Prerequisite: eldritch blast)"),
        F("Maddening Hex", text="Bonus action: psychic damage (Cha modifier) to the target of your hex or curse and creatures around it. (5th level)", effects=[ACT("maddening-hex", "Maddening Hex", "bonus", damage={"dice": "mod.cha", "type": "psychic"})]),
        F("Relentless Hex", text="Bonus action: teleport 30 ft next to the target of your hex or curse. (7th level)", effects=[ACT("relentless-hex", "Relentless Hex", "bonus")]),
        F("Shroud of Shadow", text="Cast invisibility at will without a slot. (15th level)", effects=[GRANT([{"id": "invisibility", "noSlot": True}], cls="warlock")]),
        F("Tomb of Levistus", text="Reaction when damaged: temp HP of 10 per warlock level in ice, but vulnerable to fire and speed 0. Once per short rest.", effects=[ACT("tomb-of-levistus", "Tomb of Levistus", "reaction", tempHp="10 * classLevel")]),
        F("Trickster's Escape", text="Cast freedom of movement on yourself once per long rest without a slot. (7th level)", effects=[GRANT([{"id": "freedom-of-movement", "uses": 1, "recharge": "long", "noSlot": True}], cls="warlock")]),
    ]
    X.fill(inv, "Eldritch Invocations", span=4)
    return [{"id": "arcane-shots", "name": "Arcane Shot Options", "options": shots}, {"id": "storm-auras", "name": "Storm Aura", "options": auras},
            {"id": "divine-affinities", "name": "Divine Soul Affinity", "options": affinity}, {"id": "eldritch-invocations", "name": "Eldritch Invocations", "options": inv}]


def racial_feats():
    half = lambda fid, abils: [ABIL_CHOICE(fid + "-ability", "+1 ability score", abils, 1)] if len(abils) > 1 else [ASC(abils[0], 1, 20)]
    nos = lambda rows: [GRANT([{"id": s} if u is None else {"id": s, "uses": u, "recharge": r, "noSlot": True} for s, u, r in rows], ability="cha")]
    fs = [
        ("Bountiful Luck", "Halfling", "Reaction when an ally within 30 ft rolls a 1: they reroll.", [ACT("bountiful-luck", "Bountiful Luck", "reaction")]),
        ("Dragon Fear", "Dragonborn", "+1 Str, Con or Cha; use Breath Weapon to frighten creatures within 30 ft instead.", half("dragon-fear", ["str", "con", "cha"])),
        ("Dragon Hide", "Dragonborn", "+1 Str, Con or Cha; AC 13 + Dex without armor; retractable claws (1d4 slashing).", half("dragon-hide", ["str", "con", "cha"]) + [AC("13 + mod.dex", when="unarmored")]),
        ("Drow High Magic", "Elf (drow)", "Detect magic at will; levitate and dispel magic once each per long rest without a slot.", nos([("detect-magic", None, None), ("levitate", 1, "long"), ("dispel-magic", 1, "long")])),
        ("Dwarven Fortitude", "Dwarf", "+1 Con; when you Dodge, spend a Hit Die to heal.", half("dwarven-fortitude", ["con"])),
        ("Elven Accuracy", "Elf or half-elf", "+1 Dex, Int, Wis or Cha; with advantage on an attack using one of them, reroll one of the dice.", half("elven-accuracy", ["dex", "int", "wis", "cha"])),
        ("Fade Away", "Gnome", "+1 Dex or Int; reaction when damaged: turn invisible until your next turn. Once per short rest.", half("fade-away", ["dex", "int"]) + [RES("fade-away", "Fade Away", 1, "short"), ACT("use-fade-away", "Fade Away", "reaction", cost={"resource": "fade-away", "amount": 1})]),
        ("Fey Teleportation", "Elf (high elf)", "+1 Int or Cha; learn Sylvan; misty step once per short rest without a slot.", half("fey-teleportation", ["int", "cha"]) + [PROF("language", ["Sylvan"]), GRANT([{"id": "misty-step", "uses": 1, "recharge": "short", "noSlot": True}], ability="int")]),
        ("Flames of Phlegethos", "Tiefling", "+1 Int or Cha; reroll 1s on fire spell damage; wreathe yourself in flame after casting one.", half("flames-of-phlegethos", ["int", "cha"])),
        ("Infernal Constitution", "Tiefling", "+1 Con; resistance to cold and poison; advantage on saves against being poisoned.", half("infernal-constitution", ["con"]) + [RESIST("cold", "poison"), ADV("Saves against being poisoned")]),
        ("Orcish Fury", "Half-orc", "+1 Str or Con; once per short rest, add one weapon damage die to a hit; attack as a reaction when using Relentless Endurance.", half("orcish-fury", ["str", "con"]) + [RES("orcish-fury", "Orcish Fury", 1, "short"), RIDER("orcish-fury", "Orcish Fury", damage="1d8", cost={"resource": "orcish-fury", "amount": 1}, requires=["weapon", "hit"])]),
        ("Prodigy", "Half-elf, half-orc or human", "One skill, one tool and one language; expertise in one proficient skill.", [CHOICE("prodigy-skill", "Skill", "skill", 1, {"skills": "any"}), CHOICE("prodigy-tool", "Tool", "tool", 1, {"list": ["any"]}), CHOICE("prodigy-language", "Language", "language", 1, {"list": ["any"]}), CHOICE("prodigy-expertise", "Expertise", "expertise", 1, {"skills": "proficient"})]),
        ("Second Chance", "Halfling", "+1 Dex, Con or Cha; reaction when hit: force the attacker to reroll. Once per combat or short rest.", half("second-chance", ["dex", "con", "cha"]) + [RES("second-chance", "Second Chance", 1, "short"), ACT("use-second-chance", "Second Chance", "reaction", cost={"resource": "second-chance", "amount": 1})]),
        ("Squat Nimbleness", "Dwarf or a Small race", "+1 Str or Dex; +5 ft speed; Acrobatics or Athletics proficiency; advantage to escape grapples.", half("squat-nimbleness", ["str", "dex"]) + [BON("speed", 5), CHOICE("squat-skill", "Skill", "skill", 1, {"skills": ["acrobatics", "athletics"]})]),
        ("Wood Elf Magic", "Elf (wood elf)", "A druid cantrip; longstrider and pass without trace once each per long rest without a slot.", [CHOICE("wood-elf-cantrip", "Druid cantrip", "spell", 1, {"spells": {"list": "druid", "level": 0}}), GRANT([{"id": "longstrider", "uses": 1, "recharge": "long", "noSlot": True}, {"id": "pass-without-trace", "uses": 1, "recharge": "long", "noSlot": True}], ability="wis")]),
    ]
    out = []
    feats = [F(n) for n, _, _, _ in fs]
    X.fill(feats, "Racial Feats", span=4)
    for (name, pre, summary, fx), f in zip(fs, feats):
        out.append({"id": slug(name), "name": name, "prerequisite": {"formula": "1", "text": pre},
                    "text": f.get("text") or summary, "effects": fx})
    return out
