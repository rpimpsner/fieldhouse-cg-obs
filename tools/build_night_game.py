"""Builds the "Night Game" package: templates/packages/night-game.json, also used as templates/default.json.

Layouts and motion are modeled on the reference frames: clean rounded translucent cards with thin
divider rows and an accent rule, kinetic "Due Up" type that resolves into a player card, a split-screen
matchup, a three-panel player spotlight, a diamond transition, and four scorebug layouts drawn from
current network bugs. All marks are your own: team logos, photos and backgrounds come from data or
the media/ folder. Run:  python tools/build_night_game.py
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "templates", "packages", "night-game.json")
DEFAULT = os.path.join(ROOT, "templates", "default.json")
_n = [0]


def nid(p):
    _n[0] += 1
    return "%s_%d" % (p, _n[0])


def A(t="fade", dur=400, delay=0, ease="out", dist=None, out=None, rows=None, change=None, origin=None, hold=None, loop=None, stagger=None):
    a = {"in": {"type": t, "dur": dur, "delay": delay, "ease": ease}}
    if dist is not None:
        a["in"]["dist"] = dist
    if origin:
        a["in"]["origin"] = origin
    if stagger is not None:
        a["in"]["stagger"] = stagger
    a["out"] = out or {"type": "fade", "dur": 220, "delay": 0, "ease": "in"}
    if rows:
        a["rows"] = rows
    if change:
        a["change"] = change
    if hold:
        a["hold"] = hold
    if loop:
        a["loop"] = loop
    return a


FADE_OUT = {"type": "fade", "dur": 220, "delay": 0, "ease": "in"}


def box(name, x, y, w, h, fill=None, a=None, show=None, bg=None, **st):
    s = {}
    if fill is not None:
        s["fill"] = fill
    if bg:
        s["background"] = bg
    s.update(st)
    e = {"id": nid("box"), "name": name, "type": "box", "x": x, "y": y, "w": w, "h": h, "style": s, "anim": a or A()}
    if show:
        e["showIf"] = show
    return e


def txt(name, x, y, w, h, text, size=32, a=None, show=None, **st):
    s = {"color": "$text", "size": size, "weight": 700, "align": "left", "valign": "center", "padX": 0, "fit": True}
    s.update(st)
    e = {"id": nid("txt"), "name": name, "type": "text", "x": x, "y": y, "w": w, "h": h, "text": text, "style": s, "anim": a or A()}
    if show:
        e["showIf"] = show
    return e


def img(name, x, y, w, h, src, a=None, show=None, **st):
    s = {"fit": "contain", "focus": "center"}
    s.update(st)
    e = {"id": nid("img"), "name": name, "type": "image", "x": x, "y": y, "w": w, "h": h, "src": src, "style": s, "anim": a or A()}
    if show:
        e["showIf"] = show
    return e


def el(kind, name, x, y, w, h, a=None, show=None, **kw):
    e = {"id": nid(kind), "name": name, "type": kind, "x": x, "y": y, "w": w, "h": h, "anim": a or A()}
    e.update(kw)
    if show:
        e["showIf"] = show
    return e


def logo_or_abbr(name, x, y, w, h, team, size, a, show=None, color="$text"):
    """Team logo when one is available, otherwise the abbreviation in the same box."""
    s1 = "%s.logo" % team + (" && " + show if show else "")
    s2 = "!%s.logo" % team + (" && " + show if show else "")
    return [img(name + " logo", x, y, w, h, "{%s.logo}" % team, a, show=s1),
            txt(name + " abbr", x, y, w, h, "{%s.abbr}" % team, size, a, show=s2, align="center", weight=800, color=color)]


def sponsor_tab(x, y, w, h, delay, style="light", radius=10, a_type="wipe-up", label_w=None, slot_note=""):
    """Sponsor block: label ("Presented by") + logo, or the sponsor name when no logo is set.
    Every layer shows only when the graphic's sponsor slot has an active sponsor."""
    light = style == "light"
    fill = "#FFFFFF@0.96" if light else "$card"
    if style == "silver":
        fill = None
    lc = "#5A6270" if style != "dark" else "$dim"
    nc = "#16181C" if style != "dark" else "$text"
    lw = label_w or int(w * 0.42)
    pad = max(8, int(h * 0.14))
    on = "sponsor.on"
    out = {"type": "fade", "dur": 220, "delay": 0, "ease": "in"}
    layers = [box("Sponsor bg", x, y, w, h, fill, A(a_type, 360, delay, out=out), show=on, radius=radius,
                  bg="linear-gradient(180deg, #F7F8FA, #D7DCE2)" if style == "silver" else None, shadow=True)]
    layers += [
        txt("Sponsor label", x + pad, y, lw - pad, h, "{sponsor.label}", min(22, max(12, int(h * 0.32))), A("fade", 260, delay + 180, out=out),
            show=on + " && sponsor.label", weight=600, color=lc, fit=True),
        img("Sponsor logo", x + lw, y + pad, w - lw - pad, h - 2 * pad, "{sponsor.logo}", A("fade", 300, delay + 220, out=out, change="fade"),
            show=on + " && sponsor.logo && sponsor.label"),
        img("Sponsor logo (no label)", x + pad, y + pad, w - 2 * pad, h - 2 * pad, "{sponsor.logo}", A("fade", 300, delay + 220, out=out, change="fade"),
            show=on + " && sponsor.logo && !sponsor.label"),
        txt("Sponsor name", x + lw, y, w - lw - pad, h, "{sponsor.name}", max(14, int(h * 0.42)), A("fade", 260, delay + 220, out=out, change="fade"),
            show=on + " && !sponsor.logo && sponsor.label", weight=800, color=nc, align="right"),
        txt("Sponsor name (no label)", x + pad, y, w - 2 * pad, h, "{sponsor.name}", max(14, int(h * 0.42)), A("fade", 260, delay + 220, out=out, change="fade"),
            show=on + " && !sponsor.logo && !sponsor.label", weight=800, color=nc, align="center"),
    ]
    return layers


LIVE = "inPlay"

