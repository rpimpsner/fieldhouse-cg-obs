"""Builds templates/default.json, the starter broadcast package.
Run:  python tools/build_default_templates.py
Every value here is editable later in the visual editor."""
import json
import sys as _sys
_sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import broadcast_lib as BL  # noqa: E402
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "packages", "classic.json")
_n = [0]


def nid(prefix):
    _n[0] += 1
    return "%s_%d" % (prefix, _n[0])


def anim(t="fade", dur=400, delay=0, ease="out", dist=None, out=None, rows=None, change=None, origin=None):
    a = {"in": {"type": t, "dur": dur, "delay": delay, "ease": ease}}
    if dist is not None:
        a["in"]["dist"] = dist
    if origin:
        a["in"]["origin"] = origin
    a["out"] = out or {"type": "auto", "dur": max(200, int(dur * 0.7)), "delay": 0, "ease": "in"}
    if rows:
        a["rows"] = rows
    if change:
        a["change"] = change
    return a


def box(name, x, y, w, h, fill, a=None, show=None, **st):
    s = {"fill": fill}
    s.update(st)
    e = {"id": nid("box"), "name": name, "type": "box", "x": x, "y": y, "w": w, "h": h, "style": s, "anim": a or anim()}
    if show:
        e["showIf"] = show
    return e


def text(name, x, y, w, h, txt, size=32, a=None, show=None, **st):
    s = {"color": "$text", "size": size, "weight": 800, "align": "left", "valign": "center", "padX": 0, "fit": True}
    s.update(st)
    e = {"id": nid("txt"), "name": name, "type": "text", "x": x, "y": y, "w": w, "h": h, "text": txt, "style": s, "anim": a or anim()}
    if show:
        e["showIf"] = show
    return e


def el(kind, name, x, y, w, h, a=None, show=None, **kw):
    e = {"id": nid(kind), "name": name, "type": kind, "x": x, "y": y, "w": w, "h": h, "anim": a or anim()}
    e.update(kw)
    if show:
        e["showIf"] = show
    return e


OUT_FADE = {"type": "fade", "dur": 220, "delay": 0, "ease": "in"}


def logo(name, x, y, w, h, team, a):
    """Team logo (from Teams in the Scoring panel); the graphic shows the abbreviation instead when there is none."""
    return {"id": nid("img"), "name": name, "type": "image", "x": x, "y": y, "w": w, "h": h, "src": "{%s.logo}" % team,
            "style": {"fit": "contain"}, "anim": a, "showIf": "%s.logo" % team}


def sponsor_tab(x, y, w, h, delay):
    on = "sponsor.on"
    return [
        box("Sponsor bg", x, y, w, h, "#FFFFFF@0.96", anim("wipe-down", 320, delay, out=OUT_FADE), show=on),
        box("Sponsor accent", x, y, 6, h, "$accent", anim("grow-y", 260, delay + 100, out=OUT_FADE), show=on),
        text("Sponsor label", x + 16, y, int(w * 0.38), h, "{sponsor.label|upper}", 15, anim("fade", 240, delay + 200, out=OUT_FADE),
             show=on + " && sponsor.label", color="$primary", weight=800, tracking=1),
        {"id": nid("img"), "name": "Sponsor logo", "type": "image", "x": x + int(w * 0.4), "y": y + 5, "w": int(w * 0.58), "h": h - 10,
         "src": "{sponsor.logo}", "style": {"fit": "contain"}, "anim": anim("fade", 260, delay + 220, out=OUT_FADE, change="fade"),
         "showIf": on + " && sponsor.logo && sponsor.label"},
        {"id": nid("img"), "name": "Sponsor logo (no label)", "type": "image", "x": x + 14, "y": y + 5, "w": w - 28, "h": h - 10,
         "src": "{sponsor.logo}", "style": {"fit": "contain"}, "anim": anim("fade", 260, delay + 220, out=OUT_FADE, change="fade"),
         "showIf": on + " && sponsor.logo && !sponsor.label"},
        text("Sponsor name", x + int(w * 0.4), y, int(w * 0.56), h, "{sponsor.name|upper}", 20, anim("fade", 240, delay + 220, out=OUT_FADE, change="fade"),
             show=on + " && !sponsor.logo", color="$primary", align="right"),
    ]

