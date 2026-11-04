# -*- coding: utf-8 -*-
"""Parse tools (axes, picks, shovels, electric, salvage) from items.xml."""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\tools_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")

CATS = [
    ("axe", "斧头", "Axes", "#e0574c", "砍树、拆木结构的主力，伐木速度最快。"),
    ("pick", "镐", "Pickaxes", "#e2b03c", "挖矿、拆石头，对矿物和石头有加成。"),
    ("shovel", "铲子", "Shovels", "#8fa3ad", "挖土、挖沙，对泥土和沙砾效率最高。"),
    ("electric", "电动工具", "Power Tools", "#49b6e8", "电锯、螺旋钻、钉枪：耗油/耗电，但效率碾压手动工具。"),
    ("salvage", "拆解工具", "Salvage Tools", "#57b95f", "扳手、棘轮、冲击起子：拆电器和载具能多回收零件。"),
    ("repair", "修理工具", "Repair Tools", "#c58ae0", "石斧、羊角锤：修理建筑方块，也能当武器用。"),
]

MATS = {"wood": "木头", "earth": "泥土", "stone": "石头", "metal": "金属",
        "terrGravel": "砂砾", "terrAsphalt": "沥青", "terrDestroyedStone": "碎石"}

SKIP_STATS = {"SphereCastRadius", "BurstRoundCount", "IncrementalSpreadMultiplier",
             "SpreadDegreesVertical", "SpreadDegreesHorizontal", "SpreadMultiplierAiming",
             "SpreadMultiplierCrouching", "SpreadMultiplierWalking", "SpreadMultiplierRunning",
             "KickDegreesVerticalMin", "KickDegreesVerticalMax", "KickDegreesHorizontalMin",
             "KickDegreesHorizontalMax", "ReloadSpeedMultiplier", "DamageFalloffRange"}

SKIP = {"meleeToolTorch", "meleeToolFlashlight02", "meleeToolWireTool",
        "meleeToolPaintTool", "meleeToolBlockReplaceTool"}


def clean(s):
    return COLOR_RE.sub("", (s or "").replace("\\n", "\n")).strip()


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
    for q in [1, 2, 3, 4, 5, 6]:
        if q < tiers[0]:
            out.append(0.0)
        elif q >= tiers[-1]:
            out.append(vals[-1])
        else:
            for i in range(len(tiers) - 1):
                if tiers[i] <= q <= tiers[i + 1]:
                    t = (q - tiers[i]) / (tiers[i + 1] - tiers[i])
                    out.append(vals[i] + (vals[i + 1] - vals[i]) * t)
                    break
    return [round(v, 3) for v in out]


