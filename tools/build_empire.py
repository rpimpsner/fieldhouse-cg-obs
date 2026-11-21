"""Builds the "Empire Blue" package: templates/packages/empire-blue.json.

Modelled on the look of a 2023 New York regional-network baseball package (studied from the designer's public
case study): deep navy bars with a bright "new blue" accent, silver logo tiles, condensed type for names and
numbers, heavy type for titles, a light diagonal pattern band framing full screens, and team-coloured stat panels.
No network or team marks are included; logos come from your own team / brand settings.
Run:  python tools/build_empire.py   (after tools/build_night_game.py)
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import broadcast_lib as BL  # noqa: E402
import sports_lib as SL  # noqa: E402
import skin as SK  # noqa: E402
from broadcast_lib import A, box, txt, img, el, both, logo_or_abbr, sponsor_tab, U, L  # noqa: E402

NAVY = "linear-gradient(180deg, #213E6C 0%, #13284D 52%, #0B1A36 100%)"
NAVY2 = "linear-gradient(180deg, #1A325C 0%, #0E2042 100%)"
DEEP = "#0A1530"
BLUE = "#3D8EF0"
BLUE_BAR = "linear-gradient(180deg, #3F86E6 0%, #2A63C2 100%)"
FIRST = "#5AA9FF"
SILVER = "linear-gradient(180deg, #FFFFFF 0%, #E4E8EE 45%, #B8C0CB 100%)"
SUBROW = "linear-gradient(180deg, #F2F4F7 0%, #D9DEE5 100%)"
PATTERN = "repeating-linear-gradient(135deg, #F1F3F7 0 16px, #DCE2EA 16px 32px)"
INK = "#0B1A36"
TEAM = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 82%%, #fff) 0%%, {%s.color} 50%%, "
        "color-mix(in srgb, {%s.color} 58%%, #000) 100%%)")

EB = dict(BL.NETWORK, key="empire", font="$font2", body="$font2", up=True, radius=4, cardRadius=4,
          panel=NAVY, panel2=NAVY2, dark=DEEP, strip=BLUE_BAR, stripText="#FFFFFF", val=SILVER, valText=INK,
          hi=BLUE, hiText="#FFFFFF", line="#5AA9FF@0.45", shadow="0 14px 34px rgba(0,0,0,.5)", cardIn="zoom-out",
          teamGrad=TEAM, titleBg="linear-gradient(160deg, #9CCBFF 0%, #3D8EF0 45%, #1C58BC 100%)")
F = "$font2"           # condensed: names, numbers, labels
H = "$font"            # heavy: titles
LIVE = "inPlay"
OUT_ = {"type": "fade", "dur": 260, "delay": 0, "ease": "in"}


def T(team):
    return TEAM % (team, team, team)


# ------------------------------------------------------------------ scorebug (top left)
def scorebug():
    """Two team blocks (colour box with logo and abbreviation, white score box, gray sub-row with the pitcher and
    pitch speed or the batter and his line) and a silver situation box (bases, inning, count, outs)."""
    X, Y, TW, R1, R2 = 40, 34, 264, 52, 30
    SW = 172
    W = 2 * TW + SW + 8
    E = [box("Frame", X, Y, W, R1 + R2 + 8, None, A("wipe-right", 420, 0, out={"type": "wipe-left", "dur": 300, "delay": 120, "ease": "in"}),
             bg=SILVER, radius=6, shadow=EB["shadow"])]
    for i, side in enumerate(("away", "home")):
        x = X + 4 + i * TW
        d = i * 80
        other = "home" if side == "away" else "away"
        E += [box("%s color" % side, x, Y + 4, 168, R1, None, A("wipe-right", 360, 120 + d), bg=T(side), radius=3)]
        E += logo_or_abbr("%s logo" % side, x + 6, Y + 8, 46, R1 - 8, side, 18, A("fade", 260, 300 + d), S=EB)
        E += [txt("%s abbr" % side, x + 56, Y + 4, 108, R1, "{%s.abbr|upper}" % side, 38, A("fade", 260, 320 + d), font=F, weight=800, textShadow=True),
              box("%s score bg" % side, x + 170, Y + 4, TW - 174, R1, "#FFFFFF", A("fade", 260, 200 + d), radius=3),
              txt("%s runs" % side, x + 170, Y + 4, TW - 174, R1, "{%s.runs}" % side, 44, A("reveal-up", 300, 360 + d, change="pop"), font=F, weight=800,
                  align="center", color="{%s.color}" % side),
              box("%s sub" % side, x, Y + 4 + R1, TW - 4, R2, None, A("wipe-down", 300, 260 + d), bg=SUBROW, show=LIVE),
              # this team in the field: its pitcher and the last pitch speed (or pitch count)
              txt("%s pitcher" % side, x + 8, Y + 4 + R1, 170, R2, "{pitcher.last|upper}", 20, A("fade", 240, 440 + d),
                  show=both(LIVE, "battingSide==%s" % other), font=F, weight=800, color=INK),
              txt("%s velo" % side, x + 170, Y + 4 + R1, TW - 186, R2, "{velo.ps} MPH", 20, A("fade", 240, 460 + d, change="flash"),
                  show=both(LIVE, "battingSide==%s" % other, "velo.ps"), font=F, weight=800, color=INK, align="right"),
              txt("%s pc" % side, x + 170, Y + 4 + R1, TW - 186, R2, "P {pitcher.today.pc|zero}", 20, A("fade", 240, 460 + d, change="flash"),
                  show=both(LIVE, "battingSide==%s" % other, "!velo.ps"), font=F, weight=800, color=INK, align="right"),
              # this team batting: slot, batter, today's line
              txt("%s batter" % side, x + 8, Y + 4 + R1, 180, R2, "{batter.slot} {batter.last|upper}", 20, A("fade", 240, 440 + d),
                  show=both(LIVE, "battingSide==%s" % side), font=F, weight=800, color=INK),
              txt("%s hab" % side, x + 180, Y + 4 + R1, TW - 196, R2, "{batter.today.hab}", 20, A("fade", 240, 460 + d, change="flash"),
                  show=both(LIVE, "battingSide==%s" % side), font=F, weight=800, color=INK, align="right")]
    sx = X + 4 + 2 * TW
    E += [box("Situation", sx, Y + 4, SW - 4, R1 + R2, None, A("wipe-right", 360, 260), bg=SUBROW, radius=3),
          el("bases", "Bases", sx + 8, Y + 8, 84, 46, A("pop", 360, 460), show=LIVE, bind="bases",
             style={"layout": "tight", "on": "#13284D", "off": "#FFFFFF", "stroke": "#8C97A6", "strokeW": 2}),
          txt("Inning", sx + 8, Y + 52, 84, 30, "{arrow}{inning}", 22, A("fade", 240, 500, change="roll"), show=LIVE, font=F, weight=800, align="center",
              color=INK),
          txt("Count", sx + 92, Y + 6, SW - 100, 44, "{balls}-{strikes}", 34, A("fade", 240, 520, change="flash"), show=LIVE, font=F, weight=800,
              align="center", color=INK),
          el("dots", "Outs", sx + 100, Y + 54, SW - 112, 24, A("fade", 240, 540), show=LIVE, bind="outs",
             style={"total": 2, "size": 14, "gap": 7, "on": "#13284D", "off": "#13284D@0.22", "align": "center"}),
          txt("Status", sx, Y + 4, SW - 4, R1 + R2, "{statusText}", 26, A("fade", 240, 460), show="!" + LIVE, font=F, weight=800, align="center",
              color=INK, wrap=True, fit=False)]
    E += sponsor_tab(X, Y + R1 + R2 + 14, 300, 40, 600, radius=4, a_type="wipe-down")
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(kind):
    """Silver logo tile, navy bar with a thin blue outline: number over position, first name in blue over the last
    name, then four stat columns with labels and dividers."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    if kind == "pit":
        cols = [("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.today.ip|dash}"),
                ("SO", "{pitcher.today.k|zero}")]
        tag = "{pitcher.throws|hand}"
    else:
        cols = [("AVG", "{batter.season.avg|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}"),
                ("OBP", "{batter.season.obp|avg}")]
        tag = "{batter.pos}"
    W, Hh = 1180, 96
    X, Y = (1920 - W) // 2, 896
    TL, NM, CW = 128, 380, (W - 128 - 380) // 4
    E = [box("Tile", X, Y, TL, Hh, None, A("pop", 420, 0, out=OUT_), bg=SILVER, radius=4, shadow=EB["shadow"])]
    E += logo_or_abbr("Logo", X + 14, Y + 8, TL - 28, Hh - 16, team, 34, A("zoom-out", 400, 160), color=INK, S=EB)
    E += [box("Bar", X + TL - 4, Y, W - TL + 4, Hh, None, A("wipe-right", 460, 120, out=OUT_), bg=NAVY, radius=4, borderW=2, borderColor="#5AA9FF@0.85",
              shadow=EB["shadow"]),
          txt("Number", X + TL + 6, Y + 6, 56, 44, "{%s.number}" % who, 36, A("fade", 260, 380), font=F, weight=800, align="center"),
          txt("Tag", X + TL + 6, Y + 46, 56, 40, tag, 30, A("fade", 260, 400), font=F, weight=800, align="center"),
          box("Rule", X + TL + 66, Y + 14, 2, Hh - 28, "#FFFFFF@0.35", A("grow-y", 260, 420)),
          txt("First", X + TL + 80, Y + 4, NM - 90, 38, "{%s.first|upper}" % who, 32, A("fade", 260, 420), font=F, weight=600, color=FIRST),
          txt("Last", X + TL + 78, Y + 34, NM - 90, 60, "{%s.last|upper}" % who, 56, A("reveal-up", 360, 400), font=F, weight=800)]
    for i, (lab, val) in enumerate(cols):
        cx = X + TL + NM + i * CW
        E += [txt("%s label" % lab, cx, Y + 6, CW, 26, lab, 20, A("fade", 240, 520 + i * 60), font=F, weight=700, align="center", color="#C9D6EA"),
              txt("%s value" % lab, cx, Y + 28, CW, 62, val, 56, A("reveal-up", 300, 540 + i * 60, change="flash"), font=H, weight=800, align="center")]
        if i:
            E.append(box("Divider %d" % i, cx, Y + 18, 2, Hh - 36, "#5AA9FF@0.45", A("grow-y", 240, 560 + i * 60)))
    E += sponsor_tab(X + W - 300, Y - 48, 300, 42, 640, radius=4, a_type="wipe-up")
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


