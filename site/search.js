
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
