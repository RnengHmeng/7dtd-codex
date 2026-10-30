# -*- coding: utf-8 -*-
"""Parse 7 Days to Die armor data, expanding every stat to quality 1..6."""
import csv
import json
import re
import sys
from collections import Counter
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\armor_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")
QS = [1, 2, 3, 4, 5, 6]

SLOTS = {"Head": "头部", "Chest": "胸甲", "Hands": "手部", "Feet": "足部"}
CLASS_CN = {"light": "轻甲", "medium": "中甲", "heavy": "重甲"}
CLASS_EN = {"light": "Light", "medium": "Medium", "heavy": "Heavy"}

UNIVERSAL = {"ModSlots", "ModPowerBonus", "PhysicalDamageResist", "ElementalDamageResist",
             "BuffResistance", "DegradationMax", "DegradationPerUse"}
PENALTY_KEYS = (("Mobility|", "mobility"), ("StaminaChangeOT|walking", "walk"),
                ("StaminaChangeOT|running", "run"), ("NoiseMultiplier|", "noise"))

LABELS = {
    "HarvestCount": "采集量", "EntityDamage": "伤害", "BlockDamage": "方块伤害",
    "CarryCapacity": "负重", "HealthMax": "生命上限", "StaminaMax": "体力上限",
    "StaminaLoss": "体力消耗", "RunSpeed": "奔跑速度", "PlayerExpGain": "经验获取",
    "BarteringBuying": "买入价格", "BarteringSelling": "卖出价格",
    "ScavengingTime": "搜刮时间", "LootStage": "搜刮阶段", "LootProb": "掉落概率",
    "LightMultiplier": "光照强度", "CrouchSpeed": "潜行速度",
    "EnemySearchDuration": "敌人搜索时间", "LockPickTime": "撬锁时间",
    "LockPickBreakChance": "撬锁损坏率", "AttacksPerMinute": "攻击速度",
    "RoundsPerMinute": "射速", "SilenceBlockSteps": "脚步噪音", "DamageBonus": "伤害加成",
    "GeneralDamageResist": "通用减伤", "VehicleFuelUsePer": "载具油耗",
    "FoodLossPerStaminaPointGained": "体力消耗（食物）",
    "WaterLossPerStaminaPointGained": "体力消耗（水分）",
    "TraderStage": "商人阶段",
    "Mobility": "移动能力", "NoiseMultiplier": "噪音", "StaminaChangeOT": "体力消耗",
}
PCT_BASE = {"DamageBonus", "GeneralDamageResist", "BarteringBuying", "BarteringSelling",
            "BuffResistance", "LightMultiplier"}

FALLBACK_NAMES = {"groupPrimitive": ("粗糙", "Primitive")}


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
    """Expand a passive_effect value/tier pair into 6 values (quality 1..6)."""
    vals = [float(x) for x in str(values).split(",") if x.strip() != ""]
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


def kind_of(name, op):
    if name == "SilenceBlockSteps":
        return "const"
    if name == "LootProb" and op.startswith("perc"):
        return "mult"
    if op.startswith("perc") or name in PCT_BASE:
        return "pct"
    return "raw"


def label_of(name, tags):
    if name == "StaminaChangeOT":
        return {"walking": "走动体力", "running": "跑动体力"}.get(tags, "体力消耗")
    if name == "LootProb" and "seedSkill" in (tags or ""):
        return "种子掉落"
    return LABELS.get(name, name)


def strip_desc(desc):
    if not desc:
        return ""
    out = []
    for i, line in enumerate(desc.split("\n")):
        line = line.strip()
        if i == 0 and line in ("轻甲", "中甲", "重甲", "中型护甲", "重型护甲"):
            continue
        if line.startswith("全套奖励") or line.startswith("完整套装加成"):
            continue
        if line:
            out.append(line)
    return "\n".join(out)


def mode_str(values):
    return Counter(values).most_common(1)[0][0]


def mode_arr(arrs):
    return [mode_str([a[i] for a in arrs]) for i in range(6)]


