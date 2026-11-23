# -*- coding: utf-8 -*-
"""Envoltorio de página (técnicas de formulario.html) + motor de interacciones en JS ES5."""
import html, json

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">')

CSS = """
.awx-overlay{position:fixed;inset:0;z-index:9999;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;background:var(--fz-bg,#6fd95d)}
.awx-overlay.fz-lock{overflow:hidden}
.awx-landing{font-family:Inter,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;color:#1f3328;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
.awx-landing div,.awx-landing span,.awx-landing a,.awx-landing svg,.awx-landing img,.awx-landing input,.awx-landing textarea{box-sizing:border-box;margin:0;max-width:none;float:none;letter-spacing:inherit}
.awx-landing div::before,.awx-landing div::after{content:none!important;display:none!important}
.awx-landing a{color:inherit;text-decoration:none}
.awx-landing input,.awx-landing textarea{font:inherit;width:100%;height:100%;background-clip:padding-box;appearance:none;-webkit-appearance:none;box-shadow:none}
.awx-landing input::placeholder,.awx-landing textarea::placeholder{color:inherit;opacity:.75;-webkit-text-fill-color:currentColor}
.awx-landing .fz-desk,.awx-landing .fz-mob{position:relative;margin:0 auto;overflow:hidden}
.awx-landing [data-fz],.awx-landing [data-send]{cursor:pointer}
.awx-landing [data-fz]:focus-visible,.awx-landing [data-send]:focus-visible{outline:3px solid #6b2b8f;outline-offset:2px}
.awx-landing [data-fixed]{position:fixed!important;z-index:50}
.awx-landing [data-ring]{animation:fzSpin 40s linear infinite;transform-origin:50% 50%}
.awx-landing [data-ring=in]{animation-duration:55s;animation-direction:reverse}
.awx-landing svg{overflow:visible}
.awx-landing [data-hide]{visibility:hidden!important;pointer-events:none!important}
.awx-landing.fz-still [data-ring],.awx-landing.fz-still .fz-enter>*{animation:none!important}
@keyframes fzSpin{to{transform:rotate(360deg)}}
.awx-landing .fz-enter>*{animation:fzIn .42s ease-out both}
.awx-landing .fz-enter>*:nth-child(2){animation-delay:.06s}.awx-landing .fz-enter>*:nth-child(3){animation-delay:.12s}
.awx-landing .fz-enter>*:nth-child(4){animation-delay:.18s}.awx-landing .fz-enter>*:nth-child(5){animation-delay:.24s}
@keyframes fzIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.awx-landing .fz-ovl{position:fixed;inset:0;z-index:100000;overflow-y:auto;overflow-x:hidden;display:flex;align-items:flex-start;justify-content:center;animation:fzFade .2s ease-out}
.awx-landing .fz-ovl[hidden]{display:none}
.awx-landing .fz-ovl.fz-dim{background:rgba(20,32,24,.45)}
.awx-landing .fz-ovf{position:relative;margin:auto 0}
@keyframes fzFade{from{opacity:0}to{opacity:1}}
.awx-landing .fz-msg{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.awx-landing .fz-msg span{display:inline-flex;padding:7px 12px;border-radius:999px;font-size:13px;font-weight:700}
.awx-landing .fz-msg .ok{background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0}
.awx-landing .fz-msg .warn{background:#fff7ed;color:#9a3412;border:1px solid #fed7aa}
.awx-landing .fz-msg .err{background:#fef2f2;color:#991b1b;border:1px solid #fecaca}
.awx-landing [data-send].fz-busy{opacity:.7;cursor:wait}
@media (prefers-reduced-motion:reduce){.awx-landing [data-ring],.awx-landing .fz-enter>*,.awx-landing .fz-ovl{animation:none!important}}
"""