# ===================================================================== SCOREBUGS
# 1. Stacked (two team rows, diamond, inning, count + pitches)
X, Y = 1300, 930
bug_stack = {"name": "Scorebug: Stacked", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": [
    box("Panel", X, Y, 566, 104, "$card", A("wipe-right", 520, 0, out={"type": "wipe-left", "dur": 360, "delay": 140, "ease": "in"}), radius=8, shadow=True, blur=14),
]}
for i, side in enumerate(("away", "home")):
    yy = Y + i * 52
    bug_stack["elements"] += [
        box("%s color" % side, X, yy, 8, 52, "{%s.color}" % side, A("grow-y", 260, 160 + i * 60, origin="center top")),
        img("%s logo" % side.title(), X + 18, yy + 7, 38, 38, "{%s.logo}" % side, A("fade", 260, 240 + i * 60), show="%s.logo" % side),
    ] + [
        txt("%s abbr" % side.title(), X + 66, yy, 112, 52, "{%s.abbr}" % side, 30, A("reveal-up", 340, 260 + i * 60), weight=800),
        txt("%s runs" % side.title(), X + 168, yy, 66, 52, "{%s.runs}" % side, 34, A("reveal-up", 340, 300 + i * 60, change="pop"), weight=800, align="right"),
    ]
bug_stack["elements"] += [
    box("Row line", X + 8, Y + 51, 236, 2, "$line", A("grow-x", 300, 240)),
    box("Divider", X + 246, Y + 12, 2, 80, "$line", A("grow-y", 260, 280)),
    el("bases", "Bases", X + 252, Y + 8, 112, 62, A("pop", 420, 380), show=LIVE, bind="bases",
       style={"layout": "tight", "on": "$accent", "off": "#FFFFFF@0.16", "stroke": "#FFFFFF@0.55", "strokeW": 2}),
    el("dots", "Outs", X + 262, Y + 72, 92, 24, A("fade", 260, 440), show=LIVE, bind="outs",
       style={"total": 2, "size": 13, "gap": 9, "on": "$accent", "off": "#FFFFFF@0.22", "align": "center"}),
    txt("Arrow", X + 364, Y + 12, 70, 28, "{arrow}", 18, A("fade", 260, 420), show=LIVE + " && arrow", align="center", color="$accent"),
    txt("Inning", X + 364, Y + 38, 70, 52, "{inning}", 36, A("reveal-up", 340, 420, change="flash"), show=LIVE, align="center", weight=800),
    txt("Mid/End", X + 364, Y + 12, 70, 28, "{halfShort}", 16, A("fade", 260, 420), show=LIVE + " && !arrow", align="center", color="$accent", weight=800),
    box("Divider 2", X + 436, Y + 12, 2, 80, "$line", A("grow-y", 260, 320)),
    txt("Count", X + 440, Y + 6, 126, 58, "{count}", 34, A("reveal-up", 340, 480, change="roll"), show=LIVE, align="center", weight=800),
    txt("Pitches", X + 440, Y + 62, 126, 32, "P-S {pitcher.today.pc|zero}-{pitcher.today.st|zero}", 14, A("fade", 260, 540, change="flash"), show=LIVE + " && pitcher.last",
        align="center", color="$dim", weight=700, tracking=1),
    txt("Final", X + 252, Y, 314, 104, "{statusText}", 34, A("fade", 300, 380), show="isFinal || isPre", align="center", weight=800, tracking=2),
] + sponsor_tab(X, Y - 52, 566, 46, 520, radius=8)

# 2. Broadcast bar (team blocks with pitcher / batter sub-row, diamond, count)
X, Y = 56, 40
bug_bar = {"name": "Scorebug: Broadcast Bar", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": []}
for i, side in enumerate(("away", "home")):
    bx = X + i * 304
    d = 80 * i
    bug_bar["elements"] += [
        box("%s block" % side.title(), bx, Y, 300, 64, None, A("wipe-down", 380, d), bg="linear-gradient(180deg, {%s.color}, color-mix(in srgb, {%s.color} 70%%, #000))" % (side, side)),
        img("%s logo" % side.title(), bx + 10, Y + 8, 52, 48, "{%s.logo}" % side, A("pop", 380, 220 + d), show="%s.logo" % side),
    ] + [
        txt("%s abbr" % side.title(), bx + 70, Y, 140, 64, "{%s.abbr}" % side, 36, A("reveal-up", 320, 240 + d), weight=800, font="$font2", textShadow=True),
        box("%s score bg" % side.title(), bx + 214, Y, 86, 64, "#000000@0.28", A("fade", 300, 200 + d)),
        txt("%s runs" % side.title(), bx + 214, Y, 86, 64, "{%s.runs}" % side, 44, A("reveal-up", 320, 300 + d, change="pop"), weight=800, align="center", font="$font2"),
        box("%s sub" % side.title(), bx, Y + 64, 300, 38, "$card", A("wipe-down", 300, 320 + d)),
        # Fielding team shows the pitcher and pitch count; batting team shows the batter and today's line.
        txt("%s pitcher" % side.title(), bx + 12, Y + 64, 200, 38, "{pitcher.last|upper}", 21, A("fade", 260, 460 + d),
            show="fieldingSide==%s && pitcher.last && %s" % (side, LIVE), weight=700, font="$font2"),
        txt("%s pc" % side.title(), bx + 196, Y + 64, 94, 38, "P-S {pitcher.today.pc|zero}-{pitcher.today.st|zero}", 21, A("fade", 260, 480 + d, change="flash"),
            show="fieldingSide==%s && pitcher.last && %s" % (side, LIVE), align="right", color="$accent", weight=800, font="$font2"),
        txt("%s batter" % side.title(), bx + 12, Y + 64, 210, 38, "{batter.slot|dot}{batter.last|upper}", 21, A("fade", 260, 460 + d),
            show="battingSide==%s && batter.last && %s" % (side, LIVE), weight=700, font="$font2"),
        txt("%s line" % side.title(), bx + 214, Y + 64, 76, 38, "{batter.today.hab}", 21, A("fade", 260, 480 + d, change="flash"),
            show="battingSide==%s && batter.last && %s" % (side, LIVE), align="right", weight=800, font="$font2"),
        txt("%s record" % side.title(), bx + 12, Y + 64, 278, 38, "{%s.record}" % side, 20, A("fade", 260, 460 + d),
            show="!inPlay", weight=700, color="$dim", font="$font2"),
    ]
bug_bar["elements"] += [
    box("Situation", X + 608, Y, 160, 102, "$card", A("wipe-right", 380, 160)),
    el("bases", "Bases", X + 618, Y + 4, 140, 60, A("pop", 420, 360), show=LIVE, bind="bases",
       style={"layout": "tight", "on": "#FFD447", "off": "#FFFFFF@0.15", "stroke": "#FFFFFF@0.5", "strokeW": 2}),
    txt("Inning", X + 612, Y + 64, 72, 36, "{arrow}{inning}", 24, A("fade", 260, 420, change="flash"), show=LIVE, align="center", weight=800, font="$font2"),
    el("dots", "Outs", X + 686, Y + 66, 76, 32, A("fade", 260, 460), show=LIVE, bind="outs",
       style={"total": 2, "size": 14, "gap": 8, "on": "#FFFFFF", "off": "#FFFFFF@0.22", "align": "center"}),
    box("Count bg", X + 772, Y, 112, 102, "$card", A("wipe-right", 380, 240)),
    txt("Count", X + 772, Y, 112, 102, "{count}", 38, A("reveal-up", 340, 460, change="roll"), show=LIVE, align="center", weight=800, font="$font2"),
    txt("Final", X + 612, Y, 268, 102, "{statusText}", 34, A("fade", 300, 380), show="!inPlay", align="center", weight=800, tracking=2, font="$font2"),
] + sponsor_tab(X, Y + 106, 604, 46, 520, radius=4, a_type="wipe-down")

# 3. Center diamond (score, team, diamond, team, score + count / outs strip)
CX, Y = 960, 942
bug_diamond = {"name": "Scorebug: Center Diamond", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": [
    box("Away block", CX - 330, Y, 270, 74, None, A("wipe-left", 420, 200, origin="right center"), bg="linear-gradient(90deg, color-mix(in srgb, {away.color} 75%, #000), {away.color})"),
    txt("Away runs", CX - 330, Y, 86, 74, "{away.runs}", 46, A("reveal-up", 320, 480, change="pop"), align="center", weight=800, font="$font2"),
    box("Home block", CX + 60, Y, 270, 74, None, A("wipe-right", 420, 200), bg="linear-gradient(90deg, {home.color}, color-mix(in srgb, {home.color} 75%, #000))"),
    txt("Home runs", CX + 244, Y, 86, 74, "{home.runs}", 46, A("reveal-up", 320, 480, change="pop"), align="center", weight=800, font="$font2"),
    box("Strip", CX - 300, Y + 74, 600, 40, "#000000@0.82", A("wipe-center", 380, 380), radius=4),
    txt("Count", CX - 280, Y + 74, 220, 40, "{count}", 26, A("fade", 260, 560, change="roll"), show=LIVE, weight=800, font="$font2"),
    txt("Outs", CX + 60, Y + 74, 220, 40, "{outs} {outsWord}", 26, A("fade", 260, 580, change="flash"), show=LIVE, align="right", weight=800, font="$font2"),
    txt("Final", CX - 280, Y + 74, 560, 40, "{statusText}", 24, A("fade", 260, 560), show="!inPlay", align="center", weight=800, tracking=2),
    box("Diamond", CX - 62, Y - 30, 124, 124, "#0B0D10@0.96", A("scale", 420, 0), rotate=45, borderW=4, borderColor="#FFFFFF", shadow=True),
    el("bases", "Bases", CX - 44, Y - 26, 88, 58, A("pop", 380, 260), show=LIVE, bind="bases",
       style={"layout": "tight", "on": "#FFFFFF", "off": "#FFFFFF@0.15", "stroke": "#FFFFFF@0.6", "strokeW": 2}),
    txt("Inning", CX - 44, Y + 34, 88, 44, "{arrow}{inning}", 28, A("fade", 260, 320, change="flash"), show=LIVE, align="center", weight=800, font="$font2"),
    txt("Final small", CX - 44, Y + 4, 88, 60, "F", 40, A("fade", 260, 320), show="isFinal", align="center", weight=800),
] + logo_or_abbr("Away mark", CX - 236, Y + 8, 150, 58, "away", 38, A("pop", 380, 420)) + logo_or_abbr("Home mark", CX + 86, Y + 8, 150, 58, "home", 38, A("pop", 380, 420))
   + sponsor_tab(CX + 340, Y, 250, 74, 520, radius=4, a_type="wipe-right", label_w=96)}