# ---------------------------------------------------------------- scorebug
X, Y = 64, 48
scorebug = {
    "name": "Scorebug", "group": "", "autoHide": 0, "side": "", "sided": False,
    "elements": [
        box("Panel", X, Y, 500, 104, "$panel", anim("wipe-right", 520, 0, "out", out={"type": "wipe-left", "dur": 380, "delay": 120, "ease": "in"}), shadow=True, radius=4),
        box("Away color", X, Y, 12, 52, "{away.color}", anim("grow-y", 300, 180, origin="center top", out=OUT_FADE)),
        box("Home color", X, Y + 52, 12, 52, "{home.color}", anim("grow-y", 300, 230, origin="center top", out=OUT_FADE)),
        box("Row divider", X + 12, Y + 51, 254, 2, "#FFFFFF@0.12", anim("grow-x", 300, 260, out=OUT_FADE)),
        logo("Away logo", X + 20, Y + 6, 44, 40, "away", anim("fade", 300, 260, out=OUT_FADE)),
        text("Away abbr", X + 26, Y, 140, 52, "{away.abbr}", 34, anim("slide-right", 360, 240, dist=24, out=OUT_FADE), show="!away.logo"),
        text("Away abbr (logo)", X + 72, Y, 98, 52, "{away.abbr}", 34, anim("slide-right", 360, 240, dist=24, out=OUT_FADE), show="away.logo"),
        text("Away runs", X + 176, Y, 84, 52, "{away.runs}", 40, anim("fade", 300, 300, out=OUT_FADE, change="pop"), align="right"),
        logo("Home logo", X + 20, Y + 58, 44, 40, "home", anim("fade", 300, 310, out=OUT_FADE)),
        text("Home abbr", X + 26, Y + 52, 140, 52, "{home.abbr}", 34, anim("slide-right", 360, 290, dist=24, out=OUT_FADE), show="!home.logo"),
        text("Home abbr (logo)", X + 72, Y + 52, 98, 52, "{home.abbr}", 34, anim("slide-right", 360, 290, dist=24, out=OUT_FADE), show="home.logo"),
        text("Home runs", X + 176, Y + 52, 84, 52, "{home.runs}", 40, anim("fade", 300, 350, out=OUT_FADE, change="pop"), align="right"),
        box("Divider", X + 270, Y + 10, 2, 84, "#FFFFFF@0.15", anim("grow-y", 260, 300, out=OUT_FADE)),
        text("Inning", X + 274, Y + 2, 96, 56, "{arrow} {inning}", 32, anim("fade", 300, 360, out=OUT_FADE, change="flash"), show="arrow && !isFinal", align="center"),
        text("Inning (mid/end)", X + 274, Y + 2, 96, 56, "{halfShort} {inning}", 24, anim("fade", 300, 360, out=OUT_FADE), show="!arrow && !isFinal", align="center"),
        text("Final", X + 274, Y, 96, 104, "{statusText}", 26, anim("fade", 300, 360, out=OUT_FADE), show="isFinal || isPre", align="center", color="$accent"),
        el("dots", "Outs", X + 282, Y + 62, 80, 30, anim("fade", 300, 420, out=OUT_FADE), show="!isFinal && !isPre", bind="outs",
           style={"total": 2, "size": 15, "gap": 9, "on": "$accent", "off": "#FFFFFF@0.22", "shape": "circle", "align": "center"}),
        box("Divider 2", X + 372, Y + 10, 2, 84, "#FFFFFF@0.15", anim("grow-y", 260, 320, out=OUT_FADE)),
        el("bases", "Bases", X + 382, Y + 6, 108, 62, anim("pop", 420, 420, out=OUT_FADE), show="!isFinal && !isPre", bind="bases",
           style={"on": "$accent", "off": "#FFFFFF@0.16", "stroke": "#FFFFFF@0.65", "strokeW": 2}),
        text("Count", X + 376, Y + 66, 120, 34, "{count}", 24, anim("fade", 300, 480, out=OUT_FADE, change="flash"), show="!isFinal && !isPre", align="center"),
        box("PC tab", X, Y + 104, 500, 34, "$primary@0.94", anim("wipe-down", 320, 520, out={"type": "wipe-up", "dur": 220, "delay": 0, "ease": "in"}), show="pitcher.last && isLive"),
        text("PC pitcher", X + 16, Y + 104, 330, 34, "P: {pitcher.last|upper}", 19, anim("fade", 260, 620, out=OUT_FADE), show="pitcher.last && isLive", weight=700, tracking=1),
        text("PC value", X + 300, Y + 104, 186, 34, "P-S {pitcher.today.pc|zero}-{pitcher.today.st|zero}", 19, anim("fade", 260, 660, out=OUT_FADE, change="flash"), show="pitcher.last && isLive", align="right", color="$accent"),
    ] + sponsor_tab(X, Y + 142, 500, 40, 700),
}