JS = r"""
(function(){
  var root = document.querySelector('.awx-landing');
  if(!root) return;
  var T = __TABLE__, RUBRO = __RUBRO__, EP = __EP__, DEST = __DEST__, AUTO = __AUTO__;
  var $$ = function(s,c){ return Array.prototype.slice.call((c||root).querySelectorAll(s)); };
  var desk = root.querySelector('.fz-desk'), mob = root.querySelector('.fz-mob');
  var stack = [], ip = '';

  function isMob(){ return !!mob && root.clientWidth <= 700; }
  function tree(){ return isMob() ? mob : desk; }
  function layout(){
    var w = root.clientWidth, m = isMob();
    if(desk) desk.style.display = m ? 'none' : '';
    if(mob) mob.style.display = m ? '' : 'none';
    var t = tree(); if(t) t.style.zoom = w / (m ? 390 : 1440);
    stack.forEach(function(o){ zoomOv(o); });
  }
  function zoomOv(o){
    o.firstElementChild.style.zoom = root.clientWidth / (isMob() ? 390 : 1440);
  }
  window.addEventListener('resize', layout);
  layout();

  // ---- capas superpuestas ----
  function openOv(id, entry){
    var o = root.querySelector('.fz-ovl[data-ov="'+id+'"]');
    if(!o) return;
    o.hidden = false; stack.push(o); zoomOv(o); o.scrollTop = 0;
    root.classList.add('fz-lock');
    if(entry && entry.fn){
      $$('[data-var="VariableID:10:291"]', o).forEach(function(e){ e.textContent = entry.fn; });
      $$('[data-var="VariableID:10:292"]', o).forEach(function(e){ e.textContent = RUBRO; });
    }
    o.setAttribute('tabindex','-1'); try{ o.focus({preventScroll:true}); }catch(e){}
    timers(o);
  }
  function closeTop(){
    var o = stack.pop(); if(o) o.hidden = true;
    if(!stack.length) root.classList.remove('fz-lock');
  }
  function closeAll(){ while(stack.length) closeTop(); }

  // ---- variantes (cambiar a) ----
  var KEEP = ['position','left','top','right','bottom','flex','flexShrink','alignSelf','zIndex'];
  function change(el, id, set){
    var cur = el.closest('[data-set="'+set+'"]');
    if(!cur){ var cand = $$('[data-set="'+set+'"]', tree()); cur = cand[0]; }
    var tpl = root.querySelector('template[data-tpl="'+id+'"]');
    if(!cur || !tpl) return;
    var nu = tpl.content.firstElementChild.cloneNode(true);
    KEEP.forEach(function(k){ if(cur.style[k]) nu.style[k] = cur.style[k]; });
    nu.setAttribute('data-set', set);
    if(cur.getAttribute('data-fz') && !nu.getAttribute('data-fz')) nu.setAttribute('data-fz', cur.getAttribute('data-fz'));
    if(!root.classList.contains('fz-still')) nu.classList.add('fz-enter');
    cur.parentNode.replaceChild(nu, cur);
    timers(nu);
  }
  function timers(scope){
    var list = $$('[data-fz]', scope); if(scope.getAttribute && scope.getAttribute('data-fz')) list.unshift(scope);
    list.forEach(function(e){
      (T[+e.getAttribute('data-fz')]||[]).forEach(function(en){
        if(en.t === 'time') setTimeout(function(){ if(document.contains(e)) run(en, e); }, en.ms);
      });
    });
  }

  // ---- acciones ----
  function run(en, el){
    en.a.forEach(function(a){
      if(a.k === 'go'){ location.href = a.u; }
      else if(a.k === 'url'){ if(a.b) window.open(a.u, '_blank', 'noopener'); else location.href = a.u; }
      else if(a.k === 'scroll'){
        closeAll();
        var t = tree().querySelector('[data-anchor="'+a.id+'"]');
        if(t) t.scrollIntoView({behavior: root.classList.contains('fz-still') ? 'auto' : 'smooth', block:'start'});
      }
      else if(a.k === 'ov'){ openOv(a.id, en); }
      else if(a.k === 'swapov'){ closeTop(); openOv(a.id, en); }
      else if(a.k === 'close'){ closeTop(); }
      else if(a.k === 'change'){ change(el, a.id, a.set); }
      else if(a.k === 'motion'){ root.classList.toggle('fz-still'); }
    });
  }
  root.addEventListener('click', function(ev){
    var s = ev.target.closest('[data-send]');
    if(s && root.contains(s)){ ev.preventDefault(); send(s); return; }
    var el = ev.target.closest('[data-fz]');
    if(el && root.contains(el)){
      var list = T[+el.getAttribute('data-fz')] || [], done = false;
      list.forEach(function(en){ if(en.t === 'click'){ run(en, el); done = true; } });
      if(done){ ev.preventDefault(); return; }
    }
    // clic en el fondo oscuro de una capa: cerrar
    var o = stack[stack.length-1];
    if(o && (ev.target === o || ev.target === o.firstElementChild || ev.target === o.firstElementChild.firstElementChild)) closeTop();
  });
  document.addEventListener('keydown', function(ev){
    if(ev.key === 'Escape' && stack.length){ closeTop(); return; }
    if(!root.contains(ev.target)) return;
    if((ev.key === 'Enter' || ev.key === ' ') && ev.target.matches && ev.target.matches('[data-fz],[data-send]') ){ ev.preventDefault(); ev.target.click(); }
  });
  $$('[data-fz],[data-send]').forEach(function(e){ e.setAttribute('tabindex','0'); e.setAttribute('role', e.getAttribute('data-send') ? 'button' : (e.getAttribute('role') || 'button')); });
  timers(tree());

  // ---- animaciones automáticas (antes con botón) ----
  function swapTo(set, id){
    [desk, mob].forEach(function(t){
      if(!t) return;
      var cur = t.querySelector('[data-set="'+set+'"]'), tpl = root.querySelector('template[data-tpl="'+id+'"]');
      if(!cur || !tpl) return;
      var nu = tpl.content.firstElementChild.cloneNode(true);
      KEEP.forEach(function(k){ if(cur.style[k]) nu.style[k] = cur.style[k]; });
      nu.setAttribute('data-set', set);
      cur.parentNode.replaceChild(nu, cur);
    });
  }
  Object.keys(AUTO).forEach(function(set){
    var cfg = AUTO[set], i = 0;
    (function step(){
      if(!root.classList.contains('fz-still')){ swapTo(set, cfg.seq[i]); i = (i + 1) % cfg.seq.length; }
      setTimeout(step, cfg.ms[(i + cfg.seq.length - 1) % cfg.seq.length] || 900);
    })();
  });
  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(!e.isIntersecting) return;
        var el = e.target, inner = el.querySelector('[data-set]') || el;
        if(!root.classList.contains('fz-still')){ el.classList.remove('fz-enter'); void el.offsetWidth; el.classList.add('fz-enter'); }
      });
    }, {root: root, threshold: 0.25});
    $$('[data-enter]').forEach(function(e){ io.observe(e); });
  }

  // ---- formulario: POST al centralizador de Apiworking ----
  if(root.querySelector('input[name]')){
    fetch('https://api.ipify.org?format=json', {cache:'no-store'}).then(function(r){ return r.json(); })
      .then(function(d){ ip = d && d.ip ? d.ip : ''; }).catch(function(){});
  }
  $$('input[name=whatsapp]').forEach(function(t){ t.addEventListener('input', function(){ this.value = this.value.replace(/\D/g,''); }); });
  function scopeOf(btn){
    var p = btn.parentNode;
    while(p && p !== root && !p.querySelector('input[name=nombre]')) p = p.parentNode;
    return p || root;
  }
  function msg(btn, items, type){
    var box = btn.nextElementSibling;
    if(!box || !box.classList.contains('fz-msg')){ box = document.createElement('div'); box.className = 'fz-msg'; box.setAttribute('aria-live','polite'); btn.parentNode.insertBefore(box, btn.nextSibling); }
    box.innerHTML = '';
    items.forEach(function(t){ var s = document.createElement('span'); s.className = type; s.textContent = t; box.appendChild(s); });
  }
  function val(f, n){ var e = f.querySelector('[name="'+n+'"]'); return e ? String(e.value||'').trim() : ''; }
  function send(btn){
    if(btn.classList.contains('fz-busy')) return;
    var f = scopeOf(btn), nombre = val(f,'nombre'), tel = val(f,'whatsapp'), neg = val(f,'negocio'), warn = [];
    if(!nombre) warn.push('Falta tu nombre');
    if(!tel || tel.length < 7) warn.push('WhatsApp inválido');
    if(!neg) warn.push('Falta el nombre del negocio');
    if(warn.length){ msg(btn, warn, 'warn'); return; }
    var extra = [];
    $$('input[name],textarea[name]', f).forEach(function(i){
      if(/^(nombre|whatsapp|negocio)$/.test(i.name)) return;
      var v = String(i.value||'').trim(); if(v) extra.push((i.getAttribute('data-label')||i.name) + ': ' + v);
    });
    var giro = RUBRO.toUpperCase() + (extra.length ? ' | ' + extra.join(' | ') : '');
    btn.classList.add('fz-busy'); msg(btn, ['Enviando...'], 'ok');
    fetch(EP, {method:'POST', headers:{'accept':'text/plain','Content-Type':'application/json'},
      body: JSON.stringify({nombreCompleto:nombre, telefono:tel, nombreNegocio:neg, giroNegocio:giro, ipCreacion: ip || '0.0.0.0', destinatarios: DEST}), redirect:'follow'})
      .then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r.text(); })
      .then(function(){
        msg(btn, ['¡Enviado! Te contactaremos pronto.'], 'ok');
        $$('input[name],textarea[name]', f).forEach(function(i){ i.value = ''; });
        var k = btn.getAttribute('data-send'); if(k !== 'x' && T[+k]) T[+k].forEach(function(en){ if(en.t === 'click') run(en, btn); });
      })
      .catch(function(){ msg(btn, ['Error al enviar. Intenta nuevamente.'], 'err'); })
      .then(function(){ btn.classList.remove('fz-busy'); });
  }
})();
"""


