# -*- coding: utf-8 -*-
"""Render the tools page."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\tools_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4工具速查表.html"
GAME_VERSION = "V 3.4.0 (b9)"

CSS = """
:root{--bg:#100e0c;--panel:#1a1714;--line:#332b24;--text:#e8e1d8;--dim:#a2988c;
  --accent:#e8a33d;--accent2:#c8762a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.65 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif}
a{color:var(--accent);text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}
header.top{padding:34px 0 18px;border-bottom:1px solid var(--line)}
h1{margin:0 0 6px;font-size:27px}
h1 .ver{font-size:14px;color:var(--accent);border:1px solid var(--accent2);
  border-radius:4px;padding:2px 7px;margin-left:10px;vertical-align:middle}
.sub{color:var(--dim);font-size:13px}
.sub code{background:#251f1a;padding:1px 5px;border-radius:3px;color:#d8c9b6}
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
section.cat{margin:0 0 38px}
.cat-head{display:flex;align-items:baseline;gap:12px;padding-bottom:10px;
  border-bottom:2px solid var(--line);margin-bottom:8px}
.cat-head .bar{width:6px;height:24px;border-radius:3px;display:inline-block}
.cat-head h2{margin:0;font-size:20px}
.cat-head .cnt{margin-left:auto;color:var(--dim);font-size:12px}
.cat-intro{color:#c4b8a9;font-size:13px;margin:0 0 16px;max-width:900px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(335px,1fr));gap:14px}
.tool{background:var(--panel);border:1px solid var(--line);border-radius:9px;
  display:flex;flex-direction:column;padding-bottom:12px}
.thead{display:flex;align-items:center;gap:8px;padding:12px 15px 6px;flex-wrap:wrap}
.thead h3{margin:0;font-size:16px;color:#f3eadc}
.thead h3 em{font-style:normal;font-weight:400;font-size:11px;color:#7d7367;margin-left:7px}
.badge{font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:10px;color:#141210}
.badge.axe{background:#e0574c}.badge.pick{background:#e2b03c}.badge.shovel{background:#8fa3ad}
.badge.electric{background:#49b6e8}.badge.salvage{background:#57b95f}.badge.repair{background:#c58ae0}
.tier{font-size:10.5px;font-weight:700;color:#d9b477;border:1px solid #4a3a24;
  border-radius:4px;padding:1px 6px}
.setq,.rrow{display:flex;align-items:center;gap:9px;padding:0 15px 9px}
.setq .qlbl,.rrow .qlbl{font-size:11px;color:#8b8175;letter-spacing:.5px;white-space:nowrap}
.setq input[type=range]{-webkit-appearance:none;appearance:none;width:150px;height:5px;
  border-radius:3px;background:linear-gradient(90deg,#4a3c2b,#c8762a,#e8a33d);outline:0}
.setq input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;
  border-radius:50%;background:#f3eadc;border:3px solid var(--accent);cursor:pointer}
.rrow input[type=range]{-webkit-appearance:none;appearance:none;width:150px;height:5px;
  border-radius:3px;background:linear-gradient(90deg,#4a2f24,#332b24,#4a2f24);outline:0}
.rrow input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;
  border-radius:50%;background:#f3eadc;border:2px solid #8fa3ad;cursor:pointer}
.setq .qnow{font-size:12.5px;color:var(--accent);font-weight:700;min-width:12px}
.rrow .rnow{font-size:12px;color:#8fa3ad;font-weight:700;min-width:44px}
.chips{display:flex;flex-wrap:wrap;gap:5px;padding:0 15px 8px}
.chips i{font-style:normal;font-size:11px;color:#d9b477;background:#2a2118;
  border:1px solid #4a3a24;border-radius:4px;padding:1px 6px;white-space:nowrap}
.chips i b{font-weight:700;color:#f0c98a}
.chips i.core{color:#e8d1a5;border-color:#6b5334;background:#302518}
details.more{padding:0 15px 6px}
details.more summary{cursor:pointer;font-size:11px;color:#8b8175;outline:0;padding:2px 0 4px}
details.more .chips{padding:2px 0 4px}
.desc{margin:8px 15px 0;padding-top:8px;font-size:11.5px;color:#8f857a;line-height:1.55;
  border-top:1px dashed #2c2520}
footer{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
.hide{display:none!important}
body.range .setq,body.range .rrow{display:none}
@media (max-width:620px){.grid{grid-template-columns:1fr}.search input{width:110px}}
@media print{body{background:#fff;color:#000}nav.jump,.setq,.rrow{display:none}
  .tool{background:#fff;border-color:#ccc;break-inside:avoid}.thead h3,.desc{color:#000}}
"""

JS = r"""
(function(){
  function trim(x){
    var r = Math.round(x * 10) / 10;
    if (Math.abs(r - Math.round(r)) < 0.0001) return String(Math.round(r));
    return String(r);
  }
  var FMT = {
    num: function(v){ return trim(v); },
    pct: function(v){ var x = Math.round(v * 1000) / 10; return (x > 0 ? '+' : '') + trim(x) + '%'; },
    raw: function(v){ return (v > 0 ? '+' : '') + trim(v); },
    mult: function(v){ return '×' + trim(1 + v); },
    x: function(v){ return '×' + (Math.round(v * 100) / 100); }
  };
  var mode = 'single';

  function renderChip(el, q, t){
    var groups = el.getAttribute('data-vals').split('|');
    var f = FMT[el.getAttribute('data-fmt')] || FMT.num;
    var roll = el.getAttribute('data-roll');
    var off = 0, rop = '';
    if (roll){
      var rp = roll.split(',');
      rop = rp[0];
      var lo = parseFloat(rp[1]), hi = parseFloat(rp[2]);
      off = lo + (hi - lo) * t;
    }
    if (mode === 'range'){
      var lo2 = Infinity, hi2 = -Infinity;
      for (var qq = 1; qq <= 6; qq++){
        for (var gi = 0; gi < groups.length; gi++){
          var base = parseFloat(groups[gi].split(',')[qq - 1]);
          var vals = [base];
          if (roll){
            var l = (rop === 'perc_add') ? base * (1 + parseFloat(rp[1])) : base + parseFloat(rp[1]);
            var h = (rop === 'perc_add') ? base * (1 + parseFloat(rp[2])) : base + parseFloat(rp[2]);
            vals.push(l, h);
          }
          lo2 = Math.min(lo2, Math.min.apply(null, vals));
          hi2 = Math.max(hi2, Math.max.apply(null, vals));
        }
      }
      el.textContent = (hi2 - lo2 < 1e-9) ? f(lo2) : (f(lo2) + ' ~ ' + f(hi2));
      return;
    }
    var parts = [];
    for (var i = 0; i < groups.length; i++){
      var v = parseFloat(groups[i].split(',')[q - 1]);
      if (roll) v = (rop === 'perc_add') ? v * (1 + off) : v + off;
      parts.push(f(v));
    }
    el.textContent = parts.join(' / ');
  }
  function applyTo(root, q, t){
    var nodes = root.querySelectorAll('[data-vals]');
    for (var i = 0; i < nodes.length; i++) renderChip(nodes[i], q, t);
  }
  var cards = [].slice.call(document.querySelectorAll('.tool'));
  var syncers = [];
  cards.forEach(function(card){
    var s = card.querySelector('.qslider');
    var rs = card.querySelector('.rslider');
    var qnow = card.querySelector('.setq .qnow');
    var rnow = card.querySelector('.rnow');
    if (!s) return;
    function sync(){
      var q = parseInt(s.value, 10);
      var t = rs ? parseInt(rs.value, 10) / 100 : 0.5;
      if (qnow) qnow.textContent = q;
      if (rnow && rs){
        var roll = card.querySelector('[data-roll]');
        var v = 0;
        if (roll){
          var rp = roll.getAttribute('data-roll').split(',');
          var lo = parseFloat(rp[1]), hi = parseFloat(rp[2]);
          v = lo + (hi - lo) * t;
        }
        rnow.textContent = Math.abs(t - 0.5) < 0.001 ? '基准'
          : (v > 0 ? '+' : '') + (Math.round(v * 1000) / 10) + '%';
      }
      applyTo(card, q, t);
    }
    s.addEventListener('input', sync); s.addEventListener('change', sync);
    if (rs){ rs.addEventListener('input', sync); rs.addEventListener('change', sync); }
    syncers.push(sync);
    sync();
  });

  var rt = document.getElementById('rangetoggle');
  if (rt) rt.addEventListener('click', function(){
    mode = (mode === 'single') ? 'range' : 'single';
    document.body.classList.toggle('range', mode === 'range');
    rt.textContent = (mode === 'range') ? '显示单值' : '显示区间';
    syncers.forEach(function(fn){ fn(); });
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
      s.classList.toggle('hide', s.querySelectorAll('.tool:not(.hide)').length === 0);
    });
  }
  btns.forEach(function(b){ b.addEventListener('click', function(){
    cat = b.dataset.cat;
    btns.forEach(function(x){ x.classList.toggle('on', x === b); });
    filter();
  }); });
  q.addEventListener('input', filter);
  document.addEventListener('keydown', function(e){
    if (e.key === '/' && document.activeElement !== q){ e.preventDefault(); q.focus(); }
    if (e.key === 'Escape' && document.activeElement === q){ q.value = ''; filter(); q.blur(); }
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


def trim2(x):
    x = round(float(x), 2)
    if abs(x - round(x)) < 0.0001:
        return str(int(round(x)))
    return ("%.2f" % x).rstrip("0").rstrip(".")


def fmt_one(v, fmt):
    v = float(v)
    if fmt == "pct":
        x = round(v * 100, 1)
        return ("+" if x > 0 else "") + trim(x) + "%"
    if fmt == "mult":
        return "×" + trim(1 + v)
    if fmt == "x":
        return "×" + trim2(v)
    if fmt == "raw":
        return ("+" if v > 0 else "") + trim(v)
    return trim(v)


def spec_of(variants):
    return "|".join(",".join("%g" % float(v) for v in arr) for arr in variants)


def chip_html(ch, core, q=6):
    roll = ""
    if ch.get("roll"):
        r = ch["roll"]
        roll = " data-roll='%s,%s,%s'" % (r["op"], r["lo"], r["hi"])
    return ("<i class='%s'>%s <b data-vals='%s' data-fmt='%s'%s>%s</b></i>"
            % ("core" if core else "", e(ch["k"]), e(spec_of(ch["variants"])),
               e(ch["fmt"]), roll, e(fmt_one(ch["variants"][0][q - 1], ch["fmt"]))))


def build():
    data = json.load(open(JSON_IN, encoding="utf-8"))
    cats, tools = data["categories"], data["tools"]
    q = 6
    out = []
    w = out.append
    w("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w("<title>七日杀 V3.4 工具速查表</title>")
    w("<style>" + CSS + "</style></head><body><div class='wrap'>")

    w("<header class='top'><h1>七日杀 · 工具速查表<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>items.xml</code> 与 <code>Localization.csv</code>"
      "<br>生成时间 %s ｜ %d 把工具 · %d 个分类</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(tools), len(cats)))
    w("<div class='sub' style='margin-top:8px'>数值是品质 1–6 的区间；"
      "「对泥土 / 对石头 / 对金属」是工具对不同材质的效率倍率（×0.2 表示只有 20%）。"
      "电锯和螺旋钻另有 ±8% 的随机浮动，卡片上可以拖动查看。</div></header>")

    w("<nav class='jump'><div class='navrow'>")
    w("<button class='chipbtn on' data-cat='all'>全部<small>%d</small></button>" % len(tools))
    for c in cats:
        w("<button class='chipbtn' data-cat='%s'>%s<small>%d</small></button>"
          % (c["id"], e(c["name"]), c["count"]))
    w("<span class='spacer'></span>")
    w("<button class='btn' id='rangetoggle'>显示区间</button>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索工具'></label>")
    w("</div></nav>")

    for c in cats:
        members = [x for x in tools if x["cat"] == c["id"]]
        w("<section class='cat' id='%s'>" % c["id"])
        w("<div class='cat-head'><span class='bar' style='background:%s'></span>"
          "<h2>%s</h2><span class='cnt'>%d 把</span></div>" % (c["color"], e(c["name"]), len(members)))
        w("<p class='cat-intro'>%s</p>" % e(c["intro"]))
        w("<div class='grid'>")
        for t in members:
            blob = " ".join([t["name"], t["name_en"], t["desc"]] + [ch["k"] for ch in t["chips"]]).lower()
            w("<article class='tool' id='%s' data-cat='%s' data-text='%s'>"
              % (e(t["id"]), c["id"], e(blob)))
            w("<div class='thead'><span class='badge %s'>%s</span>%s<h3>%s<em>%s</em></h3></div>"
              % (c["id"], e(c["name"]),
                 ("<span class='tier'>%s</span>" % e(t["tier"])) if t["tier"] else "",
                 e(t["name"]), e(t["name_en"])))
            w("<div class='setq'><span class='qlbl'>品质</span>"
              "<input class='qslider' type='range' min='1' max='6' step='1' value='6' "
              "aria-label='%s 品质'><b class='qnow'>6</b></div>" % e(t["name"]))
            if t.get("has_roll"):
                w("<div class='rrow'><span class='qlbl'>随机浮动</span>"
                  "<input class='rslider' type='range' min='0' max='100' step='5' value='50' "
                  "aria-label='%s 随机浮动'><b class='rnow'>基准</b></div>" % e(t["name"]))
            core = [ch for ch in t["chips"] if ch.get("primary")]
            other = [ch for ch in t["chips"] if not ch.get("primary")]
            if core:
                w("<div class='chips'>%s</div>" % "".join(chip_html(ch, True, q) for ch in core))
            if other:
                w("<details class='more'><summary>更多数值（%d）</summary><div class='chips'>%s</div></details>"
                  % (len(other), "".join(chip_html(ch, False, q) for ch in other)))
            if t["desc"]:
                w("<p class='desc'>%s</p>" % e(t["desc"]).replace("\n", "<br>"))
            w("</article>")
        w("</div></section>")

    w("<footer>数据来源：本机 <code>Data/Config/items.xml</code> 与 <code>Localization.csv</code>。"
      "<br>游戏更新后重新运行 <code>parse_tools.py</code> 与 <code>render_tools_sheet.py</code> 即可刷新。</footer>")
    w("</div><script>" + JS + "</script></body></html>")

    open(OUT_HTML, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
