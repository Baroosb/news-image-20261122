#!/usr/bin/env python3
"""
build.py — renders the entry image for make.fun news-image-20261122.

A one-page broadsheet, "THE WORLD IN ONE DAY", summing up the world news
of Sunday 22 November 2026: 3 leads, 10 cards and a 24-item also-list —
37 stories, every one fact-audited against dated original reporting (see
STORIES.md for the frozen story set and AUDIT.md for the audit trail).

Version 4 rebuilds the page in the pattern of the winning entries of
news-image-20261121: a full-colour editorial infographic. Colour is
information — every region has its own muted print tone, used for the
lead header bands, the card pictograms and stat figures, the map pins
and the region tally. The leads carry real illustrated panels: a drawn
mini-map of the Gulf for the Bahrain strike, a COP31 draft-document and
overtime-clock panel, a Khartoum dusk skyline with drones. The cards
carry coloured pictograms and the story's own big number where it has
one; the world map is a filled landmass on an ocean panel with coloured
numbered pins; the tiers ride in small coloured pills.

Version 5 applies the owner + Musehood panel critique of v4: the
date shrinks from 168px to 104px and joins a composed masthead, and
the vertical space that frees goes to the three lead panels, which
grow from 140px to 272px tall — the Gulf map gains separate
Al-Riffa and Awali markers, arrowheads and bigger labels, the COP31
draft document and overtime clock are drawn large with a NO DEAL
stamp, and the Khartoum dusk skyline gains a background row of
buildings, bigger smoke and larger drones. Story content is
unchanged from v4.

Version 6 applies the Musehood panel's consolidated work list,
filtered against the winners: the ten mid cards trade their small
pictogram chips for full-colour scene bands across the card tops
(the winners' main device); the Bahrain panel's strike routes turn
red with orange impact bursts and a HIT OVERNIGHT tag; the COP31
panel's dead beige fills with delegate seats, bloc nameplates and
a gavel on the desk edge; the stat strip names its sources and the
50 becomes 50 MISSING; and the date-check exclusions move into a
full-width red-bordered box with larger type, so the framing can
no longer be misread as a contradiction. The standfirst strap is
unchanged: the audited story set attests no UTC clock times, so no
timeline markers could be placed without inventing them. Space
for the footer box comes from tighter brief leading and section
gaps in the bottom zones. Story content is otherwise unchanged.

Version 7 applies the panel's critique of v6: the world map is
redrawn as true coastline polygons with region labels, and its
pins are de-overlapped on leader lines so every number reads;
the standfirst strap stops repeating the three lead headlines
and instead carries three other stories' headlines, verbatim
from the cards; the three stat cards whose scene bands were
dominated by their figure blocks (Serang, Wellington, Bitcoin)
go scene-first, the figure shrunk to about three-fifths, so the
strip's big figures keep the hierarchy; the COP31 delegate rows
grow into the panel's dead ground under the clock, their bloc
nameplates set at card-headline scale; and the Bahrain panel's
two impact bursts are separated, one centred on each base.
Story content is unchanged apart from the strap's new words,
which are themselves frozen card headlines.

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


def serif_i(size):
    return ImageFont.truetype(os.path.join(LIB_DIR,
                                           "LiberationSerif-Italic.ttf"),
                              size)


def dsans_b(size):
    return ImageFont.truetype(os.path.join(DEJA_DIR, "DejaVuSans-Bold.ttf"),
                              size)


def dsans(size):
    return ImageFont.truetype(os.path.join(DEJA_DIR, "DejaVuSans.ttf"), size)


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
WHITE = (250, 248, 242)          # paper-white, text on colour

# muted editorial region tones — colour is the region code, everywhere
REGION_COLORS = {
    "Europe": (70, 100, 140),        # slate blue
    "Asia": (34, 110, 104),          # teal
    "Africa": (198, 118, 38),        # ochre
    "Americas": (96, 122, 52),       # olive green
    "Middle East": (138, 28, 19),    # oxblood red
    "Global": (51, 72, 79),          # slate
    "Oceania": (112, 72, 112),       # plum
}

TIER_COLORS = {
    "CONFIRMED": (96, 122, 52),      # olive
    "OFFICIAL": (70, 100, 140),      # slate blue
    "REPORTED": (178, 102, 30),     # ochre
}

OCEAN = (188, 206, 216)          # map panel sea
LAND_TONE = (233, 223, 196)      # map landmass
SEA = (172, 196, 208)            # Gulf mini-map sea
TAN = (226, 210, 174)            # Gulf mini-map land
GHOST = (232, 217, 208)          # oxblood at ~10% over paper
RED = (198, 26, 16)              # strike-route red (v6)
ORANGE = (232, 116, 24)          # impact-burst orange (v6)

# ---------------------------------------------------------------- content
STATS = [
    ("NO DEAL", "COP31 ends in Antalya with no agreement at all · 350.org"),
    ("2 BASES", "US positions in Bahrain hit by Iranian missiles and "
                "drones · Xinhua"),
    ("4 DEAD", "as RSF drones strike Khartoum homes and a UN building "
               "· DW"),
    ("720/9", "India's declared total — a record Test score in New "
              "Zealand · Reuters"),
    ("$61,197", "Bitcoin's Sunday print as it bounces back above "
                "$60,000 · BeInCrypto"),
    ("50 MISSING", "workers still missing in the Banten candy-factory "
                   "ruins · AP"),
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
                 "agreed. Britain said the text “moves us backwards on "
                 "the science”."),
        "source": "— The Independent / GOV.UK, 22 Nov",
        "tier": "CONFIRMED", "art": "cop",
    },
    {
        "num": 2, "band": "IRAN STRIKES BAHRAIN", "band_color": (22, 34, 66),
        "kicker": "MANAMA · MISSILES & DRONES",
        "headline": "Iran strikes US bases in Bahrain",
        "body": ("The Revolutionary Guard said its missiles and drones hit "
                 "US positions at the Al-Riffa and Awali bases overnight, "
                 "striking Patriot radars. Bahrain said a civilian industrial "
                 "site was set ablaze, two people were injured — and took "
                 "the attack to the UN."),
        "source": "— Xinhua / Arab News / Al Jazeera, 22 Nov",
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
        "source": "— Al Jazeera / DW / AFP, 22 Nov",
        "tier": "CONFIRMED", "art": "drones",
    },
]

CARDS = [
    {"num": 4, "place": "SERANG · INDONESIA", "region": "Asia",
     "headline": "Fifty missing in the factory ruins",
     "body": ("Rescuers comb the gutted Banten candy factory for 50 missing "
              "workers after Saturday evening's blaze. At least three are dead."),
     "source": "— AP / DW, 22 Nov", "tier": "CONFIRMED", "art": "flame"},
    {"num": 5, "place": "SEOUL · EXAM CHAOS", "region": "Asia",
     "headline": "Exam chaos costs a minister his job",
     "body": ("Education Minister Choi Kyo-jin resigns over last-minute CSAT "
              "security changes driven by fears of AI cheating."),
     "source": "— Yonhap / AFP, 22 Nov", "tier": "CONFIRMED", "art": "paper"},
    {"num": 6, "place": "BEIJING · MARKETS", "region": "Asia",
     "headline": "China loosens the margin screw",
     "body": ("The exchanges cut the minimum margin for leveraged share-buying "
              "from 100% to 80%, from 30 November."),
     "source": "— SZSE / Bloomberg, 22 Nov", "tier": "OFFICIAL", "art": "chart"},
    {"num": 7, "place": "WELLINGTON · CRICKET", "region": "Oceania",
     "headline": "India pile up 720 in Wellington",
     "body": ("Pant's hundred powers a record 720/9 declared; New Zealand "
              "close day four at 119/2, trailing by 233."),
     "source": "— Reuters / Sportstar, 22 Nov", "tier": "CONFIRMED", "art": "cricket"},
    {"num": 8, "place": "LAS VEGAS · FORMULA 1", "region": "Americas",
     "headline": "Verstappen wins a wild one in Vegas",
     "body": ("He beats Norris and Piastri as Russell's late lock-up drops him "
              "to ninth — and the Ferraris collide again."),
     "source": "— Formula1.com / Sky, 22 Nov", "tier": "CONFIRMED", "art": "car"},
    {"num": 9, "place": "MARKETS · CRYPTO", "region": "Global",
     "headline": "Bitcoin bounces above $60,000",
     "body": ("After a two-month low amid “extreme fear”, BTC rebounds "
              "as short sellers are squeezed out of crowded bets."),
     "source": "— BeInCrypto, 22 Nov", "tier": "CONFIRMED", "art": "coin"},
    {"num": 10, "place": "WASHINGTON · IRAN WAR", "region": "Americas",
     "headline": "Trump: no regime change in Iran",
     "body": ("“I never cared too much about the regime” — he wants "
              "a permanent deal barring nuclear weapons instead."),
     "source": "— India Today, 22 Nov", "tier": "REPORTED", "art": "dome"},
    {"num": 11, "place": "WASHINGTON · CYBER", "region": "Americas",
     "headline": "Trump shrugs at the FBI hack",
     "body": ("The reported database breach is “not good”, he says "
              "— “but maybe we'll learn things.”"),
     "source": "— Euronews, 22 Nov", "tier": "REPORTED", "art": "shield"},
    {"num": 12, "place": "KYIV · UKRAINE", "region": "Europe",
     "headline": "“Big bosses can't decide fate”",
     "body": ("Zelenskyy answers the Trump–Putin–Xi meeting in China: "
              "big powers cannot settle the world's future."),
     "source": "— Euromaidan Press, 22 Nov", "tier": "CONFIRMED", "art": "quote"},
    {"num": 13, "place": "OYO · DIPLOMACY", "region": "Africa",
     "headline": "Kenya and the DRC mend fences",
     "body": ("Ruto and Tshisekedi agree in Oyo to restore diplomatic ties, "
              "at a four-leader meeting on peace and security."),
     "source": "— The Standard, 22 Nov", "tier": "CONFIRMED", "art": "hands"},
]

ALSO = [
    ("BALTIYSK", "Explosions and drone activity reported at Russia's Baltic Fleet base", "Euromaidan"),
    ("BENGHAZI", "Ukrainian drones strike a Russian military vessel in port", "Il Sole 24 Ore"),
    ("DYMER", "Death toll from the Russian attack rises to three", "Il Sole 24 Ore"),
    ("TEHRAN", "Moves to break the US blockade; threatens Gulf oil fields ablaze", "Yeshiva World"),
    ("HORMUZ", "Swimmer Lewis Pugh braves the strait for its wildlife", "Arab News"),
    ("VATICAN", "Pope Leo XIV lunches with 1,300 people living in poverty", "Vatican News"),
    ("LONDON", "Minister condemns Trump's embrace of “butcher” Putin", "Independent"),
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

# ------------------------------------------------------- v4 presentation
# Region of each lead (the LEADS dicts carry no region field of their own)
LEAD_REGION = {1: "Global", 2: "Middle East", 3: "Africa"}

# A card's big figure, where the frozen text itself carries one:
# story number -> (figure, caption). Figures and caption words are taken
# from the frozen STATS / body text above, never invented.
CARD_STAT = {
    4: ("50", "MISSING"),
    6: ("80%", "WAS 100%"),
    7: ("720/9", "DECLARED"),
    8: ("9TH", "RUSSELL"),
    9: ("$61,197", "SUNDAY PRINT"),
}

# story number -> region, for the map pins and the brief chips
# (regions as recorded in STORIES.md)
PIN_REGION = {
    1: "Global", 2: "Middle East", 3: "Africa", 4: "Asia", 5: "Asia",
    6: "Asia", 7: "Oceania", 8: "Americas", 9: "Global", 10: "Americas",
    11: "Americas", 12: "Europe", 13: "Africa", 14: "Europe",
    15: "Africa", 16: "Europe", 17: "Middle East", 18: "Middle East",
    19: "Europe", 20: "Europe", 21: "Europe", 22: "Europe",
    23: "Europe", 24: "Asia", 25: "Oceania", 26: "Asia", 27: "Asia",
    28: "Africa", 29: "Americas", 30: "Americas", 31: "Asia",
    32: "Africa", 33: "Africa", 34: "Asia", 35: "Africa",
    36: "Americas", 37: "Global",
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
    while text and draw.textlength(text + "…", font=fnt) > max_w:
        text = text[:-1]
    return text.rstrip() + "…"


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


# ------------------------------------------------------------- components
def pill(draw, x, y, tier, size=13, light=False):
    """A small coloured tier pill, drawn from its top-left corner.
    Returns its width. `light` draws a paper pill with ink text, for
    sitting on a coloured band."""
    fnt = dsans_b(size)
    tw = draw.textlength(tier, font=fnt)
    w_ = tw + 22
    h_ = size + 11
    if light:
        draw.rounded_rectangle([x, y, x + w_, y + h_], radius=h_ / 2,
                               fill=PAPER)
        draw.text((x + 11, y + 4), tier, font=fnt, fill=INK)
    else:
        draw.rounded_rectangle([x, y, x + w_, y + h_], radius=h_ / 2,
                               fill=TIER_COLORS[tier])
        draw.text((x + 11, y + 4), tier, font=fnt, fill=WHITE)
    return w_


def pill_width(draw, tier, size=13):
    return draw.textlength(tier, font=dsans_b(size)) + 22


def starburst(draw, cx, cy, r, fill, spikes=12, inner=0.42):
    pts = []
    for i in range(spikes * 2):
        a = math.pi * i / spikes - math.pi / 2
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    draw.polygon(pts, fill=fill)


def dashed_bezier(draw, p0, p1, p2, fill, width=4, dash=15, gap=10):
    """A dashed quadratic-bezier stroke (missile routes on the map)."""
    pts = []
    for i in range(121):
        t = i / 120
        px = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        py = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((px, py))
    seg, pen = [], True
    acc = 0.0
    for i in range(1, len(pts)):
        step = math.dist(pts[i - 1], pts[i])
        if pen:
            seg.append(pts[i - 1])
        acc += step
        limit = dash if pen else gap
        if acc >= limit:
            if pen and len(seg) >= 1:
                draw.line(seg + [pts[i]], fill=fill, width=width)
            seg, pen, acc = [], not pen, 0.0
    if pen and len(seg) >= 1:
        draw.line(seg + [pts[-1]], fill=fill, width=width)


def lead_body(draw, x, y, lead, col_w, zone_h):
    """Lead body with a drop cap: the first letter enlarged in the
    region colour, the first two lines set narrower to clear it."""
    body = lead["body"]
    cap, rest = body[0], body[1:]
    region = REGION_COLORS[LEAD_REGION[lead["num"]]]
    size, fnt, cap_f, cap_w, lines = 19, None, None, 0, []
    for size in (22, 21, 20, 19, 18):
        fnt = lsans(size)
        cap_f = serif_b(int(size * 2.8))
        cap_w = draw.textlength(cap, font=cap_f)
        widths = [col_w - cap_w - 14, col_w - cap_w - 14, col_w]
        lines = wrap_var(draw, rest, fnt, widths)
        if len(lines) * size * 1.24 <= zone_h:
            break
    height = len(lines) * size * 1.24
    _register(f"lead{lead['num']} body", height, zone_h)
    draw.text((x, y - size * 0.30), cap, font=cap_f, fill=region)
    ly = y
    for i, ln in enumerate(lines):
        lx = x + (cap_w + 14 if i < 2 else 0)
        draw.text((lx, ly), ln, font=fnt, fill=INK)
        ly += size * 1.24
    return size


# ------------------------------------------------------- lead art panels
# Each lead illustration is a full-colour panel drawn in code: a Gulf
# mini-map, a COP31 document/clock panel, a Khartoum dusk skyline.
def art_cop(d, x, y, w_, h):
    """COP31, drawn large: slate name block, the draft document with
    'fossil fuels' struck out in oxblood and a NO DEAL stamp, and a
    big overtime pie-clock."""
    d.rectangle([x, y, x + w_, y + h], fill=(238, 233, 219))
    # summit name block
    bw = 150
    d.rectangle([x, y, x + bw, y + h], fill=SLATE)
    f1 = serif_b(34)
    _register("cop panel COP31", d.textlength("COP31", font=f1), bw - 16)
    d.text((x + bw / 2, y + 34), "COP31", font=f1, fill=WHITE, anchor="ma")
    f2 = dsans_b(15)
    draw_tracked(d, x + (bw - tracked_width(d, "ANTALYA", f2, 3)) / 2,
                 y + 94, "ANTALYA", f2, 3, WHITE)
    f3 = dsans_b(11)
    for i, ln in enumerate(["UN CLIMATE", "SUMMIT"]):
        draw_tracked(d, x + (bw - tracked_width(d, ln, f3, 2)) / 2,
                     y + 120 + i * 17, ln, f3, 2, (196, 208, 210))
    d.line([x + 22, y + h - 62, x + bw - 22, y + h - 62], fill=(196, 208, 210),
           width=2)
    f4 = dsans_b(12)
    draw_tracked(d, x + (bw - tracked_width(d, "TALKS END", f4, 2)) / 2,
                 y + h - 48, "TALKS END", f4, 2, WHITE)
    # the draft document, large, with ruled lines top and bottom
    dx, dy, dw, dh = x + 166, y + 16, 246, h - 32
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(252, 250, 244),
                outline=MID, width=2)
    ft = dsans_b(15)
    d.text((dx + 16, dy + 12), "DRAFT TEXT", font=ft, fill=INK)
    for i, lw in enumerate([0.94, 0.84, 0.90, 0.78, 0.88]):
        ly = dy + 46 + i * 14
        d.line([dx + 16, ly, dx + 16 + (dw - 32) * lw, ly],
               fill=(168, 160, 148), width=4)
    ff = lsans_b(34)
    strike = "fossil fuels"
    _register("cop panel strike", d.textlength(strike, font=ff), dw - 28)
    d.text((dx + 16, dy + 122), strike, font=ff, fill=OXB)
    sw = d.textlength(strike, font=ff)
    d.line([dx + 13, dy + 144, dx + 19 + sw, dy + 144], fill=OXB, width=5)
    fc = dsans_b(12)
    d.text((dx + 16, dy + 158), "NOT MENTIONED", font=fc, fill=MID)
    for i, lw in enumerate([0.88, 0.80]):
        ly = dy + 190 + i * 14
        d.line([dx + 16, ly, dx + 16 + (dw - 32) * lw, ly],
               fill=(168, 160, 148), width=4)
    # NO DEAL stamp, bottom-right of the document
    sx0, sy0, sx1, sy1 = dx + 106, dy + dh - 52, dx + dw - 14, dy + dh - 10
    d.rectangle([sx0, sy0, sx1, sy1], outline=OXB, width=3)
    d.rectangle([sx0 + 4, sy0 + 4, sx1 - 4, sy1 - 4], outline=OXB, width=1)
    fst = serif_b(20)
    _register("cop panel stamp", d.textlength("NO DEAL", font=fst),
              sx1 - sx0 - 16)
    d.text(((sx0 + sx1) / 2, (sy0 + sy1) / 2), "NO DEAL", font=fst,
           fill=OXB, anchor="mm")
    # overtime pie-clock, big
    cx, cy, r = x + w_ - 92, y + 102, 74
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 250, 244),
              outline=INK, width=3)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], start=-90, end=0, fill=OXB)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        d.line([cx + math.cos(rad) * (r - 12), cy + math.sin(rad) * (r - 12),
                cx + math.cos(rad) * (r - 4), cy + math.sin(rad) * (r - 4)],
               fill=INK, width=2)
    d.line([cx, cy, cx + 8, cy - r * 0.62], fill=INK, width=5)
    d.line([cx, cy, cx + r * 0.55, cy + 13], fill=INK, width=5)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=INK)
    fo = dsans_b(16)
    label = "OVERTIME"
    _register("cop panel overtime", tracked_width(d, label, fo, 2), 176)
    draw_tracked(d, cx - tracked_width(d, label, fo, 2) / 2, cy + r + 14,
                 label, fo, 2, OXB)
    # v6: fill the dead beige at the panel's right and base — a desk
    # edge along the document's foot with the gavel resting on it,
    # and rows of delegate seats seen from behind, nameplates up
    d.rectangle([dx - 4, y + 250, x + w_ - 8, y + 262],
                fill=(150, 120, 84))
    d.line([dx - 4, y + 250, x + w_ - 8, y + 250], fill=(110, 84, 58),
           width=3)
    # the gavel, resting on the desk at the document's bottom-left:
    # a capped head on its sound block, a two-tone handle angled
    # down across the desk edge (v7: scaled up with the assembly)
    d.rectangle([dx + 18, y + 253, dx + 70, y + 258], fill=(96, 70, 44))
    d.rectangle([dx + 23, y + 232, dx + 66, y + 252], fill=(110, 78, 46))
    d.rectangle([dx + 18, y + 232, dx + 26, y + 252], fill=(84, 58, 34))
    d.rectangle([dx + 63, y + 232, dx + 71, y + 252], fill=(84, 58, 34))
    d.line([dx + 23, y + 236, dx + 66, y + 236], fill=(196, 156, 104),
           width=2)
    d.line([dx + 66, y + 241, dx + 104, y + 254], fill=(96, 66, 40),
           width=9)
    d.line([dx + 66, y + 241, dx + 104, y + 254], fill=(172, 130, 82),
           width=5)
    # v7: the delegate assembly grows into the dead ground under
    # the clock — a back row of four bigger delegates, then a front
    # row of three whose bloc nameplates are set at card-headline
    # scale so they read at entry size
    back_shades = [(96, 90, 84), (104, 98, 92), (92, 86, 80),
                   (100, 94, 88)]
    for i, off in enumerate([452, 494, 534, 574]):
        cx = x + off
        d.ellipse([cx - 11, y + 208, cx + 11, y + 230],
                  fill=(70, 62, 55))
        d.rectangle([cx - 19, y + 228, cx + 19, y + 248],
                    fill=back_shades[i])
    fp = dsans_b(19)
    for name, cx, pw in [("EU", x + 436, 44), ("G77", x + 487, 56),
                         ("BRICS", x + 555, 72)]:
        d.ellipse([cx - 13, y + 221, cx + 13, y + 247],
                  fill=(43, 38, 34))
        d.rectangle([cx - 26, y + 243, cx + 26, y + 264],
                    fill=(58, 52, 47))
        d.rectangle([cx - pw / 2, y + 251, cx + pw / 2, y + 271],
                    fill=(252, 250, 244), outline=MID, width=1)
        _register(f"cop nameplate {name}",
                  d.textlength(name, font=fp), pw - 8)
        d.text((cx, y + 261), name, font=fp, fill=INK, anchor="mm")


def art_gulf(d, x, y, w_, h):
    """A drawn map of the Gulf, large: tan land, blue sea, dashed
    oxblood strike routes with arrowheads from Iran to the two
    Bahrain bases — Al-Riffa on the island, Awali just south."""
    d.rectangle([x, y, x + w_, y + h], fill=SEA)

    def P(u, v):
        return (x + u * w_, y + v * h)

    def bez(p0, p1, p2, t):
        return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0]
                + t ** 2 * p2[0],
                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1]
                + t ** 2 * p2[1])

    def arrowhead(p0, p1, p2):
        tip = bez(p0, p1, p2, 0.965)
        back = bez(p0, p1, p2, 0.86)
        vx, vy = tip[0] - back[0], tip[1] - back[1]
        n = math.hypot(vx, vy) or 1.0
        vx, vy = vx / n, vy / n
        bx_, by_ = tip[0] - vx * 17, tip[1] - vy * 17
        d.polygon([tip, (bx_ - vy * 8, by_ + vx * 8),
                   (bx_ + vy * 8, by_ - vx * 8)], fill=RED)

    # Iran, across the top
    iran = [(0.50, 0.0), (1.0, 0.0), (1.0, 0.54), (0.95, 0.52),
            (0.90, 0.40), (0.83, 0.43), (0.77, 0.32), (0.715, 0.335),
            (0.68, 0.36), (0.645, 0.30), (0.61, 0.25), (0.575, 0.265),
            (0.55, 0.28), (0.50, 0.16)]
    d.polygon([P(u, v) for u, v in iran], fill=TAN)
    # Arabia, bottom-left, its coast facing the Gulf
    arabia = [(0.0, 0.30), (0.14, 0.36), (0.23, 0.44), (0.30, 0.55),
              (0.335, 0.605), (0.37, 0.66), (0.47, 0.79), (0.58, 0.90),
              (0.68, 1.0), (0.0, 1.0)]
    d.polygon([P(u, v) for u, v in arabia], fill=TAN)
    # Qatar, a small peninsula on the Arabian coast
    qatar = [(0.252, 0.475), (0.285, 0.385), (0.315, 0.40), (0.322, 0.50),
             (0.30, 0.565), (0.268, 0.55)]
    d.polygon([P(u, v) for u, v in qatar], fill=TAN)
    # Oman / UAE corner, bottom-right, with the Musandam jut
    oman = [(0.80, 1.0), (0.86, 0.80), (0.915, 0.66), (0.945, 0.545),
            (0.965, 0.60), (1.0, 0.60), (1.0, 1.0)]
    d.polygon([P(u, v) for u, v in oman], fill=TAN)
    # two low islets in the Gulf sea
    for (iu, iv, ir) in [(0.52, 0.56, 5), (0.60, 0.64, 4)]:
        ix, iy = P(iu, iv)
        d.ellipse([ix - ir, iy - ir * 0.7, ix + ir, iy + ir * 0.7], fill=TAN)
    # Bahrain island (Al-Riffa) and the Awali marker just south of it
    bx, by = P(0.345, 0.44)
    d.ellipse([bx - 11, by - 8, bx + 11, by + 8], fill=TAN, outline=INK,
              width=2)
    ax_, ay_ = P(0.315, 0.575)
    # v6: two dashed RED trajectories, one to each base, each ending
    # in an orange impact burst — the attack must be unmissable
    r1 = (P(0.70, 0.345), P(0.55, 0.02), (bx, by))
    r3 = (P(0.66, 0.35), P(0.44, 0.10), (ax_, ay_))
    for rt in (r1, r3):
        dashed_bezier(d, *rt, RED, 5)
        arrowhead(*rt)
    # v7: two clearly separated bursts, one centred on each base —
    # at v6 sizes (30 + 22 against centres ~41px apart) they merged
    # into a single blob; 19 + 17 leaves a visible gap between them
    starburst(d, bx, by, 19, ORANGE)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=INK)
    starburst(d, ax_, ay_, 17, ORANGE)
    d.ellipse([ax_ - 4, ay_ - 4, ax_ + 4, ay_ + 4], fill=INK)
    # a small red tag in the open sea south-east of the island
    ftg = dsans_b(14)
    tag = "HIT OVERNIGHT"
    tag_w = d.textlength(tag, font=ftg) + 18
    _register("gulf tag", tag_w, 170)
    tx, ty = P(0.37, 0.60)
    d.rounded_rectangle([tx, ty, tx + tag_w, ty + 25], radius=4,
                        fill=RED)
    d.text((tx + tag_w / 2, ty + 12), tag, font=ftg, fill=WHITE,
           anchor="mm")
    # labels
    fi = dsans_b(30)
    _register("gulf label IRAN", tracked_width(d, "IRAN", fi, 5), 220)
    draw_tracked(d, *P(0.755, 0.09), "IRAN", fi, 5, INK)
    fs = dsans_b(19)
    _register("gulf label SAUDI", tracked_width(d, "SAUDI ARABIA", fs, 2),
              240)
    draw_tracked(d, *P(0.03, 0.82), "SAUDI ARABIA", fs, 2, INK)
    fq = dsans_b(16)
    _register("gulf label QATAR", tracked_width(d, "QATAR", fq, 2), 110)
    draw_tracked(d, *P(0.13, 0.40), "QATAR", fq, 2, INK)
    fb = dsans_b(22)
    _register("gulf label BAHRAIN", tracked_width(d, "BAHRAIN", fb, 2), 190)
    draw_tracked(d, *P(0.15, 0.10), "BAHRAIN", fb, 2, INK)
    fa = dsans_b(13)
    _register("gulf label AL-RIFFA", tracked_width(d, "AL-RIFFA", fa, 1),
              130)
    draw_tracked(d, *P(0.15, 0.205), "AL-RIFFA", fa, 1, OXB)
    _register("gulf label AWALI", tracked_width(d, "AWALI", fa, 1), 100)
    draw_tracked(d, *P(0.115, 0.635), "AWALI", fa, 1, OXB)
    fg = dsans(20)
    _register("gulf label THE GULF", tracked_width(d, "THE GULF", fg, 3),
              190)
    draw_tracked(d, *P(0.53, 0.72), "THE GULF", fg, 3, (40, 60, 68))
    fh = dsans_b(13)
    _register("gulf label HORMUZ",
              tracked_width(d, "STRAIT OF HORMUZ", fh, 0.5), 230)
    draw_tracked(d, *P(0.63, 0.47), "STRAIT OF HORMUZ", fh, 0.5,
                 (40, 60, 68))
    # compass
    nx, ny = P(0.04, 0.09)
    d.polygon([(nx, ny - 18), (nx + 8, ny + 8), (nx, ny + 2),
               (nx - 8, ny + 8)], fill=INK)
    d.text((nx, ny + 12), "N", font=dsans_b(16), fill=INK, anchor="ma")


def art_khartoum(d, x, y, w_, h):
    """Khartoum at dusk: banded sky, a low sun, smoke over an ink
    skyline, a UN tower, filled drone silhouettes, oxblood blasts."""
    # banded dusk sky, slate at the top warming to ochre at the horizon
    top = (74, 88, 96)
    mid = (168, 116, 66)
    low = (226, 178, 112)
    horizon = y + h * 0.66
    yy = y
    while yy < horizon:
        t = (yy - y) / max(1, horizon - y)
        if t < 0.5:
            tt = t * 2
            col = tuple(int(top[i] + (mid[i] - top[i]) * tt)
                        for i in range(3))
        else:
            tt = (t - 0.5) * 2
            col = tuple(int(mid[i] + (low[i] - mid[i]) * tt)
                        for i in range(3))
        d.line([x, yy, x + w_, yy], fill=col)
        yy += 3
    d.rectangle([x, horizon, x + w_, y + h], fill=(52, 44, 38))
    # low sun, large
    sx, sy, sr = x + w_ * 0.80, horizon - 24, 40
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(243, 216, 150))
    base = y + h
    heights = [0.30, 0.46, 0.36, 0.58, 0.42, 0.52, 0.34, 0.48, 0.38, 0.55,
               0.40, 0.44]
    # background skyline: a lighter, lower row behind for depth
    bx = x + 2
    i = 0
    while bx < x + w_ - 20:
        bw = w_ * 0.055
        bh = h * heights[(i + 3) % len(heights)] * 0.55
        d.rectangle([bx, base - bh, bx + bw, base], fill=(84, 72, 62))
        bx += bw + 9
        i += 1
    # foreground skyline silhouette
    bx = x + 6
    tops = []
    i = 0
    while bx < x + w_ - 30:
        bw = w_ * 0.052
        bh = h * heights[i % len(heights)]
        d.rectangle([bx, base - bh, bx + bw, base], fill=INK)
        tops.append((bx + bw / 2, base - bh))
        bx += bw + 5
        i += 1
    # the UN tower: taller, prominent, with a flag and the letters
    ux, uw = x + w_ * 0.435, w_ * 0.09
    uh = h * 0.74
    d.rectangle([ux, base - uh, ux + uw, base], fill=INK)
    d.line([ux + uw / 2, base - uh, ux + uw / 2, base - uh - 26],
           fill=INK, width=3)
    d.polygon([(ux + uw / 2, base - uh - 26), (ux + uw / 2 + 30,
               base - uh - 18), (ux + uw / 2, base - uh - 10)],
              fill=(120, 170, 205))
    fu = dsans_b(26)
    _register("khartoum UN", d.textlength("UN", font=fu), uw)
    d.text((ux + uw / 2, base - uh + 16), "UN", font=fu, fill=WHITE,
           anchor="ma")
    # smoke plumes: bigger layered ellipses drifting up-right
    for (px, py) in [tops[2], tops[8]]:
        for k in range(5):
            ex = px + k * 21
            ey = py - 14 - k * 17
            er = 16 + k * 8
            shade = (140 + k * 20, 132 + k * 20, 124 + k * 19)
            d.ellipse([ex - er, ey - er * 0.62, ex + er, ey + er * 0.62],
                      fill=shade)
    # blast starbursts on the skyline
    starburst(d, tops[4][0], tops[4][1] + 4, 22, OXB)
    starburst(d, tops[10][0], tops[10][1] + 4, 19, OXB)
    # drones: filled quadcopter silhouettes, larger
    for (du, dv, s) in [(0.15, 0.17, 1.0), (0.55, 0.10, 0.8),
                        (0.72, 0.27, 0.62)]:
        cx, cy = x + w_ * du, y + h * dv
        r = 34 * s
        for (ax, ay) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            ex, ey = cx + ax * r, cy + ay * r * 0.62
            d.line([cx, cy, ex, ey], fill=INK, width=max(3, int(5 * s)))
            d.ellipse([ex - 8 * s, ey - 3.5 * s, ex + 8 * s, ey + 3.5 * s],
                      fill=INK)
        d.ellipse([cx - 8 * s, cy - 5 * s, cx + 8 * s, cy + 5 * s],
                  fill=INK)
    # v6: one larger, clearer drone high in the sky, rotor discs up
    cx, cy, r = x + w_ * 0.40, y + h * 0.14, 44
    for (ax, ay) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        ex, ey = cx + ax * r, cy + ay * r * 0.62
        d.line([cx, cy, ex, ey], fill=INK, width=6)
        d.ellipse([ex - 13, ey - 5, ex + 13, ey + 5], outline=INK,
                  width=2)
        d.ellipse([ex - 8, ey - 3, ex + 8, ey + 3], fill=INK)
    d.ellipse([cx - 11, cy - 6, cx + 11, cy + 6], fill=INK)
    d.ellipse([cx - 3, cy + 5, cx + 3, cy + 10], fill=INK)


ART = {"cop": art_cop, "missiles": art_gulf, "drones": art_khartoum}

# ------------------------------------------------------------ pictograms
# Simple bold glyphs in paper-white on a region-colour chip.
def draw_icon(d, x, y, s, kind, region):
    d.rounded_rectangle([x, y, x + s, y + s], radius=8,
                        fill=REGION_COLORS[region])
    fg = WHITE

    def R(u0, v0, u1, v1):
        return [x + u0 * s, y + v0 * s, x + u1 * s, y + v1 * s]

    def L(pts, wdt=4):
        d.line([(x + u * s, y + v * s) for u, v in pts], fill=fg, width=wdt)

    if kind == "flame":      # factory with a flame over the chimney
        d.rectangle(R(0.20, 0.46, 0.72, 0.86), fill=fg)
        d.rectangle(R(0.26, 0.24, 0.38, 0.46), fill=fg)
        d.polygon([(x + 0.32 * s, y + 0.06 * s), (x + 0.40 * s, y + 0.20 * s),
                   (x + 0.24 * s, y + 0.20 * s)], fill=fg)
        for (wu, wv) in [(0.30, 0.58), (0.46, 0.58), (0.30, 0.72),
                         (0.46, 0.72)]:
            d.rectangle(R(wu, wv, wu + 0.09, wv + 0.09),
                        fill=REGION_COLORS[region])
    elif kind == "paper":    # exam sheet with a tick
        d.rectangle(R(0.28, 0.13, 0.72, 0.87), fill=fg)
        for i, lw in enumerate([0.30, 0.34, 0.26]):
            ly = 0.28 + i * 0.13
            d.line([x + 0.36 * s, y + ly * s, x + (0.36 + lw) * s,
                    y + ly * s], fill=REGION_COLORS[region], width=4)
        L([(0.38, 0.70), (0.48, 0.79), (0.64, 0.60)], 5)
        # redraw the tick in the region colour on the white sheet
        d.line([(x + 0.38 * s, y + 0.70 * s), (x + 0.48 * s, y + 0.79 * s),
                (x + 0.64 * s, y + 0.60 * s)], fill=REGION_COLORS[region],
               width=5)
    elif kind == "chart":    # margin arrow, rising
        L([(0.18, 0.16), (0.18, 0.82), (0.84, 0.82)], 4)
        L([(0.24, 0.66), (0.44, 0.48), (0.56, 0.56), (0.76, 0.30)], 5)
        d.polygon([(x + 0.80 * s, y + 0.22 * s), (x + 0.80 * s, y + 0.40 * s),
                   (x + 0.64 * s, y + 0.28 * s)], fill=fg)
    elif kind == "cricket":  # bat and ball
        d.polygon([(x + 0.30 * s, y + 0.30 * s), (x + 0.44 * s, y + 0.40 * s),
                   (x + 0.34 * s, y + 0.82 * s), (x + 0.18 * s, y + 0.72 * s)],
                  fill=fg)
        L([(0.38, 0.34), (0.58, 0.16)], 6)
        d.ellipse(R(0.60, 0.58, 0.84, 0.82), fill=fg)
        d.arc(R(0.65, 0.58, 0.89, 0.82), start=100, end=260,
              fill=REGION_COLORS[region], width=3)
    elif kind == "car":      # chequered flag
        L([(0.26, 0.12), (0.26, 0.88)], 5)
        d.rectangle(R(0.26, 0.14, 0.82, 0.52), fill=fg)
        for r_ in range(2):
            for c_ in range(3):
                if (r_ + c_) % 2 == 0:
                    d.rectangle(R(0.26 + c_ * 0.187, 0.14 + r_ * 0.19,
                                  0.26 + (c_ + 1) * 0.187,
                                  0.14 + (r_ + 1) * 0.19),
                                fill=REGION_COLORS[region])
    elif kind == "coin":     # bitcoin-ish B in a ring
        d.ellipse(R(0.14, 0.14, 0.86, 0.86), outline=fg, width=5)
        fb = serif_b(int(s * 0.52))
        d.text((x + s / 2, y + s * 0.47), "B", font=fb, fill=fg,
               anchor="mm")
        for bx in (0.44, 0.56):
            d.line([x + bx * s, y + 0.22 * s, x + bx * s, y + 0.30 * s],
                   fill=fg, width=3)
            d.line([x + bx * s, y + 0.70 * s, x + bx * s, y + 0.78 * s],
                   fill=fg, width=3)
    elif kind == "dome":     # capitol dome
        d.pieslice(R(0.26, 0.22, 0.74, 0.66), start=180, end=360, fill=fg)
        L([(0.50, 0.10), (0.50, 0.24)], 4)
        d.rectangle(R(0.18, 0.64, 0.82, 0.72), fill=fg)
        for cu in (0.26, 0.42, 0.58, 0.72):
            d.rectangle(R(cu, 0.72, cu + 0.05, 0.84), fill=fg)
        d.rectangle(R(0.16, 0.84, 0.84, 0.89), fill=fg)
    elif kind == "shield":   # shield with a bolt
        d.polygon([(x + 0.50 * s, y + 0.12 * s), (x + 0.80 * s, y + 0.22 * s),
                   (x + 0.78 * s, y + 0.52 * s), (x + 0.50 * s, y + 0.88 * s),
                   (x + 0.22 * s, y + 0.52 * s), (x + 0.20 * s, y + 0.22 * s)],
                  outline=fg, width=5)
        d.polygon([(x + 0.55 * s, y + 0.30 * s), (x + 0.40 * s, y + 0.55 * s),
                   (x + 0.50 * s, y + 0.55 * s), (x + 0.44 * s, y + 0.74 * s),
                   (x + 0.62 * s, y + 0.46 * s), (x + 0.51 * s, y + 0.46 * s)],
                  fill=fg)
    elif kind == "quote":    # big quotation mark
        fq = serif_b(int(s * 0.78))
        d.text((x + s / 2, y + s * 0.52), "“", font=fq, fill=fg,
               anchor="mm")
    elif kind == "hands":    # fence mended: posts and rails
        for pu in (0.24, 0.47, 0.70):
            d.rectangle(R(pu, 0.20, pu + 0.08, 0.84), fill=fg)
            d.polygon([(x + pu * s, y + 0.20 * s),
                       (x + (pu + 0.04) * s, y + 0.12 * s),
                       (x + (pu + 0.08) * s, y + 0.20 * s)], fill=fg)
        d.rectangle(R(0.16, 0.36, 0.84, 0.44), fill=fg)
        d.rectangle(R(0.16, 0.60, 0.84, 0.68), fill=fg)


# ------------------------------------------------------------ card bands
# v6: each mid card carries a drawn full-colour scene band across its
# top — the winners' main device — in the same flat style as the lead
# panels. Stat cards keep their figure in a paper block at the band's
# right end, so the scene is drawn in the remaining width.
def band_factory(d, x, y, w_, h):
    """Serang: factory silhouette, smoke plume, rescue lights."""
    d.rectangle([x, y, x + w_, y + h], fill=(219, 170, 108))
    # smoke plume from the chimney, drifting right and thinning
    for k, (su, sv, sr) in enumerate([(0.16, 0.14, 9), (0.21, 0.09, 12),
                                      (0.27, 0.05, 15), (0.34, 0.03, 18)]):
        shade = (118 + k * 14, 112 + k * 14, 106 + k * 13)
        cx, cy = x + su * w_, y + sv * h + 6
        d.ellipse([cx - sr, cy - sr * 0.62, cx + sr, cy + sr * 0.62],
                  fill=shade)
    # factory silhouette: chimney, sawtooth main block, side block
    d.rectangle([x + 0.10 * w_, y + 16, x + 0.17 * w_, y + h - 10],
                fill=INK)
    d.rectangle([x + 0.05 * w_, y + 34, x + 0.55 * w_, y + h - 10],
                fill=INK)
    for k in range(3):
        tx = x + (0.05 + k * 0.167) * w_
        d.polygon([(tx, y + 34), (tx + 0.083 * w_, y + 24),
                   (tx + 0.167 * w_, y + 34)], fill=INK)
    d.rectangle([x + 0.58 * w_, y + 40, x + 0.80 * w_, y + h - 10],
                fill=INK)
    # fire glow at the base of the main block, ground, rescue lights
    d.ellipse([x + 0.20 * w_, y + h - 18, x + 0.38 * w_, y + h - 4],
              fill=(206, 74, 32))
    d.rectangle([x, y + h - 10, x + w_, y + h], fill=(96, 78, 60))
    for lu in (0.60, 0.70, 0.80, 0.90):
        cx = x + lu * w_
        d.ellipse([cx - 3.5, y + h - 9, cx + 3.5, y + h - 2],
                  fill=(255, 198, 64))


def band_exam(d, x, y, w_, h):
    """Seoul: exam-hall gate, a CSAT paper with a grade stamp, a clock."""
    d.rectangle([x, y, x + w_, y + h], fill=(203, 219, 211))
    d.rectangle([x + 0.03 * w_, y + 5, x + 0.97 * w_, y + 15], fill=SLATE)
    for pu in (0.05, 0.90):
        d.rectangle([x + pu * w_, y + 15, x + (pu + 0.05) * w_, y + h],
                    fill=SLATE)
    px0, px1 = x + 0.34 * w_, x + 0.62 * w_
    d.rectangle([px0, y + 10, px1, y + 54], fill=(252, 250, 244),
                outline=MID, width=2)
    for i, lw in enumerate([0.80, 0.66, 0.74, 0.52]):
        ly = y + 19 + i * 8
        d.line([px0 + 8, ly, px0 + 8 + (px1 - px0 - 16) * lw, ly],
               fill=(168, 160, 148), width=3)
    d.ellipse([px1 - 24, y + 36, px1 - 10, y + 50], outline=OXB, width=2)
    cx, cy, r = x + 0.79 * w_, y + 31, 14
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 250, 244),
              outline=INK, width=2)
    d.line([cx, cy, cx, cy - 8], fill=INK, width=2)
    d.line([cx, cy, cx + 7, cy + 4], fill=INK, width=2)


def band_margin(d, x, y, w_, h):
    """Beijing: a margin line dropping 100 to 80, and a gear."""
    d.rectangle([x, y, x + w_, y + h], fill=(43, 62, 70))
    for gv in (0.28, 0.52, 0.76):
        lx = x
        while lx < x + w_ - 12:
            d.line([lx, y + gv * h, lx + 7, y + gv * h],
                   fill=(92, 112, 120), width=1)
            lx += 14
    pts = [(0.05, 0.32), (0.22, 0.38), (0.38, 0.54), (0.54, 0.66)]
    d.line([(x + u * w_, y + v * h) for u, v in pts],
           fill=(255, 138, 92), width=4)
    for u, v in pts:
        cx, cy = x + u * w_, y + v * h
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 138, 92))
    f1 = dsans_b(14)
    d.text((x + 0.05 * w_, y + 3), "100", font=f1, fill=WHITE)
    d.text((x + 0.54 * w_, y + 0.70 * h), "80", font=f1,
           fill=(255, 138, 92))
    gx, gy = x + 0.84 * w_, y + 0.50 * h
    starburst(d, gx, gy, 17, (198, 206, 212), spikes=8, inner=0.80)
    d.ellipse([gx - 6, gy - 6, gx + 6, gy + 6], fill=(43, 62, 70))


def band_cricket(d, x, y, w_, h):
    """Wellington: mow stripes, the pitch, stumps and a red ball."""
    n = 6
    for i in range(n):
        col = (104, 146, 74) if i % 2 == 0 else (117, 159, 83)
        d.rectangle([x + i * w_ / n, y, x + (i + 1) * w_ / n, y + h],
                    fill=col)
    d.rectangle([x + 0.06 * w_, y + 22, x + 0.94 * w_, y + 40],
                fill=(226, 210, 174))
    for cu in (0.10, 0.86):
        d.line([x + cu * w_, y + 22, x + cu * w_, y + 40], fill=WHITE,
               width=2)
    for k in range(3):
        sx = x + (0.885 + k * 0.018) * w_
        d.line([sx, y + 16, sx, y + 34], fill=(250, 248, 242), width=3)
    d.line([x + 0.885 * w_, y + 15, x + 0.925 * w_, y + 15],
           fill=(250, 248, 242), width=2)
    bx, by = x + 0.52 * w_, y + 27
    d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(178, 34, 40))
    d.arc([bx - 6, by - 6, bx + 6, by + 6], start=80, end=280,
          fill=WHITE, width=1)


def band_f1(d, x, y, w_, h):
    """Las Vegas: night, a kerbed track curve, an F1 silhouette."""
    d.rectangle([x, y, x + w_, y + h], fill=(26, 34, 58))
    for (lu, lv, lr) in [(0.08, 0.14, 2.5), (0.20, 0.08, 2),
                         (0.66, 0.10, 2.5), (0.80, 0.16, 2),
                         (0.93, 0.08, 2.5), (0.38, 0.12, 2),
                         (0.55, 0.06, 2)]:
        cx, cy = x + lu * w_, y + lv * h
        d.ellipse([cx - lr, cy - lr, cx + lr, cy + lr],
                  fill=(255, 220, 150))
    path = [(x - 0.05 * w_, y + 0.80 * h), (x + 0.30 * w_, y + 0.56 * h),
            (x + 0.62 * w_, y + 0.64 * h), (x + 1.05 * w_, y + 0.40 * h)]
    d.line(path, fill=(178, 60, 48), width=30)
    d.line(path, fill=(97, 101, 109), width=21)
    cx, cy = x + 0.50 * w_, y + 0.60 * h
    body = [(cx - 52, cy + 8), (cx - 50, cy + 1), (cx - 30, cy - 1),
            (cx - 16, cy - 9), (cx + 2, cy - 10), (cx + 14, cy - 3),
            (cx + 34, cy - 4), (cx + 50, cy - 2), (cx + 52, cy + 8)]
    d.polygon(body, fill=(10, 10, 12))
    d.rectangle([cx + 36, cy - 14, cx + 52, cy - 9], fill=(10, 10, 12))
    d.line([cx + 50, cy - 14, cx + 50, cy + 2], fill=(10, 10, 12),
           width=3)
    d.rectangle([cx - 54, cy - 6, cx - 46, cy + 6], fill=(10, 10, 12))
    for wx in (cx - 34, cx + 32):
        d.ellipse([wx - 8, cy + 2, wx + 8, cy + 16], fill=(8, 8, 10),
                  outline=(150, 150, 155), width=1)
    d.rectangle([cx - 12, cy - 13, cx + 2, cy - 8], fill=(178, 34, 40))


def band_btc(d, x, y, w_, h):
    """Markets: a rising curve behind a Bitcoin coin."""
    d.rectangle([x, y, x + w_, y + h], fill=(22, 30, 46))
    pts = [(0.06, 0.80), (0.30, 0.64), (0.50, 0.70), (0.74, 0.38),
           (0.94, 0.24)]
    d.line([(x + u * w_, y + v * h) for u, v in pts],
           fill=(64, 196, 110), width=4)
    tip = (x + 0.94 * w_, y + 0.24 * h)
    d.polygon([tip, (tip[0] - 12, tip[1] + 1), (tip[0] - 3, tip[1] + 11)],
              fill=(64, 196, 110))
    cx, cy, r = x + 0.19 * w_, y + 0.48 * h, 19
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26))
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
              outline=(255, 196, 92), width=2)
    fb = serif_b(25)
    d.text((cx, cy - 1), "B", font=fb, fill=WHITE, anchor="mm")
    for bx in (cx - 5, cx + 2):
        d.line([bx, cy - 13, bx, cy - 8], fill=WHITE, width=2)
        d.line([bx, cy + 8, bx, cy + 13], fill=WHITE, width=2)


def band_nuclear(d, x, y, w_, h):
    """Washington/Iran: a document with a NUCLEAR stamp, and an atom."""
    d.rectangle([x, y, x + w_, y + h], fill=(233, 227, 213))
    dx0, dx1 = x + 0.05 * w_, x + 0.44 * w_
    d.rectangle([dx0, y + 7, dx1, y + 53], fill=(252, 250, 244),
                outline=MID, width=2)
    for i, lw in enumerate([0.82, 0.68, 0.76]):
        ly = y + 15 + i * 7
        d.line([dx0 + 7, ly, dx0 + 7 + (dx1 - dx0 - 14) * lw, ly],
               fill=(168, 160, 148), width=3)
    sx0, sy0, sx1, sy1 = dx0 + 10, y + 33, dx1 - 8, y + 48
    d.rectangle([sx0, sy0, sx1, sy1], outline=OXB, width=3)
    fs = dsans_b(13)
    _register("card10 stamp", d.textlength("NUCLEAR", font=fs),
              sx1 - sx0 - 8)
    d.text(((sx0 + sx1) / 2, (sy0 + sy1) / 2), "NUCLEAR", font=fs,
           fill=OXB, anchor="mm")
    cx, cy = x + 0.72 * w_, y + 0.50 * h
    for ang in (0, 60, 120):
        pts = []
        for t in range(41):
            th = 2 * math.pi * t / 40
            ex, ey = 27 * math.cos(th), 10.5 * math.sin(th)
            ca, sa = (math.cos(math.radians(ang)),
                      math.sin(math.radians(ang)))
            pts.append((cx + ex * ca - ey * sa, cy + ex * sa + ey * ca))
        d.line(pts, fill=SLATE, width=2)
    d.ellipse([cx - 4.5, cy - 4.5, cx + 4.5, cy + 4.5], fill=OXB)


def band_cyber(d, x, y, w_, h):
    """Washington/Cyber: a cracked shield, a database, an alert."""
    d.rectangle([x, y, x + w_, y + h], fill=(40, 54, 62))
    cx, cy = x + 0.24 * w_, y + 0.50 * h
    shield = [(cx, cy - 24), (cx + 19, cy - 17), (cx + 18, cy + 2),
              (cx, cy + 25), (cx - 18, cy + 2), (cx - 19, cy - 17)]
    d.polygon(shield, outline=(170, 205, 225), width=3)
    crack = [(cx + 2, cy - 22), (cx - 3, cy - 10), (cx + 4, cy - 1),
             (cx - 2, cy + 10), (cx + 3, cy + 21)]
    d.line(crack, fill=(255, 120, 80), width=3)
    bx0, bx1 = x + 0.56 * w_, x + 0.76 * w_
    d.rectangle([bx0, y + 16, bx1, y + 46], fill=(86, 110, 122))
    d.ellipse([bx0, y + 9, bx1, y + 23], fill=(150, 180, 195))
    d.ellipse([bx0, y + 24, bx1, y + 38], outline=(150, 180, 195),
              width=2)
    d.ellipse([bx0, y + 38, bx1, y + 52], outline=(150, 180, 195),
              width=2)
    tx, ty = x + 0.90 * w_, y + 0.46 * h
    d.polygon([(tx, ty - 15), (tx + 14, ty + 11), (tx - 14, ty + 11)],
              fill=(255, 176, 66))
    fe = dsans_b(16)
    d.text((tx, ty + 1), "!", font=fe, fill=INK, anchor="mm")


def band_kyiv(d, x, y, w_, h):
    """Kyiv: blue over yellow, a giant quote mark, Ukraine's outline."""
    d.rectangle([x, y, x + w_, y + h / 2], fill=(74, 116, 184))
    d.rectangle([x, y + h / 2, x + w_, y + h], fill=(242, 205, 74))
    fq = serif_b(72)
    d.text((x + 0.05 * w_, y + 0.46 * h), "“", font=fq, fill=WHITE,
           anchor="lm")
    ua = [(0.08, 0.36), (0.17, 0.20), (0.31, 0.15), (0.44, 0.19),
          (0.53, 0.09), (0.66, 0.13), (0.78, 0.07), (0.92, 0.15),
          (0.97, 0.29), (0.88, 0.39), (0.93, 0.52), (0.80, 0.60),
          (0.66, 0.55), (0.55, 0.67), (0.42, 0.60), (0.30, 0.69),
          (0.18, 0.58), (0.05, 0.49)]
    ox, oy, ow, oh = x + 0.52 * w_, y + 0.16 * h, 0.42 * w_, 0.68 * h
    d.polygon([(ox + u * ow, oy + v * oh) for u, v in ua],
              fill=(250, 248, 242), outline=INK, width=2)
    cr = [(0.56, 0.80), (0.68, 0.75), (0.71, 0.86), (0.60, 0.92)]
    d.polygon([(ox + u * ow, oy + v * oh) for u, v in cr],
              fill=(250, 248, 242), outline=INK, width=2)


