# -*- coding: utf-8 -*-
"""Genera páginas HTML autocontenidas (HTML + CSS + JS en un solo archivo)."""
import math, os, re, sys, html
from data import *

OUT = sys.argv[1]
esc = html.escape

FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">'

CSS = r"""
:root{--g:#6cd65b;--g2:#a8e69a;--g3:#dff5d8;--g4:#f3fbef;--dk:#1f3328;--hd:#2b7f35;--y:#ffc414;--y2:#ffe9a6;--cr:#fff4cf;--pu:#6b2b8f;--w:#fff;--mut:#4d6152;--line:rgba(31,51,40,.12);--r:22px;--sh:0 10px 30px rgba(31,51,40,.12)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--dk);background:var(--g);line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:inherit}
img{max-width:100%}
button{font:inherit;cursor:pointer;border:0;background:none;color:inherit}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}
section{padding:88px 0;scroll-margin-top:96px}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:14px}
h1{font-size:clamp(38px,6vw,68px);line-height:1.04;font-weight:700;letter-spacing:-.02em}
h2{font-size:clamp(30px,4.4vw,52px);line-height:1.08;font-weight:700;letter-spacing:-.02em}
h3{font-size:22px;line-height:1.25;font-weight:700}
.lead{font-size:18px;color:var(--mut);max-width:620px;margin-top:16px}
.small{font-size:13px;color:var(--mut)}
.hd{color:var(--hd)}
/* botones */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:15px 26px;border-radius:999px;font-weight:600;font-size:15px;text-decoration:none;transition:transform .15s,box-shadow .15s,background .15s}
.btn:hover{transform:translateY(-1px);box-shadow:var(--sh)}
.btn-y{background:var(--y);color:var(--dk)}
.btn-w{background:#ecfbe3;color:var(--dk)}
.btn-dk{background:var(--dk);color:#fff}
.btn-g{background:var(--g);color:var(--dk)}
.btn-ghost{padding:8px 0;font-weight:600;text-decoration:none}
.btn-ghost:hover{text-decoration:underline}
.btn-sm{padding:9px 16px;font-size:13px}
.btn-block{width:100%}
/* header */
.hdr{position:sticky;top:12px;z-index:50;margin:12px auto 0;max-width:1200px;padding:0 24px}
.hdr-in{display:flex;align-items:center;gap:16px;background:rgba(168,230,154,.9);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.6);border-radius:22px;padding:10px 12px 10px 20px;box-shadow:0 6px 20px rgba(31,51,40,.08)}
.logo{font-weight:800;font-size:21px;letter-spacing:-.03em;text-decoration:none;margin-right:auto}
.nav{display:flex;gap:6px;flex-wrap:wrap}
.nav a{padding:9px 16px;border-radius:999px;font-size:14px;font-weight:600;text-decoration:none;background:rgba(255,255,255,.45)}
.nav a:nth-child(2){background:var(--y2)}
.nav a:hover{background:#fff}
@media(max-width:760px){.hdr-in{flex-wrap:wrap}.nav{order:3;width:100%}.nav a{flex:1;text-align:center;padding:9px 6px;font-size:13px}}
/* placeholders de imagen */
.ph{position:relative;display:flex;align-items:center;justify-content:center;text-align:center;padding:16px;border-radius:18px;background:repeating-linear-gradient(135deg,#eef7ea 0 14px,#e2f1dc 14px 28px);color:var(--mut);font-size:13px;font-weight:600;min-height:160px;overflow:hidden}
.ph span{background:rgba(255,255,255,.85);padding:6px 12px;border-radius:999px}
.ph.img{padding:0;background:#fff;overflow:hidden}
.ph.img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.ph.img.contain{background:var(--g4)}
.ph.img.contain img{object-fit:contain;padding:14%}
.lb .ph.img img{object-fit:contain;background:#fff}
.wheel-center .ph.img.contain img{padding:16% 22% 36%}
.st .ph.img.contain{background:#fff}
.st .ph.img.contain img{padding:4px}
.eq-card .ph.img{aspect-ratio:4/3;min-height:0}
.eq-card .ph.img.contain img{padding:0}
.yape-media .ph.img.contain img{padding:4%}
.status-logos img{height:30px;width:auto;display:block}
.wallet-img img{width:100%;height:auto;display:block;max-height:560px;object-fit:contain}
/* tarjetas */
.card{background:#fff;border-radius:var(--r);padding:28px;box-shadow:0 1px 0 var(--line)}
.chip{display:inline-block;background:#ecfbe3;border-radius:999px;padding:6px 14px;font-size:13px;font-weight:600}
.grid{display:grid;gap:20px}
.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
@media(max-width:900px){.g3,.g4{grid-template-columns:repeat(2,1fr)}}
@media(max-width:620px){.g2,.g3,.g4{grid-template-columns:1fr}section{padding:64px 0}.wrap{padding:0 16px}.hdr{padding:0 16px}}
/* hero */
.hero{padding-top:56px}
.hero-grid{display:grid;grid-template-columns:1.05fr 1fr;gap:48px;align-items:center}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr}}
.hero-ctas{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.hero-ctas .btn{min-width:200px}
.para{margin-top:24px;font-size:13px}
.para b{display:block;font-size:11px;letter-spacing:.08em;margin-bottom:4px}
.wheel-box{position:relative;max-width:520px;margin:0 auto;width:100%}
.wheel{position:relative;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle,#c9efbd 0 42%,#b5e8a6 42% 60%,transparent 60%)}
.wheel-ring{position:absolute;inset:0;border-radius:50%;transition:transform 1.6s cubic-bezier(.3,.8,.2,1)}
.wheel-ring .wn{position:absolute;transform:translate(-50%,-50%);background:#fff;border-radius:999px;padding:8px 14px;font-size:13px;font-weight:700;box-shadow:var(--sh);white-space:nowrap}
.wheel-ring .wn:nth-child(odd){background:var(--y)}
.wheel-center{position:absolute;inset:24%;border-radius:50%;overflow:hidden;display:flex;align-items:center;justify-content:center;background:#fff;box-shadow:var(--sh);flex-direction:column;text-align:center}
.wheel-center .ph{position:absolute;inset:0;border-radius:0;min-height:0}
.wheel-center .brand{position:relative;z-index:1;background:rgba(255,255,255,.9);border-radius:14px;padding:6px 14px;font-weight:800;margin-top:auto;margin-bottom:18%}
.wheel-center .brand small{display:block;font-weight:600;font-size:11px;color:var(--mut)}
.spin-btn{display:flex;margin:12px auto 0}
.status{margin-top:18px;background:#fff;border-radius:20px;padding:18px 20px;box-shadow:var(--sh)}
.status-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;font-weight:700}
.status-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.status-steps div{background:var(--g4);border-radius:12px;padding:10px;font-size:13px;font-weight:600}
.status-steps div small{display:block;color:var(--mut);font-weight:700}
.status-steps div.on{background:#dff5d8}
.status-logos{display:flex;gap:10px;margin-top:12px}
.status-logos span{font-size:12px;font-weight:700;border-radius:8px;padding:5px 10px;background:#ffeef0;color:#d6334a}
.status-logos span+span{background:#fff1e6;color:#e05a00}
/* franja */
.strip{background:var(--g2);padding:28px 0}
.strip ul{list-style:none;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;font-size:14px;font-weight:600}
.strip li b{margin-right:12px}
@media(max-width:760px){.strip ul{grid-template-columns:1fr}}
/* ecosistema */
.eco{background:var(--g)}
.eco-grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:28px;align-items:stretch}
@media(max-width:900px){.eco-grid{grid-template-columns:1fr}}
.eco-left{background:var(--g4);border-radius:28px;padding:36px;display:flex;flex-direction:column}
.note-y{background:var(--y2);border-radius:18px;padding:18px 20px;margin-top:24px}
.note-y b{display:block;font-size:11px;letter-spacing:.08em;margin-bottom:6px}
.plant{margin:28px auto 0;text-align:center}
.plant svg{width:140px;height:140px;transform-origin:50% 100%;transition:transform 1.2s cubic-bezier(.3,1.4,.4,1)}
.plant.small svg{transform:scale(.55)}
.orbit{position:relative;aspect-ratio:1;max-width:560px;width:100%;margin:0 auto}
.orbit::before{content:"";position:absolute;inset:14%;border-radius:50%;border:2px dashed rgba(31,51,40,.25)}
.orbit-c{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);text-align:center;font-weight:800}
.orbit-c .m{font-size:64px;line-height:1;display:block;animation:bob 3s ease-in-out infinite}
.orbit-c small{display:block;font-weight:600;font-size:12px}
.node{position:absolute;transform:translate(-50%,-50%);background:#fff;border-radius:18px;padding:12px 14px;min-width:132px;text-align:left;box-shadow:var(--sh);font-weight:700;font-size:14px;transition:transform .2s}
.node:hover,.node:focus-visible{transform:translate(-50%,-50%) scale(1.05)}
.node small{display:block;font-size:11px;color:var(--mut);font-weight:700}
.node:nth-child(3n+2){background:var(--y2)}.node:nth-child(3n+3){background:#ffd8b8}
.eco-actions{text-align:center;margin-top:12px}
@keyframes bob{50%{transform:translateY(-8px)}}
/* pack */
.pack{background:var(--g)}
.pieces{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:40px}
@media(max-width:900px){.pieces{grid-template-columns:1fr}}
.piece{background:#fff;border-radius:26px;padding:22px;display:flex;flex-direction:column;gap:14px}
.piece-top{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:700;letter-spacing:.06em}
.piece .ph{min-height:260px}
.piece p{font-size:15px;color:var(--mut)}
.wallet p{color:inherit!important}
.wallet{background:#111;color:#fff;border-radius:22px;padding:22px;font-size:13px}
.wallet-top{display:flex;justify-content:space-between;align-items:flex-start}
.wallet-top b{font-size:16px}
.wallet-top small{display:block;font-size:10px;opacity:.7}
.wallet h4{font-size:26px;font-weight:600;margin:16px 0 10px}
.wallet .lbl{font-size:10px;letter-spacing:.06em;opacity:.8}
.stamps{display:flex;gap:8px;margin:10px 0 14px;flex-wrap:wrap}
.stamps i{width:34px;height:34px;border-radius:50%;border:1px solid rgba(255,255,255,.5);display:flex;align-items:center;justify-content:center;font-style:normal;font-size:11px}
.wallet .qr{width:110px;height:110px;margin:16px auto 6px;background:#fff;border-radius:8px;background-image:repeating-linear-gradient(90deg,#111 0 6px,transparent 6px 12px),repeating-linear-gradient(0deg,#111 0 6px,transparent 6px 12px);background-blend-mode:difference}
.wallet .qr-n{text-align:center;font-size:9px;opacity:.7}
.sell{display:flex;gap:12px;background:var(--y2);border-radius:18px;padding:16px}
.sell b{display:block;font-size:12px;color:#b4561c;letter-spacing:.04em}
.loyal{display:grid;grid-template-columns:1.2fr 1fr;gap:20px;margin-top:20px}
@media(max-width:900px){.loyal{grid-template-columns:1fr}}
.loyal .card h3{font-size:26px}
.push{display:grid;gap:12px;margin-top:20px}
.push div{background:#dff5d8;border-radius:16px;padding:16px}
.connect{background:var(--g4);border-radius:22px;padding:22px}
.connect ol{list-style:none;display:grid;gap:10px;margin-top:10px}
.connect li{display:flex;gap:10px;align-items:center;font-weight:600}
.connect li i{width:28px;height:28px;border-radius:8px;background:#d9b3e8;display:inline-flex;align-items:center;justify-content:center;font-style:normal;font-size:13px}
.connect li:nth-child(2) i{background:#f6b0a8}.connect li:nth-child(3) i{background:#bfe0f7}
.validate{background:var(--g4);border-radius:18px;padding:18px;margin-top:14px;font-size:14px}
/* ojo de águila / secciones especiales */
.eagle{background:var(--g)}
.feature{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}
@media(max-width:900px){.feature{grid-template-columns:1fr}}
.feature .ph{min-height:380px;border-radius:28px}
.steps3{display:grid;gap:10px;margin-top:24px}
.steps3 div{background:#fff;border-radius:14px;padding:16px 18px;font-weight:600;display:flex;gap:14px}
.steps3 b{color:#c43a5a;font-size:13px}
.special{background:var(--y)}
/* así funciona */
.map{background:var(--g2)}
.map-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin:28px 0 14px}
.stations{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
@media(max-width:760px){.stations{grid-template-columns:1fr}}
.st{background:#fff;border-radius:18px;padding:14px;display:grid;grid-template-columns:auto 64px 1fr;gap:12px;align-items:center}
.st b.n{font-size:18px}
.st .ph{min-height:56px;padding:0;border-radius:12px}
.st h4{font-size:15px}
.st p{font-size:13px;color:var(--mut)}
.stages{margin-top:36px}
.stages ol{list-style:none;display:grid;gap:8px;margin-top:12px}
.stages li{background:rgba(255,255,255,.7);border-radius:14px;padding:12px 16px;font-size:15px}
/* funciones */
.fns{background:var(--g)}
.fn-box{background:var(--g4);border-radius:30px;padding:28px;margin-top:32px}
.fn-tools{display:flex;justify-content:flex-end;gap:8px;margin-bottom:14px}
.tabs{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:24px}
@media(max-width:760px){.tabs{grid-template-columns:repeat(3,1fr)}}
.tab{background:#fff;border-radius:999px;padding:11px 8px;font-size:13px;font-weight:600}
.tab[aria-selected=true]{background:var(--y)}
.fn-panel h3{font-size:30px}
.fn-cards{margin-top:18px}
.fn-card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:22px;display:flex;flex-direction:column;gap:12px;min-height:200px;text-align:left;opacity:0;transform:translateY(14px);animation:rise .45s forwards}
.fn-card:nth-child(2){animation-delay:.07s}.fn-card:nth-child(3){animation-delay:.14s}.fn-card:nth-child(4){animation-delay:.21s}
.fn-card h4{font-size:17px;display:flex;gap:12px;align-items:center}
.fn-card h4 i{font-style:normal;width:34px;height:34px;border-radius:10px;background:#c9efbd;display:inline-flex;align-items:center;justify-content:center;font-size:17px;flex:none}
.fn-card p{font-size:14px;color:var(--mut);flex:1}
.fn-card .more{font-size:13px;font-weight:700;color:var(--hd)}
.tag-c{font-size:10px;font-weight:700;background:var(--y2);border-radius:999px;padding:2px 8px;margin-left:auto}
@keyframes rise{to{opacity:1;transform:none}}
.fn-nav{display:flex;justify-content:space-between;margin-top:18px}
/* beneficios */
.benefits{background:var(--y)}
.benefit{background:#fff;border-radius:22px;padding:24px}
.benefit i{font-style:normal;width:40px;height:40px;border-radius:10px;display:inline-flex;align-items:center;justify-content:center;background:#e7c6ef;font-size:20px;margin-bottom:16px}
.benefit:nth-child(2) i{background:#f6b0a8}.benefit:nth-child(3) i{background:#e8e2a2}.benefit:nth-child(4) i{background:#bcd6c4}
.benefit p{font-size:14px;color:var(--mut);margin-top:6px}
/* yape */
.yape{background:var(--g)}
.zero{font-size:clamp(110px,16vw,200px);font-weight:800;color:var(--pu);line-height:.9;letter-spacing:-.04em;margin:18px 0 8px}
.yape-steps{background:#fff;border-radius:22px;padding:20px 24px;display:grid;gap:10px;margin:22px 0;font-weight:500}
.yape-media{display:grid;grid-template-columns:1.3fr .8fr;gap:16px;align-items:center}
.yape-media .ph{min-height:360px;border-radius:28px}
.yape-media .ph:last-child{min-height:260px}
/* qubit */
.qubit{background:var(--cr)}
.checks{list-style:none;display:grid;gap:10px;margin:20px 0}
.checks li::before{content:"✓ ";font-weight:700;color:var(--hd)}
.optional{background:var(--y);border-radius:20px;padding:22px;margin:20px 0}
.optional b{display:block;font-size:12px;letter-spacing:.06em;margin-bottom:6px}
.eq-card{background:#fff;border-radius:22px;padding:22px}
.eq-card .ph{min-height:170px;margin-bottom:16px}
.eq-card p{color:var(--mut);font-size:15px;margin-top:6px}
/* precios */
.prices{background:var(--g)}
.plans{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:36px}
.plans.one{grid-template-columns:minmax(0,460px);justify-content:center}
@media(max-width:1000px){.plans{grid-template-columns:repeat(2,1fr)}}
@media(max-width:620px){.plans{grid-template-columns:1fr}}
.plan{background:#fff;border-radius:26px;padding:24px;display:flex;flex-direction:column;gap:12px}
.plan.feat{background:#eaf8e4;outline:3px solid var(--hd)}
.plan .tier{font-size:11px;font-weight:700;letter-spacing:.06em}
.plan h3{font-size:20px}
.plan .d{font-size:14px;color:var(--mut);min-height:42px}
.plan .p{font-size:42px;font-weight:600;letter-spacing:-.02em}
.plan .p small{display:block;font-size:13px;font-weight:600;letter-spacing:0}
.plan .eq{font-size:13px;color:var(--mut)}
.plan ul{list-style:none;display:grid;gap:8px;font-size:14px;margin-top:4px}
.plan ul li::before{content:"✓ ";color:var(--hd);font-weight:700}
.plan .foot{margin-top:auto;font-size:12px;color:var(--mut)}
.price-notes{margin-top:24px;font-size:13px;display:grid;gap:8px;max-width:760px}
/* testimonios / faq */
.testi{background:var(--cr)}
.testi .card{max-width:640px}
.faq{background:var(--g2)}
.faq details{background:#fbfdf9;border-radius:20px;padding:22px 24px;margin-top:12px}
.faq summary{cursor:pointer;font-weight:700;font-size:18px;list-style:none;display:flex;gap:14px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";margin-left:auto;font-size:22px;line-height:1}
.faq details[open] summary::after{content:"–"}
.faq summary small{font-size:12px;color:var(--mut);font-weight:600;padding-top:4px}
.faq details p{margin-top:12px;color:var(--mut)}
/* formulario */
.contact{background:var(--g)}
.contact-grid{display:grid;grid-template-columns:1fr 1.1fr;gap:32px;align-items:start}
@media(max-width:900px){.contact-grid{grid-template-columns:1fr}}
.interest{background:var(--g4);border-radius:18px;padding:18px;margin-top:24px}
.interest b{display:block;font-size:11px;letter-spacing:.06em;margin-bottom:6px}
form.cform{background:#fff;border-radius:26px;padding:28px;display:grid;gap:14px}
.rubro-box{background:#dff5d8;border-radius:14px;padding:12px 16px}
.rubro-box small{display:block;font-size:12px}
.rubro-box b{font-size:16px}
label{display:grid;gap:6px;font-size:14px;font-weight:600}
input,select,textarea{font:inherit;border:1px solid var(--line);background:#fafcf8;border-radius:12px;padding:12px 14px;color:var(--dk);width:100%}
textarea{min-height:96px;resize:vertical}
.fgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:620px){.fgrid{grid-template-columns:1fr}}
.submit{background:#d9f590;border-radius:14px;padding:16px;font-weight:700;text-align:left}
.before{background:#eaf5e5;border-radius:16px;padding:18px;font-size:14px;display:grid;gap:6px}
/* footer */
.ftr{background:var(--g);padding:64px 0 40px;border-top:1px solid rgba(31,51,40,.15)}
.ftr-grid{display:grid;grid-template-columns:1.2fr 2fr;gap:40px}
@media(max-width:760px){.ftr-grid{grid-template-columns:1fr}}
.ftr h5{font-size:12px;letter-spacing:.08em;margin-bottom:12px}
.ftr ul{list-style:none;display:grid;gap:10px}
.ftr a{text-decoration:none}
.ftr a:hover{text-decoration:underline}
.ftr-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
@media(max-width:620px){.ftr-cols{grid-template-columns:1fr 1fr}}
.ftr-bottom{border-top:1px solid rgba(31,51,40,.2);margin-top:40px;padding-top:24px;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;font-size:13px}
.big-brand{font-size:clamp(48px,10vw,120px);font-weight:800;letter-spacing:-.04em;line-height:1;margin-top:32px}
/* capas: modal, drawer, panel, lightbox */
.ov{position:fixed;inset:0;background:rgba(18,30,22,.55);z-index:100;display:none;align-items:center;justify-content:center;padding:16px}
.ov.open{display:flex}
.modal{background:#fff;border-radius:26px;max-width:620px;width:100%;max-height:calc(100vh - 32px);overflow:auto;padding:30px;position:relative}
.x{position:absolute;top:14px;right:14px;width:40px;height:40px;border-radius:50%;background:var(--g4);font-size:20px;line-height:1}
.x:hover{background:var(--g3)}
.drawer-ov{justify-content:flex-end;padding:0}
.drawer{background:#fff;width:min(460px,100%);height:100%;overflow:auto;padding:28px;position:relative;display:flex;flex-direction:column;gap:16px}
.drawer .ptabs{display:flex;gap:6px;flex-wrap:wrap;padding-right:48px}
.drawer .ptabs button{padding:8px 12px;border-radius:999px;background:var(--g4);font-size:12px;font-weight:700}
.drawer .ptabs button.on{background:var(--y)}
.drawer ul{list-style:none;display:grid;gap:10px}
.drawer ul li{padding:10px 12px;background:var(--g4);border-radius:12px;font-size:14px}
.drawer ul li::before{content:"✓ ";color:var(--hd);font-weight:700}
.drawer-nav{display:flex;justify-content:space-between;gap:8px;margin-top:auto;padding-top:12px}
.lb .modal{max-width:760px;display:flex;flex-direction:column;gap:14px}
.lb .ph{min-height:min(52vh,420px)}
.lb-nav{display:flex;justify-content:space-between;align-items:center;gap:8px}
.pend{background:var(--cr);border-radius:14px;padding:14px;font-size:14px}
.summary dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:14px;margin:16px 0}
.summary dt{font-weight:700}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
:focus-visible{outline:3px solid var(--pu);outline-offset:2px}
body.no-motion *,body.no-motion *::before{animation:none!important;transition:none!important}
body.no-motion .fn-card{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.fn-card{opacity:1;transform:none}}
body.lock{overflow:hidden}
body{overflow-x:clip}
@media(max-width:620px){.wheel-box{padding:0 34px}.wheel-ring .wn{font-size:11px;padding:6px 10px}.node{min-width:0;padding:10px;font-size:12px}.orbit-c .m{font-size:44px}}
"""

