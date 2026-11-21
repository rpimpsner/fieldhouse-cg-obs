"""Builds the "Caribbean League" package: templates/packages/caribbean-league.json.

Modelled on the Caribbean winter-league broadcast Rob sent: a wide top-left scorebug with a "Presented by" sponsor
strip, the two teams side by side in glossy team-colour blocks (challenge pips, logo, abbreviation, big score), a dark
block with the bases and the inning, and a strip underneath with the batter (order slot, name, average), the pitcher
with pitch count, the outs and the count; a lower third with the team-colour logo tile, position and number, first
name over a bold LAST, a white average box and a dark stat run with a season tab; and an R-H-E linescore bug with a
title strip and the inning underneath. Built around those: pitcher lower third, pitcher's line, batter vs pitcher,
due up, a sponsor bug and every other graphic type restyled in the same glossy black, silver and gold.
Run:  python tools/build_caribbean.py   (after tools/build_night_game.py)
"""
import theme_lib as TL
from theme_lib import A, box, img, el, logo_or_abbr, W, OUT_, LIVE, COND

WIDE = "'BBG Archivo Black', 'Arial Black', sans-serif"
GLOSS = "linear-gradient(180deg, #44474D 0%, #1C1D21 46%, #060607 54%, #1E2024 100%)"
GLOSS2 = "linear-gradient(180deg, #2C2E33 0%, #121316 50%, #0A0A0C 100%)"
WHITE = "linear-gradient(180deg, #FFFFFF 0%, #E9EBEE 55%, #CFD3D8 100%)"
SILVER = "#C9CDD3"
GOLD = "#E2B93B"
INK = "#0B0B0D"
SHADOW = "0 8px 22px rgba(0,0,0,.55)"


def tg(t):
    """Glossy team colour: a lighter band on top, the colour, a darker base."""
    return ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 62%%, #fff) 0%%, {%s.color} 44%%, color-mix(in srgb, {%s.color} 82%%, #000) 56%%, "
            "color-mix(in srgb, {%s.color} 92%%, #000) 100%%)") % (t, t, t, t)


def tink(t):
    """Text on a team-colour block: the team's second colour, else white."""
    return "#FFFFFF"


def pips(name, x, y, side, d):
    """Two small upright pips (challenges left) at the left of a team block."""
    E = []
    for i in range(2):
        E.append(box("%s pip %d" % (name, i + 1), x, y + i * 26, 9, 22, None, A("fade", 240, d), radius=5, borderW=2, borderColor="#FFFFFF@0.85",
                     bg="#FFFFFF", show="ops.chal.%s > %d" % (side, i)))
        E.append(box("%s pip %d off" % (name, i + 1), x, y + i * 26, 9, 22, None, A("fade", 240, d), radius=5, borderW=2, borderColor="#FFFFFF@0.6",
                     show="ops.chal.%s <= %d" % (side, i)))
    return E


