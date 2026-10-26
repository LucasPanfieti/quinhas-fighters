"""Reaplica: abaixar, poses do Quinhas-Kun, Hadouken, cenarios e Cai-Ren (sobre a base v1.1)."""
import json, re
R='C:/Users/lukin/OneDrive/Documentos/LAMP-13/quinhas-fighters/'
s=open(R+'index.html',encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    if a not in s: raise SystemExit('missing: '+a[:80])
    s=s.replace(a,b,n)

# ---- SPR q + r --------------------------------------------------------------
qm=json.load(open(R+'tools/out/q_poses.json'))
rm=json.load(open(R+'tools/out/r_poses.json'))
def spr(cid,meta,v):
    return '{'+','.join('%s:"assets/spr/%s/%s.webp?v=%s"'%(k,cid,k,v) for k in meta)+',m:'+json.dumps(meta)+'}'
a=s.index(',q:{id:"assets/spr/q/id.webp');b=s.index(',e:{id:',a)
s=s[:a]+',q:'+spr('q',qm,8)+',r:'+spr('r',rm,1)+s[b:]

# ---- CSS abaixar + hadouken + cenario ---------------------------------------
rep(".dpad .b[data-k=vR]{grid-column:3;grid-row:2}",
    ".dpad .b[data-k=vR]{grid-column:3;grid-row:2}\n.dpad .b[data-k=vD]{grid-column:2;grid-row:2}")
rep(".acts{grid-template-columns:repeat(2,var(--bs));grid-template-rows:repeat(2,var(--bs))}",
    ".acts{grid-template-columns:repeat(2,var(--bs));grid-template-rows:repeat(3,var(--bs))}")
rep(".acts .b[data-k=vP]{grid-column:1;grid-row:2}",
    ".acts .b[data-k=vH]{grid-column:1/-1;grid-row:3;width:100%;aspect-ratio:auto;height:var(--bs);border-radius:999px}\n.acts .b[data-k=vP]{grid-column:1;grid-row:2}")
rep(".b[data-k=vB].on{",
    ".b[data-k=vH].on{background:linear-gradient(#8fe0ff,#1aa0ff)}\n.b[data-k=vB].on{")
css='''
/* ---- escolha de cenario ---- */
#stgrid{display:flex;gap:clamp(10px,2vw,22px);justify-content:center;flex-wrap:wrap;width:min(940px,96vw)}
.stc{position:relative;width:min(290px,44vw);aspect-ratio:16/9;border:0;padding:0;border-radius:4px;overflow:hidden;cursor:pointer;background:#050a1c;color:#fff;box-shadow:0 0 0 2px rgba(90,160,255,.7),0 8px 18px rgba(0,0,0,.6);transition:transform .15s,box-shadow .15s}
.stc img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .35s}
.stc b{position:absolute;left:0;right:0;bottom:0;padding:22px 10px 8px;background:linear-gradient(transparent,rgba(2,4,16,.94));font:italic 700 clamp(11px,2.6vw,15px)/1.1 var(--ui);letter-spacing:.1em;text-transform:uppercase;text-shadow:0 2px 0 #000}
.stc:hover,.stc.gf{transform:translateY(-4px) scale(1.04);box-shadow:0 0 0 3px #fff,0 0 28px rgba(255,140,50,.85),0 8px 18px rgba(0,0,0,.6);outline:none}
.stc:hover img,.stc.gf img{transform:scale(1.07)}
.stc.rnd{background:radial-gradient(circle at 50% 45%,#27409c,#070b22 75%)}
.stc.rnd i{position:absolute;inset:0 0 18px 0;display:flex;align-items:center;justify-content:center;font:italic 900 clamp(44px,9vw,76px)/1 var(--ui);color:#ffb04a;text-shadow:0 3px 0 #000,0 0 22px rgba(255,150,50,.7)}
'''
i=s.index('/* ---- mobile pad ---- */');s=s[:i]+css+s[i:]
s=re.sub(r'#op((?:::before|::after|>\*|>:nth-child\(\d\)| h1|\[style\*="flex"\])?)(?=[,{)])',r'#op\1,#stg\1',s)

# ---- HTML -------------------------------------------------------------------
rep('<button type="button" class="b" data-k="vR" aria-label="Direita">▶</button>',
    '<button type="button" class="b" data-k="vD" aria-label="Abaixar">▼</button>\n   <button type="button" class="b" data-k="vR" aria-label="Direita">▶</button>')
rep('<button type="button" class="b" data-k="vP" aria-label="Soco">',
    '<button type="button" class="b" data-k="vH" aria-label="Hadouken">Hadouken</button>\n   <button type="button" class="b" data-k="vP" aria-label="Soco">')
rep('<tr><td>Soco</td><td><kbd>F</kbd>',
    '<tr><td>Abaixar</td><td><kbd>S</kbd></td><td><kbd>▼</kbd></td><td data-pc="crouch"></td></tr><tr><td>Soco</td><td><kbd>F</kbd>')
rep('<tr><td>Defesa</td><td><kbd>S</kbd></td><td><kbd>J</kbd></td><td data-pc="block"></td></tr>',
    '<tr><td>Hadouken</td><td><kbd>R</kbd></td><td><kbd>I</kbd></td><td data-pc="hadouken"></td></tr><tr><td>Defesa</td><td><kbd>H</kbd></td><td><kbd>J</kbd></td><td data-pc="block"></td></tr>')
html='''<div id="stg"><h1>Escolha o cenário</h1><div id="stgrid">
   <button type="button" class="stc" data-i="0"><img src="assets/stg/1.webp" alt=""><b>Templo da Montanha</b></button>
   <button type="button" class="stc" data-i="1"><img src="assets/stg/2.webp" alt=""><b>Colégio Leila Guedes</b></button>
   <button type="button" class="stc rnd" data-i="r"><i>?</i><b>Aleatório</b></button></div>
  <button class="go alt" id="stback">Voltar</button></div>
 '''
rep('<div id="hp"><h1>Controles</h1>',html+'<div id="hp"><h1>Controles</h1>')

# ---- entrada ----------------------------------------------------------------
rep("u:B(12)||B(3)||A[1]<-.55,p:B(2),k:B(0),b:B(1)||B(4)||B(5)||B(6)||B(7)}",
    "u:B(12)||B(3)||A[1]<-.55,d:B(13)||A[1]>.55,h:B(5),p:B(2),k:B(0),b:B(1)||B(4)||B(6)||B(7)}")
rep("u:keys.KeyW||keys.vU||g.u,p:keys.KeyF||keys.vP||g.p,k:keys.KeyG||keys.vK||g.k,b:keys.KeyS||keys.vB||g.b}",
    "u:keys.KeyW||keys.vU||g.u,d:keys.KeyS||keys.vD||g.d,h:keys.KeyR||keys.vH||g.h,p:keys.KeyF||keys.vP||g.p,k:keys.KeyG||keys.vK||g.k,b:keys.KeyH||keys.vB||g.b}")
rep("u:keys.ArrowUp||g.u,p:keys.KeyK||g.p,k:keys.KeyL||g.k,b:keys.KeyJ||g.b}",
    "u:keys.ArrowUp||g.u,d:keys.ArrowDown||g.d,h:keys.KeyI||g.h,p:keys.KeyK||g.p,k:keys.KeyL||g.k,b:keys.KeyJ||g.b}")
rep("td.innerHTML=a==='move'?gI('move')+' '+dim('ou')+' <kbd>analógico</kbd>'",
    "td.innerHTML=a==='move'?gI('move')+' '+dim('ou')+' <kbd>analógico</kbd>'\n   :a==='crouch'?gI('move')+' '+dim('para baixo ou')+' <kbd>analógico ▼</kbd>'\n   :a==='hadouken'?'<kbd>'+(mix?'RB / R1':pk==='p'?'R1':'RB')+'</kbd>'")

# ---- combate: ATK h, projeteis, abaixar, poses extras -----------------------
rep("const W=800,H=450,G=362,SH=240;","const W=800,H=450,SH=240;let G=362;")
rep("k:{s:10,a:4,n:30,d:11,r:160,st:18,kb:8,hy:165}};",
 "k:{s:10,a:4,n:30,d:11,r:160,st:18,kb:8,hy:165},h:{s:16,a:0,n:38,d:9,r:0,st:16,kb:6,hy:135}};\n"
 "const PJ=[];\n"
 "function fireball(o){const P=o.P,hb=P.m&&P.m.hb;if(!hb)return;const sc=P.sc||SC;PJ.push({x:o.x+o.face*(hb.dx*sc+6),y:G+o.y-hb.dy*sc,dir:o.face,o,t:0,im:P.hb,m:hb,sc});o.hcd=80;sfxSwing('k');sfxSwing('p')}\n"
 "function updPJ(){for(let i=PJ.length-1;i>=0;i--){const p=PJ[i];p.x+=p.dir*8;p.t++;const tg=p.o===p1?p2:p1;let dead=p.x<-100||p.x>W+100;"
 "if(!dead&&!tg.ko&&Math.abs(p.x-tg.x)<34&&tg.y>-100){tg.hurt(p.o,ATK.h);dead=true;spark(p.x,p.y,p.dir,10)}"
 "if(!dead)for(let j=0;j<PJ.length;j++){const q=PJ[j];if(j!==i&&q.dir!==p.dir&&Math.abs(q.x-p.x)<46){spark(p.x,p.y,p.dir,10);spark(p.x,p.y,-p.dir,10);PJ.splice(j,1);if(j<i)i--;dead=true;break}}"
 "if(dead)PJ.splice(PJ.indexOf(p),1)}}\n"
 "function drawPJ(){PJ.forEach(p=>{const k=1+Math.sin(T*.9+p.t)*.07,w=p.m.w*p.sc*k,h=p.m.h*p.sc*k;x.save();x.translate(p.x,p.y);x.scale(p.dir,1);x.shadowColor='#4cc3ff';x.shadowBlur=26;x.drawImage(p.im,-w*.45,-h/2,w,h);x.restore()})}")
rep(" reset(){Object.assign(this,{x:this.sx,y:0,vy:0,hp:100,gh:100,atk:null,t:0,stun:0,kb:0,blk:false,ko:false,mv:0,wp:0,land:0,jt:0,hf:0,tr:[],cur:null,landed:false,face:this.sx<W/2?1:-1})}",
 " reset(){Object.assign(this,{x:this.sx,y:0,vy:0,hp:100,gh:100,atk:null,t:0,stun:0,kb:0,blk:false,ko:false,mv:0,cr:false,hcd:0,wp:0,land:0,jt:0,hf:0,tr:[],cur:null,landed:false,face:this.sx<W/2?1:-1})}")
rep(" this.t++;\n  if(this.gh>this.hp)"," this.t++;if(this.hcd>0)this.hcd--;\n  if(this.gh>this.hp)")
rep("else if(this.atk){const a=ATK[this.atk];if(this.t>=a.s","else if(this.atk){const a=ATK[this.atk];if(this.atk==='h'&&this.t===a.s)fireball(this);if(this.t>=a.s")
rep("if(this.t%2===0&&this.t>=a.s-2&&this.t<a.s+a.a+8&&this.cur)this.tr.push","if(this.atk!=='h'&&this.t%2===0&&this.t>=a.s-2&&this.t<a.s+a.a+8&&this.cur)this.tr.push")
rep("    this.blk=!!i.b&&gr;this.mv=0;\n    if(!this.blk){\n     this.mv=(i.r?1:0)-(i.l?1:0);\n     this.x+=this.mv*3.4*(this.mv*this.face>0?1:.8);if(this.mv&&gr){this.wp++;if(this.wp%9===0){dust(this.x-this.face*10,G,2,-this.face);sfxStep()}}\n     if(i.u&&gr){this.vy=-15;this.jt=6;dust(this.x,G,4,0);sfxJump()}\n     if(i.p)this.go('p');else if(i.k)this.go('k');\n    }",
 "    this.blk=!!i.b&&gr;this.mv=0;this.cr=!!i.d&&gr&&!this.blk;\n    if(!this.blk){\n     this.mv=this.cr?0:(i.r?1:0)-(i.l?1:0);\n     this.x+=this.mv*3.4*(this.mv*this.face>0?1:.8);if(this.mv&&gr){this.wp++;if(this.wp%9===0){dust(this.x-this.face*10,G,2,-this.face);sfxStep()}}\n     if(i.u&&gr&&!this.cr){this.vy=-15;this.jt=6;dust(this.x,G,4,0);sfxJump()}\n     if(i.h&&this.P.hd&&!this.hcd&&gr)this.go('h');else if(i.p)this.go('p');else if(i.k)this.go('k');\n    }")
# draw
rep("if(t<9){pz='ht';tx=-t*2;","if(t<9){pz=P.fa?'fa':'ht';tx=-t*2;")
rep("   if(this.mv){pz=((this.wp>>3)&1)?'wk':'id';ty=-Math.abs(Math.sin(this.wp*.39))*5;rot=this.mv*this.face>0?.05:-.03}",
 "   if(st==='end'&&P.vi&&(this===p1?p2:p1).ko)pz='vi';\n   else if(this.cr){if(P.cr)pz='cr';else{sy=.74;sx=1.08}}\n   else if(this.mv){pz=((this.wp>>3)&1)?'wk':'id';ty=-Math.abs(Math.sin(this.wp*.39))*5;rot=this.mv*this.face>0?.05:-.03}")
rep("  else if(this.atk==='p'){pz=","  else if(this.atk==='h'&&P.hd){pz='hd';tx=kf(t,[[0,0],[16,6],[26,0]])}\n  else if(this.atk==='p'){pz=")
rep("  if(a&&t>=a.s-3&&t<a.s+a.a+5){","  if(a&&this.atk!=='h'&&t>=a.s-3&&t<a.s+a.a+5){")
rep("x.shadowBlur=0;\n  if(this.hf>0)",
 "x.shadowBlur=0;\n  if(this.atk==='h'&&P.hb&&t<a.s){const hb=P.m.hb,k=.3+.7*Math.min(1,t/a.s),w=hb.w*sc*k,h=hb.h*sc*k;x.save();x.shadowColor='#4cc3ff';x.shadowBlur=20;const pk=Math.min(1,t/a.s),cx=((hb.hx||hb.dx)+(hb.dx-(hb.hx||hb.dx))*pk)*sc;x.drawImage(P.hb,cx-w*.45,-hb.dy*sc-h/2,w,h);x.restore()}\n  if(this.hf>0)")
rep("p2.shadow();p1.draw();p2.draw();drawPs()}","p2.shadow();p1.draw();p2.draw();drawPJ();drawPs()}")
rep("p1.up(in1(),p2);p2.up(mode==='ai'?ai(p2,p1):in2(),p1);flushHits();sep();","p1.up(in1(),p2);p2.up(mode==='ai'?ai(p2,p1):in2(),p1);flushHits();updPJ();sep();")
rep("function startRound(){p1.reset();","function startRound(){PJ.length=0;p1.reset();")
# IA
rep("  if(d>175)me.plan=r<.8?'ap':'jump';","  if(me.P.hd&&!me.hcd&&d>150&&r>.8)me.plan='h';\n  else if(d>175)me.plan=r<.8?'ap':'jump';")
rep("  case 'blk':i.b=1;break;","  case 'h':i.h=1;me.plan='idle';break;\n  case 'blk':i.b=1;break;")
rep(" const to=tw?'r':'l',aw=tw?'l':'r';"," if(PJ.some(q=>q.o===o&&Math.abs(q.x-me.x)<220)&&Math.random()<.06){me.plan='blk';me.pt=20}\n const to=tw?'r':'l',aw=tw?'l':'r';")

# ---- cenario + rostos + load ------------------------------------------------
rep('const bg=new Image();bg.src="assets/bg.webp";',
 'const bg=new Image();bg.src="assets/bg.webp";\nconst bg2=new Image();bg2.src="assets/bg2.webp";\n'
 'const MAPS=[{n:"Templo da Montanha",img:bg,G:362},{n:"Colégio Leila Guedes",img:bg2,G:438}];let curBg=bg,stgSel=null;\n'
 'function askStage(m,a,b){stgSel={m,a,b};selEl.style.display="none";menu.style.display="none";$("stg").style.display="flex";mi=0}\n'
 '$("stgrid").querySelectorAll(".stc").forEach(c=>c.onclick=()=>{const v=c.dataset.i,i=v==="r"?Math.random()*MAPS.length|0:+v;$("stg").style.display="none";begin(stgSel.m,stgSel.a,stgSel.b,i)});\n'
 '$("stback").onclick=()=>{$("stg").style.display="none";openSel(stgSel.m)};')
rep(" x.drawImage(bg,0,0,W,H);if(st!=='menu')"," x.drawImage(st==='menu'?bg:curBg,0,0,W,H);if(st!=='menu')")
rep("function begin(m,a,b){LASTM=[m,a,b];mode=m;","function begin(m,a,b,stg=0){LASTM=[m,a,b,stg];G=MAPS[stg].G;curBg=MAPS[stg].img;mode=m;")
rep("begin('ai',id,o[Math.random()*o.length|0]);return}","askStage('ai',id,o[Math.random()*o.length|0]);return}")
rep("const a=pick1;pick1=null;begin('2p',a,id)}","const a=pick1;pick1=null;askStage('2p',a,id)}")
rep("setTimeout(()=>begin('2p',s2.lk[0],s2.lk[1]),900)","setTimeout(()=>askStage('2p',s2.lk[0],s2.lk[1]),900)")
rep("if(vis(selEl))return 'sel';","if(vis($('stg')))return 'stage';if(vis(selEl))return 'sel';")
rep("pause:()=>[...$('pause').querySelectorAll('.go')]};","pause:()=>[...$('pause').querySelectorAll('.go')],stage:()=>[...$('stg').querySelectorAll('.stc'),$('stback')]};")
rep("if(k==='bk'){if(s==='sel')$('back').click();","if(k==='bk'){if(s==='stage')$('stback').click();else if(s==='sel')$('back').click();")
rep("b.id==='back'||b.id==='hback'||b.id==='oback'?'back'","b.id==='back'||b.id==='hback'||b.id==='oback'||b.id==='stback'?'back'")
rep("const ROSTER=['b',null,'c',","const ROSTER=['b','r','c',")
rep("for(const k of ['id','wk','pu','ki','bl','ht','jp','ko'])r[k]=await load(o[k]);return r};",
 "for(const k of ['id','wk','pu','ki','bl','ht','jp','ko','cr','hd','hb','fa','vi'])if(o[k])r[k]=await load(o[k]);return r};")
rep("ld(SPR.b),new Promise(r=>{if(bg.complete)","ld(SPR.b),ld(SPR.r),new Promise(r=>{if(bg.complete)")
rep("bg.onerror=()=>{LOAD.bad.push('assets/bg.webp');r()}}})]).then(([it,iq,ie,ig,il,ic,iu,ik,ib])=>{",
 "bg.onerror=()=>{LOAD.bad.push('assets/bg.webp');r()}}}),new Promise(r=>{if(bg2.complete){if(!bg2.naturalWidth)LOAD.bad.push('assets/bg2.webp');r()}else{bg2.onload=r;bg2.onerror=()=>{LOAD.bad.push('assets/bg2.webp');r()}}})]).then(([it,iq,ie,ig,il,ic,iu,ik,ib,ir])=>{")
rep("iq.sc=.587;","iq.sc=.587;ir.sc=.587;ir.pf=new Image();ir.pf.src=FACE_OF('r');")
rep("b:{n:'Bea-Trix',P:ib,col:'#e0b45a'}","b:{n:'Bea-Trix',P:ib,col:'#e0b45a'},r:{n:'Cai-Ren',P:ir,col:'#8a9bb8'}")
rep("total:Object.keys(SPR).length*8+1","total:Object.keys(SPR).length*8+2")

open(R+'index.html','w',encoding='utf-8').write(s)
checks=['MAPS=','fireball','askStage','Cai-Ren','this.cr=','assets/spr/r/id','Abaixar','Hadouken','G:438']
print({c:c in open(R+'index.html',encoding='utf-8').read() for c in checks})