# ---------------------------------------------------------- lower thirds
def lower_third(kind):
    L, T = 180, 842
    if kind == "batter":
        who, team, num, nm, tag = "batter", "batting", "{batter.number|num}", "{batter.name|upper}", "{batter.pos}   BATS {batter.bats}"
        left_label, left_val = "TODAY", "{batter.today.line}"
        right = "AVG {batter.season.avg|avg}    HR {batter.season.hr|zero}    RBI {batter.season.rbi|zero}    OPS {batter.season.ops|avg}"
        left_show = "batter.today.line"
    else:
        who, team, num, nm, tag = "pitcher", "fielding", "{pitcher.number|num}", "{pitcher.name|upper}", "{pitcher.throws|hand}"
        left_label, left_val = "TODAY", "{pitcher.today.ip} IP   {pitcher.today.h} H   {pitcher.today.er} ER   {pitcher.today.bb} BB   {pitcher.today.k} K"
        right = "ERA {pitcher.season.era|era}    PC {pitcher.today.pc|zero}"
        left_show = "pitcher.today.ip"
    return {
        "name": "Batter Lower Third" if kind == "batter" else "Pitcher Lower Third",
        "group": "lower", "autoHide": 8, "side": "", "sided": False,
        "elements": [
            box("Accent bar", L, T, 14, 128, "$accent", anim("grow-y", 280, 0, origin="center bottom", out={"type": "fade", "dur": 200, "delay": 300, "ease": "in"})),
            box("Team block", L + 14, T, 112, 128, "{%s.color}" % team, anim("wipe-right", 300, 120, out={"type": "wipe-left", "dur": 240, "delay": 220, "ease": "in"})),
            logo("Team logo", L + 24, T + 14, 92, 100, team, anim("fade", 260, 320, out=OUT_FADE)),
            text("Team abbr", L + 14, T, 112, 128, "{%s.abbr}" % team, 34, anim("fade", 260, 320, out=OUT_FADE), align="center", show="!%s.logo" % team),
            box("Name panel", L + 126, T, 860, 76, "$panel", anim("wipe-right", 460, 200, out={"type": "wipe-left", "dur": 300, "delay": 120, "ease": "in"})),
            text("Number", L + 144, T, 96, 76, num, 36, anim("slide-right", 320, 380, dist=24, out=OUT_FADE), color="$accent"),
            text("Name", L + 232, T, 560, 76, nm, 46, anim("slide-right", 360, 420, dist=30, out=OUT_FADE)),
            text("Tag", L + 790, T, 180, 76, tag, 22, anim("fade", 300, 520, out=OUT_FADE), align="right", color="#FFFFFF@0.75", weight=700, fit=True),
            box("Stat strip", L + 126, T + 76, 860, 52, "#FFFFFF@0.94", anim("wipe-right", 460, 320, out={"type": "wipe-left", "dur": 280, "delay": 0, "ease": "in"})),
            text("Today label", L + 144, T + 76, 100, 52, left_label, 17, anim("fade", 260, 560, out=OUT_FADE), show=left_show, color="$accent", tracking=2),
            text("Today value", L + 228, T + 76, 400 if kind == "batter" else 470, 52, left_val, 24, anim("fade", 260, 600, out=OUT_FADE, change="flash"), show=left_show, color="$primary", weight=700),
            text("Season", L + 600 if kind == "batter" else L + 700, T + 76, 370 if kind == "batter" else 270, 52, right, 22, anim("fade", 260, 640, out=OUT_FADE), align="right", color="$primary", weight=700),
        ] + sponsor_tab(L + 686, T - 48, 300, 44, 560),
    }


custom_lt = {
    "name": "Custom Lower Third", "group": "lower", "autoHide": 0, "side": "", "sided": False,
    "elements": [
        box("Accent bar", 180, 842, 14, 128, "$accent", anim("grow-y", 280, 0, origin="center bottom", out={"type": "fade", "dur": 200, "delay": 260, "ease": "in"})),
        box("Panel", 194, 842, 980, 80, "$panel", anim("wipe-right", 460, 120, out={"type": "wipe-left", "dur": 300, "delay": 80, "ease": "in"})),
        text("Line 1", 220, 842, 930, 80, "{custom.line1|upper}", 44, anim("slide-right", 360, 320, dist=30, out=OUT_FADE)),
        box("Strip", 194, 922, 980, 48, "$primary@0.95", anim("wipe-right", 460, 260, out={"type": "wipe-left", "dur": 260, "delay": 0, "ease": "in"}), show="custom.line2"),
        text("Line 2", 220, 922, 930, 48, "{custom.line2}", 24, anim("fade", 300, 520, out=OUT_FADE), show="custom.line2", color="#FFFFFF@0.9", weight=600),
    ],
}