# 4. Top bar (thin full-width strip)
X, Y, W = 400, 22, 1120
bug_top = {"name": "Scorebug: Top Bar", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": [
    box("Bar", X, Y, W, 50, None, A("wipe-center", 520, 0), bg="linear-gradient(180deg, #2A2F37, #0E1014)", radius=4, shadow=True, borderW=1, borderColor="#FFFFFF@0.15"),
    el("bases", "Bases", X + 14, Y + 4, 78, 42, A("pop", 360, 300), show=LIVE, bind="bases",
       style={"layout": "tight", "on": "#FFD447", "off": "#FFFFFF@0.2", "stroke": "#FFFFFF@0.6", "strokeW": 2}),
    box("Away pill", X + 108, Y + 7, 190, 36, "{away.color}", A("grow-x", 320, 260), radius=3),
    txt("Away", X + 120, Y + 7, 120, 36, "{away.abbr}", 26, A("fade", 260, 380), weight=800, font="$font2"),
    txt("Away runs", X + 236, Y + 7, 56, 36, "{away.runs}", 28, A("fade", 260, 400, change="pop"), weight=800, align="right", font="$font2"),
    box("Home pill", X + 310, Y + 7, 190, 36, "{home.color}", A("grow-x", 320, 300), radius=3),
    txt("Home", X + 322, Y + 7, 120, 36, "{home.abbr}", 26, A("fade", 260, 420), weight=800, font="$font2"),
    txt("Home runs", X + 438, Y + 7, 56, 36, "{home.runs}", 28, A("fade", 260, 440, change="pop"), weight=800, align="right", font="$font2"),
    txt("Inning", X + 520, Y, 150, 50, "{arrow} {inningOrd|upper}", 26, A("fade", 260, 460, change="flash"), show=LIVE, align="center", weight=800, font="$font2"),
    txt("Outs", X + 670, Y, 140, 50, "{outs} {outsWord}", 26, A("fade", 260, 480, change="flash"), show=LIVE, align="center", weight=800, font="$font2"),
    txt("Count", X + 810, Y, 110, 50, "{count}", 28, A("fade", 260, 500, change="roll"), show=LIVE, align="center", weight=800, color="#FFD447", font="$font2"),
    txt("Final", X + 520, Y, 400, 50, "{statusText}", 26, A("fade", 260, 460), show="!inPlay", align="center", weight=800, tracking=3),
    img("Brand", X + 940, Y + 6, 166, 38, "{theme.logo}", A("fade", 300, 520), show="theme.logo && !sponsor.on"),
] + sponsor_tab(X + 926, Y + 5, 188, 40, 520, radius=3, a_type="fade", label_w=74)}

# ===================================================================== CARDS
CARD = "$card"


