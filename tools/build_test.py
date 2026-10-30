"""Corta uma folha de poses (4x3, fundo branco ou verde) e grava como poses soltas do personagem.
Uso: python build_test.py <folha.png> <id do personagem>
Ordem: parado, flutuar, abaixar, pulo / soco, chute, defesa, levar golpe / hadouken, caindo, nocaute, vitoria.
Todas na mesma escala (uma imagem so); escala ajustada pela altura da defesa antiga."""
import json, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import slice as S
from build_sprites import torso_cx

R='C:/Users/lukin/OneDrive/Documentos/LAMP-13/quinhas-fighters/'
# ajuste fino por pose (tamanho da cabeca igualado ao do parado, medido pela area do rosto)
ADJ={k:1 for k in ['id','wk','cr','jp','pu','ki','bl','ht','hd','fa','ko','vi']}
NAMES=['id','wk','cr','jp','pu','ki','bl','ht','hd','fa','ko','vi']

def key_white(im):
    """Fundo branco -> transparente, so o que esta ligado a borda (o brilho branco do hadouken fica)."""
    rgb=im.convert('RGB');W,H=rgb.size
    r,g,b=rgb.split()
    white=ImageChops.darker(ImageChops.darker(r,g),b).point(lambda v:255 if v>228 else 0)
    m=white.copy()
    for pt in [(0,0),(W-1,0),(0,H-1),(W-1,H-1),(W//2,0),(W//2,H-1),(0,H//2),(W-1,H//2)]:
        if m.getpixel(pt)==255:ImageDraw.floodfill(m,pt,128)
    alpha=m.point(lambda v:0 if v==128 else 255)
    # matte suave sem MinFilter (evita picotar)
    alpha=alpha.filter(ImageFilter.GaussianBlur(.85))
    alpha=alpha.point(lambda v:0 if v<16 else (255 if v>232 else int((v-16)*255/216)))
    out=rgb.convert('RGBA');out.putalpha(alpha);return out

def key_magenta(im):
    """Delegado ao chroma magenta profissional em slice.py."""
    return S.key_magenta(im)

def split_ball(p):
    """Separa o poder (bola) do corpo por componentes conectados. Devolve (corpo, bola recortada, cx, cy da bola)."""
    A=p.split()[3];w,h=A.size;mask=A.point(lambda v:255 if v>100 else 0)
    cw,ch,comps=S.components(mask,2)
    comps=sorted(comps,key=len,reverse=True)
    body_px=comps[0];bx=sum(q%cw for q in body_px)/len(body_px)
    ball_px=[q for c in comps[1:] if len(c)>=120 and sum(q%cw for q in c)/len(c)>bx for q in c]
    def maskof(px):
        m=Image.new('L',(cw,ch),0);mp=m.load()
        for q in px:mp[q%cw,q//cw]=255
        return m.resize((w,h),Image.NEAREST).filter(ImageFilter.MaxFilter(5)).point(lambda v:255 if v>0 else 0)
    mb=maskof(ball_px);mr=maskof(body_px)
    ball=p.copy();body=p.copy()
    ball.putalpha(ImageChops.multiply(A,mb));body.putalpha(ImageChops.multiply(A,mr))
    bb=ball.split()[3].point(lambda v:255 if v>40 else 0).getbbox()
    global BODY_R
    BODY_R=body.split()[3].point(lambda v:255 if v>40 else 0).getbbox()[2]
    return body,ball.crop(bb),(bb[0]+bb[2])/2,(bb[1]+bb[3])/2

def main():
    sheet,cid=sys.argv[1],sys.argv[2];only=set(sys.argv[3].split(',')) if len(sys.argv)>3 else None
    raw=Image.open(sheet)
    if raw.mode=='RGBA' and raw.getpixel((2,2))[3]<10:im=raw.convert('RGBA')
    else:
        px=raw.convert('RGB').getpixel((2,2));r0,g0,b0=px
        if r0>200 and g0>200 and b0>200:im=key_white(raw)
        elif r0>180 and b0>180 and g0<100:im=key_magenta(raw)
        else:im=S.key(raw)
    fr=S.frames_from(im,4,3,12)
    assert len(fr)==12,len(fr)
    old=R+'assets/spr/%s/'%cid
    # escala: mesma altura do parado do Quinhas-Kun (proporcao na luta)
    import os
    qid=R+'assets/spr/q/id.webp'
    if cid!='q' and os.path.exists(qid):
        s=Image.open(qid).size[1]/fr[0][0].size[1];print('match height',Image.open(qid).size[1],'-> s=%.3f'%s)
    else:
        s=395.0/fr[6][0].size[1];print('s=%.3f'%s)
    meta=json.load(open(R+'tools/out/%s_poses.json'%cid)) if only else {}
    s0=s
    for n,(p,bb,cell) in zip(NAMES,fr):
        if only and n not in only:continue
        s=s0*ADJ[n]
        w,h=round(p.size[0]*s),round(p.size[1]*s)
        r=p.resize((w,h),Image.LANCZOS)
        ax=torso_cx(p)*s
        if n=='hd':ax=torso_cx(p.crop((0,0,int(p.size[0]*.65),p.size[1])))*s
        if n in('ko',):ax=w/2
        if n=='hd':
            body,ball,bcx,bcy=split_ball(p);r=body.resize((w,h),Image.LANCZOS)
            bw,bh=round(ball.size[0]*s),round(ball.size[1]*s)
            ball.resize((bw,bh),Image.LANCZOS).save(old+'hb.webp','WEBP',lossless=True)
            meta['hb']={'w':bw,'h':bh,'ax':bw/2,'dx':round(bcx*s-ax,1),'dy':round((p.size[1]-bcy)*s,1),'hx':round(BODY_R*s-ax,1)};print('hb',meta['hb'])
        # lossless evita o encoder reintroduzir fringe verde nas bordas
        r.save(old+'%s.webp'%n,'WEBP',lossless=True)
        meta[n]={'w':w,'h':h,'ax':round(ax,1)};print(n,meta[n])
    json.dump(meta,open(R+'tools/out/%s_poses.json'%cid,'w'))

if __name__=='__main__':main()