# ------------------------------------------------------------------ matchup
matchup = {
    "name": "Matchup", "group": "lower", "autoHide": 10, "side": "", "sided": False,
    "elements": [
        box("Pitcher panel", 190, 846, 720, 124, "$panel", anim("slide-right", 460, 0, dist=90, out={"type": "slide-left", "dur": 300, "delay": 0, "ease": "in", "dist": 90})),
        box("Pitcher color", 190, 846, 10, 124, "{fielding.color}", anim("grow-y", 300, 200, out=OUT_FADE)),
        text("Pitching label", 222, 852, 300, 30, "PITCHING  |  {fielding.abbr}", 16, anim("fade", 260, 300, out=OUT_FADE), color="$accent", tracking=2),
        text("Pitcher name", 222, 880, 600, 52, "{pitcher.name|upper}", 40, anim("slide-right", 320, 340, dist=20, out=OUT_FADE)),
        text("Pitcher line", 222, 930, 660, 34, "{pitcher.today.ip} IP   {pitcher.today.k} K   PC {pitcher.today.pc|zero}   ERA {pitcher.season.era|era}", 21, anim("fade", 260, 420, out=OUT_FADE), color="#FFFFFF@0.8", weight=600),
        box("Batter panel", 1010, 846, 720, 124, "$panel", anim("slide-left", 460, 0, dist=90, out={"type": "slide-right", "dur": 300, "delay": 0, "ease": "in", "dist": 90})),
        box("Batter color", 1720, 846, 10, 124, "{batting.color}", anim("grow-y", 300, 200, out=OUT_FADE)),
        text("Batting label", 1040, 852, 660, 30, "{batting.abbr}  |  AT BAT", 16, anim("fade", 260, 300, out=OUT_FADE), color="$accent", tracking=2, align="right"),
        text("Batter name", 1040, 880, 660, 52, "{batter.name|upper}", 40, anim("slide-left", 320, 340, dist=20, out=OUT_FADE), align="right"),
        text("Batter line", 1040, 930, 660, 34, "{batter.today.line}   AVG {batter.season.avg|avg}   HR {batter.season.hr|zero}", 21, anim("fade", 260, 420, out=OUT_FADE), color="#FFFFFF@0.8", weight=600, align="right"),
        box("VS disc", 910, 858, 100, 100, "$accent", anim("pop", 460, 320, out={"type": "scale", "dur": 220, "delay": 0, "ease": "in"}), radius=50, shadow=True),
        text("VS", 910, 858, 100, 100, "VS", 34, anim("pop", 460, 380, out=OUT_FADE), align="center", color="$primary"),
    ],
}

# ------------------------------------------------------------------ lineup
LX, LY, LW = 140, 110, 780
lineup = {
    "name": "Lineup", "group": "full", "autoHide": 0, "side": "home", "sided": True,
    "elements": [
        box("Body", LX, LY + 104, LW, 690, "$panel", anim("wipe-down", 520, 160, out={"type": "wipe-up", "dur": 360, "delay": 140, "ease": "in"}), shadow=True),
        box("Header", LX, LY, LW, 104, "{team.color}", anim("wipe-right", 460, 0, out={"type": "wipe-left", "dur": 320, "delay": 300, "ease": "in"})),
        box("Header stripe", LX, LY + 98, LW, 6, "$accent", anim("grow-x", 380, 240, out=OUT_FADE)),
        text("Team name", LX + 28, LY + 8, 560, 58, "{team.name|upper}", 40, anim("slide-right", 360, 220, dist=30, out=OUT_FADE)),
        text("Subtitle", LX + 28, LY + 60, 560, 34, "STARTING LINEUP", 20, anim("fade", 300, 320, out=OUT_FADE), color="#FFFFFF@0.8", tracking=4, weight=700),
        text("Record", LX + LW - 220, LY, 196, 98, "{team.record}", 28, anim("fade", 300, 360, out=OUT_FADE), align="right"),
        el("table", "Lineup table", LX + 16, LY + 124, LW - 32, 560,
           anim("none", 1, 0, out=OUT_FADE, rows={"type": "slide-right", "dur": 320, "stagger": 55, "delay": 300, "dist": 40}),
           bind="team.lineup",
           columns=[
               {"label": "", "field": "slot", "w": 0.7, "align": "center", "color": "$accent", "weight": 800},
               {"label": "", "field": "{row.name|upper}", "w": 4.6, "align": "left"},
               {"label": "", "field": "pos", "w": 1, "align": "center", "color": "#FFFFFF@0.75"},
               {"label": "", "field": "{row.avg|avg}", "w": 1.3, "align": "right"},
           ],
           style={"rowH": 58, "size": 30, "weight": 700, "color": "$text", "rowFill": "", "altFill": "#FFFFFF@0.05",
                  "header": False, "padX": 12, "gap": 4, "highlight": "isCurrent", "highlightFill": "$accent@0.35", "maxRows": 9}),
        box("Footer", LX, LY + 714, LW, 80, "$primary@0.96", anim("wipe-up", 360, 520, out=OUT_FADE)),
        text("SP label", LX + 28, LY + 718, 300, 30, "STARTING PITCHER", 16, anim("fade", 260, 640, out=OUT_FADE), color="$accent", tracking=3),
        text("SP name", LX + 28, LY + 744, 500, 44, "{team.sp.name|upper}", 30, anim("fade", 260, 680, out=OUT_FADE)),
        text("SP ERA", LX + LW - 240, LY + 714, 216, 80, "ERA {team.sp.era|era}", 26, anim("fade", 260, 700, out=OUT_FADE), align="right", show="team.sp.era"),
    ],
}