def band_flags(d, x, y, w_, h):
    """Oyo: the Kenya and DRC flags, and a handshake between them."""
    d.rectangle([x, y, x + w_, y + h], fill=(238, 231, 214))
    fx0, fy0, fx1, fy1 = x + 0.06 * w_, y + 9, x + 0.34 * w_, y + 33
    d.line([fx0, y + 6, fx0, y + 54], fill=INK, width=3)
    third = (fy1 - fy0) / 3
    d.rectangle([fx0, fy0, fx1, fy0 + third], fill=(20, 20, 20))
    d.rectangle([fx0, fy0 + third, fx1, fy0 + 2 * third],
                fill=(178, 34, 40))
    d.rectangle([fx0, fy0 + 2 * third, fx1, fy1], fill=(34, 110, 64))
    d.ellipse([fx0 + (fx1 - fx0) * 0.40, fy0 + 3,
               fx0 + (fx1 - fx0) * 0.60, fy1 - 3], fill=(178, 34, 40),
              outline=WHITE, width=1)
    gx0, gy0, gx1, gy1 = x + 0.66 * w_, y + 9, x + 0.94 * w_, y + 33
    d.line([gx1, y + 6, gx1, y + 54], fill=INK, width=3)
    d.rectangle([gx0, gy0, gx1, gy1], fill=(95, 165, 220))
    d.polygon([(gx0, gy1 - 5), (gx1, gy0 + 5), (gx1, gy0 + 12),
               (gx0, gy1 - 12)], fill=(206, 44, 52))
    starburst(d, gx0 + 11, gy0 + 9, 6, (247, 214, 60), spikes=5,
              inner=0.5)
    cy = y + 45
    d.rectangle([x + 0.395 * w_, cy - 6, x + 0.465 * w_, cy + 7],
                fill=INK)
    d.rectangle([x + 0.535 * w_, cy - 6, x + 0.605 * w_, cy + 7],
                fill=SLATE)
    d.polygon([(x + 0.465 * w_, cy - 5), (x + 0.545 * w_, cy - 5),
               (x + 0.565 * w_, cy + 3), (x + 0.520 * w_, cy + 9),
               (x + 0.470 * w_, cy + 4)], fill=(198, 140, 96))
    d.polygon([(x + 0.535 * w_, cy - 5), (x + 0.470 * w_, cy + 1),
               (x + 0.455 * w_, cy + 8), (x + 0.500 * w_, cy + 10),
               (x + 0.545 * w_, cy + 2)], fill=(128, 84, 54))


