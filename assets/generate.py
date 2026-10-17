"""Rebuild local profile art: python assets/generate.py (Pillow + NumPy).

All motion is periodic. No remote assets, APIs or credentials are required.
Fonts: DejaVu Sans (system package fonts-dejavu-core on Debian/Ubuntu).
"""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TAU = 2 * math.pi
FONT = Path('/usr/share/fonts/truetype/dejavu')


def font(size, bold=False):
    return ImageFont.truetype(str(FONT / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')), size)


def save(frames, name, duration):
    # One shared palette prevents color flicker between frames. No dithering:
    # gradients compress better and stars stay sharp.
    sample = Image.new('RGB', (frames[0].width, frames[0].height * 8))
    for i in range(8):
        sample.paste(frames[i * len(frames) // 8], (0, i * frames[0].height))
    palette = sample.quantize(colors=128)
    quantized = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    quantized[0].save(ROOT / f'{name}.gif', save_all=True, append_images=quantized[1:],
                      duration=duration, loop=0, optimize=True, disposal=1)
    frames[0].save(ROOT / f'{name}-still.png', optimize=True)


def banner(t):
    w, h = 960, 400
    y, x = np.mgrid[0:h, 0:w]
    # Orbiting, overlapping clouds return to the same state after one period.
    cloud = np.zeros((h, w, 3), dtype=float)
    for cx, cy, sx, sy, color, phase in [
        (690, 130, 230, 115, (55, 13, 102), 0),
        (810, 310, 260, 100, (10, 45, 115), 2),
        (390, 370, 290, 90, (42, 15, 83), 4),
    ]:
        cx += 50 * math.cos(t + phase)
        cy += 25 * math.sin(t + phase)
        swirl = 1 + .24 * np.sin(x / 61 + y / 43 + 2 * t + phase)
        g = np.exp(-((x - cx) / sx) ** 2 - ((y - cy) / sy) ** 2) * swirl
        cloud += g[..., None] * color
    # Full rotation and a closed drifting orbit make motion unmistakable.
    # All terms return to their initial phase at 2*pi.
    galaxy_x = 730 + 22 * math.cos(t)
    galaxy_y = 172 + 17 * math.sin(t)
    gx, gy = x - galaxy_x, (y - galaxy_y) / .72
    u, v = gx * .97 - gy * .24, gx * .24 + gy * .97
    radius = np.sqrt(u*u + v*v)
    angle = np.arctan2(v, u)
    phase = 3 * angle - 6.5 * np.log1p(radius / 23) - 3 * t
    arms = np.exp(3.8 * (np.cos(phase) - 1))
    disk = np.exp(-(radius / 218) ** 1.5)
    knots = .72 + .28 * np.cos(radius / 12 + 2 * phase)
    dust = np.exp(12 * (np.cos(phase - .38) - 1))
    core = np.exp(-(radius / 30) ** 1.4)
    halo = np.exp(-(radius / 80) ** 1.5)
    cloud += (arms * disk * knots)[..., None] * (112, 74, 208)
    cloud += (disk * .28)[..., None] * (37, 67, 136)
    cloud *= (1 - .48 * dust * disk)[..., None]
    cloud += core[..., None] * (208, 190, 229)
    cloud += halo[..., None] * (40, 35, 65)
    cloud += (4, 6, 17)
    im = Image.fromarray(np.uint8(np.clip(cloud, 0, 255)))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(159)
    for i in range(115):
        xx, yy = rng.uniform(12, w - 12), rng.uniform(12, h - 12)
        phase = rng.uniform(0, TAU)
        brightness = int(80 + 140 * (.5 + .5 * math.sin(2 * t + phase)))
        xx += 4 * math.sin(t + phase)
        yy += 3 * math.cos(t + phase)
        d.ellipse((xx, yy, xx + 1, yy + 1), fill=(brightness, brightness, min(255, brightness + 25)))
        if i % 19 == 0:
            d.line((xx - 3, yy, xx + 4, yy), fill=(brightness, brightness, 240))
            d.line((xx, yy - 3, xx, yy + 4), fill=(brightness, brightness, 240))
    # Bright orbiting dust makes the background motion visible even on mobile.
    for i in range(70):
        a = rng.uniform(0, TAU) + t
        r = rng.uniform(50, 245)
        xx, yy = galaxy_x + r * math.cos(a), galaxy_y + .66 * r * math.sin(a)
        bright = int(130 + 85 * (.5 + .5 * math.sin(2*t + i)))
        if i % 7 == 0:
            trail = [(galaxy_x + r * math.cos(a - j / 100),
                      galaxy_y + .66 * r * math.sin(a - j / 100)) for j in range(11)]
            d.line(trail, fill='#7c91db', width=2)
        d.ellipse((xx, yy, xx + 1.5, yy + 1.5), fill=(bright, bright, 255))
    # A smaller foreground planet leaves the spiral galaxy clearly visible.
    px, py = 843, 313 + 7 * math.sin(t)
    def ring(front):
        for radius, color, width in [(84, '#605ea9', 2), (76, '#b9adff', 2), (71, '#5d92e2', 1)]:
            points = []
            for a in np.linspace(0 if front else math.pi, math.pi if front else TAU, 100):
                u, v = radius * math.cos(a), 19 * math.sin(a)
                points.append((px + u * .94 - v * -.34, py + u * -.34 + v * .94))
            d.line(points, fill=color, width=width)
    ring(False)
    r = 44
    for row in range(-r, r + 1):
        span = math.sqrt(max(0, r * r - row * row))
        for col in range(-int(span), int(span) + 1):
            z = math.sqrt(max(0, 1 - (col / r) ** 2 - (row / r) ** 2))
            light = max(.12, .55 * z - .35 * col / r - .3 * row / r)
            bands = 7 * math.sin(row / 7 + .65 * math.sin(t) + col / 40)
            color = tuple(int(max(0, min(255, base * light + bands))) for base in (151, 115, 244))
            d.point((px + col, py + row), fill=color)
    ring(True)
    # A tiny moon travels on an actual closed orbit.
    mx, my = px + 98 * math.cos(t), py + 39 * math.sin(t)
    d.ellipse((mx - 4, my - 4, mx + 4, my + 4), fill='#9ccaff')
    # Quiet opaque panel keeps text legible through every frame.
    d.rounded_rectangle((40, 83, 593, 308), radius=20, fill='#090c20', outline='#282340', width=1)
    d.text((65, 109), 'ESTRATEGIA  /  TECNOLOGÍA  /  INNOVACIÓN', font=font(13), fill='#a9a0da')
    d.text((61, 141), 'Lenin Silva', font=font(57, True), fill='#f4f1ff')
    d.text((65, 218), 'Ingeniero empresarial', font=font(27), fill='#c6d6ff')
    d.line((66, 275, 151, 275), fill='#9a7cff', width=3)
    d.line((157, 275, 190, 275), fill='#53acff', width=3)
    d.text((42, 359), 'IDEAS CON DIRECCIÓN. PROYECTOS CON PROPÓSITO.', font=font(12), fill='#a7acd0')
    return im


def signals(t):
    im = Image.new('RGB', (560, 76), '#090c20')
    d = ImageDraw.Draw(im)
    # Rocket: smooth closed elliptical flight, gently pulsing exhaust.
    x, y = 58 + 12 * math.cos(t), 36 + 6 * math.sin(t)
    d.polygon([(x - 16, y + 10), (x - 30 - 4 * math.sin(3*t), y + 20), (x - 21, y + 2)], fill='#9376ff')
    d.polygon([(x - 13, y - 3), (x + 14, y - 20), (x + 12, y + 8), (x - 6, y + 16)], fill='#dde7ff')
    d.ellipse((x - 1, y - 10, x + 8, y - 1), fill='#399df7')
    d.polygon([(x - 13, y + 2), (x - 23, y + 3), (x - 16, y + 15)], fill='#7778eb')
    # Floating ringed planet.
    x, y = 168, 38 + 6 * math.sin(t + 1)
    d.ellipse((x - 17, y - 17, x + 17, y + 17), fill='#8262cf')
    d.ellipse((x - 31, y - 7, x + 31, y + 7), outline='#a9b9fa', width=2)
    # Rotating spiral galaxy.
    for arm in range(3):
        pts = [(280 + (4 + 1.7*a) * math.cos(a / 3 + t + arm*TAU/3),
                38 + .65 * (4 + 1.7*a) * math.sin(a / 3 + t + arm*TAU/3)) for a in np.linspace(0, 13, 70)]
        d.line(pts, fill=['#8a75da', '#5c9ff0', '#c5b6ff'][arm], width=3)
    d.ellipse((276, 34, 284, 42), fill='#e8dfff')
    # Twinkling stars, without abrupt flashes.
    for x, y, phase in [(390, 35, 0), (411, 22, 2), (414, 55, 4)]:
        r = 3 + 4 * (.5 + .5 * math.sin(t + phase))
        d.polygon([(x, y-r), (x+2, y-2), (x+r, y), (x+2, y+2), (x, y+r), (x-2, y+2), (x-r, y), (x-2, y-2)], fill='#c9c9ff')
    # Satellite drifts on a closed path; solar panels remain readable.
    x, y = 503 + 6 * math.sin(t), 38 + 5 * math.cos(t)
    d.rectangle((x-7, y-9, x+7, y+9), fill='#bdc6e5')
    for side in [-1, 1]:
        a, b = sorted((x+side*11, x+side*29))
        d.rectangle((a, y-10, b, y+10), fill='#305ea4', outline='#779ff1')
        d.line((a+9, y-10, a+9, y+10), fill='#779ff1')
        d.line((a, y, b, y), fill='#779ff1')
    d.arc((x-9, y-25, x+9, y-7), 0, 180, fill='#c5c9f7', width=2)
    return im


def phrase_frame(index, alpha):
    im = Image.new('RGB', (800, 78), '#090c20')
    d = ImageDraw.Draw(im)
    phrases = ['Ingeniero empresarial', 'Estrategia y tecnología', 'Construyendo proyectos con propósito']
    color = tuple(int(a + (b-a)*alpha) for a, b in zip((9, 12, 32), (211, 215, 255)))
    d.text((400, 36), phrases[index], anchor='mm', font=font(29), fill=color)
    for i in range(3):
        d.ellipse((382+i*16, 64, 386+i*16, 68), fill='#a78bfa' if i == index else '#34324f')
    return im


if __name__ == '__main__':
    frames = 96
    save([banner(TAU*i/frames) for i in range(frames)], 'galaxy-motion', 50)
    save([signals(TAU*i/frames) for i in range(frames)], 'orbit-signals', 50)
    phrases = []
    for i in range(3):
        for n in range(48):
            alpha = min(1, n/5, (47-n)/5)
            phrases.append(phrase_frame(i, alpha))
    save(phrases, 'intro', 80)
    # First GIF frame is a fade boundary; the static alternative must be readable.
    phrase_frame(0, 1).save(ROOT / 'intro-still.png', optimize=True)
    for path in sorted(ROOT.glob('*.gif')):
        print(f'{path.name}: {path.stat().st_size / 1024:.0f} KiB')