# ------------------------------------------------------------------ ticker
def ticker():
    Y, HH = 1022, 50
    E = [box("Bar", 0, Y - 6, 1920, HH + 12, DEEP, A("wipe-up", 400, 0, out={"type": "wipe-down", "dur": 300, "delay": 0, "ease": "in"})),
         txt("Label", 40, Y, 170, HH, "{ticker.label|upper}", 30, A("fade", 260, 300), show="ticker.label", font=F, weight=800, align="center"),
         txt("League", 40, Y, 170, HH, "{league.name|upper}", 26, A("fade", 260, 300), show="!ticker.label && league.name", font=F, weight=800,
             align="center"),
         box("Inner", 230, Y + 4, 1420, HH - 8, None, A("wipe-right", 420, 160), bg=NAVY, radius=4, borderW=1, borderColor="#5AA9FF@0.6"),
         box("Chip", 236, Y + 8, 52, HH - 16, None, A("pop", 300, 360), bg=SILVER, radius=3),
         img("Chip logo", 240, Y + 10, 44, HH - 20, "{home.logo}", A("fade", 260, 420), show="home.logo"),
         el("ticker", "Crawl", 300, Y + 4, 1340, HH - 8, A("fade", 400, 500), bind="ticker.items",
            style={"size": 28, "weight": 800, "color": "#FFFFFF", "font": F, "speed": 110, "headFill": BLUE, "headColor": "#FFFFFF", "upper": True}),
         box("Brand box", 1680, Y + 6, 200, HH - 12, None, A("pop", 320, 420), bg=DEEP, radius=4, show="brand.logo"),
         img("Brand", 1690, Y + 8, 180, HH - 16, "{brand.logo}", A("fade", 300, 480), show="brand.logo")]
    return {"name": "Bottom Ticker", "group": "ticker", "autoHide": 0, "side": "", "sided": False, "elements": E, "noLift": False}