# ----------------------------------------------------------------- defense
defense = {
    "name": "Defense", "group": "full", "autoHide": 0, "side": "home", "sided": True,
    "elements": [
        box("Header", 560, 56, 800, 84, "{team.color}", anim("wipe-center", 420, 0, out={"type": "wipe-center", "dur": 300, "delay": 300, "ease": "in"}), shadow=True),
        box("Header stripe", 560, 134, 800, 6, "$accent", anim("grow-x", 380, 200, origin="center center", out=OUT_FADE)),
        text("Title", 560, 56, 800, 78, "{team.name|upper} DEFENSE", 38, anim("fade", 300, 240, out=OUT_FADE), align="center"),
        el("field", "Field", 360, 160, 1200, 860,
           anim("fade", 520, 120, out={"type": "fade", "dur": 300, "delay": 0, "ease": "in"},
                rows={"type": "pop", "dur": 380, "stagger": 70, "delay": 380}),
           bind="team.defense",
           style={"grass": "#1F6B3A@0.42", "dirt": "#B5835A@0.5", "line": "#FFFFFF@0.75", "labelFill": "$primary@0.94",
                  "nameColor": "$text", "posColor": "$accent", "size": 26, "nameField": "last"}),
    ],
}

# ---------------------------------------------------------------- pitching
PX, PY, PW = 1000, 150, 780
pitching = {
    "name": "Pitching Line", "group": "full", "autoHide": 0, "side": "home", "sided": True,
    "elements": [
        box("Header", PX, PY, PW, 96, "{team.color}", anim("wipe-left", 440, 0, out={"type": "wipe-right", "dur": 320, "delay": 260, "ease": "in"}), shadow=True),
        box("Header stripe", PX, PY + 90, PW, 6, "$accent", anim("grow-x", 360, 220, origin="right center", out=OUT_FADE)),
        text("Title", PX + 28, PY + 6, 520, 56, "{team.abbr} PITCHING", 40, anim("slide-left", 340, 220, dist=30, out=OUT_FADE)),
        text("Subtitle", PX + 28, PY + 56, 520, 32, "TODAY", 18, anim("fade", 300, 320, out=OUT_FADE), color="#FFFFFF@0.8", tracking=4),
        el("table", "Pitchers table", PX, PY + 96, PW, 520,
           anim("none", 1, 0, out=OUT_FADE, rows={"type": "slide-left", "dur": 320, "stagger": 70, "delay": 300, "dist": 40}),
           bind="team.pitchers",
           columns=[
               {"label": "PITCHER", "field": "{row.name|upper}", "w": 4, "align": "left"},
               {"label": "IP", "field": "ip", "w": 1, "align": "center"},
               {"label": "H", "field": "h", "w": 0.8, "align": "center"},
               {"label": "R", "field": "r", "w": 0.8, "align": "center"},
               {"label": "ER", "field": "er", "w": 0.8, "align": "center"},
               {"label": "BB", "field": "bb", "w": 0.8, "align": "center"},
               {"label": "K", "field": "k", "w": 0.8, "align": "center"},
               {"label": "PC", "field": "pc", "w": 1, "align": "center", "color": "$accent"},
           ],
           style={"rowH": 60, "size": 26, "weight": 700, "color": "$text", "rowFill": "$panel", "altFill": "$panel2",
                  "header": True, "headerH": 44, "headerSize": 17, "headerColor": "$accent", "headerFill": "$primary@0.96",
                  "padX": 16, "gap": 2, "highlight": "isCurrent", "highlightFill": "$accent@0.3", "maxRows": 8}),
    ],
}

