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
import re
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

LINK_MAP = {
    "七日杀V3.4天赋速查表.html": "perks.html",
    "七日杀V3.4装甲速查表.html": "armor.html",
    "七日杀V3.4模组速查表.html": "mods.html",
    "七日杀V3.4武器速查表.html": "weapons.html",
    "七日杀V3.4丧尸图鉴.html": "zombies.html",
    "七日杀V3.4食物药品表.html": "food.html",
    "七日杀V3.4载具表.html": "vehicles.html",
}

NAV = [("index.html", "首页"), ("perks.html", "天赋"), ("armor.html", "装甲"),
       ("weapons.html", "武器"), ("mods.html", "模组"), ("zombies.html", "丧尸"),
       ("food.html", "食物"), ("vehicles.html", "载具")]

NAV_CSS = """
.sitebar{position:relative;z-index:30;background:#14110e;border-bottom:1px solid #2a231d;
  font-size:12.5px}
.sitebar .in{max-width:1180px;margin:0 auto;padding:7px 20px;display:flex;gap:14px;
  align-items:center;flex-wrap:wrap}
.sitebar a{color:#a2988c;text-decoration:none;padding:2px 0}
.sitebar a:hover{color:#e8a33d}
.sitebar a.cur{color:#e8a33d;border-bottom:1px solid #e8a33d}
.sitebar .ss{margin-left:auto;color:#6f665c;font-size:11px}
#sbtn{position:fixed;right:18px;bottom:18px;z-index:60;width:44px;height:44px;border-radius:50%;
  border:1px solid #4a3c2b;background:#1e1a16;color:#e8a33d;font-size:18px;cursor:pointer;
  box-shadow:0 4px 14px rgba(0,0,0,.45)}
#sbox{position:fixed;inset:0;z-index:70;background:rgba(8,7,6,.72);display:flex;
  align-items:flex-start;justify-content:center;padding-top:12vh}
#sbox[hidden]{display:none}
.sbox-in{width:min(640px,92vw);background:#191512;border:1px solid #3a3027;border-radius:12px;
  overflow:hidden;box-shadow:0 18px 48px rgba(0,0,0,.6)}
#sinput{width:100%;box-sizing:border-box;background:#0f0d0b;border:0;border-bottom:1px solid #2c2520;
  color:#e8e1d8;font:15px/1.6 "Microsoft YaHei",system-ui,sans-serif;padding:14px 16px;outline:0}
#sres{max-height:52vh;overflow:auto;padding:6px}
#sres a{display:flex;gap:10px;align-items:baseline;padding:8px 10px;border-radius:7px;
  color:#ded3c4;text-decoration:none;font-size:13.5px}
#sres a:hover{background:#241f1a}
#sres small{color:#7d7367;font-size:11px}
#sres .empty{color:#6f665c;font-size:13px;padding:14px}
"""

SEARCH_JS = r"""
(function(){
  var idx = window.SEARCH_INDEX || [];
  var box = document.getElementById('sbox');
  var input = document.getElementById('sinput');
  var res = document.getElementById('sres');
  if (!box || !input || !res) return;

  function norm(s){
    return String(s).toLowerCase().replace(/[\s\-_·:：,，.。/]/g, '');
  }

  function render(q){
    q = norm(q || '');
    var pool = q ? idx.filter(function(x){
      return norm(x.n + ' ' + x.e + ' ' + (x.k || '') + ' ' + x.t).indexOf(q) !== -1;
    }) : idx.slice(0, 24);
    var list = pool.slice(0, 60);
    res.innerHTML = list.length ? list.map(function(x){
      return '<a href="' + x.u + '"><b>' + x.n + '</b><small>' + x.t + '</small></a>';
    }).join('') : '<p class="empty">没有匹配的条目</p>';
  }
  function open(){ box.hidden = false; input.value = ''; render(''); input.focus(); }
  function close(){ box.hidden = true; }

  var btn = document.getElementById('sbtn');
  if (btn) btn.addEventListener('click', open);
  input.addEventListener('input', function(){ render(input.value); });
  box.addEventListener('click', function(e){ if (e.target === box) close(); });
  document.addEventListener('keydown', function(e){
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')){ e.preventDefault(); open(); }
    if (e.key === 'Escape') close();
  });
})();
"""


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def nav_html(current):
    links = []
    for href, label in NAV:
        cls = " class='cur'" if href == current else ""
        links.append("<a href='%s'%s>%s</a>" % (href, cls, label))
    return ("<div class='sitebar'><div class='in'>%s"
            "<span class='ss'>V 3.4 · 数据来自游戏文件</span></div></div>"
            "<button id='sbtn' title='搜索（Ctrl+K）'>🔍</button>"
            "<div id='sbox' hidden><div class='sbox-in'>"
            "<input id='sinput' placeholder='搜索天赋 / 装甲 / 武器 / 模组 / 丧尸 / 食物…'>"
            "<div id='sres'></div></div></div>" % "".join(links))