def stat_card(kind):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    X, Y, W, H = 90, 60, 576, 880
    return {"name": "Pitcher Season Card" if kind == "pit" else "Batter Season Card", "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": [
                box("Card", X, Y, W, H, CARD, A("zoom-out", 520, 0, out={"type": "fade", "dur": 300, "delay": 120, "ease": "in"}), radius=24, blur=24, shadow="0 30px 80px rgba(0,0,0,.45)"),
            ] + logo_or_abbr("Team", X + 46, Y + 46, 100, 104, team, 34, A("fade", 360, 260)) + [
                txt("Position", X + 160, Y + 50, 64, 40, "{%s.pos}" % who, 24, A("fade", 300, 300), align="center", weight=500, color="$dim"),
                txt("Number", X + 160, Y + 94, 64, 44, "{%s.number}" % who, 28, A("fade", 300, 340), align="center", weight=600),
                box("Accent bar", X + 238, Y + 50, 4, 104, "$accent", A("grow-y", 320, 300, origin="center top")),
                txt("Name", X + 266, Y + 44, W - 300, 118, "{%s.first}\\n{%s.last}" % (who, who), 46, A("reveal-up", 460, 340, ease="out"),
                    weight=400, wrap=True, fit=False, lineH=1.08, valign="center"),
                txt("Season label", X + 48, Y + 190, W - 96, 44, "{seasonYear} Statistics", 26, A("fade", 300, 460), weight=500),
                box("Rule", X + 48, Y + 242, W - 96, 4, "$accent", A("grow-x", 420, 480)),
                el("table", "Stats", X + 48, Y + 276, W - 96, H - 316,
                   A("none", 1, 0, rows={"type": "slide-up", "dur": 360, "stagger": 55, "delay": 520, "dist": 18}),
                   bind="%s.card" % who,
                   columns=[{"label": "", "field": "label", "w": 2.6, "align": "left", "weight": 500, "padX": 0},
                            {"label": "", "field": "value", "w": 1.4, "align": "right", "weight": 700, "padX": 8}],
                   style={"rowH": 68, "size": 27, "weight": 500, "color": "$text", "rowFill": "", "altFill": "", "header": False,
                          "padX": 0, "gap": 0, "rowLine": "$line", "rowLineW": 2, "maxRows": 8}),
            ] + sponsor_tab(X, Y + H + 14, W, 84, 760, radius=20)}


def lower(kind):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    X, Y, W, H = 96, 836, 820, 156
    line = ("{pitcher.today.ip} IP   {pitcher.today.k} K   {pitcher.today.pc|zero} pitches   ERA {pitcher.season.era|era}"
            if kind == "pit" else "{batter.today.line}   AVG {batter.season.avg|avg}   HR {batter.season.hr|zero}   OPS {batter.season.ops|avg}")
    tag = "{pitcher.throws|hand}  #{pitcher.number}" if kind == "pit" else "{batter.pos}  #{batter.number}  Bats {batter.bats}"
    return {"name": "Pitcher Lower Third" if kind == "pit" else "Batter Lower Third", "group": "lower", "autoHide": 8, "side": "", "sided": False,
            "elements": [
                box("Card", X, Y, W, H, CARD, A("zoom-out", 460, 0, out={"type": "fade", "dur": 280, "delay": 100, "ease": "in"}), radius=20, blur=20, shadow=True),
            ] + logo_or_abbr("Team", X + 28, Y + 28, 96, 100, team, 30, A("fade", 300, 220)) + [
                box("Accent bar", X + 144, Y + 30, 4, 96, "$accent", A("grow-y", 300, 240, origin="center top")),
                txt("Tag", X + 172, Y + 24, W - 200, 32, tag, 21, A("fade", 260, 300), weight=500, color="$dim", tracking=1),
                txt("Name", X + 172, Y + 52, W - 200, 60, "{%s.name}" % who, 48, A("reveal-up", 420, 300), weight=500),
                txt("Line", X + 172, Y + 110, W - 200, 32, line, 22, A("fade", 300, 460, change="flash"), weight=500, color="$dim"),
            ] + sponsor_tab(X + W - 360, Y - 66, 360, 58, 380, radius=12)}


def roster_card(name, bind, columns, title, rows_max, side="home", H=940):
    X, Y, W = 96, 70, 660
    return {"name": name, "group": "full", "autoHide": 0, "side": side, "sided": True, "elements": [
        box("Card", X, Y, W, H, CARD, A("zoom-out", 520, 0, out={"type": "fade", "dur": 300, "delay": 120, "ease": "in"}), radius=24, blur=24, shadow=True),
    ] + logo_or_abbr("Team", X + 44, Y + 40, 92, 92, "team", 30, A("fade", 360, 240)) + [
        box("Accent bar", X + 156, Y + 40, 4, 92, "$accent", A("grow-y", 320, 280, origin="center top")),
        txt("Team", X + 182, Y + 36, W - 220, 56, "{team.name}", 38, A("reveal-up", 420, 300), weight=500),
        txt("Title", X + 182, Y + 90, W - 220, 40, title, 24, A("fade", 300, 380), weight=500, color="$dim"),
        box("Rule", X + 44, Y + 160, W - 88, 4, "$accent", A("grow-x", 420, 420)),
        el("table", "Rows", X + 44, Y + 180, W - 88, H - 280,
           A("none", 1, 0, rows={"type": "slide-up", "dur": 340, "stagger": 50, "delay": 460, "dist": 16}),
           bind=bind, columns=columns,
           style={"rowH": 70, "size": 28, "weight": 500, "color": "$text", "rowFill": "", "altFill": "", "header": False, "padX": 0, "gap": 0,
                  "rowLine": "$line", "rowLineW": 2, "highlight": "isCurrent", "highlightFill": "$accent@0.22", "maxRows": rows_max, "radius": 6}),
    ]}


lineup = roster_card("Lineup", "team.lineup", [
    {"label": "", "field": "slot", "w": 0.5, "align": "left", "color": "$accent", "weight": 700},
    {"label": "", "field": "name", "w": 3.2, "align": "left"},
    {"label": "", "field": "pos", "w": 0.7, "align": "center", "color": "$dim"},
    {"label": "", "field": "{row.avg|avg}", "w": 0.9, "align": "right", "weight": 700},
    # Each lineup spot's sponsor (Sponsors > Lineup spots). Empty when the spot has none.
    {"label": "", "field": "{row.sponsor.logo}", "w": 1.3, "align": "right", "image": True, "imgH": 90}], "Starting Lineup", 9)