def parse_quality_groups(block, group_name):
    """cvar -> {quality: value} from effect groups gated by ArmorGroupLowestQuality."""
    out = {}
    for chunk in block.split("<effect_group")[1:]:
        m = re.search(r'name="ArmorGroupLowestQuality"[^>]*group_name="%s"[^>]*value="(\d+)"'
                      % re.escape(group_name), chunk)
        if not m:
            continue
        q = int(m.group(1))
        for cm in re.finditer(r'cvar="(\.\w+)"[^>]*?value="([-\d\.]+)"', chunk):
            out.setdefault(cm.group(1), {})[q] = float(cm.group(2))
    return out


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(key, fallback=""):
        if not key:
            return fallback
        return clean(zh.get(key, "")) or clean(en.get(key, "")) or fallback

    root = ET.parse(CFG + r"\items.xml").getroot()

    sets = {}
    skipped = []
    for it in root.iter("item"):
        props = {p.get("name"): p.get("value") for p in it.findall("property")}
        group = props.get("ArmorGroup")
        if not group:
            continue
        tags = props.get("Tags", "")
        cls = ("light" if "lightArmor" in tags else
               "medium" if "mediumArmor" in tags else
               "heavy" if "heavyArmor" in tags else "")
        if not cls:
            continue
        name = it.get("name")
        if props.get("CreativeMode") == "Dev" or "Demo" in name or "Admin" in name:
            skipped.append(name)
            continue

        entry = sets.setdefault(group, {"id": group, "cls": cls, "pieces": []})
        universal, pen, chips = {}, {}, []
        for pe in it.iter("passive_effect"):
            pname = pe.get("name")
            op = pe.get("operation", "")
            val = pe.get("value", "")
            tier = pe.get("tier", "")
            ptags = pe.get("tags", "") or ""
            q6 = tier_values(val, tier)
            if pname in UNIVERSAL:
                universal.setdefault(pname, []).append({"op": op, "vals": q6, "tags": ptags})
            elif pname in {"Mobility", "StaminaChangeOT", "NoiseMultiplier"}:
                pen["%s|%s" % (pname, ptags)] = {"op": op, "vals": q6}
            else:
                chips.append({"k": label_of(pname, ptags), "fmt": kind_of(pname, op),
                              "vals": q6})

        seen, uniq = set(), []
        for c in chips:
            key = (c["k"], tuple(c["vals"]))
            if key in seen:
                continue
            seen.add(key)
            uniq.append(c)

        entry["pieces"].append({
            "item": name,
            "slot": SLOTS.get(props.get("EquipSlot", ""), props.get("EquipSlot", "")),
            "name": t(name, name),
            "name_en": clean(en.get(name, "")),
            "desc": strip_desc(t(props.get("DescriptionKey", ""))),
            "chips": uniq,
            "pen": pen,
            "universal": universal,
        })

    # ---------- per-set stats
    for s in sets.values():
        p0 = s["pieces"][0]

        def stat(key):
            for e in p0["universal"].get(key, []):
                return e["vals"]
            return [0] * 6

        s["stats"] = {
            "armor": stat("PhysicalDamageResist"),
            "element": stat("ElementalDamageResist"),
            "durability": stat("DegradationMax"),
            "modslots": stat("ModSlots"),
            "element_tags": (p0["universal"].get("ElementalDamageResist", [{"tags": ""}])[0]["tags"] or ""),
        }

        common = {}
        for key, short in PENALTY_KEYS:
            entries = [p["pen"].get(key) for p in s["pieces"]]
            if any(e is None for e in entries):
                continue
            firsts = [e["vals"][0] for e in entries]
            if max(firsts) - min(firsts) > 0.004:
                continue
            common[short] = entries[0]
        s["pen"] = common

        for p in s["pieces"]:
            devs = []
            for key, short in PENALTY_KEYS:
                cur = p["pen"].get(key)
                if cur is None:
                    continue
                label = {"mobility": "移动能力", "walk": "走动体力",
                         "run": "跑动体力", "noise": "噪音"}[short]
                c = common.get(short)
                if c is not None and abs(cur["vals"][0] - c["vals"][0]) <= 0.004:
                    continue
                devs.append({"k": label, "fmt": kind_of(key.split("|")[0], cur["op"]),
                             "vals": cur["vals"], "dev": True})
            p["chips"] = devs + p["chips"]

    # ---------- set bonuses
    buffs_text = open(CFG + r"\buffs.xml", encoding="utf-8", errors="replace").read()
    buff_blocks = {}
    for m in re.finditer(r'<buff name="(buff\w+SetBonus)"[^>]*>', buffs_text):
        start = m.start()
        buff_blocks[m.group(1)] = buffs_text[start:buffs_text.find("</buff>", start)]

    for s in sets.values():
        s["bonus"] = {"name": "", "desc": "", "en": "", "flavor": "", "qdesc": [""] * 6}
        for bname, block in buff_blocks.items():
            if 'group_name="%s"' % s["id"] not in block:
                continue
            template = t(bname + "Desc").replace("后文改为：", "").strip()
            cvars = parse_quality_groups(block, s["id"])

            def render(q):
                def repl(m):
                    vals = cvars.get(m.group(1), {})
                    if not vals:
                        return "?"
                    v = vals.get(q)
                    if v is None:
                        v = vals[min(vals)]
                    return "%g" % v
                return re.sub(r"\{cvar\((\.\w+)[^}]*\)\}", repl, template)

            chunks = [c.strip() for c in render(6).split("\n\n") if c.strip()]
            flavor = chunks[0] if len(chunks) > 1 else ""
            s["bonus"] = {
                "name": t(bname + "Name"),
                "en": clean(en.get(bname + "Name", "")),
                "desc": render(6),
                "flavor": flavor,
                "qdesc": [render(q) for q in QS],
            }
            break

    # ---------- class summary
    classes = {}
    for cls in ("light", "medium", "heavy"):
        members = [s for s in sets.values() if s["cls"] == cls]
        if not members:
            continue
        pen = {}
        for key, short in PENALTY_KEYS:
            vals = []
            for s in members:
                for p in s["pieces"]:
                    e = p["pen"].get(key)
                    vals.append(None if e is None else round(e["vals"][0], 4))
            pen[short] = mode_str(vals)
        classes[cls] = {
            "name": CLASS_CN[cls], "name_en": CLASS_EN[cls],
            "armor": mode_arr([s["stats"]["armor"] for s in members]),
            "element": mode_arr([s["stats"]["element"] for s in members]),
            "durability": mode_arr([s["stats"]["durability"] for s in members]),
            "modslots": mode_arr([s["stats"]["modslots"] for s in members]),
            "pen": pen,
            "count_sets": sum(1 for s in members if len(s["pieces"]) >= 4),
            "element_tags": members[0]["stats"]["element_tags"],
        }

    # ---------- names + sort
    out = []
    for s in sets.values():
        cn = re.sub(r"\s*全套奖励$", "", s["bonus"]["name"]).strip()
        enn = re.sub(r"\s*Full Set Bonus$", "", s["bonus"]["en"]).strip()
        if not cn or not enn:
            fb = FALLBACK_NAMES.get(s["id"], ("", ""))
            cn = cn or fb[0] or s["id"]
            enn = enn or fb[1]
        s["name"], s["name_en"] = cn, enn
        if len(s["pieces"]) >= 4:
            out.append(s)

    order = {"light": 0, "medium": 1, "heavy": 2}
    out.sort(key=lambda s: (order[s["cls"]], s["name"]))

    singles = [p for s in sets.values() if len(s["pieces"]) < 4 for p in s["pieces"]]

    model = {"classes": classes, "sets": out, "singles": singles, "skipped": skipped}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=1)

    print("sets", len(out), "singles", len(singles), "skipped", skipped)
    s = out[0]
    print(s["name"], "armor", s["stats"]["armor"], "slots", s["stats"]["modslots"])
    print("chips:", [(c["k"], c["fmt"], c["vals"]) for c in s["pieces"][0]["chips"]])
    print("bonus q1:", s["bonus"]["qdesc"][0][-40:])
    print("bonus q6:", s["bonus"]["qdesc"][5][-40:])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