def inject_common(path, current, base_url, title, desc):
    s = path.read_text(encoding="utf-8")
    for old, new in LINK_MAP.items():
        s = s.replace(old, new)
    s = re.sub(r"<(div|article) class='(perk|wpn|mod)' data-id='([^']+)'",
               r"<\1 class='\2' id='\3' data-id='\3'", s)
    og = (base_url.rstrip("/") + "/og.png") if base_url else "og.png"
    meta = (
        '\n<meta name="description" content="%s">'
        '\n<link rel="icon" href="favicon.png">'
        '\n<link rel="stylesheet" href="search.css">'
        '\n<meta property="og:type" content="website">'
        '\n<meta property="og:title" content="%s">'
        '\n<meta property="og:description" content="%s">'
        '\n<meta property="og:image" content="%s">'
        '\n<meta name="twitter:card" content="summary_large_image">'
        % (html.escape(desc, quote=True), html.escape(title, quote=True),
           html.escape(desc, quote=True), html.escape(og, quote=True))
    )
    s = s.replace("</head>", meta + "\n</head>", 1)
    s = s.replace("<body>", "<body>\n" + nav_html(current), 1)
    s = s.replace("</body>",
                  "<script src='search-index.js'></script><script src='search.js' defer></script>\n</body>",
                  1)
    path.write_text(s, encoding="utf-8")


def font(size, bold=False):
    path = r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"
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
    d.text((74, 200), "%s · 天赋 / 装甲 / 武器 / 模组 / 丧尸" % GAME_VERSION,
           font=font(32), fill="#a2988c")
    chips = [("天赋", "#49b6e8"), ("装甲", "#57b95f"), ("武器", "#e0574c"),
             ("模组", "#e2b03c"), ("丧尸", "#ef8377"), ("食物", "#7fd487")]
    x = 74
    for label, color in chips:
        tw = d.textlength(label, font=font(30, True))
        d.rounded_rectangle([x, 300, x + tw + 50, 368], radius=34, fill="#221d19",
                            outline=color, width=3)
        d.text((x + 25, 316), label, font=font(30, True), fill=color)
        x += tw + 74
    d.text((74, 430), "每级数值 · 品质滑杆 · 套装奖励 · 模组效果 · 丧尸血量",
           font=font(28), fill="#c4b8a9")
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


