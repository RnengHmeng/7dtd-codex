# -*- coding: utf-8 -*-
"""Build the static site into ./site from the JSON snapshots in ./data.

Usage:
    python scripts/build_site.py                 # render all pages + index + images
    python scripts/build_site.py --url https://xxx.pages.dev   # absolute og:image
"""
import argparse
import html
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "site"
SCRIPTS = ROOT / "scripts"

GAME_VERSION = "V 3.4.0 (b9)"

# old (Chinese) file name -> new (ASCII) file name
LINK_MAP = {
    "七日杀V3.4天赋速查表.html": "perks.html",
    "七日杀V3.4装甲速查表.html": "armor.html",
    "七日杀V3.4模组速查表.html": "mods.html",
    "七日杀V3.4武器速查表.html": "weapons.html",
}

FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def postprocess(path, spec, base_url):
    s = path.read_text(encoding="utf-8")
    for old, new in LINK_MAP.items():
        s = s.replace(old, new)
    og_image = (base_url.rstrip("/") + "/og.png") if base_url else "og.png"
    meta = (
        '\n<meta name="description" content="%s">'
        '\n<link rel="icon" href="favicon.png">'
        '\n<meta property="og:type" content="website">'
        '\n<meta property="og:title" content="%s">'
        '\n<meta property="og:description" content="%s">'
        '\n<meta property="og:image" content="%s">'
        '\n<meta name="twitter:card" content="summary_large_image">'
        % (html.escape(spec["desc"], quote=True), html.escape(spec["title"], quote=True),
           html.escape(spec["desc"], quote=True), html.escape(og_image, quote=True))
    )
    if "</head>" in s:
        s = s.replace("</head>", meta + "\n</head>", 1)
    path.write_text(s, encoding="utf-8")


def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def make_og(out_path):
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#100e0c")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill="#e8a33d")
    d.text((70, 96), "七日杀 · 数据速查", font=font(76, True), fill="#f3eadc")
    d.text((74, 200), "%s · 天赋 / 装甲 / 武器 / 模组" % GAME_VERSION,
           font=font(34), fill="#a2988c")

    chips = [("天赋", "#49b6e8"), ("装甲", "#57b95f"), ("武器", "#e0574c"), ("模组", "#e2b03c")]
    x = 74
    for label, color in chips:
        tw = d.textlength(label, font=font(32, True))
        d.rounded_rectangle([x, 300, x + tw + 56, 372], radius=36, fill="#221d19",
                            outline=color, width=3)
        d.text((x + 28, 318), label, font=font(32, True), fill=color)
        x += tw + 84

    d.text((74, 430), "每级数值 · 品质滑杆 · 套装奖励 · 模组效果",
           font=font(30), fill="#c4b8a9")
    d.text((74, 540), "非官方粉丝资料 · 数据取自游戏文件 · The Fun Pimps 版权所有",
           font=font(22), fill="#6f665c")
    im.save(out_path)


def make_favicon(out_path):
    size = 128
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, size - 4, size - 4], radius=26, fill="#e8a33d")
    d.text((30, 26), "7D", font=font(64, True), fill="#1a1208")
    im.save(out_path)