lineup["rowSponsors"] = "lineup_{row.slot}"
lineup["elements"] += [
    txt("SP label", 140, 920, 300, 34, "Starting Pitcher", 20, A("fade", 300, 900), color="$dim", weight=500),
    txt("SP", 140, 950, 400, 44, "{team.sp.name}", 28, A("fade", 300, 940), weight=600),
    txt("SP ERA", 472, 930, 240, 60, "ERA {team.sp.era|era}", 26, A("fade", 300, 960), show="team.sp.era", align="right", weight=600),
]
pitching = roster_card("Pitching Line", "team.pitchers", [
    {"label": "", "field": "{row.last}", "w": 2.4, "align": "left"},
    {"label": "", "field": "{row.ip} IP", "w": 1.2, "align": "right"},
    {"label": "", "field": "{row.h} H", "w": 0.9, "align": "right", "color": "$dim"},
    {"label": "", "field": "{row.er} ER", "w": 1, "align": "right", "color": "$dim"},
    {"label": "", "field": "{row.k} K", "w": 0.9, "align": "right", "color": "$dim"},
    {"label": "", "field": "{row.pc}", "w": 0.8, "align": "right", "color": "$accent", "weight": 700}], "Pitching Today", 7, H=760)

# ===================================================================== DUE UP (kinetic type, then the next three batters)
DX, DY, DW, DH = 110, 190, 1700, 720
PW, PG = 360, 28              # player panel width / gap
PX0 = DX + DW - 3 * PW - 2 * PG - 50
dueup = {"name": "Due Up", "group": "full", "autoHide": 10, "side": "batting", "sided": True, "elements": [
    box("Backdrop", 0, 0, 1920, 1080, None, A("fade", 500, 0, out={"type": "fade", "dur": 400, "delay": 200, "ease": "in"}, loop={"type": "breathe", "dur": 7000, "amount": 0.06}),
        bg="radial-gradient(ellipse at 72% 28%, rgba(104,140,150,0.55), rgba(12,16,19,0.97) 62%)"),
    txt("Kinetic", 160, 300, 2200, 440, "Due Up", 400, A("slide-left", 1500, 150, ease="out", dist=1100, hold=350,
        out={"type": "blur", "dur": 380, "delay": 0, "ease": "in"}), weight=500, fit=False, tracking=-12),
    box("Card", DX, DY, DW, DH, None, A("zoom-out", 620, 2150, out={"type": "fade", "dur": 300, "delay": 120, "ease": "in"}), radius=30, shadow="0 40px 100px rgba(0,0,0,.5)",
        bg="linear-gradient(100deg, rgba(14,16,18,0.96) 30%, rgba(40,52,58,0.88))"),
] + logo_or_abbr("Team", DX + 70, DY + 70, 100, 100, "team", 34, A("fade", 400, 2350)) + [
    txt("Title", DX + 70, DY + 200, 420, 90, "Due Up", 76, A("reveal-up", 520, 2380), weight=500),
    box("Rule", DX + 74, DY + 302, 54, 6, "$accent", A("grow-x", 360, 2550)),
    txt("Half", DX + 70, DY + 324, 420, 40, "{nextHalfLabel}", 26, A("fade", 360, 2600), weight=500, color="$dim"),
    txt("Team name", DX + 70, DY + 366, 420, 40, "{team.name}", 26, A("fade", 360, 2640), weight=500, color="$dim"),
]}
for i in range(3):
    x = PX0 + i * (PW + PG)
    d = 2350 + i * 140
    who = "team.dueUp.%d" % i
    dueup["elements"] += [
        box("P%d panel" % (i + 1), x, DY + 50, PW, DH - 100, "#FFFFFF@0.06", A("slide-up", 520, d, dist=40), radius=22, show=who + ".name"),
        box("P%d photo bg" % (i + 1), x, DY + 50, PW, 400, None, A("fade", 400, d + 80), show=who + ".name", radius=22,
            bg="linear-gradient(180deg, color-mix(in srgb, {team.color} 55%, #1a1d22), #121417)"),
        txt("P%d number" % (i + 1), x, DY + 80, PW, 340, "{%s.number}" % who, 200, A("fade", 400, d + 160), show="!%s.photo && %s.number" % (who, who),
            align="center", weight=800, color="#FFFFFF@0.18", fit=False),
        img("P%d photo" % (i + 1), x, DY + 50, PW, 400, "{%s.photo}" % who, A("reveal-up", 600, d + 160), show=who + ".photo",
            fit="cover", focus="center top", radius=22),
        box("P%d slot" % (i + 1), x + 18, DY + 68, 52, 52, "$accent", A("pop", 380, d + 420), show=who + ".slot", radius=26),
        txt("P%d slot no" % (i + 1), x + 18, DY + 68, 52, 52, "{%s.slot}" % who, 26, A("pop", 380, d + 420), show=who + ".slot", align="center", weight=800, color="$primary"),
        txt("P%d first" % (i + 1), x + 26, DY + 470, PW - 52, 40, "{%s.first}" % who, 28, A("fade", 380, d + 360), weight=500, color="$dim"),
        txt("P%d last" % (i + 1), x + 26, DY + 506, PW - 52, 58, "{%s.last}" % who, 46, A("reveal-up", 460, d + 380), weight=600),
        txt("P%d stats" % (i + 1), x + 26, DY + 570, PW - 52, 34, "{%s.pos}   AVG {%s.avg|avg}   HR {%s.hr|zero}" % (who, who, who), 22,
            A("fade", 380, d + 460), show=who + ".name", weight=500),
        txt("P%d today" % (i + 1), x + 26, DY + 606, PW - 52, 30, "Today {%s.today}" % who, 20, A("fade", 380, d + 500), show=who + ".today", weight=500, color="$dim"),
    ]
dueup["elements"] += sponsor_tab(DX + 70, DY + DH - 150, 380, 90, 2900, radius=16)

# ===================================================================== INNING SPONSOR (half-inning presented-by)
IX, IY, IW, IH = 96, 846, 900, 140
inning_sp = {"name": "Inning Sponsor", "group": "lower", "autoHide": 7, "side": "", "sided": False, "elements": [
    box("Card", IX, IY, IW, IH, CARD, A("zoom-out", 460, 0, out={"type": "fade", "dur": 280, "delay": 100, "ease": "in"}), radius=20, blur=20, shadow=True),
    box("Accent bar", IX + 30, IY + 28, 4, IH - 56, "$accent", A("grow-y", 300, 200, origin="center top")),
    txt("Half", IX + 56, IY + 22, 460, 60, "{nextHalfLabel}", 46, A("reveal-up", 420, 260), weight=600),
    txt("Score", IX + 58, IY + 82, 460, 36, "{away.abbr} {away.runs}   {home.abbr} {home.runs}", 24, A("fade", 360, 380), weight=500, color="$dim"),
    box("Sponsor area", IX + IW - 400, IY + 16, 384, IH - 32, "#FFFFFF@0.96", A("wipe-left", 420, 300), show="sponsor.on", radius=14),
    txt("Sponsor label", IX + IW - 384, IY + 16, 120, IH - 32, "{sponsor.label}", 20, A("fade", 300, 520), show="sponsor.on && sponsor.label",
        weight=600, color="#5A6270", wrap=True, fit=False, lineH=1.15),
    img("Sponsor logo", IX + IW - 256, IY + 26, 228, IH - 52, "{sponsor.logo}", A("fade", 360, 560, change="fade"), show="sponsor.logo"),
    txt("Sponsor name", IX + IW - 256, IY + 16, 228, IH - 32, "{sponsor.name}", 30, A("fade", 360, 560), show="sponsor.on && !sponsor.logo",
        weight=800, color="#16181C", align="center"),
]}

