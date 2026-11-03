"""Importa poses soltas de char-src/<char>/SPRITES/ para assets/spr/<id>/.
Chroma key profissional + escala pela altura do parado (418px alvo).

Uso:
  python build_sprites_dir.py              # Quinhas (q) — padrao
  python build_sprites_dir.py u char-src/luan-zin/SPRITES/ 12
  python build_sprites_dir.py patch u 12   # so atualiza index.html
"""
import json, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slice as S
from build_sprites import torso_cx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/') + '/'
IDLE_H = 418
PRE_MAX = 1400

# arquivo -> chave (ordem = prioridade: v2 rosa primeiro, depois originais)
MAP = {
    '01-parado-2.png': 'id', '01-parado-2.jpg': 'id',
    '01-parado.png': 'id', '01-parado.jpg': 'id',
    'andando-2.jpg': 'wk', 'andando-2.png': 'wk',
    'andando.jpg': 'wk', 'andando.png': 'wk',
    'andando-tras-2.jpg': 'wb', 'andando-tras-2.png': 'wb',
    'andando-tras.jpg': 'wb', 'andando-tras.png': 'wb',
    '02-soco-2.png': 'pu', '02-soco-2.jpg': 'pu',
    '02-soco.png': 'pu', '02-soco.jpg': 'pu',
    '03-chute-2.png': 'ki', '03-chute-2.jpg': 'ki',
    '03-chute.png': 'ki', '03-chute.jpg': 'ki',
    '04-defesa-2.png': 'bl', '04-defesa-2.jpg': 'bl',
    '04-defesa.png': 'bl', '04-defesa.jpg': 'bl',
    '05-agachado-2.png': 'cr', '05-agachado-2.jpg': 'cr',
    '05-agachado.png': 'cr', '05-agachado.jpg': 'cr',
    '06-soco-agachado-2.png': 'cp', '06-soco-agachado-2.jpg': 'cp',
    '06-soco-agachado.png': 'cp', '06-soco-agachado.jpg': 'cp',
    '07-chute-agachado-2.png': 'ck', '07-chute-agachado-2.jpg': 'ck',
    '07-chute-agachado.png': 'ck', '07-chute-agachado.jpg': 'ck',
    '08-defesa-agachado-2.png': 'cb', '08-defesa-agachado-2.jpg': 'cb',
    '08-defesa-agachado.png': 'cb', '08-defesa-agachado.jpg': 'cb',
    '09-pulando-2.png': 'jp', '09-pulando-2.jpg': 'jp',
    '09-pulando.png': 'jp', '09-pulando.jpg': 'jp',
    '10-soco-pulando-2.png': 'ap', '10-soco-pulando-2.jpg': 'ap',
    '10-soco-pulando.png': 'ap', '10-soco-pulando.jpg': 'ap',
    '11-chute-pulando-2.png': 'ak', '11-chute-pulando-2.jpg': 'ak',
    '11-chute-pulando.png': 'ak', '11-chute-pulando.jpg': 'ak',
    '12-defesa-pulando-2.png': 'ab', '12-defesa-pulando-2.jpg': 'ab',
    '12-defesa-pulando.png': 'ab', '12-defesa-pulando.jpg': 'ab',
    '13-hit-2.jpg': 'ht', '13-hit-2.png': 'ht',
    '13-hit.jpg': 'ht', '13-hit.png': 'ht',
    '14-caindo-2.jpg': 'fa', '14-caindo-2.png': 'fa',
    '14-caindo.jpg': 'fa', '14-caindo.png': 'fa',
    '15-nocaute-2.jpg': 'ko', '15-nocaute-2.png': 'ko',
    '15-nocaute.jpg': 'ko', '15-nocaute.png': 'ko',
    '16-vitoria-2.jpg': 'vi', '16-vitoria-2.png': 'vi',
    '16-vitoria.jpg': 'vi', '16-vitoria.png': 'vi',
    'hadouken-2.png': 'hd', 'hadouken-2.jpg': 'hd',
    'hadouken.png': 'hd', 'hadouken.jpg': 'hd',
    'esfera-ki2.png': 'hb', 'esfera-ki2.jpg': 'hb',
    'esfera-ki-2.png': 'hb', 'esfera-ki-2.jpg': 'hb',
    'esfera.jpg': 'hb', 'esfera-ki.png': 'hb', 'esfera-ki.jpg': 'hb',
}

POSE_ORDER = [
    'id', 'wk', 'cr', 'jp', 'pu', 'ki', 'bl', 'ht', 'hb', 'hd', 'fa', 'ko', 'vi',
    'ck', 'cp', 'ap', 'ak', 'cb', 'ab', 'wb',
]

# padrao: Quinhas
DEFAULT_CID = 'q'
DEFAULT_SRC = ROOT + 'char-src/quinhas-kun/SPRITES/'


def _pick_key(im):
    """Escolhe chroma pelo canto: magenta/rosa, branco, ou verde neon."""
    rgb = im.convert('RGB')
    r0, g0, b0 = rgb.getpixel((2, 2))
    if r0 > 180 and b0 > 180 and g0 < 100:
        return S.key_magenta(im)
    if r0 > 200 and g0 > 200 and b0 > 200:
        from build_test import key_white
        return key_white(im)
    return S.key(im)


