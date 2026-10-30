"""Ferramenta de build: recorta as tiras de animacao (fundo verde) de um personagem.
Usa so Pillow. Chroma key profissional (matte suave + despill + choke de borda),
separa os quadros por componentes conectados e devolve RGBA recortados sem fundo."""
from PIL import Image, ImageChops, ImageFilter, ImageDraw
import os
from collections import deque

# acao: (arquivo, colunas, linhas, quadros)
QUINHAS = {
    'id': ('parado/parado.png', 4, 1, 4), 'wk': ('andar/andar.png', 3, 2, 6),
    'pu': ('soco/soco.png', 4, 1, 4), 'ki': ('chute/chute.png', 4, 1, 4),
    'bl': ('defesa/defesa.png', 2, 1, 2), 'ht': ('levar-golpe/levar-golpe.png', 2, 1, 2),
    'jp': ('pulo/pulo.png', 2, 1, 2), 'ko': ('nocaute/nocaute.png', 2, 2, 4),
}

# verde neon de tela (~#00FD00)
_SCR = (2, 252, 2)


def _smoothstep(e0, e1, x):
    if x <= e0:
        return 0.0
    if x >= e1:
        return 1.0
    t = (x - e0) / (e1 - e0)
    return t * t * (3.0 - 2.0 * t)


def _green_score_u8(r, g, b):
    """Score 0..255: quanto o pixel parece chroma verde neon."""
    mx = r if r > b else b
    dom = g - mx
    if dom <= 0:
        return 0
    # distancia ao verde de tela (aprox.)
    dr, dg, db = r - _SCR[0], g - _SCR[1], b - _SCR[2]
    dist2 = dr * dr + dg * dg + db * db
    # dominancia 8..90 -> 0..1
    d_n = _smoothstep(8, 90, dom)
    # perto da cor de tela (dist ~40..200)
    dist = dist2 ** 0.5
    near = 1.0 - _smoothstep(40, 200, dist)
    purity = 1.0 - min(1.0, (r + b) / 140.0)
    s = 0.55 * d_n + 0.30 * near + 0.15 * purity * d_n
    if s <= 0:
        return 0
    if s >= 1:
        return 255
    return int(s * 255)


def _despill(r, g, b, strength):
    mx = r if r > b else b
    if g <= mx:
        return r, g, b
    spill = (g - mx) * strength
    ng = int(g - spill)
    if strength > 0.6 and spill > 20:
        boost = int(spill * 0.10)
        r = min(255, r + boost)
        b = min(255, b + boost)
    return r, max(0, ng), b


