"""Tasha's Cauldron of Everything (2014): subclasses, feats, and the new options it adds
to existing lists (fighting styles, maneuvers, metamagic, invocations, pact boons).
Structure and effects are written here; feature text comes from your extracted pages."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import *
from kit import Book

X = Book("tce", 1, 194, body=9)
CD = {"resource": "channel-divinity", "amount": 1}
BI = {"resource": "bardic-inspiration", "amount": 1}
WS = {"resource": "wild-shape", "amount": 1}
KI = lambda n: {"resource": "ki", "amount": n}
SP = lambda n: {"resource": "sorcery-points", "amount": n}
PSI = {"resource": "psionic-energy", "amount": 1}
PSI_DIE = {"3": "d6", "5": "d8", "11": "d10", "17": "d12"}
PSI_DMG = {"3": "1d6", "5": "1d8", "11": "1d10", "17": "1d12"}
ALL = ["str", "dex", "con", "int", "wis", "cha"]
MENTAL = ["int", "wis", "cha"]
PB = lambda id, name, rec="long", **kw: RES(id, name, "prof", rec, **kw)


def spells(cls, rows, levels):
    return GRANT([(s, lv) for lv, row in zip(levels, rows) for s in row], cls=cls)


def uses(id, name, mx, rec, econ, **kw):
    return [RES(id, name, mx, rec), ACT("use-" + id, name, econ, cost={"resource": id, "amount": 1}, **kw)]


def divine_strike(dtype):
    return F("Divine Strike", 8, "Once per turn, a weapon hit deals an extra 1d8 %s damage (2d8 at 14th level)." % dtype,
             [RIDER("divine-strike", "Divine Strike", damage={"8": "1d8", "14": "2d8"}, damageType=dtype, oncePer="turn", requires=["weapon", "hit"])])


def potent():
    return F("Potent Spellcasting", 8, "Add your Wisdom modifier to the damage of your cleric cantrips.", [BON("damage.spell", "mod.wis", note="Cleric cantrips")])


ART = (3, 5, 9, 13, 17)
DOM = (1, 3, 5, 7, 9)


def build():
    S = X.subclass
    subs = [
        S("artificer", "Alchemist", [
            F("Tool Proficiency", 3, "Proficiency with alchemist's supplies.", [PROF("tool", ["Alchemist's supplies"])], id="alchemist-tools"),
            F("Experimental Elixir", 3, "After a long rest, make a random elixir (more at 6th and 15th level); spend a spell slot to make more.", [RES("experimental-elixir", "Experimental Elixirs", {"3": 1, "6": 2, "15": 3}, "long")]),
            F("Alchemical Savant", 5, "Add your Int modifier to one roll of healing or acid, fire, necrotic or poison damage from your spells cast with alchemist's supplies.", [BON("damage.spell", "mod.int", note="Acid, fire, necrotic, poison or healing")]),
            F("Restorative Reagents", 9, "Elixirs grant temp HP (2d6 + Int); cast lesser restoration without a slot Int-modifier times per long rest.", [GRANT([{"id": "lesser-restoration", "uses": "max(1, mod.int)", "recharge": "long", "noSlot": True}], cls="artificer")]),
            F("Chemical Mastery", 15, "Resistance to acid and poison, immune to being poisoned; cast greater restoration and heal once each per long rest without a slot.",
              [RESIST("acid", "poison"), {"type": "conditionImmunity", "conditions": ["Poisoned"]}, GRANT([{"id": "greater-restoration", "uses": 1, "recharge": "long", "noSlot": True}, {"id": "heal", "uses": 1, "recharge": "long", "noSlot": True}], cls="artificer")]),
        ], spells=spells("artificer", [["healing-word", "ray-of-sickness"], ["flaming-sphere", "acid-arrow"], ["gaseous-form", "mass-healing-word"], ["blight", "death-ward"], ["cloudkill", "raise-dead"]], ART), nxt="Armorer"),
        S("artificer", "Armorer", [
            F("Tools of the Trade", 3, "Proficiency with heavy armor and smith's tools.", [PROF("armor", ["Heavy armor"]), PROF("tool", ["Smith's tools"])], id="armorer-tools"),
            F("Arcane Armor", 3, "Turn armor into a spellcasting focus that covers you; no Strength requirement."),
            F("Armor Model", 3, "Choose Guardian or Infiltrator, which gives your armor special weapons and features.", [CHOICE("armor-model", "Armor Model", "option", 1, {"optionSet": "armor-models"})]),
            F("Extra Attack", 5, "Attack twice when you take the Attack action.", [SET("attacksPerAction", 2)], id="armorer-extra-attack"),
            F("Armor Modifications", 9, "Your armor counts as separate items for infusions; two more infusions."),
            F("Perfected Armor", 15, "Your armor model gains a stronger feature."),
        ], spells=spells("artificer", [["magic-missile", "thunderwave"], ["mirror-image", "shatter"], ["hypnotic-pattern", "lightning-bolt"], ["fire-shield", "greater-invisibility"], ["passwall", "wall-of-force"]], ART), nxt="Artillerist"),
        S("artificer", "Artillerist", [
            F("Tool Proficiency", 3, "Proficiency with woodcarver's tools.", [PROF("tool", ["Woodcarver's tools"])], id="artillerist-tools"),
            F("Eldritch Cannon", 3, "Action: create a cannon (flamethrower, force ballista or protector) for 1 hour; bonus action to activate it. Once per long rest, or spend a slot.",
              uses("eldritch-cannon", "Eldritch Cannon", 1, "long", "action") + [ACT("activate-cannon", "Activate cannon", "bonus")]),
            F("Arcane Firearm", 5, "Through your firearm, add 1d8 to one damage roll of an artificer spell.", [REM("cast", "Arcane Firearm: +1d8 to one damage roll of the spell.")]),
            F("Explosive Cannon", 9, "Cannon damage rises by 1d8; detonate it as an action for 3d8 force (Dex save)."),
            F("Fortified Position", 15, "Two cannons at once; allies near a cannon have half cover."),
        ], spells=spells("artificer", [["shield", "thunderwave"], ["scorching-ray", "shatter"], ["fireball", "wind-wall"], ["ice-storm", "wall-of-fire"], ["cone-of-cold", "wall-of-force"]], ART), nxt="Battle Smith"),
        S("artificer", "Battle Smith", [
            F("Tool Proficiency", 3, "Proficiency with smith's tools.", [PROF("tool", ["Smith's tools"])], id="battle-smith-tools"),
            F("Battle Ready", 3, "Proficiency with martial weapons; use Intelligence for attacks and damage with magic weapons.", [PROF("weapon", ["Martial weapons"])]),
            F("Steel Defender", 3, "A steel defender companion fights beside you; command it with a bonus action.", [ACT("command-defender", "Command Steel Defender", "bonus")]),
            F("Extra Attack", 5, "Attack twice when you take the Attack action.", [SET("attacksPerAction", 2)], id="battle-smith-extra-attack"),
            F("Arcane Jolt", 9, "Once per turn on a magic weapon or defender hit: 2d6 force, or heal a creature within 30 ft 2d6 (4d6 at 15th). Int-modifier uses per long rest.",
              [RES("arcane-jolt", "Arcane Jolt", "max(1, mod.int)", "long"), RIDER("arcane-jolt", "Arcane Jolt", damage={"9": "2d6", "15": "4d6"}, damageType="force", cost={"resource": "arcane-jolt", "amount": 1}, oncePer="turn", requires=["hit"])]),
            F("Improved Defender", 15, "Arcane Jolt and your defender get stronger."),
        ], spells=spells("artificer", [["heroism", "shield"], ["branding-smite", "warding-bond"], ["aura-of-vitality", "conjure-barrage"], ["aura-of-purity", "fire-shield"], ["banishing-smite", "mass-cure-wounds"]], ART)),
        S("barbarian", "Path of the Beast", [
            F("Form of the Beast", 3, "When you rage, grow a bite, claws or a tail as a natural weapon.", [CHOICE("beast-form", "Form of the Beast", "option", 1, {"optionSet": "beast-forms"})]),
            F("Bestial Soul", 6, "Natural weapons are magical; gain a swimming, climbing or jumping trait after each rest."),
            F("Infectious Fury", 10, "When you hit with natural weapons, the target makes a Wis save or attacks someone else or takes 2d12 psychic. Proficiency-bonus uses per long rest.", [PB("infectious-fury", "Infectious Fury")]),
            F("Call the Hunt", 14, "When you rage, up to Con-modifier allies gain +1d6 damage once per turn and you gain 5 temp HP each. Proficiency-bonus uses per long rest.", [PB("call-the-hunt", "Call the Hunt")]),
        ], nxt="Path of Wild Magic"),
        S("barbarian", "Path of Wild Magic", [
            F("Magic Awareness", 3, "Action: sense spells and magic items within 60 ft. Proficiency-bonus uses per long rest.", [PB("magic-awareness", "Magic Awareness"), ACT("use-magic-awareness", "Magic Awareness", "action", cost={"resource": "magic-awareness", "amount": 1})]),
            F("Wild Surge", 3, "When you rage, roll on the Wild Magic table.", [REM("attack", "Wild Surge: roll on the Wild Magic table when you rage.")]),
            F("Bolstering Magic", 6, "Action: a creature adds 1d3 to attacks and checks, or regains a spell slot of 1d3 level. Proficiency-bonus uses per long rest.", [PB("bolstering-magic", "Bolstering Magic"), ACT("use-bolstering-magic", "Bolstering Magic", "action", cost={"resource": "bolstering-magic", "amount": 1}, roll="1d3")]),
            F("Unstable Backlash", 10, "Reaction while raging when damaged or failing a save: roll a new Wild Magic effect.", [ACT("unstable-backlash", "Unstable Backlash", "reaction", when="toggle:raging")]),
            F("Controlled Surge", 14, "Roll twice on the Wild Magic table and choose."),
        ]),
        S("bard", "College of Creation", [
            F("Mote of Potential", 3, "Bardic Inspiration you give carries a mote that adds an effect to checks, attacks or saves."),
            F("Performance of Creation", 3, "Action: create a nonmagical item worth up to 20 × bard level gp. Once per long rest (or spend a 2nd-level slot).", uses("performance-of-creation", "Performance of Creation", 1, "long", "action")),
            F("Animating Performance", 6, "Action: animate a Large or smaller nonmagical item as a dancing item companion for 1 hour. Once per long rest (or a 3rd-level slot).", uses("animating-performance", "Animating Performance", 1, "long", "action")),
            F("Creative Crescendo", 14, "Performance of Creation makes more items (Cha modifier) with no gp limit for one."),
        ], nxt="College of Eloquence"),
        S("bard", "College of Eloquence", [
            F("Silver Tongue", 3, "Treat a d20 roll of 9 or lower as 10 on Persuasion and Deception checks."),
            F("Unsettling Words", 3, "Bonus action: spend a Bardic Inspiration; a creature subtracts the die from its next save.", [ACT("unsettling-words", "Unsettling Words", "bonus", cost=BI)]),
            F("Unfailing Inspiration", 6, "A creature keeps its Bardic Inspiration die if it fails after adding it."),
            F("Universal Speech", 6, "Action: up to Cha-modifier creatures understand you for 1 hour. Once per long rest (or a slot).", uses("universal-speech", "Universal Speech", 1, "long", "action")),
            F("Infectious Inspiration", 14, "Reaction when someone succeeds with your inspiration: give a free Bardic Inspiration to another creature. Cha-modifier uses per long rest.", uses("infectious-inspiration", "Infectious Inspiration", "max(1, mod.cha)", "long", "reaction")),
        ]),
        S("cleric", "Order Domain", [
            F("Bonus Proficiencies", 1, "Proficiency with heavy armor, and in Intimidation or Persuasion.", [PROF("armor", ["Heavy armor"]), CHOICE("order-skill", "Order skill", "skill", 1, {"skills": ["intimidation", "persuasion"]})], id="order-bonus-proficiencies"),
            F("Voice of Authority", 1, "When you cast a spell of 1st level or higher on an ally, it can use its reaction to make one weapon attack.", [REM("cast", "Voice of Authority: an ally you target can attack with its reaction.")]),
            F("Channel Divinity: Order's Demand", 2, "Action: creatures within 30 ft make a Wisdom save or are charmed until your next turn ends and drop what they hold.", [ACT("orders-demand", "Order's Demand", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
            F("Embodiment of the Law", 6, "Cast enchantment spells of 1st level or higher as a bonus action. Wis-modifier uses per long rest.", [RES("embodiment-of-the-law", "Embodiment of the Law", "max(1, mod.wis)", "long")]),
            divine_strike("psychic"),
            F("Order's Wrath", 17, "Once per turn, a Divine Strike curses the target: the next ally hit on it adds 2d8 psychic."),
        ], spells=spells("cleric", [["command", "heroism"], ["hold-person", "zone-of-truth"], ["mass-healing-word", "slow"], ["compulsion", "locate-creature"], ["commune", "dominate-person"]], DOM), nxt="Peace Domain"),
        S("cleric", "Peace Domain", [
            F("Implement of Peace", 1, "Proficiency in Insight, Performance or Persuasion.", [CHOICE("peace-skill", "Implement of Peace", "skill", 1, {"skills": ["insight", "performance", "persuasion"]})]),
            F("Emboldening Bond", 1, "Action: bond up to proficiency-bonus creatures for 10 minutes; once per turn each adds 1d4 to an attack, check or save while near another. Proficiency-bonus uses per long rest.",
              [PB("emboldening-bond", "Emboldening Bond"), ACT("use-emboldening-bond", "Emboldening Bond", "action", cost={"resource": "emboldening-bond", "amount": 1})]),
            F("Channel Divinity: Balm of Peace", 2, "Action: move without provoking; each creature you pass within 5 ft regains 2d6 + Wis modifier HP.", [ACT("balm-of-peace", "Balm of Peace", "action", cost=CD, roll="2d6 + mod.wis")]),
            F("Protective Bond", 6, "Reaction when a bonded creature is about to take damage: teleport to it and take the damage instead.", [ACT("protective-bond", "Protective Bond", "reaction")]),
            potent(),
            F("Expansive Bond", 17, "Bond range is 60 ft, and Protective Bond grants resistance."),
        ], spells=spells("cleric", [["heroism", "sanctuary"], ["aura-of-vitality", "warding-bond"], ["beacon-of-hope", "sending"], ["aura-of-purity", "resilient-sphere"], ["greater-restoration", "telepathic-bond"]], DOM), nxt="Twilight Domain"),
        S("cleric", "Twilight Domain", [
            F("Bonus Proficiencies", 1, "Proficiency with martial weapons and heavy armor.", [PROF("weapon", ["Martial weapons"]), PROF("armor", ["Heavy armor"])], id="twilight-bonus-proficiencies"),
            F("Eyes of Night", 1, "Darkvision 300 ft; share it with Wis-modifier creatures for 1 hour once per long rest.", [SENSE("darkvision", 300)]),
            F("Vigilant Blessing", 1, "Action: a creature has advantage on its next initiative roll.", [ACT("vigilant-blessing", "Vigilant Blessing", "action")]),
            F("Channel Divinity: Twilight Sanctuary", 2, "Action: a 30-ft sphere of twilight for 1 minute; creatures ending their turn in it gain 1d6 + cleric level temp HP or end charm or fear.",
              [ACT("twilight-sanctuary", "Twilight Sanctuary", "action", cost=CD, roll="1d6 + classLevel")]),
            F("Steps of Night", 6, "Bonus action in dim light or darkness: flying speed equal to walking speed for 1 minute. Proficiency-bonus uses per long rest.",
              [PB("steps-of-night", "Steps of Night"), ACT("use-steps-of-night", "Steps of Night", "bonus", cost={"resource": "steps-of-night", "amount": 1})]),
            divine_strike("radiant"),
            F("Twilight Shroud", 17, "You and allies in your Twilight Sanctuary have half cover."),
        ], spells=spells("cleric", [["faerie-fire", "sleep"], ["moonbeam", "see-invisibility"], ["aura-of-vitality", "tiny-hut"], ["aura-of-life", "greater-invisibility"], ["circle-of-power", "mislead"]], DOM)),
        S("druid", "Circle of Spores", [
            F("Circle Spells", 2, "You know chill touch, and gain circle spells at 3rd, 5th, 7th and 9th level.", [GRANT([("chill-touch", 2), ("blindness-deafness", 3), ("gentle-repose", 3), ("animate-dead", 5), ("gaseous-form", 5), ("blight", 7), ("confusion", 7), ("cloudkill", 9), ("contagion", 9)], cls="druid")], id="spores-circle-spells"),
            F("Halo of Spores", 2, "Reaction when a creature moves or starts its turn within 10 ft: 1d4 necrotic (Con save negates); 1d6 at 6th, 1d8 at 10th, 1d10 at 14th.",
              [ACT("halo-of-spores", "Halo of Spores", "reaction", damage={"dice": {"2": "1d4", "6": "1d6", "10": "1d8", "14": "1d10"}, "type": "necrotic"}, save={"ability": "con", "dc": "spellDC"})]),
            F("Symbiotic Entity", 2, "Action: spend a Wild Shape use; gain 4 temp HP per druid level for 10 minutes, Halo of Spores doubles, and melee hits deal 1d6 necrotic.",
              [{"type": "toggle", "id": "symbiotic-entity", "name": "Symbiotic Entity", "endsOn": ["manual"]}, ACT("symbiotic-entity", "Symbiotic Entity", "action", cost=WS, tempHp="4 * classLevel", toggle="symbiotic-entity"),
               RIDER("symbiotic-strike", "Symbiotic Entity", damage="1d6", damageType="necrotic", when="toggle:symbiotic-entity", requires=["melee", "hit"])]),
            F("Fungal Infestation", 6, "Reaction when a Small or Medium beast or humanoid dies within 10 ft: animate it as a zombie for 1 hour. Wis-modifier uses per long rest.", uses("fungal-infestation", "Fungal Infestation", "max(1, mod.wis)", "long", "reaction")),
            F("Spreading Spores", 10, "Bonus action while Symbiotic Entity is active: a 10-foot cube of spores."),
            F("Fungal Body", 14, "Immune to being blinded, deafened, frightened or poisoned; crits against you are normal hits.", [{"type": "conditionImmunity", "conditions": ["Blinded", "Deafened", "Frightened", "Poisoned"]}]),
        ], nxt="Circle of Stars"),
        S("druid", "Circle of Stars", [
            F("Star Map", 2, "You know guidance and can cast guiding bolt without a slot proficiency-bonus times per long rest.", [GRANT([{"id": "guidance"}, {"id": "guiding-bolt", "uses": "prof", "recharge": "long", "noSlot": True}], cls="druid")]),
            F("Starry Form", 2, "Bonus action: spend a Wild Shape use to take an Archer, Chalice or Dragon constellation form for 10 minutes.", [ACT("starry-form", "Starry Form", "bonus", cost=WS), CHOICE("starry-form", "Constellation", "option", 1, {"optionSet": "starry-forms"})]),
            F("Cosmic Omen", 6, "After a long rest, roll for weal or woe; reaction to add or subtract 1d6 from a nearby roll. Proficiency-bonus uses per long rest.",
              [PB("cosmic-omen", "Cosmic Omen"), ACT("use-cosmic-omen", "Cosmic Omen", "reaction", cost={"resource": "cosmic-omen", "amount": 1}, roll="1d6")]),
            F("Twinkling Constellations", 10, "Starry Form dice become 2d8, the dragon gives a 20-ft flying speed, and you can change constellation each turn."),
            F("Full of Stars", 14, "In Starry Form, resistance to bludgeoning, piercing and slashing damage."),
        ], nxt="Circle of Wildfire"),
        S("druid", "Circle of Wildfire", [
            F("Summon Wildfire Spirit", 2, "Action: spend a Wild Shape use to summon a wildfire spirit for 1 hour.", [ACT("summon-wildfire-spirit", "Summon Wildfire Spirit", "action", cost=WS)]),
            F("Enhanced Bond", 6, "With your spirit summoned, add 1d8 to one fire damage or healing roll of your spells, and cast spells from its space.", [REM("cast", "Enhanced Bond: +1d8 to one fire damage or healing roll.")]),
            F("Cauterizing Flames", 10, "When a creature dies near your spirit, create a flame that heals or burns 2d10 + Wis. Proficiency-bonus uses per long rest.", [PB("cauterizing-flames", "Cauterizing Flames")]),
            F("Blazing Revival", 14, "When you drop to 0 HP, end your spirit to regain half your HP and stand. Once per long rest.", [RES("blazing-revival", "Blazing Revival", 1, "long")]),
        ], spells=spells("druid", [["burning-hands", "cure-wounds"], ["flaming-sphere", "scorching-ray"], ["plant-growth", "revivify"], ["aura-of-life", "fire-shield"], ["flame-strike", "mass-cure-wounds"]], (2, 3, 5, 7, 9))),
        S("fighter", "Psi Warrior", [
            F("Psionic Power", 3, "Psionic Energy dice (twice your proficiency bonus, d6 rising to d12) power Protective Field, Psionic Strike and Telekinetic Movement. Regain one as a bonus action once per short rest.",
              [RES("psionic-energy", "Psionic Energy dice", "2 * prof", "long", die=PSI_DIE, color="psy"),
               ACT("protective-field", "Protective Field", "reaction", cost=PSI, roll=PSI_DMG),
               RIDER("psionic-strike", "Psionic Strike", damage={"3": "1d6 + mod.int", "5": "1d8 + mod.int", "11": "1d10 + mod.int", "17": "1d12 + mod.int"}, damageType="force", cost=PSI, oncePer="turn", requires=["weapon", "hit"]),
               ACT("telekinetic-movement", "Telekinetic Movement", "action"), ACT("regain-psionic-die", "Regain a Psionic die", "bonus", gain={"resource": "psionic-energy", "amount": 1})]),
            F("Telekinetic Adept", 7, "Psi-Powered Leap (flying speed for a turn) and Telekinetic Thrust (push or knock prone on a Psionic Strike).", [ACT("psi-powered-leap", "Psi-Powered Leap", "bonus")]),
            F("Guarded Mind", 10, "Resistance to psychic damage; spend a Psionic die to end charm or fear on yourself.", [RESIST("psychic")]),
            F("Bulwark of Force", 15, "Bonus action: half cover for up to Int-modifier creatures for 1 minute. Once per long rest (or a Psionic die).", uses("bulwark-of-force", "Bulwark of Force", 1, "long", "bonus")),
            F("Telekinetic Master", 18, "Cast telekinesis without a slot once per long rest (or a Psionic die), and attack as a bonus action while concentrating on it.", [GRANT([{"id": "telekinesis", "uses": 1, "recharge": "long", "noSlot": True}], ability="int")]),
        ], nxt="Rune Knight"),
        S("fighter", "Rune Knight", [
            F("Bonus Proficiencies", 3, "Proficiency with smith's tools, and you learn Giant.", [PROF("tool", ["Smith's tools"]), PROF("language", ["Giant"])], id="rune-knight-bonus-proficiencies"),
            F("Rune Carver", 3, "Inscribe runes on your gear; learn more runes at 7th, 10th and 15th level. Each rune's power works once per short rest.", [CHOICE("runes", "Runes", "option", {"3": 2, "7": 3, "10": 4, "15": 5}, {"optionSet": "runes"})]),
            F("Giant's Might", 3, "Bonus action: become Large for 1 minute, with advantage on Strength checks and saves and +1d6 damage once per turn. Proficiency-bonus uses per long rest.",
              [PB("giants-might", "Giant's Might", color="gold"), {"type": "toggle", "id": "giants-might", "name": "Giant's Might", "endsOn": ["combatEnd", "manual"]},
               ACT("use-giants-might", "Giant's Might", "bonus", cost={"resource": "giants-might", "amount": 1}, toggle="giants-might"),
               RIDER("giants-might", "Giant's Might", damage={"3": "1d6", "10": "1d8", "18": "1d10"}, oncePer="turn", when="toggle:giants-might", requires=["weapon", "hit"])]),
            F("Runic Shield", 7, "Reaction when a creature within 60 ft is hit: force a reroll. Proficiency-bonus uses per long rest.", [PB("runic-shield", "Runic Shield"), ACT("use-runic-shield", "Runic Shield", "reaction", cost={"resource": "runic-shield", "amount": 1})]),
            F("Great Stature", 10, "Grow 3d4 inches; Giant's Might extra damage becomes 1d8."),
            F("Master of Runes", 15, "Each rune's power works twice per short rest."),
            F("Runic Juggernaut", 18, "Giant's Might extra damage becomes 1d10, you can become Huge, and reach grows 5 ft."),
        ]),
        S("monk", "Way of Mercy", [
            F("Implements of Mercy", 3, "Proficiency in Insight and Medicine and with the herbalism kit.", [PROF("skill", ["insight", "medicine"]), PROF("tool", ["Herbalism kit"])]),
            F("Hand of Healing", 3, "Action (or in place of a Flurry strike): spend 1 ki to heal a creature a martial arts die + Wis.", [ACT("hand-of-healing", "Hand of Healing", "action", cost=KI(1), roll="col.martialArts + mod.wis")]),
            F("Hand of Harm", 3, "Once per turn on an unarmed hit, spend 1 ki for a martial arts die + Wis necrotic.", [RIDER("hand-of-harm", "Hand of Harm", damage="col.martialArts + mod.wis", damageType="necrotic", cost=KI(1), oncePer="turn", requires=["melee", "hit"])]),
            F("Physician's Touch", 6, "Hand of Healing also ends a disease or condition; Hand of Harm can poison."),
            F("Flurry of Healing and Harm", 11, "Replace Flurry strikes with Hand of Healing for free; one Hand of Harm per Flurry without ki."),
            F("Hand of Ultimate Mercy", 17, "Spend 5 ki to return a creature that died in the last 24 hours to life. Once per long rest.", [RES("hand-of-ultimate-mercy", "Hand of Ultimate Mercy", 1, "long")]),
        ], nxt="Way of the Astral Self"),
        S("monk", "Way of the Astral Self", [
            F("Arms of the Astral Self", 3, "Bonus action, 1 ki: summon spectral arms for 10 minutes; use Wis for unarmed strikes with 10-ft reach and force damage.",
              [{"type": "toggle", "id": "astral-arms", "name": "Arms of the Astral Self", "endsOn": ["manual"]}, ACT("arms-of-the-astral-self", "Arms of the Astral Self", "bonus", cost=KI(1), toggle="astral-arms"),
               ACT("astral-strike", "Astral arm strike", "action", when="toggle:astral-arms", damage={"dice": "col.martialArts + mod.wis", "type": "force"})]),
            F("Visage of the Astral Self", 6, "Bonus action, 1 ki: a spectral visage for 10 minutes with darkvision 120 ft and advantage on Insight and Intimidation.", [ACT("visage-of-the-astral-self", "Visage of the Astral Self", "bonus", cost=KI(1))]),
            F("Body of the Astral Self", 11, "With arms and visage summoned, deflect damage as a reaction and add a martial arts die to one arm hit each turn."),
            F("Awakened Astral Self", 17, "Bonus action, 5 ki: full astral self for 10 minutes: +2 AC and three arm strikes per Attack action.", [ACT("awakened-astral-self", "Awakened Astral Self", "bonus", cost=KI(5))]),
        ]),
        S("paladin", "Oath of Glory", [
            F("Channel Divinity: Peerless Athlete", 3, "Bonus action: advantage on Athletics and Acrobatics and better carrying and jumping for 10 minutes.", [ACT("peerless-athlete", "Peerless Athlete", "bonus", cost=CD)]),
            F("Channel Divinity: Inspiring Smite", 3, "Bonus action after Divine Smite: share 2d8 + paladin level temp HP among creatures within 30 ft.", [ACT("inspiring-smite", "Inspiring Smite", "bonus", cost=CD, roll="2d8 + classLevel")]),
            F("Aura of Alacrity", 7, "+10 ft walking speed; allies starting their turn near you gain +10 ft too.", [BON("speed", 10)]),
            F("Glorious Defense", 15, "Reaction when a creature you can see is hit: add your Cha modifier to its AC, and attack back if it misses. Cha-modifier uses per long rest.", uses("glorious-defense", "Glorious Defense", "max(1, mod.cha)", "long", "reaction")),
            F("Living Legend", 20, "Bonus action for 1 minute: advantage on Charisma checks, turn a miss into a hit once per turn, reroll failed saves. Once per long rest.", uses("living-legend", "Living Legend", 1, "long", "bonus")),
        ], spells=spells("paladin", [["guiding-bolt", "heroism"], ["enhance-ability", "magic-weapon"], ["haste", "protection-from-energy"], ["compulsion", "freedom-of-movement"], ["commune", "flame-strike"]], (3, 5, 9, 13, 17)), nxt="Oath of the Watchers"),
        S("paladin", "Oath of the Watchers", [
            F("Channel Divinity: Watcher's Will", 3, "Action: up to Cha-modifier creatures have advantage on Int, Wis and Cha saves for 1 minute.", [ACT("watchers-will", "Watcher's Will", "action", cost=CD)]),
            F("Channel Divinity: Abjure the Extraplanar", 3, "Action: aberrations, celestials, elementals, fey and fiends within 30 ft make a Wisdom save or are turned.", [ACT("abjure-the-extraplanar", "Abjure the Extraplanar", "action", cost=CD, save={"ability": "wis", "dc": "spellDC"})]),
            F("Aura of the Sentinel", 7, "You and allies within 10 ft add your proficiency bonus to initiative.", [BON("initiative", "prof")]),
            F("Vigilant Rebuke", 15, "Reaction when a creature succeeds on an Int, Wis or Cha save: deal 2d8 + Cha force to the creature that forced it.", [ACT("vigilant-rebuke", "Vigilant Rebuke", "reaction", damage={"dice": "2d8 + mod.cha", "type": "force"})]),
            F("Mortal Bulwark", 20, "Bonus action for 1 minute: truesight 120 ft, advantage against extraplanar creatures, and banish them on a hit. Once per long rest.", uses("mortal-bulwark", "Mortal Bulwark", 1, "long", "bonus")),
        ], spells=spells("paladin", [["alarm", "detect-magic"], ["moonbeam", "see-invisibility"], ["counterspell", "nondetection"], ["aura-of-purity", "banishment"], ["hold-monster", "scrying"]], (3, 5, 9, 13, 17))),
        S("ranger", "Fey Wanderer", [
            F("Dreadful Strikes", 3, "Once per turn, a weapon hit deals an extra 1d4 psychic (1d6 at 11th).", [RIDER("dreadful-strikes", "Dreadful Strikes", damage={"3": "1d4", "11": "1d6"}, damageType="psychic", oncePer="turn", requires=["weapon", "hit"])]),
            F("Otherworldly Glamour", 3, "Add your Wis modifier to Charisma checks; proficiency in Deception, Performance or Persuasion.", [BON("check.cha", "mod.wis"), CHOICE("otherworldly-glamour", "Glamour skill", "skill", 1, {"skills": ["deception", "performance", "persuasion"]})]),
            F("Beguiling Twist", 7, "Advantage on saves against charm and fear; reaction when a creature nearby succeeds on one to charm or frighten another creature.", [ADV("Saves against being charmed or frightened"), ACT("beguiling-twist", "Beguiling Twist", "reaction")]),
            F("Fey Reinforcements", 11, "You know summon fey and can cast it once per long rest without a slot or material component.", [GRANT([{"id": "summon-fey", "uses": 1, "recharge": "long", "noSlot": True}], cls="ranger")]),
            F("Misty Wanderer", 15, "Cast misty step without a slot Wis-modifier times per long rest, bringing a willing creature along.", [GRANT([{"id": "misty-step", "uses": "max(1, mod.wis)", "recharge": "long", "noSlot": True}], cls="ranger")]),
        ], spells=spells("ranger", [["charm-person"], ["misty-step"], ["dispel-magic"], ["dimension-door"], ["mislead"]], (3, 5, 9, 13, 17)), nxt="Swarmkeeper"),
        S("ranger", "Swarmkeeper", [
            F("Gathered Swarm", 3, "Once per turn on a hit, your swarm deals an extra 1d6 piercing, pushes the target, or moves you (1d8 at 11th).", [RIDER("gathered-swarm", "Gathered Swarm", damage={"3": "1d6", "11": "1d8"}, damageType="piercing", oncePer="turn", requires=["hit"])]),
            F("Swarmkeeper Magic", 3, "You know mage hand and gain swarm spells as you level.", [GRANT([("mage-hand", 3), ("faerie-fire", 3), ("web", 5), ("gaseous-form", 9), ("arcane-eye", 13), ("insect-plague", 17)], cls="ranger")]),
            F("Writhing Tide", 7, "Bonus action: your swarm lifts you, a 10-ft flying speed for 1 minute. Proficiency-bonus uses per long rest.", [PB("writhing-tide", "Writhing Tide"), ACT("use-writhing-tide", "Writhing Tide", "bonus", cost={"resource": "writhing-tide", "amount": 1})]),
            F("Mighty Swarm", 11, "Gathered Swarm grows stronger: knock prone, half cover, or 1d8 damage."),
            F("Swarming Dispersal", 15, "Reaction when damaged: resistance, and teleport 30 ft. Proficiency-bonus uses per long rest.", [PB("swarming-dispersal", "Swarming Dispersal"), ACT("use-swarming-dispersal", "Swarming Dispersal", "reaction", cost={"resource": "swarming-dispersal", "amount": 1})]),
        ]),
        S("rogue", "Phantom", [
            F("Whispers of the Dead", 3, "After a rest, gain one skill or tool proficiency until your next rest."),
            F("Wails from the Grave", 3, "After a Sneak Attack, a second creature within 30 ft takes half your Sneak Attack dice in necrotic. Proficiency-bonus uses per long rest.",
              [PB("wails-from-the-grave", "Wails from the Grave"), ACT("use-wails-from-the-grave", "Wails from the Grave", "free", cost={"resource": "wails-from-the-grave", "amount": 1})]),
            F("Tokens of the Departed", 9, "Create soul trinkets when creatures die near you; they give advantage on Con saves and death saves."),
            F("Ghost Walk", 13, "Bonus action: spectral form for 10 minutes, 10-ft flying speed and disadvantage on attacks against you. Once per long rest (or a soul trinket).", uses("ghost-walk", "Ghost Walk", 1, "long", "bonus")),
            F("Death's Friend", 17, "Wails from the Grave deals damage to both creatures; you always have a soul trinket after a long rest."),
        ], nxt="Soulknife"),
        S("rogue", "Soulknife", [
            F("Psionic Power", 3, "Psionic Energy dice (twice your proficiency bonus, d6 rising to d12) power Psi-Bolstered Knack and Psychic Whispers.",
              [RES("psionic-energy", "Psionic Energy dice", "2 * prof", "long", die=PSI_DIE, color="psy"), ACT("psi-bolstered-knack", "Psi-Bolstered Knack", "free", cost=PSI, roll=PSI_DMG),
               ACT("psychic-whispers", "Psychic Whispers", "action", cost=PSI)]),
            F("Psychic Blades", 3, "Manifest a psychic blade (1d6 + Dex psychic, 60-ft thrown); bonus action for a second blade (1d4).",
              [ACT("psychic-blade", "Psychic Blade", "action", damage={"dice": "1d6 + mod.dex", "type": "psychic"}), ACT("psychic-blade-bonus", "Psychic Blade (bonus)", "bonus", damage={"dice": "1d4 + mod.dex", "type": "psychic"})]),
            F("Soul Blades", 9, "Homing Strikes (add a Psionic die to a missed blade attack) and Psychic Teleportation.", [ACT("homing-strikes", "Homing Strikes", "free", cost=PSI, roll=PSI_DMG), ACT("psychic-teleportation", "Psychic Teleportation", "bonus", cost=PSI)]),
            F("Psychic Veil", 13, "Action: invisible for 1 hour. Once per long rest (or a Psionic die).", uses("psychic-veil", "Psychic Veil", 1, "long", "action")),
            F("Rend Mind", 17, "On a Sneak Attack with a psychic blade, the target makes a Wisdom save or is stunned for 1 minute. Once per long rest (or 3 Psionic dice).", [RES("rend-mind", "Rend Mind", 1, "long")]),
        ]),
        S("sorcerer", "Aberrant Mind", [
            F("Psionic Spells", 1, "Always-prepared psionic spells at sorcerer levels 1, 3, 5, 7 and 9.", [GRANT([("arms-of-hadar", 1), ("dissonant-whispers", 1), ("mind-sliver", 1), ("calm-emotions", 3), ("detect-thoughts", 3), ("hunger-of-hadar", 5), ("sending", 5),
                                                                                                            ("black-tentacles", 7), ("summon-aberration", 7), ("telepathic-bond", 9), ("telekinesis", 9)], cls="sorcerer")]),
            F("Telepathic Speech", 1, "Bonus action: telepathic link with a creature for minutes equal to your sorcerer level.", [ACT("telepathic-speech", "Telepathic Speech", "bonus")]),
            F("Psionic Sorcery", 6, "Cast psionic spells with sorcery points instead of slots, with no components."),
            F("Psychic Defenses", 6, "Resistance to psychic damage; advantage on saves against being charmed or frightened.", [RESIST("psychic"), ADV("Saves against being charmed or frightened")]),
            F("Revelation in Flesh", 14, "Bonus action, sorcery points: gain see-invisible, flight, swimming or squeezing for 10 minutes.", [ACT("revelation-in-flesh", "Revelation in Flesh", "bonus", cost=SP(1))]),
            F("Warping Implosion", 18, "Action: teleport 120 ft; creatures near your old spot take 3d10 force and are pulled (Str save). Once per long rest (or 5 sorcery points).", uses("warping-implosion", "Warping Implosion", 1, "long", "action")),
        ], nxt="Clockwork Soul"),
        S("sorcerer", "Clockwork Soul", [
            F("Clockwork Magic", 1, "Always-prepared clockwork spells at sorcerer levels 1, 3, 5, 7 and 9.", [GRANT([("alarm", 1), ("protection-from-evil-and-good", 1), ("aid", 3), ("lesser-restoration", 3), ("dispel-magic", 5), ("protection-from-energy", 5),
                                                                                                                ("freedom-of-movement", 7), ("summon-construct", 7), ("greater-restoration", 9), ("wall-of-force", 9)], cls="sorcerer")]),
            F("Restore Balance", 1, "Reaction: cancel advantage or disadvantage on a roll within 60 ft. Proficiency-bonus uses per long rest.", [PB("restore-balance", "Restore Balance"), ACT("use-restore-balance", "Restore Balance", "reaction", cost={"resource": "restore-balance", "amount": 1})]),
            F("Bastion of Law", 6, "Action: spend 1-5 sorcery points to ward a creature with that many d8s that reduce damage.", [ACT("bastion-of-law", "Bastion of Law", "action", cost=SP(1))]),
            F("Trance of Order", 14, "Bonus action: for 1 minute, attacks can't have advantage against you and your d20 rolls of 9 or lower count as 10. Once per long rest (or 5 sorcery points).", uses("trance-of-order", "Trance of Order", 1, "long", "bonus")),
            F("Clockwork Cavalcade", 18, "Action: a 30-ft cube that heals 100 HP, repairs objects and ends spells of 6th level or lower. Once per long rest (or 7 sorcery points).", uses("clockwork-cavalcade", "Clockwork Cavalcade", 1, "long", "action")),
        ]),
        S("warlock", "The Fathomless", [
            F("Tentacle of the Deeps", 1, "Bonus action: a spectral tentacle for 1 minute; bonus action attacks deal 1d8 cold (2d8 at 10th) and reduce speed. Proficiency-bonus uses per long rest.",
              [PB("tentacle-of-the-deeps", "Tentacle of the Deeps"), ACT("use-tentacle", "Tentacle of the Deeps", "bonus", cost={"resource": "tentacle-of-the-deeps", "amount": 1}), ACT("tentacle-attack", "Tentacle attack", "bonus", damage={"dice": {"1": "1d8", "10": "2d8"}, "type": "cold"})]),
            F("Gift of the Sea", 1, "40-ft swimming speed; breathe underwater.", [SPEED("swim", 40)]),
            F("Oceanic Soul", 6, "Resistance to cold damage; speak with underwater creatures.", [RESIST("cold")]),
            F("Guardian Coil", 6, "Reaction when a creature near your tentacle is damaged: reduce it by 1d8 (2d8 at 10th).", [ACT("guardian-coil", "Guardian Coil", "reaction", roll={"6": "1d8", "10": "2d8"})]),
            F("Grasping Tentacles", 10, "Cast Evard's black tentacles once per long rest without a slot; gain temp HP equal to your warlock level when you do.", [GRANT([{"id": "black-tentacles", "uses": 1, "recharge": "long", "noSlot": True}], cls="warlock")]),
            F("Fathomless Plunge", 14, "Action: teleport yourself and up to five creatures to a body of water within 1 mile. Once per short rest.", uses("fathomless-plunge", "Fathomless Plunge", 1, "short", "action")),
        ], nxt="The Genie"),
        S("warlock", "The Genie", [
            F("Genie's Vessel", 1, "Your vessel is a focus. Bottled Respite: vanish into it for hours equal to twice your proficiency bonus, once per long rest. Genie's Wrath: once per turn add your proficiency bonus to a hit's damage.",
              [CHOICE("genie-kind", "Genie kind", "option", 1, {"optionSet": "genie-kinds"}), RES("bottled-respite", "Bottled Respite", 1, "long"),
               RIDER("genies-wrath", "Genie's Wrath", damage="prof", oncePer="turn", requires=["hit"])]),
            F("Elemental Gift", 6, "Resistance from your genie kind; bonus action flying speed of 30 ft for 10 minutes, proficiency-bonus times per long rest.",
              [PB("elemental-gift", "Elemental Gift flight"), ACT("use-elemental-gift", "Elemental Gift (fly)", "bonus", cost={"resource": "elemental-gift", "amount": 1})]),
            F("Sanctuary Vessel", 10, "Bring up to five creatures into your vessel; a short rest there heals extra."),
            F("Limited Wish", 14, "Action: gain the effect of a spell of 6th level or lower. Usable again after 1d4 long rests.", [RES("limited-wish", "Limited Wish", 1, "never", note="Back after 1d4 long rests")]),
        ]),
        S("wizard", "Bladesinging", [
            F("Training in War and Song", 2, "Proficiency with light armor, one one-handed melee weapon, and Performance.", [PROF("armor", ["Light armor"]), PROF("skill", ["performance"]), CHOICE("bladesinger-weapon", "Weapon", "text", 1)]),
            F("Bladesong", 2, "Bonus action without medium or heavy armor or a shield: for 1 minute, add Int to AC and concentration saves, +10 ft speed, advantage on Acrobatics. Proficiency-bonus uses per long rest.",
              [PB("bladesong", "Bladesong", color="psy"), {"type": "toggle", "id": "bladesong", "name": "Bladesong", "endsOn": ["manual"]},
               ACT("use-bladesong", "Bladesong", "bonus", cost={"resource": "bladesong", "amount": 1}, toggle="bladesong"),
               BON("ac", "max(1, mod.int)", when="toggle:bladesong"), BON("speed", 10, when="toggle:bladesong")]),
            F("Extra Attack", 6, "Attack twice when you take the Attack action; one attack can be a cantrip.", [SET("attacksPerAction", 2)], id="bladesinger-extra-attack"),
            F("Song of Defense", 10, "Reaction while Bladesong is active: spend a slot to reduce damage by five times its level.", [ACT("song-of-defense", "Song of Defense", "reaction", when="toggle:bladesong")]),
            F("Song of Victory", 14, "While Bladesong is active, add your Int modifier to melee weapon damage.", [BON("damage.melee", "max(1, mod.int)", when="toggle:bladesong")]),
        ], nxt="Order of Scribes"),
        S("wizard", "Order of Scribes", [
            F("Wizardly Quill", 2, "Bonus action: a magical quill; copying spells takes 2 minutes per level."),
            F("Awakened Spellbook", 2, "Your spellbook is a focus; swap a spell's damage type for another of your spells' types; once per long rest, cast a ritual at normal speed."),
            F("Manifest Mind", 6, "Bonus action: a spectral mind within 60 ft; cast spells from it proficiency-bonus times per long rest.", [PB("manifest-mind", "Manifest Mind casts"), ACT("summon-manifest-mind", "Manifest Mind", "bonus")]),
            F("Master Scrivener", 10, "After a long rest, make a spell scroll from your book that casts one level higher."),
            F("One with the Word", 14, "Advantage on Arcana; reaction when damaged: your spellbook takes it instead, at the cost of spells. Once per long rest.", [ADV("Arcana checks"), RES("one-with-the-word", "One with the Word", 1, "long")]),
        ]),
    ]
    feats = tasha_feats()
    sets = option_sets()
    X.report()
    return {"subclasses": subs, "feats": feats, "optionSets": sets}


def option_sets():
    sup = {"resource": "superiority-dice", "amount": 1}
    die = {"3": "1d8", "10": "1d10", "18": "1d12"}
    styles = [
        F("Blind Fighting", text="Blindsight 10 ft.", effects=[SENSE("blindsight", 10)]),
        F("Interception", text="Reaction with a shield or weapon: reduce damage to a nearby creature by 1d10 + proficiency bonus.", effects=[ACT("interception", "Interception", "reaction", roll="1d10 + prof")]),
        F("Superior Technique", text="Learn one maneuver and gain one d6 superiority die per short rest.", effects=[CHOICE("superior-technique", "Maneuver", "option", 1, {"optionSet": "maneuvers"}), RES("superiority-dice", "Superiority dice", 1, "short", die="d6", color="gold")]),
        F("Thrown Weapon Fighting", text="Draw a thrown weapon as part of the attack; +2 damage with thrown weapons.", effects=[BON("damage.weapon", 2, note="Thrown weapons")]),
        F("Unarmed Fighting", text="Unarmed strikes deal 1d6 (1d8 with free hands); grappled creatures take 1d4 each turn."),
        F("Blessed Warrior", text="Learn two cleric cantrips; Charisma is their ability. (Paladin)", effects=[CHOICE("blessed-warrior", "Cleric cantrips", "spell", 2, {"spells": {"list": "cleric", "level": 0}})]),
        F("Druidic Warrior", text="Learn two druid cantrips; Wisdom is their ability. (Ranger)", effects=[CHOICE("druidic-warrior", "Druid cantrips", "spell", 2, {"spells": {"list": "druid", "level": 0}})]),
    ]
    X.fill(styles, "Fighting Style Options", span=3)
    pick = lambda *ns: [s for s in styles if s["name"] in ns]
    maneuvers = [
        F("Ambush", text="Add the superiority die to a Stealth check or initiative roll.", effects=[ACT("ambush", "Ambush", "free", cost=sup, roll=die)]),
        F("Bait and Switch", text="Swap places with a willing creature within 5 ft; one of you adds the die to AC.", effects=[ACT("bait-and-switch", "Bait and Switch", "free", cost=sup, roll=die)]),
        F("Brace", text="Reaction when a creature moves into your reach: attack it, adding the die to damage.", effects=[ACT("brace", "Brace", "reaction", cost=sup, roll=die)]),
        F("Commanding Presence", text="Add the die to an Intimidation, Performance or Persuasion check.", effects=[ACT("commanding-presence", "Commanding Presence", "free", cost=sup, roll=die)]),
        F("Grappling Strike", text="After a hit, grapple as a bonus action, adding the die to the check.", effects=[ACT("grappling-strike", "Grappling Strike", "bonus", cost=sup, roll=die)]),
        F("Quick Toss", text="Bonus action: throw a weapon, adding the die to damage.", effects=[ACT("quick-toss", "Quick Toss", "bonus", cost=sup, roll=die)]),
        F("Tactical Assessment", text="Add the die to an Investigation, History or Insight check.", effects=[ACT("tactical-assessment", "Tactical Assessment", "free", cost=sup, roll=die)]),
    ]
    X.fill(maneuvers, "Maneuver Options", span=3)
    metamagic = [F("Seeking Spell", text="2 sorcery points: reroll a missed spell attack."), F("Transmuted Spell", text="1 sorcery point: change a spell's damage type to another elemental type.")]
    X.fill(metamagic, "Metamagic Options", span=3)
    nos = lambda sid, **kw: [GRANT([dict({"id": sid, "noSlot": True}, **kw)], cls="warlock")]
    inv = [
        F("Bond of the Talisman", text="Teleport to your talisman's wearer as an action, proficiency-bonus times per long rest. (12th level, Pact of the Talisman)"),
        F("Eldritch Mind", text="Advantage on Constitution saves to keep concentration.", effects=[ADV("Con saves to keep concentration")]),
        F("Far Scribe", text="Send messages to creatures who wrote in your Book of Shadows. (5th level, Pact of the Tome)"),
        F("Gift of the Protectors", text="Once per long rest, a creature named in your book drops to 1 HP instead of 0. (9th level, Pact of the Tome)"),
        F("Investment of the Chain Master", text="Your familiar flies or swims 40 ft, attacks as a bonus action, uses your save DC and resists damage. (Pact of the Chain)"),
        F("Protection of the Talisman", text="The talisman's wearer adds 1d4 to a failed save, proficiency-bonus times per long rest. (7th level, Pact of the Talisman)"),
        F("Rebuke of the Talisman", text="Reaction when the wearer is hit: psychic damage equal to your proficiency bonus and a 10-ft push. (Pact of the Talisman)"),
        F("Undying Servitude", text="Cast animate dead once per long rest without a slot. (5th level)", effects=nos("animate-dead", uses=1, recharge="long")),
    ]
    X.fill(inv, "Eldritch Invocation Options", span=3)
    talisman = [F("Pact of the Talisman", text="An amulet that lets its wearer add 1d4 to failed ability checks, proficiency-bonus times per long rest.")]
    X.fill(talisman, "Pact Boon Option", span=3)
    beast = [
        F("Bite", text="1d8 piercing; once per turn on a hit below half HP, regain HP equal to your proficiency bonus.", effects=[ACT("beast-bite", "Bite", "action", when="toggle:raging", damage={"dice": "1d8 + mod.str", "type": "piercing"})], id="beast-bite"),
        F("Claws", text="1d6 slashing; one extra claw attack when you attack with a claw.", effects=[ACT("beast-claws", "Claws", "action", when="toggle:raging", damage={"dice": "1d6 + mod.str", "type": "slashing"})], id="beast-claws"),
        F("Tail", text="1d8 piercing with reach; reaction to add 1d8 to AC against an attack.", effects=[ACT("beast-tail", "Tail", "action", when="toggle:raging", damage={"dice": "1d8 + mod.str", "type": "piercing"}), ACT("tail-swipe", "Tail swipe (+1d8 AC)", "reaction", roll="1d8", when="toggle:raging")], id="beast-tail"),
    ]
    stars = [
        F("Archer", text="Bonus action: a ranged spell attack of 1d8 + Wis radiant.", effects=[ACT("starry-archer", "Luminous arrow", "bonus", damage={"dice": "1d8 + mod.wis", "type": "radiant"})], id="starry-archer"),
        F("Chalice", text="Healing spells also heal a creature within 30 ft for 1d8 + Wis.", effects=[REM("cast", "Chalice: a creature within 30 ft also heals 1d8 + Wis.")], id="starry-chalice"),
        F("Dragon", text="Treat 9 or lower as 10 on Int and Wis checks and concentration saves.", id="starry-dragon"),
    ]
    runes = [F(n + " Rune", text=t, effects=[RES(slug(n) + "-rune", n + " Rune", 1, "short", color="gold")] + fx) for n, t, fx in [
        ("Cloud", "Advantage on Sleight of Hand and Deception; reaction to redirect an attack to another creature.", [ACT("cloud-rune", "Cloud Rune", "reaction", cost={"resource": "cloud-rune", "amount": 1})]),
        ("Fire", "Double proficiency with tools; on a hit, 2d6 fire and restrain (Str save).", [RIDER("fire-rune", "Fire Rune", damage="2d6", damageType="fire", cost={"resource": "fire-rune", "amount": 1}, requires=["weapon", "hit"])]),
        ("Frost", "Advantage on Animal Handling and Intimidation; bonus action for +2 to Str and Con checks and saves for 10 minutes.", [ACT("frost-rune", "Frost Rune", "bonus", cost={"resource": "frost-rune", "amount": 1})]),
        ("Stone", "Advantage on Insight; darkvision 120 ft; reaction to charm a creature that ends its turn near you (Wis save).", [SENSE("darkvision", 120), ACT("stone-rune", "Stone Rune", "reaction", cost={"resource": "stone-rune", "amount": 1})]),
        ("Hill", "Advantage on saves against poison and resistance to poison; bonus action for resistance to bludgeoning, piercing and slashing for 1 minute.", [RESIST("poison"), ACT("hill-rune", "Hill Rune", "bonus", cost={"resource": "hill-rune", "amount": 1})]),
        ("Storm", "Advantage on Arcana; can't be surprised; bonus action to grant or impose advantage with your reactions for 1 minute.", [ACT("storm-rune", "Storm Rune", "bonus", cost={"resource": "storm-rune", "amount": 1})])]]
    X.fill(runes, "Rune Carver", span=3)
    models = [
        F("Guardian", text="Thunder gauntlets (1d8 thunder; the target has disadvantage attacking others); Defensive Field: bonus action for temp HP equal to your artificer level, proficiency-bonus times per long rest.",
          effects=[ACT("thunder-gauntlets", "Thunder Gauntlets", "action", damage={"dice": "1d8 + mod.int", "type": "thunder"}), RES("defensive-field", "Defensive Field", "prof", "long"),
                   ACT("use-defensive-field", "Defensive Field", "bonus", cost={"resource": "defensive-field", "amount": 1}, tempHp="classLevel")]),
        F("Infiltrator", text="Lightning launcher (1d6 lightning, 90/300 ft, +1d6 once per turn); +5 ft speed; advantage on Stealth.",
          effects=[ACT("lightning-launcher", "Lightning Launcher", "action", damage={"dice": "1d6 + mod.int", "type": "lightning"}), RIDER("lightning-launcher", "Lightning Launcher", damage="1d6", damageType="lightning", oncePer="turn", requires=["hit"]), BON("speed", 5), ADV("Stealth")]),
    ]
    genies = [F(n, text="Resistance to %s damage." % d, effects=[RESIST(d)], id="genie-" + slug(n)) for n, d in [("Dao", "bludgeoning"), ("Djinni", "thunder"), ("Efreeti", "fire"), ("Marid", "cold")]]
    return [
        {"id": "fighting-styles", "name": "Fighting Styles", "options": pick("Blind Fighting", "Interception", "Superior Technique", "Thrown Weapon Fighting", "Unarmed Fighting")},
        {"id": "ranger-fighting-styles", "name": "Ranger Fighting Styles", "options": pick("Blind Fighting", "Druidic Warrior", "Thrown Weapon Fighting")},
        {"id": "paladin-fighting-styles", "name": "Paladin Fighting Styles", "options": pick("Blessed Warrior", "Blind Fighting", "Interception")},
        {"id": "maneuvers", "name": "Maneuvers", "options": maneuvers},
        {"id": "metamagic", "name": "Metamagic", "options": metamagic},
        {"id": "eldritch-invocations", "name": "Eldritch Invocations", "options": inv},
        {"id": "pact-boons", "name": "Pact Boons", "options": talisman},
        {"id": "beast-forms", "name": "Form of the Beast", "options": beast},
        {"id": "starry-forms", "name": "Starry Form", "options": stars},
        {"id": "runes", "name": "Runes", "options": runes},
        {"id": "armor-models", "name": "Armor Model", "options": models},
        {"id": "genie-kinds", "name": "Genie Kind", "options": genies},
    ]


def tasha_feats():
    half = lambda fid, abils: [ABIL_CHOICE(fid + "-ability", "+1 ability score", abils, 1)] if len(abils) > 1 else [ASC(abils[0], 1, 20)]
    P = lambda t: {"formula": "1", "text": t}
    fs = [
        ("Artificer Initiate", None, "Learn an artificer cantrip and a 1st-level artificer spell (once per long rest without a slot); proficiency with one artisan's tool.",
         [CHOICE("ai-cantrip", "Artificer cantrip", "spell", 1, {"spells": {"list": "artificer", "level": 0}}), CHOICE("ai-spell", "1st-level artificer spell", "spell", 1, {"spells": {"list": "artificer", "level": 1}}, grants={"uses": 1, "recharge": "long", "noSlot": True}),
          CHOICE("ai-tool", "Artisan's tools", "tool", 1, {"list": ["any"]})]),
        ("Chef", None, "+1 Con or Wis; cook's utensils; extra healing on short rests; treats that give temp HP.", half("chef", ["con", "wis"]) + [PROF("tool", ["Cook's utensils"])]),
        ("Crusher", None, "+1 Str or Con; once per turn push a creature 5 ft with bludgeoning damage; crits give advantage to attacks against the target.", half("crusher", ["str", "con"])),
        ("Eldritch Adept", P("Spellcasting or Pact Magic"), "Learn one eldritch invocation.", [CHOICE("eldritch-adept", "Invocation", "option", 1, {"optionSet": "eldritch-invocations"})]),
        ("Fey Touched", None, "+1 Int, Wis or Cha; misty step and a 1st-level divination or enchantment spell, each once per long rest without a slot.",
         half("fey-touched", ["int", "wis", "cha"]) + [GRANT([{"id": "misty-step", "uses": 1, "recharge": "long", "noSlot": True}], ability="cha"), CHOICE("fey-touched-spell", "1st-level divination or enchantment spell", "spell", 1, {"spells": {"list": "any", "level": 1}}, grants={"uses": 1, "recharge": "long", "noSlot": True})]),
        ("Fighting Initiate", P("Proficiency with a martial weapon"), "Learn one Fighting Style.", [CHOICE("fighting-initiate", "Fighting Style", "option", 1, {"optionSet": "fighting-styles"})]),
        ("Gunner", None, "+1 Dex; firearm proficiency; ignore loading; no disadvantage at 5 ft.", half("gunner", ["dex"])),
        ("Metamagic Adept", P("Spellcasting or Pact Magic"), "Learn two Metamagic options and gain 2 sorcery points for them per long rest.", [CHOICE("metamagic-adept", "Metamagic", "option", 2, {"optionSet": "metamagic"}), RES("metamagic-adept", "Metamagic Adept points", 2, "long", color="psy")]),
        ("Piercer", None, "+1 Str or Dex; once per turn reroll a piercing damage die; crits add an extra die.", half("piercer", ["str", "dex"])),
        ("Poisoner", None, "Poisoner's kit; ignore poison resistance; craft potent poisons (2d8 poison, Con save).", [PROF("tool", ["Poisoner's kit"])]),
        ("Shadow Touched", None, "+1 Int, Wis or Cha; invisibility and a 1st-level illusion or necromancy spell, each once per long rest without a slot.",
         half("shadow-touched", ["int", "wis", "cha"]) + [GRANT([{"id": "invisibility", "uses": 1, "recharge": "long", "noSlot": True}], ability="cha"), CHOICE("shadow-touched-spell", "1st-level illusion or necromancy spell", "spell", 1, {"spells": {"list": "any", "level": 1}}, grants={"uses": 1, "recharge": "long", "noSlot": True})]),
        ("Skill Expert", None, "+1 to any score; one skill proficiency; expertise in one proficient skill.", half("skill-expert", ALL) + [CHOICE("skill-expert-skill", "Skill", "skill", 1, {"skills": "any"}), CHOICE("skill-expert-expertise", "Expertise", "expertise", 1, {"skills": "proficient"})]),
        ("Slasher", None, "+1 Str or Dex; once per turn reduce a target's speed by 10 ft with slashing damage; crits give disadvantage on its attacks.", half("slasher", ["str", "dex"])),
        ("Telekinetic", None, "+1 Int, Wis or Cha; invisible mage hand; bonus action shove 5 ft (Str save).", half("telekinetic", MENTAL) + [GRANT([{"id": "mage-hand"}], ability="cha"), ACT("telekinetic-shove", "Telekinetic shove", "bonus")]),
        ("Telepathic", None, "+1 Int, Wis or Cha; telepathy 60 ft; detect thoughts once per long rest without a slot.", half("telepathic", MENTAL) + [GRANT([{"id": "detect-thoughts", "uses": 1, "recharge": "long", "noSlot": True}], ability="cha")]),
    ]
    feats = [F(n) for n, _, _, _ in fs]
    X.fill(feats, "Feats", span=4)
    out = []
    for (name, pre, summary, fx), f in zip(fs, feats):
        e = {"id": slug(name), "name": name, "text": f.get("text") or summary, "effects": fx}
        if pre:
            e["prerequisite"] = pre
        out.append(e)
    return out
