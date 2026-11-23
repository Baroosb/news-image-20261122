#!/usr/bin/env python3
"""
build.py — renders the entry image for make.fun news-image-20261122.

A one-page broadsheet, "THE WORLD IN ONE DAY", summing up the world news
of Sunday 22 November 2026: 3 leads, 10 cards and a 24-item also-list —
37 stories, every one fact-audited against dated original reporting (see
STORIES.md for the frozen story set and AUDIT.md for the audit trail).

Version 3 is a premium redesign to a design panel's specification —
Mark Porter's Guardian print redesign crossed with Swiss grid
discipline, Monocle restraint: type does the work, decoration is
removed. A strict six-colour palette (paper, ink, mid ink, hairline,
oxblood, slate), one hairline weight used only as full-width section
dividers, duotone spot art for the three leads, margin numerals, drop
caps, square tier markers, an oversized ghost "22" in the masthead and
a dotted map with oxblood pins. No boxes, no pills, no shadows.

The page is drawn programmatically with Pillow at 2048x2048
(entry-master.png) and downscaled to the 1024x1024 entry.png that
main.py ships. Every text block is measured and fitted into its zone;
the build registers a fit check per block and fails loudly if any
block overflows.

Run:  python3 build.py        (needs Pillow and the DejaVu /
                              Liberation fonts)
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 2048

# ---------------------------------------------------------------- fonts
DEJA_DIR = "/usr/share/fonts/truetype/dejavu"
LIB_DIR = "/usr/share/fonts/truetype/liberation"


def serif_b(size):
    return ImageFont.truetype(os.path.join(DEJA_DIR, "DejaVuSerif-Bold.ttf"),
                              size)


def serif(size):
    return ImageFont.truetype(os.path.join(DEJA_DIR, "DejaVuSerif.ttf"), size)


def dsans_b(size):
    return ImageFont.truetype(os.path.join(DEJA_DIR, "DejaVuSans-Bold.ttf"),
                              size)


def lsans(size):
    return ImageFont.truetype(os.path.join(LIB_DIR, "LiberationSans-Regular.ttf"),
                              size)


def lsans_b(size):
    return ImageFont.truetype(os.path.join(LIB_DIR, "LiberationSans-Bold.ttf"),
                              size)


# ---------------------------------------------------------------- palette
PAPER = (242, 238, 229)          # #F2EEE5
INK = (23, 18, 15)               # #17120F
MID = (87, 80, 74)               # #57504A
HAIR = (213, 206, 193)           # #D5CEC1
OXB = (138, 28, 19)              # #8A1C13
SLATE = (51, 72, 79)             # #33484F
INK_TINT = (112, 103, 94)        # ink family, for the tally bar
SLATE_TINT = (104, 122, 128)     # slate family, for the tally bar
MID_TINT = (152, 144, 134)       # mid family, for the tally bar
GHOST = (232, 217, 208)          # oxblood at ~10% over paper

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
        "num": 2, "band": "IRAN STRIKES BAHRAIN", "band_color": (22, 34, 66),
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


def wrap_var(draw, text, fnt, widths):
    """Greedy wrap where line i may use widths[min(i, len(widths)-1)]."""
    words, lines, cur = text.split(), [], ""

    def limit():
        return widths[min(len(lines), len(widths) - 1)]

    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= limit() or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ fit checks
CHECKS = []
ELLIPSIZED = []


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
    fits, the check records what was actually drawn, and the label is
    noted in ELLIPSIZED for the report.
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
        ELLIPSIZED.append(label)
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


def tracked_width(draw, text, fnt, tracking):
    if not text:
        return 0
    return (sum(draw.textlength(ch, font=fnt) for ch in text)
            + tracking * (len(text) - 1))


def draw_tracked(draw, x, y, text, fnt, tracking, fill):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += draw.textlength(ch, font=fnt) + tracking
    return cx - tracking


def fit_tracked(draw, label, text, make_font, start, min_size, tracking,
                max_w):
    """Largest font whose letter-spaced (tracked) line fits max_w."""
    size = start
    while size > min_size:
        fnt = make_font(size)
        w_ = tracked_width(draw, text, fnt, tracking)
        if w_ <= max_w:
            _register(label, w_, max_w)
            return fnt
        size -= 1
    fnt = make_font(min_size)
    _register(label, tracked_width(draw, text, fnt, tracking), max_w)
    return fnt


def report_checks():
    bad = [(l, n, b) for (l, n, b) in CHECKS if n > b + 0.5]
    for l, n, b in CHECKS:
        print(f"  fit {'ok  ' if n <= b + 0.5 else 'FAIL'} {l}: "
              f"{n:.0f} <= {b:.0f}")
    if ELLIPSIZED:
        print("  ellipsized blocks:", ", ".join(ELLIPSIZED))
    if bad:
        raise SystemExit(f"FIT CHECK FAILED: {len(bad)} block(s) do not fit")
    print(f"fit check: all {len(CHECKS)} blocks fit")


def text_block(draw, x, y, lines, fnt, leading, fill=INK):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def tier_marker(draw, x_right, y, tier, size=15, tracking=2, sq=8):
    """A small ink square plus the tier word in tracked small caps,
    right-aligned to x_right. No pills, no rounded rectangles."""
    fnt = dsans_b(size)
    tw = tracked_width(draw, tier, fnt, tracking)
    total = sq + 8 + tw
    draw.rectangle([x_right - total, y + (size - sq) / 2 + 1,
                    x_right - total + sq, y + (size - sq) / 2 + 1 + sq],
                   fill=INK)
    draw_tracked(draw, x_right - tw, y, tier, fnt, tracking, INK)
    return total


# ------------------------------------------------------- duotone spot art
# Each lead illustration is flat shapes in ink + oxblood only, drawn in a
# wide strip inside a single 1px (2px at master scale) ink frame.
def art_cop(d, x, y, w_, h):
    """Concentric sun disc and a bold thermometer silhouette."""
    cy = y + h / 2
    # concentric sun: oxblood core, ink ring, oxblood ring, ink rays
    cx, r = x + h * 0.62, h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=4)
    r2 = r * 0.68
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=OXB, width=4)
    r3 = r * 0.38
    d.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], fill=OXB)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        d.line([cx + math.cos(rad) * r * 1.18, cy + math.sin(rad) * r * 1.18,
                cx + math.cos(rad) * r * 1.48, cy + math.sin(rad) * r * 1.48],
               fill=INK, width=4)
    # thermometer silhouette, right of centre
    tx = x + w_ * 0.60
    tube_w = h * 0.16
    d.rectangle([tx, y + h * 0.14, tx + tube_w, y + h * 0.72], fill=INK)
    bulb_r = h * 0.17
    bcx, bcy = tx + tube_w / 2, y + h * 0.80
    d.ellipse([bcx - bulb_r, bcy - bulb_r, bcx + bulb_r, bcy + bulb_r],
              fill=INK)
    mcy = y + h * 0.80
    d.rectangle([tx + tube_w * 0.28, y + h * 0.30, tx + tube_w * 0.72, mcy],
                fill=OXB)
    br = bulb_r * 0.55
    d.ellipse([bcx - br, bcy - br, bcx + br, bcy + br], fill=OXB)
    for i in range(3):
        yy = y + h * (0.24 + i * 0.18)
        d.line([tx + tube_w + 8, yy, tx + tube_w + 26, yy], fill=INK, width=3)
    # a rising oxblood line running away to the right edge
    pts = [(x + w_ * 0.76, y + h * 0.74), (x + w_ * 0.84, y + h * 0.58),
           (x + w_ * 0.91, y + h * 0.62), (x + w_ * 0.985, y + h * 0.30)]
    d.line(pts, fill=OXB, width=5)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 16, ey + 3), (ex - 5, ey + 15)], fill=OXB)
    # baseline
    d.line([x + 10, y + h - 7, x + w_ - 10, y + h - 7], fill=INK, width=3)


def art_missiles(d, x, y, w_, h):
    """A night band: ink field, three oxblood missile arcs, paper stars."""
    d.rectangle([x, y, x + w_, y + h], fill=INK)
    for sx, sy in [(0.06, 0.22), (0.16, 0.5), (0.30, 0.16), (0.46, 0.34),
                   (0.60, 0.14), (0.72, 0.44), (0.86, 0.2), (0.95, 0.52),
                   (0.38, 0.58), (0.55, 0.55)]:
        px, py = x + w_ * sx, y + h * sy
        d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=PAPER)
    # three descending arcs ending in small bursts
    for (x0, x1, peak) in [(0.04, 0.46, 0.60), (0.14, 0.62, 0.78),
                            (0.02, 0.34, 0.42)]:
        pts = []
        for t in range(25):
            tt = t / 24
            px = x + w_ * (x0 + (x1 - x0) * tt)
            py = y + h * (0.30 + peak * tt - 0.55 * tt * tt)
            pts.append((px, py))
        d.line(pts, fill=OXB, width=5)
        ex, ey = pts[-1]
        for a in range(0, 360, 45):
            rad = math.radians(a)
            d.line([ex, ey, ex + math.cos(rad) * 13, ey + math.sin(rad) * 13],
                   fill=OXB, width=4)
    # horizon: a paper line, with oxblood base blocks standing on it
    hy = y + h * 0.88
    d.line([x, hy, x + w_, hy], fill=PAPER, width=3)
    for bx, bw, bh in [(0.58, 0.10, 0.16), (0.70, 0.07, 0.24),
                       (0.79, 0.12, 0.13), (0.93, 0.05, 0.20)]:
        d.rectangle([x + w_ * bx, hy - h * bh, x + w_ * (bx + bw), hy],
                    fill=OXB)
    # one pale dome among the blocks
    dx = x + w_ * 0.845
    d.pieslice([dx, hy - h * 0.20, dx + w_ * 0.055, hy + h * 0.06], 180, 360,
               fill=PAPER)


def art_drones(d, x, y, w_, h):
    """Skyline blocks in ink along the bottom, drone X shapes in oxblood."""
    base = y + h - 6
    heights = [0.34, 0.58, 0.42, 0.72, 0.5, 0.64, 0.38, 0.56, 0.46, 0.68,
               0.4, 0.52]
    bx = x + 8
    i = 0
    while bx < x + w_ - 30:
        bw = w_ * 0.068
        bh = h * heights[i % len(heights)]
        d.rectangle([bx, base - bh, bx + bw, base], fill=INK)
        bx += bw + 7
        i += 1
    d.line([x + 4, base + 3, x + w_ - 4, base + 3], fill=INK, width=3)
    # drones: an X of two crossed lines with a small centre ring
    for (dx, dy, s) in [(0.16, 0.30, 1.0), (0.40, 0.18, 0.72),
                        (0.63, 0.36, 0.85), (0.86, 0.16, 0.6)]:
        cx, cy = x + w_ * dx, y + h * dy
        r = h * 0.17 * s
        for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            ex, ey = cx + sx * r, cy + sy * r * 0.72
            d.line([cx, cy, ex, ey], fill=OXB, width=5)
            d.ellipse([ex - 6 * s, ey - 6 * s, ex + 6 * s, ey + 6 * s],
                      outline=OXB, width=4)
        cr = r * 0.30
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=OXB, width=4)


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
    """Dotted world map: mid-ink dots on the paper, oxblood pins with
    paper numerals. Latitude range 76..-48 keeps the dots near-square."""
    cols, rows = 88, 30
    sx, sy = w_ / cols, h / rows
    for r_ in range(rows):
        lat = 76 - (r_ + 0.5) * (124 / rows)
        for c_ in range(cols):
            lon = -172 + (c_ + 0.5) * (356 / cols)
            if is_land(lon, lat):
                cx, cy = x + (c_ + 0.5) * sx, y + (r_ + 0.5) * sy
                d.ellipse([cx - 3.1, cy - 3.1, cx + 3.1, cy + 3.1], fill=MID)
    pf = dsans_b(13)
    for num, (lon, lat) in PINS.items():
        px = x + (lon + 172) / 356 * w_
        py = y + (76 - lat) / 124 * h
        r = 11.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=OXB)
        d.text((px, py), str(num), font=pf, fill=PAPER, anchor="mm")


def brief_width(d, num, place, txt, src, src_size):
    fb, fr = lsans_b(22), lsans(22)
    fn = serif_b(20)
    fs = lsans(src_size)
    return (d.textlength(str(num), font=fn) + 9
            + d.textlength(place, font=fb)
            + d.textlength(" \u2014 " + txt, font=fr)
            + d.textlength(f" ({src})", font=fs))


def draw_brief(d, x, y, num, place, txt, src, src_size):
    fb, fr = lsans_b(22), lsans(22)
    fn = serif_b(20)
    fs = lsans(src_size)
    d.text((x, y), str(num), font=fn, fill=INK)
    cx = x + d.textlength(str(num), font=fn) + 9
    d.text((cx, y), place, font=fb, fill=INK)
    cx += d.textlength(place, font=fb)
    body = " \u2014 " + txt
    d.text((cx, y), body, font=fr, fill=INK)
    cx += d.textlength(body, font=fr)
    d.text((cx, y), f" ({src})", font=fs, fill=MID)


def lead_body(draw, x, y, lead, col_w, zone_h):
    """Lead body with a drop cap: the first letter enlarged in oxblood
    serif, the first two lines set narrower to clear it."""
    body = lead["body"]
    cap, rest = body[0], body[1:]
    size, fnt, cap_f, cap_w, lines = 19, None, None, 0, []
    for size in (22, 21, 20, 19):
        fnt = lsans(size)
        cap_f = serif_b(int(size * 2.8))
        cap_w = draw.textlength(cap, font=cap_f)
        widths = [col_w - cap_w - 14, col_w - cap_w - 14, col_w]
        lines = wrap_var(draw, rest, fnt, widths)
        if len(lines) * size * 1.24 <= zone_h:
            break
    height = len(lines) * size * 1.24
    _register(f"lead{lead['num']} body", height, zone_h)
    draw.text((x, y - size * 0.30), cap, font=cap_f, fill=OXB)
    ly = y
    for i, ln in enumerate(lines):
        lx = x + (cap_w + 14 if i < 2 else 0)
        draw.text((lx, ly), ln, font=fnt, fill=INK)
        ly += size * 1.24
    return size


# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 96
    right = W - M
    CW = right - M

    def divider(y):
        d.line([M, y, right, y], fill=HAIR, width=2)

    # ghost numeral "22", oxblood at ~10%, cropped by the masthead rule
    DIV1 = 258
    ghost_layer = Image.new("RGB", (W, H), PAPER)
    gd = ImageDraw.Draw(ghost_layer)
    gf = serif_b(300)
    gw = gd.textlength("22", font=gf)
    gd.text((right + 10 - gw, 0), "22", font=gf, fill=GHOST)
    img.paste(ghost_layer.crop((0, 0, W, DIV1)), (0, 0))
    d = ImageDraw.Draw(img)

    # top microtext row
    lf = fit_tracked(d, "microtext left", "THE WORLD IN ONE DAY", dsans_b,
                     24, 18, 4, CW * 0.42)
    draw_tracked(d, M, 30, "THE WORLD IN ONE DAY", lf, 4, INK)
    tag = ("37 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED "
           "SUNDAY 22 NOVEMBER 2026")
    tf = fit_tracked(d, "microtext right", tag, dsans_b, 23, 17, 2, CW * 0.60)
    tw = tracked_width(d, tag, tf, 2)
    draw_tracked(d, right - tw, 31, tag, tf, 2, MID)

    # the date, as large as the measure allows
    date = "22 November 2026"
    df = fit_oneline(d, "date display", date, serif_b, 184, 148, CW)
    d.text((M, 72), date, font=df, fill=INK)
    divider(DIV1)

    # stat strip: serif figures in oxblood on a shared baseline, captions
    # confined to their own column
    col_w = CW / 6
    base_y = DIV1 + 92
    for i, (big, cap) in enumerate(STATS):
        cx = M + i * col_w
        bf = fit_oneline(d, f"stat {big}", big, serif_b, 104, 52, col_w - 20)
        d.text((cx + 10, base_y), big, font=bf, fill=OXB, anchor="ls")
        cf, clines, clead = fit_box(d, f"stat caption {big}", cap, lsans,
                                    19, 16, col_w - 20, 42, 1.18)
        text_block(d, cx + 10, base_y + 16, clines, cf, clead, fill=MID)
    DIV2 = 424
    divider(DIV2)

    # leads: margin numeral + kicker, duotone art in a 1px frame,
    # serif headline, drop-cap body, source + square tier marker
    y0 = 440
    lead_w = 597
    lead_gap = 32
    for i, lead in enumerate(LEADS):
        x = M + i * (lead_w + lead_gap)
        num = f"{lead['num']:02d}"
        nf = serif_b(70)
        num_w = d.textlength(num, font=nf)
        _register(f"lead{lead['num']} numeral", num_w, lead_w)
        d.text((x, y0), num, font=nf, fill=INK)
        kf = fit_tracked(d, f"lead{lead['num']} kicker", lead["kicker"],
                         dsans_b, 17, 13, 3, lead_w - num_w - 14)
        draw_tracked(d, x + num_w + 14, y0 + 25, lead["kicker"], kf, 3, MID)
        ay = y0 + 78
        d.rectangle([x, ay, x + lead_w, ay + 80], outline=INK, width=2)
        ART[lead["art"]](d, x + 3, ay + 3, lead_w - 6, 74)
        hf, hlines, hlead = fit_box(d, f"lead{lead['num']} headline",
                                    lead["headline"], serif_b, 48, 34,
                                    lead_w, 98, 1.02)
        text_block(d, x, ay + 90, hlines, hf, hlead)
        lead_body(d, x, ay + 196, lead, lead_w, 124)
        sy = ay + 330
        tier_w = tracked_width(d, lead["tier"], dsans_b(15), 2) + 16
        sf = fit_oneline(d, f"lead{lead['num']} source", lead["source"],
                         lsans, 18, 14, lead_w - tier_w - 16)
        d.text((x, sy), lead["source"], font=sf, fill=MID)
        tier_marker(d, x + lead_w, sy + 1, lead["tier"])
    DIV3 = 880
    divider(DIV3)

    # mid cards, two rows of five: numeral + place, bold sans headline,
    # brief body, source + tier marker — separated by whitespace only
    y0 = 894
    card_w = 345
    card_gap = 32
    row_h = 200
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x = M + col * (card_w + card_gap)
        y = y0 + row * (row_h + 8)
        num = f"{card['num']:02d}"
        nf = serif_b(29)
        num_w = d.textlength(num, font=nf)
        d.text((x, y), num, font=nf, fill=INK)
        kf = fit_tracked(d, f"card{card['num']} kicker", card["place"],
                         dsans_b, 15, 12, 2.5, card_w - num_w - 9)
        draw_tracked(d, x + num_w + 9, y + 7, card["place"], kf, 2.5, MID)
        hf, hlines, hlead = fit_box(d, f"card{card['num']} headline",
                                    card["headline"], lsans_b, 27, 21,
                                    card_w, 54, 1.04)
        text_block(d, x, y + 30, hlines, hf, hlead)
        bf, blines, blead = fit_box(d, f"card{card['num']} body",
                                    card["body"], lsans, 20, 18, card_w, 90,
                                    1.27)
        text_block(d, x, y + 90, blines, bf, blead, fill=INK)
        sy = y + 182
        tier_w = tracked_width(d, card["tier"], dsans_b(13), 1.5) + 15
        sf = fit_oneline(d, f"card{card['num']} source", card["source"],
                         lsans, 17, 13, card_w - tier_w - 14)
        d.text((x, sy), card["source"], font=sf, fill=MID)
        tier_marker(d, x + card_w, sy + 2, card["tier"], size=13,
                    tracking=1.5, sq=7)
    DIV4 = 1316
    divider(DIV4)

    # map + briefs band. The briefs are LOCKED at Liberation Sans 22 with
    # 30px leading (11px / 15px at entry scale): items 14-25 run in one
    # column beside the map, items 26-37 continue full-width below it.
    hy = 1330
    hf1 = fit_tracked(d, "map heading", "WHERE IT HAPPENED", dsans_b, 19,
                      15, 3, 850)
    draw_tracked(d, M, hy, "WHERE IT HAPPENED", hf1, 3, INK)
    ba_x = M + 850 + 32
    ba_w = right - ba_x
    ah = "ALSO ON SUNDAY \u2014 24 MORE STORIES"
    hf2 = fit_tracked(d, "also heading", ah, dsans_b, 19, 15, 3, ba_w)
    draw_tracked(d, ba_x, hy, ah, hf2, 3, INK)
    ry = 1358
    draw_map(d, M, ry, 850, 296)
    cap = "Each number is the story with that number on this page."
    cf = fit_oneline(d, "map caption", cap, lsans, 16, 13, 848)
    d.text((M + 2, ry + 304), cap, font=cf, fill=MID)

    b1 = [(14 + j, ALSO[j]) for j in range(12)]          # beside the map
    b2 = [(26 + j, ALSO[12 + j]) for j in range(6)]      # below, left
    b3 = [(32 + j, ALSO[18 + j]) for j in range(6)]      # below, right
    col_of = {}
    for n, _ in b1:
        col_of[n] = ba_w
    for n, _ in b2:
        col_of[n] = 880
    for n, _ in b3:
        col_of[n] = right - (M + 880 + 30)
    src_size = 19
    for cand in (22, 21, 20, 19):
        if all(brief_width(d, n, p, t, s, cand) <= col_of[n]
               for n, (p, t, s) in b1 + b2 + b3):
            src_size = cand
            break
    for n, (p, t, s) in b1 + b2 + b3:
        _register(f"brief {n}", brief_width(d, n, p, t, s, src_size),
                  col_of[n])
    for j, (n, (p, t, s)) in enumerate(b1):
        draw_brief(d, ba_x, ry + j * 30, n, p, t, s, src_size)
    ry2 = ry + 364
    for j, (n, (p, t, s)) in enumerate(b2):
        draw_brief(d, M, ry2 + j * 30, n, p, t, s, src_size)
    for j, (n, (p, t, s)) in enumerate(b3):
        draw_brief(d, M + 880 + 30, ry2 + j * 30, n, p, t, s, src_size)
    DIV5 = 1906
    divider(DIV5)

    # region tally: one stacked bar, typographic labels under each segment
    y0 = 1914
    total = sum(n for _, n in REGION_TALLY)
    seg_colors = [INK, OXB, SLATE, MID, INK_TINT, SLATE_TINT, MID_TINT]
    cx = M
    for k, (name, n) in enumerate(REGION_TALLY):
        wseg = CW * n / total
        d.rectangle([cx, y0, cx + wseg, y0 + 26], fill=seg_colors[k])
        label = f"{name} {n}"
        lf = fit_tracked(d, f"tally {name}", label, dsans_b, 14, 11, 1.5,
                         wseg - 4)
        tw = tracked_width(d, label, lf, 1.5)
        draw_tracked(d, cx + (wseg - tw) / 2, y0 + 32, label, lf, 1.5, MID)
        cx += wseg

    # date check: title at the left, the exclusions set beside it
    y0 = 1972
    dct = "DATE CHECK \u2014 LEFT OUT ON PURPOSE: OLDER NEWS, HOWEVER BIG"
    tf, tlines, tlead = fit_box(d, "date check title", dct, dsans_b, 16, 13,
                                440, 40, 1.2)
    text_block(d, M, y0, tlines, tf, tlead, fill=OXB)
    dc = ("The Bayelsa boat sinking \u2014 Friday 20 Nov (only Sunday's probe "
          "order is on this page) \u00b7 The Sparta II ship fire \u2014 Saturday "
          "21 Nov \u00b7 The UK\u2013EU \u201clandmark\u201d deal \u2014 Friday 20 Nov "
          "\u00b7 Brazil's election fallout \u2014 18 Nov \u00b7 \u201cCOP31 close "
          "to a deal\u201d \u2014 Saturday's optimism, overtaken by Sunday's collapse")
    df, dlines, dlead = fit_box(d, "date check body", dc, lsans, 18, 15,
                                CW - 470, 44, 1.2)
    text_block(d, M + 470, y0, dlines, df, dlead, fill=MID)

    # folio line
    d.line([M, 2022, right, 2022], fill=HAIR, width=2)
    folio = "22.11.26 \u2014 37 STORIES"
    ff = fit_tracked(d, "folio left", folio, dsans_b, 14, 12, 2, 400)
    draw_tracked(d, M, 2028, folio, ff, 2, MID)
    foot = ("Every story here happened, or was first reported, on Sunday "
            "22 November 2026. Officials' counts and claims are attributed. "
            "Original drawings.")
    ff2 = fit_oneline(d, "folio right", foot, lsans, 16, 13, CW - 430)
    tw = d.textlength(foot, font=ff2)
    d.text((right - tw, 2028), foot, font=ff2, fill=MID)

    report_checks()

    # subtle paper grain over the whole page, then the crop marks
    noise = Image.effect_noise((W, H), 12).convert("RGB")
    img = Image.blend(img, noise, 0.015)
    d = ImageDraw.Draw(img)
    for (cx, cy, dx, dy) in [(30, 30, 1, 1), (W - 30, 30, -1, 1),
                             (30, H - 30, 1, -1), (W - 30, H - 30, -1, -1)]:
        d.line([cx, cy, cx + dx * 26, cy], fill=MID, width=2)
        d.line([cx, cy, cx, cy + dy * 26], fill=MID, width=2)
    d.ellipse([W / 2 - 7, 23, W / 2 + 7, 37], outline=MID, width=2)
    d.line([W / 2 - 11, 30, W / 2 + 11, 30], fill=MID, width=2)
    d.line([W / 2, 19, W / 2, 41], fill=MID, width=2)

    master = os.path.join(HERE, "entry-master.png")
    entry = os.path.join(HERE, "entry.png")
    img.save(master)
    img.resize((1024, 1024), Image.LANCZOS).save(entry, optimize=True)
    print("wrote", master, os.path.getsize(master))
    print("wrote", entry, os.path.getsize(entry))


if __name__ == "__main__":
    render()