JS = r"""
(function(){
  var D = /*DATA*/{};
  var root = document.querySelector('.awx-landing');
  if(!root) return;
  var $ = function(s,c){return (c||root).querySelector(s)};
  var $$ = function(s,c){return Array.prototype.slice.call((c||root).querySelectorAll(s))};
  var lastFocus = null;
  function open(ov){ if(!ov) return; lastFocus=document.activeElement; ov.classList.add('open'); root.classList.add('lock'); var f=ov.querySelector('.x'); if(f) f.focus(); }
  function close(ov){ if(!ov) return; ov.classList.remove('open'); if(!$('.ov.open')) root.classList.remove('lock'); if(lastFocus) lastFocus.focus(); }

  // Anclas (#seccion): se resuelven dentro de la capa, sin cambiar la URL del CMS
  $$('a[href^="#"]').forEach(function(a){
    a.addEventListener('click',function(e){
      var h=a.getAttribute('href'); if(!h || h==='#') return;
      e.preventDefault();
      if(h==='#top'){ root.scrollTo({top:0,behavior:'smooth'}); return; }
      var t=root.querySelector(h); if(t) t.scrollIntoView({behavior:'smooth',block:'start'});
    });
  });
  $$('.ov').forEach(function(ov){
    ov.addEventListener('click',function(e){ if(e.target===ov || e.target.closest('[data-close]')) close(ov); });
  });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'){ var o=$$('.ov.open'); if(o.length) close(o[o.length-1]); }
  });

  // Modal de consulta (Solicitar demo / Elegir plan / Contactar)
  var cm = $('#consulta');
  $$('[data-consulta]').forEach(function(b){
    b.addEventListener('click',function(e){
      e.preventDefault();
      var plan = b.getAttribute('data-plan') || '';
      var pl = $('#m-plan'); if(pl){ pl.textContent = plan ? plan : 'Por definir en la demo'; }
      var hp = $('#consulta input[name=plan]'); if(hp){ hp.value = plan; }
      var pd = $('#drawer'); if(pd && pd.classList.contains('open')) close(pd);
      open(cm);
    });
  });

/*FORM*/
  // Rueda del hero
  var ring = $('.wheel-ring'), turns = 0;
  var sb = $('[data-spin]');
  if(sb && ring){ sb.addEventListener('click',function(){ turns+=1; ring.style.transform='rotate('+(turns*360)+'deg)'; $$('.wn',ring).forEach(function(n){n.style.transform='translate(-50%,-50%) rotate('+(-turns*360)+'deg)';}); }); }

  // Planta "Ver crecer"
  var plant = $('.plant');
  var gb = $('[data-grow]');
  if(gb && plant){ gb.addEventListener('click',function(){ plant.classList.add('small'); setTimeout(function(){plant.classList.remove('small')},60); }); }

  // Sin movimiento
  $$('[data-motion]').forEach(function(b){
    b.addEventListener('click',function(){
      var on = root.classList.toggle('no-motion');
      $$('[data-motion]').forEach(function(x){ x.textContent = on ? 'Con movimiento' : 'Sin movimiento'; x.setAttribute('aria-pressed', on); });
    });
  });

  // Nodos del ecosistema
  var np = $('#nodo');
  $$('.node').forEach(function(n){
    n.addEventListener('click',function(){
      var i = +n.getAttribute('data-i'); var d = (D.nodes||[])[i]; if(!d) return;
      $('#nodo-t').textContent = d[0]; $('#nodo-d').textContent = d[1]; $('#nodo-n').textContent = (i<9?'0':'')+(i+1)+' / '+(D.rubro||'');
      open(np);
    });
  });

  // Lightbox del pack
  var lb = $('#lightbox'), li = 0;
  function lbShow(i){ var p = D.pieces||[]; if(!p.length) return; li=(i+p.length)%p.length; $('#lb-t').textContent=p[li][0]; var box=$('#lb-img'); box.innerHTML=''; if(p[li][2]){ var im=document.createElement('img'); im.src=p[li][2]; im.alt=p[li][1]; box.appendChild(im); box.classList.add('img','cover'); } else { var sp=document.createElement('span'); sp.textContent=p[li][1]; box.appendChild(sp); box.classList.remove('img','cover'); } $('#lb-n').textContent='Pieza '+(li+1)+' de '+p.length; }
  $$('[data-piece]').forEach(function(b){ b.addEventListener('click',function(){ lbShow(+b.getAttribute('data-piece')); open(lb); }); });
  $$('[data-lb]').forEach(function(b){ b.addEventListener('click',function(){ lbShow(li + (+b.getAttribute('data-lb'))); }); });

  // Pestañas de funciones
  var tabs = $$('.tab'), cur = 0;
  function showTab(i){
    cur=(i+tabs.length)%tabs.length;
    tabs.forEach(function(t,k){ var on=k===cur; t.setAttribute('aria-selected',on); t.tabIndex=on?0:-1; var p=$('#'+t.getAttribute('aria-controls')); if(p){ p.hidden=!on; if(on){ $$('.fn-card',p).forEach(function(c){ c.style.animation='none'; c.offsetHeight; c.style.animation=''; }); } } });
  }
  tabs.forEach(function(t,k){
    t.addEventListener('click',function(){showTab(k)});
    t.addEventListener('keydown',function(e){ if(e.key==='ArrowRight'){showTab(cur+1);tabs[cur].focus()} if(e.key==='ArrowLeft'){showTab(cur-1);tabs[cur].focus()} });
  });
  $$('[data-tabstep]').forEach(function(b){ b.addEventListener('click',function(){ showTab(cur + (+b.getAttribute('data-tabstep'))); }); });
  var stg = $('[data-stagger]');
  if(stg){ stg.addEventListener('click',function(){ showTab(cur); }); }

  // Detalle de función
  var fm = $('#funcion');
  $$('.fn-card').forEach(function(c){
    c.addEventListener('click',function(){
      $('#fn-t').textContent = c.getAttribute('data-name');
      $('#fn-a').textContent = c.getAttribute('data-tab') + ' · ' + (D.rubro||'');
      $('#fn-d').textContent = c.getAttribute('data-desc');
      open(fm);
    });
  });

  // Panel de planes (Ver más)
  var dr = $('#drawer'), pi = 0;
  function planShow(i){
    var P = D.plans||[]; if(!P.length) return; pi=(i+P.length)%P.length; var p=P[pi];
    $$('#drawer .ptabs button').forEach(function(b,k){ b.classList.toggle('on',k===pi); });
    $('#dr-tier').textContent=p.tier; $('#dr-name').textContent=p.name; $('#dr-desc').textContent=p.desc;
    $('#dr-price').textContent = p.price ? ('S/ '+p.price+' por año · IGV incluido') : 'Cotización personalizada';
    var ul=$('#dr-list'); ul.innerHTML='';
    p.all.forEach(function(x){ var li=document.createElement('li'); li.textContent=x; ul.appendChild(li); });
    $('#dr-count').textContent = p.all.length + ' beneficios';
    $('#dr-choose').setAttribute('data-plan', p.name + (p.price?(' · S/ '+p.price+' al año'):''));
    var prev=P[(pi-1+P.length)%P.length], next=P[(pi+1)%P.length];
    $('#dr-prev').textContent='← '+prev.name; $('#dr-next').textContent=next.name+' →';
    $('#dr-prev').hidden = $('#dr-next').hidden = P.length<2;
  }
  $$('[data-plan-more]').forEach(function(b){ b.addEventListener('click',function(){ planShow(+b.getAttribute('data-plan-more')); open(dr); }); });
  $$('#drawer .ptabs button').forEach(function(b,k){ b.addEventListener('click',function(){planShow(k)}); });
  if($('#dr-prev')){ $('#dr-prev').addEventListener('click',function(){planShow(pi-1)}); $('#dr-next').addEventListener('click',function(){planShow(pi+1)}); }
})();
"""

