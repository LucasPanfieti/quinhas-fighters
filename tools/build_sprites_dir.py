"""Importa poses soltas de char-src/quinhas-kun/SPRITES/ para assets/spr/q/.
Chroma key profissional + escala pela altura do parado (418px alvo).
Uso: python build_sprites_dir.py
"""
import json, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slice as S
from build_sprites import torso_cx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/') + '/'
SRC = ROOT + 'char-src/quinhas-kun/SPRITES/'
OUT = ROOT + 'assets/spr/q/'
META_PATH = ROOT + 'tools/out/q_poses.json'
IDLE_H = 418          # altura alvo do parado (igual ao quinhas atual no jogo)
PRE_MAX = 1400        # limita o lado maior antes do key (acelera sem perder qualidade no jogo)

# arquivo -> chave de pose no jogo
MAP = {
    '01-parado.png': 'id',
    'andando.jpg': 'wk',
    'andando.png': 'wk',
    'andando-tras.jpg': 'wb',
    'andando-tras.png': 'wb',
    '02-soco.png': 'pu',
    '03-chute.png': 'ki',
    '04-defesa.png': 'bl',
    '05-agachado.png': 'cr',
    '06-soco-agachado.png': 'cp',
    '07-chute-agachado.png': 'ck',
    '08-defesa-agachado.png': 'cb',
    '09-pulando.png': 'jp',
    '10-soco-pulando.png': 'ap',
    '11-chute-pulando.png': 'ak',
    '12-defesa-pulando.png': 'ab',
    '13-hit.jpg': 'ht',
    '13-hit.png': 'ht',
    '14-caindo.jpg': 'fa',
    '14-caindo.png': 'fa',
    '15-nocaute.jpg': 'ko',
    '15-nocaute.png': 'ko',
    '16-vitoria.jpg': 'vi',
    '16-vitoria.png': 'vi',
    'hadouken.png': 'hd',
    'hadouken.jpg': 'hd',
    'esfera.jpg': 'hd',
    'esfera-ki.png': 'hb',
}


def _prepare(path):
    """Abre, reduz se gigante, aplica key e recorta bbox."""
    im = Image.open(path)
    w, h = im.size
    m = max(w, h)
    if m > PRE_MAX:
        s = PRE_MAX / m
        im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    keyed = S.key(im)
    bb = keyed.split()[3].point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bb:
        raise RuntimeError('sem silhueta: ' + path)
    return keyed.crop(bb)


def _worker(item):
    fn, key = item
    t0 = time.time()
    crop = _prepare(SRC + fn)
    return key, fn, crop, time.time() - t0


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    if os.path.exists(META_PATH):
        meta = json.load(open(META_PATH))

    items = [(fn, k) for fn, k in MAP.items() if os.path.exists(SRC + fn)]
    missing = [fn for fn in MAP if not os.path.exists(SRC + fn)]
    if missing:
        print('faltando:', missing)

    crops = {}
    # processa em paralelo (key e o gargalo)
    workers = min(4, max(1, os.cpu_count() or 2))
    print('keying %d poses com %d workers...' % (len(items), workers))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_worker, it) for it in items]
        for fut in as_completed(futs):
            key, fn, crop, dt = fut.result()
            crops[key] = crop
            print('  %s <- %s  %s  %.1fs' % (key, fn, crop.size, dt))

    if 'id' not in crops:
        raise SystemExit('precisa de 01-parado.png')

    # escala global pelo parado
    g = IDLE_H / crops['id'].size[1]
    print('scale g=%.4f (idle %d -> %d)' % (g, crops['id'].size[1], IDLE_H))

    # wk: reusa o parado (ainda nao tem tira de andar nesta pasta)
    if 'wk' not in crops:
        crops['wk'] = crops['id'].copy()

    for key, crop in crops.items():
        s = g
        # esfera um pouco menor relativa (opcional fine-tune)
        if key == 'hb':
            # bola ~35% da altura do parado (nao escala como corpo)
            s = (IDLE_H * 0.35) / crop.size[1]
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
        r.save(OUT + key + '.webp', 'WEBP', lossless=True)
        meta[key] = entry
        print('save', key, entry)

    # offsets da bola depois do hd estar no meta
    if 'hb' in meta and 'hd' in meta:
        hd = meta['hd']
        meta['hb'].update({
            'dx': round(hd['w'] * 0.55, 1),
            'dy': round(hd['h'] * 0.69, 1),
            'hx': round(hd['w'] * 0.42, 1),
        })
        print('hb offsets', meta['hb'])

    # wk meta se so copiamos o id
    if 'wk' in crops:
        meta['wk'] = dict(meta['id'])

    json.dump(meta, open(META_PATH, 'w'))
    print('meta ->', META_PATH)
    print('pronto. Atualize index.html (q.m + ?v=) ou rode o patch abaixo.')


def patch_index(v=9):
    """Reescreve o bloco q:{...} do index.html com meta atual."""
    meta = json.load(open(META_PATH))
    path = ROOT + 'index.html'
    s = open(path, encoding='utf-8').read()
    # encontra q: { ... }, r: {
    start = s.find('q: {\n          id: "assets/spr/q/')
    if start < 0:
        start = s.find('q:{id:"assets/spr/q/')
    if start < 0:
        raise SystemExit('bloco q nao encontrado')
    # fim = proximo personagem no mesmo nivel (r:)
    # preserva a virgula antes de r:
    end = s.find('\n        r: {', start)
    if end < 0:
        end = s.find(',r:{', start)
    if end < 0:
        raise SystemExit('bloco r nao encontrado')
    # se o trecho anterior ao r ja tinha "}," consumido mal, o end aponta ao \n antes de r

    # ordem estavel: keys do meta, hb depois de hd se ambos
    keys = [k for k in (
        'id', 'wk', 'cr', 'jp', 'pu', 'ki', 'bl', 'ht', 'hb', 'hd', 'fa', 'ko', 'vi',
        'ck', 'cp', 'ap', 'ak', 'cb', 'ab', 'wb',
    ) if k in meta]
    for k in meta:
        if k not in keys:
            keys.append(k)

    lines = ['        q: {']
    for k in keys:
        lines.append('          %s: "assets/spr/q/%s.webp?v=%d",' % (k, k, v))
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
    print('index.html patch ok (v=%d)' % v)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'patch':
        patch_index(int(sys.argv[2]) if len(sys.argv) > 2 else 9)
    else:
        main()
        patch_index(9)
