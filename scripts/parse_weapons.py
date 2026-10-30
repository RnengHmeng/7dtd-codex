# -*- coding: utf-8 -*-
"""Parse 7 Days to Die weapons (items.xml), expanded to quality 1..6."""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\weapons_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")
QS = [1, 2, 3, 4, 5, 6]

CATS = [
    ("handgun", "手枪与冲锋枪", "Handguns & SMG", "#e0574c",
     "9mm 系列：射速与机动性平衡，弹药便宜。"),
    ("shotgun", "霰弹枪", "Shotguns", "#e08a3c",
     "近距离高爆发，一次打出多颗弹丸，远距离衰减明显。"),
    ("rifle", "步枪", "Rifles", "#e2b03c",
     "7.62 系列：单发伤害高、射程远，适合中远距离点射。"),
    ("mg", "机枪", "Machine Guns", "#c8762a",
     "高射速、大弹匣，压制成群丧尸，弹药消耗也最大。"),
    ("bow", "弓弩", "Bows & Crossbows", "#57b95f",
     "消音远程武器，箭矢可回收；弩的上弦更慢但伤害更高。"),
    ("explosive", "爆炸物", "Explosives", "#a06fd0",
     "火箭筒与投掷物：范围伤害，注意别把自己炸了。"),
    ("blade", "刀剑", "Blades", "#49b6e8",
     "小刀与砍刀：攻速快、出血效果，适合潜行收割。"),
    ("club", "棍棒", "Clubs", "#8fa3ad",
     "棒球棍与钢棍：击倒与眩晕，综合手感最稳的近战。"),
    ("sledge", "大锤", "Sledgehammers", "#ef8377",
     "单发伤害最高，挥动慢、耗体力，适合正面硬刚。"),
    ("spear", "长矛", "Spears", "#6ec6ef",
     "攻击距离最远的近战武器，可投掷，穿透力强。"),
    ("knuckles", "拳套", "Knuckles", "#c58ae0",
     "徒手格斗的强化版：极快攻速，连击叠伤害。"),
    ("baton", "电击棍", "Batons", "#7fd487",
     "智慧系武器：电击控制丧尸，配合机器人流派。"),
    ("misc", "炮塔与杂项", "Turrets & Misc", "#9a8f80",
     "垃圾炮塔、机械锤和火把等特殊武器。"),
]

# stats that get a dedicated slot at the top of the card
PRIMARY = ["EntityDamage", "BlockDamage", "RoundsPerMinute", "AttacksPerMinute",
           "MagazineSize", "MaxRange", "DegradationMax", "ModSlots", "StaminaLoss"]

MANUAL_LABEL = {
    "EntityDamage": "伤害", "BlockDamage": "物块伤害", "RoundsPerMinute": "射速（发/分）",
    "AttacksPerMinute": "攻速（次/分）", "MagazineSize": "弹匣", "MaxRange": "射程",
    "DegradationMax": "耐久", "ModSlots": "模组槽", "StaminaLoss": "体力消耗",
    "DamageModifier": "伤害修正", "HarvestCount": "采集量", "DamageBonus": "伤害加成",
    "TargetArmor": "目标护甲穿透", "EntityPenetrationCount": "穿透数量",
    "BlockPenetrationFactor": "物块穿透", "BlockRange": "物块攻击距离",
    "DismemberChance": "肢解几率", "GrazeDamageMultiplier": "擦伤倍率",
    "RoundRayCount": "弹丸数量", "ReloadSpeedMultiplier": "装填速度",
    "WeaponHandling": "武器操控性", "IncrementalSpreadMultiplier": "连射散布",
    "BurstRoundCount": "连发数", "DamageFalloffRange": "有效射程",
    "SpreadMultiplierAiming": "瞄准精确度", "SpreadMultiplierHip": "腰射精确度",
    "SpreadMultiplierCrouching": "蹲伏精确度", "SpreadMultiplierWalking": "移动精确度",
    "SpreadMultiplierRunning": "奔跑精确度", "SpreadDegreesVertical": "散布（垂直）",
    "SpreadDegreesHorizontal": "散布（水平）", "KickDegreesVerticalMin": "后坐力（垂直·小）",
    "KickDegreesVerticalMax": "后坐力（垂直·大）",
    "KickDegreesHorizontalMin": "后坐力（水平·小）",
    "KickDegreesHorizontalMax": "后坐力（水平·大）",
    "ProjectileVelocity": "初速", "HypothermalResist": "寒冷抗性",
}