# ---------- Envío real al endpoint de Apiworking (igual que formulario.html) ----------
FORM_ENDPOINT = "https://api-centralizador.apiworking.pe/api/Administrativo/sendFormContact"
FORM_DEST = ["danielaapiworking@gmail.com", "alo.midocto@gmail.com", "rexlobo45699@gmail.com", "josephchamorrotv@gmail.com"]

FORM_JS = r"""
  // ===== Formulario de contacto: POST al centralizador de Apiworking =====
  var AWX_FORM_ENDPOINT = '__ENDPOINT__';
  var AWX_FORM_DEST = __DEST__;
  var awxIp = '';
  // Campos que tienen su propio lugar en el endpoint; el resto se suma a giroNegocio
  var AWX_OWN = { nombre:1, whatsapp:1, negocio:1, rubro:1 };

  if($('form.cform')){
    fetch('https://api.ipify.org?format=json', { cache: 'no-store' })
      .then(function(r){ return r.json(); })
      .then(function(d){ awxIp = d && d.ip ? d.ip : ''; })
      .catch(function(){ awxIp = ''; });
  }

  function awxBadges(f, items, type){
    var box = $('.awx-badges', f); if(!box) return;
    box.innerHTML = '';
    items.forEach(function(t){ var s=document.createElement('span'); s.className=type; s.textContent=t; box.appendChild(s); });
  }
  function awxVal(f, name){ var el=f.querySelector('[name="'+name+'"]'); return el ? String(el.value||'').trim() : ''; }

  $$('input[name=whatsapp]').forEach(function(t){
    t.addEventListener('input',function(){ this.value = this.value.replace(/\D/g,''); });
  });

  $$('form.cform').forEach(function(f){
    var btn = $('[data-send]', f);
    if(!btn) return;
    var txt = $('.awx-txt', btn), ico = $('.awx-ico', btn), label = txt ? txt.textContent : '';
    function send(){
      var nombre = awxVal(f,'nombre'), tel = awxVal(f,'whatsapp'), negocio = awxVal(f,'negocio'), rubro = awxVal(f,'rubro');
      var warn = [];
      if(!nombre) warn.push('Falta tu nombre');
      if(!tel || tel.length < 7) warn.push('WhatsApp inválido');
      if(!negocio) warn.push('Falta el nombre del negocio');
      if(!rubro) warn.push('Selecciona el rubro');
      if(warn.length){ awxBadges(f, warn, 'warn'); return; }

      // giroNegocio: rubro + datos extra (plan, locales, necesidad...) para que lleguen en el correo
      var extra = [];
      $$('input,select,textarea', f).forEach(function(i){
        if(!i.name || AWX_OWN[i.name]) return;
        var v = String(i.value||'').trim(); if(!v) return;
        extra.push((i.getAttribute('data-label')||i.name) + ': ' + v);
      });
      var giro = rubro.toUpperCase() + (extra.length ? ' | ' + extra.join(' | ') : '');

      var body = JSON.stringify({
        nombreCompleto: nombre,
        telefono: tel,
        nombreNegocio: negocio,
        giroNegocio: giro,
        ipCreacion: awxIp || '0.0.0.0',
        destinatarios: AWX_FORM_DEST
      });

      btn.disabled = true;
      if(txt) txt.textContent = 'Enviando...';
      if(ico) ico.innerHTML = '<span class="awx-spin" aria-hidden="true"></span>';
      awxBadges(f, [], 'ok');

      fetch(AWX_FORM_ENDPOINT, {
        method: 'POST',
        headers: { 'accept': 'text/plain', 'Content-Type': 'application/json' },
        body: body,
        redirect: 'follow'
      })
        .then(function(r){ if(!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
        .then(function(){
          var dl = $('#sum-list');
          if(dl){
            dl.innerHTML = '';
            $$('input,select,textarea', f).forEach(function(i){
              if(!i.name) return; var v = String(i.value||'').trim(); if(!v) return;
              var dt=document.createElement('dt'); dt.textContent=i.getAttribute('data-label')||i.name;
              var dd=document.createElement('dd'); dd.textContent=v;
              dl.appendChild(dt); dl.appendChild(dd);
            });
          }
          f.reset();
          awxBadges(f, ['¡Enviado! Te contactaremos pronto.'], 'ok');
          if(cm && cm.classList.contains('open')) close(cm);
          open($('#resumen'));
        })
        .catch(function(){ awxBadges(f, ['Error al enviar. Intenta nuevamente.'], 'err'); })
        .then(function(){
          btn.disabled = false;
          if(txt) txt.textContent = label;
          if(ico) ico.innerHTML = '';
        });
    }
    btn.addEventListener('click', send);
    f.addEventListener('submit', function(e){ e.preventDefault(); send(); });
  });
""".replace("__ENDPOINT__", FORM_ENDPOINT).replace("__DEST__", "[" + ",".join("'" + d + "'" for d in FORM_DEST) + "]")