# ------------------------------------------------------------------ full-screen frame
def frame(title, sub, logo="{team.logo}", logo_show="team.logo", X=160, Y=80, W=1600, Hb=740, title_size=82, delay=0):
    """Pattern band, silver logo tile + navy title bar, blue sub strip, navy body, pattern band."""
    E = [box("Band top", X, Y, W, 40, None, A("wipe-right", 420, delay), bg=PATTERN),
         box("Band top line", X, Y + 38, W, 3, BLUE, A("grow-x", 420, delay + 120)),
         box("Tile", X, Y + 41, 160, 100, None, A("fade", 360, delay + 160), bg=SILVER),
         img("Tile logo", X + 18, Y + 49, 124, 84, logo, A("zoom-out", 400, delay + 300), show=logo_show),
         box("Title bar", X + 160, Y + 41, W - 160, 100, None, A("wipe-right", 420, delay + 160), bg="linear-gradient(180deg, #0B1A36, #13284D)"),
         txt("Title", X + 190, Y + 41, W - 220, 100, title, title_size, A("reveal-up", 420, delay + 340), font=H, weight=800),
         box("Sub strip", X, Y + 141, W, 46, None, A("wipe-right", 380, delay + 260), bg=BLUE_BAR, show=None if sub else "false"),
         txt("Sub", X + 190, Y + 141, W - 220, 46, sub, 30, A("fade", 260, delay + 420), font=F, weight=700, show=None if sub else "false"),
         box("Body", X, Y + 187, W, Hb - 187, None, A("fade", 400, delay + 200), bg=NAVY),
         box("Body lines", X, Y + 187, W, Hb - 187, None, A("fade", 600, delay + 400),
             bg="repeating-linear-gradient(135deg, rgba(255,255,255,0.025) 0 22px, transparent 22px 44px)"),
         box("Band bottom line", X, Y + Hb, W, 3, BLUE, A("grow-x", 420, delay + 200)),
         box("Band bottom", X, Y + Hb + 3, W, 34, None, A("wipe-right", 420, delay + 120), bg=PATTERN)]
    return E


