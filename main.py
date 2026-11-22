#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - broadsheet front page for 22 November 2026.

Pure standard-library Python. Renders a 1024x1024 PNG entirely from data
embedded in this file: a hand-defined 5x7 bitmap font, simplified continent
polygons in lon/lat, 35 verified news stories, and vector illustration panels.
Deterministic: no randomness, no clock, no network, no external files.

Output: $MAKEFUN_OUTPUT_DIR/entry.png, or ./output/entry.png when the
variable is not set. Nothing is ever written next to this file.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 241, 222)
PAPER2 = (242, 234, 210)
INK = (18, 18, 18)
INK_SOFT = (58, 54, 46)
RED = (178, 34, 28)
BLUE = (28, 62, 110)
TEAL = (16, 96, 92)
GOLD = (176, 132, 32)
SEA = (168, 196, 208)
LAND = (214, 196, 150)
LAND2 = (202, 184, 138)
GREEN = (46, 110, 58)
ORANGE = (214, 110, 24)
GREY = (120, 116, 104)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits ('1' = ink). Uppercase only, by design:
# the whole page is set in newspaper caps.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "00100", "01000", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}

# ---------------------------------------------------------------- canvas
IMG = bytearray(W * H * 3)


def _idx(x, y):
    return (y * W + x) * 3


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = _idx(x, y)
        IMG[i] = c[0]
        IMG[i + 1] = c[1]
        IMG[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    r, g, b = c
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            IMG[i] = r
            IMG[i + 1] = g
            IMG[i + 2] = b


def hline(x0, x1, y, c, thick=1):
    for t in range(thick):
        fill_rect(min(x0, x1), y + t, abs(x1 - x0) + 1, 1, c)


def vline(x, y0, y1, c, thick=1):
    for t in range(thick):
        fill_rect(x + t, min(y0, y1), 1, abs(y1 - y0) + 1, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        set_px(x, y, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_poly(points, c):
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y0, y1 = max(0, min(ys)), min(H - 1, max(ys))
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x0, yy0 = points[i]
            x1, yy1 = points[(i + 1) % n]
            if (yy0 <= y < yy1) or (yy1 <= y < yy0):
                if yy1 != yy0:
                    xs.append(x0 + (y - yy0) * (x1 - x0) / (yy1 - yy0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            fill_rect(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), 1, c)


def poly_line(points, c):
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]
        line(a[0], a[1], b[0], b[1], c)


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)


def ring(cx, cy, r, c):
    for a in range(360):
        import math
        x = cx + int(r * math.cos(a * 3.14159265 / 180.0))
        y = cy + int(r * math.sin(a * 3.14159265 / 180.0))
        set_px(x, y, c)


# ---------------------------------------------------------------- text
def text_width(s, sx):
    return len(s) * (5 * sx + 2) - 2 if s else 0


def draw_text(s, x, y, sx, sy, c, bold=False, align="left"):
    s = "".join(ch if ch in FONT else " " for ch in s.upper())
    w = text_width(s, sx)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    for ci, ch in enumerate(s):
        g = FONT[ch]
        gx0 = x + ci * (5 * sx + 2)
        for gy in range(7):
            row = g[gy]
            for gx in range(5):
                if row[gx] == "1":
                    bw = sx + (1 if bold else 0)
                    fill_rect(gx0 + gx * sx, y + gy * sy, bw, sy, c)
    return w


def wrap_words(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for wd in words:
        if not cur:
            cur = wd
        elif len(cur) + 1 + len(wd) <= max_chars:
            cur += " " + wd
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def wrap_max(text, max_chars, max_lines):
    lines = wrap_words(text, max_chars)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        # trim the last line so it fits, keep it a whole word when possible
        last = lines[-1]
        if len(last) > max_chars:
            last = last[: max_chars - 1].rstrip()
        lines[-1] = last
    return lines


# ---------------------------------------------------------------- stories
# (region, headline, deck) -- every item verified in the 22 Nov 2026 news
# cycle (Reuters / BBC / AP / CNN / Al Jazeera and wire reports). Headlines
# fit 2 lines of 16 chars; decks fit 2 lines of 32 chars at render size.
STORIES = [
    ("WORLD", "COP31 TALKS RUN PAST DEADLINE",
     "NEARLY 200 NATIONS WEIGH A NEW TEXT AFTER THE FOSSIL-FUEL ROW."),
    ("WORLD", "KILLER-ROBOT TALKS STALL",
     "GENEVA AGREES TO DRAFT A 2028 ACCORD, WITH NO BINDING RULES."),
    ("WORLD", "EU SIGNS INDONESIA PACT",
     "BRUSSELS CONFIRMS TRADE AND INVESTMENT DEALS WITH JAKARTA."),
    ("WORLD", "NIGERIA BOAT CAPSIZE KILLS 24",
     "AGENCY REPORTS 24 BODIES RECOVERED AFTER THE CAPSIZE."),
    ("WORLD", "KENYA FREES LAST EBOLA PATIENT",
     "KENYA FREES ITS LAST PATIENT AS DRC TOLL PASSES 5,300."),
    ("AMERICAS", "CHAPO ISIDRO SEIZED",
     "FBI TOP-10 FUGITIVE TAKEN IN A GUASAVE RAID. ELEVEN KILLED."),
    ("AMERICAS", "QUAKE M6.8 SHAKES PERU",
     "JUNIN TREMOR RATTLES LIMA. NO MAJOR DAMAGE REPORTED SO FAR."),
    ("AMERICAS", "VIRGINIA MEASLES DEATH SINCE 1978",
     "A CHILD AGED 0-4 DIES. THE STATE COUNTS 220 CASES IN 2026."),
    ("AMERICAS", "HEGSETH MEMO HITS CANADA",
     "SECRET MEMO RESTRICTS THE US-CANADA DEFENCE RELATIONSHIP."),
    ("AMERICAS", "HAITI INKS PRISON DEAL",
     "PORT-AU-PRINCE AGREES A PLAN TO BUILD NEW PRISONS."),
    ("EUROPE", "SPARTA II BURNS IN BALTIC SEA",
     "DRONE-HIT CARGO SHIP DRIFTS INTO FINNISH WATERS. CREW IS SAFE."),
    ("EUROPE", "ESTONIA TO SHUT RUSSIA BORDER",
     "FIVE ROAD CROSSINGS CLOSE ON 1 DECEMBER FOR SIX MONTHS."),
    ("EUROPE", "FINLAND PROBES HELICOPTER",
     "RUSSIAN HELICOPTER FLEW 4.1 KM INTO FINNISH AIRSPACE."),
    ("EUROPE", "THOUSANDS MARCH IN LISBON",
     "RAIN-SOAKED PROTEST OVER LIVING COSTS, HOUSING AND LOW WAGES."),
    ("EUROPE", "FRANCE PROTESTS A FOURTH WEEKEND",
     "COST-OF-LIVING MARCHES CONTINUE ACROSS FRANCE."),
    ("MIDDLE EAST & AFRICA", "IRAN HITS US BASES IN BAHRAIN",
     "GUARDS CLAIM PATRIOT RADARS STRUCK. FIRE AT A PLANT."),
    ("MIDDLE EAST & AFRICA", "KUWAIT ON ALERT AFTER DRONE RAID",
     "AIR DEFENCES ENGAGE IRANIAN DRONES AT ALI AL SALEM AIR BASE."),
    ("MIDDLE EAST & AFRICA", "BASRA POWER FIRE KILLS AT LEAST 4",
     "HARTHA PLANT BLAZE INJURES 35. THE PM ORDERS AN INQUIRY."),
    ("MIDDLE EAST & AFRICA", "EISENKOT INVITES LIKUD TO TALKS",
     "MARATHON COALITION TALKS DUE TO START ON SUNDAY IN JERUSALEM."),
    ("MIDDLE EAST & AFRICA", "FOUR NATIONS URGE GAZA AID",
     "AUSTRALIA, CANADA, ITALY AND THE UK CITE FLOODING IN GAZA."),
    ("ASIA-PACIFIC", "NEPAL PM LANDS IN DELHI",
     "BALENDRA SHAH BEGINS FIRST STATE VISIT. MODI TALKS MONDAY."),
    ("ASIA-PACIFIC", "SEOUL OFFERS EXAM REWARD",
     "SOUTH KOREA REPEATS A REWARD FOR REPORTING CHEATING ON EXAMS."),
    ("ASIA-PACIFIC", "MYANMAR GUILTY OF GENOCIDE",
     "UN COURT FINDS MYANMAR COMMITTED GENOCIDE AGAINST THE ROHINGYA."),
    ("ASIA-PACIFIC", "MONGOLIA PRESIDENT QUITS",
     "PARLIAMENT ACCEPTS PRESIDENT KHURELSUKH RESIGNATION."),
    ("ASIA-PACIFIC", "PRABOWO AND XI TALK SEA DISPUTE",
     "INDONESIA AND CHINA REACH AN UNDERSTANDING ON JOINT WORK."),
    ("SPORT", "ALCARAZ FACES ZVEREV IN FINAL",
     "TOP TWO SEEDS MEET FOR THE ATP FINALS TITLE ON SUNDAY."),
    ("SPORT", "ARSENAL HELD 2-2 AT NEWCASTLE",
     "MADUEKE EQUALISER SAVES A POINT FOR THE LEAGUE LEADERS."),
    ("SPORT", "LEEDS THRASH CHELSEA 4-1",
     "OKAFOR SCORES TWICE IN A STUNNING STAMFORD BRIDGE WIN."),
    ("SPORT", "MAN CITY HELD 1-1 BY FULHAM",
     "ANDERSON EQUALISER SPARES CITY A FOURTH STRAIGHT DEFEAT."),
    ("SPORT", "FRANCE REACH RUGBY FINAL",
     "FRANCE BEAT ARGENTINA TO FACE SOUTH AFRICA IN THE FINAL."),
    ("TECH & MARKETS", "BRENT FALLS FOR THIRD WEEK",
     "OIL SETTLES UP ON FRIDAY BUT DOWN 3.41 PERCENT FOR THE WEEK."),
    ("TECH & MARKETS", "US STOCKS TUMBLE ON FRIDAY",
     "S AND P 500 FALLS 3.70 PERCENT. NASDAQ DROPS 5.28 PERCENT."),
    ("TECH & MARKETS", "OPEC+ TO SET 2027 QUOTAS",
     "MINISTERS MEET ON 29 NOVEMBER TO DECIDE OUTPUT LEVELS."),
    ("TECH & MARKETS", "ASIAN STOCKS SLUMP",
     "ASIAN SHARES HEAD FOR WORST WEEK SINCE 2020."),
    ("TECH & MARKETS", "JAPAN INFLATION FUELS RATE BETS",
     "CORE INFLATION BEATS THE 2 PERCENT TARGET AGAIN."),
]

# ---------------------------------------------------------------- map data
# Simplified continent outlines in (lon, lat). Equirectangular projection.
CONTINENTS = [
    [(-168, 66), (-158, 58), (-140, 60), (-130, 54), (-125, 49), (-124, 42),
     (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-92, 15),
     (-86, 12), (-83, 9), (-79, 9), (-80, 13), (-84, 16), (-87, 21),
     (-90, 21), (-91, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
     (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
     (-65, 44), (-60, 47), (-55, 47), (-60, 52), (-65, 50), (-68, 55),
     (-72, 58), (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68),
     (-125, 70), (-140, 70), (-155, 71), (-165, 68)],
    [(-58, 64), (-52, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70),
     (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-60, 70)],
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-73, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-68, -50), (-65, -45), (-62, -40), (-58, -35), (-52, -32),
     (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
     (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
     (-72, 12), (-77, 8)],
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 4), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1), (12, -5),
     (13, -10), (12, -15), (14, -22), (16, -28), (19, -34), (26, -34),
     (32, -29), (35, -24), (40, -16), (40, -10), (42, -4), (46, -1),
     (51, 2), (51, 11), (48, 11), (44, 11), (40, 15), (38, 18), (37, 22),
     (34, 27), (32, 31), (30, 31), (25, 32), (20, 32), (15, 32), (10, 34),
     (10, 37), (5, 37), (0, 36)],
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
     (0, 51), (3, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62),
     (10, 64), (12, 66), (18, 69), (25, 71), (30, 70), (32, 68), (35, 66),
     (40, 64), (44, 62), (48, 60), (50, 59), (48, 57), (44, 55), (40, 55),
     (38, 52), (35, 50), (32, 48), (30, 46), (28, 44), (24, 42), (23, 40),
     (26, 38), (28, 37), (30, 36), (27, 37), (23, 36), (20, 38), (18, 40),
     (15, 38), (12, 38), (12, 42), (10, 44), (8, 44), (3, 43), (0, 40),
     (-2, 37), (-6, 36), (-9, 37)],
    [(30, 36), (32, 40), (35, 42), (38, 44), (40, 46), (42, 48), (45, 50),
     (48, 52), (50, 55), (52, 58), (55, 60), (58, 62), (60, 65), (65, 68),
     (68, 70), (72, 72), (75, 73), (80, 73), (85, 74), (90, 75), (95, 76),
     (100, 77), (105, 77), (110, 76), (115, 73), (120, 73), (125, 72),
     (130, 72), (135, 71), (140, 72), (145, 72), (150, 70), (155, 69),
     (160, 69), (162, 66), (160, 62), (158, 58), (155, 55), (150, 55),
     (145, 52), (142, 50), (140, 45), (138, 40), (135, 35), (132, 33),
     (130, 31), (128, 34), (127, 35), (126, 38), (124, 40), (122, 38),
     (120, 35), (122, 32), (120, 28), (118, 25), (115, 22), (110, 20),
     (108, 18), (106, 10), (104, 9), (103, 7), (101, 6), (100, 8),
     (99, 12), (98, 14), (97, 16), (95, 16), (93, 20), (91, 22), (89, 22),
     (87, 21), (85, 19), (83, 17), (80, 15), (78, 13), (77, 8), (76, 10),
     (74, 13), (72, 20), (70, 22), (68, 23), (66, 25), (64, 25), (62, 25),
     (60, 25), (58, 26), (56, 26), (54, 27), (52, 27), (50, 29), (48, 30),
     (48, 29), (50, 26), (52, 24), (54, 24), (56, 24), (58, 22), (59, 22),
     (57, 20), (55, 18), (54, 17), (52, 16), (50, 15), (48, 14), (46, 13),
     (44, 12), (43, 12), (42, 15), (40, 15), (39, 18), (38, 20), (37, 22),
     (36, 24), (35, 28), (34, 28), (34, 31), (33, 31), (32, 34)],
    [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (141, -13), (137, -12), (135, -15), (132, -12), (130, -13), (127, -14),
     (124, -15), (122, -17), (118, -20)],
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
     (141, 39), (141, 42), (142, 44), (144, 44), (145, 43), (143, 41),
     (141, 38), (140, 36), (138, 34), (136, 33), (133, 34), (131, 33)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -5), (100, 0),
     (97, 4)],
    [(109, 1), (112, 4), (116, 6), (118, 2), (117, -2), (114, -4),
     (110, -3)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9),
     (142, -8), (138, -8), (134, -4)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
     (175, -40), (173, -42), (170, -44)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25), (44, -25),
     (43, -20)],
]