# --------------------------------------------------------------- linescore
linescore = {
    "name": "Linescore", "group": "full", "autoHide": 0, "side": "", "sided": False,
    "elements": [
        box("Status tab", 410, 800, 240, 46, "$accent", anim("wipe-up", 300, 300, out={"type": "wipe-down", "dur": 220, "delay": 0, "ease": "in"})),
        text("Status", 410, 800, 240, 46, "{statusText}", 22, anim("fade", 260, 420, out=OUT_FADE), align="center", color="$primary", tracking=2),
        el("linescore", "Linescore", 410, 846, 1100, 150,
           anim("wipe-up", 460, 0, out={"type": "wipe-down", "dur": 340, "delay": 120, "ease": "in"},
                rows={"type": "slide-left", "dur": 320, "stagger": 90, "delay": 220, "dist": 40}),
           style={"size": 32, "color": "$text", "headColor": "$accent", "headSize": 18, "rowFill": "$panel",
                  "totalFill": "$primary@0.96", "current": "$accent@0.28", "minInnings": 9, "teamW": 130}),
    ],
}

# ------------------------------------------------------------------ due up
dueup = {
    "name": "Due Up", "group": "", "autoHide": 0, "side": "home", "sided": True,
    "elements": [
        box("Header", 1440, 640, 420, 64, "{team.color}", anim("wipe-left", 380, 0, out={"type": "wipe-right", "dur": 280, "delay": 220, "ease": "in"}), shadow=True),
        box("Header stripe", 1440, 700, 420, 4, "$accent", anim("grow-x", 300, 180, origin="right center", out=OUT_FADE)),
        text("Title", 1462, 640, 380, 60, "{team.abbr}  DUE UP", 30, anim("slide-left", 300, 200, dist=20, out=OUT_FADE)),
        el("table", "Due up table", 1440, 704, 420, 200,
           anim("none", 1, 0, out=OUT_FADE, rows={"type": "slide-left", "dur": 300, "stagger": 80, "delay": 260, "dist": 30}),
           bind="team.dueUp",
           columns=[
               {"label": "", "field": "{row.name|upper}", "w": 3.4, "align": "left"},
               {"label": "", "field": "{row.avg|avg}", "w": 1, "align": "right", "color": "$accent"},
           ],
           style={"rowH": 62, "size": 26, "weight": 700, "color": "$text", "rowFill": "$panel", "altFill": "$panel2",
                  "header": False, "padX": 18, "gap": 2, "highlight": "", "maxRows": 3}),
    ],
}

doc = {
    "name": "Classic Bar",
    "description": "Navy and orange bar package: square panels, wipes, team-color blocks.",
    "version": 1,
    "theme": {
        "primary": "#0A2240",
        "accent": "#F5821F",
        "text": "#FFFFFF",
        "panel": "rgba(8,18,36,0.86)",
        "panel2": "rgba(18,36,64,0.86)",
        "font": "Bahnschrift, 'DIN Alternate', 'DIN Condensed', 'Barlow Semi Condensed', 'Roboto Condensed', 'Arial Narrow', Arial, sans-serif",
    },
    "graphics": {
        "scorebug": scorebug,
        "batter": lower_third("batter"),
        "pitcher": lower_third("pitcher"),
        "matchup": matchup,
        "custom": custom_lt,
        "lineup": lineup,
        "defense": defense,
        "pitching": pitching,
        "linescore": linescore,
        "dueup": dueup,
    },
}