def feature():
    """Milestones card: photo panel with the name, three lines with blue rules, an italic footnote."""
    X, Y, W, Hb = 160, 80, 1600, 760
    E = frame("{notes.title|upper}", "{notes.kicker|upper}", Hb=Hb)
    E[5]["showIf"] = "notes.title"
    E.insert(6, txt("Title (name)", X + 190, Y + 41, W - 220, 100, "{team.name|upper}", 82, A("reveal-up", 420, 340), show="!notes.title", font=H,
                    weight=800))
    E[7]["showIf"] = E[8]["showIf"] = "notes.kicker"
    E += [box("Photo panel", X, Y + 187, 560, Hb - 187, None, A("wipe-up", 420, 400), bg=T("team")),
          img("Photo logo", X + 30, Y + 220, 220, 180, "{team.logo}", A("fade", 400, 500), show="team.logo", opacity=0.35),
          img("Photo", X + 120, Y + 200, 440, Hb - 200, "{batter.photo}", A("slide-up", 500, 520, dist=40), show="batter.photo", fit="contain",
              focus="center bottom"),
          box("Name rule", X + 40, Y + Hb - 150, 4, 110, BLUE, A("grow-y", 300, 700)),
          txt("First", X + 56, Y + Hb - 156, 480, 50, "{batter.first|upper}", 40, A("fade", 260, 760), font=F, weight=700, color=FIRST, textShadow=True),
          txt("Last", X + 54, Y + Hb - 110, 480, 76, "{batter.last|upper}", 70, A("reveal-up", 340, 780), font=F, weight=800, textShadow=True)]
    for i in range(3):
        k = "notes.b%d" % (i + 1)
        y = Y + 220 + i * 140
        E += [txt("Line %d" % (i + 1), X + 600, y, W - 660, 110, "{%s|upper}" % k, 48, A("slide-left", 360, 640 + i * 140, dist=30), show=k, font=F,
                  weight=800, wrap=True, fit=False, lineH=1.05),
              box("Rule %d" % (i + 1), X + 600, y + 122, W - 680, 2, BLUE, A("grow-x", 360, 700 + i * 140), show=k)]
    E += [box("Foot bg", X + 560, Y + Hb - 64, W - 560, 64, DEEP, A("fade", 300, 900), show="notes.foot"),
          txt("Foot", X + 600, Y + Hb - 64, W - 660, 64, "{notes.foot|upper}", 32, A("fade", 260, 1000), show="notes.foot", font=F, weight=700,
              italic=True, align="center", color="#D6DEEA")]
    E += sponsor_tab(X + W - 340, Y - 50, 340, 44, 900, radius=4)
    return {"name": "Feature Card", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "feature"}


