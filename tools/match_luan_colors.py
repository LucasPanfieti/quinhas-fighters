"""Equaliza pele / verde / cabelo / gi dos sprites do Luan pelo frame parado (id).
Usa matching de histograma em Lab por classe. Nao mexe em contorno puro nem hb.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPR = ROOT / "assets" / "spr" / "u"
BACKUP = ROOT / "tools" / "out" / "luan_pre_color"
SKIP = {"hb", "id"}
REF = "id"

M_RGB_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ],
    dtype=np.float64,
)
M_XYZ_RGB = np.linalg.inv(M_RGB_XYZ)


def srgb_to_linear(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * (c ** (1 / 2.4)) - 0.055)


def rgb_to_lab(rgb):
    lin = srgb_to_linear(np.clip(rgb, 0, 255) / 255.0)
    xyz = lin @ M_RGB_XYZ.T
    x, y, z = xyz[..., 0] / 0.95047, xyz[..., 1], xyz[..., 2] / 1.08883

    def f(t):
        return np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)

    fx, fy, fz = f(x), f(y), f(z)
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], -1)


def lab_to_rgb(lab):
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def finv(t):
        t3 = t**3
        return np.where(t3 > 0.008856, t3, (t - 16 / 116) / 7.787)

    xyz = np.stack(
        [finv(fx) * 0.95047, finv(fy), finv(fz) * 1.08883], -1
    )
    return linear_to_srgb(xyz @ M_XYZ_RGB.T) * 255.0


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0] / 255.0, rgb[..., 1] / 255.0, rgb[..., 2] / 255.0
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    df = mx - mn
    h = np.zeros_like(mx)
    mask = df > 1e-6
    rq, gq, bq = mask & (mx == r), mask & (mx == g), mask & (mx == b)
    h[rq] = ((g[rq] - b[rq]) / df[rq]) % 6
    h[gq] = (b[gq] - r[gq]) / df[gq] + 2
    h[bq] = (r[bq] - g[bq]) / df[bq] + 4
    h /= 6.0
    s = np.where(mx > 1e-6, df / np.maximum(mx, 1e-6), 0.0)
    return h, s, mx


def classify(rgba):
    rgb = rgba[..., :3].astype(np.float32)
    m = rgba[..., 3] > 128
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = (r + g + b) / 3.0
    h, s, v = rgb_to_hsv(rgb)

    outline = m & (lum < 28)  # contorno puro — intacto
    body = m & ~outline

    green = (
        body
        & (g > r + 5)
        & (g > b + 3)
        & (g > 38)
        & (lum < 195)
        & (((h > 0.20) & (h < 0.55)) | ((g - r > 10) & (g - b > 6)))
    )

    skin = (
        body
        & ~green
        & (r > 90)
        & (g > 50)
        & (b > 28)
        & (r > g + 4)
        & (r > b + 10)
        & (r - b > 14)
        & (g - b < 100)
        & (lum > 60)
        & (lum < 240)
        & (s > 0.06)
        & (s < 0.78)
        & ((h < 0.14) | (h > 0.90))
    )

    # loiro/creme do topo + castanho das laterais
    hair = (
        body
        & ~green
        & ~skin
        & (lum > 30)
        & (lum < 230)
        & (r > 40)
        & (r >= g - 18)
        & (g >= b - 10)
        & (r - b > 4)
        & (
            ((lum > 100) & (s < 0.50) & (r > 110))  # loiro
            | ((lum <= 100) & (s > 0.04) & (r > 35))  # castanho
        )
    )

    # gi / calça / bota carvao (cinza escuro, pouca sat)
    cloth = (
        body
        & ~green
        & ~skin
        & ~hair
        & (lum >= 28)
        & (lum < 115)
        & (s < 0.28)
    )

    return {
        "skin": skin,
        "green": green,
        "hair": hair,
        "cloth": cloth,
    }


def hist_match_channel(src, ref):
    """src, ref: 1D float arrays -> src mapped to ref distribution."""
    if len(src) < 20 or len(ref) < 20:
        return src
    # quantize lightly for stable CDF
    s = np.clip(src, -50, 150)
    r = np.clip(ref, -50, 150)
    # use percentile mapping (robust)
    qs = np.linspace(0, 100, 64)
    s_p = np.percentile(s, qs)
    r_p = np.percentile(r, qs)
    # ensure strictly increasing for interp
    for arr in (s_p, r_p):
        for i in range(1, len(arr)):
            if arr[i] <= arr[i - 1]:
                arr[i] = arr[i - 1] + 1e-4
    return np.interp(s, s_p, r_p)


def match_class(lab_src, lab_ref, mask_s, mask_r):
    if mask_s.sum() < 30 or mask_r.sum() < 30:
        return
    for c in range(3):
        lab_src[..., c][mask_s] = hist_match_channel(
            lab_src[..., c][mask_s], lab_ref[..., c][mask_r]
        )


def match_pose(ref_rgba, pose_rgba):
    out = pose_rgba.astype(np.float32).copy()
    lab_r = rgb_to_lab(ref_rgba[..., :3].astype(np.float32))
    lab_s = rgb_to_lab(pose_rgba[..., :3].astype(np.float32))
    cr, cs = classify(ref_rgba), classify(pose_rgba)
    for key in ("skin", "green", "hair", "cloth"):
        match_class(lab_s, lab_r, cs[key], cr[key])
    rgb = lab_to_rgb(lab_s)
    touched = cs["skin"] | cs["green"] | cs["hair"] | cs["cloth"]
    out[touched, :3] = np.clip(rgb[touched], 0, 255)
    out[..., 3] = pose_rgba[..., 3]
    return out.astype(np.uint8), {k: int(cs[k].sum()) for k in cs}


def skin_mean(rgba):
    m = classify(rgba)["skin"]
    if not m.any():
        return np.zeros(3)
    return rgba[m][:, :3].mean(0)


def main():
    # restaura do backup se existir (pra poder re-rodar limpo)
    if BACKUP.is_dir():
        for p in BACKUP.glob("*.webp"):
            Image.open(p).save(SPR / p.name, "WEBP", quality=92, method=6)
        print("restored from backup")

    ref = np.array(Image.open(SPR / f"{REF}.webp").convert("RGBA"))
    print("ref", {k: int(v.sum()) for k, v in classify(ref).items()})
    ref_skin = skin_mean(ref)

    for name in sorted(
        p.stem for p in SPR.glob("*.webp") if p.stem not in SKIP
    ):
        src_path = (
            BACKUP / f"{name}.webp" if (BACKUP / f"{name}.webp").exists() else SPR / f"{name}.webp"
        )
        src = np.array(Image.open(src_path).convert("RGBA"))
        before = skin_mean(src)
        out, counts = match_pose(ref, src)
        Image.fromarray(out).save(SPR / f"{name}.webp", "WEBP", quality=92, method=6)
        after = skin_mean(out)
        print(
            f"{name:3} skin {before[0]:5.1f}->{after[0]:5.1f} "
            f"(ref {ref_skin[0]:.1f})  "
            f"s/g/h/c={counts['skin']}/{counts['green']}/{counts['hair']}/{counts['cloth']}"
        )

    tiles = [Image.open(SPR / "id.webp").convert("RGBA")]
    for n in ["cr", "ak", "ap", "wk", "cp", "vi", "ht", "pu"]:
        tiles.append(Image.open(SPR / f"{n}.webp").convert("RGBA"))
    H = max(t.size[1] for t in tiles)
    W = sum(t.size[0] for t in tiles) + 8 * len(tiles)
    sheet = Image.new("RGBA", (W, H + 8), (28, 30, 44, 255))
    x = 4
    for t in tiles:
        sheet.alpha_composite(t, (x, H - t.size[1] + 4))
        x += t.size[0] + 8
    sheet.convert("RGB").save(ROOT / "tools" / "out" / "luan_color_lineup.png")
    print("previa tools/out/luan_color_lineup.png")


if __name__ == "__main__":
    main()