# (number, label, lon, lat, label dx, label dy) -- offsets staggered so the
# tight Europe / Middle East cluster stays legible at this scale.
PINS = [
    (1, "ANTALYA", 30.7, 36.9, -52, -14),
    (2, "LIMA", -77.0, -12.0, 8, -4),
    (3, "MANAMA", 50.6, 26.2, -52, 12),
    (4, "KUWAIT CITY", 48.0, 29.4, 8, 10),
    (5, "KYIV", 30.5, 50.5, -42, 10),
    (6, "MOSCOW", 37.6, 55.8, 10, -14),
    (7, "DELHI", 77.2, 28.6, 8, -4),
    (8, "KATHMANDU", 85.3, 27.7, -64, 10),
    (9, "CULIACAN", -107.4, 24.8, -62, -12),
    (10, "BASRA", 47.8, 30.5, -48, 20),
    (11, "HELSINKI", 24.9, 60.2, -60, -12),
    (12, "JERUSALEM", 35.2, 31.8, 8, -14),
]

# ---------------------------------------------------------------- layout
MX = 8                      # side margin
CW = 1008                   # content width
STORY_TOP = 434
STORY_ROWS = 7
STORY_COLS = 5
CELL_W = 196
CELL_GAP = 7
ROW_H = 82


def project(lon, lat, mx0, my0, mw, mh):
    x = mx0 + (lon + 168.0) / 360.0 * mw
    y = my0 + (78.0 - lat) / 136.0 * mh
    return (int(x), int(y))