def summary():
    """Game summary: inning header in blue, each team as a silver logo tile and a team-colour bar of numbers with
    dividers and a darker R H E end, then each team's starter and last pitcher on its colour, and a note."""
    X, Y, W = 160, 80, 1600
    E = [box("Band top", X, Y, W, 40, None, A("wipe-right", 420, 0), bg=PATTERN),
         box("Band line", X, Y + 38, W, 3, BLUE, A("grow-x", 420, 120)),
         box("Title bar", X, Y + 41, W, 110, None, A("wipe-center", 420, 160), bg="linear-gradient(180deg, #0B1A36, #13284D)"),
         txt("Title", X, Y + 41, W, 110, "GAME SUMMARY", 88, A("reveal-up", 420, 340), font=H, weight=800, align="center"),
         box("Inning bar", X, Y + 151, W, 50, None, A("wipe-right", 380, 260), bg=BLUE_BAR)]
    TL, CW = 180, 104
    x0 = X + TL + 30
    for i in range(9):
        E.append(txt("Inn %d" % (i + 1), x0 + i * CW, Y + 151, CW, 50, str(i + 1), 32, A("fade", 240, 360 + i * 20), font=F, weight=700, align="center"))
    for j, lab in enumerate(("R", "H", "E")):
        E.append(txt("Head " + lab, x0 + 9 * CW + 20 + j * 104, Y + 151, 104, 50, lab, 32, A("fade", 240, 560), font=F, weight=800, align="center"))
    for r, side in enumerate(("away", "home")):
        y = Y + 220 + r * 116
        d = 400 + r * 140
        E += [box("%s tile" % side, X, y, TL, 100, None, A("fade", 320, d), bg=SILVER)]
        E += logo_or_abbr("%s logo" % side, X + 22, y + 8, TL - 44, 84, side, 34, A("zoom-out", 360, d + 120), color=INK, S=EB)
        E += [box("%s bar" % side, X + TL, y, W - TL, 100, None, A("wipe-right", 420, d + 60), bg=T(side), radius=6),
              box("%s totals" % side, x0 + 9 * CW + 20, y, W - (x0 + 9 * CW + 20 - X), 100, "#000000@0.25", A("fade", 300, d + 260))]
        for i in range(9):
            E += [txt("%s %d" % (side, i + 1), x0 + i * CW, y, CW, 100, "{linescore.%s.%d}" % (side, i), 60, A("fade", 240, d + 200 + i * 30,
                      change="flash"), font=H, weight=800, align="center", textShadow=True)]
            if i:
                E.append(box("%s div %d" % (side, i), x0 + i * CW, y + 24, 2, 52, "#FFFFFF@0.35", A("grow-y", 220, d + 200 + i * 30)))
        for j, k in enumerate(("runs", "hits", "errors")):
            E.append(txt("%s %s" % (side, k), x0 + 9 * CW + 20 + j * 104, y, 104, 100, "{%s.%s}" % (side, k), 60, A("fade", 240, d + 520 + j * 40,
                         change="pop"), font=H, weight=800, align="center", textShadow=True))
    for i, side in enumerate(("away", "home")):
        px = X + i * W // 2
        pw = W // 2
        E += [box("%s pitchers" % side, px, Y + 458, pw, 236, None, A("wipe-up", 400, 900 + i * 120), bg=T(side))]
        for j, who in enumerate(("sp", "finisher")):
            y = Y + 470 + j * 110
            ix = px + 14 if i == 0 else px + pw - 114
            tx = px + 130 if i == 0 else px + 20
            al = "left" if i == 0 else "right"
            E += [img("%s %s photo" % (side, who), ix, y, 100, 100, "{%s.%s.photo}" % (side, who), A("fade", 300, 1000 + i * 120 + j * 80),
                      show="%s.%s.photo" % (side, who), fit="cover", focus="center top"),
                  txt("%s %s name" % (side, who), tx, y + 4, pw - 150, 50, "{%s.%s.name|upper}" % (side, who), 40, A("reveal-up", 320, 1040 + i * 120 + j * 80),
                      show="%s.%s.name" % (side, who), font=F, weight=800, align=al, textShadow=True),
                  txt("%s %s line" % (side, who), tx, y + 54, pw - 150, 40, "{%s.%s.line|upper}" % (side, who), 30, A("fade", 260, 1100 + i * 120 + j * 80),
                      show="%s.%s.name" % (side, who), font=F, weight=700, align=al)]
    E += [box("Note bg", X, Y + 694, W, 56, DEEP, A("fade", 300, 1200)),
          txt("Note", X, Y + 694, W, 56, "{custom.line1|upper}", 32, A("fade", 260, 1300), show="custom.line1", font=F, weight=700, italic=True,
              align="center", color="#D6DEEA"),
          box("Band bottom line", X, Y + 750, W, 3, BLUE, A("grow-x", 420, 200)),
          box("Band bottom", X, Y + 753, W, 34, None, A("wipe-right", 420, 120), bg=PATTERN)]
    return {"name": "Game Summary", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "final"}


