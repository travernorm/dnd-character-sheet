"""Dungeon Master's Guide (2014): magic items.

Items and their text come from items.py (your extracted pages). The mechanics below are
written here: bonuses, AC formulas, score-setting items, charges and the actions that use
them, attack riders. Items the book folds into one entry (each Belt of Giant Strength,
each Ioun stone, +1/+2/+3 wands and rods) become separate items. Items the scan misses
but that matter mechanically are added with a short summary.

Plain +1/+2/+3 weapons, armor and shields don't need an item: give the gear entry a
"magic" bonus instead.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import *
import items as itemparser

ALL = ["str", "dex", "con", "int", "wis", "cha"]


def charges(id, name, n, regain="dawn"):
    return RES(id, name + " charges", n, regain, color="gold")


def spend(id, name, cid, n=1, econ="action", **kw):
    return ACT(id, name, econ, cost={"resource": cid, "amount": n}, **kw)


def wand(id, name, n, act, **kw):
    return [charges(id, name, n), spend("use-" + id, act, id, **kw)]


def setscore(ab, v):
    return SET("ability." + ab, v, mode="max")


# id -> extra fields (effects, and kind/armor/weapon/magic where the book defines the base item)
FX = {
    "cloak-of-protection": {"effects": [BON("ac", 1), BON("save.all", 1)]},
    "ring-of-protection": {"effects": [BON("ac", 1), BON("save.all", 1)]},
    "bracers-of-defense": {"effects": [BON("ac", 2, when="unarmored and noShield")]},
    "amulet-of-health": {"effects": [setscore("con", 19)]},
    "gauntlets-of-ogre-power": {"effects": [setscore("str", 19)]},
    "headband-of-intellect": {"effects": [setscore("int", 19)]},
    "belt-of-dwarvenkind": {"effects": [ASC("con", 2, 20), SENSE("darkvision", 60), RESIST("poison"), ADV("Saves against poison")]},
    "stone-of-good-luck-luckstone": {"effects": [BON("check.all", 1), BON("save.all", 1)]},
    "robe-of-the-archmagi": {"effects": [AC("15 + mod.dex", when="unarmored"), BON("spell.dc", 2), BON("spell.attack", 2), ADV("Saves against spells")]},
    "staff-of-power": {"effects": [BON("ac", 2), BON("save.all", 2), BON("spell.attack", 2), charges("staff-of-power", "Staff of Power", 20)]},
    "staff-of-the-magi": {"effects": [BON("spell.attack", 2), ADV("Saves against spells"), charges("staff-of-the-magi", "Staff of the Magi", 50)]},
    "staff-of-healing": {"effects": [charges("staff-of-healing", "Staff of Healing", 10), spend("staff-cure-wounds", "Staff: cure wounds", "staff-of-healing")]},
    "staff-of-fire": {"effects": [RESIST("fire"), charges("staff-of-fire", "Staff of Fire", 10), spend("staff-fireball", "Staff: fireball (3)", "staff-of-fire", 3)]},
    "staff-of-frost": {"effects": [RESIST("cold"), charges("staff-of-frost", "Staff of Frost", 10), spend("staff-cone-of-cold", "Staff: cone of cold (5)", "staff-of-frost", 5)]},
    "staff-of-striking": {"effects": [charges("staff-of-striking", "Staff of Striking", 10)], "kind": "weapon", "magic": 3,
                          "weapon": {"category": "simple", "ranged": False, "dmg": "1d6", "damageType": "bludgeoning", "versatile": "1d8", "props": ["Versatile"]}},
    "staff-of-thunder-and-lightning": {"effects": [charges("staff-tl", "Staff of Thunder and Lightning", 5, "dawn")]},
    "staff-of-the-woodlands": {"effects": [BON("spell.attack", 2), charges("staff-of-the-woodlands", "Staff of the Woodlands", 10)]},
    "staff-of-charming": {"effects": [charges("staff-of-charming", "Staff of Charming", 10)]},
    "staff-of-withering": {"effects": [charges("staff-of-withering", "Staff of Withering", 3)]},
    "staff-of-swarming-insects": {"effects": [charges("staff-of-swarming-insects", "Staff of Swarming Insects", 10)]},
    "wand-of-magic-missiles": {"effects": wand("wand-of-magic-missiles", "Wand of Magic Missiles", 7, "Wand: magic missile", damage={"dice": "3d4 + 3", "type": "force"})},
    "wand-of-fireballs": {"effects": wand("wand-of-fireballs", "Wand of Fireballs", 7, "Wand: fireball", damage={"dice": "8d6", "type": "fire"}, save={"ability": "dex", "dc": 15})},
    "wand-of-lightning-bolts": {"effects": wand("wand-of-lightning-bolts", "Wand of Lightning Bolts", 7, "Wand: lightning bolt", damage={"dice": "8d6", "type": "lightning"}, save={"ability": "dex", "dc": 15})},
    "wand-of-web": {"effects": wand("wand-of-web", "Wand of Web", 7, "Wand: web", save={"ability": "dex", "dc": 15})},
    "wand-of-paralysis": {"effects": wand("wand-of-paralysis", "Wand of Paralysis", 7, "Wand: paralysis", save={"ability": "con", "dc": 15})},
    "wand-of-fear": {"effects": wand("wand-of-fear", "Wand of Fear", 7, "Wand: fear", save={"ability": "wis", "dc": 15})},
    "wand-of-binding": {"effects": wand("wand-of-binding", "Wand of Binding", 7, "Wand: hold monster (5)", save={"ability": "wis", "dc": 17})},
    "wand-of-polymorph": {"effects": wand("wand-of-polymorph", "Wand of Polymorph", 7, "Wand: polymorph", save={"ability": "wis", "dc": 15})},
    "wand-of-wonder": {"effects": wand("wand-of-wonder", "Wand of Wonder", 7, "Wand of Wonder", roll="1d100")},
    "wand-of-magic-detection": {"effects": wand("wand-of-magic-detection", "Wand of Magic Detection", 3, "Wand: detect magic")},
    "wand-of-secrets": {"effects": wand("wand-of-secrets", "Wand of Secrets", 3, "Wand: find secret doors")},
    "wand-of-enemy-detection": {"effects": wand("wand-of-enemy-detection", "Wand of Enemy Detection", 7, "Wand: sense enemies")},
    "necklace-of-fireballs": {"effects": [RES("fireball-beads", "Fireball beads", 6, "never"), spend("throw-bead", "Throw a fireball bead", "fireball-beads", damage={"dice": "5d6", "type": "fire"}, save={"ability": "dex", "dc": 15})]},
    "pearl-of-power": {"effects": [RES("pearl-of-power", "Pearl of Power", 1, "dawn", when="attuned"),
                                   ACT("use-pearl-of-power", "Pearl of Power", "action", cost={"resource": "pearl-of-power", "amount": 1}, gain={"slots": {"total": 3, "maxLevel": 3, "count": 1}}, when="attuned")]},
    "ring-of-evasion": {"effects": [charges("ring-of-evasion", "Ring of Evasion", 3), spend("use-ring-of-evasion", "Ring of Evasion", "ring-of-evasion", econ="reaction")]},
    "ring-of-the-ram": {"effects": [charges("ring-of-the-ram", "Ring of the Ram", 3), spend("use-ring-of-the-ram", "Ring of the Ram", "ring-of-the-ram", damage={"dice": "2d10", "type": "force"})]},
    "ring-of-shooting-stars": {"effects": [charges("ring-of-shooting-stars", "Ring of Shooting Stars", 6)]},
    "ring-of-warmth": {"effects": [RESIST("cold")]},
    "ring-of-swimming": {"effects": [SPEED("swim", 40)]},
    "ring-of-jumping": {"effects": [GRANT([{"id": "jump", "noSlot": True, "econ": "bonus"}])]},
    "ring-of-feather-falling": {"effects": [REM("always", "Ring of Feather Falling: you fall at 60 ft per round and take no falling damage.")]},
    "boots-of-elvenkind": {"effects": [ADV("Stealth that relies on moving silently")]},
    "cloak-of-elvenkind": {"effects": [ADV("Stealth checks to hide")]},
    "boots-of-striding-and-springing": {"effects": [SET("speed", 30, mode="max")]},
    "boots-of-speed": {"effects": [{"type": "toggle", "id": "boots-of-speed", "name": "Boots of Speed", "endsOn": ["manual"]}, ACT("boots-of-speed", "Click the heels", "bonus", toggle="boots-of-speed")]},
    "winged-boots": {"effects": [SPEED("fly", "walk")]},
    "boots-of-the-winterlands": {"effects": [RESIST("cold")]},
    "slippers-of-spider-climbing": {"effects": [SPEED("climb", "walk")]},
    "cloak-of-the-manta-ray": {"effects": [SPEED("swim", 60)]},
    "cloak-of-arachnida": {"effects": [RESIST("poison"), SPEED("climb", "walk")]},
    "goggles-of-night": {"effects": [SENSE("darkvision", 60)]},
    "robe-of-eyes": {"effects": [SENSE("darkvision", 120), ADV("Perception that relies on sight")]},
    "eyes-of-the-eagle": {"effects": [ADV("Perception that relies on sight")]},
    "gloves-of-thievery": {"effects": [BON("skill.sleightOfHand", 5)]},
    "gloves-of-missile-snaring": {"effects": [ACT("missile-snaring", "Gloves of Missile Snaring", "reaction", roll="1d10 + mod.dex")]},
    "bracers-of-archery": {"effects": [PROF("weapon", ["Longbows", "Shortbows"]), BON("damage.ranged", 2, note="Longbows and shortbows")]},
    "brooch-of-shielding": {"effects": [RESIST("force")]},
    "periapt-of-proof-against-poison": {"effects": [{"type": "immunity", "damage": ["poison"]}, {"type": "conditionImmunity", "conditions": ["Poisoned"]}]},
    "periapt-of-wound-closure": {"effects": [REM("always", "Periapt of Wound Closure: you stabilize at 0 HP and heal double from Hit Dice.")]},
    "mantle-of-spell-resistance": {"effects": [ADV("Saves against spells")]},
    "scarab-of-protection": {"effects": [ADV("Saves against spells"), charges("scarab-of-protection", "Scarab of Protection", 12, "never")]},
    "helm-of-telepathy": {"effects": [GRANT([{"id": "detect-thoughts", "noSlot": True}, {"id": "suggestion", "uses": 1, "recharge": "dawn", "noSlot": True}])]},
    "cape-of-the-mountebank": {"effects": [GRANT([{"id": "dimension-door", "uses": 1, "recharge": "dawn", "noSlot": True}])]},
    "circlet-of-blasting": {"effects": [GRANT([{"id": "scorching-ray", "uses": 1, "recharge": "dawn", "noSlot": True}])]},
    "medallion-of-thoughts": {"effects": [charges("medallion-of-thoughts", "Medallion of Thoughts", 3), spend("use-medallion", "Medallion: detect thoughts", "medallion-of-thoughts")]},
    "cloak-of-displacement": {"effects": [REM("always", "Cloak of Displacement: attacks against you have disadvantage until you take damage (resets at the start of your turn).")]},
    "flame-tongue": {"effects": [{"type": "toggle", "id": "flame-tongue", "name": "Flame Tongue lit", "endsOn": ["manual"]}, ACT("ignite-flame-tongue", "Ignite Flame Tongue", "bonus", toggle="flame-tongue"),
                                 RIDER("flame-tongue", "Flame Tongue", damage="2d6", damageType="fire", when="toggle:flame-tongue", requires=["weapon", "hit"])]},
    "frost-brand": {"effects": [RESIST("fire"), RIDER("frost-brand", "Frost Brand", damage="1d6", damageType="cold", requires=["weapon", "hit"])]},
    "sun-blade": {"kind": "weapon", "magic": 2, "weapon": {"category": "martial", "ranged": False, "dmg": "1d8", "damageType": "radiant", "versatile": "1d10", "props": ["Finesse", "Versatile"]},
                  "effects": [RIDER("sun-blade-undead", "Sun Blade vs undead", damage="1d8", damageType="radiant", requires=["weapon", "hit"])]},
    "holy-avenger": {"magic": 3, "effects": [RIDER("holy-avenger", "Holy Avenger vs fiends or undead", damage="2d10", damageType="radiant", requires=["weapon", "hit"]), ADV("You and allies within 10 ft: saves against spells")]},
    "dragon-slayer": {"magic": 1, "effects": [RIDER("dragon-slayer", "Dragon Slayer vs dragons", damage="3d6", requires=["weapon", "hit"])]},
    "giant-slayer": {"magic": 1, "effects": [RIDER("giant-slayer", "Giant Slayer vs giants", damage="2d6", requires=["weapon", "hit"])]},
    "mace-of-disruption": {"effects": [RIDER("mace-of-disruption", "Mace of Disruption vs fiends or undead", damage="2d6", damageType="radiant", requires=["weapon", "hit"])]},
    "oathbow": {"effects": [RIDER("oathbow", "Oathbow vs sworn enemy", damage="3d6", damageType="piercing", requires=["ranged", "hit"])]},
    "javelin-of-lightning": {"kind": "weapon", "weapon": {"category": "simple", "ranged": False, "dmg": "1d6", "damageType": "piercing", "range": "30/120", "props": ["Thrown"]},
                             "effects": [RES("javelin-of-lightning", "Javelin of Lightning", 1, "dawn"), spend("use-javelin-of-lightning", "Javelin: lightning bolt", "javelin-of-lightning", damage={"dice": "4d6", "type": "lightning"}, save={"ability": "dex", "dc": 13})]},
    "dagger-of-venom": {"kind": "weapon", "magic": 1, "weapon": {"category": "simple", "ranged": False, "dmg": "1d4", "damageType": "piercing", "range": "20/60", "props": ["Finesse", "Light", "Thrown"]},
                        "effects": [RES("dagger-of-venom", "Dagger of Venom", 1, "dawn"), RIDER("dagger-of-venom", "Dagger of Venom poison", damage="2d10", damageType="poison", cost={"resource": "dagger-of-venom", "amount": 1}, requires=["hit"])]},
    "dwarven-thrower": {"kind": "weapon", "magic": 3, "weapon": {"category": "martial", "ranged": False, "dmg": "1d8", "damageType": "bludgeoning", "versatile": "1d10", "range": "20/60", "props": ["Versatile", "Thrown"]},
                        "effects": [RIDER("dwarven-thrower", "Dwarven Thrower (thrown)", damage="1d8", requires=["hit"])]},
    "berserker-axe": {"magic": 1, "effects": [BON("hp.perLevel", 1)]},
    "defender": {"magic": 3}, "vorpal-sword": {"magic": 3}, "luck-blade": {"magic": 1, "effects": [BON("save.all", 1)]},
    "nine-lives-stealer": {"magic": 2}, "sword-of-sharpness": {}, "vicious-weapon": {"effects": [RIDER("vicious-weapon", "Vicious Weapon (on a 20)", damage="2d6", requires=["hit"])]},
    "scimitar-of-speed": {"kind": "weapon", "magic": 2, "weapon": {"category": "martial", "ranged": False, "dmg": "1d6", "damageType": "slashing", "props": ["Finesse", "Light"]},
                          "effects": [ACT("scimitar-of-speed", "Scimitar of Speed attack", "bonus")]},
    "elven-chain": {"kind": "armor", "armor": {"category": "medium", "base": 13, "dexCap": 2}, "magic": 1},
    "dragon-scale-mail": {"kind": "armor", "armor": {"category": "medium", "base": 14, "dexCap": 2}, "magic": 1, "effects": [ADV("Saves against the Frightful Presence and breath weapons of dragons")]},
    "dwarven-plate": {"kind": "armor", "armor": {"category": "heavy", "base": 18, "dexCap": 0, "strength": 15, "stealthDisadvantage": True}, "magic": 2},
    "demon-armor": {"kind": "armor", "armor": {"category": "heavy", "base": 18, "dexCap": 0, "strength": 15, "stealthDisadvantage": True}, "magic": 1},
    "efreeti-chain": {"kind": "armor", "armor": {"category": "heavy", "base": 16, "dexCap": 0, "strength": 13, "stealthDisadvantage": True}, "magic": 3, "effects": [{"type": "immunity", "damage": ["fire"]}]},
    "glamoured-studded-leather-armor": {"kind": "armor", "armor": {"category": "light", "base": 12, "dexCap": None}, "magic": 1},
    "plate-armor-of-etherealness": {"kind": "armor", "armor": {"category": "heavy", "base": 18, "dexCap": 0, "strength": 15, "stealthDisadvantage": True}},
    "arrow-catching-shield": {"kind": "shield", "armor": {"base": 2}, "effects": [BON("ac", 2, note="Against ranged attacks"), ACT("arrow-catching", "Arrow-Catching Shield", "reaction")]},
    "animated-shield": {"kind": "shield", "armor": {"base": 2}},
    "sentinel-shield": {"kind": "shield", "armor": {"base": 2}, "effects": [ADV("Initiative and Perception")]},
    "spellguard-shield": {"kind": "shield", "armor": {"base": 2}, "effects": [ADV("Saves against spells")]},
    "shield-of-missile-attraction": {"kind": "shield", "armor": {"base": 2}, "effects": [RESIST("ranged weapon damage")]},
    "potion-of-healing": {"effects": [ACT("drink-healing", "Drink potion of healing", "action", heal="2d4 + 2")]},
    "elixir-of-health": {"effects": [ACT("drink-elixir-of-health", "Drink elixir of health", "action")]},
    "potion-of-heroism": {"effects": [ACT("drink-heroism", "Drink potion of heroism", "action", tempHp=10)]},
    "potion-of-speed": {"effects": [ACT("drink-speed", "Drink potion of speed", "action")]},
}
# Variants the book lists in one entry.
EXTRA = []
for name, v, rar in [("Hill", 21, "Rare"), ("Stone", 23, "Very rare"), ("Frost", 23, "Very rare"), ("Fire", 25, "Very rare"), ("Cloud", 27, "Legendary"), ("Storm", 29, "Legendary")]:
    EXTRA.append({"id": "belt-of-%s-giant-strength" % slug(name), "name": "Belt of %s Giant Strength" % name, "kind": "wondrous", "rarity": rar, "attune": True,
                  "text": "Your Strength score is %d while you wear this belt." % v, "effects": [setscore("str", v)]})
    EXTRA.append({"id": "potion-of-%s-giant-strength" % slug(name), "name": "Potion of %s Giant Strength" % name, "kind": "potion", "rarity": rar,
                  "text": "Your Strength score becomes %d for 1 hour." % v, "effects": [ACT("drink-%s-giant-strength" % slug(name), "Drink potion of %s giant strength" % name.lower(), "action")]})
for name, heal, rar in [("Greater", "4d4 + 4", "Uncommon"), ("Superior", "8d4 + 8", "Rare"), ("Supreme", "10d4 + 20", "Very rare")]:
    EXTRA.append({"id": "potion-of-%s-healing" % slug(name), "name": "Potion of %s Healing" % name, "kind": "potion", "rarity": rar,
                  "text": "You regain %s hit points when you drink this potion." % heal, "effects": [ACT("drink-%s-healing" % slug(name), "Drink potion of %s healing" % name.lower(), "action", heal=heal)]})
for name, ab, text in [("Agility", "dex", "+2 Dexterity (max 20)"), ("Fortitude", "con", "+2 Constitution (max 20)"), ("Insight", "wis", "+2 Wisdom (max 20)"),
                       ("Intellect", "int", "+2 Intelligence (max 20)"), ("Leadership", "cha", "+2 Charisma (max 20)"), ("Strength", "str", "+2 Strength (max 20)")]:
    EXTRA.append({"id": "ioun-stone-of-%s" % slug(name), "name": "Ioun Stone of %s" % name, "kind": "wondrous", "rarity": "Very rare", "attune": True, "text": "While it orbits your head: " + text + ".", "effects": [ASC(ab, 2, 20)]})
EXTRA += [
    {"id": "ioun-stone-of-protection", "name": "Ioun Stone of Protection", "kind": "wondrous", "rarity": "Rare", "attune": True, "text": "+1 bonus to AC while it orbits your head.", "effects": [BON("ac", 1)]},
    {"id": "ioun-stone-of-awareness", "name": "Ioun Stone of Awareness", "kind": "wondrous", "rarity": "Rare", "attune": True, "text": "You can't be surprised while it orbits your head.", "effects": []},
    {"id": "ioun-stone-of-mastery", "name": "Ioun Stone of Mastery", "kind": "wondrous", "rarity": "Legendary", "attune": True, "text": "Your proficiency bonus increases by 1.", "effects": [REM("always", "Ioun Stone of Mastery: add 1 to your proficiency bonus.")]},
    {"id": "ioun-stone-of-regeneration", "name": "Ioun Stone of Regeneration", "kind": "wondrous", "rarity": "Legendary", "attune": True, "text": "Regain 15 HP at the end of each hour while it orbits your head.", "effects": []},
]
for b, rar in [(1, "Uncommon"), (2, "Rare"), (3, "Very rare")]:
    EXTRA.append({"id": "wand-of-the-war-mage-%d" % b, "name": "Wand of the War Mage, +%d" % b, "kind": "wand", "rarity": rar, "attune": "by a spellcaster",
                  "text": "While holding it: +%d to spell attack rolls, and your spell attacks ignore half cover." % b, "effects": [BON("spell.attack", b, when="equipped")]})
    EXTRA.append({"id": "rod-of-the-pact-keeper-%d" % b, "name": "Rod of the Pact Keeper, +%d" % b, "kind": "rod", "rarity": rar, "attune": "by a warlock",
                  "text": "While holding it: +%d to warlock spell attacks and save DC. Once per long rest, action: regain one warlock spell slot." % b,
                  "effects": [BON("spell.dc.warlock", b, when="equipped"), BON("spell.attack.warlock", b, when="equipped"), RES("rod-of-the-pact-keeper", "Rod of the Pact Keeper", 1, "long", when="attuned"),
                              ACT("use-rod-of-the-pact-keeper", "Rod: regain a pact slot", "action", cost={"resource": "rod-of-the-pact-keeper", "amount": 1}, gain={"resource": "pact", "amount": 1}, when="attuned")]})
# Mechanically useful items the scan can miss; used only when items.py doesn't find them.
FALLBACK = {
    "frost-brand": {"name": "Frost Brand", "kind": "weapon", "rarity": "Very rare", "attune": True, "type": "Weapon (any sword), very rare (requires attunement)",
                    "text": "Extra 1d6 cold damage on a hit, fire resistance, sheds light in freezing cold, and can put out nearby flames once per hour."},
    "dragon-scale-mail": {"name": "Dragon Scale Mail", "kind": "armor", "rarity": "Very rare", "attune": True, "type": "Armor (scale mail), very rare (requires attunement)",
                          "text": "+1 AC, advantage on saves against dragons' Frightful Presence and breath weapons, resistance to one damage type set by the dragon, and you can sense dragons once per dawn."},
    "sword-of-wounding": {"name": "Sword of Wounding", "kind": "weapon", "rarity": "Rare", "attune": True, "type": "Weapon (any sword), rare (requires attunement)",
                          "text": "Damage from it can't be healed except by resting; once per turn a hit wounds the target for 1d4 necrotic each turn until it succeeds on a DC 15 Con save."},
}


def build():
    found = itemparser.parse("dmg", 148, 230)
    by = {i["id"]: i for i in found}
    for k, v in FALLBACK.items():
        if k not in by:
            by[k] = dict(v, id=k)
    for k, extra in FX.items():
        if k in by:
            for f, val in extra.items():
                by[k][f] = val
    for e in EXTRA:
        by.setdefault(e["id"], e)
    out = sorted(by.values(), key=lambda i: i["name"])
    for i in out:
        if not i.get("effects"):
            i.pop("effects", None)
        if i.get("page") is None:
            i.pop("page", None)
    n = sum(1 for i in out if i.get("effects"))
    print("items: %d from the book, %d variants, %d with effects" % (len(found), len(EXTRA), n))
    return {"items": out}