# ---------------------------------------------------------------- drawing
def draw_masthead():
    hline(MX, MX + CW - 1, 6, INK, 3)
    draw_text("THE WORLD IN ONE DAY", 512, 10, 6, 5, INK, bold=True,
              align="center")
    draw_text("SUNDAY, 22 NOVEMBER 2026", 512, 48, 2, 2, RED, bold=True,
              align="center")
    draw_text("ONE DAY. EVERY STORY THAT MATTERED.", 512, 64, 1, 2,
              INK_SOFT, align="center")
    hline(MX, MX + CW - 1, 82, INK, 2)


def draw_hero():
    draw_text("CLIMATE - ANTALYA, TURKIYE - 22 NOV 2026", 512, 88, 2, 2,
              TEAL, bold=True, align="center")
    draw_text("COP31 NEARS DEAL AT DAWN", 512, 106, 4, 5, INK, bold=True,
              align="center")
    draw_text("AFTER FOSSIL-FUEL FIGHT", 512, 144, 4, 5, INK, bold=True,
              align="center")
    draw_text("NEARLY 200 NATIONS DEBATE A NEW TEXT AFTER ALL-NIGHT TALKS.",
              512, 184, 1, 2, INK_SOFT, align="center")
    draw_text("PLENARY VOTE DUE TODAY AS FOSSIL-FUEL LANGUAGE IS ARGUED.",
              512, 200, 1, 2, INK_SOFT, align="center")
    hline(MX, MX + CW - 1, 220, INK, 1)