def tall(kind):
    """Team-colour season card: photo with logo and hand, name band, season band, stat rows with thin dividers."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    X, Y, W = 1470, 110, 380
    E = [box("Card", X, Y, W, 850, None, A("wipe-up", 460, 0, out=OUT_), bg=T(team), radius=10, borderW=2, borderColor="#FFFFFF@0.35",
             shadow=EB["shadow"]),
         img("Logo", X + 190, Y + 20, 170, 150, "{%s.logo}" % team, A("fade", 400, 200), show="%s.logo" % team, opacity=0.9),
         img("Photo", X + 10, Y + 14, 220, 250, "{%s.photo}" % who, A("slide-up", 460, 260, dist=30), show="%s.photo" % who, fit="contain",
             focus="center bottom"),
         txt("Number", X + 10, Y + 14, 220, 250, "{%s.number}" % who, 150, A("fade", 400, 260), show="!%s.photo" % who, font=H, weight=800,
             align="center", color="#FFFFFF@0.35", fit=False),
         txt("Hand", X + 220, Y + 176, 140, 50, ("{pitcher.throws|hand}" if kind == "pit" else "{batter.pos}"), 36, A("fade", 260, 420), font=F,
             weight=800, align="center", textShadow=True),
         box("Name band", X + 2, Y + 266, W - 4, 116, "#000000@0.45", A("fade", 300, 300)),
         txt("First", X + 22, Y + 270, W - 44, 44, "{%s.first|upper}" % who, 36, A("fade", 260, 420), font=F, weight=600, color="#D9E3F2"),
         txt("Last", X + 20, Y + 306, W - 40, 70, "{%s.last|upper}" % who, 62, A("reveal-up", 340, 440), font=F, weight=800),
         box("Season band", X + 2, Y + 382, W - 4, 46, None, A("wipe-right", 300, 480), bg="color-mix(in srgb, {%s.color} 70%%, #fff)" % team),
         txt("Season", X + 2, Y + 382, W - 4, 46, "{seasonYear} SEASON", 30, A("fade", 260, 560), font=F, weight=700, align="center")]
    for i in range(6):
        p = "%s.card.%d" % (who, i)
        y = Y + 438 + i * 66
        E += [txt("Label %d" % i, X + 24, y, 200, 62, "{%s.label|upper}" % p, 28, A("fade", 240, 600 + i * 60), show=p + ".label", font=F, weight=600),
              txt("Value %d" % i, X + 180, y, W - 204, 62, "{%s.value}" % p, 50, A("reveal-up", 280, 620 + i * 60), show=p + ".label", font=H, weight=800,
                  align="right"),
              box("Line %d" % i, X + 24, y + 63, W - 48, 2, "#FFFFFF@0.35", A("grow-x", 260, 640 + i * 60), show=p + ".label")]
    return {"name": "%s Season Card" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


def performers():
    """Four team-colour columns: photo with logo, dark name band with a coloured rule, stat rows."""
    X, Y, W = 160, 80, 1600
    E = frame("TOP PERFORMERS", "TONIGHT", logo="{league.logo}", logo_show="league.logo", Hb=760)
    cw = (W - 30) // 4
    for i in range(4):
        p = "performers.%d" % i
        cx = X + i * (cw + 10)
        d = 520 + i * 110
        tg = TEAM % (p, p, p)
        E += [box("P%d bg" % i, cx, Y + 187, cw, 573, None, A("wipe-down", 400, d), show=p + ".name", bg=tg),
              img("P%d logo" % i, cx + 12, Y + 200, cw // 2 - 10, 170, "{%s.logo}" % p, A("fade", 400, d + 100), show=p + ".logo"),
              img("P%d photo" % i, cx + cw // 3, Y + 190, cw - cw // 3, 230, "{%s.photo}" % p, A("slide-up", 440, d + 140, dist=30), show=p + ".photo",
                  focus="center bottom"),
              box("P%d name bg" % i, cx, Y + 420, cw, 92, "#000000@0.5", A("fade", 300, d + 160), show=p + ".name"),
              box("P%d rule" % i, cx + 14, Y + 434, 4, 64, "{%s.color}" % p, A("grow-y", 240, d + 220), show=p + ".name"),
              txt("P%d first" % i, cx + 28, Y + 424, cw - 40, 32, "{%s.first|upper}" % p, 24, A("fade", 240, d + 240), show=p + ".name", font=F, weight=600),
              txt("P%d last" % i, cx + 26, Y + 450, cw - 40, 56, "{%s.last|upper}" % p, 48, A("reveal-up", 300, d + 240), show=p + ".name", font=F,
                  weight=800)]
        for j, (lab, val) in enumerate((("AVG", "{%s.avg|avg}" % p), ("HR", "{%s.hr|zero}" % p), ("RBI", "{%s.rbi|zero}" % p),
                                        ("TONIGHT", "{%s.hab}" % p))):
            y = Y + 520 + j * 58
            E += [txt("P%d %s" % (i, lab), cx + 22, y, cw // 2, 54, lab, 28, A("fade", 240, d + 300 + j * 50), show=p + ".name", font=F, weight=600),
                  txt("P%d %s v" % (i, lab), cx + cw // 2, y, cw // 2 - 22, 54, val, 44, A("fade", 240, d + 320 + j * 50), show=p + ".name", font=H,
                      weight=800, align="right"),
                  box("P%d line %d" % (i, j), cx + 22, y + 55, cw - 44, 2, "#FFFFFF@0.35", A("grow-x", 240, d + 320 + j * 50), show=p + ".name")]
    return {"name": "Top Performers", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def due_up():
    """Silver tile and navy "Due Up" bar with a blue strip, then the next three hitters side by side."""
    W = 1180
    X, Y = (1920 - W) // 2, 800
    E = [box("Tile", X, Y, 128, 82, None, A("pop", 420, 0, out=OUT_), bg=SILVER, radius=4)]
    E += logo_or_abbr("Logo", X + 14, Y + 6, 100, 70, "team", 30, A("zoom-out", 400, 160), color=INK, S=EB)
    E += [box("Head", X + 124, Y, W - 124, 82, None, A("wipe-right", 440, 120, out=OUT_), bg="linear-gradient(180deg, #0B1A36, #13284D)", radius=4),
          txt("Title", X + 150, Y, 400, 82, "DUE UP", 60, A("reveal-up", 360, 300), font=H, weight=800),
          txt("Team", X + 560, Y, W - 590, 82, "{team.name|upper}", 34, A("fade", 260, 400), font=F, weight=700, align="right", color=FIRST),
          box("Body", X, Y + 82, W, 96, None, A("wipe-down", 400, 260, out=OUT_), bg=NAVY, borderW=2, borderColor="#5AA9FF@0.6")]
    cw = W // 3
    for i in range(3):
        p = "team.dueUp.%d" % i
        x = X + i * cw
        d = 420 + i * 120
        E += [txt("Slot %d" % i, x + 10, Y + 82, 50, 96, "{%s.slot}" % p, 44, A("fade", 240, d), show=p + ".name", font=H, weight=800, color=FIRST,
                  align="center"),
              txt("First %d" % i, x + 66, Y + 88, cw - 80, 32, "{%s.first|upper}" % p, 26, A("fade", 240, d + 60), show=p + ".name", font=F, weight=600,
                  color=FIRST),
              txt("Last %d" % i, x + 64, Y + 114, cw - 80, 52, "{%s.last|upper}" % p, 46, A("reveal-up", 300, d + 60), show=p + ".name", font=F, weight=800),
              txt("Avg %d" % i, x + 66, Y + 88, cw - 80, 32, "{%s.avg|avg}" % p, 26, A("fade", 240, d + 100), show=p + ".name", font=F, weight=800,
                  align="right")]
        if i:
            E.append(box("Div %d" % i, x, Y + 100, 2, 60, "#5AA9FF@0.45", A("grow-y", 240, d)))
    return {"name": "Due Up", "group": "lower", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "half_{halfKey}, dueup"}


def standings():
    X, Y, W, Hb, RH = 360, 80, 1200, 820, 60
    E = frame("{standingsGroup.name|upper}", "{seasonYear} STANDINGS", logo="{league.logo}", logo_show="league.logo", X=X, W=W, Hb=Hb, title_size=70)
    for lab, x, w in (("W", 760, 100), ("L", 860, 100), ("PCT", 960, 120), ("GB", 1080, 100)):
        E.append(txt("Head " + lab, X + x, Y + 141, w, 46, lab, 28, A("fade", 240, 400), font=F, weight=800, align="center"))
    for i in range(10):
        p = "standingsGroup.teams.%d" % i
        y = Y + 196 + i * RH
        d = 420 + i * 60
        E += [box("Game %d" % i, X, y, 8, RH - 4, BLUE, A("grow-y", 240, d + 100), show=both(p + ".name", p + ".isGame")),
              txt("Rank %d" % i, X + 20, y, 50, RH - 4, "{%s.rank}" % p, 30, A("fade", 220, d), show=p + ".name", font=H, weight=800, color=FIRST,
                  align="center"),
              box("Tile %d" % i, X + 80, y + 4, 70, RH - 12, None, A("fade", 220, d + 40), show=both(p + ".name", p + ".logo"), bg=SILVER, radius=3),
              img("Logo %d" % i, X + 84, y + 7, 62, RH - 18, "{%s.logo}" % p, A("fade", 220, d + 80), show=both(p + ".name", p + ".logo")),
              txt("Team %d" % i, X + 170, y, 580, RH - 4, "{%s.name|upper}" % p, 36, A("slide-right", 300, d + 60, dist=20), show=p + ".name", font=F,
                  weight=800),
              box("Line %d" % i, X + 20, y + RH - 3, W - 40, 2, "#5AA9FF@0.4", A("grow-x", 260, d + 80), show=p + ".name")]
        for k, x, w in (("w", 760, 100), ("l", 860, 100), ("pct", 960, 120), ("gb", 1080, 100)):
            E.append(txt("%s %d" % (k, i), X + x, y, w, RH - 4, "{%s.%s}" % (p, k), 38, A("fade", 220, d + 100), show=p + ".name", font=H, weight=800,
                         align="center", color=FIRST if k == "gb" else "#FFFFFF"))
    return {"name": "Standings", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(EB, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("inning_sponsor", "lineup", "pitching", "defense", "linescore", "spotlight", "custom", "note", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g["batter_card"] = BL.stat_card_tonight(MS, "bat")
g["pitcher_card"] = BL.stat_card_tonight(MS, "pit")
g.update({"scorebug": scorebug(), "batter": lower("bat"), "pitcher": lower("pit"), "ticker": ticker(), "feature": feature(), "summary": summary(),
          "batter_tall": tall("bat"), "pitcher_tall": tall("pit"), "performers": performers(),
          "dueup": due_up(), "standings": standings()})
g.update(SL.all_sports(MS))

# ------------------------------------------------------------------ rebuild kit (shared graphics drawn with this style's chassis)
import rebuild as RB  # noqa: E402
TA = BL._tr_anim


def kit_transition(gid, g):
    """Deep navy field with diagonal lines, pattern bands framing a navy word band with blue rules."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=NAVY),
         box("Lines", 0, 0, 1920, 1080, None, TA("fade", 400, 80), bg="repeating-linear-gradient(135deg, rgba(255,255,255,0.03) 0 22px, transparent 22px 44px)"),
         box("Team edge", 0, 0, 34, 1080, "{team.color}", TA("grow-y", 360, 120)),
         box("Band top", 0, 300, 1920, 60, None, TA("wipe-right", 420, 120), bg=PATTERN),
         box("Rule top", 0, 360, 1920, 6, BLUE, TA("grow-x", 420, 180)),
         box("Word band", 0, 366, 1920, 348, None, TA("wipe-right", 420, 160), bg="linear-gradient(180deg, #0B1A36, #13284D)"),
         box("Rule bottom", 0, 714, 1920, 6, BLUE, TA("grow-x", 420, 220)),
         box("Band bottom", 0, 720, 1920, 60, None, TA("wipe-left", 420, 160), bg=PATTERN),
         box("Tile", 860, 120, 200, 150, None, TA("pop", 380, 220), bg=SILVER, radius=4)]
    return {"elements": E, "word": {"font": H, "weight": 800, "color": "#FFFFFF", "textShadow": "", "rect": (60, 386, 1800, 220)},
            "sub": {"font": F, "weight": 700, "color": FIRST, "textShadow": "", "rect": (60, 606, 1800, 90)},
            "brand": {"rect": (875, 135, 170, 120)}}


