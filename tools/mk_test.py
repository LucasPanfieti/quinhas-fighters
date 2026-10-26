import sys
R='C:/Users/lukin/OneDrive/Documentos/LAMP-13/quinhas-fighters/'
s=open(R+'index.html',encoding='utf-8').read()
inj="""<script>
(function(){const h=location.hash.slice(1);let n=0;
const iv=setInterval(()=>{try{if(!CH||!CH.q)return}catch(e){return}
clearInterval(iv);document.getElementById('title').style.display='none';begin('ai','q','e');
setTimeout(()=>{st='fight';p1.x=330;p2.x=560;p2.up=function(){};p1.up=function(){};
const [k,t]=h.split(',');const T0=+t||0;
if(k==='p'){p1.atk='p';p1.t=T0}else if(k==='k'){p1.atk='k';p1.t=T0}
else if(k==='w'){p1.mv=1;p1.wp=T0*4}else if(k==='h'){p1.stun=T0}else if(k==='b'){p1.blk=true;p1.stun=T0}
else if(k==='r'){p1.cr=true;p2.cr=true}else if(k==='c'){p1.land=8}else if(k==='d'){p1.P.id=p1.P.hd;p1.P.m.id=p1.P.m.hd}else if(k==='o'){p1.ko=true;p1.t=T0}else if(k==='j'){p1.vy=T0}
p1.y=k==='j'?-120:0;p2.y=0;p1.land=k==='c'?8:0;p1.jt=0;
},300)},50)})();
</script>
</body>"""
i=s.rindex('</body>')
open(R+'_test.html','w',encoding='utf-8').write(s[:i]+inj+s[i+7:])