def cat_of(name):
    if "Chainsaw" in name or "Auger" in name or "Nailgun" in name:
        return "electric"
    if "Salvage" in name:
        return "salvage"
    if "Pick" in name:
        return "pick"
    if "Shovel" in name:
        return "shovel"
    if "Axe" in name:
        return "axe"
    return "repair"


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(k, fb=""):
        return (clean(zh.get(k, "")) or clean(en.get(k, "")) or fb) if k else fb

    root = ET.parse(CFG + r"\items.xml").getroot()
    out = []
    for it in root.iter("item"):
        name = it.get("name")
        props = {p.get("name"): p.get("value") for p in it.findall("property") if p.get("class") is None}
        tags = [x.strip() for x in (props.get("Tags") or "").split(",") if x.strip()]
        if "tool" not in tags or "Parts" in name or "Admin" in name or name in SKIP:
            continue

        dmg, blk, mats, others, rolls = [], [], [], [], {}
        handling = None
        for eg in it.findall("effect_group"):
            if eg.findall("requirement"):
                continue
            for pe in eg.findall("passive_effect"):
                pn = pe.get("name")
                op = pe.get("operation", "")
                val = pe.get("value", "")
                tier = pe.get("tier", "")
                ptags = pe.get("tags", "") or ""
                if not tier and "," in val:
                    try:
                        lo, hi = [float(x) for x in val.split(",")[:2]]
                    except ValueError:
                        continue
                    rolls.setdefault(pn, {"op": op, "lo": lo, "hi": hi})
                    continue
                vals = tier_values(val, tier)
                if vals is None:
                    continue
                e = {"op": op, "vals": vals, "secondary": "secondary" in ptags}
                if pn == "WeaponHandling" and op == "base_set":
                    handling = float(vals[0])
                elif pn == "EntityDamage":
                    dmg.append(e)
                elif pn == "BlockDamage":
                    blk.append(e)
                elif pn == "DamageModifier":
                    for m in [x.strip() for x in ptags.split(",") if x.strip()]:
                        mats.append((m, e))
                else:
                    others.append((pn, e))

        def combine(effects, base=0.0):
            v = [base] * 6
            for x in effects:
                if x["secondary"]:
                    continue
                if x["op"] == "base_set":
                    v = list(x["vals"])
                elif x["op"] == "base_add":
                    v = [a + b for a, b in zip(v, x["vals"])]
            perc = [0.0] * 6
            for x in effects:
                if x["secondary"]:
                    continue
                if x["op"] == "perc_add":
                    perc = [a + b for a, b in zip(perc, x["vals"])]
            return [round(a * (1 + p), 2) for a, p in zip(v, perc)]

        chips = []
        if dmg:
            chips.append({"k": "伤害", "fmt": "num", "variants": [combine(dmg)], "stat": "EntityDamage"})
        if blk:
            chips.append({"k": "物块伤害", "fmt": "num", "variants": [combine(blk)], "stat": "BlockDamage"})

        grouped, order = {}, []
        for pn, e in others:
            if pn in ("ModPowerBonus", "DegradationPerUse") or pn in SKIP_STATS:
                continue
            key = (pn, e["op"])
            if key not in grouped:
                grouped[key] = []
                order.append(key)
            if e["vals"] not in grouped[key]:
                grouped[key].append(e["vals"])
        for pn, op in order:
            vals = grouped[(pn, op)]
            label = {"AttacksPerMinute": "攻速（次/分）", "StaminaLoss": "体力消耗",
                     "DegradationMax": "耐久", "ModSlots": "模组槽", "MaxRange": "射程",
                     "BlockRange": "物块攻击距离", "HarvestCount": "采集倍率",
                     "PlayerExpGain": "经验获取", "RoundsPerMinute": "转速（发/分）",
                     "DamageFalloffRange": "有效射程",
                     "MagazineSize": "燃料容量"}.get(pn, pn)
            if pn == "DamageFalloffRange" and op.startswith("perc"):
                label = "射程衰减"
            fmt = "x" if pn == "HarvestCount" else (
                "pct" if op.startswith("perc") else "num")
            chips.append({"k": label, "fmt": fmt, "variants": vals, "stat": pn})

        for mat, e in mats:
            if e["op"] != "perc_add":
                continue
            chips.append({"k": "对%s" % MATS.get(mat, mat), "fmt": "mult",
                          "variants": [e["vals"]], "stat": "DamageModifier"})

        if handling is not None:
            chips.append({"k": "武器操控性", "fmt": "x",
                          "variants": [[handling] * 6], "stat": "WeaponHandling"})

        for c in chips:
            r = rolls.get(c.get("stat") or "")
            if r:
                c["roll"] = r

        core = ["伤害", "物块伤害", "攻速（次/分）", "体力消耗", "耐久", "模组槽"]
        for c in chips:
            c["primary"] = c["k"] in core
        chips.sort(key=lambda c: core.index(c["k"]) if c["k"] in core else 99)

        tier = ""
        m = re.search(r"T(\d)", name)
        if m:
            tier = "T" + m.group(1)

        out.append({
            "id": name,
            "name": t(name, name),
            "name_en": clean(en.get(name, "")),
            "cat": cat_of(name),
            "tier": tier,
            "desc": t(props.get("DescriptionKey") or name + "Desc"),
            "chips": chips,
            "has_roll": any("roll" in c for c in chips),
            "rolls": [{"k": k, "lo": r["lo"], "hi": r["hi"]} for k, r in rolls.items()],
            "tiered": any(len(set(v)) > 1 for c in chips for v in c["variants"]),
        })

    order = {c[0]: i for i, c in enumerate(CATS)}
    out.sort(key=lambda x: (order.get(x["cat"], 9), x["tier"], x["name"]))
    cats = []
    for cid, cn, enn, color, intro in CATS:
        n = sum(1 for x in out if x["cat"] == cid)
        if n:
            cats.append({"id": cid, "name": cn, "en": enn, "color": color,
                         "intro": intro, "count": n})

    json.dump({"categories": cats, "tools": out},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("tools:", len(out))
    for x in out:
        print("  ", x["cat"], x["tier"], x["name"], "| chips:", [(c["k"], c["fmt"]) for c in x["chips"]][:5],
              "| roll:", x["has_roll"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