def kit_slab(R, slab, g):
    x, y, w, h = R
    return [box("Band top", 0, y - 44, 1920, 40, None, A("wipe-right", 320, 60), bg=PATTERN),
            box("Rule top", 0, y - 4, 1920, 4, BLUE, A("grow-x", 300, 100)),
            box("Rule bottom", 0, y + h, 1920, 4, BLUE, A("grow-x", 300, 140)),
            box("Band bottom", 0, y + h + 4, 1920, 40, None, A("wipe-left", 320, 60), bg=PATTERN)]

def kit_screen(bg, team, g):
    over = [box("Lines", 0, 0, 1920, 1080, None, A("fade", 500, 100), bg="repeating-linear-gradient(135deg, rgba(255,255,255,0.03) 0 22px, transparent 22px 44px)"),
            box("Band top", 0, 0, 1920, 40, None, A("wipe-right", 420, 80), bg=PATTERN),
            box("Rule top", 0, 40, 1920, 4, BLUE, A("grow-x", 420, 160)),
            box("Rule bottom", 0, 1036, 1920, 4, BLUE, A("grow-x", 420, 160)),
            box("Band bottom", 0, 1040, 1920, 40, None, A("wipe-left", 420, 80), bg=PATTERN)]
    return {"floor": "repeating-linear-gradient(90deg, #3D8EF0 0 150px, #2A63C2 150px 154px)", "replace": NAVY, "over": over}

