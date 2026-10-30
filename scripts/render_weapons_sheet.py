# -*- coding: utf-8 -*-
"""Render the parsed weapon model into a single self-contained Chinese HTML sheet."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\weapons_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4武器速查表.html"
PERK_PAGE = "七日杀V3.4天赋速查表.html"
ARMOR_PAGE = "七日杀V3.4装甲速查表.html"
MOD_PAGE = "七日杀V3.4模组速查表.html"
GAME_VERSION = "V 3.4.0 (b9)"

CSS = """
:root{
  --bg:#100e0c; --panel:#1a1714; --panel2:#221d19; --line:#332b24;
  --text:#e8e1d8; --dim:#a2988c; --accent:#e8a33d; --accent2:#c8762a;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.65 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif;}
a{color:var(--accent);text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}
header.top{padding:34px 0 18px;border-bottom:1px solid var(--line)}
h1{margin:0 0 6px;font-size:27px;letter-spacing:.5px}
h1 .ver{font-size:14px;color:var(--accent);border:1px solid var(--accent2);
  border-radius:4px;padding:2px 7px;margin-left:10px;vertical-align:middle}
.sub{color:var(--dim);font-size:13px}
.sub code{background:#251f1a;padding:1px 5px;border-radius:3px;color:#d8c9b6}
.rules{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:22px 0 4px}
.rule{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:6px;padding:12px 14px}
.rule b{display:block;color:var(--accent);font-size:13px;letter-spacing:.5px;margin-bottom:4px}
.rule span{color:var(--dim);font-size:13px}
.rule span em{color:var(--text);font-style:normal}

nav.jump{position:sticky;top:0;z-index:20;background:rgba(16,14,12,.97);
  border-bottom:1px solid var(--line);padding:10px 0;margin:26px 0}
.navrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.navrow .spacer{flex:1}
.chipbtn{font-size:13px;padding:5px 12px;border:1px solid var(--line);border-radius:20px;
  color:var(--text);background:var(--panel);cursor:pointer;font-family:inherit}
.chipbtn:hover{border-color:var(--accent);color:var(--accent)}
.chipbtn.on{background:var(--accent);color:#1a1208;border-color:var(--accent);font-weight:700}
.chipbtn small{opacity:.65;margin-left:4px;font-size:11px}
.search{display:flex;align-items:center;gap:6px;background:var(--panel);
  border:1px solid var(--line);border-radius:20px;padding:4px 12px}
.search input{background:transparent;border:0;outline:0;color:var(--text);
  font-size:13px;width:190px;font-family:inherit}
.search input::placeholder{color:#6f665c}

section.cat{margin:0 0 42px;scroll-margin-top:84px}
.cat-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
  padding:0 0 10px;border-bottom:2px solid var(--line);margin-bottom:8px}
.cat-head .bar{width:6px;height:26px;border-radius:3px;display:inline-block}
.cat-head h2{margin:0;font-size:21px}
.cat-head .en{color:var(--dim);font-size:13px;letter-spacing:1px}
.cat-head .cnt{margin-left:auto;color:var(--dim);font-size:12px}
.cat-intro{color:#c4b8a9;font-size:13.5px;margin:0 0 18px;max-width:920px}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}
.wpn{background:var(--panel);border:1px solid var(--line);border-radius:9px;overflow:hidden;
  display:flex;flex-direction:column;padding-bottom:12px}
.whead{display:flex;align-items:center;gap:8px;padding:12px 15px 6px;flex-wrap:wrap}
.whead h3{margin:0;font-size:16px;color:#f3eadc}
.whead h3 em{font-style:normal;font-weight:400;font-size:11px;color:#7d7367;
  letter-spacing:.3px;margin-left:7px}
.badge{font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:10px;color:#141210}
.badge.handgun{background:#e0574c}.badge.shotgun{background:#e08a3c}.badge.rifle{background:#e2b03c}
.badge.mg{background:#c8762a}.badge.bow{background:#57b95f}.badge.explosive{background:#a06fd0}
.badge.blade{background:#49b6e8}.badge.club{background:#8fa3ad}.badge.sledge{background:#ef8377}
.badge.spear{background:#6ec6ef}.badge.knuckles{background:#c58ae0}.badge.baton{background:#7fd487}
.badge.misc{background:#9a8f80}
.tier{font-size:10.5px;font-weight:700;color:#d9b477;border:1px solid #4a3a24;
  border-radius:4px;padding:1px 6px}
.ammo{padding:0 15px 6px;font-size:11px;color:#7d7367;line-height:1.5}
.ammo b{color:#b9ab97;font-weight:600}
.setq{display:flex;align-items:center;gap:9px;padding:0 15px 9px}
.setq .qlbl{font-size:11px;color:#8b8175;letter-spacing:.5px;white-space:nowrap}
.setq input[type=range]{-webkit-appearance:none;appearance:none;width:150px;height:5px;
  border-radius:3px;background:linear-gradient(90deg,#4a3c2b,#c8762a,#e8a33d);outline:0}
.setq input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;
  border-radius:50%;background:#f3eadc;border:3px solid var(--accent);cursor:pointer;
  box-shadow:0 0 5px rgba(232,163,61,.55)}
.setq input[type=range]::-moz-range-thumb{width:12px;height:12px;border-radius:50%;
  background:#f3eadc;border:3px solid var(--accent);cursor:pointer}
.setq .qnow{font-size:12.5px;color:var(--accent);font-weight:700;min-width:12px}
.fixed{padding:0 15px 9px;font-size:11px;color:#6f665c}
.chips{display:flex;flex-wrap:wrap;gap:5px;padding:0 15px 8px}
.chips i{font-style:normal;font-size:11px;color:#d9b477;background:#2a2118;
  border:1px solid #4a3a24;border-radius:4px;padding:1px 6px;white-space:nowrap}
.chips i b{font-weight:700;color:#f0c98a}
.chips i.core{color:#e8d1a5;border-color:#6b5334;background:#302518}
details.more{padding:0 15px 6px}
details.more summary{cursor:pointer;font-size:11px;color:#8b8175;outline:0;padding:2px 0 4px}
details.more summary::marker{color:var(--accent2)}
details.more .chips{padding:2px 0 4px}
.desc{margin:8px 15px 0;padding-top:8px;font-size:11.5px;color:#8f857a;line-height:1.55;
  border-top:1px dashed #2c2520}
footer{margin-top:36px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
.hide{display:none !important}
@media (max-width:620px){
  .grid{grid-template-columns:1fr}
  .search input{width:100px}
  h1{font-size:22px}
  .setq input[type=range]{width:110px}
}
@media print{
  body{background:#fff;color:#000}
  nav.jump,.setq{display:none}
  .wpn{background:#fff;border-color:#ccc;break-inside:avoid}
  .whead h3,.desc{color:#000}
}
"""

JS = r"""
(function(){
  function trim(x){
    var r = Math.round(x * 10) / 10;
    if (Math.abs(r - Math.round(r)) < 0.0001) return String(Math.round(r));
    return String(r);
  }
  var FMT = {
    num:    function(v){ return trim(v); },
    pct:    function(v){ var x = Math.round(v * 1000) / 10; return (x > 0 ? '+' : '') + trim(x) + '%'; },
    raw:    function(v){ return (v > 0 ? '+' : '') + trim(v); },
    mult:   function(v){ return '×' + trim(1 + v); },
    pctset: function(v){ return '= ' + trim(Math.round(v * 1000) / 10) + '%'; },
    rawset: function(v){ return '= ' + trim(v); },
    mulset: function(v){ return '×' + trim(v); },
    pctabs: function(v){ return '= ' + trim(v) + '%'; }
  };
  function renderChip(el, q){
    var groups = el.getAttribute('data-vals').split('|');
    var f = FMT[el.getAttribute('data-fmt')] || FMT.num;
    var parts = [];
    for (var i = 0; i < groups.length; i++){
      var arr = groups[i].split(',');
      parts.push(f(parseFloat(arr[q - 1])));
    }
    el.textContent = parts.join(' / ');
  }
  function applyTo(root, q){
    q = Math.max(1, Math.min(6, q));
    var nodes = root.querySelectorAll('[data-vals]');
    for (var i = 0; i < nodes.length; i++) renderChip(nodes[i], q);
  }
  var cards = [].slice.call(document.querySelectorAll('.wpn'));
  cards.forEach(function(card){
    var slider = card.querySelector('.qslider');
    if (!slider) return;
    var qnow = card.querySelector('.setq .qnow');
    function sync(){
      var q = parseInt(slider.value, 10);
      if (qnow) qnow.textContent = q;
      applyTo(card, q);
    }
    slider.addEventListener('input', sync);
    slider.addEventListener('change', sync);
    sync();
  });

  var btns = [].slice.call(document.querySelectorAll('.chipbtn[data-cat]'));
  var secs = [].slice.call(document.querySelectorAll('section.cat'));
  var q = document.getElementById('q');
  var cat = 'all';
  function filter(){
    var v = (q.value || '').trim().toLowerCase();
    cards.forEach(function(c){
      var okCat = (cat === 'all' || c.dataset.cat === cat);
      var okTxt = !v || c.dataset.text.indexOf(v) !== -1;
      c.classList.toggle('hide', !(okCat && okTxt));
    });
    secs.forEach(function(s){
      s.classList.toggle('hide', s.querySelectorAll('.wpn:not(.hide)').length === 0);
    });
  }
  btns.forEach(function(b){
    b.addEventListener('click', function(){
      cat = b.dataset.cat;
      btns.forEach(function(x){ x.classList.toggle('on', x === b); });
      filter();
    });
  });
  q.addEventListener('input', filter);
  document.addEventListener('keydown', function(ev){
    var tag = (document.activeElement && document.activeElement.type) || '';
    if (ev.key === '/' && document.activeElement !== q && tag !== 'range'){
      ev.preventDefault(); q.focus();
    }
    if (ev.key === 'Escape' && document.activeElement === q){ q.value=''; filter(); q.blur(); }
  });
})();
"""


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def trim(x):
    import math
    x = math.floor(float(x) * 10 + 0.5) / 10
    if abs(x - round(x)) < 0.0001:
        return str(int(round(x)))
    return ("%.1f" % x).rstrip("0").rstrip(".")


def fmt_one(v, fmt):
    v = float(v)
    if fmt == "pct":
        x = round(v * 100, 1)
        return ("+" if x > 0 else "") + trim(x) + "%"
    if fmt == "raw":
        return ("+" if v > 0 else "") + trim(v)
    if fmt == "mult":
        return "×" + trim(1 + v)
    if fmt == "pctset":
        return "= " + trim(round(v * 100, 1)) + "%"
    if fmt == "rawset":
        return "= " + trim(v)
    if fmt == "mulset":
        return "×" + trim(v)
    if fmt == "pctabs":
        return "= " + trim(round(v, 1)) + "%"
    return trim(v)


def spec_of(variants):
    return "|".join(",".join("%g" % float(v) for v in arr) for arr in variants)


def fmt_chip(chip, q=6):
    return " / ".join(fmt_one(arr[q - 1], chip["fmt"]) for arr in chip["variants"])


def chip_html(chip, core, q=6):
    return ("<i class='%s'>%s <b data-vals='%s' data-fmt='%s'>%s</b></i>"
            % ("core" if core else "", e(chip["k"]), e(spec_of(chip["variants"])),
               e(chip["fmt"]), e(fmt_chip(chip, q))))


def build():
    with open(JSON_IN, encoding="utf-8") as f:
        m = json.load(f)
    cats = m["categories"]
    weapons = m["weapons"]
    q = 6

    out = []
    w = out.append
    w("<!DOCTYPE html>")
    w('<html lang="zh-CN"><head><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w("<title>七日杀 V3.4 武器速查表</title>")
    w("<style>" + CSS + "</style>")
    w("</head><body><div class='wrap'>")

    w("<header class='top'>")
    w("<h1>七日杀 · 武器速查表<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>Data/Config/items.xml</code> 与 "
      "<code>Localization.csv</code>（简体中文）"
      "<br>生成时间 %s ｜ %d 把武器 · %d 个分类（已排除零件/开发物品）</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(weapons), len(cats)))
    w("<div class='sub' style='margin-top:8px'>"
      "<span style='color:#e8a33d'>品质滑杆：</span>每把武器卡片有自己的 1–6 品质滑杆，"
      "拖动即可切换该卡显示的数值。<br>"
      "<span style='color:#e8a33d'>更多数值：</span>核心数值直接显示，散布、后坐力、穿透等"
      "折叠在「更多数值」里。<br>"
      "<span style='color:#e8a33d'>配套页面：</span>"
      "<a href='%s'>天赋速查表</a> · <a href='%s'>装甲速查表</a> · <a href='%s'>模组速查表</a></div>"
      % (e(PERK_PAGE), e(ARMOR_PAGE), e(MOD_PAGE)))
    w("</header>")

    w("<div class='rules'>")
    w("<div class='rule'><b>伤害怎么算</b>"
      "<span>近战 = 武器基础值 × 品质加成；枪械 = <em>默认弹药基础伤害 + 枪械修正</em>，"
      "再乘品质加成。所以同一把枪换穿甲弹，伤害会变。</span></div>")
    w("<div class='rule'><b>品质 1→6</b>"
      "<span>大多数武器<em>从品质 2 起</em>才有伤害加成（1 级是白板），耐久和模组槽也会随品质涨。</span></div>")
    w("<div class='rule'><b>霰弹枪标“伤害/弹丸”</b>"
      "<span>一发打出多颗弹丸，卡片上的伤害是<em>单颗</em>的；实际总伤害要乘弹丸数。</span></div>")
    w("</div>")

    # nav
    w("<nav class='jump'><div class='navrow'>")
    w("<button class='chipbtn on' data-cat='all'>全部<small>%d</small></button>" % len(weapons))
    for c in cats:
        w("<button class='chipbtn' data-cat='%s'>%s<small>%d</small></button>"
          % (c["id"], e(c["name"]), c["count"]))
    w("<span class='spacer'></span>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索武器 / 种类'></label>")
    w("</div></nav>")

    for c in cats:
        members = [x for x in weapons if x["cat"] == c["id"]]
        w("<section class='cat' id='%s'>" % c["id"])
        w("<div class='cat-head'><span class='bar' style='background:%s'></span>"
          "<h2>%s</h2><span class='en'>%s</span>"
          "<span class='cnt'>%d 把</span></div>"
          % (c["color"], e(c["name"]), e(c["en"]), len(members)))
        w("<p class='cat-intro'>%s</p>" % e(c["intro"]))
        w("<div class='grid'>")
        for wp in members:
            blob = " ".join([wp["name"], wp["name_en"], wp["desc"], c["name"]] +
                            [ch["k"] for ch in wp["chips"]])
            w("<article class='wpn' data-id='%s' data-cat='%s' data-text='%s'>"
              % (e(wp["id"]), c["id"], e(blob.lower())))
            w("<div class='whead'><span class='badge %s'>%s</span>%s"
              "<h3>%s<em>%s</em></h3></div>"
              % (c["id"], e(c["name"]),
                 ("<span class='tier'>%s</span>" % e(wp["tier"])) if wp["tier"] else "",
                 e(wp["name"]), e(wp["name_en"])))

            if wp["ammo"]:
                ammo_line = " · ".join(wp["ammo"])
                extra = ""
                if wp["pellets"] > 1:
                    extra = " ｜ 每发 %d 颗弹丸" % wp["pellets"]
                w("<div class='ammo'><b>弹药</b> %s%s</div>" % (e(ammo_line), e(extra)))

            if wp["tiered"]:
                w("<div class='setq'><span class='qlbl'>品质</span>"
                  "<input class='qslider' type='range' min='1' max='6' step='1' value='6' "
                  "aria-label='%s 品质'><b class='qnow'>6</b></div>" % e(wp["name"]))
            elif wp["chips"]:
                w("<div class='fixed'>数值固定，无品质差异</div>")
            else:
                w("<div class='fixed'>爆炸伤害由爆炸计算，无面板数值</div>")

            core = [ch for ch in wp["chips"] if ch["primary"]]
            other = [ch for ch in wp["chips"] if not ch["primary"]]
            if core:
                w("<div class='chips'>%s</div>" % "".join(chip_html(ch, True, q) for ch in core))
            if other:
                w("<details class='more'><summary>更多数值（%d）</summary>"
                  "<div class='chips'>%s</div></details>"
                  % (len(other), "".join(chip_html(ch, False, q) for ch in other)))
            if wp["desc"]:
                w("<p class='desc'>%s</p>" % e(wp["desc"]).replace("\n", "<br>"))
            w("</article>")
        w("</div></section>")

    w("<footer>数据来源：本机 <code>7 Days to Die</code> 安装目录下 "
      "<code>Data/Config/items.xml</code> 与 <code>Localization.csv</code>。"
      "<br>伤害按文件里的 <code>base_set/base_add</code> 叠加、再乘 <code>perc_add</code> 品质加成计算，"
      "与游戏内默认弹种口径一致；投掷物（手雷、炸药等）的伤害在爆炸逻辑里，不在面板上。"
      "游戏更新后重新运行 <code>parse_weapons.py</code> 与 <code>render_weapons_sheet.py</code> 即可刷新。</footer>")

    w("</div><script>" + JS + "</script></body></html>")

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