ABS = {"EntityDamage", "BlockDamage", "RoundsPerMinute", "AttacksPerMinute", "MagazineSize",
       "MaxRange", "DegradationMax", "ModSlots", "StaminaLoss",
       "TargetArmor", "EntityPenetrationCount", "BlockPenetrationFactor", "BlockRange",
       "RoundRayCount", "BurstRoundCount", "DamageFalloffRange",
       "SpreadDegreesVertical", "SpreadDegreesHorizontal", "KickDegreesVerticalMin",
       "KickDegreesVerticalMax", "KickDegreesHorizontalMin", "KickDegreesHorizontalMax",
       "ProjectileVelocity", "HypothermalResist", "GrazeDamageMultiplier"}

FMT_OVERRIDE = {"ModSlots": "num"}


def clean(s):
    return COLOR_RE.sub("", (s or "").replace("\\n", "\n").replace("\r", "")).strip()


def load_loc():
    loc = {"schinese": {}, "english": {}}
    with open(CFG + r"\Localization.csv", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        h = next(r)
        idx = {n: i for i, n in enumerate(h)}
        for row in r:
            if not row or not row[0]:
                continue
            loc["schinese"][row[0]] = row[idx["schinese"]] or row[idx["tchinese"]]
            loc["english"][row[0]] = row[idx["english"]]
    return loc


def tier_values(values, tier):
    try:
        vals = [float(x) for x in str(values).split(",") if x.strip() != ""]
    except ValueError:
        return None
    if not vals:
        return None
    if not tier:
        return [round(vals[0], 3)] * 6
    tiers = [int(float(x)) for x in str(tier).split(",") if x.strip() != ""]
    if len(tiers) != len(vals):
        if len(vals) == 1:
            return [round(vals[0], 3)] * 6
        tiers = [tiers[0], tiers[-1]]
        vals = [vals[0], vals[-1]]
    out = []
    for q in QS:
        if q < tiers[0]:
            out.append(0.0)
        elif q == tiers[0]:
            out.append(vals[0])
        elif q >= tiers[-1]:
            out.append(vals[-1])
        else:
            for i in range(len(tiers) - 1):
                if tiers[i] <= q <= tiers[i + 1]:
                    span = tiers[i + 1] - tiers[i]
                    t = (q - tiers[i]) / span
                    out.append(vals[i] + (vals[i + 1] - vals[i]) * t)
                    break
    return [round(v, 3) for v in out]


def fmt_kind(name, op=""):
    if name == "DamageModifier":
        return "pctabs"
    if name in FMT_OVERRIDE:
        return FMT_OVERRIDE[name]
    if op.startswith("perc"):
        return "pct"
    return "num" if name in ABS else "pct"


def cat_of(name):
    for prefix, cid in (("gunHandgun", "handgun"), ("gunShotgun", "shotgun"),
                        ("gunRifle", "rifle"), ("gunMG", "mg"), ("gunBow", "bow"),
                        ("gunExplosives", "explosive"), ("thrown", "explosive"),
                        ("meleeWpnBlade", "blade"), ("meleeWpnClub", "club"),
                        ("meleeWpnSledge", "sledge"), ("meleeWpnSpear", "spear"),
                        ("meleeWpnKnuckles", "knuckles"), ("meleeWpnBaton", "baton")):
        if name.startswith(prefix):
            return cid
    return "misc"


def tidy_desc(s):
    if not s:
        return ""
    s = s.replace("[action:local:Primary]", "「左键」").replace("[action:local:Secondary]", "「右键」")
    s = re.sub(r"\[action:[^\]]+\]", "", s)
    return s


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(key, fallback=""):
        if not key:
            return fallback
        return clean(zh.get(key, "")) or clean(en.get(key, "")) or fallback

    root = ET.parse(CFG + r"\items.xml").getroot()
    items = {it.get("name"): it for it in root.iter("item")}

    def item_props(it):
        return {p.get("name"): p.get("value") for p in it.findall("property")}

    def ammo_base(ammo_id):
        it = items.get(ammo_id)
        if it is None:
            return None, None, 1
        ent = blk = None
        rays = 1
        for eg in it.findall("effect_group"):
            for pe in eg.findall("passive_effect"):
                if pe.get("name") == "EntityDamage" and pe.get("operation") == "base_set":
                    ent = float(pe.get("value").split(",")[0])
                if pe.get("name") == "BlockDamage" and pe.get("operation") == "base_set":
                    blk = float(pe.get("value").split(",")[0])
                if pe.get("name") == "RoundRayCount":
                    rays = int(float(pe.get("value").split(",")[0]))
        return ent, blk, rays

    weapons = []
    for it in root.iter("item"):
        props = item_props(it)
        tags = [x.strip() for x in (props.get("Tags") or "").split(",") if x.strip()]
        if "weapon" not in tags:
            continue
        name = it.get("name")
        if "Parts" in name or "Admin" in name:
            continue

        # ammo list from Action0
        ammo_ids = []
        for p in it.findall("property"):
            if p.get("class") == "Action0":
                for q in p.findall("property"):
                    if q.get("name") == "Magazine_items":
                        ammo_ids = [x.strip() for x in q.get("value").split(",") if x.strip()]

        default_ammo = ammo_ids[0] if ammo_ids else None
        ammo_dmg, ammo_blk, pellets = ammo_base(default_ammo) if default_ammo else (None, None, 1)

        dmg_eff, blk_eff, others = [], [], []
        for eg in it.findall("effect_group"):
            if eg.findall("requirement"):      # conditional group -> skip
                continue
            for pe in eg.findall("passive_effect"):
                pe_name = pe.get("name")
                op = pe.get("operation", "")
                val = pe.get("value", "")
                tier = pe.get("tier", "")
                ptags = pe.get("tags", "") or ""
                if not tier and "," in val:     # random roll, not quality-based
                    continue
                vals = tier_values(val, tier)
                if vals is None:
                    continue
                e = {"op": op, "vals": vals, "tags": ptags,
                     "secondary": "secondary" in ptags}
                if pe_name == "EntityDamage":
                    dmg_eff.append(e)
                elif pe_name == "BlockDamage":
                    blk_eff.append(e)
                elif op != "base_set" or pe_name in ABS:
                    others.append((pe_name, e))

        def combine(effects, base):
            v = [base] * 6
            for e in effects:
                if e["secondary"]:
                    continue
                if e["op"] == "base_set":
                    v = list(e["vals"])
                elif e["op"] == "base_add":
                    v = [a + b for a, b in zip(v, e["vals"])]
            perc = [0.0] * 6
            for e in effects:
                if e["secondary"]:
                    continue
                if e["op"] == "perc_add":
                    perc = [a + b for a, b in zip(perc, e["vals"])]
            return [round(a * (1 + p), 2) for a, p in zip(v, perc)]

        melee = not ammo_ids and not name.startswith(("gun", "thrown"))
        damage = combine(dmg_eff, ammo_dmg or 0) if (dmg_eff or ammo_dmg) else None
        block = combine(blk_eff, 0) if (melee and blk_eff) else None

        # secondary (power attack) damage bonus
        sec = [e for e in dmg_eff if e["secondary"]]

        chips = []
        if damage:
            chips.append({"k": ("伤害/弹丸" if pellets > 1 else "伤害"), "fmt": "num", "variants": [damage],
                          "note": ("按 %s 计算" % t(default_ammo)) if default_ammo else ""})
        if block:
            chips.append({"k": "物块伤害", "fmt": "num", "variants": [block]})

        mag_eff = [e for nm, e in others if nm == "MagazineSize"]
        if mag_eff:
            chips.append({"k": "弹匣", "fmt": "num", "variants": [combine(mag_eff, 0)]})

        grouped = {}
        order = []
        for eff_name, e in others:
            if eff_name in ("ModPowerBonus", "DegradationPerUse", "MagazineSize"):
                continue
            key = (eff_name, e["op"], e["tags"] if eff_name == "DamageModifier" else "")
            if key not in grouped:
                grouped[key] = []
                order.append(key)
            if e["vals"] not in grouped[key]:
                grouped[key].append(e["vals"])
        for key in order:
            eff_name, op = key[0], key[1]
            vals = grouped[key]
            if eff_name == "BurstRoundCount" and all(all(v in (0, 1) for v in arr) for arr in vals):
                continue
            label = MANUAL_LABEL.get(eff_name) or clean(zh.get("stat" + eff_name, "")) or eff_name
            fmt = fmt_kind(eff_name, op)
            if eff_name == "DamageFalloffRange" and op.startswith("perc"):
                label = "射程衰减"
            if eff_name == "DamageModifier":
                tag = key[2]
                if "head" in tag:
                    label, fmt = "爆头伤害", ("pct" if op.startswith("perc") else "pctabs")
                else:
                    mat = {"wood": "木头", "stone": "石头", "metal": "金属",
                           "iron": "铁", "dirt": "泥土"}.get(tag, tag)
                    label, fmt = "伤害（%s）" % mat, "pct"
            chips.append({"k": label, "fmt": fmt, "variants": vals})

        # sort: primary first in canonical order, then the rest
        cat = cat_of(name)
        ranged = cat in ("handgun", "shotgun", "rifle", "mg", "bow")
        core = (["伤害", "射速（发/分）", "弹匣", "射程", "耐久", "模组槽"] if ranged
                else ["伤害", "物块伤害", "攻速（次/分）", "体力消耗", "耐久", "模组槽"])
        for c in chips:
            c["primary"] = c["k"] in core or c["k"] == "伤害/弹丸"
        chips.sort(key=lambda c: core.index(c["k"]) if c["k"] in core
                   else (-1 if c["k"] == "伤害/弹丸" else 99))

        tier = ""
        for x in tags:
            if re.fullmatch(r"T\d", x):
                tier = x
                break
        if not tier:
            m = re.search(r"T(\d)", name)
            tier = "T" + m.group(1) if m else ""

        dm = re.search(r"T\d", name)
        weapons.append({
            "id": name,
            "name": t(name, name),
            "name_en": clean(en.get(name, "")),
            "cat": cat_of(name),
            "tier": tier,
            "desc": tidy_desc(t(name + "Desc")),
            "ammo": [t(a, a) for a in ammo_ids],
            "pellets": pellets,
            "ammo_dmg": ammo_dmg,
            "default_ammo": t(default_ammo, "") if default_ammo else "",
            "chips": chips,
            "damage": damage,
            "tiered": any(len(set(v)) > 1 for c in chips for v in c["variants"]),
        })

    order = {c[0]: i for i, c in enumerate(CATS)}
    weapons.sort(key=lambda w: (order.get(w["cat"], 99), w["tier"], w["name"]))

    cats = []
    for cid, cn, enn, color, intro in CATS:
        n = sum(1 for w in weapons if w["cat"] == cid)
        if n:
            cats.append({"id": cid, "name": cn, "en": enn, "color": color,
                         "intro": intro, "count": n})

    model = {"categories": cats, "weapons": weapons}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=1)

    print("weapons:", len(weapons))
    for c in cats:
        print("  %-10s %-8s %d" % (c["id"], c["name"], c["count"]))
    for w in weapons[:8]:
        print("   ", w["cat"], w["tier"], w["name"], "| dmg:", w["damage"],
              "| ammo:", w["default_ammo"], "| chips:", len(w["chips"]))
    print("untiered:", [w["name"] for w in weapons if not w["tiered"]][:8])
    print("no damage:", [w["name"] for w in weapons if not w["damage"]][:10])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
