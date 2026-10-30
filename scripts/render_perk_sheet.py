# -*- coding: utf-8 -*-
"""Render the parsed perk model into a single self-contained Chinese HTML sheet
with a build planner and full book-volume details."""
import html
import json
import re
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\perks_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4天赋速查表.html"
GAME_VERSION = "V 3.4.0 (b9)"

ATTR_META = {
    "attPerception": {"emoji": "👁", "color": "#49b6e8", "short": "感知"},
    "attStrength": {"emoji": "💪", "color": "#e0574c", "short": "力量"},
    "attFortitude": {"emoji": "🛡", "color": "#57b95f", "short": "强健"},
    "attAgility": {"emoji": "🏃", "color": "#e2b03c", "short": "敏捷"},
    "attIntellect": {"emoji": "🧠", "color": "#a06fd0", "short": "智慧"},
    "attGeneralPerks": {"emoji": "⭐", "color": "#8fa3ad", "short": "通用"},
}

CSS = """
:root{
  --bg:#100e0c; --panel:#1a1714; --panel2:#221d19; --line:#332b24;
  --text:#e8e1d8; --dim:#a2988c; --accent:#e8a33d; --accent2:#c8762a;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.65 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif;}
body.plan{padding-bottom:70px}
a{color:var(--accent);text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}
header.top{padding:34px 0 18px;border-bottom:1px solid var(--line)}
h1{margin:0 0 6px;font-size:27px;letter-spacing:.5px}
h1 .ver{font-size:14px;color:var(--accent);border:1px solid var(--accent2);
  border-radius:4px;padding:2px 7px;margin-left:10px;vertical-align:middle}
.sub{color:var(--dim);font-size:13px}
.sub code{background:#251f1a;padding:1px 5px;border-radius:3px;color:#d8c9b6}
.rules{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:22px 0 4px}
.rule{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:6px;padding:12px 14px}
.rule b{display:block;color:var(--accent);font-size:13px;letter-spacing:.5px;margin-bottom:4px}
.rule span{color:var(--dim);font-size:13px}
.rule span em{color:var(--text);font-style:normal}

nav.jump{position:sticky;top:0;z-index:20;background:rgba(16,14,12,.96);
  border-bottom:1px solid var(--line);
  display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 0;margin-bottom:26px}
nav.jump a{font-size:13px;padding:5px 11px;border:1px solid var(--line);border-radius:20px;
  color:var(--text);background:var(--panel);white-space:nowrap}
nav.jump a:hover{border-color:var(--accent);color:var(--accent)}
.chipbtn{font-size:13px;padding:5px 11px;border:1px solid var(--line);border-radius:20px;
  color:var(--text);background:var(--panel);cursor:pointer;font-family:inherit;white-space:nowrap}
.chipbtn:hover{border-color:var(--accent);color:var(--accent)}
.chipbtn.on{background:var(--accent);color:#1a1208;border-color:var(--accent);font-weight:700}
.chipbtn small{opacity:.6;margin-left:4px;font-size:10.5px}
nav.jump .spacer{flex:1}
.search{display:flex;align-items:center;gap:6px;background:var(--panel);
  border:1px solid var(--line);border-radius:20px;padding:4px 12px}
.search input{background:transparent;border:0;outline:0;color:var(--text);
  font-size:13px;width:180px;font-family:inherit}
.search input::placeholder{color:#6f665c}
.btn{font-size:12px;padding:5px 11px;border-radius:20px;border:1px solid var(--line);
  background:var(--panel);color:var(--dim);cursor:pointer;font-family:inherit}
.btn:hover{color:var(--accent);border-color:var(--accent)}
.btn.primary{color:#1a1208;background:var(--accent);border-color:var(--accent);font-weight:700}
.btn.primary:hover{background:#f0b455;color:#1a1208}

section.attr{margin:0 0 46px;scroll-margin-top:70px}
.attr-head{display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  padding:0 0 10px;border-bottom:2px solid var(--line);margin-bottom:6px}
.attr-head .bar{width:6px;height:26px;border-radius:3px;display:inline-block}
.attr-head h2{margin:0;font-size:21px}
.attr-head .en{color:var(--dim);font-size:13px;letter-spacing:1px}
.attr-right{margin-left:auto;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.attr-head .cnt{color:var(--dim);font-size:12px}
.attr-desc{color:#c4b8a9;font-size:13.5px;margin:10px 0 14px;max-width:900px}
details.attr-ranks{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:10px 14px;margin:0 0 20px;font-size:13px}
details.attr-ranks summary{cursor:pointer;color:var(--accent);outline:0;font-size:13px}
table.ranks-tbl{width:100%;border-collapse:collapse;margin-top:10px}
table.ranks-tbl td{padding:6px 8px;border-top:1px solid var(--line);vertical-align:top;color:#cfc3b5}
table.ranks-tbl td:first-child{color:var(--accent);white-space:nowrap;width:52px}
table.ranks-tbl td.cost{white-space:nowrap;width:60px;color:var(--dim)}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(345px,1fr));gap:14px}
.perk{background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.perk.open{border-color:#463a2e;background:var(--panel2)}
.perk.on{border-color:#6b5334;box-shadow:inset 0 0 0 1px #3d2f1f}
.pbody{padding:13px 15px 12px;cursor:pointer}
.phead{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pname{font-size:16px;font-weight:700;color:#f3eadc}
.pname em{font-style:normal;font-weight:400;font-size:11.5px;color:#7d7367;
  letter-spacing:.4px;margin-left:6px}
.tag{font-size:11px;color:var(--dim);border:1px solid var(--line);
  border-radius:10px;padding:1px 7px;white-space:nowrap}
.caret{margin-left:auto;color:#6f665c;font-size:11px;transition:transform .15s}
body.plan .phead .caret{margin-left:6px}
body.plan .phead .prank{margin-left:auto}
.perk.open .caret{transform:rotate(90deg);color:var(--accent)}
.pdesc{margin:7px 0 10px;font-size:12.8px;color:#b3a897;white-space:pre-line}
.ladder{display:flex;gap:5px;flex-wrap:wrap}
.ladder i{font-style:normal;font-size:11px;min-width:22px;text-align:center;
  background:#2a231d;border:1px solid #3a3027;border-radius:4px;padding:2px 4px;color:#8b8175}
.ladder i span{color:#6f665c;font-size:9px;margin-left:3px}
.ladder i.lit{border-color:#4a3c2b;color:#cbbfae}
.ladder i.got{background:#e8a33d;border-color:#e8a33d;color:#1a1208;font-weight:700}
.ladder i.got span{color:#4a3520}
.ranks{display:none;padding:0 15px 14px;border-top:1px solid var(--line)}
.perk.open .ranks{display:block}
.rank{display:grid;grid-template-columns:26px 66px 1fr;gap:8px;padding:9px 0;
  border-bottom:1px dashed #2c2520;font-size:12.8px}
.rank:last-child{border-bottom:0}
.rank .rn{color:var(--accent);font-weight:700}
.rank .rq{color:var(--dim);font-size:11.5px;white-space:nowrap}
.rank p{margin:0;color:#c9bdad;white-space:pre-line}
.empty{color:var(--dim);padding:30px;text-align:center;font-size:14px}

/* planner controls */
.actrl,.prank{display:none;align-items:center;gap:6px}
body.plan .actrl,body.plan .prank{display:flex}
.actrl button,.prank button{width:22px;height:22px;line-height:1;padding:0;
  border-radius:5px;border:1px solid #4a3c2b;background:#2a231d;color:var(--accent);
  font-size:14px;cursor:pointer;font-family:inherit}
.actrl button:hover:not(:disabled),.prank button:hover:not(:disabled){background:#3a2f22;border-color:var(--accent)}
.actrl button:disabled,.prank button:disabled{color:#5a5148;border-color:#332b24;cursor:not-allowed}
.actrl b{color:#f3eadc;min-width:18px;text-align:center;font-size:14px}
.actrl .aspent{color:#7d7367;font-size:11px;white-space:nowrap}
.prank{margin-left:auto}
.prank b{color:var(--accent);min-width:14px;text-align:center;font-size:13px}
.prank i{font-style:normal;color:#6f665c;font-size:11px;margin-left:-3px}

#planbar{display:none;position:fixed;left:0;right:0;bottom:0;z-index:40;
  background:rgba(26,23,20,.98);border-top:1px solid #4a3c2b;
  padding:10px 18px;gap:18px;align-items:center;justify-content:center;
  font-size:13px;flex-wrap:wrap}
body.plan #planbar{display:flex}
#planbar label{color:var(--dim)}
#planbar input{width:62px;background:#0f0d0b;border:1px solid #4a3c2b;border-radius:5px;
  color:var(--text);padding:3px 7px;font-family:inherit;font-size:13px;text-align:center}
#planbar .big{font-size:15px;color:#f3eadc;font-weight:700}
#planbar .neg{color:#e0574c !important}
#planbar .hint{color:#7d7367;font-size:11.5px}

.appendix{margin-top:52px;padding-top:22px;border-top:2px solid var(--line)}
.appendix h2{font-size:19px;margin:0 0 6px}
.appendix .note{color:var(--dim);font-size:12.5px;margin-bottom:16px}
.cols{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:8px}
.mini{background:var(--panel);border:1px solid var(--line);border-radius:6px;
  padding:8px 11px;font-size:12.5px}
.mini b{display:block;color:#ded3c4;font-weight:600}
.mini small{color:#8b8175;font-size:11px}
details.series{background:var(--panel);border:1px solid var(--line);border-radius:8px;margin-bottom:10px}
details.series summary{cursor:pointer;padding:10px 14px;font-size:13.5px;outline:0}
details.series summary b{color:#eee2d3;font-size:14.5px}
details.series summary small{color:#7d7367;margin-left:8px;font-size:11.5px}
details.series summary .vc{float:right;color:var(--accent);font-size:12px}
.vols{padding:0 14px 12px}
.vol{display:grid;grid-template-columns:64px 1fr;gap:10px;padding:8px 0;
  border-top:1px dashed #2c2520;font-size:12.8px}
.vol .vn{color:var(--accent);font-size:12px;white-space:nowrap}
.vol p{margin:0;color:#c2b6a6;white-space:pre-line}
.vol.done .vn{color:#57b95f}
.vol.done p{color:#9fc7a2}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
.hide{display:none !important}
@media (max-width:620px){
  .search input{width:110px}
  .grid{grid-template-columns:1fr}
  h1{font-size:22px}
  #planbar{gap:10px;font-size:12px;padding:8px 10px}
  body.plan{padding-bottom:104px}
}
@media print{
  body{background:#fff;color:#000}
  nav.jump,#planbar{display:none !important}
  .perk,.series,.attr-ranks{background:#fff;border-color:#ccc;break-inside:avoid}
  .ranks{display:block !important}
  .pname,.pdesc,.rank p,.attr-desc,.vol p{color:#000}
}
"""