CARD_BANDS = {"flame": band_factory, "paper": band_exam,
              "chart": band_margin, "cricket": band_cricket,
              "car": band_f1, "coin": band_btc, "dome": band_nuclear,
              "shield": band_cyber, "quote": band_kyiv,
              "hands": band_flags}


def draw_card_band(d, x, y, w_, h, card):
    CARD_BANDS[card["art"]](d, x, y, w_, h)
    d.rectangle([x, y, x + w_, y + h - 1], outline=INK, width=1)


# ---------------------------------------------------------------- the map
# v7: the landmasses are true coastline polygons — (lon, lat) vertices
# projected with the same linear map as the pins — replacing the v4–v6
# ellipse-mask dots that read as pale blobs. Eurasia is one loop (its
# interior borders are not coasts); the Black Sea, the Caspian and
# the Persian Gulf are carved back out as sea bites.
COAST = [
    # North America, Pacific side down to Panama, Atlantic side back
    [(-168, 66), (-164, 60), (-158, 56), (-152, 58), (-146, 60),
     (-140, 60), (-136, 56), (-131, 53), (-127, 50), (-124, 45),
     (-124, 39), (-121, 34), (-116, 32), (-112, 29), (-109, 25),
     (-105, 21), (-101, 18), (-96, 15.5), (-92, 14.5), (-87, 13),
     (-83, 9), (-79, 9), (-82, 9.5), (-83, 15), (-87, 16),
     (-88, 21.5), (-90.5, 21.5), (-91, 19), (-94, 18.5), (-96, 19),
     (-97, 24), (-97, 27), (-93, 30), (-89, 30), (-85, 29.5),
     (-82, 28), (-81, 25), (-80, 27), (-79, 31), (-76, 35),
     (-74, 39), (-71, 41), (-69, 44), (-65, 44), (-60, 46),
     (-63, 49), (-60, 52), (-64, 58), (-68, 58), (-77, 62),
     (-81, 64), (-82, 66), (-85, 68), (-90, 66), (-93, 69),
     (-105, 68), (-120, 69), (-135, 70), (-150, 70), (-158, 71),
     (-164, 69)],
    # South America
    [(-77, 7), (-75, 10), (-72, 12), (-68, 11), (-64, 10.5),
     (-60, 8.5), (-55, 6), (-51, 4), (-50, 1), (-46, -1),
     (-42, -2.5), (-38, -5), (-35, -7.5), (-37, -11), (-39, -14),
     (-39, -17), (-40, -21), (-42, -23), (-46, -25), (-49, -28),
     (-52, -33), (-54, -35), (-57, -39), (-58, -40), (-62, -41),
     (-62, -44), (-65, -45), (-65, -47), (-67, -50), (-67, -52),
     (-66, -55), (-69, -54), (-71, -52), (-72, -49), (-73, -46),
     (-74, -42), (-73, -37), (-72, -32), (-70, -27), (-70, -22),
     (-70, -18.5), (-72, -17), (-75, -15), (-76, -13), (-78, -8),
     (-80, -5), (-81, -1), (-80, 2), (-79, 5)],
    # Africa, Atlantic side down, round the Cape, up the east coast
    [(-6, 35), (-9.5, 31), (-9.5, 28), (-13, 27.5), (-16, 24),
     (-17, 20), (-17, 16), (-16, 12), (-13.5, 9), (-12, 8),
     (-7.5, 4.5), (-3, 5), (2, 6), (6, 4.5), (8.5, 4), (9, -1),
     (11, -4), (12.5, -7), (13, -11), (12, -15), (12.5, -18),
     (14, -21), (15, -25), (16.5, -29), (18, -32), (19.5, -34.5),
     (20, -35), (26, -34), (30, -31), (32, -28.5), (35, -25),
     (35.5, -22), (36, -19), (37, -16), (39, -13), (40, -10),
     (40.5, -6), (42, -2), (46, 0), (51, 5), (51, 10.5),
     (48, 11.5), (44, 11), (42, 13), (40, 15), (38.5, 18),
     (37, 21), (35.5, 23.5), (34, 26), (33, 28), (32.5, 31),
     (30, 31.2), (25, 32), (20, 32.2), (15, 32.4), (11, 33.5),
     (10, 34), (10, 37), (5, 36.8), (0, 36), (-2, 35)],
    # Madagascar
    [(44, -16), (46.5, -15), (49, -13.5), (50, -16), (49.5, -19),
     (47.5, -23), (46, -25), (44.5, -24.5), (43.5, -21), (43, -18),
     (44, -16.5)],
    # Eurasia, one loop: Arctic coast east, Pacific down, the south
    # coasts west, round Arabia, up the Levant, west along the Med
    [(-9, 37), (-9, 43), (-5, 48), (-1.5, 49.5), (1, 51), (3.5, 53),
     (6, 53.5), (8, 55), (8, 57), (5.5, 58), (5, 60), (6, 62),
     (11, 64), (14, 67), (18, 69), (23, 70), (29, 71), (33, 69),
     (40, 66.5), (45, 68), (52, 68.5), (60, 69.5), (68, 70),
     (75, 72), (82, 73), (90, 75), (97, 76), (105, 77), (110, 75),
     (118, 73), (125, 72), (132, 72), (140, 72), (148, 71),
     (155, 70), (162, 70), (170, 67), (178, 65), (178, 63),
     (173, 62), (169, 60), (162, 59), (158, 53), (156, 50),
     (152, 56), (148, 59), (143, 55), (142, 50), (141, 45),
     (140, 40), (139, 35), (135, 34.5), (130, 33), (126, 36),
     (122, 37.5), (120, 34), (120, 30), (121, 26), (116, 23),
     (110, 20), (108, 16), (107, 12), (106, 8.5), (103.5, 6),
     (101, 6.5), (99, 9), (98, 13), (96, 15.5), (94, 16.5),
     (91.5, 22), (89, 21.5), (86.5, 20), (84, 18.5), (81, 15.5),
     (80, 13.5), (77.5, 8), (75.5, 11.5), (73, 16), (72, 19.5),
     (69, 22), (66.5, 25), (61, 25), (57.5, 26.5), (48.5, 29.8),
     (50.5, 26.3), (52, 24.3), (55.5, 24.3), (59.5, 22.3),
     (57.8, 19), (55, 17), (52.5, 15), (48, 14), (45, 12.3),
     (43, 11.8), (42, 14), (40, 17.5), (38.5, 21), (36.5, 25),
     (35, 28.5), (36, 31), (35.8, 33.3), (36.2, 36.3),
     (33.5, 36.2), (30, 36.3), (27.2, 36.8), (26.8, 38.3),
     (23.5, 36.7), (22.8, 39), (20, 39.8), (19.3, 41.8),
     (18.2, 40.2), (16.2, 38.4), (15.7, 38), (16.3, 39.4),
     (15, 40.8), (13, 42.5), (11, 44.2), (8.5, 44.2), (7.4, 43.6),
     (4, 43.2), (3, 42.3), (2.2, 41.3), (1, 39.5), (0, 38.8),
     (-0.7, 37.9), (-2.2, 36.7), (-5.4, 35.9)],
    # Britain, Ireland, Iceland
    [(-5.2, 50), (-3.5, 53.3), (-5, 55), (-5.7, 58.3), (-3, 58.5),
     (-1.5, 57.5), (-0.5, 54.5), (1.3, 51.5), (0, 50.8)],
    [(-10.2, 51.8), (-8, 51.5), (-6, 52.2), (-5.6, 54.3),
     (-7, 55.2), (-9.8, 54.1), (-10.3, 53)],
    [(-22.5, 64), (-21, 63.5), (-15, 63.5), (-13.5, 64.5),
     (-14.5, 66.3), (-20, 66.5), (-22.8, 65.5)],
    # Japan
    [(130, 31), (131.5, 32.5), (133, 33.8), (135.5, 34.3),
     (137, 34.8), (138.5, 35.5), (140, 35.8), (140.5, 38),
     (141.5, 40), (141.8, 43), (143.5, 43.5), (142, 44.8),
     (140.5, 44.5), (139.8, 41), (139, 37.5), (136.5, 35.3),
     (133.5, 34), (131, 32.8)],
    # Indonesia and New Guinea
    [(95.3, 5.5), (97.5, 5.2), (100, 2), (102.5, 0), (104.5, -2.5),
     (105.8, -5.8), (104, -5.5), (101.5, -3.5), (99, -0.5),
     (96.8, 3.5)],
    [(105.5, -6.8), (108, -6.7), (111, -6.9), (114.3, -7.6),
     (114.5, -8.6), (111, -8), (107.5, -7.8), (105.3, -7)],
    [(109, 1), (109.5, 2.5), (111.5, 3.2), (114, 4.2), (116.5, 6.5),
     (118, 3), (119, 0.5), (117.5, -1.5), (116, -3.2), (113, -3.4),
     (110, -2.5), (108.8, -0.5)],
    [(119, -0.5), (120.5, -0.8), (120, -2.5), (119.3, -3.5),
     (118.8, -1.5)],
    [(130.8, -1), (133, -1.8), (136, -2.3), (138.5, -1.9),
     (141, -2.8), (143, -3.5), (146, -5.5), (148.5, -8),
     (150.5, -10), (147.5, -9.5), (144, -8), (140, -7.5),
     (136, -6), (132.5, -3.8), (131, -2.5)],
    # the Philippines, Cuba
    [(120, 18.3), (121, 18), (121.8, 16), (122.2, 14), (121.5, 13.5),
     (122, 11.5), (122.5, 10), (121, 11), (120.5, 13.5),
     (119.9, 16)],
    [(-84.8, 22.5), (-81, 23), (-77, 21.5), (-74.2, 20.2),
     (-74.5, 20), (-78, 21), (-81.5, 22.3), (-84.5, 21.9)],
    # Australia
    [(113.5, -22), (114, -28), (115, -33.5), (118, -35), (124, -33),
     (129, -31.8), (132, -32), (135, -34.8), (137, -35), (139, -37),
     (140, -38.5), (145, -38.3), (147, -38), (150, -37), (153, -30.8),
     (153, -27), (151, -24), (149, -20), (146, -19), (143.5, -15),
     (142, -11), (142, -14.5), (141, -17.5), (140, -17.8),
     (136.5, -15), (135, -12), (132, -11), (130, -12.5), (126, -14),
     (122, -17), (118, -20), (114.8, -21.5)],
    # New Zealand, both islands
    [(172.7, -34.5), (175, -36.5), (178, -37.5), (176.8, -39.5),
     (174.8, -41.3), (173.8, -39.2), (172.7, -37)],
    [(166.5, -46), (168, -46.3), (170.5, -45.5), (171.5, -43.5),
     (173.5, -42), (172, -41.5), (169, -43.8), (167.5, -45.8)],
]

