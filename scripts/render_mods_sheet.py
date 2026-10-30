# -*- coding: utf-8 -*-
"""Render the parsed mod model into a single self-contained Chinese HTML sheet,
each mod card with its own quality (1-6) slider."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\mods_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4模组速查表.html"
ARMOR_PAGE = "七日杀V3.4装甲速查表.html"
PERK_PAGE = "七日杀V3.4天赋速查表.html"
WEAPON_PAGE = "七日杀V3.4武器速查表.html"
GAME_VERSION = "V 3.4.0 (b9)"
QS = [1, 2, 3, 4, 5, 6]

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

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(335px,1fr));gap:14px}
.mod{background:var(--panel);border:1px solid var(--line);border-radius:9px;overflow:hidden;
  display:flex;flex-direction:column;padding-bottom:12px}
.mhead{display:flex;align-items:center;gap:9px;padding:12px 15px 6px;flex-wrap:wrap}
.mhead h3{margin:0;font-size:16px;color:#f3eadc}
.mhead h3 em{font-style:normal;font-weight:400;font-size:11px;color:#7d7367;
  letter-spacing:.3px;margin-left:7px}
.badge{font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:10px;color:#141210}
.badge.gun{background:#e0574c}.badge.melee{background:#e2b03c}.badge.bow{background:#57b95f}
.badge.armor{background:#49b6e8}.badge.vehicle{background:#a06fd0}.badge.drone{background:#8fa3ad}
.badge.dye{background:#c8762a}
.inst{display:flex;flex-wrap:wrap;gap:5px;padding:0 15px 9px;font-size:11px;color:#7d7367;align-items:center}
.inst span{background:#241e19;border:1px solid #3a3027;border-radius:4px;padding:0 6px;color:#c2b6a6}
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
.desc{margin:0;padding:6px 15px 0;font-size:11.5px;color:#8f857a;line-height:1.55;
  border-top:1px dashed #2c2520;margin-top:auto;padding-top:9px}
.appendix{margin-top:46px;padding-top:22px;border-top:2px solid var(--line)}
.appendix h2{font-size:18px;margin:0 0 8px}
.appendix p{color:var(--dim);font-size:13px;margin:0 0 8px}
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
  .mod{background:#fff;border-color:#ccc;break-inside:avoid}
  .mhead h3,.desc{color:#000}
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
    mulset: function(v){ return '×' + trim(v); }
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

  var mods = [].slice.call(document.querySelectorAll('.mod'));
  mods.forEach(function(card){
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
    mods.forEach(function(c){
      var okCat = (cat === 'all' || c.dataset.cat === cat);
      var okTxt = !v || c.dataset.text.indexOf(v) !== -1;
      c.classList.toggle('hide', !(okCat && okTxt));
    });
    secs.forEach(function(s){
      s.classList.toggle('hide', s.querySelectorAll('.mod:not(.hide)').length === 0);
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
    x = round(float(x), 1)
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
    return trim(v)


def spec_of(variants):
    return "|".join(",".join("%g" % float(v) for v in arr) for arr in variants)


def fmt_chip(chip, q=6):
    return " / ".join(fmt_one(arr[q - 1], chip["fmt"]) for arr in chip["variants"])


def build():
    with open(JSON_IN, encoding="utf-8") as f:
        m = json.load(f)
    cats = m["categories"]
    mods = m["mods"]
    q = 6

    out = []
    w = out.append
    w("<!DOCTYPE html>")
    w('<html lang="zh-CN"><head><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w("<title>七日杀 V3.4 模组速查表</title>")
    w("<style>" + CSS + "</style>")
    w("</head><body><div class='wrap'>")

    w("<header class='top'>")
    w("<h1>七日杀 · 模组速查表<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>Data/Config/item_modifiers.xml</code> 与 "
      "<code>Localization.csv</code>（简体中文）"
      "<br>生成时间 %s ｜ %d 个模组 · %d 个分类（已排除开发/测试/任务物品）</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(mods), len(cats)))
    w("<div class='sub' style='margin-top:8px'>"
      "<span style='color:#e8a33d'>品质滑杆：</span>每个模组卡片都有自己的 1–6 品质滑杆，"
      "拖动即可切换该卡显示的数值；没有品质差异的模组会直接标“数值固定”。<br>"
      "<span style='color:#e8a33d'>怎么用：</span>按分类筛选，或搜索模组名、效果、可装部位（按 "
      "<code>/</code> 聚焦）。<br>"
      "<span style='color:#e8a33d'>配套页面：</span>"
      "<a href='%s'>天赋速查表</a> · <a href='%s'>装甲速查表</a> · "
      "<a href='%s'>武器速查表</a></div>" % (e(PERK_PAGE), e(ARMOR_PAGE), e(WEAPON_PAGE)))
    w("</header>")

    w("<div class='rules'>")
    w("<div class='rule'><b>模组也有品质</b>"
      "<span>同一模组 1–6 级数值不同，装到装备上后按<em>模组自身品质</em>生效；"
      "滑杆展示的正是这 6 档。</span></div>")
    w("<div class='rule'><b>槽位有限</b>"
      "<span>每件装备能装的模组数量看它自己的槽位：护甲 2–5 个（粗糙套只有 1–2），"
      "武器/载具/无人机各有固定上限。</span></div>")
    w("<div class='rule'><b>“可装于”的含义</b>"
      "<span>卡片上列出的是<em>接口类型</em>（如“中瞄具位”“头盔”），"
      "只有带对应接口的装备才装得上。</span></div>")
    w("</div>")

    # nav
    w("<nav class='jump'><div class='navrow'>")
    w("<button class='chipbtn on' data-cat='all'>全部<small>%d</small></button>" % len(mods))
    for c in cats:
        w("<button class='chipbtn' data-cat='%s'>%s<small>%d</small></button>"
          % (c["id"], e(c["name"]), c["count"]))
    w("<span class='spacer'></span>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索模组 / 效果 / 部位'></label>")
    w("</div></nav>")

    # sections
    for c in cats:
        members = [x for x in mods if x["cat"] == c["id"]]
        w("<section class='cat' id='%s'>" % c["id"])
        w("<div class='cat-head'><span class='bar' style='background:%s'></span>"
          "<h2>%s</h2><span class='en'>%s</span>"
          "<span class='cnt'>%d 个模组</span></div>"
          % (c["color"], e(c["name"]), e(c["en"]), len(members)))
        w("<p class='cat-intro'>%s</p>" % e(c["intro"]))
        w("<div class='grid'>")
        for mod in members:
            blob = " ".join([mod["name"], mod["name_en"], mod["desc"],
                             " ".join(mod["install"])] +
                            [ch["k"] for ch in mod["chips"]])
            w("<article class='mod' data-id='%s' data-cat='%s' data-text='%s'>"
              % (e(mod["id"]), c["id"], e(blob.lower())))
            w("<div class='mhead'><span class='badge %s'>%s</span>"
              "<h3>%s<em>%s</em></h3></div>"
              % (c["id"], e(c["name"]), e(mod["name"]), e(mod["name_en"])))
            w("<div class='inst'>可装于 %s</div>"
              % "".join("<span>%s</span>" % e(t) for t in mod["install"]))
            if mod["tiered"]:
                w("<div class='setq'><span class='qlbl'>品质</span>"
                  "<input class='qslider' type='range' min='1' max='6' step='1' value='6' "
                  "aria-label='%s 品质'>"
                  "<b class='qnow'>6</b></div>"
                  % e(mod["name"]))
            elif mod["chips"]:
                w("<div class='fixed'>数值固定，无品质差异</div>")
            elif c["id"] == "dye":
                w("<div class='fixed'>纯外观，无属性变化</div>")
            else:
                w("<div class='fixed'>无数值词条，效果见描述</div>")

            if mod["chips"]:
                w("<div class='chips'>%s</div>" % "".join(
                    "<i>%s <b data-vals='%s' data-fmt='%s'>%s</b></i>"
                    % (e(ch["k"]), e(spec_of(ch["variants"])), e(ch["fmt"]),
                       e(fmt_chip(ch, q)))
                    for ch in mod["chips"]))
            if mod["desc"]:
                w("<p class='desc'>%s</p>" % e(mod["desc"]).replace("\n", "<br>"))
            w("</article>")
        w("</div></section>")

    # appendix
    w("<div class='appendix'>")
    w("<h2>说明</h2>")
    w("<p>· 数值都来自游戏文件里的 <code>tier</code> 区间，按品质 1–6 展开；<code>base_set</code> / "
      "<code>perc_set</code> 这类“直接设定”的效果显示为 <code>= 数值</code>。</p>")
    w("<p>· 同一个模组出现两三个数值（如“-8% / -9%”）表示它有两个不同条件下的效果，"
      "游戏里会分别生效。</p>")
    w("<p>· 护甲套装与 4 件套奖励见 <a href='%s'>装甲速查表</a>；属性与天赋见 "
      "<a href='%s'>天赋速查表</a>。</p>" % (e(ARMOR_PAGE), e(PERK_PAGE)))
    w("</div>")

    w("<footer>数据来源：本机 <code>7 Days to Die</code> 安装目录下 "
      "<code>Data/Config/item_modifiers.xml</code> 与 <code>Localization.csv</code>。"
      "<br>已排除：%s（开发/测试/任务物品，共 %d 个）。游戏更新后重新运行 "
      "<code>parse_mods.py</code> 与 <code>render_mods_sheet.py</code> 即可刷新。"
      "</footer>" % (e("、".join(m.get("skipped", []))), len(m.get("skipped", [])))
      )
    w("</div><script>" + JS + "</script></body></html>")

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