def _prepare(path):
    """Abre, reduz se gigante, aplica key e recorta bbox."""
    im = Image.open(path)
    w, h = im.size
    m = max(w, h)
    if m > PRE_MAX:
        s = PRE_MAX / m
        im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    keyed = _pick_key(im)
    bb = keyed.split()[3].point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bb:
        raise RuntimeError('sem silhueta: ' + path)
    return keyed.crop(bb)


def _worker(item):
    path, key, fn = item
    t0 = time.time()
    crop = _prepare(path)
    return key, fn, crop, time.time() - t0


def _band_median_width(im, y0f, y1f):
    """Largura mediana da silhueta numa faixa vertical relativa."""
    import numpy as np
    a = np.asarray(im.split()[3]) > 20
    ys = np.where(a.any(axis=1))[0]
    if len(ys) == 0:
        return 1.0
    y0, y1 = int(ys[0]), int(ys[-1])
    sh = max(1, y1 - y0 + 1)
    lo = y0 + int(sh * y0f)
    hi = y0 + max(lo + 1, int(sh * y1f))
    widths = a[lo:hi].sum(axis=1).astype(float)
    widths = widths[widths > 0]
    return float(np.median(widths)) if len(widths) else 1.0


def _face_w(im):
    return _band_median_width(im, 0.04, 0.13)


def _shoulder_w(im):
    return _band_median_width(im, 0.12, 0.30)


def _pose_scale_adj(crop, idle_face, idle_shoulder, key):
    """Fator pra igualar o tamanho do personagem ao parado (evita 'crescer' no golpe)."""
    if key in ('hb', 'ko'):
        return 1.0
    # defesa: bracos na frente da cara inflam face_w — nao mexe na escala
    if key in ('bl', 'ab'):
        return 1.0
    face = max(1.0, _face_w(crop))
    shoulder = max(1.0, _shoulder_w(crop))
    adj_f = idle_face / face
    adj_s = idle_shoulder / shoulder
    # cabeca e a metrica mais estavel; ombro e fallback
    if 0.78 <= adj_f <= 1.20:
        adj = adj_f
    elif 0.80 <= adj_s <= 1.20:
        adj = adj_s
    else:
        adj = 1.0
    # agachado pode precisar encolher mais (fonte vem maior)
    lo = 0.82 if key in ('cr', 'cp', 'ck', 'cb') else 0.88
    return max(lo, min(1.12, adj))


def _is_v2_name(fn):
    n = fn.lower()
    return ('-2.' in n) or n.endswith('2.png') or n.endswith('2.jpg') or '-2' in n


def build(cid, src, v=12, prefer_v2=True):
    src = src.replace('\\', '/')
    if not src.endswith('/'):
        src += '/'
    out = ROOT + 'assets/spr/%s/' % cid
    meta_path = ROOT + 'tools/out/%s_poses.json' % cid
    os.makedirs(out, exist_ok=True)

    meta = {}
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path))

    # se png e jpg existem pro mesmo key, prefere o que MAP lista primeiro
    chosen = {}
    for fn, key in MAP.items():
        if key in chosen:
            continue
        if not prefer_v2 and _is_v2_name(fn):
            continue
        if prefer_v2 is False:
            pass
        if os.path.exists(src + fn):
            chosen[key] = fn

    items = [(src + fn, key, fn) for key, fn in chosen.items()]
    print('src', src)
    print('out', out)
    print('poses', sorted(chosen.keys()))
    missing_keys = [k for k in ('id', 'pu', 'ki', 'bl') if k not in chosen]
    if missing_keys:
        print('aviso: faltando basicos', missing_keys)

    crops = {}
    workers = min(4, max(1, os.cpu_count() or 2))
    print('keying %d poses com %d workers...' % (len(items), workers))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_worker, it) for it in items]
        for fut in as_completed(futs):
            key, fn, crop, dt = fut.result()
            crops[key] = crop
            print('  %s <- %s  %s  %.1fs' % (key, fn, crop.size, dt))

    if 'id' not in crops:
        raise SystemExit('precisa de 01-parado')

    g = IDLE_H / crops['id'].size[1]
    print('scale g=%.4f (idle %d -> %d)' % (g, crops['id'].size[1], IDLE_H))

    idle_face = _face_w(crops['id'])
    idle_shoulder = _shoulder_w(crops['id'])
    print('idle face_w=%.1f shoulder_w=%.1f' % (idle_face, idle_shoulder))

    wk_from_id = False
    if 'wk' not in crops:
        crops['wk'] = crops['id'].copy()
        wk_from_id = True

    for key, crop in crops.items():
        adj = _pose_scale_adj(crop, idle_face, idle_shoulder, key)
        s = g * adj
        if key == 'hb':
            s = (IDLE_H * 0.35) / crop.size[1]
            adj = 1.0
        w = max(1, round(crop.size[0] * s))
        h = max(1, round(crop.size[1] * s))
        r = crop.resize((w, h), Image.LANCZOS)
        if key == 'hb':
            ax = w / 2
        elif key == 'ko':
            ax = w / 2
        elif key in ('hd', 'pu', 'ap', 'cp'):
            ax = torso_cx(crop.crop((0, 0, int(crop.size[0] * 0.68), crop.size[1]))) * s
        elif key in ('ki', 'ak', 'ck'):
            left = int(crop.size[0] * 0.15)
            body = crop.crop((left, 0, int(crop.size[0] * 0.75), crop.size[1]))
            ax = (torso_cx(body) + left) * s
        else:
            ax = torso_cx(crop) * s

        entry = {'w': w, 'h': h, 'ax': round(ax, 1)}
        r.save(out + key + '.webp', 'WEBP', lossless=True)
        meta[key] = entry
        print('save', key, entry, 'adj=%.3f' % adj)

    if 'hb' in meta and 'hd' in meta:
        hd = meta['hd']
        meta['hb'].update({
            'dx': round(hd['w'] * 0.55, 1),
            'dy': round(hd['h'] * 0.69, 1),
            'hx': round(hd['w'] * 0.42, 1),
        })
        print('hb offsets', meta['hb'])

    if wk_from_id:
        meta['wk'] = dict(meta['id'])

    # remove poses velhas do sheet 4x3 que nao existem mais no kit solto? manter extras ok
    json.dump(meta, open(meta_path, 'w'))
    print('meta ->', meta_path)
    patch_index(cid, v)
    return meta