STX, STY, STW = 560, 110, 800
doc["graphics"]["standings"] = {
    "name": "Standings", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True,
    "elements": [
        box("Header", STX, STY, STW, 96, "$primary", anim("wipe-right", 440, 0, out={"type": "wipe-left", "dur": 320, "delay": 260, "ease": "in"}), shadow=True),
        box("Header stripe", STX, STY + 90, STW, 6, "$accent", anim("grow-x", 360, 220, out=OUT_FADE)),
        text("Title", STX + 28, STY + 6, 560, 56, "{standingsGroup.name|upper}", 40, anim("slide-right", 340, 220, dist=30, out=OUT_FADE)),
        text("Subtitle", STX + 28, STY + 56, 520, 32, "{seasonYear} STANDINGS", 18, anim("fade", 300, 320, out=OUT_FADE), color="#FFFFFF@0.8", tracking=4),
        el("table", "Teams", STX, STY + 96, STW, 760,
           anim("none", 1, 0, out=OUT_FADE, rows={"type": "slide-right", "dur": 320, "stagger": 60, "delay": 300, "dist": 40}),
           bind="standingsGroup.teams",
           columns=[{"label": "", "field": "rank", "w": 0.5, "align": "center", "color": "$accent", "weight": 800},
                    {"label": "", "field": "{row.logo}", "w": 0.8, "align": "center", "image": True, "imgH": 76},
                    {"label": "TEAM", "field": "{row.name|upper}", "w": 4, "align": "left"},
                    {"label": "W", "field": "w", "w": 0.8, "align": "center"},
                    {"label": "L", "field": "l", "w": 0.8, "align": "center"},
                    {"label": "PCT", "field": "pct", "w": 1, "align": "center"},
                    {"label": "GB", "field": "gb", "w": 0.9, "align": "center", "color": "$accent"}],
           style={"rowH": 62, "size": 26, "weight": 700, "color": "$text", "rowFill": "$panel", "altFill": "$panel2",
                  "header": True, "headerH": 44, "headerSize": 17, "headerColor": "$accent", "headerFill": "$primary@0.96",
                  "padX": 12, "gap": 2, "highlight": "isGame", "highlightFill": "$accent@0.3", "maxRows": 11}),
    ],
}
# Every other graphic type, from the shared broadcast library in this package's square navy-and-orange look
CB = dict(BL.NETWORK, key="classicbar", font="$font", body="$font", up=True, radius=0, cardRadius=0,
          panel="rgba(8,18,36,0.92)", panel2="rgba(18,36,64,0.92)", dark="rgba(4,10,22,0.95)",
          strip="rgba(255,255,255,0.96)", stripText="#0A2240", val="rgba(255,255,255,0.96)", valText="#0A2240",
          hi="$accent", hiText="#0A2240", line="#FFFFFF@0.15", shadow="0 12px 30px rgba(0,0,0,.4)", cardIn="wipe-right",
          teamGrad="linear-gradient(180deg, {%s.color}, {%s.color} 62%%, color-mix(in srgb, {%s.color} 70%%, #000))",
          titleBg="radial-gradient(ellipse at 70% 30%, #1B3D6E, #0A2240 55%, #040C18)")
import skin as SK  # noqa: E402
ORIG = set(doc["graphics"])
MS = dict(CB, **SK.MARKS)
lib = BL.all_new(MS)
KEEP = ("batter_tall", "pitcher_tall", "feature", "sp_compare", "sp_today", "final", "summary", "performers", "matchup_banner",
        "side_defense", "side_plays", "hr_event", "hr_tracker", "wp_event", "show_bp", "show_pregame", "show_postgame", "team_title",
        "show_bug", "up_next", "talent", "ticker", "bp_info", "league_bug", "umpires", "def_lineup", "split_card", "brand_bumper",
        "tonight", "lineup_results", "pitchers_today", "probables", "stat_card_one", "word_bumper", "road_ahead", "around_league",
        "open_station") + tuple(BL.pro_suite(CB))
for gid, gdef in lib.items():
    if gid in KEEP or gid.startswith(("tr_", "lay_")) or gid in BL.auto_game(CB) or gid in BL.extra_graphics(CB):
        if gid not in doc["graphics"]:
            doc["graphics"][gid] = gdef
doc["graphics"]["batter_card"] = BL.stat_card_tonight(MS, "bat")
doc["graphics"]["pitcher_card"] = BL.stat_card_tonight(MS, "pit")
doc["graphics"]["scorebug"]["group"] = "bug"
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in doc["graphics"] and gid not in ("scorebug", "batter", "pitcher"):
        doc["graphics"][gid]["sponsorSlot"] = slot
for gid in BL.PICKABLE:
    if gid in doc["graphics"]:
        doc["graphics"][gid]["pickable"] = True
doc["theme"].update({"dim": "rgba(255,255,255,0.74)", "line": "rgba(255,255,255,0.18)", "card": "rgba(8,18,36,0.92)",
                     "font2": doc["theme"]["font"], "logo": "", "brandName": "", "openerVideo": ""})

# Sponsor rules: first slot with an active sponsor wins (see the Night Game builder for the slot names).
for gid, slot in (("scorebug", "half_{halfKey}, scorebug"), ("batter", "lineup_{batter.slot}, batter"), ("pitcher", "pitcher")):
    doc["graphics"][gid]["sponsorSlot"] = slot