JS = r"""
(function(){
  var secs  = [].slice.call(document.querySelectorAll('section.attr'));
  var cards = [].slice.call(document.querySelectorAll('.perk'));
  var series = [].slice.call(document.querySelectorAll('details.series'));
  var appendix = document.getElementById('books');
  var catBtns = [].slice.call(document.querySelectorAll('.chipbtn[data-cat]'));
  var cat = 'all';
  var lvlInput = document.getElementById('plv');
  var barAvail = document.getElementById('pavail');
  var barUsed  = document.getElementById('pused');
  var barLeft  = document.getElementById('pleft');
  var toggle   = document.getElementById('plantoggle');
  var resetBtn = document.getElementById('preset');
  var q        = document.getElementById('q');

  var attrLevel = {}, perkRank = {};
  secs.forEach(function(s){ attrLevel[s.dataset.attr] = 1; });
  cards.forEach(function(c){ perkRank[c.dataset.id] = 0; });

  function secOf(id){ for (var i=0;i<secs.length;i++) if (secs[i].dataset.attr === id) return secs[i]; return null; }
  function costsOf(s){ return s.dataset.costs.split(',').map(Number); }
  function attrCost(id){
    var s = secOf(id), cs = costsOf(s), sum = 0;
    for (var l = 2; l <= attrLevel[id]; l++) sum += cs[l];
    return sum;
  }
  function spent(){
    var t = 0;
    secs.forEach(function(s){ t += attrCost(s.dataset.attr); });
    cards.forEach(function(c){ t += perkRank[c.dataset.id]; });
    return t;
  }
  function budget(){
    var v = parseInt(lvlInput.value, 10);
    if (isNaN(v)) v = 1;
    return Math.max(1, Math.min(300, v));
  }
  function left(){ return budget() - spent(); }
  function reqsOf(c){ return c.dataset.reqs.split(',').map(function(x){ return parseInt(x,10) || 0; }); }
  function allowed(c){
    var r = reqsOf(c), lv = attrLevel[c.dataset.attr], n = 0;
    for (var i=0;i<r.length;i++){ if (lv >= r[i]) n++; else break; }
    return n;
  }

  function render(){
    var used = spent(), avail = budget(), rest = avail - used;
    barAvail.textContent = avail;
    barUsed.textContent  = used;
    barLeft.textContent  = rest;
    barLeft.classList.toggle('neg', rest < 0);

    secs.forEach(function(s){
      var id = s.dataset.attr, lv = attrLevel[id], cs = costsOf(s);
      s.querySelector('.alv').textContent = lv;
      s.querySelector('.aspent').textContent = '已投 ' + attrCost(id) + ' 点';
      s.querySelector('[data-act="attr-"]').disabled = (lv <= 1);
      s.querySelector('[data-act="attr+"]').disabled = (lv >= 10) || (rest < cs[lv+1]);
    });

    cards.forEach(function(c){
      var id = c.dataset.id, rank = perkRank[id], max = parseInt(c.dataset.max, 10), al = allowed(c);
      c.querySelector('.prank b').textContent = rank;
      c.classList.toggle('on', rank > 0);
      c.querySelector('[data-act="perk-"]').disabled = (rank <= 0);
      c.querySelector('[data-act="perk+"]').disabled = (rank >= max) || (rank >= al) || (rest < 1);
      var chips = c.querySelectorAll('.ladder i');
      for (var i=0;i<chips.length;i++){
        chips[i].classList.toggle('lit', i < al);
        chips[i].classList.toggle('got', i < rank);
      }
    });
  }

  document.addEventListener('click', function(ev){
    var b = ev.target.closest ? ev.target.closest('button[data-act]') : null;
    if (b){
      ev.preventDefault(); ev.stopPropagation();
      var act = b.dataset.act;
      if (act === 'attr+' || act === 'attr-'){
        var id = b.closest('section').dataset.attr;
        var cs = costsOf(secOf(id));
        if (act === 'attr+' && attrLevel[id] < 10 && left() >= cs[attrLevel[id]+1]){
          attrLevel[id]++;
        } else if (act === 'attr-' && attrLevel[id] > 1){
          attrLevel[id]--;
          cards.forEach(function(c){
            if (c.dataset.attr === id && perkRank[c.dataset.id] > allowed(c))
              perkRank[c.dataset.id] = allowed(c);
          });
        }
      } else {
        var card = b.closest('.perk'), pid = card.dataset.id;
        var max = parseInt(card.dataset.max, 10);
        if (act === 'perk+' && perkRank[pid] < max && perkRank[pid] < allowed(card) && left() >= 1){
          perkRank[pid]++;
          card.classList.add('open');
        } else if (act === 'perk-' && perkRank[pid] > 0){
          perkRank[pid]--;
        }
      }
      render();
      return;
    }
    var body = ev.target.closest ? ev.target.closest('.pbody') : null;
    if (body) body.parentNode.classList.toggle('open');
  });

  toggle.addEventListener('click', function(){
    var on = document.body.classList.toggle('plan');
    toggle.textContent = on ? '退出模拟' : '开始模拟加点';
    toggle.classList.toggle('primary', !on);
    if (on) render();
  });

  if (resetBtn) resetBtn.addEventListener('click', function(){
    secs.forEach(function(s){ attrLevel[s.dataset.attr] = 1; });
    cards.forEach(function(c){ perkRank[c.dataset.id] = 0; });
    render();
  });

  lvlInput.addEventListener('input', render);
  lvlInput.addEventListener('blur', function(){
    lvlInput.value = budget();
    render();
  });

  function filter(){
    var v = (q.value || '').trim().toLowerCase();
    cards.forEach(function(c){
      c.classList.toggle('hide', !!v && c.dataset.text.indexOf(v) === -1);
    });
    series.forEach(function(s){
      s.classList.toggle('hide', !!v && (s.dataset.text || '').indexOf(v) === -1);
    });
    secs.forEach(function(s){
      var okCat = (cat === 'all' || cat === s.dataset.attr);
      var visible = okCat && s.querySelectorAll('.perk:not(.hide)').length > 0;
      s.classList.toggle('hide', !visible);
    });
    if (appendix){
      var okCat = (cat === 'all' || cat === 'books');
      var anySeries = appendix.querySelectorAll('details.series:not(.hide)').length > 0;
      appendix.classList.toggle('hide', !(okCat && anySeries));
    }
  }
  q.addEventListener('input', filter);

  catBtns.forEach(function(b){
    b.addEventListener('click', function(){
      cat = b.dataset.cat;
      catBtns.forEach(function(x){ x.classList.toggle('on', x === b); });
      filter();
    });
  });

  function pickCat(id){
    var btn = catBtns.filter(function(b){ return b.dataset.cat === id; })[0];
    if (!btn) return;
    cat = id;
    catBtns.forEach(function(x){ x.classList.toggle('on', x === btn); });
    filter();
  }

  if (location.hash){
    var hid = location.hash.slice(1);
    if (hid === 'books' || secs.some(function(s){ return s.dataset.attr === hid; }))
      pickCat(hid);
  }
  document.addEventListener('keydown', function(ev){
    if (ev.key === '/' && document.activeElement !== q && document.activeElement !== lvlInput){
      ev.preventDefault(); q.focus();
    }
    if (ev.key === 'Escape' && document.activeElement === q){ q.value=''; filter(); q.blur(); }
  });

  render();
})();
"""