# ------------------------------------------------------------------ scorebug
def scorebug(T):
    X, Y = 52, 40
    TB, TW, RH, SB = 30, 238, 74, 34          # title strip, team block, row, sub strip
    BW = 230                                   # bases / inning block
    Wd = 2 * TW + BW
    E = [box("Title", X, Y, Wd, TB, None, A("wipe-right", 380, 0, out=OUT_), bg=GLOSS, borderW=1, borderColor=SILVER + "@0.6", radius="3px 3px 0 0"),
         W(T, "Title sponsor", X, Y, Wd, TB, "Presented by {sponsor.name}", 21, A("fade", 260, 200, change="fade"), show="sponsor.on",
           align="center", weight=600),
         W(T, "Title text", X, Y, Wd, TB, "{notes.bugTitle}", 21, A("fade", 260, 200), show="!sponsor.on && notes.bugTitle", align="center",
           weight=600),
         W(T, "Title default", X, Y, Wd, TB, "{league.name}", 21, A("fade", 260, 200), show="!sponsor.on && !notes.bugTitle",
           align="center", weight=600),
         box("Frame", X, Y + TB, Wd, RH + SB + 2, None, A("wipe-right", 420, 60, out=OUT_), bg=GLOSS, borderW=2, borderColor=SILVER, shadow=SHADOW)]
    y = Y + TB + 2
    for i, side in enumerate(("away", "home")):
        x = X + 2 + i * TW
        d = 160 + i * 90
        E += [box("%s block" % side, x, y, TW - 2, RH - 2, None, A("wipe-right", 360, d), bg=tg(side))]
        E += pips(side, x + 8, y + 12, side, d + 120)
        E += logo_or_abbr("%s logo" % side, x + 24, y + 8, 62, RH - 18, side, 22, A("fade", 260, d + 120), S={"font": WIDE})
        E += [W(T, "%s abbr" % side, x + 88, y, 76, RH - 2, "{%s.abbr|upper}" % side, 26, A("fade", 260, d + 140), font=WIDE, weight=400, color=tink(side)),
              box("%s score bg" % side, x + 166, y + 4, TW - 172, RH - 10, None, A("fade", 260, d + 80),
                  bg="linear-gradient(180deg, color-mix(in srgb, {%s.color} 70%%, #fff), color-mix(in srgb, {%s.color} 85%%, #000))" % (side, side),
                  radius=4),
              W(T, "%s runs" % side, x + 166, y + 2, TW - 172, RH - 6, "{%s.runs}" % side, 50, A("reveal-up", 300, d + 180, change="pop"), align="center",
                font=WIDE, weight=400, color=tink(side), textShadow="0 2px 4px rgba(0,0,0,.35)")]
    bx = X + 2 * TW
    E += [el("bases", "Bases", bx + 18, y + 6, 120, RH - 14, A("pop", 320, 420), show=LIVE, bind="bases",
             style={"layout": "tight", "on": "#FFFFFF", "off": "#FFFFFF@0.16", "stroke": "#FFFFFF@0.9", "strokeW": 2}),
          W(T, "Inning", bx + 140, y, 84, RH - 2, "{inning}{arrow}", 38, A("fade", 260, 460, change="roll"), show=LIVE, align="center", font=WIDE, weight=400),
          W(T, "Status", bx, y, BW - 4, RH - 2, "{statusText|upper}", 24, A("fade", 260, 420), show="!" + LIVE, align="center", font=WIDE, weight=400,
            wrap=True, fit=False)]
    sy = y + RH
    E += [box("Sub", X + 2, sy, Wd - 4, SB, None, A("wipe-down", 300, 500, out=OUT_), bg=GLOSS2)]
    for i, side in enumerate(("away", "home")):
        x = X + 2 + i * TW
        bat = "half==top" if side == "away" else "half==bottom"
        fld = "half==bottom" if side == "away" else "half==top"
        d = 600 + i * 60
        E += [box("%s sub rule" % side, x + TW - 3, sy + 4, 2, SB - 8, SILVER + "@0.5", A("fade", 200, d)),
              box("%s slot bg" % side, x + 6, sy + 5, 24, SB - 10, "#FFFFFF", A("pop", 240, d), show=LIVE + " && " + bat, radius=2),
              W(T, "%s slot" % side, x + 6, sy + 5, 24, SB - 10, "{batter.slot}", 18, A("fade", 200, d + 60), show=LIVE + " && " + bat, align="center",
                color=INK, font=WIDE, weight=400),
              W(T, "%s batter" % side, x + 36, sy, 130, SB, "{batter.last|upper}", 20, A("fade", 240, d + 80, change="fade"), show=LIVE + " && " + bat,
                font=WIDE, weight=400),
              W(T, "%s avg" % side, x + 160, sy, TW - 172, SB, "{batter.season.avg|avg}", 19, A("fade", 240, d + 100, change="fade"),
                show=LIVE + " && " + bat, align="right", weight=700),
              W(T, "%s pitcher" % side, x + 8, sy, 140, SB, "{pitcher.last|upper}", 20, A("fade", 240, d + 80, change="fade"), show=LIVE + " && " + fld,
                font=WIDE, weight=400),
              W(T, "%s pc" % side, x + 146, sy, TW - 158, SB, "P: {pitcher.today.pc|zero}", 19, A("fade", 240, d + 100, change="flash"),
                show=LIVE + " && " + fld, align="right", weight=700)]
    bx = X + 2 * TW
    E += [el("dots", "Outs", bx + 14, sy + 8, 80, SB - 16, A("fade", 240, 700), show=LIVE, bind="outs",
             style={"total": 2, "size": 13, "gap": 8, "on": GOLD, "off": "#FFFFFF@0.22", "shape": "circle", "align": "left"}),
          W(T, "Count", bx + 96, sy, BW - 110, SB, "{balls}-{strikes}", 24, A("fade", 240, 720, change="flash"), show=LIVE, align="right", font=WIDE,
            weight=400)]
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(T, kind):
    """Logo tile, position and number, first over LAST, white headline-stat box, dark stat run, season tab on top."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    big = ("ERA", "{pitcher.season.era|era}") if kind == "pit" else ("AVG", "{batter.season.avg|avg}")
    rest = ([("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"), ("K", "{pitcher.season.k|zero}")]
            if kind == "pit" else [("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}"), ("OBP", "{batter.season.obp|avg}")])
    X, Y, Hh = 330, 880, 96
    LT, NM, BB, SR = 210, 360, 190, 470
    Wd = LT + NM + BB + SR
    E = [box("Tab", X + Wd - 380, Y - 30, 380, 30, None, A("wipe-up", 300, 500, out=OUT_), bg=WHITE, borderW=2, borderColor=INK),
         W(T, "Tab text", X + Wd - 380, Y - 30, 380, 30, "{notes.tab|upper}", 19, A("fade", 240, 600), show="notes.tab", align="center", color=INK, font=WIDE,
           weight=400),
         W(T, "Tab default", X + Wd - 380, Y - 30, 380, 30, "REGULAR SEASON {seasonYear}", 19, A("fade", 240, 600), show="!notes.tab", align="center",
           color=INK, font=WIDE, weight=400),
         box("Tile", X, Y, LT, Hh, None, A("wipe-right", 340, 0, out=OUT_), bg=tg(team), borderW=2, borderColor=SILVER, shadow=SHADOW)]
    E += logo_or_abbr("Logo", X + 30, Y + 8, LT - 60, Hh - 16, team, 34, A("zoom-out", 360, 160), S={"font": WIDE})
    x = X + LT
    E += [box("Name", x, Y, NM, Hh, None, A("wipe-right", 380, 100, out=OUT_), bg=GLOSS, borderW=2, borderColor=SILVER),
          box("Pos bg", x + 8, Y + 8, 58, 38, None, A("pop", 260, 300), bg=WHITE, radius=2),
          W(T, "Pos", x + 8, Y + 8, 58, 38, "{%s.pos}" % who if kind == "bat" else "{pitcher.throws|hand}", 24, A("fade", 200, 360), align="center", color=INK,
            font=WIDE, weight=400),
          W(T, "Number", x + 6, Y + 50, 62, 42, "{%s.number}" % who, 32, A("fade", 240, 380), align="center", color="#D5D8DD", font=WIDE, weight=400),
          W(T, "First", x + 78, Y + 6, NM - 88, 36, "{%s.first|upper}" % who, 30, A("fade", 260, 380), font=COND, weight=600),
          W(T, "Last", x + 76, Y + 40, NM - 86, 52, "{%s.last|upper}" % who, 44, A("reveal-up", 320, 360), font=WIDE, weight=400)]
    x += NM
    E += [box("Rule", x, Y, 4, Hh, GOLD, A("grow-y", 260, 300)),
          box("Big", x + 4, Y, BB, Hh, None, A("wipe-right", 360, 200, out=OUT_), bg=WHITE, borderW=2, borderColor=SILVER),
          W(T, "Big label", x + 16, Y + 6, BB - 24, 26, big[0], 21, A("fade", 240, 420), color="#3A3D42", weight=700),
          W(T, "Big value", x + 4, Y + 28, BB, 64, big[1], 56, A("reveal-up", 300, 440, change="flash"), align="center", color=INK, font=WIDE, weight=400)]
    x += BB + 4
    E += [box("Run", x, Y, SR, Hh, None, A("wipe-right", 400, 260, out=OUT_), bg=GLOSS, borderW=2, borderColor=SILVER, shadow=SHADOW)]
    cw = SR // 3
    for i, (lab, val) in enumerate(rest):
        cx = x + i * cw
        E += [W(T, "%s label" % lab, cx + 14, Y, 66, Hh, lab, 22, A("fade", 240, 480 + i * 60), weight=700, color="#D5D8DD", align="right"),
              W(T, "%s value" % lab, cx + 84, Y, cw - 92, Hh, val, 38, A("reveal-up", 300, 500 + i * 60, change="flash"), font=WIDE, weight=400)]
    E += TL.BL.sponsor_tab(X + LT, Y - 46, 300, 42, 640, radius=2, a_type="wipe-up")
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def rhe_bug(T):
    """R-H-E linescore bug: title strip, a glossy team row each with logo and NAME, white R H E, the inning underneath."""
    X, Y, Wd = 118, 776, 472
    TB, RH, FB = 34, 88, 36
    TWd = 216
    E = [box("Gold top", X, Y, Wd, 3, GOLD, A("grow-x", 300, 0)),
         box("Title", X, Y + 3, Wd, TB, None, A("wipe-right", 360, 0, out=OUT_), bg=GLOSS),
         W(T, "Title text", X, Y + 3, Wd, TB, "{notes.tab|upper}", 22, A("fade", 240, 160), show="notes.tab", align="center", font=WIDE, weight=400),
         W(T, "Title default", X, Y + 3, Wd, TB, "REGULAR SEASON {seasonYear}", 22, A("fade", 240, 160), show="!notes.tab", align="center", font=WIDE,
           weight=400),
         box("Body", X, Y + 3 + TB, Wd, 2 * RH, None, A("wipe-right", 400, 80, out=OUT_), bg=GLOSS2, borderW=2, borderColor=SILVER + "@0.6", shadow=SHADOW)]
    hx = X + TWd + 8
    cw = (Wd - TWd - 16) // 3
    for i, side in enumerate(("away", "home")):
        y = Y + 3 + TB + i * RH
        d = 200 + i * 100
        E += [box("%s block" % side, X + 2, y + 2, TWd, RH - 4, None, A("wipe-right", 340, d), bg=tg(side))]
        E += logo_or_abbr("%s logo" % side, X + 10, y + 8, 76, RH - 16, side, 22, A("fade", 240, d + 100), S={"font": WIDE})
        E += [W(T, "%s name" % side, X + 88, y + 2, TWd - 94, RH - 4, "{%s.nick|upper}" % side, 26, A("fade", 240, d + 120), font=WIDE, weight=400,
                align="center")]
        for j, key in enumerate(("runs", "hits", "errors")):
            E += [W(T, "%s %s" % (side, key), hx + j * cw, y, cw, RH, "{%s.%s}" % (side, key), 64, A("reveal-up", 300, d + 160 + j * 60, change="pop"),
                    align="center", font=WIDE, weight=400)]
    fy = Y + 3 + TB + 2 * RH
    E += [box("Foot", X, fy, Wd, FB, None, A("wipe-down", 300, 400, out=OUT_), bg=GLOSS),
          W(T, "Inning", X, fy, Wd, FB, "{statusText|upper}", 24, A("fade", 240, 520), align="center", font=WIDE, weight=400),
          box("Gold bottom", X, fy + FB, Wd, 3, GOLD, A("grow-x", 300, 500))]
    return {"name": "Linescore R-H-E", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "scorebug"}


def bar(T, name, title, cells, team="batting", sub=None, auto=9, group="lower"):
    """A one-line bar in the same look: team tile with logo, a white title box, a dark run of label / value cells."""
    X, Y, Hh = 330, 900, 80
    LT, TT = 150, 300
    run = 120 * len(cells) + 40
    E = [box("Tile", X, Y, LT, Hh, None, A("wipe-right", 320, 0, out=OUT_), bg=tg(team), borderW=2, borderColor=SILVER, shadow=SHADOW)]
    E += logo_or_abbr("Logo", X + 20, Y + 8, LT - 40, Hh - 16, team, 28, A("zoom-out", 340, 160), S={"font": WIDE})
    E += [box("Title", X + LT, Y, TT, Hh, None, A("wipe-right", 340, 100, out=OUT_), bg=WHITE, borderW=2, borderColor=SILVER),
          W(T, "Title text", X + LT + 12, Y + (4 if sub else 0), TT - 24, 44 if sub else Hh, title, 30, A("fade", 240, 260), color=INK, font=WIDE, weight=400),
          box("Rule", X + LT + TT, Y, 4, Hh, GOLD, A("grow-y", 260, 300)),
          box("Run", X + LT + TT + 4, Y, run, Hh, None, A("wipe-right", 380, 200, out=OUT_), bg=GLOSS, borderW=2, borderColor=SILVER, shadow=SHADOW)]
    if sub:
        E += [W(T, "Sub", X + LT + 12, Y + 44, TT - 24, 32, sub, 20, A("fade", 240, 320), color="#3A3D42", weight=700)]
    x = X + LT + TT + 24
    for i, (lab, val) in enumerate(cells):
        E += [W(T, "%s label" % lab, x + i * 120, Y + 4, 110, 26, lab, 19, A("fade", 240, 420 + i * 50), weight=700, color="#D5D8DD", align="center"),
              W(T, "%s value" % lab, x + i * 120, Y + 28, 110, 48, val, 36, A("reveal-up", 300, 440 + i * 50, change="flash"), font=WIDE, weight=400,
                align="center")]
    return {"name": name, "group": group, "autoHide": auto, "side": "", "sided": False, "elements": E}


def due_up(T):
    X, Y, Hh = 330, 900, 80
    E = [box("Label", X, Y, 200, Hh, None, A("wipe-right", 320, 0, out=OUT_), bg=WHITE, borderW=2, borderColor=SILVER),
         W(T, "Label text", X, Y, 200, Hh, "DUE UP", 32, A("fade", 240, 200), color=INK, font=WIDE, weight=400, align="center"),
         box("Rule", X + 200, Y, 4, Hh, GOLD, A("grow-y", 260, 260))]
    for i in range(3):
        p = "team.dueUp.%d" % i
        x = X + 204 + i * 360
        d = 300 + i * 120
        E += [box("Batter %d" % (i + 1), x, Y, 356, Hh, None, A("wipe-right", 340, d, out=OUT_), bg=tg("team") if i == 0 else GLOSS, borderW=2,
                  borderColor=SILVER, show=p + ".name"),
              W(T, "Slot %d" % (i + 1), x + 10, Y, 50, Hh, "{%s.slot}" % p, 34, A("fade", 240, d + 100), show=p + ".name", font=WIDE, weight=400, align="center",
                color=GOLD if i else "#FFFFFF"),
              W(T, "Name %d" % (i + 1), x + 64, Y + 4, 280, 44, "{%s.last|upper}" % p, 32, A("reveal-up", 300, d + 120), show=p + ".name", font=WIDE, weight=400),
              W(T, "Line %d" % (i + 1), x + 66, Y + 46, 280, 30, "{%s.pos}  {%s.avg|avg}" % (p, p), 20, A("fade", 240, d + 160), show=p + ".name", weight=700,
                color="#D5D8DD")]
    return {"name": "Due Up Bar", "group": "lower", "autoHide": 8, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "half_{halfKey}, dueup"}


def sponsor_bug(T):
    X, Y, Wd = 52, 40, 706
    E = [box("Strip", X, Y, Wd, 30, None, A("wipe-right", 360, 0, out=OUT_), bg=GLOSS, borderW=1, borderColor=SILVER + "@0.6"),
         W(T, "Presented", X, Y, Wd, 30, "{sponsor.label}", 20, A("fade", 240, 160), show="sponsor.label", align="center", weight=600),
         W(T, "Presented default", X, Y, Wd, 30, "Presented by", 20, A("fade", 240, 160), show="!sponsor.label", align="center", weight=600),
         box("Plate", X, Y + 30, Wd, 120, None, A("wipe-right", 400, 80, out=OUT_), bg=WHITE, borderW=2, borderColor=SILVER, shadow=SHADOW),
         img("Logo", X + 40, Y + 40, Wd - 80, 100, "{sponsor.logo}", A("fade", 300, 300, change="fade"), show="sponsor.on && sponsor.logo"),
         W(T, "Name", X + 20, Y + 30, Wd - 40, 120, "{sponsor.name}", 54, A("fade", 300, 300, change="fade"), show="sponsor.on && !sponsor.logo", align="center",
           color=INK, font=WIDE, weight=400),
         box("Gold", X, Y + 150, Wd, 3, GOLD, A("grow-x", 300, 400))]
    return {"name": "Sponsor Bug", "group": "bug2", "autoHide": 12, "side": "", "sided": False, "elements": E, "sponsorSlot": "scorebug, show"}


def override(T):
    return {"scorebug": scorebug(T), "batter": lower(T, "bat"), "pitcher": lower(T, "pit")}


def extras(T):
    return {
        "rhe": rhe_bug(T),
        "pitcher_line": bar(T, "Pitcher's Line Today", "{pitcher.last|upper}", [("IP", "{pitcher.today.ip|dash}"), ("H", "{pitcher.today.h|zero}"),
                            ("R", "{pitcher.today.r|zero}"), ("ER", "{pitcher.today.er|zero}"), ("BB", "{pitcher.today.bb|zero}"),
                            ("K", "{pitcher.today.k|zero}"), ("P", "{pitcher.today.pc|zero}")], team="fielding", sub="TODAY"),
        "batter_today": bar(T, "Batter Today", "{batter.last|upper}", [("TODAY", "{batter.today.hab}"), ("AVG", "{batter.season.avg|avg}"),
                            ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}")], team="batting", sub="{batter.today.line}"),
        "matchup": bar(T, "Batter vs Pitcher", "{batter.last|upper}", [("VS", "{pitcher.last|upper}"), ("AVG", "{batter.season.avg|avg}"),
                       ("ERA", "{pitcher.season.era|era}"), ("P", "{pitcher.today.pc|zero}")], team="batting", sub="AT BAT"),
        "dueup": due_up(T),
        "sponsor": sponsor_bug(T),
    }


TT = TL.defaults(dict(
    key="carib", file="caribbean-league", name="Caribbean League", font=WIDE, font2=COND, deco=WIDE, upper=True,
    desc="Caribbean winter-league TV look: glossy black and silver with gold rules, glossy team-colour blocks. A wide scorebug with a Presented by "
         "sponsor strip, side-by-side teams with challenge pips, bases and inning, and a strip with the batter's slot, name and average, the "
         "pitcher's pitch count, outs and count. Lower thirds with a white headline-stat box and a season tab, an R-H-E linescore bug, the "
         "pitcher's line, batter today, batter vs pitcher, due up and a sponsor bug. Every graphic type, plus basketball, football and hockey.",
    bg="#060607", panel=GLOSS2, panel2="linear-gradient(180deg, #34363C, #1A1B1F)", dark="#0A0A0C", head=GLOSS, strip=WHITE, stripText=INK, val=WHITE,
    valText=INK, hi=GOLD, hiText=INK, edge=SILVER + "@0.7", tile_border=SILVER, r=2, title="radial-gradient(ellipse at 50% 35%, #2C2E33, #060607 70%)",
    texture="", title_color="#FFFFFF", rule=GOLD, team=tg, shadow=SHADOW, base_on="#FFFFFF", base_off="#FFFFFF@0.16", hr_word="HOME RUN",
    hr_band=GLOSS, open_kicker="{seasonYear}", override=override, extras=extras))

if __name__ == "__main__":
    TL.build(TT)
