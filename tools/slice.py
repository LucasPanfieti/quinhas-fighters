"""Ferramenta de build: recorta as tiras de animacao (fundo verde) de um personagem.
Usa so Pillow. Separa os quadros por componentes conectados (funciona mesmo quando
um golpe invade a celula vizinha) e devolve quadros RGBA recortados, sem fundo."""
from PIL import Image, ImageChops, ImageFilter
import os
from collections import deque

# acao: (arquivo, colunas, linhas, quadros)
QUINHAS={'id':('parado/parado.png',4,1,4),'wk':('andar/andar.png',3,2,6),'pu':('soco/soco.png',4,1,4),'ki':('chute/chute.png',4,1,4),
         'bl':('defesa/defesa.png',2,1,2),'ht':('levar-golpe/levar-golpe.png',2,1,2),'jp':('pulo/pulo.png',2,1,2),'ko':('nocaute/nocaute.png',2,2,4)}

def key(im):
    """Remove so o verde neon de chroma (ligado a borda). Nao come verde de roupa/poder.
    Despill nas bordas: tira o halo verde sem roer a silhueta."""
    from PIL import ImageDraw
    rgb=im.convert('RGB');W,H=rgb.size
    r,g,b=rgb.split();R,G,B=r.tobytes(),g.tobytes(),b.tobytes()
    # so verde chapado: G bem alto e R/B quase zero (fundo #00F200)
    m=bytearray(W*H)
    for i in range(W*H):
        gv,rv,bv=G[i],R[i],B[i]
        if gv>160 and rv<60 and bv<60 and gv>rv+80 and gv>bv+80:m[i]=255
    fill=Image.frombytes('L',(W,H),bytes(m))
    for pt in [(0,0),(W-1,0),(0,H-1),(W-1,H-1),(W//2,0),(W//2,H-1),(0,H//2),(W-1,H//2)]:
        if fill.getpixel(pt)==255:ImageDraw.floodfill(fill,pt,128)
    alpha=fill.point(lambda v:0 if v==128 else 255)
    alpha=alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.35))
    # mascara de borda (opaco perto de transparente) p/ despill forte so no halo
    near=alpha.filter(ImageFilter.MaxFilter(5))
    edge=ImageChops.subtract(near, alpha.point(lambda v:255 if v>20 else 0))
    out=rgb.convert('RGBA');px=out.load();ap=alpha.load();ep=edge.load()
    for y in range(H):
        for x in range(W):
            a=ap[x,y]
            if a<6:
                px[x,y]=(0,0,0,0);continue
            rv,gv,bv,_=px[x,y]
            mx=max(rv,bv)
            # residual de chroma puro -> some
            if gv>120 and rv<100 and bv<100 and gv>rv+45 and gv>bv+45:
                px[x,y]=(0,0,0,0);continue
            on_edge=ep[x,y]>10 or a<200
            # contorno preto misturado com chroma -> some ou neutraliza
            if on_edge and max(rv,gv,bv)<55 and gv>=mx:
                if max(rv,gv,bv)<28 or (gv>mx and a<160):
                    px[x,y]=(0,0,0,0);continue
                v=(rv+bv)//2;px[x,y]=(v,v,v,min(a,180));continue
            if max(rv,gv,bv)<60 and gv>mx:
                px[x,y]=(rv,mx,bv,a);continue
            if gv>mx+10:
                if on_edge:
                    if gv>mx+25:a=max(0,int(a*.4))
                    px[x,y]=(rv,mx,bv,a)
                else:
                    px[x,y]=(rv,mx+int((gv-mx)*.4),bv,a)
            else:
                px[x,y]=(rv,gv,bv,a)
    return out

def components(mask,f=2):
    """Componentes conectados (8-viz.) numa versao reduzida por f. Devolve (rotulos, w, h, lista de pixels por componente)."""
    W,H=mask.size;w,h=W//f,H//f
    small=mask.resize((w,h),Image.BOX).point(lambda v:255 if v>0 else 0)
    d=small.tobytes();lab=[0]*(w*h);comps=[]
    for i in range(w*h):
        if d[i] and not lab[i]:
            n=len(comps)+1;q=deque([i]);lab[i]=n;px=[]
            while q:
                p=q.popleft();px.append(p);y,x=divmod(p,w)
                for dy in(-1,0,1):
                    for dx in(-1,0,1):
                        yy,xx=y+dy,x+dx
                        if 0<=yy<h and 0<=xx<w:
                            k=yy*w+xx
                            if d[k] and not lab[k]:lab[k]=n;q.append(k)
            comps.append(px)
    return w,h,comps

def frames(root,spec):
    fn,cols,rows,n=spec
    return frames_from(key(Image.open(os.path.join(root,fn))),cols,rows,n)

def frames_from(im,cols,rows,n):
    """Lista de (imagem recortada, bbox na origem, origem x da celula nominal)."""
    W,H=im.size;F=2
    mask=im.split()[3].point(lambda v:255 if v>100 else 0)
    w,h,comps=components(mask,F)
    cw,ch=W/cols,H/rows
    cells={}
    for px in comps:
        if len(px)<25:continue           # ruido
        xs=[p%w for p in px];ys=[p//w for p in px]
        cx=(sum(xs)/len(xs))*F;cy=(sum(ys)/len(ys))*F
        c=min(cols-1,int(cx//cw));r=min(rows-1,int(cy//ch))
        cells.setdefault((r,c),[]).extend(px)
    out=[]
    for r in range(rows):
        for c in range(cols):
            if len(out)>=n:break
            px=cells.get((r,c))
            if not px:continue
            m=Image.new('L',(w,h),0);mp=m.load()
            for p in px:mp[p%w,p//w]=255
            m=m.resize((W,H),Image.NEAREST).filter(ImageFilter.MaxFilter(7))
            piece=im.copy();piece.putalpha(ImageChops.multiply(im.split()[3],m))
            bb=piece.split()[3].point(lambda v:255 if v>40 else 0).getbbox()
            out.append((piece.crop(bb),bb,(int(round(c*cw)),int(round(r*ch)))))
    return out

if __name__=='__main__':
    root='C:/Users/lukin/OneDrive/Documentos/LAMP-13/quinhas-fighters/char-src/quinhas-kun/'
    for a,s in QUINHAS.items():
        print(a,[(f[0].size) for f in frames(root,s)])