def draw_map():
    draw_text("THE WORLD AT A GLANCE - 22 NOVEMBER 2026", MX, 226, 1, 2,
              INK, bold=True)
    draw_text("NUMBERED PINS MARK THE DAY'S PLACES", 1016, 226, 1, 2,
              INK_SOFT, align="right")
    mx0, my0, mw, mh = MX, 244, CW, 92
    fill_rect(mx0, my0, mw, mh, SEA)
    # faint latitude lines for a chart feel
    for lat in (60, 30, 0, -30):
        _, yy = project(0, lat, mx0, my0, mw, mh)
        for xx in range(mx0, mx0 + mw, 6):
            set_px(xx, yy, (150, 178, 192))
    for i, poly in enumerate(CONTINENTS):
        pts = [project(lo, la, mx0, my0, mw, mh) for lo, la in poly]
        fill_poly(pts, LAND if i % 2 == 0 else LAND2)
        poly_line(pts, (120, 104, 72))
    # pins with leader lines to staggered labels
    for num, label, lon, lat, dx, dy in PINS:
        px, py = project(lon, lat, mx0, my0, mw, mh)
        lx, ly = px + dx, py + dy
        line(px, py, lx + (4 if dx >= 0 else text_width(label, 1) - 4),
             ly + 3, INK_SOFT)
        draw_text(label, lx, ly, 1, 1, INK, bold=True)
        disc(px, py, 7, RED)
        ring(px, py, 7, (255, 255, 255))
        draw_text(str(num), px, py - 3, 1, 1, (255, 255, 255), align="center")
    # frame
    fill_rect(mx0, my0, mw, 2, INK)
    fill_rect(mx0, my0 + mh - 2, mw, 2, INK)
    fill_rect(mx0, my0, 2, mh, INK)
    fill_rect(mx0 + mw - 2, my0, 2, mh, INK)