import sports_lib as SL  # noqa: E402
doc["graphics"].update(SL.all_sports(MS))     # basketball, football, hockey
# Skin: everything added from the shared library is redrawn like the original Classic Bar graphics
# (square navy panels, white strips with navy type, orange accent bars, flat team-colour blocks).
K = dict(panel="rgba(8,18,36,0.9)", panel2="rgba(18,36,64,0.9)", dark="rgba(4,10,22,0.95)", strip="rgba(255,255,255,0.96)", stripText="#0A2240",
         val="rgba(255,255,255,0.96)", ink="#0A2240", hi="#F5821F", hiText="#0A2240", hiDark=True, line="rgba(255,255,255,0.15)",
         title=CB["titleBg"], shadow="0 10px 24px rgba(0,0,0,.45)", team=lambda t: "{%s.color}" % t, rule="#F5821F", text2="#FFFFFF", radius=0,
         noBlur=True, panelBox={"radius": 0, "shadow": "0 10px 24px rgba(0,0,0,.45)"}, lightBox={"radius": 0}, hiBox={"radius": 0},
         text={"textShadow": ""}, textDark={"textShadow": ""})
import rebuild as RB  # noqa: E402
_NAVY = "#0A2240"
_OR = "#F5821F"


def kit_tr_cb(gid, g, TA):
    """Navy field, square orange-edged band, white word, orange rule."""
    E = [BL.box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg="linear-gradient(180deg, #0F2A4D, #040C18)"),
         BL.box("Accent", 0, 0, 24, 1080, _OR, TA("grow-y", 360, 100)),
         BL.box("Band", 0, 390, 1920, 300, "rgba(8,18,36,0.92)", TA("wipe-right", 420, 120)),
         BL.box("Stripe", 0, 684, 1920, 8, _OR, TA("grow-x", 360, 260)),
         BL.box("Team block", 0, 390, 40, 300, "{team.color}", TA("grow-y", 300, 200))]
    return {"elements": E, "word": {"font": "$font", "weight": 800, "color": "#FFFFFF", "textShadow": "", "rect": (80, 400, 1760, 220)},
            "sub": {"font": "$font", "weight": 700, "color": "#FFFFFF@0.85", "textShadow": "", "tracking": 4, "rect": (80, 600, 1760, 80)},
            "brand": {"rect": (860, 160, 200, 160)}}


def kit_lower_cb(U, M, g):
    x, y, w, h = M
    return [BL.box("Accent bar", x - 14, y, 14, h, _OR, BL.A("grow-y", 280, 0, origin="center bottom", out={"type": "fade", "dur": 200, "delay": 300, "ease": "in"}))] if x >= 14 else []


def kit_slab(R, slab, g):
    x, y, w, h = R
    return [dict(BL.box("Stripe", 0, y + h - 8, 1920, 8, _OR, BL.A("grow-x", 300, 140)), _over=True),
            dict(BL.box("Accent", 0, y, 24, h, _OR, BL.A("grow-y", 300, 100)), _over=True)]

def kit_screen(bg, team, g):
    over = [BL.box("Accent", 0, 0, 24, 1080, _OR, BL.A("grow-y", 360, 100)),
            BL.box("Stripe", 0, 1072, 1920, 8, _OR, BL.A("grow-x", 360, 160))]
    return {"floor": "linear-gradient(180deg, #F5821F 0 8px, #0A2240 8px)", "replace": "linear-gradient(180deg, #0F2A4D, #040C18)", "over": over}

KIT = RB.make_kit(dict(
    screen=kit_screen,
    slab=kit_slab,
    body="rgba(8,18,36,0.92)", bodyBox={"shadow": "0 12px 30px rgba(0,0,0,.4)"},
    head=_NAVY, headRule=_OR, headRuleH=6, sub="rgba(255,255,255,0.96)",
    title={"font": "$font", "weight": 800, "color": "#FFFFFF", "textShadow": "", "italic": False},
    headText={"textShadow": ""}, subText={"font": "$font", "weight": 700, "color": _NAVY, "textShadow": ""},
    roles={"PANEL": "rgba(8,18,36,0.92)", "PANEL2": "rgba(18,36,64,0.92)", "DARK": "rgba(4,10,22,0.95)", "STRIP": "rgba(255,255,255,0.96)"},
    barBox={"radius": 0}, mainBox={"shadow": "0 12px 30px rgba(0,0,0,.4)"}, lowerDecor=kit_lower_cb,
    tile={"radius": 0, "borderW": 0, "background": _NAVY}, tr=kit_tr_cb))

doc["graphics"] = RB.rebuild_all(doc["graphics"], KIT, only=set(doc["graphics"]) - ORIG)
doc["graphics"] = RB.strip_flags(SK.skin_all(doc["graphics"], K, only=set(doc["graphics"]) - ORIG))
doc["graphics"]["matchup"]["sport"] = "baseball"   # pitcher vs batter
os.makedirs(os.path.dirname(OUT), exist_ok=True)
BL.stamp(doc)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", OUT, "graphics:", len(doc["graphics"]))