def key(im):
    """Remove verde neon com matte suave, unblend de tela e despill.
    Fundo ligado a borda (e buracos de chroma puro) some; verde de roupa/poder fica.
    Sem MinFilter na silhueta — evita o corte 'picotado'."""
    rgb = im.convert('RGB')
    W, H = rgb.size
    R, G, B = (c.tobytes() for c in rgb.split())
    N = W * H
    sr, sg, sb = _SCR

    # --- 1) score + candidatos duros ---
    score = bytearray(N)
    hard = bytearray(N)
    for i in range(N):
        s = _green_score_u8(R[i], G[i], B[i])
        score[i] = s
        if s >= 184 and G[i] > 150 and R[i] < 70 and B[i] < 70:
            hard[i] = 255

    fill = Image.frombytes('L', (W, H), bytes(hard))
    for pt in ((0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1),
               (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2)):
        if fill.getpixel(pt) == 255:
            ImageDraw.floodfill(fill, pt, 128)

    # buracos fechados (ex.: entre braço e ombro): todo chroma duro some,
    # nao so o ligado a borda
    bg = fill.point(lambda v: 255 if v in (128, 255) else 0)
    bg_dil = bg.filter(ImageFilter.MaxFilter(5))
    bp = bytearray(bg.tobytes())
    bdp = bg_dil.tobytes()
    for i in range(N):
        if bp[i] == 0 and score[i] >= 224 and bdp[i] == 255:
            bp[i] = 255
        # verde de tela "sujo" preso no buraco (mais escuro que o neon puro)
        if bp[i] == 0 and score[i] >= 150:
            rv, gv, bv = R[i], G[i], B[i]
            if gv > 105 and gv > rv + 18 and gv > bv + 18 and rv < 110 and bv < 110:
                bp[i] = 255
    bg = Image.frombytes('L', (W, H), bytes(bp))
    near_bg = bg.filter(ImageFilter.MaxFilter(9))
    nbp = near_bg.tobytes()

    # --- 2) matte: fundo por score; fringe do FG preserva AA (mistura outline+tela) ---
    alpha_b = bytearray(N)
    for i in range(N):
        rv, gv, bv = R[i], G[i], B[i]
        s = score[i] / 255.0
        if bp[i] == 255:
            # fundo: soft key (rampa larga = menos picotado)
            t = _smoothstep(0.15, 0.58, s)
            alpha_b[i] = int(255 * (1.0 - t))
        elif nbp[i] == 255:
            mx = rv if rv > bv else bv
            spill = gv - mx
            lum = rv if rv > gv else gv
            if bv > lum:
                lum = bv
            if spill <= 2 and s < 0.10:
                alpha_b[i] = 255
            elif lum < 50 and gv > mx:
                # contorno preto misturado com verde: a ≈ 1 - g/sg (mantém AA)
                af = 1.0 - min(1.0, gv / float(sg))
                # se ainda tem pigmento do FG, nao zera
                af = max(af, 1.0 - _smoothstep(2, 48, spill))
                alpha_b[i] = int(255 * max(0.0, min(1.0, af)))
            else:
                # pele/roupa na borda: rampa pelo excesso de verde
                t = _smoothstep(3, 52, spill)
                alpha_b[i] = int(255 * (1.0 - t))
        else:
            alpha_b[i] = 255

    alpha = Image.frombytes('L', (W, H), bytes(alpha_b))
    # blur proporcional ao tamanho (em 3k px, raio fixo 0.8 some)
    blur_r = max(0.7, min(2.2, min(W, H) / 1400.0))
    alpha = alpha.filter(ImageFilter.GaussianBlur(blur_r))
    # levels suaves: preserva rampa de AA no meio
    alpha = alpha.point(lambda v: 0 if v < 8 else (255 if v > 248 else int((v - 8) * 255 / 240)))

    ap = alpha.tobytes()

    # --- 3) unblend da tela + despill ---
    out_b = bytearray(N * 4)
    for i in range(N):
        a = ap[i]
        o = i * 4
        if a < 8:
            out_b[o:o + 4] = b'\x00\x00\x00\x00'
            continue
        rv, gv, bv = R[i], G[i], B[i]
        s = score[i] / 255.0

        if s >= 0.82 and gv > 150 and rv < 85 and bv < 85:
            out_b[o:o + 4] = b'\x00\x00\x00\x00'
            continue

        af = a / 255.0
        # descontaminacao: C = F*a + S*(1-a)  =>  F = (C - S*(1-a)) / a
        if af < 0.995 and (nbp[i] == 255 or a < 250):
            ia = 1.0 - af
            fr = (rv - sr * ia) / af
            fg = (gv - sg * ia) / af
            fb = (bv - sb * ia) / af
            rv = 0 if fr < 0 else (255 if fr > 255 else int(fr))
            gv = 0 if fg < 0 else (255 if fg > 255 else int(fg))
            bv = 0 if fb < 0 else (255 if fb > 255 else int(fb))

        mx = rv if rv > bv else bv
        lum = max(rv, gv, bv)

        # outline preto ainda contaminado
        if a < 240 and lum < 55 and gv >= mx:
            if lum < 28 or gv > mx + 2:
                out_b[o:o + 4] = b'\x00\x00\x00\x00'
                continue
            v = (rv + bv) // 2
            out_b[o] = out_b[o + 1] = out_b[o + 2] = v
            out_b[o + 3] = a
            continue

        if gv > mx:
            strength = 1.0 if a < 220 else (0.85 if nbp[i] == 255 else 0.45)
            rv, gv, bv = _despill(rv, gv, bv, strength)

        out_b[o] = rv
        out_b[o + 1] = gv
        out_b[o + 2] = bv
        out_b[o + 3] = a

    out = Image.frombytes('RGBA', (W, H), bytes(out_b))
    return _punch_green_holes(out)


def _punch_green_holes(im, max_comp=900):
    """Remove ilhas pequenas de verde residual (buraco braço/ombro etc.)."""
    W, H = im.size
    px = im.load()
    N = W * H
    mark = bytearray(N)
    for y in range(H):
        row = y * W
        for x in range(W):
            r, g, b, a = px[x, y]
            if a < 24:
                continue
            if g > 95 and g > r + 16 and g > b + 16 and r < 135 and b < 135 and (r + b) < g + 55:
                mark[row + x] = 1

    seen = bytearray(N)
    for i in range(N):
        if not mark[i] or seen[i]:
            continue
        stack = [i]
        seen[i] = 1
        comp = []
        while stack:
            j = stack.pop()
            comp.append(j)
            x, y = j % W, j // W
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if nx < 0 or ny < 0 or nx >= W or ny >= H:
                    continue
                k = ny * W + nx
                if mark[k] and not seen[k]:
                    seen[k] = 1
                    stack.append(k)
        if len(comp) > max_comp:
            continue
        for j in comp:
            x, y = j % W, j // W
            px[x, y] = (0, 0, 0, 0)
    return im


