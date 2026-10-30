# -*- coding: utf-8 -*-
"""Parse 7 Days to Die item mods (item_modifiers.xml), expanded to quality 1..6."""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\mods_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")
QS = [1, 2, 3, 4, 5, 6]

CATS = [
    ("gun", "枪械配件", "Gun Mods", "#e0574c",
     "装在手枪、冲锋枪、步枪、霰弹枪和机枪上：瞄具、枪管、枪口、弹匣、握把、枪托、扳机组。"),
    ("melee", "近战与工具", "Melee & Tool", "#e2b03c",
     "装在近战武器和工具上：刀刃、锤头、握把、钉刺、特效伤害。"),
    ("bow", "弓弩配件", "Bow Mods", "#57b95f",
     "弓箭与弩专用：弓弦、箭台、箭矢效果。"),
    ("armor", "护甲配件", "Armor Mods", "#49b6e8",
     "装在头盔、胸甲、手套、靴子上：内衬、装甲板、口袋、降噪、属性 +1、夜视。"),
    ("vehicle", "载具配件", "Vehicle Mods", "#a06fd0",
     "装在载具上：引擎、车灯、座位、油箱、车铲、车体装甲、储物。"),
    ("drone", "无人机配件", "Drone Mods", "#8fa3ad",
     "装在垃圾无人机上：装甲、货舱、士气、头灯、医疗、武器。"),
    ("dye", "染料", "Dyes", "#c8762a",
     "纯外观，不占属性：给武器、工具、载具、无人机换色。"),
]

# installable / effect tag -> Chinese
TAG_CN = {
    "weapon": "武器", "tool": "工具", "melee": "近战武器", "gun": "枪械", "ranged": "远程武器",
    "shotgun": "霰弹枪", "firingMode": "射击模式位", "barrelAttachments": "枪管位",
    "sideAttachments": "侧挂位", "smallTopAttachments": "小瞄具位",
    "mediumTopAttachments": "中瞄具位", "largeTopAttachments": "大瞄具位",
    "bottomAttachments": "下挂位", "stock": "枪托位", "magazine": "弹匣位",
    "drumMagazine": "弹鼓位", "modGunShotgunTubeExtenderMagazine": "霰弹枪弹仓",
    "turretRanged": "远程炮塔", "turretMelee": "近战炮塔", "bow": "弓", "perkArchery": "弓弩",
    "armor": "护甲", "armorHead": "头盔", "armorChest": "胸甲", "armorHands": "手套",
    "armorFeet": "靴子", "head": "头部",
    "vehicle": "载具", "vengine": "引擎", "vlight": "车灯", "vseat": "座位", "vfuel": "油箱",
    "vplow": "车铲", "varmor": "车体装甲", "vstorage": "载具储物",
    "drone": "无人机",
    "club": "棍棒", "axe": "斧头", "knife": "小刀", "machete": "砍刀", "shovel": "铲子",
    "longShaft": "长柄武器", "light": "轻型棍棒", "medium": "中型棍棒", "heavy": "重型棍棒",
    "motorTool": "电动工具", "perkBrawler": "铁拳", "perkJavelinMaster": "长矛",
    "perkDeepCuts": "利刃", "perkElectrocutioner": "电击棍",
    # effect tags
    "attStrength": "力量", "attPerception": "感知", "attFortitude": "强健",
    "attAgility": "敏捷", "attIntellect": "智慧",
    "wood": "木头", "stone": "石头", "iron": "铁", "dirt": "泥土", "animal": "动物",
    "heat": "热", "electrical": "电",
}

ABS = {"AttributeLevel", "SkillLevel", "PerkLevel", "BurstRoundCount", "VehicleSeats",
       "DegradationMax", "HypothermalResist", "HyperthermalResist", "LightIntensity",
       "JunkDroneModCooldown", "LootStage", "HealthMax", "DismemberChance",
       "TreasureBlocksPerReduction", "CarryCapacity", "JumpStrength",
       "SpreadDegreesVertical", "SpreadDegreesHorizontal",
       "PhysicalDamageResist", "ElementalDamageResist"}

MANUAL_LABEL = {
    "AttributeLevel": "属性等级", "BarteringBuying": "买入价格", "BarteringSelling": "卖出价格",
    "BurstRoundCount": "连发数", "DamageModifier": "伤害（按材质）", "DismemberChance": "肢解几率",
    "ElementalDamageResist": "元素抗性", "HealthMax": "生命上限",
    "IncrementalSpreadMultiplier": "连射散布", "JunkDroneModCooldown": "无人机冷却",
    "KickDegreesVerticalMin": "后坐力（垂直·小）", "KickDegreesVerticalMax": "后坐力（垂直·大）",
    "KickDegreesHorizontalMin": "后坐力（水平·小）", "KickDegreesHorizontalMax": "后坐力（水平·大）",
    "LightIntensity": "灯光强度", "LightMultiplier": "亮度", "NoiseMultiplier": "噪音",
    "PerkLevel": "特长等级", "ProjectileStickChance": "钉住几率", "ReloadSpeedMultiplier": "装填速度",
    "SkillLevel": "技能等级", "SpreadDegreesHorizontal": "散布（水平）",
    "SpreadDegreesVertical": "散布（垂直）", "SpreadMultiplierCrouching": "蹲伏精确度",
    "SpreadMultiplierWalking": "移动精确度", "TreasureBlocksPerReduction": "宝藏方块减少",
    "VehicleBlockDamage": "载具物块伤害", "VehicleEntityDamage": "载具实体伤害",
    "VehicleFuelMaxPer": "油箱容量", "VehicleFuelUsePer": "载具油耗",
    "VehicleMotorTorquePer": "引擎扭矩", "VehicleSeats": "座位数",
    "VehicleStrongSelfDamage": "载具自伤", "VehicleVelocityMaxPer": "载具极速",
    "WalkSpeed": "行走速度",
}