# ===================================================================== STANDINGS
SX, SY, SW, SH = 560, 60, 800, 960
standings = {"name": "Standings", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": [
    dict(box("Card", SX, SY, SW, SH, CARD, A("zoom-out", 520, 0, out={"type": "fade", "dur": 300, "delay": 120, "ease": "in"}), radius=24, blur=24, shadow=True),
         growWith={"bind": "standingsGroup.teams", "base": 250, "per": 68, "max": 11, "min": 400}),
    img("League logo", SX + 44, SY + 40, 92, 92, "{league.logo}", A("fade", 360, 240), show="league.logo"),
    img("Brand logo", SX + 44, SY + 40, 92, 92, "{brand.logo}", A("fade", 360, 240), show="!league.logo && brand.logo"),
    box("Accent bar", SX + 156, SY + 40, 4, 92, "$accent", A("grow-y", 320, 280, origin="center top")),
    txt("Group", SX + 182, SY + 36, SW - 220, 56, "{standingsGroup.name}", 38, A("reveal-up", 420, 300), weight=500),
    txt("Title", SX + 182, SY + 90, SW - 220, 40, "{seasonYear} Standings", 24, A("fade", 300, 380), weight=500, color="$dim"),
    box("Rule", SX + 44, SY + 160, SW - 88, 4, "$accent", A("grow-x", 420, 420)),
    el("table", "Teams", SX + 44, SY + 176, SW - 88, SH - 210,
       A("none", 1, 0, rows={"type": "slide-up", "dur": 340, "stagger": 50, "delay": 460, "dist": 16}),
       bind="standingsGroup.teams",
       columns=[{"label": "", "field": "rank", "w": 0.45, "align": "left", "color": "$accent", "weight": 700},
                {"label": "", "field": "{row.logo}", "w": 0.75, "align": "center", "image": True, "imgH": 78},
                {"label": "TEAM", "field": "name", "w": 4.2, "align": "left"},
                {"label": "W", "field": "w", "w": 0.75, "align": "right", "weight": 700},
                {"label": "L", "field": "l", "w": 0.75, "align": "right", "weight": 700},
                {"label": "PCT", "field": "pct", "w": 1, "align": "right", "color": "$dim"},
                {"label": "GB", "field": "gb", "w": 0.85, "align": "right", "color": "$dim"}],
       style={"rowH": 68, "size": 27, "weight": 500, "color": "$text", "rowFill": "", "altFill": "", "header": True, "headerH": 44, "headerSize": 16,
              "headerColor": "$dim", "headerFill": "", "padX": 0, "gap": 0, "rowLine": "$line", "rowLineW": 2,
              "highlight": "isGame", "highlightFill": "$accent@0.18", "maxRows": 11, "radius": 6}),
]}