def index_html(cards, base_url):
    og = (base_url.rstrip("/") + "/og.png") if base_url else "og.png"
    cells = []
    for c in cards:
        cells.append(
            "<a class='card' href='%s'><span class='dot' style='background:%s'></span>"
            "<b>%s</b><small>%s</small><span class='meta'>%s</span>"
            "<span class='go'>查看 →</span></a>"
            % (c["href"], c["color"], html.escape(c["name"]), html.escape(c["en"]),
               html.escape(c["meta"])))
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>七日杀 %s 数据速查</title>
<meta name="description" content="七日杀 V3.4 天赋、装甲、武器、模组速查表：逐级数值、品质滑杆、套装奖励。">
<link rel="icon" href="favicon.png">
<meta property="og:type" content="website">
<meta property="og:title" content="七日杀 %s 数据速查">
<meta property="og:description" content="天赋 / 装甲 / 武器 / 模组，逐级数值与品质滑杆。">
<meta property="og:image" content="%s">
<meta name="twitter:card" content="summary_large_image">
<style>
:root{--bg:#100e0c;--panel:#1a1714;--line:#332b24;--text:#e8e1d8;--dim:#a2988c;--accent:#e8a33d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.7 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif}
a{text-decoration:none;color:inherit}
.wrap{max-width:960px;margin:0 auto;padding:64px 22px 80px}
h1{font-size:38px;margin:0 0 8px;letter-spacing:.5px}
h1 span{color:var(--accent)}
.sub{color:var(--dim);font-size:14px;margin-bottom:6px}
.sub code{background:#251f1a;padding:1px 6px;border-radius:4px;color:#d8c9b6}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin:32px 0}
.card{position:relative;display:block;background:var(--panel);border:1px solid var(--line);
  border-radius:12px;padding:20px 20px 18px;transition:.15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card b{display:block;font-size:20px;color:#f3eadc;margin-bottom:2px}
.card small{display:block;color:#7d7367;font-size:12px;letter-spacing:.6px}
.card .meta{display:block;margin-top:12px;color:#c4b8a9;font-size:13px}
.card .go{position:absolute;right:18px;bottom:16px;font-size:12px;color:var(--accent)}
.dot{position:absolute;left:20px;top:-5px;width:34px;height:5px;border-radius:3px}
footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
</style></head><body><div class="wrap">
<h1>七日杀 <span>数据速查</span></h1>
<div class="sub">%s ｜ 全部数值取自游戏文件，可切换品质 1–6 查看每级变化</div>
<div class="grid">%s</div>
<footer>非官方粉丝资料，与 The Fun Pimps 无关；游戏内文本与数值版权归原公司所有。<br>
生成时间 %s ｜ 数据来源：本机 <code>Data/Config</code> 下的 progression / items / buffs / item_modifiers 与 Localization.csv</footer>
</div></body></html>""" % (
        html.escape(GAME_VERSION), html.escape(GAME_VERSION), html.escape(og),
        html.escape(GAME_VERSION), "".join(cells),
        datetime.now().strftime("%Y-%m-%d %H:%M"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("SITE_URL", ""),
                    help="站点根地址，用于 og:image 绝对路径，例如 https://xxx.pages.dev")
    args = ap.parse_args()

    SITE.mkdir(parents=True, exist_ok=True)

    perks = json.loads((DATA / "perks_v34.json").read_text(encoding="utf-8"))
    armor = json.loads((DATA / "armor_v34.json").read_text(encoding="utf-8"))
    mods = json.loads((DATA / "mods_v34.json").read_text(encoding="utf-8"))
    weapons = json.loads((DATA / "weapons_v34.json").read_text(encoding="utf-8"))

    cards = [
        {"name": "天赋", "en": "Perks", "color": "#49b6e8", "href": "perks.html",
         "meta": "%d 个天赋 · %d 套书籍 %d 卷 · 带加点模拟" % (
             len(perks["perks"]), len(perks["book_groups"]),
             sum(len(b["volumes"]) for b in perks["book_groups"]))},
        {"name": "装甲", "en": "Armor", "color": "#57b95f", "href": "armor.html",
         "meta": "%d 套 · %d 件 · 4 件套奖励" % (
             len(armor["sets"]),
             sum(len(s["pieces"]) for s in armor["sets"]) + len(armor["singles"]))},
        {"name": "武器", "en": "Weapons", "color": "#e0574c", "href": "weapons.html",
         "meta": "%d 把 · %d 个分类 · 品质 1–6" % (
             len(weapons["weapons"]), len(weapons["categories"]))},
        {"name": "模组", "en": "Mods", "color": "#e2b03c", "href": "mods.html",
         "meta": "%d 个模组 · %d 个分类" % (len(mods["mods"]), len(mods["categories"]))},
    ]

    specs = [
        {"script": "render_perk_sheet.py", "json": "perks_v34.json", "out": "perks.html",
         "title": "七日杀 V3.4 天赋速查表",
         "desc": "5 项属性、50 个属性天赋、7 个通用天赋、19 套书籍 133 卷；每级门槛、花费与完整中文效果，附加点模拟器。"},
        {"script": "render_armor_sheet.py", "json": "armor_v34.json", "out": "armor.html",
         "title": "七日杀 V3.4 装甲速查表",
         "desc": "轻甲 / 中甲 / 重甲共 16 套 64 件，逐件词条、4 件套奖励，每套独立品质滑杆。"},
        {"script": "render_weapons_sheet.py", "json": "weapons_v34.json", "out": "weapons.html",
         "title": "七日杀 V3.4 武器速查表",
         "desc": "51 把武器按 13 类整理，伤害、射速、弹匣、射程、耐久与隐藏数值，品质 1–6 逐级切换。"},
        {"script": "render_mods_sheet.py", "json": "mods_v34.json", "out": "mods.html",
         "title": "七日杀 V3.4 模组速查表",
         "desc": "97 个模组按安装接口分 7 类，含枪械、近战、护甲、载具、无人机与染料，品质 1–6 数值。"},
    ]

    for spec in specs:
        mod = load_module(SCRIPTS / spec["script"])
        mod.JSON_IN = str(DATA / spec["json"])
        mod.OUT_HTML = str(SITE / spec["out"])
        mod.build()
        postprocess(SITE / spec["out"], spec, args.url)
        print("  ->", spec["out"])

    (SITE / "index.html").write_text(index_html(cards, args.url), encoding="utf-8")
    if HAVE_PIL:
        make_og(SITE / "og.png")
        make_favicon(SITE / "favicon.png")
    else:
        print("  ! Pillow 未安装，跳过 og.png / favicon.png（已有文件会保留）")
        for name in ("og.png", "favicon.png"):
            if not (SITE / name).exists():
                print("  ! 缺少", name, "，请先 pip install pillow 后重新构建")
    print("wrote", SITE)
    for f in sorted(SITE.iterdir()):
        print("   %-14s %7.1f KB" % (f.name, f.stat().st_size / 1024))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