def page(title, desc, bg, desk_html, mob_html, overlays, templates, table, rubro, auto=None):
    ovs = "".join(
        f'<div class="fz-ovl{" fz-dim" if w not in (1440, 390) else ""}" data-ov="{html.escape(i)}" data-w="{w}" hidden role="dialog" aria-modal="true"><div class="fz-ovf">{h}</div></div>'
        for i, (h, w) in overlays.items())
    tpls = "".join(f'<template data-tpl="{html.escape(i)}">{h}</template>' for i, h in templates.items())
    js = (JS.replace("__TABLE__", json.dumps(table, ensure_ascii=False, separators=(",", ":")))
            .replace("__RUBRO__", json.dumps(rubro, ensure_ascii=False))
            .replace("__AUTO__", json.dumps(auto or {}, separators=(",", ":")))
            .replace("__EP__", json.dumps("https://api-centralizador.apiworking.pe/api/Administrativo/sendFormContact"))
            .replace("__DEST__", json.dumps(["danielaapiworking@gmail.com", "alo.midocto@gmail.com", "rexlobo45699@gmail.com", "josephchamorrotv@gmail.com"])))
    js = js.replace("</", "<\\/")
    mob = f'<div class="fz-mob" style="width:390px;display:none">{mob_html}</div>' if mob_html else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{FONT}
<style>{CSS}</style>
</head>
<body>
<div class="awx-overlay awx-landing" lang="es" role="document" aria-label="{html.escape(title)}" style="--fz-bg:{bg}">
<div class="fz-desk" style="width:1440px">{desk_html}</div>
{mob}
{ovs}
{tpls}
<script>
{js}
</script>
</div>
</body>
</html>
"""