# ===================================================================== MATCHUP (split screen)
matchup_full = {"name": "Matchup", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": []}
for i, side in enumerate(("away", "home")):
    hx = i * 960
    sgn = -1 if i == 0 else 1
    slide = "slide-right" if i == 0 else "slide-left"
    matchup_full["elements"] += [
        box("%s base" % side.title(), hx, 0, 960, 1080, "#0D1014", A(slide, 620, 0, dist=240, out={"type": "fade", "dur": 360, "delay": 200, "ease": "in"})),
        img("%s background" % side.title(), hx, 0, 960, 1080, "{%s.bg}" % side, A("fade", 800, 200, out=FADE_OUT, loop={"type": "breathe", "dur": 9000, "amount": 0.05}),
            show="%s.bg" % side, fit="cover"),
        box("%s tint" % side.title(), hx, 0, 960, 1080, None, A("fade", 600, 120), bg="linear-gradient(%ddeg, rgba(8,12,18,0.86), color-mix(in srgb, {%s.color} 30%%, rgba(8,12,18,0.55)))" % (90 if i == 0 else 270, side)),
    ] + logo_or_abbr("%s mark" % side.title(), hx + (300 if i == 0 else 320), 380, 340, 320, side, 150, A("zoom-out", 620, 420)) + [
        # home side mirrors away exactly: logo centred in its half, name and record on the outer edge
        txt("%s name" % side.title(), hx + (40 if i == 0 else 710), 440, 210, 200, "{%s.name}" % side, 30, A("fade", 500, 640),
            weight=500, wrap=True, fit=False, lineH=1.2, align="left" if i == 0 else "right"),
        txt("%s record" % side.title(), hx + (40 if i == 0 else 710), 640, 210, 40, "{%s.record}" % side, 24, A("fade", 500, 720), weight=500, color="$dim",
            align="left" if i == 0 else "right"),
    ]
matchup_full["elements"] += [
    box("Bar L", 872, 506, 5, 76, "$accent", A("grow-y", 360, 760)),
    txt("VS", 880, 480, 160, 128, "VS", 66, A("pop", 460, 700), align="center", weight=500),
    box("Bar R", 1043, 506, 5, 76, "$accent", A("grow-y", 360, 760)),
    txt("Note", 560, 930, 800, 50, "{custom.line1}", 28, A("fade", 400, 900), show="custom.line1", align="center", weight=500, color="$dim"),
]

# ===================================================================== PLAYER SPOTLIGHT (three panels)
SIL = "linear-gradient(180deg, #F7F8FA, #D7DCE2)"
spotlight = {"name": "Player Spotlight", "group": "full", "autoHide": 0, "side": "batting", "sided": False, "elements": [
    box("Left frame", 150, 440, 540, 400, None, A("flip-y", 620, 0, out={"type": "fade", "dur": 300, "delay": 160, "ease": "in"}), bg=SIL, shadow=True, radius=4),
    box("Left field", 168, 458, 504, 364, None, A("fade", 400, 300), bg="radial-gradient(circle at 50% 45%, color-mix(in srgb, {team.color} 70%, #fff), {team.color} 70%)"),
] + logo_or_abbr("Left logo", 210, 480, 420, 320, "team", 120, A("zoom-out", 520, 420)) + [
    box("Center back", 690, 440, 560, 400, None, A("fade", 500, 100), bg="repeating-linear-gradient(180deg, #E9ECF0 0 118px, #3B4C66 118px 121px)"),
    img("Player", 720, 160, 500, 690, "{batter.photo}", A("slide-up", 620, 300, dist=60), show="batter.photo", focus="center bottom"),
    txt("Number", 720, 500, 500, 300, "{batter.number}", 260, A("fade", 500, 300), show="!batter.photo", align="center", weight=800, color="{team.color}"),
    box("Right frame", 1250, 440, 540, 400, None, A("flip-y", 620, 0, out={"type": "fade", "dur": 300, "delay": 160, "ease": "in"}), bg=SIL, shadow=True, radius=4),
    txt("Season", 1290, 456, 470, 76, "{seasonYear} SEASON", 52, A("reveal-up", 420, 420), align="center", weight=800, color="#16181C", font="$font2"),
    el("table", "Stats", 1290, 540, 470, 272, A("none", 1, 0, rows={"type": "slide-left", "dur": 360, "stagger": 80, "delay": 520, "dist": 40}),
       bind="batter.card",
       columns=[{"label": "", "field": "{row.label|upper}", "w": 1.7, "align": "left", "fill": "#16181C", "padX": 18, "weight": 800},
                {"label": "", "field": "value", "w": 1, "align": "right", "fill": "{team.color}", "padX": 18, "size": 40, "weight": 800}],
       style={"rowH": 60, "size": 30, "weight": 800, "color": "#FFFFFF", "rowFill": "", "header": False, "padX": 0, "gap": 8, "maxRows": 4, "font": "$font2"}),
    txt("Note", 1290, 806, 470, 30, "{custom.line2|upper}", 20, A("fade", 360, 900), show="custom.line2", align="right", weight=800, color="#16181C", font="$font2"),
    box("Title frame", 520, 860, 880, 124, None, A("slide-up", 520, 380, dist=60, out={"type": "fade", "dur": 260, "delay": 0, "ease": "in"}), bg=SIL, shadow=True, radius=4),
    box("Title team", 534, 874, 250, 96, None, A("wipe-right", 380, 640), bg="linear-gradient(180deg, color-mix(in srgb, {team.color} 80%, #fff), {team.color})"),
] + logo_or_abbr("Title mark", 544, 880, 230, 84, "team", 46, A("fade", 300, 820)) + [
    txt("Title", 806, 868, 580, 64, "PLAYER SPOTLIGHT", 54, A("reveal-up", 420, 700), weight=800, color="{team.color}", font="$font2"),
    txt("Name", 808, 928, 580, 40, "{batter.name|upper}", 30, A("fade", 360, 820), weight=800, color="#1A1D22", font="$font2"),
] + sponsor_tab(1410, 868, 340, 108, 760, style="silver", radius=4, a_type="slide-up")}
spotlight["elements"][0]["tiltY"] = 16
spotlight["elements"][1]["tiltY"] = 16
for e in spotlight["elements"]:
    if e["name"].startswith("Left logo"):
        e["tiltY"] = 16
    if e["name"] in ("Right frame", "Season", "Stats", "Note"):
        e["tiltY"] = -16

# ===================================================================== LINESCORE, DEFENSE, NOTE
linescore = {"name": "Linescore", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": [
    box("Card", 380, 790, 1160, 214, CARD, A("zoom-out", 480, 0, out={"type": "fade", "dur": 300, "delay": 120, "ease": "in"}), radius=22, blur=20, shadow=True),
    txt("Status", 420, 806, 400, 40, "{statusText}", 22, A("fade", 300, 260), weight=600, color="$accent", tracking=2),
    el("linescore", "Linescore", 410, 846, 1100, 140, A("fade", 300, 200, rows={"type": "slide-up", "dur": 340, "stagger": 90, "delay": 260, "dist": 16}),
       style={"size": 32, "color": "$text", "headColor": "$dim", "headSize": 18, "rowFill": "", "totalFill": "#FFFFFF@0.07",
              "current": "$accent@0.22", "minInnings": 9, "teamW": 140}),
]}
defense = {"name": "Defense", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": [
    box("Card", 330, 50, 1260, 990, CARD, A("zoom-out", 520, 0, out={"type": "fade", "dur": 300, "delay": 120, "ease": "in"}), radius=26, blur=22, shadow=True),
] + logo_or_abbr("Team", 380, 86, 80, 80, "team", 28, A("fade", 360, 240)) + [
    box("Accent bar", 482, 90, 4, 72, "$accent", A("grow-y", 300, 280, origin="center top")),
    txt("Team", 506, 80, 900, 52, "{team.name}", 36, A("reveal-up", 420, 300), weight=500),
    txt("Title", 506, 128, 900, 36, "Defensive Alignment", 22, A("fade", 300, 380), weight=500, color="$dim"),
    el("field", "Field", 390, 190, 1140, 830, A("fade", 520, 300, rows={"type": "pop", "dur": 380, "stagger": 70, "delay": 500}), bind="team.defense",
       style={"grass": "#FFFFFF@0.05", "dirt": "#FFFFFF@0.08", "line": "#FFFFFF@0.45", "labelFill": "#0E1013@0.92", "nameColor": "$text",
              "posColor": "$accent", "size": 26, "nameField": "last"}),
]}
custom_lt = {"name": "Custom Lower Third", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": [
    box("Card", 96, 856, 820, 136, CARD, A("zoom-out", 460, 0, out={"type": "fade", "dur": 280, "delay": 100, "ease": "in"}), radius=20, blur=20, shadow=True),
    box("Accent bar", 130, 884, 4, 80, "$accent", A("grow-y", 300, 200, origin="center top")),
    txt("Line 1", 158, 872, 730, 58, "{custom.line1}", 44, A("reveal-up", 420, 260), weight=500),
    txt("Line 2", 158, 928, 730, 40, "{custom.line2}", 24, A("fade", 300, 420), show="custom.line2", weight=500, color="$dim"),
]}
note = {"name": "Note", "group": "note", "autoHide": 10, "side": "", "sided": False, "elements": [
    txt("Line 1", 1080, 940, 780, 40, "{custom.line1}", 30, A("reveal-up", 420, 0), align="right", weight=500, textShadow="0 2px 10px rgba(0,0,0,.75)"),
    txt("Line 2", 1080, 980, 780, 40, "{custom.line2}", 30, A("reveal-up", 420, 90), show="custom.line2", align="right", weight=500, textShadow="0 2px 10px rgba(0,0,0,.75)"),
]}

# ===================================================================== TRANSITIONS
END = 1350  # all stinger layers leave together at this time (ms after take)