def e(s):
    return html.escape(s or "", quote=True)


def para(s):
    return e(s).replace("\n", "<br>")


def vol_label(name):
    m = re.search(r"第\s*(\d+)\s*卷", name or "")
    if m:
        return "第%s卷" % m.group(1)
    m = re.search(r"卷\s*(\d+)", name or "")
    if m:
        return "第%s卷" % m.group(1)
    return name or ""


def build():
    with open(JSON_IN, encoding="utf-8") as f:
        m = json.load(f)

    attrs = m["attributes"]
    perks = m["perks"]
    lvl = m["level"]

    # per-attribute purchase cost by target level (level 1 = start, free)
    attr_costs = {}
    for a in attrs:
        cs = [0] * 11
        for k, v in a["reqs"].items():
            lv = int(k)
            cs[lv] = v.get("cost") or 1
        cs[1] = 0
        attr_costs[a["id"]] = cs

    total_perk_ranks = sum(len(p["ranks"]) for p in perks)
    n_volumes = sum(len(b["volumes"]) for b in m["book_groups"])
    max_points = sum(sum(attr_costs[a["id"]]) for a in attrs) + total_perk_ranks

    out = []
    w = out.append
    w("<!DOCTYPE html>")
    w('<html lang="zh-CN"><head><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w("<title>七日杀 V3.4 天赋速查表</title>")
    w("<style>" + CSS + "</style>")
    w("</head><body><div class='wrap'>")

    # ---------- header
    w("<header class='top'>")
    w("<h1>七日杀 · 天赋速查表<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据直接取自本机游戏文件 "
      "<code>Data/Config/progression.xml</code>、<code>items.xml</code>、"
      "<code>Localization.csv</code>（简体中文）"
      "<br>生成时间 %s ｜ 5 项属性 · 50 个属性天赋 · 7 个通用天赋 · "
      "19 套书籍（%d 卷）· 24 本制作杂志</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), n_volumes))
    w("<div class='sub' style='margin-top:8px'>"
      "<span style='color:#e8a33d'>筛选：</span>顶部按钮按属性过滤，点「力量」就只显示力量系天赋，"
      "「书籍/杂志」只看书；搜索框支持中英文名和效果关键词（按 <code>/</code> 聚焦）。<br>"
      "<span style='color:#e8a33d'>看数值：</span>点卡片展开每一级的具体效果。<br>"
      "<span style='color:#e8a33d'>试加点：</span>点右上角「开始模拟加点」，输入等级后加减属性和天赋，"
      "实时结算剩余点数，属性掉级会自动退还受影响的加点。<br>"
      "<span style='color:#e8a33d'>配套页面：</span>"
      "<a href='七日杀V3.4装甲速查表.html'>装甲速查表</a> · "
      "<a href='七日杀V3.4武器速查表.html'>武器速查表</a> · "
      "<a href='七日杀V3.4模组速查表.html'>模组速查表</a></div>")
    w("</header>")

    # ---------- rules
    w("<div class='rules'>")
    w("<div class='rule'><b>技能点怎么来</b><span>每升 1 级得 "
      "<em>%d 点</em>技能点，等级上限 <em>%d</em> 级；"
      "开局另有基础点数（受世界设置影响）。</span></div>"
      % (lvl["skill_points_per_level"], lvl["max_level"]))
    w("<div class='rule'><b>属性升级花费</b><span>属性 1→5 每级 <em>1 点</em>，"
      "6→8 每级 <em>2 点</em>，9→10 每级 <em>3 点</em>；五项属性点满 <em>80 点</em>。</span></div>")
    w("<div class='rule'><b>天赋升级花费</b><span>每个天赋等级固定 <em>1 点</em>，"
      "但要先把对应属性点到该级（卡片下方等级条）。</span></div>")
    w("<div class='rule'><b>全部点满要多少</b><span>属性 80 + 属性天赋 250 + 通用天赋 %d "
      "= <em>%d 点</em>；而一局最多只有 <em>%d 点</em>（%d 级封顶），注定点不满，必须取舍。</span></div>"
      % (total_perk_ranks - 250, max_points, lvl["max_level"], lvl["max_level"]))
    w("</div>")

    # ---------- nav
    w("<nav class='jump'>")
    w("<button class='chipbtn on' data-cat='all'>全部</button>")
    for a in attrs:
        meta = ATTR_META.get(a["id"], {})
        n = sum(1 for p in perks if p["attr"] == a["id"])
        w("<button class='chipbtn' data-cat='%s'>%s %s<small>%d</small></button>"
          % (a["id"], meta.get("emoji", ""), e(meta.get("short", a["name"])), n))
    w("<button class='chipbtn' data-cat='books'>📚 书籍/杂志</button>")
    w("<span class='spacer'></span>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索天赋 / 效果'></label>")
    w("<button class='btn' id='plantoggle'>开始模拟加点</button>")
    w("</nav>")

    # ---------- attribute sections
    for a in attrs:
        meta = ATTR_META.get(a["id"], {"emoji": "", "color": "#888", "short": a["name"]})
        ap = [p for p in perks if p["attr"] == a["id"]]
        name = a["name"]
        for prefix in ("属性：", "属性:"):
            if name.startswith(prefix):
                name = name[len(prefix):]
        if a["id"] == "attGeneralPerks":
            name = "通用天赋"
        cs = attr_costs[a["id"]]
        w("<section class='attr' id='%s' data-attr='%s' data-costs='%s'>"
          % (a["id"], a["id"], ",".join(str(x) for x in cs)))
        w("<div class='attr-head'><span class='bar' style='background:%s'></span>"
          "<h2>%s %s</h2><span class='en'>%s</span>"
          "<span class='attr-right'><span class='cnt'>%d 个天赋</span>"
          "<span class='actrl'><button data-act='attr-' title='降一级'>−</button>"
          "<b class='alv'>1</b>"
          "<button data-act='attr+' title='升一级'>+</button>"
          "<span class='aspent'>已投 0 点</span></span></span></div>"
          % (meta["color"], meta["emoji"], e(name), e(a["name_en"]), len(ap)))
        if a["desc"]:
            w("<p class='attr-desc'>%s</p>" % para(a["desc"]))

        if a["ranks"]:
            w("<details class='attr-ranks'><summary>查看 %s 每级效果与花费</summary>" % e(name))
            w("<table class='ranks-tbl'>")
            for lv in sorted(int(k) for k in a["ranks"]):
                r = a["ranks"][str(lv)]
                cost = cs[lv] if 0 <= lv <= 10 else None
                w("<tr><td>Lv.%d</td><td class='cost'>%s</td><td>%s</td></tr>"
                  % (lv, ("%d 点" % cost) if cost else "初始", para(r["long"])))
            w("</table></details>")

        w("<div class='grid'>")
        for p in ap:
            reqs = {int(k): v for k, v in p["reqs"].items()}
            ranks = {int(k): v for k, v in p["ranks"].items()}
            blob = " ".join([p["name"], p["name_en"], p["desc"]] +
                            [ranks[k]["long"] for k in sorted(ranks)]).lower()
            req_list = [str(reqs.get(lv, {}).get("attr_level") or 0) for lv in sorted(ranks)]
            w("<div class='perk' data-id='%s' data-attr='%s' data-max='%d' "
              "data-reqs='%s' data-text='%s'>"
              % (p["id"], a["id"], len(ranks), ",".join(req_list), e(blob)))
            w("<div class='pbody'>")
            w("<div class='phead'><span class='pname'>%s<em>%s</em></span>"
              "<span class='tag'>%s</span>"
              "<span class='prank'><button data-act='perk-' title='退一级'>−</button>"
              "<b>0</b><i>/%d</i>"
              "<button data-act='perk+' title='点一级'>+</button></span>"
              "<span class='caret'>▶</span></div>"
              % (e(p["name"]), e(p["name_en"]),
                 e("通用天赋" if a["id"] == "attGeneralPerks" else (p["group_name"] or name)),
                 len(ranks)))
            if p["desc"]:
                w("<p class='pdesc'>%s</p>" % para(p["desc"]))
            w("<div class='ladder'>")
            for lv in sorted(ranks):
                need = reqs.get(lv, {}).get("attr_level")
                w("<i>%d<span>%s</span></i>" % (lv, ("需%d" % need) if need else "通用"))
            w("</div></div>")
            w("<div class='ranks'>")
            for lv in sorted(ranks):
                need = reqs.get(lv, {}).get("attr_level")
                cost = reqs.get(lv, {}).get("cost") or 1
                w("<div class='rank'><span class='rn'>%d</span>"
                  "<span class='rq'>%s<br>%d 点</span><p>%s</p></div>"
                  % (lv, ("%s %d" % (meta["short"], need)) if need else "通用", cost, para(ranks[lv]["long"])))
            w("</div></div>")
        w("</div>")
        w("</section>")

    # ---------- books
    w("<div class='appendix' id='books' data-cat='books'>")
    w("<h2>📚 书籍系列（19 套 / %d 卷）</h2>" % n_volumes)
    w("<p class='note'>书籍天赋不能加点，只能在世界里捡到；每套 7 卷，集齐后额外解锁一个完成奖励。"
      "下面是每卷的完整中文效果。</p>")
    for b in m["book_groups"]:
        blob = " ".join([b["name"], b["name_en"]] + [v["name"] for v in b["volumes"]])
        w("<details class='series' data-text='%s'>" % e(blob.lower()))
        w("<summary><b>%s</b><small>%s</small>"
          "<span class='vc'>%d 卷</span></summary><div class='vols'>"
          % (e(b["name"]), e(b["name_en"]), len(b["volumes"])))
        for v in b["volumes"]:
            w("<div class='vol'><span class='vn'>%s</span><p>%s</p></div>"
              % (e(vol_label(v["name"])), para(v["desc"])))
        comp = b.get("complete") or {}
        if comp.get("desc"):
            w("<div class='vol done'><span class='vn'>全 %d 卷</span><p>%s</p></div>"
              % (len(b["volumes"]), para(comp["desc"])))
        w("</div></details>")

    w("<h2 style='margin-top:34px'>🔧 制作杂志（24）</h2>")
    w("<p class='note'>这些是制作技能，不占天赋点，靠读同名杂志提升（上限 100 级）。</p>")
    w("<div class='cols'>")
    for mg in m["magazines"]:
        w("<div class='mini'><b>%s</b><small>%s</small></div>" % (e(mg["name"]), e(mg["name_en"])))
    w("</div>")
    w("</div>")

    w("<footer>数据来源：本机 <code>7 Days to Die</code> 安装目录下 "
      "<code>Data/Config/progression.xml</code>（属性/天赋）、"
      "<code>items.xml</code>（书籍卷）、<code>Localization.csv</code>（中文文本）。"
      "<br>模拟器只按每级 1 点计算，不含开局额外点数；游戏更新后重新运行 "
      "<code>parse_perks.py</code> 与 <code>render_perk_sheet.py</code> 即可刷新。</footer>")

    w("</div>")

    # ---------- plan bar
    w("<div id='planbar'>")
    w("<label>玩家等级 <input id='plv' type='number' min='1' max='300' value='30'></label>")
    w("<span>可用 <b class='big' id='pavail'>30</b></span>")
    w("<span>已用 <b class='big' id='pused'>0</b></span>")
    w("<span>剩余 <b class='big' id='pleft'>30</b></span>")
    w("<span class='hint'>每级 1 点，未计开局额外点数</span>")
    w("<button class='btn' id='preset'>重置</button>")
    w("</div>")

    w("<script>" + JS + "</script>")
    w("</body></html>")

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")
    print("max points:", max_points, "perk ranks:", total_perk_ranks, "volumes:", n_volumes)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