SEA_BITES = [
    # the Black Sea
    [(28, 41.3), (32, 41.2), (36, 41), (39.5, 41.3), (41.5, 43),
     (40, 45.8), (36, 46.8), (32, 46.4), (28.5, 44.8), (27.8, 43)],
    # the Caspian Sea
    [(49.8, 37), (52, 37.8), (53.8, 39.5), (54, 42), (53.5, 44.8),
     (51.5, 46.8), (50, 45), (48.8, 41.5), (49, 38.5)],
    # the Persian Gulf
    [(48.5, 29.8), (51, 28.8), (53.5, 27.5), (56.5, 26.8),
     (56.8, 26.2), (53, 25.3), (50.3, 25.8), (48.7, 27.8)],
]

MAP_LAND = (226, 206, 164)
MAP_COAST = (168, 148, 106)
MAP_LABELS = [("AMERICAS", -110, 48), ("EUROPE", 8, 63),
              ("ASIA", 100, 52), ("AFRICA", 21, -10),
              ("MIDDLE EAST", 50, 7.5), ("OCEANIA", 134, -27)]


def draw_map(d, x, y, w_, h):
    """World map: drawn coastline polygons in a deeper land tone on
    the ocean panel, region labels on the landmasses, and the pins
    at their true lon/lat anchors — where pins would overlap, the
    circles are relaxed apart and tied back to their anchors with
    thin leader lines, so every number reads at entry scale."""
    d.rectangle([x, y, x + w_, y + h], fill=OCEAN)

    def P(lon, lat):
        return (x + (lon + 172) / 356 * w_, y + (76 - lat) / 124 * h)

    for poly in COAST:
        pts = [P(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND)
        d.line(pts + [pts[0]], fill=MAP_COAST, width=2)
    for poly in SEA_BITES:
        d.polygon([P(lon, lat) for lon, lat in poly], fill=OCEAN)
    d.rectangle([x, y, x + w_, y + h], outline=INK, width=2)
    lf = dsans_b(16)
    for name, lon, lat in MAP_LABELS:
        cx, cy = P(lon, lat)
        tw = tracked_width(d, name, lf, 2)
        _register(f"map label {name}", tw, w_)
        draw_tracked(d, cx - tw / 2, cy - 8, name, lf, 2, (94, 86, 64))
    # pins: relax overlapping circles apart (deterministic order),
    # never more than 44px from the anchor, never off the panel
    anchors = {num: P(lon, lat) for num, (lon, lat) in PINS.items()}
    pos = dict(anchors)
    nums = sorted(PINS)
    R = 13
    for _ in range(90):
        moved = False
        for i, a in enumerate(nums):
            for b in nums[i + 1:]:
                ax_, ay_ = pos[a]
                bx_, by_ = pos[b]
                dx, dy = bx_ - ax_, by_ - ay_
                dist = math.hypot(dx, dy)
                if dist < 2 * R + 2:
                    if dist < 0.01:
                        dx, dy, dist = 1.0, 0.3, math.hypot(1.0, 0.3)
                    push = (2 * R + 2 - dist) / 2
                    ux, uy = dx / dist, dy / dist
                    pos[a] = (ax_ - ux * push, ay_ - uy * push)
                    pos[b] = (bx_ + ux * push, by_ + uy * push)
                    moved = True
        for n in nums:
            ax_, ay_ = anchors[n]
            px_, py_ = pos[n]
            dx, dy = px_ - ax_, py_ - ay_
            dd = math.hypot(dx, dy)
            if dd > 44:
                px_, py_ = ax_ + dx / dd * 44, ay_ + dy / dd * 44
            pos[n] = (min(max(px_, x + R + 1), x + w_ - R - 1),
                      min(max(py_, y + R + 1), y + h - R - 1))
        if not moved:
            break
    pf = dsans_b(14)
    for n in nums:
        ax_, ay_ = anchors[n]
        px_, py_ = pos[n]
        if math.hypot(px_ - ax_, py_ - ay_) > 4:
            d.line([ax_, ay_, px_, py_], fill=(96, 86, 72), width=2)
            d.ellipse([ax_ - 3, ay_ - 3, ax_ + 3, ay_ + 3],
                      fill=REGION_COLORS[PIN_REGION[n]], outline=PAPER,
                      width=1)
    for n in nums:
        px_, py_ = pos[n]
        d.ellipse([px_ - R, py_ - R, px_ + R, py_ + R],
                  fill=REGION_COLORS[PIN_REGION[n]], outline=PAPER,
                  width=2)
        d.text((px_, py_), str(n), font=pf, fill=WHITE, anchor="mm")


def brief_width(d, num, place, txt, src, src_size):
    fb, fr = lsans_b(22), lsans(22)
    fs = lsans(src_size)
    return (34 + d.textlength(place, font=fb)
            + d.textlength(" — " + txt, font=fr)
            + d.textlength(f" ({src})", font=fs))


def draw_brief(d, x, y, num, place, txt, src, src_size):
    fb, fr = lsans_b(22), lsans(22)
    fs = lsans(src_size)
    col = REGION_COLORS[PIN_REGION[num]]
    d.ellipse([x, y - 1, x + 25, y + 24], fill=col)
    d.text((x + 12.5, y + 11), str(num), font=dsans_b(13), fill=WHITE,
           anchor="mm")
    cx = x + 34
    d.text((cx, y), place, font=fb, fill=INK)
    cx += d.textlength(place, font=fb)
    body = " — " + txt
    d.text((cx, y), body, font=fr, fill=INK)
    cx += d.textlength(body, font=fr)
    d.text((cx, y), f" ({src})", font=fs, fill=MID)


# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 96
    right = W - M
    CW = right - M

    def divider(y):
        d.line([M, y, right, y], fill=HAIR, width=2)

    # top microtext row
    lf = fit_tracked(d, "microtext left", "THE WORLD IN ONE DAY", dsans_b,
                     24, 18, 4, CW * 0.42)
    draw_tracked(d, M, 22, "THE WORLD IN ONE DAY", lf, 4, INK)
    tag = ("37 STORIES · 7 REGIONS · EVERY ONE DATED "
           "SUNDAY 22 NOVEMBER 2026")
    tf = fit_tracked(d, "microtext right", tag, dsans_b, 23, 17, 2,
                     CW * 0.60)
    tw = tracked_width(d, tag, tf, 2)
    draw_tracked(d, right - tw, 23, tag, tf, 2, MID)

    # the masthead as one composed unit: the date at 104px (v4 set it
    # at 168, a fifth of the page) with a small edition block filling
    # the measure to its right, then the standfirst under both
    date = "22 November 2026"
    df = fit_oneline(d, "date display", date, serif_b, 104, 92, CW * 0.62)
    d.text((M, 48), date, font=df, fill=INK)
    eb1 = "Sunday edition"
    ef1 = fit_oneline(d, "edition block title", eb1, serif_b, 27, 22,
                      CW * 0.34)
    ew1 = d.textlength(eb1, font=ef1)
    d.text((right - ew1, 60), eb1, font=ef1, fill=INK)
    eb2 = "All 37 stories dated 22 November 2026"
    ef2 = fit_oneline(d, "edition block line", eb2, lsans, 16, 14,
                      CW * 0.34)
    ew2 = d.textlength(eb2, font=ef2)
    d.text((right - ew2, 98), eb2, font=ef2, fill=MID)

    # standfirst: v7 — three OTHER stories' headlines, verbatim from
    # the frozen cards, italic, diamond-separated (the lead headlines
    # already run as the lead headlines and in the stat strip)
    stand = ("Fifty missing in the factory ruins ◆ Bitcoin bounces "
             "above $60,000 ◆ “Big bosses can't decide fate”")
    sf = fit_oneline(d, "standfirst", stand, serif_i, 30, 24, CW)
    d.text((M + 2, 152), stand, font=sf, fill=MID)
    DIV1 = 186
    divider(DIV1)

    # stat strip: ink serif figures on a shared baseline, captions in
    # their own columns, hairline uprights between the columns
    col_w = CW / 6
    base_y = DIV1 + 72
    for i, (big, cap) in enumerate(STATS):
        cx = M + i * col_w
        if i:
            d.line([cx, DIV1 + 16, cx, DIV1 + 100], fill=HAIR, width=2)
        bf = fit_oneline(d, f"stat {big}", big, serif_b, 100, 40,
                         col_w - 20)
        d.text((cx + 10, base_y), big, font=bf, fill=INK, anchor="ls")
        cf, clines, clead = fit_box(d, f"stat caption {big}", cap, lsans,
                                    19, 16, col_w - 20, 42, 1.18)
        text_block(d, cx + 10, base_y + 14, clines, cf, clead, fill=MID)

    # region tally, high on the page as in the winning entries: an ink
    # label block, then one coloured segmented bar with the region
    # names and counts set inside their segments, in white
    RY = DIV1 + 136
    lab_w = 168
    lf2 = fit_tracked(d, "region label", "BY REGION", dsans_b, 16, 13, 2,
                      lab_w - 16)
    d.rectangle([M, RY, M + lab_w, RY + 30], fill=INK)
    draw_tracked(d, M + (lab_w - tracked_width(d, "BY REGION", lf2, 2)) / 2,
                 RY + 7, "BY REGION", lf2, 2, WHITE)
    total = sum(n for _, n in REGION_TALLY)
    tally_names = {"EUROPE": "Europe", "ASIA": "Asia", "AFRICA": "Africa",
                   "AMERICAS": "Americas", "MIDDLE EAST": "Middle East",
                   "GLOBAL": "Global", "OCEANIA": "Oceania"}
    cx = M + lab_w
    bar_w = CW - lab_w
    for name, n in REGION_TALLY:
        wseg = bar_w * n / total
        col = REGION_COLORS[tally_names[name]]
        d.rectangle([cx, RY, cx + wseg, RY + 30], fill=col)
        label = f"{name} {n}"
        lf3 = fit_tracked(d, f"tally {name}", label, dsans_b, 14, 10, 1,
                          wseg - 8)
        tw3 = tracked_width(d, label, lf3, 1)
        draw_tracked(d, cx + (wseg - tw3) / 2, RY + 8, label, lf3, 1,
                     WHITE)
        cx += wseg
    DIV2 = RY + 36
    divider(DIV2)

    # leads: a coloured header band (number + kicker + tier pill), the
    # illustrated panel, serif headline, drop-cap body, source + pill
    y0 = DIV2 + 8
    lead_w = 597
    lead_gap = 32
    ART_H = 272
    for i, lead in enumerate(LEADS):
        x = M + i * (lead_w + lead_gap)
        region = LEAD_REGION[lead["num"]]
        col = REGION_COLORS[region]
        d.rectangle([x, y0, x + lead_w, y0 + 30], fill=col)
        nf = serif_b(23)
        num_s = f"{lead['num']:02d}"
        _register(f"lead{lead['num']} band num",
                  d.textlength(num_s, font=nf), 60)
        d.text((x + 12, y0 + 3), num_s, font=nf, fill=WHITE)
        pw = pill_width(d, lead["tier"], 13)
        kf = fit_tracked(d, f"lead{lead['num']} kicker", lead["kicker"],
                         dsans_b, 17, 13, 3, lead_w - 70 - pw - 24)
        draw_tracked(d, x + 62, y0 + 7, lead["kicker"], kf, 3, WHITE)
        pill(d, x + lead_w - pw - 8, y0 + 3, lead["tier"], 13, light=True)
        ay = y0 + 36
        ART[lead["art"]](d, x, ay, lead_w, ART_H)
        d.rectangle([x, ay, x + lead_w, ay + ART_H], outline=INK, width=2)
        hf, hlines, hlead = fit_box(d, f"lead{lead['num']} headline",
                                    lead["headline"], serif_b, 46, 30,
                                    lead_w, 66, 1.02)
        text_block(d, x, ay + ART_H + 10, hlines, hf, hlead)
        lead_body(d, x, ay + ART_H + 84, lead, lead_w, 112)
        sy = ay + ART_H + 196
        pw2 = pill_width(d, lead["tier"], 13)
        sf2 = fit_oneline(d, f"lead{lead['num']} source", lead["source"],
                          lsans, 18, 14, lead_w - pw2 - 16)
        d.text((x, sy + 2), lead["source"], font=sf2, fill=MID)
        pill(d, x + lead_w - pw2, sy, lead["tier"], 13)
    DIV3 = y0 + 530
    divider(DIV3)

    # mid cards, two rows of five: numeral + place + a colour rule,
    # a full-colour scene band (v6) with the story's big figure,
    # headline, body, source + tier pill
    y0 = DIV3 + 8
    card_w = 345
    card_gap = 32
    row_h = 233
    for idx, card in enumerate(CARDS):
        row, col_i = divmod(idx, 5)
        x = M + col_i * (card_w + card_gap)
        y = y0 + row * (row_h + 4)
        region = card["region"]
        col = REGION_COLORS[region]
        num = f"{card['num']:02d}"
        nf = serif_b(27)
        num_w = d.textlength(num, font=nf)
        d.text((x, y), num, font=nf, fill=INK)
        kf = fit_tracked(d, f"card{card['num']} kicker", card["place"],
                         dsans_b, 15, 12, 2.5, card_w - num_w - 9)
        draw_tracked(d, x + num_w + 9, y + 6, card["place"], kf, 2.5, MID)
        d.rectangle([x, y + 31, x + card_w, y + 35], fill=col)
        # v6: a full-colour scene band across the top of the card;
        # a stat card's figure keeps its place at the band's right,
        # in a paper block with a region-colour edge
        band_y = y + 38
        block_w = 0
        if card["num"] in CARD_STAT:
            big0 = CARD_STAT[card["num"]][0]
            sz = 48
            while sz > 28 and d.textlength(big0,
                                           font=serif_b(sz)) > card_w - 60:
                sz -= 1
            block_w = d.textlength(big0, font=serif_b(sz)) + 22
            if card["num"] in (4, 7, 9):
                # v7: scene first — the figure block shrinks to
                # about three-fifths, the scene takes at least 65%
                # of the band; the stat strip keeps the big figure
                block_w = min(int(block_w * 0.6), card_w - 225)
        draw_card_band(d, x, band_y, card_w - block_w, 60, card)
        if block_w:
            d.rectangle([x + card_w - block_w, band_y, x + card_w,
                         band_y + 59], fill=PAPER)
            d.rectangle([x + card_w - block_w, band_y,
                         x + card_w - block_w + 3, band_y + 59],
                        fill=col)
            big, capword = CARD_STAT[card["num"]]
            if card["num"] in (4, 7, 9):
                bf = fit_oneline(d, f"card{card['num']} stat", big,
                                 serif_b, 48, 16, block_w - 22)
            else:
                bf = fit_oneline(d, f"card{card['num']} stat", big,
                                 serif_b, 48, 28, card_w - 60)
            bw2 = d.textlength(big, font=bf)
            d.text((x + card_w - bw2, y + 38), big, font=bf, fill=col)
            cf2 = fit_tracked(d, f"card{card['num']} stat caption",
                              capword, dsans_b, 13, 10, 2, card_w - 60)
            cw2 = tracked_width(d, capword, cf2, 2)
            draw_tracked(d, x + card_w - cw2, y + 86, capword, cf2, 2,
                         MID)
        hf, hlines, hlead = fit_box(d, f"card{card['num']} headline",
                                    card["headline"], lsans_b, 27, 19,
                                    card_w, 42, 1.04)
        text_block(d, x, y + 98, hlines, hf, hlead)
        bf2, blines, blead = fit_box(d, f"card{card['num']} body",
                                     card["body"], lsans, 20, 15, card_w,
                                     60, 1.25)
        text_block(d, x, y + 144, blines, bf2, blead, fill=INK)
        sy = y + 208
        pw = pill_width(d, card["tier"], 12)
        sf3 = fit_oneline(d, f"card{card['num']} source", card["source"],
                          lsans, 17, 13, card_w - pw - 14)
        d.text((x, sy + 3), card["source"], font=sf3, fill=MID)
        pill(d, x + card_w - pw, sy, card["tier"], 12)
    DIV4 = y0 + 476
    divider(DIV4)

    # map + briefs band. The briefs are LOCKED at Liberation Sans 22
    # with 30px leading (11px / 15px at entry scale): items 14-25 run
    # in one column beside the map, items 26-37 continue below it.
    hy = DIV4 + 6
    hf1 = fit_tracked(d, "map heading", "WHERE IT HAPPENED", dsans_b, 19,
                      15, 3, 850)
    draw_tracked(d, M, hy, "WHERE IT HAPPENED", hf1, 3, INK)
    ba_x = M + 850 + 32
    ba_w = right - ba_x
    ah = "ALSO ON SUNDAY — 24 MORE STORIES"
    hf2 = fit_tracked(d, "also heading", ah, dsans_b, 19, 15, 3, ba_w)
    draw_tracked(d, ba_x, hy, ah, hf2, 3, INK)
    ry = hy + 22
    draw_map(d, M, ry, 850, 280)
    cap = "Each number is the story with that number on this page."
    cf = fit_oneline(d, "map caption", cap, lsans, 16, 13, 848)
    d.text((M + 2, ry + 286), cap, font=cf, fill=MID)
    # tier legend under the map: pill + its meaning, from STORIES.md
    ly = ry + 308
    lx = M + 2
    for tier, gloss in [("CONFIRMED", "independently reported"),
                        ("OFFICIAL", "authority's own statement"),
                        ("REPORTED", "attributed claim")]:
        w_ = pill(d, lx, ly, tier, 12)
        gf = lsans(16)
        gw = d.textlength(gloss, font=gf)
        _register(f"legend {tier}", lx + w_ + 8 + gw, M + 850)
        d.text((lx + w_ + 8, ly + 3), gloss, font=gf, fill=MID)
        lx += w_ + 8 + gw + 22

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
        draw_brief(d, ba_x, ry + j * 26, n, p, t, s, src_size)
    ry2 = ry + 344
    for j, (n, (p, t, s)) in enumerate(b2):
        draw_brief(d, M, ry2 + j * 26, n, p, t, s, src_size)
    for j, (n, (p, t, s)) in enumerate(b3):
        draw_brief(d, M + 880 + 30, ry2 + j * 26, n, p, t, s, src_size)
    DIV5 = ry2 + 166
    divider(DIV5)

    # date check, v6: the exclusions (words unchanged) inside a
    # full-width red-bordered box — the bold red label at the left
    # inside the box, the body set ~30% larger than v5's footer
    # microtext — so the framing cannot be misread as a contradiction
    y0 = DIV5 + 6
    box_h = 88
    d.rectangle([M, y0, right, y0 + box_h], fill=GHOST)
    d.rectangle([M, y0, right, y0 + box_h], outline=OXB, width=3)
    dct = "DATE CHECK — LEFT OUT ON PURPOSE: OLDER NEWS, HOWEVER BIG"
    tf, tlines, tlead = fit_box(d, "date check title", dct, dsans_b, 16,
                                13, 424, 72, 1.2)
    th = (len(tlines) - 1) * tlead + tf.size
    text_block(d, M + 16, y0 + (box_h - th) / 2, tlines, tf, tlead,
               fill=OXB)
    dc = ("The Bayelsa boat sinking — Friday 20 Nov (only Sunday's probe "
          "order is on this page) · The Sparta II ship fire — Saturday "
          "21 Nov · The UK–EU “landmark” deal — Friday 20 Nov "
          "· Brazil's election fallout — 18 Nov · “COP31 close "
          "to a deal” — Saturday's optimism, overtaken by Sunday's collapse")
    df2, dlines, dlead = fit_box(d, "date check body", dc, lsans, 21, 17,
                                 CW - 470, 72, 1.18)
    bh = (len(dlines) - 1) * dlead + df2.size
    text_block(d, M + 470, y0 + (box_h - bh) / 2, dlines, df2, dlead,
               fill=INK)

    # folio line
    fy = y0 + box_h + 8
    d.line([M, fy, right, fy], fill=HAIR, width=2)
    folio = "22.11.26 — 37 STORIES"
    ff = fit_tracked(d, "folio left", folio, dsans_b, 13, 12, 2, 400)
    draw_tracked(d, M, fy + 4, folio, ff, 2, MID)
    foot = ("Every story here happened, or was first reported, on Sunday "
            "22 November 2026. Officials' counts and claims are attributed. "
            "Original drawings.")
    ff2 = fit_oneline(d, "folio right", foot, lsans, 13, 12, CW - 430)
    tw = d.textlength(foot, font=ff2)
    d.text((right - tw, fy + 4), foot, font=ff2, fill=MID)

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
    entry_img = img.resize((1024, 1024), Image.LANCZOS)
    entry_img.save(entry, optimize=True)
    if os.path.getsize(entry) > 1_000_000:
        # keep the shipped file under the size aim: palette-quantize
        entry_img.quantize(colors=256, method=Image.MEDIANCUT,
                           dither=Image.FLOYDSTEINBERG).save(
                               entry, optimize=True)
    print("wrote", master, os.path.getsize(master))
    print("wrote", entry, os.path.getsize(entry))


if __name__ == "__main__":
    render()