def flag(x, y, c1, c2):
    vline(x, y, y + 22, INK, 1)
    fill_rect(x + 1, y, 14, 5, c1)
    fill_rect(x + 1, y + 5, 14, 5, c2)


def draw_panel_cop(x, y, w, h):
    # h is the illustration height (caption sits below it).
    fill_rect(x, y, w, h, (232, 214, 170))
    fill_rect(x, y, w, 16, (244, 196, 120))
    fill_rect(x, y + 16, w, 8, (238, 170, 110))
    disc(x + w // 2, y + 20, 9, (255, 226, 130))
    fill_rect(x, y + 24, w, h - 24, (120, 96, 70))
    fill_rect(x + 14, y + 34, w - 28, 3, (220, 196, 150))
    fill_rect(x + 14, y + 37, w - 28, 7, (90, 66, 44))
    for i in range(9):
        dx = x + 24 + i * 34
        disc(dx, y + 30, 4, (40, 40, 40))
        fill_rect(dx - 6, y + 33, 12, 7, (70, 70, 90) if i % 2 else (90, 60, 60))
    flag(x + 16, y + 2, RED, (255, 255, 255))
    flag(x + 52, y + 2, BLUE, (255, 255, 255))
    flag(x + 88, y + 2, GREEN, (255, 255, 255))
    flag(x + 250, y + 2, GOLD, (255, 255, 255))
    flag(x + 286, y + 2, TEAL, (255, 255, 255))


def draw_panel_quake(x, y, w, h):
    fill_rect(x, y, w, h, (226, 210, 180))
    fill_rect(x, y, w, 18, (196, 214, 226))
    disc(x + 280, y + 9, 7, (255, 240, 170))
    fill_rect(x, y + 34, w, h - 34, (150, 124, 88))
    pts = [(x + 10, y + 34), (x + 60, y + 40), (x + 110, y + 35),
           (x + 170, y + 42), (x + 230, y + 36), (x + 300, y + 41),
           (x + 320, y + 35), (x + 320, y + 38), (x + 230, y + 39),
           (x + 170, y + 45), (x + 110, y + 38), (x + 60, y + 43),
           (x + 10, y + 37)]
    fill_poly(pts, (90, 66, 44))
    fill_poly([(x + 40, y + 34), (x + 60, y + 30), (x + 63, y + 14),
               (x + 43, y + 18)], (176, 84, 60))
    fill_poly([(x + 90, y + 34), (x + 110, y + 32), (x + 108, y + 10),
               (x + 88, y + 12)], (150, 150, 150))
    fill_poly([(x + 200, y + 34), (x + 224, y + 37), (x + 220, y + 16),
               (x + 196, y + 13)], (96, 110, 140))
    for bx, by in ((48, 22), (96, 18), (204, 20)):
        fill_rect(x + bx, y + by, 4, 4, (255, 240, 170))
    disc(x + 150, y + 28, 7, (210, 196, 170))
    disc(x + 164, y + 31, 5, (210, 196, 170))
    disc(x + 260, y + 29, 6, (210, 196, 170))


def draw_panel_ship(x, y, w, h):
    fill_rect(x, y, w, h, (196, 214, 226))
    fill_rect(x, y + 30, w, h - 30, (36, 84, 128))
    for wy in (35, 41):
        for xx in range(x + 8, x + w - 8, 26):
            hline(xx, xx + 14, y + wy, (120, 180, 210), 1)
    fill_poly([(x + 30, y + 28), (x + 290, y + 28), (x + 270, y + 40),
               (x + 50, y + 40)], (120, 40, 32))
    fill_rect(x + 30, y + 28, 260, 3, (60, 60, 60))
    fill_rect(x + 60, y + 16, 40, 12, (200, 120, 40))
    fill_rect(x + 104, y + 16, 40, 12, (60, 120, 90))
    fill_rect(x + 148, y + 16, 40, 12, (180, 180, 170))
    fill_rect(x + 240, y + 10, 34, 18, (240, 240, 230))
    fill_rect(x + 246, y + 15, 22, 5, (40, 60, 90))
    for fx, fh, fc in ((120, 18, ORANGE), (132, 24, (230, 60, 20)),
                       (146, 16, (255, 200, 60)), (164, 21, ORANGE)):
        fill_poly([(x + fx, y + 20), (x + fx + 6, y + 20 - fh),
                   (x + fx + 12, y + 20)], fc)
    disc(x + 140, y + 4, 7, (90, 90, 90))
    disc(x + 156, y + 1, 8, (110, 110, 110))
    disc(x + 172, y + 5, 6, (90, 90, 90))
    disc(x + 188, y + 1, 7, (120, 120, 120))


def draw_panels():
    y0 = 342
    ph = 64
    pw = 328
    panels = [
        (draw_panel_cop, "COP31 HALL AT DAWN, ANTALYA"),
        (draw_panel_quake, "CRACKED EARTH, JUNIN, PERU"),
        (draw_panel_ship, "SPARTA II BURNS, GULF OF FINLAND"),
    ]
    for i, (fn, cap) in enumerate(panels):
        x = MX + i * (pw + 6)
        fn(x, y0, pw, ph - 16)
        fill_rect(x, y0, pw, 2, INK)
        fill_rect(x, y0 + ph - 16, pw, 2, INK)
        fill_rect(x, y0, 2, ph, INK)
        fill_rect(x + pw - 2, y0, 2, ph, INK)
        draw_text(cap, x + 4, y0 + ph - 14, 1, 2, INK, bold=True)


def draw_ticker():
    y0 = 412
    fill_rect(MX, y0, CW, 16, INK)
    draw_text("ALSO TODAY: PERU COUNTS 152 HOMES UNINHABITABLE - GHANA "
              "UNVEILS HERITAGE BANKNOTES - NORWAY VOIDS OIL LICENCES - "
              "AL-SHABAAB CLAIMS AMBUSH",
              MX + 6, y0 + 1, 1, 2, (255, 255, 255))


def draw_stories():
    region_color = {
        "WORLD": RED,
        "AMERICAS": BLUE,
        "EUROPE": TEAL,
        "MIDDLE EAST & AFRICA": (140, 80, 10),
        "ASIA-PACIFIC": GREEN,
        "SPORT": (120, 40, 120),
        "TECH & MARKETS": (90, 60, 20),
    }
    region_short = {
        "WORLD": "WORLD",
        "AMERICAS": "AMERICAS",
        "EUROPE": "EUROPE",
        "MIDDLE EAST & AFRICA": "MIDEAST & AFRICA",
        "ASIA-PACIFIC": "ASIA-PACIFIC",
        "SPORT": "SPORT",
        "TECH & MARKETS": "TECH & MARKETS",
    }
    for idx, (region, head, deck) in enumerate(STORIES):
        row, col = divmod(idx, STORY_COLS)
        x = MX + col * (CELL_W + CELL_GAP)
        y = STORY_TOP + row * ROW_H
        if col > 0:
            vline(x - 4, y + 2, y + ROW_H - 6, (200, 192, 172), 1)
        rc = region_color[region]
        fill_rect(x, y + 1, 5, 8, rc)
        draw_text(region_short[region] + " - 22 NOV", x + 9, y + 1, 1, 1,
                  rc, bold=True)
        hlines = wrap_max(head, 16, 2)
        for li, ln in enumerate(hlines):
            draw_text(ln, x, y + 11 + li * 21, 2, 3, INK, bold=True)
        dlines = wrap_max(deck, 32, 2)
        for li, ln in enumerate(dlines):
            draw_text(ln, x, y + 55 + li * 13, 1, 2, INK_SOFT, bold=True)


def draw_footer():
    y0 = 1015
    hline(MX, MX + CW - 1, 1012, INK, 2)
    draw_text("MARKETS 22 NOV: BRENT $92.57 +0.64% - WTI $83.98 +0.93% - "
              "S AND P 500 -3.70% - NASDAQ -5.28% - SOURCES: REUTERS - BBC "
              "- AP - CNN - AL JAZEERA",
              512, y0, 1, 1, INK, align="center")


def paper_grain():
    # Deterministic fine grain on every pixel: a small hash-based lift/dark
    # so the paper never reads as flat colour, and the PNG stays rich.
    # Pure integer hash, no RNG, no clock.
    for y in range(H):
        base = y * W * 3
        for x in range(W):
            v = (x * 2654435761 + y * 40503) & 0xFFFFFFFF
            v ^= v >> 13
            d = ((v >> 4) & 7) - 3
            if d:
                i = base + x * 3
                IMG[i] = max(0, min(255, IMG[i] + d))
                IMG[i + 1] = max(0, min(255, IMG[i + 1] + d))
                IMG[i + 2] = max(0, min(255, IMG[i + 2] + d))
    # faint horizontal press lines every 64 rows
    for y in range(32, H, 64):
        for x in range(0, W, 3):
            i = _idx(x, y)
            IMG[i] = max(0, IMG[i] - 4)
            IMG[i + 1] = max(0, IMG[i + 1] - 4)
            IMG[i + 2] = max(0, IMG[i + 2] - 4)


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(IMG[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    return png


def main():
    fill_rect(0, 0, W, H, PAPER)
    draw_masthead()
    draw_hero()
    draw_map()
    draw_panels()
    draw_ticker()
    draw_stories()
    draw_footer()
    paper_grain()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png())
    print("wrote " + path)


if __name__ == "__main__":
    main()
