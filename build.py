#!/usr/bin/env python3
"""
build.py — renders the entry image for make.fun news-image-20261122.

A one-page broadsheet, "THE WORLD ON SUNDAY", summing up the world news of
Sunday 22 November 2026: 3 leads, 10 cards and a 24-item also-list — 37
stories, every one fact-audited against dated original reporting (see
STORIES.md for the frozen story set and AUDIT.md for the audit trail).

The page is drawn programmatically with Pillow at 2048x2048
(entry-master.png) and downscaled to the 1024x1024 entry.png that main.py
ships. All illustrations are original flat drawings made in this file.

Run:  python3 build.py        (needs Pillow and the Noto fonts)
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 2048

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/noto"
DEJA_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size, fallback="DejaVuSans.ttf"):
    path = os.path.join(FONT_DIR, name)
    if not os.path.exists(path):
        path = os.path.join(DEJA_DIR, fallback)
    return ImageFont.truetype(path, size)


def serif(size):
    return font("NotoSerif-Regular.ttf", size, "DejaVuSerif.ttf")


def serif_b(size):
    return font("NotoSerif-Bold.ttf", size, "DejaVuSerif-Bold.ttf")


def serif_i(size):
    return font("NotoSerif-Italic.ttf", size, "DejaVuSerif.ttf")


def sans(size):
    return font("NotoSans-Regular.ttf", size, "DejaVuSans.ttf")


def sans_b(size):
    return font("NotoSans-Bold.ttf", size, "DejaVuSans-Bold.ttf")


def sans_sb(size):
    return font("NotoSans-SemiBold.ttf", size, "DejaVuSans-Bold.ttf")


def sans_c(size):
    return font("NotoSans-Condensed.ttf", size, "DejaVuSans.ttf")


def sans_cb(size):
    return font("NotoSans-CondensedBold.ttf", size, "DejaVuSans-Bold.ttf")


# ---------------------------------------------------------------- colours
INK = (28, 25, 22)
PAPER = (248, 244, 234)
PANEL = (252, 250, 244)
RULE = (120, 110, 96)
RED = (176, 32, 48)
DARKRED = (140, 30, 34)
NAVY = (22, 34, 66)
GOLD = (198, 148, 42)

REGION_COLORS = {
    "Europe": (38, 84, 150),
    "Asia": (198, 96, 30),
    "Middle East": (106, 62, 143),
    "Africa": (172, 128, 30),
    "Americas": (28, 118, 106),
    "Oceania": (178, 52, 110),
    "Global": (96, 96, 96),
}

TIER_COLORS = {
    "CONFIRMED": (30, 122, 62),
    "OFFICIAL": (38, 84, 150),
    "REPORTED": (196, 120, 20),
}

# ---------------------------------------------------------------- content
STATS = [
    ("NO DEAL", "COP31 ends in Antalya with no agreement at all"),
    ("2 BASES", "US positions in Bahrain hit by Iranian missiles and drones"),
    ("4 DEAD", "as RSF drones strike Khartoum homes and a UN building"),
    ("720/9", "India's declared total — a record Test score in New Zealand"),
    ("$61,197", "Bitcoin's Sunday print as it bounces back above $60,000"),
    ("50", "workers still missing in the Banten candy-factory ruins"),
]

REGION_TALLY = [
    ("EUROPE", 8), ("ASIA", 8), ("AFRICA", 7), ("AMERICAS", 6),
    ("MIDDLE EAST", 3), ("GLOBAL", 3), ("OCEANIA", 2),
]

LEADS = [
    {
        "num": 1, "band": "COP31: NO DEAL", "band_color": (146, 44, 30),
        "kicker": "ANTALYA · CLIMATE SUMMIT",
        "headline": "COP31 ends with no deal at all",
        "body": ("The longest climate summit in history ended in disarray: "
                 "country after country rejected a cover text that never "
                 "mentioned fossil fuels, and the talks closed with nothing "
                 "agreed. Britain said the text \u201cmoves us backwards on "
                 "the science\u201d."),
        "source": "\u2014 The Independent / GOV.UK, 22 Nov",
        "tier": "CONFIRMED", "art": "cop",
    },
    {
        "num": 2, "band": "IRAN STRIKES BAHRAIN", "band_color": NAVY,
        "kicker": "MANAMA · MISSILES & DRONES",
        "headline": "Iran strikes US bases in Bahrain",
        "body": ("The Revolutionary Guard said its missiles and drones hit "
                 "US positions at the Al-Riffa and Awali bases overnight, "
                 "striking Patriot radars. Bahrain said a civilian industrial "
                 "site was set ablaze, two people were injured \u2014 and took "
                 "the attack to the UN."),
        "source": "\u2014 Xinhua / Arab News / Al Jazeera, 22 Nov",
        "tier": "CONFIRMED", "art": "missiles",
    },
    {
        "num": 3, "band": "KHARTOUM: DRONES", "band_color": (112, 74, 22),
        "kicker": "KHARTOUM · SUDAN",
        "headline": "Drones hit Khartoum, and a UN building",
        "body": ("RSF drone attacks on Sudan's capital killed four people "
                 "and damaged a United Nations building in a residential "
                 "neighbourhood, as explosions echoed around the airport "
                 "and homes were destroyed."),
        "source": "\u2014 Al Jazeera / DW / AFP, 22 Nov",
        "tier": "CONFIRMED", "art": "drones",
    },
]

CARDS = [
    {"num": 4, "place": "SERANG · INDONESIA", "region": "Asia",
     "headline": "Fifty missing in the factory ruins",
     "body": ("Rescuers comb the gutted Banten candy factory for 50 missing "
              "workers after Saturday evening's blaze. At least three are dead."),
     "source": "\u2014 AP / DW, 22 Nov", "tier": "CONFIRMED", "art": "flame"},
    {"num": 5, "place": "SEOUL · EXAM CHAOS", "region": "Asia",
     "headline": "Exam chaos costs a minister his job",
     "body": ("Education Minister Choi Kyo-jin resigns over last-minute CSAT "
              "security changes driven by fears of AI cheating."),
     "source": "\u2014 Yonhap / AFP, 22 Nov", "tier": "CONFIRMED", "art": "paper"},
    {"num": 6, "place": "BEIJING · MARKETS", "region": "Asia",
     "headline": "China loosens the margin screw",
     "body": ("The exchanges cut the minimum margin for leveraged share-buying "
              "from 100% to 80%, from 30 November."),
     "source": "\u2014 SZSE / Bloomberg, 22 Nov", "tier": "OFFICIAL", "art": "chart"},
    {"num": 7, "place": "WELLINGTON · CRICKET", "region": "Oceania",
     "headline": "India pile up 720 in Wellington",
     "body": ("Pant's hundred powers a record 720/9 declared; New Zealand "
              "close day four at 119/2, trailing by 233."),
     "source": "\u2014 Reuters / Sportstar, 22 Nov", "tier": "CONFIRMED", "art": "cricket"},
    {"num": 8, "place": "LAS VEGAS · FORMULA 1", "region": "Americas",
     "headline": "Verstappen wins a wild one in Vegas",
     "body": ("He beats Norris and Piastri as Russell's late lock-up drops him "
              "to ninth \u2014 and the Ferraris collide again."),
     "source": "\u2014 Formula1.com / Sky, 22 Nov", "tier": "CONFIRMED", "art": "car"},
    {"num": 9, "place": "MARKETS · CRYPTO", "region": "Global",
     "headline": "Bitcoin bounces above $60,000",
     "body": ("After a two-month low amid \u201cextreme fear\u201d, BTC rebounds "
              "as short sellers are squeezed out of crowded bets."),
     "source": "\u2014 BeInCrypto, 22 Nov", "tier": "CONFIRMED", "art": "coin"},
    {"num": 10, "place": "WASHINGTON · IRAN WAR", "region": "Americas",
     "headline": "Trump: no regime change in Iran",
     "body": ("\u201cI never cared too much about the regime\u201d \u2014 he wants "
              "a permanent deal barring nuclear weapons instead."),
     "source": "\u2014 India Today, 22 Nov", "tier": "REPORTED", "art": "dome"},
    {"num": 11, "place": "WASHINGTON · CYBER", "region": "Americas",
     "headline": "Trump shrugs at the FBI hack",
     "body": ("The reported database breach is \u201cnot good\u201d, he says "
              "\u2014 \u201cbut maybe we'll learn things.\u201d"),
     "source": "\u2014 Euronews, 22 Nov", "tier": "REPORTED", "art": "shield"},
    {"num": 12, "place": "KYIV · UKRAINE", "region": "Europe",
     "headline": "\u201cBig bosses can't decide fate\u201d",
     "body": ("Zelenskyy answers the Trump\u2013Putin\u2013Xi meeting in China: "
              "big powers cannot settle the world's future."),
     "source": "\u2014 Euromaidan Press, 22 Nov", "tier": "CONFIRMED", "art": "quote"},
    {"num": 13, "place": "OYO · DIPLOMACY", "region": "Africa",
     "headline": "Kenya and the DRC mend fences",
     "body": ("Ruto and Tshisekedi agree in Oyo to restore diplomatic ties, "
              "at a four-leader meeting on peace and security."),
     "source": "\u2014 The Standard, 22 Nov", "tier": "CONFIRMED", "art": "hands"},
]

ALSO = [
    ("BALTIYSK", "Explosions and drone activity reported at Russia's Baltic Fleet base", "Euromaidan"),
    ("BENGHAZI", "Ukrainian drones strike a Russian military vessel in port", "Il Sole 24 Ore"),
    ("DYMER", "Death toll from the Russian attack rises to three", "Il Sole 24 Ore"),
    ("TEHRAN", "Moves to break the US blockade; threatens Gulf oil fields ablaze", "Yeshiva World"),
    ("HORMUZ", "Swimmer Lewis Pugh braves the strait for its wildlife", "Arab News"),
    ("VATICAN", "Pope Leo XIV lunches with 1,300 people living in poverty", "Vatican News"),
    ("LONDON", "Minister condemns Trump's embrace of \u201cbutcher\u201d Putin", "Independent"),
    ("LONDON", "Theresa May to Burnham: just accept Brexit, move on", "Independent"),
    ("BERLIN", "Kraftwerk venue apologises over military AI launch", "Mezha"),
    ("KYIV", "UNICEF: record toll of children killed or injured in 2026", "UNICEF"),
    ("DOHA", "Pakistan A beat India A by 48 runs despite Tilak's ton", "Indian Express"),
    ("AUSTRALIA", "Will Jacks out of England's tour with a broken hand", "ECB"),
    ("CHENNAI", "India thrash Thailand to top the hockey Champions Trophy", "Sportstar"),
    ("KOLKATA", "Mohun Bagan survive Churchill scare, go top of the ISL", "Sportstar"),
    ("ABUJA", "NDLEA arrests golfer and chef over 50kg drug shipment", "TheWill"),
    ("WASHINGTON", "Melania Trump finds a diplomatic opening on Ukraine", "NYT"),
    ("WASHINGTON", "Trump warns firms off offshore data centres", "Mt Kenya Times"),
    ("NEW DELHI", "Youth Congress protests Meta's account restrictions", "DW"),
    ("ACCRA", "Ghana suspends new PhD admissions for a national review", "MyJoyOnline"),
    ("PRETORIA", "Government and banks join forces on water investment", "SAnews"),
    ("BEIJING", "China's spies eyed AI chips years before Nvidia scandal", "NYT"),
    ("BAYELSA", "Minister orders a probe into the boat disaster", "Punch"),
    ("WASHINGTON", "Waltz: Russia's losses near WWII scale, unsustainable", "NY Post"),
    ("ANTALYA", "350.org: nations rejected fossil interests, empty promises", "350.org"),
]

# story number -> (lon, lat) for the map pins
PINS = {
    1: (30.7, 36.9), 2: (50.6, 26.2), 3: (32.5, 15.6), 4: (106.2, -6.1),
    5: (127.0, 37.5), 6: (116.4, 39.9), 7: (174.8, -41.3), 8: (-115.1, 36.2),
    9: (-74.0, 40.7), 10: (-77.0, 38.9), 11: (-77.6, 38.4), 12: (30.5, 50.4),
    13: (15.9, -1.2), 14: (19.9, 54.6), 15: (20.1, 32.1), 16: (31.3, 51.3),
    17: (51.4, 35.7), 18: (56.3, 26.5), 19: (12.5, 41.9), 20: (-0.1, 51.5),
    21: (-0.9, 52.3), 22: (13.4, 52.5), 23: (29.5, 49.4), 24: (51.5, 25.3),
    25: (151.2, -33.9), 26: (80.3, 13.1), 27: (88.4, 22.6), 28: (7.5, 9.1),
    29: (-76.4, 39.4), 30: (-77.8, 37.9), 31: (77.2, 28.6), 32: (-0.2, 5.6),
    33: (28.2, -25.7), 34: (117.4, 38.9), 35: (6.0, 4.9), 36: (-76.8, 39.9),
    37: (31.7, 35.9),
}


# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, make_font, start, min_size, max_w, max_lines, leading=1.12):
    """Largest font (from start down to min_size) whose wrap fits max_lines."""
    size = start
    while size > min_size:
        fnt = make_font(size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines, size * leading
        size -= 2
    fnt = make_font(min_size)
    return fnt, wrap(draw, text, fnt, max_w)[:max_lines], min_size * leading


# ------------------------------------------------------------ fit checks
CHECKS = []


def _register(label, needed, box):
    CHECKS.append((label, float(needed), float(box)))


def ellipsize(draw, text, fnt, max_w):
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "\u2026", font=fnt) > max_w:
        text = text[:-1]
    return text.rstrip() + "\u2026"


def fit_box(draw, label, text, make_font, start, min_size, max_w, box_h,
            leading=1.12):
    """Largest font whose wrapped block height fits box_h.

    Height of n lines is (n-1)*leading*size + size. Registers a fit check;
    if even min_size overflows, the tail is ellipsized so the block still
    fits, and the check records what was actually drawn.
    """
    size = start
    while size >= min_size:
        fnt = make_font(size)
        lines = wrap(draw, text, fnt, max_w)
        height = (len(lines) - 1) * size * leading + size if lines else 0
        if height <= box_h:
            _register(label, height, box_h)
            return fnt, lines, size * leading
        size -= 1
    fnt = make_font(min_size)
    lines = wrap(draw, text, fnt, max_w)
    max_lines = max(1, int((box_h - min_size) / (min_size * leading)) + 1)
    if len(lines) > max_lines:
        tail = " ".join(lines[max_lines - 1:])
        lines = lines[:max_lines - 1] + [ellipsize(draw, tail, fnt, max_w)]
    height = (len(lines) - 1) * min_size * leading + min_size if lines else 0
    _register(label, height, box_h)
    return fnt, lines, min_size * leading


def fit_oneline(draw, label, text, make_font, start, min_size, max_w):
    """Largest font (start..min_size) whose single line fits max_w."""
    size = start
    while size > min_size:
        fnt = make_font(size)
        w_ = draw.textlength(text, font=fnt)
        if w_ <= max_w:
            _register(label, w_, max_w)
            return fnt
        size -= 1
    fnt = make_font(min_size)
    _register(label, draw.textlength(text, font=fnt), max_w)
    return fnt


def report_checks():
    bad = [(l, n, b) for (l, n, b) in CHECKS if n > b + 0.5]
    for l, n, b in CHECKS:
        print(f"  fit {'ok  ' if n <= b + 0.5 else 'FAIL'} {l}: "
              f"{n:.0f} <= {b:.0f}")
    if bad:
        raise SystemExit(f"FIT CHECK FAILED: {len(bad)} block(s) do not fit")
    print(f"fit check: all {len(CHECKS)} blocks fit")


def text_block(draw, x, y, lines, fnt, leading, fill=INK):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def pill_width(draw, tier, size=21):
    return draw.textlength(tier, font=sans_b(size)) + 26


def tier_pill(draw, x_right, y, tier, size=21, height=34):
    fnt = sans_b(size)
    label = tier
    w_ = draw.textlength(label, font=fnt) + 26
    color = TIER_COLORS[tier]
    draw.rounded_rectangle([x_right - w_, y, x_right, y + height], 8,
                           fill=color)
    draw.text((x_right - w_ + 13, y + (height - size) / 2 - 2), label,
              font=fnt, fill=(255, 255, 255))
    return w_


def badge(draw, cx, cy, r, num, fill=RED):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    fnt = sans_b(int(r * 1.05))
    label = str(num)
    tw = draw.textlength(label, font=fnt)
    draw.text((cx - tw / 2, cy - r * 0.58), label, font=fnt, fill=(255, 255, 255))


# ---------------------------------------------------------------- flat art
def art_cop(d, x, y, w_, h):
    """Sun, thermometer and a rising line: a summit that ran too hot."""
    d.rectangle([x, y, x + w_, y + h], fill=(250, 232, 205))
    # sun
    cx, cy, r = x + w_ * 0.30, y + h * 0.52, h * 0.30
    for a in range(0, 360, 30):
        rad = math.radians(a)
        d.line([cx + math.cos(rad) * r * 1.25, cy + math.sin(rad) * r * 1.25,
                cx + math.cos(rad) * r * 1.6, cy + math.sin(rad) * r * 1.6],
               fill=GOLD, width=7)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 178, 60))
    d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55],
              fill=(246, 200, 96))
    # thermometer
    tx = x + w_ * 0.68
    d.rounded_rectangle([tx, y + h * 0.14, tx + 26, y + h * 0.78], 13,
                        outline=INK, width=5)
    d.rounded_rectangle([tx + 5, y + h * 0.30, tx + 21, y + h * 0.74], 8,
                        fill=RED)
    d.ellipse([tx - 12, y + h * 0.66, tx + 38, y + h * 0.94], fill=RED)
    for i in range(4):
        yy = y + h * (0.22 + i * 0.14)
        d.line([tx + 34, yy, tx + 56, yy], fill=INK, width=4)
    # crossed-out text lines (the missing words) + verdict, kept clear of
    # the thermometer (which starts at 0.68 of the width)
    ly = y + h * 0.88
    d.line([x + w_ * 0.08, ly, x + w_ * 0.44, ly], fill=INK, width=6)
    d.line([x + w_ * 0.08, ly - 8, x + w_ * 0.44, ly + 8], fill=RED, width=6)
    nf = sans_b(25)
    _register("cop art NO DEAL",
              w_ * 0.47 + d.textlength("NO DEAL", font=nf), w_ * 0.66)
    d.text((x + w_ * 0.47, ly - 14), "NO DEAL", font=nf, fill=DARKRED)


def art_missiles(d, x, y, w_, h):
    """Night sky, arcs and bursts over a shoreline base."""
    d.rectangle([x, y, x + w_, y + h], fill=(16, 24, 52))
    for sx, sy in [(0.08, 0.2), (0.2, 0.45), (0.36, 0.15), (0.55, 0.3),
                   (0.78, 0.18), (0.9, 0.42), (0.66, 0.55), (0.14, 0.62)]:
        d.ellipse([x + w_ * sx, y + h * sy, x + w_ * sx + 6, y + h * sy + 6],
                  fill=(230, 230, 210))
    # crescent
    cx, cy, r = x + w_ * 0.86, y + h * 0.26, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(238, 226, 170))
    d.ellipse([cx - r * 0.4, cy - r * 1.05, cx + r * 1.1, cy + r * 0.6],
              fill=(16, 24, 52))
    # missile arcs
    for (x0, x1, peak, col) in [(0.06, 0.52, 0.52, (255, 170, 80)),
                                (0.16, 0.66, 0.66, (255, 120, 90)),
                                (0.02, 0.40, 0.36, (255, 200, 120))]:
        pts = []
        for t in range(21):
            tt = t / 20
            px = x + w_ * (x0 + (x1 - x0) * tt)
            py = y + h * (0.92 - peak * 4 * tt * (1 - tt) - 0.55 * tt)
            pts.append((px, py))
        d.line(pts, fill=col, width=5)
        ex, ey = pts[-1]
        for a in range(0, 360, 45):
            rad = math.radians(a)
            d.line([ex, ey, ex + math.cos(rad) * 20, ey + math.sin(rad) * 20],
                   fill=(255, 210, 110), width=5)
    # ground + radar dome
    d.rectangle([x, y + h * 0.90, x + w_, y + h], fill=(8, 12, 28))
    bx = x + w_ * 0.60
    d.rectangle([bx, y + h * 0.80, bx + 90, y + h * 0.92], fill=(40, 52, 88))
    d.pieslice([bx + 8, y + h * 0.66, bx + 82, y + h * 0.92], 180, 360,
               fill=(200, 208, 224))
    d.text((x + 14, y + h * 0.90 - 34), "OVERNIGHT · 2 BASES HIT",
           font=sans_b(24), fill=(255, 214, 130))


def art_drones(d, x, y, w_, h):
    """Skyline, quadcopter silhouettes and a UN-blue flag."""
    d.rectangle([x, y, x + w_, y + h], fill=(238, 226, 205))
    # skyline
    base = y + h
    bx = x + 8
    heights = [0.42, 0.62, 0.5, 0.74, 0.56, 0.66, 0.46, 0.6]
    i = 0
    while bx < x + w_ - 40:
        bw = w_ * 0.105
        bh = h * heights[i % len(heights)]
        d.rectangle([bx, base - bh, bx + bw, base], fill=(70, 58, 44))
        bx += bw + 6
        i += 1
    # UN building + flag
    ux, uw = x + w_ * 0.60, w_ * 0.17
    d.rectangle([ux, base - h * 0.78, ux + uw, base], fill=(96, 84, 66))
    d.rectangle([ux + uw * 0.28, base - h * 0.97, ux + uw * 0.34, base - h * 0.78],
                fill=INK)
    d.rectangle([ux + uw * 0.34, base - h * 0.97, ux + uw * 0.34 + 74,
                 base - h * 0.97 + 44], fill=(70, 140, 200))
    d.text((ux + uw * 0.34 + 14, base - h * 0.97 + 7), "UN", font=sans_b(30),
           fill=(255, 255, 255))
    # drones
    for (dx, dy, s) in [(0.16, 0.20, 1.0), (0.38, 0.12, 0.75), (0.55, 0.30, 0.6)]:
        cx, cy = x + w_ * dx, y + h * dy
        r = 26 * s
        d.ellipse([cx - r * 0.32, cy - r * 0.22, cx + r * 0.32, cy + r * 0.22],
                  fill=INK)
        for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            ex, ey = cx + sx * r, cy + sy * r * 0.62
            d.line([cx, cy, ex, ey], fill=INK, width=5)
            d.ellipse([ex - 11 * s, ey - 5 * s, ex + 11 * s, ey + 5 * s],
                      outline=INK, width=4)
    # burst
    ex, ey = x + w_ * 0.30, y + h * 0.52
    for a in range(0, 360, 36):
        rad = math.radians(a)
        d.line([ex, ey, ex + math.cos(rad) * 30, ey + math.sin(rad) * 30],
               fill=RED, width=6)


def art_icon(d, kind, x, y, s):
    """Small flat icons for the cards; box is (x, y, s, s*0.62)."""
    w_, h = s, s * 0.62
    if kind == "flame":
        cx, by = x + w_ / 2, y + h
        d.polygon([(cx, y + 2), (cx + w_ * 0.30, by - h * 0.35),
                   (cx + w_ * 0.16, by), (cx - w_ * 0.16, by),
                   (cx - w_ * 0.30, by - h * 0.35)], fill=(224, 110, 30))
        d.polygon([(cx, y + h * 0.34), (cx + w_ * 0.15, by - h * 0.2),
                   (cx + w_ * 0.08, by), (cx - w_ * 0.08, by),
                   (cx - w_ * 0.15, by - h * 0.2)], fill=(246, 186, 60))
    elif kind == "paper":
        d.rectangle([x + 6, y + 2, x + w_ * 0.62, y + h - 2], outline=INK,
                    width=4)
        for i in range(3):
            ly = y + 12 + i * (h - 22) / 3
            d.line([x + 14, ly, x + w_ * 0.52, ly], fill=INK, width=3)
        d.line([x + w_ * 0.55, y + h - 8, x + w_ - 4, y + 8], fill=RED, width=6)
        d.polygon([(x + w_ - 4, y + 8), (x + w_ - 16, y + 10),
                   (x + w_ - 6, y + 20)], fill=INK)
    elif kind == "chart":
        d.line([x + 4, y + h - 6, x + w_ - 4, y + h - 6], fill=INK, width=4)
        pts = [(x + 8, y + 8), (x + w_ * 0.38, y + h * 0.42),
               (x + w_ * 0.62, y + h * 0.30), (x + w_ - 10, y + h * 0.62)]
        d.line(pts, fill=(30, 122, 62), width=6)
        ex, ey = pts[-1]
        d.polygon([(ex, ey), (ex - 16, ey - 2), (ex - 4, ey + 14)],
                  fill=(30, 122, 62))
        nf = sans_b(23)
        _register("chart icon 80%", w_ * 0.34 + d.textlength("80%", font=nf),
                  w_)
        d.text((x + w_ * 0.34, y + 1), "80%", font=nf, fill=(30, 122, 62))
    elif kind == "cricket":
        d.line([x + w_ * 0.30, y + h - 4, x + w_ * 0.52, y + 6],
               fill=(176, 128, 52), width=11)
        d.ellipse([x + w_ * 0.62, y + h * 0.42, x + w_ * 0.62 + h * 0.42,
                   y + h * 0.84], fill=RED)
        d.arc([x + w_ * 0.62, y + h * 0.42, x + w_ * 0.62 + h * 0.42,
               y + h * 0.84], 100, 260, fill=(255, 255, 255), width=3)
    elif kind == "car":
        by = y + h - 6
        d.polygon([(x + 4, by - 12), (x + w_ * 0.18, by - 12),
                   (x + w_ * 0.30, by - h * 0.52), (x + w_ * 0.62, by - h * 0.52),
                   (x + w_ * 0.78, by - 12), (x + w_ - 4, by - 12)],
                  fill=(28, 60, 130))
        d.rectangle([x + w_ * 0.80, by - h * 0.30, x + w_ - 2, by - h * 0.16],
                    fill=INK)
        for wx in (0.24, 0.72):
            cx = x + w_ * wx
            d.ellipse([cx - 13, by - 24, cx + 13, by + 2], fill=INK)
            d.ellipse([cx - 5, by - 16, cx + 5, by - 6], fill=(200, 200, 200))
    elif kind == "coin":
        cx, cy, r = x + w_ / 2, y + h / 2, h * 0.48
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 178, 60),
                  outline=(176, 128, 30), width=4)
        d.text((cx - 13, cy - 24), "B", font=sans_b(44), fill=(120, 78, 10))
        d.line([cx - 4, cy - r + 6, cx - 4, cy + r - 6], fill=(120, 78, 10),
               width=4)
        d.line([cx + 7, cy - r + 6, cx + 7, cy + r - 6], fill=(120, 78, 10),
               width=4)
    elif kind == "dome":
        cx = x + w_ / 2
        d.pieslice([cx - w_ * 0.26, y + 2, cx + w_ * 0.26, y + h * 0.78],
                   180, 360, fill=(90, 96, 110))
        d.rectangle([x + 6, y + h * 0.52, x + w_ - 6, y + h * 0.62], fill=INK)
        for i in range(5):
            px = x + 12 + i * (w_ - 24) / 4
            d.rectangle([px, y + h * 0.62, px + 5, y + h - 4], fill=INK)
    elif kind == "shield":
        cx, top = x + w_ / 2, y + 2
        d.polygon([(cx - w_ * 0.26, top), (cx + w_ * 0.26, top),
                   (cx + w_ * 0.26, y + h * 0.45), (cx, y + h - 2),
                   (cx - w_ * 0.26, y + h * 0.45)], outline=(38, 84, 150),
                  width=6)
        nf = sans_b(21)
        tw = d.textlength("FBI", font=nf)
        _register("shield icon FBI", tw, w_ * 0.44)
        d.text((cx - tw / 2, y + h * 0.15), "FBI", font=nf,
               fill=(38, 84, 150))
    elif kind == "quote":
        d.text((x + 4, y - 4), "\u201c", font=serif_b(62), fill=RED)
        d.text((x + w_ * 0.52, y - 4), "\u201d", font=serif_b(62), fill=RED)
    elif kind == "hands":
        cy = y + h * 0.52
        d.arc([x + 2, cy - 20, x + w_ * 0.55, cy + 22], 300, 130,
              fill=(28, 118, 106), width=8)
        d.arc([x + w_ * 0.45, cy - 22, x + w_ - 2, cy + 20], 130, 300,
              fill=(172, 128, 30), width=8)
        d.ellipse([x + w_ / 2 - 8, cy - 8, x + w_ / 2 + 8, cy + 8], fill=INK)


ART = {"cop": art_cop, "missiles": art_missiles, "drones": art_drones}

# ---------------------------------------------------------------- the map
LAND = [
    # (lon, lat, rx, ry) ellipses approximating the continents
    (-100, 49, 40, 15), (-152, 65, 13, 6), (-83, 14, 9, 3),
    (-62, -11, 11.5, 16), (-68, -29, 7, 10),
    (15, 52, 17, 9), (15, 64, 10, 5.5), (-2, 54, 3.2, 4.2), (-4, 40.5, 6, 4),
    (20, 7, 16.5, 20), (47, 5, 6.5, 6), (47, -19, 3, 6.5),
    (85, 51, 50, 14.5), (78, 21, 8.5, 9.5), (102, 15, 7.5, 8.5),
    (45, 24, 9.5, 7), (138, 37, 5.5, 5.5), (112, -2, 13, 3.2),
    (134, -25, 13.5, 8), (172, -42, 3, 4.5), (77, 8.5, 4, 3.5),
    (127, 37, 3.5, 3.5), (140, 37, 3.5, 4.5),
]


def is_land(lon, lat):
    for clon, clat, rx, ry in LAND:
        if ((lon - clon) / rx) ** 2 + ((lat - clat) / ry) ** 2 <= 1.0:
            return True
    return False


def draw_map(d, x, y, w_, h):
    d.rectangle([x, y, x + w_, y + h], fill=(18, 30, 54))
    cols, rows = 74, 34
    sx, sy = w_ / cols, h / rows
    for r_ in range(rows):
        lat = 76 - (r_ + 0.5) * (138 / rows)
        for c_ in range(cols):
            lon = -172 + (c_ + 0.5) * (356 / cols)
            if is_land(lon, lat):
                cx, cy = x + (c_ + 0.5) * sx, y + (r_ + 0.5) * sy
                d.ellipse([cx - 3.4, cy - 3.4, cx + 3.4, cy + 3.4],
                          fill=(214, 178, 92))
    for num, (lon, lat) in PINS.items():
        px = x + (lon + 172) / 356 * w_
        py = y + (76 - lat) / 138 * h
        badge(d, px, py, 13.5, num)
    cap = "Each number is the story with that number on this page."
    cf = fit_oneline(d, "map caption", cap, sans, 21, 14, w_ - 28)
    d.text((x + 14, y + h - 32), cap, font=cf, fill=(190, 200, 220))


def draw_also_line(d, x, y, num, place, txt, src, col_w):
    """One also-list story on ONE line: number + place in bold, the rest
    condensed, the source grey — shrunk until the whole line fits col_w."""
    tail = f" ({src})"
    body = f" \u2014 {txt}"
    size = 20
    while size > 15:
        fb, fc = sans_cb(size), sans_c(size)
        total = (d.textlength(str(num), font=fb) + 8
                 + d.textlength(place, font=fb)
                 + d.textlength(body, font=fc)
                 + d.textlength(tail, font=fc))
        if total <= col_w - 2:
            break
        size -= 1
    fb, fc = sans_cb(size), sans_c(size)
    w_num = d.textlength(str(num), font=fb) + 8
    w_place = d.textlength(place, font=fb)
    w_body = d.textlength(body, font=fc)
    w_tail = d.textlength(tail, font=fc)
    _register(f"also {num}", w_num + w_place + w_body + w_tail, col_w)
    d.text((x, y), str(num), font=fb, fill=RED)
    d.text((x + w_num, y), place, font=fb, fill=INK)
    d.text((x + w_num + w_place, y), body, font=fc, fill=(40, 36, 32))
    d.text((x + w_num + w_place + w_body, y), tail, font=fc,
           fill=(96, 88, 78))


# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 44
    right = W - M
    CW = right - M

    # top bar
    d.rectangle([0, 0, W, 58], fill=INK)
    d.text((M, 12), "THE WORLD IN ONE DAY", font=sans_b(30),
           fill=(255, 255, 255))
    tag = "37 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    tw = d.textlength(tag, font=sans_b(26))
    d.text((right - tw, 14), tag, font=sans_b(26), fill=(255, 214, 130))

    # masthead
    title = "Sunday 22 November 2026"
    fnt = fit_oneline(d, "masthead title", title, serif_b, 148, 60, CW)
    tw = d.textlength(title, font=fnt)
    d.text(((W - tw) / 2, 70), title, font=fnt, fill=INK)
    sub = ("Climate talks end with no deal in Antalya \u00b7 Iran strikes US "
           "bases in Bahrain \u00b7 Drones hit Khartoum and a UN building")
    fnt = fit_oneline(d, "masthead sub", sub, serif_i, 37, 22, CW)
    tw = d.textlength(sub, font=fnt)
    d.text(((W - tw) / 2, 230), sub, font=fnt, fill=(70, 62, 54))
    d.line([M, 288, right, 288], fill=INK, width=3)

    # stat strip: big number, then a caption confined to its own box
    col_w = CW / 6
    for i, (big, cap) in enumerate(STATS):
        cx = M + i * col_w
        if i:
            d.line([cx, 310, cx, 452], fill=RED, width=5)
        bf = fit_oneline(d, f"stat {big}", big, serif_b, 82, 36, col_w - 24)
        d.text((cx + 12, 302), big, font=bf, fill=DARKRED)
        cf, clines, clead = fit_box(d, f"stat caption {big}", cap, sans,
                                    24, 16, col_w - 24, 70, 1.12)
        text_block(d, cx + 12, 384, clines, cf, clead, fill=(52, 47, 42))
    d.line([M, 462, right, 462], fill=INK, width=3)

    # region tally bar: every segment label shrunk to fit its segment
    y0 = 474
    total = sum(n for _, n in REGION_TALLY)
    cx = M
    for name, n in REGION_TALLY:
        wseg = CW * n / total
        color = REGION_COLORS[{"EUROPE": "Europe", "ASIA": "Asia",
                                "AFRICA": "Africa", "AMERICAS": "Americas",
                                "MIDDLE EAST": "Middle East",
                                "GLOBAL": "Global",
                                "OCEANIA": "Oceania"}[name]]
        d.rectangle([cx, y0, cx + wseg, y0 + 38], fill=color)
        label = f"{name} {n}"
        lf = fit_oneline(d, f"tally {name}", label, sans_b, 22, 12,
                         wseg - 8)
        d.text((cx + (wseg - d.textlength(label, font=lf)) / 2, y0 + 7),
               label, font=lf, fill=(255, 255, 255))
        cx += wseg

    # leads: fixed zones — band / art / kicker / headline / body / source
    y0 = 528
    lead_h = 496
    gap = 18
    lead_w = (CW - 2 * gap) / 3
    for i, lead in enumerate(LEADS):
        x = M + i * (lead_w + gap)
        d.rectangle([x, y0, x + lead_w, y0 + lead_h], fill=PANEL,
                    outline=RULE, width=2)
        d.rectangle([x, y0, x + lead_w, y0 + 48], fill=lead["band_color"])
        bf = fit_oneline(d, f"lead{lead['num']} band", lead["band"],
                         sans_b, 29, 17, lead_w - 36)
        d.text((x + 18, y0 + 8), lead["band"], font=bf,
               fill=(255, 255, 255))
        ART[lead["art"]](d, x + 14, y0 + 54, lead_w - 28, 106)
        badge(d, x + 31, y0 + 180, 18, lead["num"])
        kf = fit_oneline(d, f"lead{lead['num']} kicker", lead["kicker"],
                         sans_b, 25, 16, lead_w - 74)
        d.text((x + 60, y0 + 166), lead["kicker"], font=kf, fill=RED)
        hf, hlines, hlead = fit_box(d, f"lead{lead['num']} headline",
                                    lead["headline"], serif_b, 46, 26,
                                    lead_w - 36, 96, 1.06)
        text_block(d, x + 18, y0 + 198, hlines, hf, hlead)
        bf2, blines, blead = fit_box(d, f"lead{lead['num']} body",
                                     lead["body"], sans, 24, 17,
                                     lead_w - 36, 124, 1.15)
        text_block(d, x + 18, y0 + 302, blines, bf2, blead,
                   fill=(52, 47, 42))
        pw = pill_width(d, lead["tier"])
        sf = fit_oneline(d, f"lead{lead['num']} source", lead["source"],
                         sans, 22, 14, lead_w - 36 - pw - 16)
        d.text((x + 18, y0 + 446), lead["source"], font=sf,
               fill=(96, 88, 78))
        tier_pill(d, x + lead_w - 16, y0 + 438, lead["tier"])

    # cards, two rows of five: fixed zones, icon kept clear of the kicker
    y0 = 1040
    card_h = 256
    cgap = 16
    card_w = (CW - 4 * cgap) / 5
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x = M + col * (card_w + cgap)
        y = y0 + row * (card_h + 12)
        d.rectangle([x, y, x + card_w, y + card_h], fill=PANEL,
                    outline=RULE, width=2)
        d.rectangle([x, y, x + card_w, y + 8],
                    fill=REGION_COLORS[card["region"]])
        kick = f"{card['num']} \u00b7 {card['place']}"
        kf = fit_oneline(d, f"card{card['num']} kicker", kick, sans_b,
                         22, 14, card_w - 120)
        d.text((x + 14, y + 15), kick, font=kf, fill=RED)
        art_icon(d, card["art"], x + card_w - 100, y + 11, 88)
        hf, hlines, hlead = fit_box(d, f"card{card['num']} headline",
                                    card["headline"], serif_b, 33, 21,
                                    card_w - 28, 72, 1.08)
        text_block(d, x + 14, y + 70, hlines, hf, hlead)
        bf, blines, blead = fit_box(d, f"card{card['num']} body",
                                    card["body"], sans, 20, 15,
                                    card_w - 28, 68, 1.14)
        text_block(d, x + 14, y + 148, blines, bf, blead,
                   fill=(52, 47, 42))
        pw = pill_width(d, card["tier"], 18)
        sf = fit_oneline(d, f"card{card['num']} source", card["source"],
                         sans, 18, 13, card_w - 28 - pw - 14)
        d.text((x + 14, y + card_h - 28), card["source"], font=sf,
               fill=(96, 88, 78))
        tier_pill(d, x + card_w - 12, y + card_h - 34, card["tier"],
                  size=18, height=30)

    # bottom: map + also-list (one line per story, shrunk to fit its column)
    y0 = 1614
    bot_h = 272
    hf2 = fit_oneline(d, "map heading", "WHERE IT HAPPENED", sans_b, 26,
                      17, 700)
    d.text((M, y0 - 32), "WHERE IT HAPPENED", font=hf2, fill=INK)
    draw_map(d, M, y0, 700, bot_h)
    ax = M + 700 + 26
    ah = "ALSO ON SUNDAY \u2014 24 MORE STORIES"
    af = fit_oneline(d, "also heading", ah, sans_b, 26, 17, right - ax)
    d.text((ax, y0 - 32), ah, font=af, fill=INK)
    col_w2 = (right - ax - 18) / 2
    per_col = 12
    line_h = bot_h / per_col
    for j, (place, txt, src) in enumerate(ALSO):
        col, row = divmod(j, per_col)
        x = ax + col * (col_w2 + 18)
        y = y0 + row * line_h + 1
        draw_also_line(d, x, y, 14 + j, place, txt, src, col_w2)

    # date check
    y0 = 1900
    d.rectangle([M, y0, right, y0 + 84], fill=(238, 230, 214),
                outline=RULE, width=2)
    dct = "DATE CHECK \u2014 LEFT OUT ON PURPOSE: OLDER NEWS, HOWEVER BIG"
    tf = fit_oneline(d, "date check title", dct, sans_b, 23, 16, CW - 32)
    d.text((M + 16, y0 + 9), dct, font=tf, fill=DARKRED)
    dc = ("The Bayelsa boat sinking \u2014 Friday 20 Nov (only Sunday's probe "
          "order is on this page) \u00b7 The Sparta II ship fire \u2014 Saturday "
          "21 Nov \u00b7 The UK\u2013EU \u201clandmark\u201d deal \u2014 Friday 20 Nov "
          "\u00b7 Brazil's election fallout \u2014 18 Nov \u00b7 \u201cCOP31 close "
          "to a deal\u201d \u2014 Saturday's optimism, overtaken by Sunday's collapse")
    df, dlines, dlead = fit_box(d, "date check body", dc, sans_c, 20, 14,
                                CW - 32, 40, 1.12)
    text_block(d, M + 16, y0 + 38, dlines, df, dlead, fill=(52, 47, 42))

    # footer
    foot = ("Every story here happened, or was first reported, on Sunday "
            "22 November 2026. Officials' counts and claims are attributed. "
            "Original drawings.")
    ff = fit_oneline(d, "footer line 1", foot, sans, 21, 14, CW)
    tw = d.textlength(foot, font=ff)
    d.text(((W - tw) / 2, 1994), foot, font=ff, fill=(70, 62, 54))
    legend = ("CONFIRMED = independently reported \u00b7 OFFICIAL = the "
              "authority's own statement \u00b7 REPORTED = an attributed claim")
    lf2 = fit_oneline(d, "footer line 2", legend, sans, 19, 13, CW)
    tw = d.textlength(legend, font=lf2)
    d.text(((W - tw) / 2, 2022), legend, font=lf2, fill=(70, 62, 54))

    report_checks()

    master = os.path.join(HERE, "entry-master.png")
    entry = os.path.join(HERE, "entry.png")
    img.save(master)
    img.resize((1024, 1024), Image.LANCZOS).save(entry, optimize=True)
    print("wrote", master, os.path.getsize(master))
    print("wrote", entry, os.path.getsize(entry))


if __name__ == "__main__":
    render()