KIT = RB.make_kit(dict(
    screen=kit_screen,
    slab=kit_slab,
    bands=PATTERN, bandLine=BLUE, body=NAVY, bodyBox={"shadow": EB["shadow"]},
    bodyOver="repeating-linear-gradient(135deg, rgba(255,255,255,0.025) 0 22px, transparent 22px 44px)",
    headTile=SILVER, head="linear-gradient(180deg, #0B1A36, #13284D)", headRule=BLUE, sub=BLUE_BAR,
    title={"font": H, "weight": 800, "color": "#FFFFFF", "textShadow": "", "italic": False},
    subText={"font": F, "weight": 700, "color": "#FFFFFF", "textShadow": ""},
    roles={"PANEL": NAVY, "PANEL2": NAVY2, "DARK": DEEP, "STRIP": BLUE_BAR}, barBox={"radius": 4},
    mainBox={"borderW": 2, "borderColor": "#5AA9FF@0.85", "shadow": EB["shadow"]}, teamMain=NAVY, teamStripe=5,
    tile={"background": SILVER, "radius": 4, "borderW": 0}, tileInk=INK,
    tr=lambda gid, g, TA: kit_transition(gid, g)))
CUSTOM = ("scorebug", "batter", "pitcher", "ticker", "feature", "summary", "batter_tall", "pitcher_tall", "performers", "dueup", "standings")
K = dict(panel=NAVY, panel2=NAVY2, dark=DEEP, strip=BLUE_BAR, stripText="#FFFFFF", stripDark=False, val=SILVER, ink=INK, hi=BLUE, hiText="#FFFFFF",
         line="#5AA9FF@0.45", title=EB["titleBg"], shadow=EB["shadow"], team=T, rule=BLUE, text2=FIRST, radius=4, noBlur=True,
         panelBox={"radius": 4, "borderW": 2, "borderColor": "#5AA9FF@0.6", "shadow": EB["shadow"]}, lightBox={"radius": 4},
         text={"textShadow": ""}, textDark={"textShadow": ""})
g = RB.rebuild_all(g, KIT, only=set(g) - set(CUSTOM))
g = RB.strip_flags(SK.skin_all(g, K, only=set(g) - set(CUSTOM)))
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
for k, d in g.items():
    if not d.get("layout") and "Empire Blue" not in d.get("name", ""):
        d["name"] = "%s (Empire Blue)" % d.get("name", k)

theme = dict(night_doc["theme"])
theme.update({"primary": "#0B1A36", "accent": BLUE, "text": "#FFFFFF", "dim": "rgba(214,224,240,0.78)", "line": "rgba(90,169,255,0.35)",
              "card": "rgba(14,32,66,0.94)", "panel": "rgba(14,32,66,0.94)", "panel2": "rgba(24,48,92,0.94)"})
doc = {"version": 2, "name": "Empire Blue",
       "description": "Navy and bright blue regional-network look: silver logo tiles, condensed names and numbers, heavy titles, a light "
                      "diagonal pattern band framing full screens, and team-colour stat panels. Every graphic type, plus basketball, football "
                      "and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "empire-blue.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