def key_magenta(im):
    """Fundo magenta/rosa (#FF00F2) -> transparente, matte suave + despill."""
    rgb = im.convert('RGB')
    W, H = rgb.size
    R, G, B = rgb.split()
    Rb, Gb, Bb = R.tobytes(), G.tobytes(), B.tobytes()
    N = W * H
    alpha_b = bytearray(N)
    for i in range(N):
        rv, gv, bv = Rb[i], Gb[i], Bb[i]
        dom = (rv if rv < bv else bv) - gv
        if dom <= 0:
            alpha_b[i] = 255
            continue
        s = _smoothstep(20, 100, dom)
        if rv > 180 and bv > 140:
            s = max(s, _smoothstep(40, 120, dom))
        alpha_b[i] = int(255 * (1.0 - s))

    alpha = Image.frombytes('L', (W, H), bytes(alpha_b))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.85))
    alpha = alpha.point(lambda v: 0 if v < 16 else (255 if v > 232 else int((v - 16) * 255 / 216)))

    ap = alpha.tobytes()
    sr, sg, sb = 255, 0, 242  # #FF00F2
    out_b = bytearray(N * 4)
    for i in range(N):
        a = ap[i]
        o = i * 4
        if a < 8:
            out_b[o:o + 4] = b'\x00\x00\x00\x00'
            continue
        rv, gv, bv = Rb[i], Gb[i], Bb[i]
        af = a / 255.0
        if af < 0.995 and a < 250:
            ia = 1.0 - af
            fr = (rv - sr * ia) / af
            fg = (gv - sg * ia) / af
            fb = (bv - sb * ia) / af
            rv = 0 if fr < 0 else (255 if fr > 255 else int(fr))
            gv = 0 if fg < 0 else (255 if fg > 255 else int(fg))
            bv = 0 if fb < 0 else (255 if fb > 255 else int(fb))
        if rv > gv + 20 and bv > gv + 20:
            spill = (rv if rv < bv else bv) - gv
            if spill > 0:
                k = 0.9 if a < 200 else 0.55
                rv = max(gv, int(rv - spill * k))
                bv = max(gv, int(bv - spill * k))
        out_b[o] = rv
        out_b[o + 1] = gv
        out_b[o + 2] = bv
        out_b[o + 3] = a
    return Image.frombytes('RGBA', (W, H), bytes(out_b))


def components(mask, f=2):
    """Componentes conectados (8-viz.) numa versao reduzida por f."""
    W, H = mask.size
    w, h = W // f, H // f
    small = mask.resize((w, h), Image.BOX).point(lambda v: 255 if v > 0 else 0)
    d = small.tobytes()
    lab = [0] * (w * h)
    comps = []
    for i in range(w * h):
        if d[i] and not lab[i]:
            n = len(comps) + 1
            q = deque([i])
            lab[i] = n
            px = []
            while q:
                p = q.popleft()
                px.append(p)
                y, x = divmod(p, w)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < h and 0 <= xx < w:
                            k = yy * w + xx
                            if d[k] and not lab[k]:
                                lab[k] = n
                                q.append(k)
            comps.append(px)
    return w, h, comps


def frames(root, spec):
    fn, cols, rows, n = spec
    return frames_from(key(Image.open(os.path.join(root, fn))), cols, rows, n)


def frames_from(im, cols, rows, n):
    """Lista de (imagem recortada, bbox na origem, origem x da celula nominal)."""
    W, H = im.size
    F = 2
    mask = im.split()[3].point(lambda v: 255 if v > 100 else 0)
    w, h, comps = components(mask, F)
    cw, ch = W / cols, H / rows
    cells = {}
    for px in comps:
        if len(px) < 25:
            continue
        xs = [p % w for p in px]
        ys = [p // w for p in px]
        cx = (sum(xs) / len(xs)) * F
        cy = (sum(ys) / len(ys)) * F
        c = min(cols - 1, int(cx // cw))
        r = min(rows - 1, int(cy // ch))
        cells.setdefault((r, c), []).extend(px)
    out = []
    for r in range(rows):
        for c in range(cols):
            if len(out) >= n:
                break
            px = cells.get((r, c))
            if not px:
                continue
            m = Image.new('L', (w, h), 0)
            mp = m.load()
            for p in px:
                mp[p % w, p // w] = 255
            m = m.resize((W, H), Image.NEAREST).filter(ImageFilter.MaxFilter(5))
            m = m.filter(ImageFilter.GaussianBlur(0.6)).point(lambda v: 255 if v > 40 else 0)
            piece = im.copy()
            piece.putalpha(ImageChops.multiply(im.split()[3], m))
            bb = piece.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox()
            out.append((piece.crop(bb), bb, (int(round(c * cw)), int(round(r * ch)))))
    return out


if __name__ == '__main__':
    root = 'C:/Users/lukin/OneDrive/Documentos/LAMP-13/quinhas-fighters/char-src/quinhas-kun/'
    for a, s in QUINHAS.items():
        print(a, [(f[0].size) for f in frames(root, s)])