def patch_index(cid, v=12):
    """Reescreve o bloco SPR.<cid> do index.html com meta atual."""
    meta_path = ROOT + 'tools/out/%s_poses.json' % cid
    meta = json.load(open(meta_path))
    path = ROOT + 'index.html'
    s = open(path, encoding='utf-8').read()

    marker = '%s: {\n          id: "assets/spr/%s/' % (cid, cid)
    start = s.find(marker)
    if start < 0:
        # fallback: linha com id url
        start = s.find('%s: {\n          id: "assets/spr/%s/' % (cid, cid))
    if start < 0:
        # try without newline quirks
        import re
        m = re.search(r'\b%s:\s*\{\s*\n\s*id:\s*"assets/spr/%s/' % (cid, cid), s)
        if not m:
            raise SystemExit('bloco %s nao encontrado' % cid)
        start = m.start()

    # fim = proximo personagem no mesmo nivel (2 espacos a menos que o miolo)
    # blocos sao "        x: {" — achar proximo "\n        <letter>: {" depois de start+1
    import re
    nxt = re.search(r'\n        [a-z]: \{', s[start + 1:])
    if not nxt:
        raise SystemExit('proximo bloco apos %s nao encontrado' % cid)
    end = start + 1 + nxt.start()

    keys = [k for k in POSE_ORDER if k in meta]
    for k in meta:
        if k not in keys:
            keys.append(k)

    lines = ['        %s: {' % cid]
    for k in keys:
        lines.append('          %s: "assets/spr/%s/%s.webp?v=%d",' % (k, cid, k, v))
    lines.append('          m: {')
    for i, k in enumerate(keys):
        m = meta[k]
        parts = ['w: %d' % m['w'], 'h: %d' % m['h'], 'ax: %s' % m['ax']]
        for extra in ('dx', 'dy', 'hx'):
            if extra in m:
                parts.append('%s: %s' % (extra, m[extra]))
        comma = ',' if i < len(keys) - 1 else ''
        lines.append('            %s: { %s }%s' % (k, ', '.join(parts), comma))
    lines.append('          },')
    lines.append('        },')
    block = '\n'.join(lines)
    s = s[:start] + block + s[end:]
    open(path, 'w', encoding='utf-8').write(s)
    print('index.html patch ok (%s v=%d)' % (cid, v))


if __name__ == '__main__':
    args = sys.argv[1:]
    prefer_v2 = True
    if '--orig' in args:
        prefer_v2 = False
        args = [a for a in args if a != '--orig']
    if '--v2' in args:
        prefer_v2 = True
        args = [a for a in args if a != '--v2']
    if args and args[0] == 'patch':
        cid = args[1] if len(args) > 1 else DEFAULT_CID
        v = int(args[2]) if len(args) > 2 else 12
        patch_index(cid, v)
    elif not args:
        build(DEFAULT_CID, DEFAULT_SRC, 23)
    else:
        cid = args[0]
        src = args[1] if len(args) > 1 else DEFAULT_SRC
        if cid != 'q' and (len(args) < 2 or args[1].startswith('-')):
            known = {
                'u': ROOT + 'char-src/luan-zin/SPRITES/',
                'q': DEFAULT_SRC,
            }
            src = known.get(cid, src)
            rest = args[1:]
        else:
            rest = args[2:]
        v = 12
        for a in rest:
            if a.isdigit():
                v = int(a)
        if len(args) > 1 and not args[1].startswith('-') and not args[1].isdigit():
            src = args[1]
            if len(args) > 2 and args[2].isdigit():
                v = int(args[2])
        build(cid, src, v, prefer_v2=prefer_v2)