def held(a, start_end):
    a["hold"] = max(50, END - start_end)
    return a


stinger_layers = []
bg_a = A("diamond", 480, 0, ease="in-out", out={"type": "diamond", "dur": 460, "delay": 0, "ease": "in-out"})
stinger_layers.append(box("Field", 0, 0, 1920, 1080, None, held(bg_a, 480), bg="radial-gradient(circle at 50% 50%, #FFFFFF, #D5DBE3 72%)"))
for k, size in enumerate((1500, 1050, 640)):
    a = A("scale", 600, 60 * k, out={"type": "fade", "dur": 300, "delay": 0, "ease": "in"})
    stinger_layers.append(box("Ring %d" % (k + 1), 960 - size // 2, 540 - size // 2, size, size, "transparent", held(a, 60 * k + 600),
                              rotate=45, borderW=3, borderColor="#9AA6B5@0.7"))
OUT_SC = {"type": "scale", "dur": 300, "delay": 0, "ease": "in"}
OUT_F = {"type": "fade", "dur": 260, "delay": 0, "ease": "in"}
# Logo above the name (brand = theme logo/name when set, otherwise the home team's).
stinger_layers.append(img("Brand logo", 735, 200, 450, 360, "{brand.logo}", held(A("pop", 520, 200, out=OUT_SC), 720), show="brand.logo"))
stinger_layers.append(txt("Brand name", 260, 590, 1400, 120, "{brand.name|upper}", 76, held(A("reveal-up", 480, 380, out=OUT_F), 860),
                          show="brand.logo && brand.name", align="center", weight=800, color="$primary"))
stinger_layers.append(box("Name rule", 810, 726, 300, 5, "$accent", held(A("grow-x", 420, 520, origin="center center", out=OUT_F), 940),
                          show="brand.logo && brand.name"))
# No logo: the name alone, centered.
stinger_layers.append(txt("Brand name (no logo)", 360, 400, 1200, 220, "{brand.name|upper}", 84, held(A("pop", 520, 200, out=OUT_SC), 720),
                          show="!brand.logo", align="center", weight=800, color="$primary", wrap=True, fit=False))
stinger_layers.append(box("Name rule (no logo)", 810, 640, 300, 5, "$accent", held(A("grow-x", 420, 420, origin="center center", out=OUT_F), 840),
                          show="!brand.logo"))
stinger = {"name": "Diamond Transition", "group": "stinger", "autoHide": 2.2, "side": "", "sided": False, "elements": stinger_layers}

opener = {"name": "Video Opener", "group": "stinger", "autoHide": 0, "side": "", "sided": False, "elements": [
    el("video", "Opener video", 0, 0, 1920, 1080, A("fade", 200, 0, out={"type": "fade", "dur": 300, "delay": 0, "ease": "in"}),
       show="theme.openerVideo", src="{theme.openerVideo}", loop=False, sound=True, style={"fit": "cover"}),
]}

doc = {
    "version": 2,
    "name": "Night Game",
    "description": "Clean translucent cards, kinetic type, split-screen matchup, player spotlight, diamond transition and four scorebug layouts.",
    "theme": {
        "primary": "#16181C",
        "accent": "#F5821F",
        "text": "#FFFFFF",
        "dim": "rgba(255,255,255,0.68)",
        "line": "rgba(255,255,255,0.20)",
        "card": "rgba(20,21,24,0.86)",
        "panel": "rgba(20,21,24,0.86)",
        "panel2": "rgba(34,36,40,0.86)",
        "font": "'Inter Var', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif",
        "font2": "'Bahnschrift SemiCondensed', Bahnschrift, 'DIN Condensed', 'Roboto Condensed', 'Arial Narrow', 'Inter Var', sans-serif",
        "logo": "",
        "brandName": "",
        "openerVideo": "",
    },
    "graphics": {
        "scorebug": bug_stack,
        "bug_bar": bug_bar,
        "bug_diamond": bug_diamond,
        "bug_top": bug_top,
        "batter": lower("bat"),
        "pitcher": lower("pit"),
        "batter_card": stat_card("bat"),
        "pitcher_card": stat_card("pit"),
        "dueup": dueup,
        "inning_sponsor": inning_sp,
        "standings": standings,
        "matchup": matchup_full,
        "spotlight": spotlight,
        "lineup": lineup,
        "pitching": pitching,
        "defense": defense,
        "linescore": linescore,
        "custom": custom_lt,
        "note": note,
        "stinger": stinger,
        "opener": opener,
    },
}

# Sponsor rules: tried left to right, first slot with an active sponsor wins.
#   half_{halfKey}: the half inning being played (or next, during a break): half_T1 ... half_B9, half_TX/BX for extras
#   lineup_{batter.slot}: the current hitter's lineup spot: lineup_1 ... lineup_9
HALF = "half_{halfKey}"
SLOTS = {"scorebug": HALF + ", scorebug", "bug_bar": HALF + ", scorebug", "bug_diamond": HALF + ", scorebug", "bug_top": HALF + ", scorebug",
         "batter": "lineup_{batter.slot}, batter", "pitcher": "pitcher",
         "batter_card": "lineup_{batter.slot}, batter_card", "pitcher_card": "pitcher_card",
         "spotlight": "lineup_{batter.slot}, spotlight", "dueup": HALF + ", dueup", "inning_sponsor": HALF}
for gid, slot in SLOTS.items():
    doc["graphics"][gid]["sponsorSlot"] = slot

# New broadcast graphic types (stat bars, cards, comparisons, final / summary, matchups, side panels,
# automatic stingers, show graphics) in the Night Game look. See tools/broadcast_lib.py.
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import broadcast_lib as BL  # noqa: E402
for gid in BL.PICKABLE:
    if gid in doc["graphics"]:
        doc["graphics"][gid]["pickable"] = True
for gid, gdef in BL.all_new(BL.NIGHT).items():
    if gid in BL.SPONSOR_SLOTS:
        gdef.setdefault("sponsorSlot", BL.SPONSOR_SLOTS[gid])
    doc["graphics"][gid] = gdef
doc["description"] += " Also: stat bars and cards, pitching comparisons, game final and summary, matchup banner and split, side panels, automatic home run / wild pitch stingers and show graphics."

import sports_lib as SL  # noqa: E402
doc["graphics"].update(SL.all_sports(BL.NIGHT))     # basketball, football, hockey

os.makedirs(os.path.dirname(OUT), exist_ok=True)
BL.stamp(doc)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
shutil.copyfile(OUT, DEFAULT)
print("wrote", OUT, "and default.json, graphics:", len(doc["graphics"]))