SEND_BTN = '<button class="submit" type="button" data-send><span class="awx-ico" aria-hidden="true"></span><span class="awx-txt">Enviar consulta</span></button>\n<div class="awx-badges" aria-live="polite"></div>'

# ---------- Técnicas de formulario.html (guía Apiworking) ----------
# 1) Todo vive dentro de <div class="awx-overlay awx-landing">: una capa fija a pantalla
#    completa (z-index 9999) que se sobrepone al contenedor HTML del CMS y hace su propio scroll.
# 2) Todo el CSS va con el prefijo .awx-landing para ganarle a los estilos del CMS y no afectarlo.
# 3) Se anulan los ::before/::after "clearfix" que el CMS pone a .wrap/.container.
# 4) Clases que chocan con Bootstrap (.modal, .lead) se renombran con prefijo awx-.
# 5) Sin entidades HTML (&nbsp; etc.), sin globales en window y JS ES5 (var/function).
# 6) Los enlaces #ancla se resuelven por JS (scrollIntoView) dentro de la capa.
SCOPE = ".awx-landing"
RENAME = ("modal", "lead")

def _scope_sel(s):
    s = s.strip()
    if s == ":root": return SCOPE
    if s == "html": return ".awx-overlay"
    if s.startswith("body.lock"): return ".awx-overlay.lock" + s[len("body.lock"):]
    if s.startswith("body."): return SCOPE + s[4:]
    if s == "body": return SCOPE
    if s.startswith("body "): return SCOPE + s[4:]
    return SCOPE + " " + s

