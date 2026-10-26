"""Monta o atlas de animacao de um personagem a partir das tiras em quinhas-kun/.
Saida: assets/spr/<id>/sheet.webp + tools/out/<id>.json (metadados dos quadros) + previa de conferencia."""
import json, os, sys
from PIL import Image, ImageDraw
import slice as S

ROOT='C:/Users/lukin/OneDrive/Documentos/LAMP-13/quinhas-fighters/'
SRC=ROOT+'quinhas-kun/'
CID='q'
IDLE_H=500            # altura final do personagem parado (px do atlas)
# fator de escala por acao (normaliza o tamanho da cabeca entre as tiras)
CAL={'id':1.0,'wk':1.61,'pu':1.25,'ki':1.225,'bl':.79,'ht':.76,'jp':.945,'ko':.85}
# acao -> quadros que voam (deslocamento vertical em px do atlas)
LIFT={'ko':[150,100,0,0]}
CENTER={'ko'}         # ancora no centro do quadro em vez dos pes

def feet_cx(fr):
    """x medio (na imagem recortada) dos pixels opacos nos 10% de baixo."""
    w,h=fr.size;a=fr.split()[3].point(lambda v:255 if v>128 else 0)
    strip=a.crop((0,int(h*.9),w,h));prof=list(strip.resize((w,1),Image.BOX).getdata())
    tot=sum(prof)
    return (sum(i*v for i,v in enumerate(prof))/tot) if tot else w/2

def torso_cx(fr):
    """x medio dos pixels opacos entre 25% e 45% da altura (tronco)."""
    w,h=fr.size;a=fr.split()[3].point(lambda v:255 if v>128 else 0).crop((0,int(h*.25),w,int(h*.45)))
    prof=list(a.resize((w,1),Image.BOX).getdata());tot=sum(prof)
    return (sum(i*v for i,v in enumerate(prof))/tot) if tot else w/2

PERFRAME={'id','wk','bl','ht','jp'}   # ciclos no lugar: ancora no tronco de cada quadro

def main():
    acts={}
    for a,spec in S.QUINHAS.items():
        fl=S.frames(SRC,spec);acts[a]=fl
    g=IDLE_H/ (sum(f[0].size[1] for f in acts['id'])/len(acts['id']))
    items=[]   # (acao, indice, imagem escalada, ax, dy)
    for a,fl in acts.items():
        s=g*CAL[a]
        fr0,bb0,cell0=fl[0]
        rel0=bb0[0]+torso_cx(fr0)-cell0[0]       # ancora relativa a celula, do 1o quadro
        for i,(fr,bb,cell) in enumerate(fl):
            if a in CENTER:ax_src=fr.size[0]/2
            elif a in PERFRAME:ax_src=torso_cx(fr)
            else:ax_src=(cell[0]+rel0)-bb[0]
            w,h=max(1,round(fr.size[0]*s)),max(1,round(fr.size[1]*s))
            im=fr.resize((w,h),Image.LANCZOS)
            items.append([a,i,im,ax_src*s,(LIFT.get(a,[0]*9)[i])])
    # empacota (prateleiras)
    items_sorted=sorted(items,key=lambda t:-t[2].size[1])
    AW=2048;pad=2;x=y=sh=0;pos={}
    for it in items_sorted:
        w,h=it[2].size
        if x+w+pad>AW:x=0;y+=sh+pad;sh=0
        pos[(it[0],it[1])]=(x,y);x+=w+pad;sh=max(sh,h)
    AH=y+sh+pad
    sheet=Image.new('RGBA',(AW,AH),(0,0,0,0))
    meta={}
    for a,i,im,ax,dy in items:
        px,py=pos[(a,i)];sheet.paste(im,(px,py))
        meta.setdefault(a,[]).append([px,py,im.size[0],im.size[1],round(ax,1),dy])
    d=ROOT+'assets/spr/%s/'%CID
    sheet.save(d+'sheet.webp','WEBP',quality=90,method=6)
    os.makedirs(ROOT+'tools/out',exist_ok=True)
    json.dump({'src':'assets/spr/%s/sheet.webp'%CID,'a':meta,'idleH':IDLE_H},open(ROOT+'tools/out/%s.json'%CID,'w'))
    # id.webp (previa na selecao) = 1o quadro parado, recortado
    acts['id'][0][0].resize(items[0][2].size,Image.LANCZOS).save(d+'id.webp','WEBP',quality=92)
    print('atlas',sheet.size,'frames',len(items),'scale g=%.3f'%g)
    # previa de conferencia: todos os quadros alinhados pela ancora e pelo chao
    rows=[];Hs=0
    for a in S.QUINHAS:
        ms=meta[a];Hr=max(m[3]+m[5] for m in ms);rows.append((a,ms,Hr));Hs+=Hr+30
    Ws=sum(max(m[2] for m in ms)+60 for a,ms,_ in rows[:1])  # placeholder
    maxW=max(sum(m[2]+20 for m in ms) for a,ms,_ in rows)+40
    prev=Image.new('RGBA',(maxW,Hs),(70,74,96,255));dr=ImageDraw.Draw(prev);yy=0
    for a,ms,Hr in rows:
        gy=yy+Hr+10;dr.line([(0,gy),(maxW,gy)],fill=(255,220,0,255));dr.text((4,yy+2),a,fill=(255,255,255,255))
        xx=20
        for m in ms:
            fr=sheet.crop((m[0],m[1],m[0]+m[2],m[1]+m[3]));ox=xx+int(m[4]);top=gy-m[3]-m[5]
            prev.alpha_composite(fr,(xx,top));dr.line([(ox,gy-30),(ox,gy+8)],fill=(255,0,0,255),width=2);xx+=m[2]+20
        yy+=Hr+30
    prev.convert('RGB').save('C:/Users/lukin/AppData/Local/Temp/lineup.png');print('previa',prev.size)

if __name__=='__main__':main()