def search_entries():
    j = lambda n: json.loads((DATA / n).read_text(encoding="utf-8"))
    perks, armor = j("perks_v34.json"), j("armor_v34.json")
    mods, weapons = j("mods_v34.json"), j("weapons_v34.json")
    zombies, food = j("zombies_v34.json"), j("consumables_v34.json")
    vehicles = j("vehicles_v34.json")

    out = []
    for p in perks["perks"]:
        out.append({"n": p["name"], "e": p["name_en"], "k": p["id"], "t": "天赋",
                    "u": "perks.html#" + p["id"]})
    for b in perks["book_groups"]:
        out.append({"n": b["name"], "e": b["name_en"], "k": b["id"], "t": "书籍",
                    "u": "perks.html#books"})
    for s in armor["sets"]:
        out.append({"n": s["name"], "e": s["name_en"], "k": s["id"], "t": "装甲", "u": "armor.html#" + s["id"]})
    for w in weapons["weapons"]:
        out.append({"n": w["name"], "e": w["name_en"], "k": w["id"], "t": "武器",
                    "u": "weapons.html#" + w["id"]})
    for m in mods["mods"]:
        out.append({"n": m["name"], "e": m["name_en"], "k": m["id"], "t": "模组", "u": "mods.html#" + m["id"]})
    for z in zombies["families"]:
        out.append({"n": z["name"], "e": z["name_en"], "k": z["id"], "t": "丧尸", "u": "zombies.html#" + z["id"]})
    for c in food["items"]:
        out.append({"n": c["name"], "e": c["name_en"], "k": c["id"], "t": "食物/药品", "u": "food.html#" + c["id"]})
    for v in vehicles["vehicles"]:
        out.append({"n": v["name"], "e": v["name_en"], "k": v["id"], "t": "载具", "u": "vehicles.html#" + v["id"]})
    return out


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
<link rel="stylesheet" href="search.css">
<style>
:root{--bg:#100e0c;--panel:#1a1714;--line:#332b24;--text:#e8e1d8;--dim:#a2988c;--accent:#e8a33d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.7 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif}
a{text-decoration:none;color:inherit}
.wrap{max-width:960px;margin:0 auto;padding:48px 22px 80px}
h1{font-size:36px;margin:0 0 8px;letter-spacing:.5px}
h1 span{color:var(--accent)}
.sub{color:var(--dim);font-size:14px;margin-bottom:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px;margin:30px 0}
.card{position:relative;display:block;background:var(--panel);border:1px solid var(--line);
  border-radius:12px;padding:20px 20px 18px;transition:.15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card b{display:block;font-size:19px;color:#f3eadc;margin-bottom:2px}
.card small{display:block;color:#7d7367;font-size:12px;letter-spacing:.6px}
.card .meta{display:block;margin-top:12px;color:#c4b8a9;font-size:13px}
.card .go{position:absolute;right:18px;bottom:16px;font-size:12px;color:var(--accent)}
.dot{position:absolute;left:20px;top:-5px;width:34px;height:5px;border-radius:3px}
footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
</style></head><body>
<div class="wrap">
<h1>七日杀 <span>数据速查</span></h1>
<div class="sub">%s ｜ 全部数值取自游戏文件，可切换品质 1–6 查看每级变化</div>
<div class="grid">%s</div>
<footer>非官方粉丝资料，与 The Fun Pimps 无关；游戏内文本与数值版权归原公司所有。<br>
生成时间 %s ｜ 数据来源：本机 <code>Data/Config</code> 下的 progression / items / buffs / item_modifiers / entityclasses / vehicles 与 Localization.csv</footer>
</div></body></html>""" % (
        html.escape(GAME_VERSION), html.escape(GAME_VERSION),
        "".join(cells), datetime.now().strftime("%Y-%m-%d %H:%M"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("SITE_URL", ""),
                    help="站点根地址，用于 og:image 绝对路径")
    args = ap.parse_args()

    SITE.mkdir(parents=True, exist_ok=True)

    perks = json.loads((DATA / "perks_v34.json").read_text(encoding="utf-8"))
    armor = json.loads((DATA / "armor_v34.json").read_text(encoding="utf-8"))
    mods = json.loads((DATA / "mods_v34.json").read_text(encoding="utf-8"))
    weapons = json.loads((DATA / "weapons_v34.json").read_text(encoding="utf-8"))
    zombies = json.loads((DATA / "zombies_v34.json").read_text(encoding="utf-8"))
    food = json.loads((DATA / "consumables_v34.json").read_text(encoding="utf-8"))
    vehicles = json.loads((DATA / "vehicles_v34.json").read_text(encoding="utf-8"))

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
        {"name": "丧尸", "en": "Bestiary", "color": "#ef8377", "href": "zombies.html",
         "meta": "%d 个丧尸系 · %d 个动物系 · 血量/经验/速度" % (
             sum(1 for f in zombies["families"] if "动物" not in f["tags"]),
             sum(1 for f in zombies["families"] if "动物" in f["tags"]))},
        {"name": "食物", "en": "Consumables", "color": "#7fd487", "href": "food.html",
         "meta": "%d 种 · 食物/水/生命/治疗" % len(food["items"])},
        {"name": "载具", "en": "Vehicles", "color": "#c58ae0", "href": "vehicles.html",
         "meta": "%d 台 · 耐久/模组槽/极速" % len(vehicles["vehicles"])},
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
        {"script": "render_zombies_sheet.py", "json": "zombies_v34.json", "out": "zombies.html",
         "title": "七日杀 V3.4 丧尸图鉴",
         "desc": "74 个丧尸/动物系、163 个实体：血量、经验、速度与群系，普通/凶残/辐射变体对照。"},
        {"script": "render_food_sheet.py", "json": "consumables_v34.json", "out": "food.html",
         "title": "七日杀 V3.4 食物药品表",
         "desc": "66 种料理、生食、饮品与药品：食物、水、生命、治疗量对照表。"},
        {"script": "render_vehicles_sheet.py", "json": "vehicles_v34.json", "out": "vehicles.html",
         "title": "七日杀 V3.4 载具表",
         "desc": "5 台载具的耐久、模组槽、可装模组类型与相对极速。"},
    ]

    for spec in specs:
        mod = load_module(SCRIPTS / spec["script"])
        mod.JSON_IN = str(DATA / spec["json"])
        mod.OUT_HTML = str(SITE / spec["out"])
        mod.build()
        inject_common(SITE / spec["out"], spec["out"], args.url, spec["title"], spec["desc"])
        print("  ->", spec["out"])

    (SITE / "index.html").write_text(index_html(cards, args.url), encoding="utf-8")
    inject_common(SITE / "index.html", "index.html", args.url,
                  "七日杀 %s 数据速查" % GAME_VERSION,
                  "天赋 / 装甲 / 武器 / 模组 / 丧尸 / 食物 / 载具，逐级数值与品质滑杆。")

    entries = search_entries()
    (SITE / "search-index.js").write_text(
        "window.SEARCH_INDEX=" + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    (SITE / "search.css").write_text(NAV_CSS, encoding="utf-8")
    (SITE / "search.js").write_text(SEARCH_JS, encoding="utf-8")
    print("  search entries:", len(entries))

    if HAVE_PIL:
        make_og(SITE / "og.png")
        make_favicon(SITE / "favicon.png")
    else:
        print("  ! Pillow 未安装，跳过 og.png / favicon.png")

    print("wrote", SITE)
    for f in sorted(SITE.iterdir()):
        print("   %-16s %7.1f KB" % (f.name, f.stat().st_size / 1024))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