def _split_top(css):
    """Devuelve [(prelude, contenido)] de nivel superior."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0: break
        pre = css[i:j].strip()
        depth, k = 1, j + 1
        while depth and k < n:
            if css[k] == "{": depth += 1
            elif css[k] == "}": depth -= 1
            k += 1
        out.append((pre, css[j + 1:k - 1]))
        i = k
    return out

def scope_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    res = []
    for pre, body in _split_top(css):
        if pre.startswith("@media") or pre.startswith("@supports"):
            res.append(pre + "{" + scope_css(body) + "}")
        elif pre.startswith("@"):
            res.append(pre + "{" + body + "}")
        else:
            sels = ",".join(_scope_sel(x) for x in pre.split(","))
            res.append(sels + "{" + body.strip() + "}")
    return "\n".join(res)

BASE_CSS = """.awx-overlay{position:fixed;inset:0;z-index:9999;overflow:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;scroll-behavior:smooth}
.awx-landing .wrap::before,.awx-landing .wrap::after,.awx-landing .hdr-in::before,.awx-landing .hdr-in::after{content:none!important;display:none!important}
.awx-landing .awx-badges{display:flex;gap:8px;flex-wrap:wrap}
.awx-landing .awx-badges span{display:inline-flex;padding:7px 12px;border-radius:999px;font-size:13px;font-weight:700}
.awx-landing .awx-badges .ok{background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0}
.awx-landing .awx-badges .warn{background:#fff7ed;color:#9a3412;border:1px solid #fed7aa}
.awx-landing .awx-badges .err{background:#fef2f2;color:#991b1b;border:1px solid #fecaca}
.awx-landing .awx-spin{width:16px;height:16px;border:2px solid rgba(255,255,255,.45);border-top-color:#fff;border-radius:50%;display:inline-block;animation:awxSpin .75s linear infinite}
.awx-landing .submit[disabled]{opacity:.7;cursor:wait}
@keyframes awxSpin{to{transform:rotate(360deg)}}"""

def _rename_classes(html_body, css):
    for c in RENAME:
        css = re.sub(r"\.%s(?![\w-])" % c, ".awx-" + c, css)
    def fix(m):
        toks = ["awx-" + t if t in RENAME else t for t in m.group(1).split()]
        return 'class="' + " ".join(toks) + '"'
    return re.sub(r'class="([^"]*)"', fix, html_body), css

def page(title, desc, body, data_js, extra_css=""):
    body = body.replace("&nbsp;", " ")
    body, css = _rename_classes(body, CSS + extra_css)
    css = scope_css(css) + "\n" + BASE_CSS
    js = JS.replace("/*DATA*/{}", data_js, 1).replace("/*FORM*/", FORM_JS, 1)
    assert "&nbsp;" not in body and "window.PAGE" not in js
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{FONT}
<style>
{css}
</style>
</head>
<body>
<div class="awx-overlay awx-landing" lang="es" role="document" aria-label="{esc(title)}">
{body}
<script>
{js}
</script>
</div>
</body>
</html>
"""

def jstr(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('</', '<\\/') + '"'

def jlist(items):
    return "[" + ",".join(items) + "]"

USED_PH = set()
CUR = {"page": None}

def _ph_lookup(label):
    m = PH_IMG_PAGE.get(CUR["page"], {}).get(label)
    if m:
        USED_PH.add((CUR["page"], label)); return m
    m = PH_IMG.get(label)
    if m: USED_PH.add(label)
    return m

def ph_url(label):
    m = _ph_lookup(label)
    return IMG[m[0]] if m else ""

def ph(label, cls="", key=None, fit="contain"):
    m = (key, fit) if key else _ph_lookup(label)
    if m:
        key, fit = m
        return f'<div class="ph img {fit} {cls}"><img src="{IMG[key]}" alt="{esc(label)}" loading="lazy" decoding="async"></div>'
    return f'<div class="ph {cls}" role="img" aria-label="{esc(label)}"><span>{esc(label)}</span></div>'

def href(k):
    r = ROUTES[k].strip("/")
    return BASE_URL + "/" + (r + "/" if r else "")

PLANT = '''<svg viewBox="0 0 120 120" aria-hidden="true"><path d="M60 112V44" stroke="#5a8f3c" stroke-width="4" fill="none"/><ellipse cx="44" cy="62" rx="16" ry="7" fill="#8cc56b" transform="rotate(-30 44 62)"/><ellipse cx="76" cy="56" rx="16" ry="7" fill="#8cc56b" transform="rotate(30 76 56)"/><ellipse cx="46" cy="40" rx="13" ry="6" fill="#a7d58a" transform="rotate(-35 46 40)"/><ellipse cx="74" cy="34" rx="13" ry="6" fill="#a7d58a" transform="rotate(35 74 34)"/><ellipse cx="60" cy="20" rx="7" ry="12" fill="#b9e19f"/><circle cx="60" cy="16" r="4" fill="#f4c35b"/><ellipse cx="60" cy="112" rx="26" ry="5" fill="#d9b98a"/></svg>'''

# ---------------- piezas comunes ----------------
def header_rubro(k):
    return f'''<header class="hdr"><div class="hdr-in">
<a class="logo" href="{href("inicio")}">apiworking</a>
<nav class="nav" aria-label="Secciones"><a href="#como-funciona">Cómo funciona</a><a href="#precios">Precios</a><a href="#testimonios">Testimonios</a></nav>
<button class="btn btn-y btn-sm" data-consulta>Agendar demo</button>
</div></header>'''

def footer(current=None, closing=None):
    cols = ""
    for g, keys in GROUPS:
        lis = "".join(f'<li><a href="{href(k)}"{" aria-current=page" if k==current else ""}>{esc(NAMES[k])} →</a></li>' for k in keys)
        cols += f'<div><h5>{g.upper()}</h5><ul>{lis}</ul></div>'
    tag = closing or "Módulos, equipos, integraciones y condiciones sujetos a confirmación comercial."
    who = f"Apiworking · Soluciones para {NAMES[current]}" if current else "Apiworking"
    return f'''<footer class="ftr"><div class="wrap">
<div class="ftr-grid"><div><h3>Hecho para tu negocio. Pensado para que vuelvan.</h3><p class="small" style="margin-top:10px">Venta, operación, atención y fidelidad. Un ecosistema. Tu forma de trabajar.</p><p style="margin-top:18px"><a class="btn btn-w btn-sm" href="{href("inicio")}">Ir al inicio</a></p></div>
<div class="ftr-cols">{cols}</div></div>
<div class="big-brand">APIWORKING</div>
<div class="ftr-bottom"><div><b>{esc(who)}</b><br>{esc(tag)}</div><a href="#top">Volver arriba ↑</a></div>
</div></footer>'''

def overlays(rubro_name, rubro_key=None, plans=None):
    # modal consulta
    opts = "".join(f'<option{" selected" if k==rubro_key else ""}>{esc(NAMES[k])}</option>' for k in ORDER)
    form_fields = f'''
<label>Rubro<select name="rubro" data-label="Rubro">{opts}</select></label>
<div class="fgrid"><label>Nombre<input name="nombre" data-label="Nombre" placeholder="Tu nombre" autocomplete="name"></label>
<label>WhatsApp<input name="whatsapp" data-label="WhatsApp" placeholder="9XX XXX XXX" inputmode="tel" autocomplete="tel"></label></div>
<div class="fgrid"><label>Negocio<input name="negocio" data-label="Negocio" placeholder="Nombre de tu negocio"></label>
<label>Locales<select name="locales" data-label="Locales"><option>1 local</option><option>2 locales</option><option>3 o más locales</option></select></label></div>
<label>Necesidad<textarea name="necesidad" data-label="Necesidad" placeholder="Cuéntanos qué te gustaría revisar"></textarea></label>
<input type="hidden" name="plan" data-label="Plan" value="">'''
    drawer = ""
    if plans:
        btns = "".join(f'<button type="button">{esc(p["name"])}</button>' for p in plans)
        drawer = f'''<div class="ov drawer-ov" id="drawer" role="dialog" aria-modal="true" aria-labelledby="dr-name"><div class="drawer">
<button class="x" data-close aria-label="Cerrar">×</button>
<div class="ptabs">{btns}</div>
<div><div class="eyebrow" id="dr-tier"></div><h2 id="dr-name" style="font-size:30px"></h2><p class="small" id="dr-desc" style="margin-top:6px"></p><p style="margin-top:10px;font-weight:700" id="dr-price"></p></div>
<p class="small"><b id="dr-count"></b> incluidos</p>
<ul id="dr-list"></ul>
<button class="btn btn-g btn-block" id="dr-choose" data-consulta>Elegir este plan</button>
<div class="drawer-nav"><button class="btn btn-w btn-sm" id="dr-prev"></button><button class="btn btn-w btn-sm" id="dr-next"></button></div>
</div></div>'''
    return f'''
<div class="ov" id="consulta" role="dialog" aria-modal="true" aria-labelledby="c-t"><div class="modal">
<button class="x" data-close aria-label="Cerrar">×</button>
<div class="eyebrow">{esc(rubro_name.upper())} · CONSULTA</div>
<h2 id="c-t" style="font-size:32px">Tu próximo paso, más simple.</h2>
<p class="small" style="margin-top:8px">Plan de interés: <b id="m-plan">Por definir en la demo</b></p>
<form class="cform" style="padding:20px 0 0" novalidate onsubmit="return false;">{form_fields}
{SEND_BTN}
<p class="small">Un asesor te contactará por WhatsApp para coordinar la demo.</p></form>
</div></div>
<div class="ov summary" id="resumen" role="dialog" aria-modal="true" aria-labelledby="r-t"><div class="modal">
<button class="x" data-close aria-label="Cerrar">×</button>
<div class="eyebrow">CONSULTA ENVIADA</div>
<h2 id="r-t" style="font-size:32px">Recibimos tu consulta.</h2>
<dl id="sum-list"></dl>
<div class="pend">Un asesor de Apiworking te escribirá pronto por WhatsApp para coordinar tu demo.</div>
<button class="btn btn-dk btn-block" data-close style="margin-top:16px">Cerrar</button>
</div></div>
<div class="ov" id="funcion" role="dialog" aria-modal="true" aria-labelledby="fn-t"><div class="modal">
<button class="x" data-close aria-label="Cerrar">×</button>
<div class="eyebrow">EXPLORADOR DE FUNCIONES</div>
<p class="small" id="fn-a"></p>
<h2 id="fn-t" style="font-size:30px;margin-top:6px"></h2>
<p id="fn-d" style="margin-top:12px;color:var(--mut)"></p>
{ph("Video demostrativo pendiente de enlace")}
<div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap"><button class="btn btn-y" data-consulta>Consultar en la demo</button><button class="btn btn-w" data-close>Volver</button></div>
</div></div>
<div class="ov" id="nodo" role="dialog" aria-modal="true" aria-labelledby="nodo-t"><div class="modal">
<button class="x" data-close aria-label="Cerrar">×</button>
<div class="eyebrow" id="nodo-n"></div>
<h2 id="nodo-t" style="font-size:30px"></h2>
<p id="nodo-d" style="margin-top:12px;color:var(--mut)"></p>
<p class="small" style="margin-top:14px">La configuración y el alcance se confirman en la demostración.</p>
</div></div>
<div class="ov lb" id="lightbox" role="dialog" aria-modal="true" aria-labelledby="lb-t"><div class="modal">
<button class="x" data-close aria-label="Cerrar">×</button>
<h3 id="lb-t" style="padding-right:48px"></h3>
<div class="ph" id="lb-img" role="img"><span></span></div>
<div class="lb-nav"><button class="btn btn-w btn-sm" data-lb="-1">← Anterior</button><span class="small" id="lb-n"></span><button class="btn btn-w btn-sm" data-lb="1">Siguiente →</button></div>
</div></div>
{drawer}'''

# ---------------- página de rubro ----------------
def rubro_page(k):
    CUR["page"] = k
    d = R[k]; name = NAMES[k]; m = MASCOT[k]
    no_pay = d.get("no_payments")
    # hero wheel
    wn = ""
    for i, w in enumerate(d["wheel"]):
        a = i / len(d["wheel"]) * 2 * math.pi
        x = 50 + 44 * math.sin(a); y = 50 - 44 * math.cos(a)
        wn += f'<span class="wn" style="left:{x:.1f}%;top:{y:.1f}%">{esc(w)}</span>'
    hc_t, hc_s = d["hero_card"]
    steps = "".join(f'<div class="{"on" if i==1 else ""}"><small>0{i+1}</small>{esc(s)}</div>' for i, s in enumerate(hc_s))
    logos = ('<div class="status-logos" aria-label="Integraciones de delivery por confirmar">'
             + "".join(f'<img src="{IMG[key]}" alt="{esc(nm)}" loading="lazy" decoding="async">' for key, nm in DELIVERY_LOGOS)
             + '</div>') if d.get("delivery") else ""
    hero = f'''<section class="hero" id="top"><div class="wrap hero-grid">
<div>
<div class="eyebrow">SOLUCIONES / {esc(name.upper())}</div>
<span class="chip">{esc(name)}</span>
<h1 style="margin-top:18px">{esc(d["title"])}</h1>
<p class="lead">{esc(d["sub"])}</p>
<div class="hero-ctas"><button class="btn btn-y" data-consulta>Solicitar demo ↗</button><a class="btn btn-w" href="#precios">Ver precios</a></div>
<p class="para"><b>PENSADO PARA</b>{esc(d["para"])}</p>
<p style="margin-top:14px"><a class="btn-ghost" href="#funciones">Explorar funciones</a></p>
</div>
<div class="wheel-box">
<div class="wheel"><div class="wheel-ring">{wn}</div>
<div class="wheel-center">{ph("Foto del rubro: " + name)}<div class="brand">apiworking<small>{esc(name)}</small></div></div></div>
<button class="btn btn-w btn-sm spin-btn" data-spin>Ver giro</button>
<div class="status"><div class="status-top"><span>{esc(hc_t)}</span><span class="small">Vista ilustrativa</span></div><div class="status-steps">{steps}</div>{logos}</div>
</div></div></section>
<div class="strip"><div class="wrap"><ul><li><b>01</b>Especializado en tu rubro</li><li><b>02</b>Operación + atención + recompra</li><li><b>03</b>Configuración revisada en la demo</li></ul></div></div>'''

    # ecosistema
    nodes = ""
    n = len(d["eco_nodes"])
    for i, (nm, _) in enumerate(d["eco_nodes"]):
        a = i / n * 2 * math.pi
        x = 50 + 36 * math.sin(a); y = 50 - 36 * math.cos(a)
        nodes += f'<button class="node" data-i="{i}" style="left:{x:.1f}%;top:{y:.1f}%"><small>0{i+1} ↗</small>{esc(nm)}</button>'
    eco = f'''<section class="eco" id="ecosistema"><div class="wrap eco-grid">
<div class="eco-left"><div class="eyebrow">ECOSISTEMA / {esc(name.upper())}</div><h2>{esc(d["eco_title"])}</h2><p class="lead">Explora cada conexión.</p>
<div class="note-y"><b>{esc(d.get("eco_service_label","DEL SERVICIO A LA PRÓXIMA VISITA"))}</b>{esc(d["eco_service"])}</div>
<div class="plant">{PLANT}<br><button class="btn btn-w btn-sm" data-grow>Ver crecer</button></div></div>
<div><div class="orbit">{nodes}<div class="orbit-c"><span class="m" aria-hidden="true">{m}</span>apiworking<small>{esc(name)}</small></div></div>
<div class="eco-actions"><button class="btn btn-w btn-sm" data-motion aria-pressed="false">Sin movimiento</button></div></div>
</div></section>'''

    # pack
    w = d["wallet"]
    if w["stamps"]:
        stamps = "".join(f"<i>0{i+1}</i>" for i in range(w["stamps"]))
    else:
        stamps = '<i style="width:auto;padding:0 12px;border-radius:999px">30 pts</i>'
    wand_t, wand_img = d["wand"]
    wand_text = d.get("wand_text", "Permite acumular puntos o estampillas en segundos. El vendedor acerca la varita al celular del cliente para registrar sus recompensas y motivarlo a regresar.")
    wand_use = d.get("wand_use", "Acerca la varita al celular, abre la experiencia de fidelización y registra los puntos o estampillas correspondientes a su compra.")
    wand_note = f'<p class="small">{esc(d["wand_note"])}</p>' if d.get("wand_note") else ""
    pack_label = d.get("pack_label", "03 / TARJETA DE FIDELIDAD TIPO WALLET")
    validate = ""
    if d.get("validate"):
        vl, vt = d["validate"]
        validate = f'<div class="validate"><b>{esc(vl)}:</b> {esc(vt)}</div>'
    connect = "".join(f'<li><i aria-hidden="true">{i+1}</i>{esc(c)}</li>' for i, c in enumerate(d["connect"]))
    if WALLET_IMG.get(k):
        wallet_html = f'<div class="wallet-img"><img src="{IMG[WALLET_IMG[k]]}" alt="Tarjeta de fidelidad digital {esc(w["name"])} (ejemplo)" loading="lazy" decoding="async"></div>'
    else:
        wallet_html = f'''<div class="wallet"><div class="wallet-top"><div><b>apiworking</b><small>APILOYALTY</small></div><div style="text-align:right"><small>ESTAMPILLAS</small><small>{esc(w["label"])}</small></div></div>
<h4>{esc(w["name"])}</h4><div class="lbl">{esc(w["goal"])}</div><div class="stamps">{stamps}</div>
<div class="lbl">TU RECOMPENSA</div><p style="margin-top:4px">{esc(w["reward"])}</p>
<div class="qr" aria-hidden="true"></div><div class="qr-n">QR DE EJEMPLO · NO CANJEABLE</div></div>'''
    pack = f'''<section class="pack" id="pack"><div class="wrap">
<div class="eyebrow">EL PACK QUE HACE QUE VUELVAN · TOCA UNA PIEZA PARA AMPLIAR</div>
<h2>Tres piezas.<br>Una experiencia para volver.</h2>
<div class="pieces">
<article class="piece"><div class="piece-top"><span>01 / VARITA MÁGICA NFC</span><button class="btn btn-w btn-sm" data-piece="0">Ampliar ↗</button></div>
{ph(wand_img)}<h3>{esc(wand_t)}</h3><p>{esc(wand_text)}</p><p>Cómo usarla: {esc(wand_use)}</p>{wand_note}</article>
<article class="piece"><div class="piece-top"><span>02 / CLUB DE FIDELIDAD NFC</span><button class="btn btn-w btn-sm" data-piece="1">Ampliar ↗</button></div>
{ph("Letrero NFC «Club de Fidelidad» sobre el mostrador")}<h3>NFC Club de Fidelidad — ¡Convierte visitantes en clientes frecuentes!</h3><p>Permite que tus clientes se unan fácilmente a tu club de fidelidad, descubran sus premios y regresen por más beneficios.</p><p>Cómo usarlo: el cliente acerca su celular al letrero NFC, se registra en el club y accede a su tarjeta digital para consultar sus puntos, estampillas y recompensas.</p></article>
<article class="piece"><div class="piece-top"><span>{esc(pack_label)}</span><button class="btn btn-w btn-sm" data-piece="2">Ampliar ↗</button></div>
{wallet_html}
<div class="sell"><span aria-hidden="true" style="font-size:26px">🏅</span><div><b>PARA VENDER MÁS</b>{esc(w["sell"])}</div></div>
<button class="btn btn-dk btn-block" data-piece="2">Ver tarjeta ampliada ↗</button>
<p class="small">Diseño de ejemplo. No añade ni descarga todavía un pase de Apple Wallet.</p></article>
</div>
<div class="loyal">
<div class="card"><h3>Convierte cada compra en puntos, estampillas y premios con una tarjeta digital en Apple Wallet o Google Wallet.</h3>
<h3 style="margin-top:18px">¡Tu negocio siempre presente!</h3>
<div class="push"><div><b>Push</b><br>Envía promociones y novedades directamente a tus clientes.</div><div><b>GeoPush</b><br>Recuérdales tus ofertas cuando estén cerca de tu negocio.</div></div>
<h3 style="margin-top:18px">¡Más visitas, más recompras y más ventas!</h3><p class="small" style="margin-top:8px">Notificaciones sujetas a compatibilidad y permisos del dispositivo.</p></div>
<div><p class="small" style="margin-bottom:14px">Artes referenciales y diseños personalizables. Club de Fidelidad digital incluido en las anualidades comerciales; las piezas NFC físicas se contratan aparte. Ejemplos configurables: ajustar premios, condiciones y márgenes antes de publicar.</p>
<button class="btn btn-y btn-block" data-consulta>Quiero este pack para mi negocio ↗</button>
<div class="connect" style="margin-top:14px"><div class="eyebrow" style="margin:0">ASÍ SE CONECTA</div><ol>{connect}</ol></div>{validate}</div>
</div></div></section>'''

    pieces_js = jlist([
        "[" + jstr(wand_t) + "," + jstr(wand_img) + "," + jstr(ph_url(wand_img)) + "]",
        "[" + jstr("NFC Club de Fidelidad") + "," + jstr("Letrero NFC «Club de Fidelidad» sobre el mostrador") + "," + jstr(ph_url("Letrero NFC «Club de Fidelidad» sobre el mostrador")) + "]",
        "[" + jstr("Tarjeta Wallet · " + w["name"]) + "," + jstr("Tarjeta de fidelidad digital " + w["name"] + " (ejemplo)") + "," + jstr(IMG[WALLET_IMG[k]] if WALLET_IMG.get(k) else "") + "]",
    ])

    # secciones especiales
    special = ""
    if d.get("eagle"):
        what = "habitación" if k == "hoteles" else "mesa"
        special += f'''<section class="eagle" id="ojo-de-aguila"><div class="wrap feature">
{ph("Punto QR/NFC Ojo de Águila en la " + what)}
<div><div class="eyebrow">ATENCIÓN CONECTADA / {esc(name.upper())}</div><h2>Tu {what} pide atención. Tu equipo responde.</h2>
<p class="lead">Ojo de Águila: un punto de contacto QR/NFC para ver la carta, llamar {"al personal" if k=="hoteles" else "al mozo"} y solicitar la cuenta o precuenta desde la {what}.</p>
<div class="steps3"><div><b>01</b>Ver carta</div><div><b>02</b>{"Llamar al personal" if k=="hoteles" else "Llamar al mozo"}</div><div><b>03</b>Pedir cuenta / Precuenta</div></div>
<p class="small" style="margin-top:14px">La configuración y el alcance se confirman en la demostración.</p></div></div></section>'''
    if d.get("scale"):
        special += f'''<section class="special" id="balanza"><div class="wrap feature">
<div><div class="eyebrow">VENTA POR PESO / MINIMARKETS</div><h2>El peso entra.<br>La venta continúa.</h2>
<p class="lead" style="color:var(--dk)">Conecta una balanza compatible para incorporar el peso, calcular el precio y continuar el cobro desde Apiworking.</p>
<div class="steps3"><div><b>01</b>Captura del peso</div><div><b>02</b>Precio por kilogramo</div><div><b>03</b>Total de la venta</div></div></div>
<div>{ph("Integración con balanza en caja")}<p class="small" style="margin-top:8px">Integración con balanza · Equipo y compatibilidad por confirmar.</p></div></div></section>'''
    if d.get("review"):
        special += f'''<section class="special" id="apireview"><div class="wrap feature">
<div>{ph("ApiReview en la entrega del vehículo")}<p class="small" style="margin-top:8px">Ilustración de uso de ApiReview · No representa una valoración real.</p></div>
<div><div class="eyebrow">CONFIANZA POSVENTA / TALLERES MECÁNICOS</div><h2>Un buen trabajo merece ser compartido.</h2>
<p class="lead" style="color:var(--dk)">ApiReview acerca la reseña al momento de la entrega. Invita al cliente a compartir su experiencia en Google con un punto de contacto QR/NFC.</p>
<div class="steps3"><div><b>01</b>Entrega del vehículo</div><div><b>02</b>Acercar celular / QR</div><div><b>03</b>Compartir experiencia</div></div></div></div></section>'''
    if d.get("zkteco"):
        special += f'''<section class="special" id="zkteco"><div class="wrap">
<div class="eyebrow">DOS FORMAS DE MARCAR. UNA ASISTENCIA CONECTADA.</div><h2>Tu equipo marca.<br>Tu negocio tiene claridad.</h2>
<div class="grid g2" style="margin-top:32px">
<div class="card"><div class="ph" style="min-height:90px" role="img" aria-label="Logo ZKTeco"><span>Logo ZKTeco</span></div><h3 style="margin-top:16px">Asistencia integrada a ZKTeco</h3><p class="small" style="margin-top:8px;font-size:15px">Conecta el control de asistencia con equipos ZKTeco compatibles y reúne la información de marcaciones para la gestión del personal.</p>
<div class="steps3"><div style="background:var(--g4)"><b>01</b>Equipo ZKTeco compatible</div><div style="background:var(--g4)"><b>02</b>Integración con tu asistencia</div><div style="background:var(--g4)"><b>03</b>Marcaciones centralizadas</div></div></div>
<div class="card"><div class="ph" style="min-height:90px" role="img" aria-label="Fotocheck NFC"><span>Fotocheck NFC</span></div><h3 style="margin-top:16px">Fotocheck / identificación NFC</h3><p class="small" style="margin-top:8px;font-size:15px">El colaborador acerca su fotocheck NFC para registrar su ingreso y salida sin registros manuales.</p>
<div class="steps3"><div style="background:var(--g4)"><b>01</b>Fotocheck del colaborador</div><div style="background:var(--g4)"><b>02</b>Lectura NFC</div><div style="background:var(--g4)"><b>03</b>Marcación registrada</div></div></div>
</div><p class="small" style="margin-top:14px;color:var(--dk)">Equipos, compatibilidad y alcance se confirman en la demostración.</p></div></section>'''

    # así funciona
    icons = STATION_ICONS.get(k, [])
    sts = "".join(f'<div class="st"><b class="n">{i+1:02d}</b>{ph("Ícono " + t, key=(icons[i] if i < len(icons) else None))}<div><h4>{esc(t)}</h4><p>{esc(s)}</p></div></div>' for i, (t, s) in enumerate(d["stations"]))
    stg = "".join(f"<li>{esc(s)}</li>" for s in d["stages"])
    mapa = f'''<section class="map" id="como-funciona"><div class="wrap">
<div class="eyebrow">ASÍ FUNCIONA / {esc(name.upper())}</div><h2 class="hd">{esc(d["map_title"])}</h2>
<div class="map-head"><div><div class="eyebrow" style="margin:0">MAPA VIVO / {esc(name.upper())}</div><p class="small">{len(d["stations"])} estaciones conectadas</p></div><span style="font-size:34px" aria-hidden="true">{m}</span></div>
<div class="stations">{sts}</div>
<div class="stages"><div class="eyebrow" style="margin:0">EL RECORRIDO, EN CINCO ETAPAS</div><ol>{stg}</ol><p class="small" style="margin-top:12px">{esc(d["stage_note"])}</p></div>
</div></section>'''

    # funciones
    tabs = ""; panels = ""
    icons = {"Producción": "📋", "Logística": "📦", "Administración": "🧾", "Atención": "🙋", "Crecimiento": "🏅", "Conexiones": "🔗"}
    total = 0
    for i, t in enumerate(TABS):
        tid = f"tab-{i}"; pid = f"panel-{i}"
        tabs += f'<button class="tab" role="tab" id="{tid}" aria-controls="{pid}" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}">{t}</button>'
        cards = ""
        for (fnm, fd) in d["functions"][t]:
            total += 1
            tag = '<span class="tag-c">CONSULTAR</span>' if "(consultar)" in fnm else ""
            clean = fnm.replace(" (consultar)", "")
            cards += f'<button class="fn-card" data-name="{esc(clean)}" data-tab="{t}" data-desc="{esc(fd)}"><h4><i aria-hidden="true">{icons[t]}</i>{esc(clean)}{tag}</h4><p>{esc(fd)}</p><span class="more">Ver detalle →</span></button>'
        panels += f'<div class="fn-panel" role="tabpanel" id="{pid}" aria-labelledby="{tid}"{"" if i==0 else " hidden"}><h3>{t}</h3><p class="small">Toca una función para ver su detalle y alcance.</p><div class="grid g2 fn-cards">{cards}</div></div>'
    funcs = f'''<section class="fns" id="funciones"><div class="wrap">
<div class="eyebrow">EXPLORA / {esc(name.upper())} / {total} FUNCIONES</div><h2>Todo lo que tu operación necesita.</h2>
<p class="lead" style="color:var(--dk)">Elige un área y explora sus funciones. Entrada escalonada breve, respuesta al mouse y alternativa sin movimiento.</p>
<div class="fn-box"><div class="fn-tools"><button class="btn btn-w btn-sm" data-stagger>Ver entrada escalonada</button><button class="btn btn-w btn-sm" data-motion aria-pressed="false">Sin movimiento</button></div>
<div class="tabs" role="tablist" aria-label="Áreas de funciones">{tabs}</div>{panels}
<div class="fn-nav"><button class="btn btn-w btn-sm" data-tabstep="-1">← Anterior</button><button class="btn btn-w btn-sm" data-tabstep="1">Siguiente →</button></div></div>
<div class="validate" style="background:#eef7ea">Las funciones, integraciones y complementos se confirman en la demo y cotización. Las opciones "consultar" requieren validación.</div>
</div></section>'''

    bicons = ["⚡", "🍳", "📊", "💚"]
    bens = "".join(f'<div class="benefit"><i aria-hidden="true">{bicons[i]}</i><h3 style="font-size:19px">{esc(t)}</h3><p>{esc(s)}</p></div>' for i, (t, s) in enumerate(d["benefits"]))
    benefits = f'''<section class="benefits" id="beneficios"><div class="wrap"><div class="eyebrow">BENEFICIOS / {esc(name.upper())}</div><h2>Lo que cambia en tu día.</h2><div class="grid g4" style="margin-top:32px">{bens}</div></div></section>'''

    pay = ""
    if not no_pay:
        qcards = d["qubit_cards"] + [("Reportes impresos", "Consulta e imprime reportes de caja chica, stock y recetas." if k in ("resto", "fastfood") else "Consulta e imprime reportes de caja chica y stock."),
                                     ("Boletas y facturas", "Genera e imprime comprobantes electrónicos según el alcance contratado.")]
        qc = "".join(f'<div class="eq-card">{ph("Pantalla del equipo: " + t)}<h3>{esc(t)}</h3><p>{esc(s)}</p></div>' for t, s in qcards)
        pay = f'''<section class="yape" id="yape"><div class="wrap feature">
<div><div class="eyebrow">COBROS SEGUROS / CONFIRMACIÓN DE YAPE</div><h2>Cada yape, confirmado.</h2>
<div class="zero">0%</div><p style="font-weight:700;font-size:18px">de comisión por la confirmación</p>
<p class="lead" style="color:var(--dk)">No te quedes solo con una captura. Confirma que el dinero ingresó antes de entregar y reduce el riesgo de fraude.</p>
<div class="yape-steps"><div>01&nbsp; Recibe el yape.</div><div>02&nbsp; Confirma la recepción del dinero.</div><div>03&nbsp; Entrega con mayor tranquilidad.</div></div>
<button class="btn btn-y" data-consulta>Quiero confirmar mis yapes ↗</button>
<p class="small" style="margin-top:12px;color:var(--dk)">El 0% corresponde a la confirmación de Yape; no a las comisiones de cobro con tarjeta.</p></div>
<div class="yape-media">{ph("Video: confirmación de Yape en múltiples dispositivos")}{ph("Foto: cajera confirmando un yape")}</div>
</div></section>
<section class="qubit" id="qubit"><div class="wrap">
<div class="feature"><div><div class="eyebrow" style="color:#a0521b">ANDROID INTELIGENTE / QUBIT</div><h2>Tu sistema y tus cobros.<br>Ahora, más cerca.</h2>
<p style="font-size:19px;font-weight:600;margin-top:16px">Gestiona tu operación y cobra con tarjeta o QR desde un equipo compatible.</p>
<ul class="checks"><li>Vincúlalo con tu tablet o computadora.</li><li>Úsalo como caja independiente en eventos o en momentos de alta demanda.</li><li>Si no tienes computadora, puedes trabajar solo con el dispositivo.</li></ul>
<p style="font-weight:700">{esc(d["qubit_bold"])}</p>
<div class="optional"><b>OPCIONAL E INDEPENDIENTE</b>La integración de tu sistema con el Android inteligente de Qubit debe solicitarla el comercio. Es opcional y se contrata de forma independiente al sistema. Equipo, disponibilidad, alcance y condiciones se confirman por separado.</div>
<button class="btn btn-g" data-consulta>Solicitar sistema integrado a medio de pago</button></div>
<div>{ph("Equipo Android Qubit con pago con tarjeta")}<p class="small" style="margin-top:8px">Imagen del equipo y del pago con tarjeta.</p></div></div>
<h2 style="margin-top:64px;font-size:34px">Así se ve en el equipo.</h2>
<div class="grid g3" style="margin-top:24px">{qc}</div>
<p class="small" style="margin-top:18px">Funciones según el rubro, el plan y la configuración. La integración con el medio de pago, el equipo y sus condiciones se confirman en la cotización independiente.</p>
</div></section>'''

    # precios
    plans = d["plans"]
    pc = ""
    for i, p in enumerate(plans):
        price = f'<div class="p">S/ {p["price"]}<small>por año · IGV incluido</small></div><div class="eq">Equivale a S/ {p["month"]}/mes*</div>' if p["price"] else '<div class="p" style="font-size:30px">A medida<small>Cotización personalizada según tu equipo</small></div>'
        ul = "".join(f"<li>{esc(b)}</li>" for b in p["bullets"])
        planlabel = p["name"] + (f' · S/ {p["price"]} al año' if p["price"] else "")
        pc += f'''<article class="plan{" feat" if p.get("featured") else ""}"><div class="tier">{esc(p["tier"])}</div><h3>{esc(p["name"])}</h3><p class="d">{esc(p["desc"])}</p>{price}
<button class="btn btn-g btn-block" data-consulta data-plan="{esc(planlabel)}">Elegir {esc(p["name"])}</button>
<button class="btn-ghost" data-consulta>Pedir demo ↗</button>
<button class="btn btn-w btn-block" data-plan-more="{i}">VER MÁS +</button>
<ul>{ul}</ul><p class="foot">Alcance y compatibilidad según plan.</p></article>'''
    plans_js = []
    acc = []
    for i, p in enumerate(plans):
        extra = ["Club de Fidelidad digital ApiLoyalty", "Facturación electrónica SUNAT", "Soporte y capacitación inicial", "Reportes de ventas y caja", "Acceso web desde cualquier equipo", "Actualizaciones incluidas"]
        if i == 0 or len(plans) == 1:
            allb = p["bullets"] + extra
        else:
            allb = [f"Todo lo del plan {plans[i-1]['name']}"] + p["bullets"] + acc[: max(0, 14 - len(p["bullets"]))]
            allb = allb[:15]
        acc = (p["bullets"] + acc + extra)
        plans_js.append("{" + f'"tier":{jstr(p["tier"])},"name":{jstr(p["name"])},"desc":{jstr(p["desc"])},"price":{p["price"] or "null"},"all":{jlist([jstr(x) for x in dict.fromkeys(allb)])}' + "}")
    notes = '<p>* El equivalente mensual es solo informativo (anual ÷ 12). No es pago mensual.</p>' if plans[0]["price"] else ""
    precios = f'''<section class="prices" id="precios"><div class="wrap">
<div class="eyebrow">PRECIOS / {esc(name.upper())}</div><h2>Elige lo que necesitas.<br>Crece a tu ritmo.</h2>
<p class="lead" style="color:var(--dk)">{"Un pago anual. IGV incluido. Sin confundir cuotas con equivalentes." if plans[0]["price"] else "Un plan a la medida de tu equipo y tus sedes."}</p>
<div class="plans{" one" if len(plans)==1 else ""}">{pc}</div>
<div class="price-notes">{notes}<p>Club de Fidelidad digital incluido en las anualidades comerciales. Piezas NFC físicas y accesorios se contratan aparte. Funciones e integraciones según compatibilidad, configuración y plan.</p>
<p><button class="btn btn-w" data-consulta>¿Necesitas ayuda? Contactar con un asesor</button></p></div>
</div></section>'''

    testi = f'''<section class="testi" id="testimonios"><div class="wrap">
<div class="eyebrow">TESTIMONIOS / {esc(name.upper())}</div><h2 class="hd">La experiencia de otros</h2>
<div class="card" style="margin-top:28px"><h3 style="font-size:24px">Los testimonios de {esc(name.lower())} se publicarán aquí cuando estén verificados y autorizados.</h3>
<p class="small" style="margin-top:10px;font-size:15px">Mientras tanto, conoce el sistema en una demostración y revisa si encaja con tu operación.</p>
<button class="btn btn-g" style="margin-top:18px" data-consulta>Conocer una demo ↗</button></div></div></section>'''

    faqs = "".join(f'<details><summary><small>{i+1:02d}</small>{esc(q)}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(COMMON_FAQ(name)))
    faq = f'''<section class="faq" id="preguntas"><div class="wrap" style="max-width:860px">
<div class="eyebrow">PREGUNTAS FRECUENTES</div><h2 class="hd">Decide con claridad.</h2>
<p class="lead">Lo que conviene conocer antes de dar el siguiente paso con {esc(name)}.</p>{faqs}</div></section>'''

    contact = f'''<section class="contact" id="consulta-form"><div class="wrap contact-grid">
<div><div class="eyebrow">CONSULTA / {esc(name.upper())}</div><h2>Hablemos de tu operación.</h2>
<p class="lead" style="color:var(--dk)">Cuéntanos cómo trabajas y qué necesitas resolver. Revisaremos el alcance, los módulos y las condiciones para tu operación.</p>
<div class="interest"><b>TU FUNCIÓN DE INTERÉS</b>Explora una función o cuéntanos qué necesitas.</div>
<p class="small" style="margin-top:14px;color:var(--dk)">La disponibilidad de funciones e integraciones se confirma en la demo y cotización.</p></div>
<form class="cform" novalidate onsubmit="return false;"><h3 style="font-size:26px">Prepara tu consulta</h3>
<p class="small">Déjanos tus datos y un asesor te contactará por WhatsApp.</p>
<div class="rubro-box"><small>Rubro</small><b>{esc(name)}</b><input type="hidden" name="rubro" data-label="Rubro" value="{esc(name)}"></div>
<label>Nombre<input name="nombre" data-label="Nombre" placeholder="Tu nombre" autocomplete="name"></label>
<div class="fgrid"><label>WhatsApp<input name="whatsapp" data-label="WhatsApp" placeholder="9XX XXX XXX" inputmode="tel" autocomplete="tel"></label>
<label>Locales<select name="locales" data-label="Locales"><option>1 local</option><option>2 locales</option><option>3 o más locales</option></select></label></div>
<label>Negocio<input name="negocio" data-label="Negocio" placeholder="Nombre de tu negocio"></label>
<label>Especialidad<input name="especialidad" data-label="Especialidad" placeholder="Ej. {esc(d["para"].split(" · ")[0])}"></label>
<label>Necesidad<textarea name="necesidad" data-label="Necesidad" placeholder="Cuéntanos qué te gustaría revisar"></textarea></label>
{SEND_BTN}
<div class="before"><b>Antes de contactar</b><span>Rubro: {esc(name)}</span><span>Explora una función o cuéntanos qué necesitas.</span><span class="small">Revisa tus datos antes de enviar.</span></div>
</form></div></section>'''

    body = (header_rubro(k) + "<main>" + hero + eco + pack + special + mapa + funcs + benefits + pay + precios + testi + faq + contact + "</main>"
            + footer(k) + overlays(name, k, plans))
    nodes_js = jlist(["[" + jstr(a) + "," + jstr(b) + "]" for a, b in d["eco_nodes"]])
    data_js = "{" + f'"rubro":{jstr(name)},"nodes":{nodes_js},"pieces":{pieces_js},"plans":{jlist(plans_js)}' + "}"
    return page(f"Apiworking · {name}", d["sub"], body, data_js)

# ---------------- inicio ----------------
def inicio_page():
    CUR["page"] = "inicio"
    cards = ""
    for i, k in enumerate(ORDER):
        grp = next(g for g, ks in GROUPS if k in ks)
        if i == 0:
            cards += f'''<a class="rcard big" href="{href(k)}">{ph("Foto: " + NAMES[k])}<div class="rbody"><span class="chip" style="background:var(--y2)">{grp.upper()} / {i+1:02d}</span><span class="rm" aria-hidden="true">{MASCOT[k]}</span><h3>{esc(NAMES[k])}</h3><p>{esc(TAGLINES[k])}</p><b>Explorar {esc(NAMES[k].lower())} ↗</b></div></a>'''
        else:
            cards += f'''<a class="rcard" href="{href(k)}"><span class="rm" aria-hidden="true">{MASCOT[k]}</span><div><h3>{esc(NAMES[k])}</h3><p>{esc(TAGLINES[k])}</p><small>{i+1:02d} / ↗</small></div></a>'''
    extra_css = """
.navh a{background:rgba(255,255,255,.45)}
.collage{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.collage>div:first-child{grid-column:1/-1}.collage>div:first-child .ph{min-height:280px}
.flow{position:absolute;left:50%;bottom:16px;transform:translateX(-50%);background:rgba(255,255,255,.9);border-radius:999px;padding:8px 16px;font-size:13px;font-weight:600;white-space:nowrap}
.loy{background:#fff;border-radius:24px;padding:22px;margin-top:14px;display:grid;grid-template-columns:1fr auto;gap:16px;align-items:end}
.loy .pts{font-size:40px;font-weight:600;color:var(--hd)}
.bar{height:6px;border-radius:9px;background:var(--g3);margin-top:10px;overflow:hidden}.bar i{display:block;height:100%;width:65%;background:var(--g)}
.stats{display:flex;gap:56px;margin-top:20px}.stats b{font-size:48px;display:block;line-height:1}
.how{background:var(--g2)}
.hcard{background:#fbfdf9;border-radius:26px;padding:28px;display:flex;flex-direction:column;gap:12px}
.hcard .ic{width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-left:auto;margin-top:-6px;background:#c8cc5a}
.hcard:nth-child(2) .ic{background:#c4554f}.hcard:nth-child(3) .ic{background:#e9d6a2}
.hcard h3{font-size:28px;color:var(--hd)}
.hcard .chain{background:var(--g3);border-radius:12px;padding:10px 14px;font-size:13px;font-weight:600;margin-top:auto}
.rgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:28px}
@media(max-width:1000px){.rgrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:620px){.rgrid{grid-template-columns:1fr}}
.rcard{background:#fff;border-radius:24px;padding:20px;text-decoration:none;display:flex;gap:16px;align-items:flex-start;transition:transform .15s,box-shadow .15s}
.rcard:hover{transform:translateY(-3px);box-shadow:var(--sh)}
.rcard .rm{font-size:30px;width:56px;height:56px;border-radius:50%;background:var(--g4);display:flex;align-items:center;justify-content:center;flex:none}
.rcard h3{font-size:19px}.rcard p{font-size:14px;color:var(--mut);margin-top:4px}.rcard small{display:block;margin-top:10px;font-weight:700;font-size:12px}
.rcard.big{grid-column:span 2;grid-row:span 2;flex-direction:column;padding:0;overflow:hidden;background:#e9f8d9}
@media(max-width:620px){.rcard.big{grid-column:auto;grid-row:auto}}
.rcard.big .ph{min-height:220px;border-radius:0;width:100%}
.rcard.big .rbody{padding:22px;position:relative;width:100%}
.rcard.big .rm{position:absolute;right:20px;top:-36px;width:72px;height:72px;font-size:38px;background:#ffb3b8}
.rcard.big h3{font-size:30px;color:var(--hd);margin-top:14px}.rcard.big b{display:block;margin-top:20px}
.loyal-h{background:var(--g2)}
.loy-steps{list-style:none;display:grid;gap:18px;margin:28px 0}
.loy-steps li{display:grid;grid-template-columns:40px 1fr;font-size:14px}
.loy-steps b{font-size:20px;display:block;color:var(--dk)}
.pieces2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.cta{background:var(--g)}
.cta-box{background:#d9f590;border-radius:30px;padding:48px;text-align:left}
"""
    body = f'''<header class="hdr"><div class="hdr-in">
<a class="logo" href="{href("inicio")}">APIWORKING</a>
<nav class="nav navh" aria-label="Secciones"><a href="#rubros">Soluciones por rubro</a><a href="#como-funciona" style="background:rgba(255,255,255,.45)">Cómo funciona</a><a href="#fidelizacion">Fidelización</a></nav>
<a class="btn btn-y btn-sm" href="#rubros">Encuentra tu solución ↗</a>
</div></header>
<main>
<section class="hero" id="top"><div class="wrap hero-grid">
<div><p class="small" style="font-weight:600;color:var(--dk)">● Un ecosistema. Tu forma de trabajar.</p>
<h1 style="margin-top:16px">Hecho para<br>tu negocio.<br>Pensado para<br>que vuelvan.</h1>
<p class="lead" style="color:var(--dk)">Más que un POS: conecta venta, operación, atención y fidelidad. Herramientas pensadas para que tus clientes regresen.</p>
<div class="hero-ctas"><a class="btn btn-w" href="#rubros">Encuentra tu solución ↗</a><a class="btn-ghost" href="#como-funciona" style="align-self:center">Conoce Apiworking ↓</a></div>
<p class="small" style="margin-top:16px;color:var(--dk)">*Funciones según rubro, plan y configuración.</p></div>
<div><div class="collage"><div style="position:relative">{ph("Foto: mozo atendiendo una mesa")}<span class="flow">Venta → operación → próxima visita</span></div>{ph("Foto: cajera en tienda")}{ph("Foto: recepción de hotel")}</div>
<div class="loy"><div><b>ApiLoyalty )))</b><div class="pts">120 puntos</div><p class="small">Tu próxima visita empieza aquí.</p><div class="bar"><i></i></div></div><div style="font-size:42px" aria-hidden="true">🪄</div></div></div>
</div></section>
<section style="padding-top:24px"><div class="wrap"><h2 style="font-size:32px">Diferentes negocios.<br>Un mismo ecosistema.</h2>
<div class="stats"><div><b>11</b>rubros para explorar</div><div><b>264</b>funciones documentadas</div></div></div></section>
<section class="how" id="como-funciona"><div class="wrap">
<div class="eyebrow">CÓMO FUNCIONA</div><h2 class="hd">No son piezas sueltas. Es tu negocio, conectado.</h2>
<p class="lead">Desde la primera venta hasta la siguiente visita de tu cliente.</p>
<div class="grid g3" style="margin-top:32px">
<div class="hcard"><div class="eyebrow" style="margin:0">01 / VENTA</div><div class="ic" aria-hidden="true">🏪</div><h3>Vende mejor</h3><p>Registra pedidos, cobra y emite comprobantes con herramientas pensadas para tu rubro.</p><div class="chain">Caja → Comprobante</div></div>
<div class="hcard"><div class="eyebrow" style="margin:0">02 / OPERACIÓN</div><div class="ic" aria-hidden="true">🏭</div><h3>Controla tu operación</h3><p>Conecta inventario, compras y tareas. Consulta lo que pasa en cocina, almacén o recepción.</p><div class="chain">Venta → Stock → Control</div></div>
<div class="hcard"><div class="eyebrow" style="margin:0">03 / RELACIÓN</div><div class="ic" aria-hidden="true">💚</div><h3>Haz que regresen</h3><p>Vincula la atención con tu club digital: puntos, estampillas y reseñas para seguir presente después de cobrar.</p><div class="pieces2">{ph("Varitas NFC")}{ph("Display Club de Fidelidad")}</div><div class="chain">Atención → Fidelidad</div></div>
</div></div></section>
<section style="background:var(--g)" id="rubros"><div class="wrap">
<div class="eyebrow">ENCUENTRA TU SOLUCIÓN</div><h2>Tu negocio tiene su propia forma. Tu sistema también debería.</h2>
<p class="lead" style="color:var(--dk)">Elige tu rubro y descubre un recorrido pensado para tu operación.</p>
<p class="eyebrow" style="margin-top:28px">11 RUBROS, TODOS A LA VISTA</p>
<div class="rgrid">{cards}</div>
<p style="margin-top:28px;font-weight:600">Gastronomía, comercio y servicios: explora cada solución sin perder de vista el conjunto.</p>
</div></section>
<section class="loyal-h" id="fidelizacion"><div class="wrap feature">
<div><div class="eyebrow">APILOYALTY + NFC</div><h2 class="hd">La venta no termina cuando tu cliente paga. Allí recién comienza.</h2>
<p class="lead">Transforma el final de una compra en el inicio de una relación: club digital, puntos, estampillas y un gesto NFC que invita a volver.</p>
<ol class="loy-steps"><li><span>01</span><div><b>Acerca</b>Un punto de contacto NFC.</div></li><li><span>02</span><div><b>Conecta</b>Tu negocio y tu club digital.</div></li><li><span>03</span><div><b>Invita a volver</b>Una recompensa por descubrir.</div></li></ol>
<a class="btn btn-y" style="background:#d9f590" href="#rubros">Ver opciones para mi negocio ↗</a></div>
<div><p class="eyebrow">UN GESTO REAL. UNA RELACIÓN DIGITAL.</p><div class="pieces2">{ph("01 · Varita NFC")}{ph("02 · Display del sistema")}</div>
<div class="wallet-img" style="margin-top:14px"><img src="{IMG[WALLET_IMG["inicio"]]}" alt="Tarjeta wallet de ejemplo: Club Mesa Feliz" loading="lazy" decoding="async"></div></div>
</div></section>
<section class="faq" id="preguntas"><div class="wrap" style="max-width:860px">
<div class="eyebrow">PREGUNTAS FRECUENTES</div><h2 class="hd">Lo esencial, sin rodeos.</h2>
<details><summary>¿Apiworking es solo un punto de venta?</summary><p>No. El ecosistema reúne venta, operación, atención y fidelización, con herramientas que cambian según el rubro.</p></details>
<details><summary>¿Todas las funciones vienen incluidas?</summary><p>El alcance depende de la solución y su configuración. Los módulos, equipos e integraciones se confirman en la demostración y cotización.</p></details>
<details><summary>¿Por dónde empiezo?</summary><p>Elige tu rubro. Encontrarás su recorrido de trabajo y las herramientas relacionadas para evaluar qué necesita tu negocio.</p></details>
</div></section>
<section class="cta"><div class="wrap"><div class="cta-box"><h2 class="hd">Tu siguiente paso tiene nombre de rubro.</h2><p class="lead">Explora las herramientas que tienen sentido para tu día a día.</p><a class="btn btn-w" style="margin-top:24px" href="#rubros">Encuentra tu solución ↗</a></div></div></section>
</main>
{footer(None)}'''
    return page("Apiworking", "Hecho para tu negocio. Pensado para que vuelvan. Venta, operación, atención y fidelidad en un ecosistema.", body, "{}", extra_css)

files = {"inicio/index.html": inicio_page()}
for k in ORDER:
    folder = k
    files[f"{folder}/{folder}.html"] = rubro_page(k)
unused = (set(PH_IMG) | {(pg, l) for pg, m in PH_IMG_PAGE.items() for l in m}) - USED_PH
if unused: print("AVISO: imágenes sin recuadro:", sorted(unused))
for path, content in files.items():
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{path}: {len(content)//1024} KB")