# extra labels that exist as stat<Name> in Localization.csv
STAT_FALLBACK = {}


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
        if q <= tiers[0]:
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


def is_pct(name, op):
    if name == "MagazineSize":
        return op.startswith("perc")
    if name == "MaxRange":
        return not op.startswith("base_set")
    return name not in ABS


def kind_of(name, op):
    if op.endswith("_set") and name.endswith("Per"):
        return "mulset"
    pct = is_pct(name, op)
    if op.endswith("_set"):
        return "pctset" if pct else "rawset"
    return "pct" if pct else "raw"


def cat_of(inst_tags, mtag, name):
    tags = set(inst_tags)
    if "dye" in mtag or name.startswith("modDye"):
        return "dye"
    if "drone" in tags:
        return "drone"
    if any(t.startswith("v") and t != "vehicle" for t in tags) or "vehicle" in tags:
        return "vehicle"
    if any(t.startswith("armor") for t in tags) or "head" in tags:
        return "armor"
    if tags & {"melee", "tool", "club", "axe", "knife", "machete", "shovel", "light",
               "medium", "heavy", "motorTool", "turretMelee", "longShaft", "perkBrawler",
               "perkJavelinMaster", "perkDeepCuts", "perkElectrocutioner"}:
        return "melee"
    if tags & {"bow", "perkArchery"}:
        return "bow"
    return "gun"


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(key, fallback=""):
        if not key:
            return fallback
        return clean(zh.get(key, "")) or clean(en.get(key, "")) or fallback

    def label(name, tags):
        if name == "StaminaChangeOT":
            base = {"walking": "走动体力", "running": "跑动体力"}.get(tags or "", "体力值/秒")
        else:
            base = clean(zh.get("stat" + name, "")) or MANUAL_LABEL.get(name) or name
        parts = [TAG_CN[x] for x in (tags or "").split(",") if x in TAG_CN]
        if parts and name in ("AttributeLevel", "DamageModifier", "EntityDamage",
                              "BlockDamage", "ElementalDamageResist", "StaminaLoss"):
            base = "%s（%s）" % (base, "/".join(parts))
        return base

    root = ET.parse(CFG + r"\item_modifiers.xml").getroot()
    mods = []
    skipped = []
    for m in root.iter("item_modifier"):
        props = {p.get("name"): p.get("value") for p in m.findall("property")}
        name = m.get("name")
        inst = [x.strip() for x in (m.get("installable_tags") or "").split(",") if x.strip()]
        mtag = [x.strip() for x in (m.get("modifier_tags") or "").split(",") if x.strip()]
        cm = props.get("CreativeMode")
        if not inst or cm in ("Dev", "Test") or name in ("modGeneralMaster",):
            skipped.append(name)
            continue

        chips = []
        for pe in m.iter("passive_effect"):
            pname = pe.get("name")
            op = pe.get("operation", "")
            vals = tier_values(pe.get("value", ""), pe.get("tier", ""))
            if vals is None:
                continue
            chips.append({"k": label(pname, pe.get("tags", "")),
                          "fmt": kind_of(pname, op), "vals": vals})

        # merge same-label effects (different conditions) into one chip with variants
        grouped, order_keys = {}, []
        for c in chips:
            key = (c["k"], c["fmt"])
            if key not in grouped:
                grouped[key] = []
                order_keys.append(key)
            if c["vals"] not in grouped[key]:
                grouped[key].append(c["vals"])
        uniq = [{"k": k, "fmt": f, "variants": grouped[(k, f)]} for k, f in order_keys]

        desc_key = props.get("DescriptionKey") or (name + "Desc")
        mods.append({
            "id": name,
            "name": t(name, name),
            "name_en": clean(en.get(name, "")),
            "cat": cat_of(inst, mtag, name),
            "install": [TAG_CN.get(x, x) for x in inst],
            "install_raw": inst,
            "chips": uniq,
            "desc": t(desc_key),
            "tiered": any(len(set(v)) > 1 for c in uniq for v in c["variants"]),
        })

    order = {c[0]: i for i, c in enumerate(CATS)}
    mods.sort(key=lambda m: (order.get(m["cat"], 99), m["name"]))

    cats = []
    for cid, cn, enn, color, intro in CATS:
        n = sum(1 for m in mods if m["cat"] == cid)
        if n:
            cats.append({"id": cid, "name": cn, "en": enn, "color": color,
                         "intro": intro, "count": n})

    model = {"categories": cats, "mods": mods, "skipped": skipped}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=1)

    print("mods:", len(mods), "skipped:", len(skipped))
    for c in cats:
        print("  %-8s %-8s %d" % (c["id"], c["name"], c["count"]))
    for m in mods[:6]:
        print("   ", m["cat"], m["name"], "| install:", m["install"], "| chips:",
              [(c["k"], c["fmt"], c["variants"][0][0], c["variants"][0][-1]) for c in m["chips"]][:3])
    print("untiered:", sum(1 for m in mods if not m["tiered"]))
    print("no desc:", [m["name"] for m in mods if not m["desc"]][:8])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
