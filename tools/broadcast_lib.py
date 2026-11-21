"""Shared generators for the network-style graphics (scorebugs, stat bars, stat cards, comparisons, game
final / summary, top performers, matchups, side panels, event stingers and show graphics).

Every generator takes a style dict S, so the same layouts are built in the Network look and in the
Night Game look. Layouts and motion follow common broadcast conventions; all artwork is original
(web/art/*.svg) and team marks come from your own media / data.
"""

_n = [0]


def nid(p):
    _n[0] += 1
    return "%s%d" % (p, _n[0])


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


OUT = {"type": "fade", "dur": 240, "delay": 0, "ease": "in"}


def box(name, x, y, w, h, fill=None, a=None, show=None, bg=None, **st):
    s = {}
    if fill is not None:
        s["fill"] = fill
    if bg:
        s["background"] = bg
    s.update(st)
    e = {"id": nid("b"), "name": name, "type": "box", "x": x, "y": y, "w": w, "h": h, "style": s, "anim": a or A()}
    if show:
        e["showIf"] = show
    return e


def txt(name, x, y, w, h, text, size=32, a=None, show=None, **st):
    s = {"color": "$text", "size": size, "weight": 700, "align": "left", "valign": "center", "padX": 0, "fit": True}
    s.update(st)
    e = {"id": nid("t"), "name": name, "type": "text", "x": x, "y": y, "w": w, "h": h, "text": text, "style": s, "anim": a or A()}
    if show:
        e["showIf"] = show
    return e


def img(name, x, y, w, h, src, a=None, show=None, opacity=None, **st):
    s = {"fit": "contain", "focus": "center"}
    s.update(st)
    e = {"id": nid("i"), "name": name, "type": "image", "x": x, "y": y, "w": w, "h": h, "src": src, "style": s, "anim": a or A()}
    if show:
        e["showIf"] = show
    if opacity is not None:
        e["opacity"] = opacity
    return e


def el(kind, name, x, y, w, h, a=None, show=None, **kw):
    e = {"id": nid(kind[0]), "name": name, "type": kind, "x": x, "y": y, "w": w, "h": h, "anim": a or A()}
    e.update(kw)
    if show:
        e["showIf"] = show
    return e


def both(*conds):
    return " && ".join(c for c in conds if c)


def logo_or_abbr(name, x, y, w, h, team, size, a, show=None, color="$text", S=None):
    font = (S or {}).get("font", "$font2")
    return [img(name + " logo", x, y, w, h, "{%s.logo}" % team, a, show=both("%s.logo" % team, show)),
            txt(name + " abbr", x, y, w, h, "{%s.abbr}" % team, size, a, show=both("!%s.logo" % team, show), align="center", weight=800, color=color, font=font)]


def sponsor_tab(x, y, w, h, delay, radius=4, a_type="wipe-up", label_w=None, fill="#FFFFFF@0.97"):
    lw = label_w or int(w * 0.42)
    pad = max(6, int(h * 0.14))
    on = "sponsor.on"
    return [
        box("Sponsor bg", x, y, w, h, fill, A(a_type, 360, delay, out=OUT), show=on, radius=radius, shadow=True),
        txt("Sponsor label", x + pad, y, lw - pad, h, "{sponsor.label}", min(22, max(12, int(h * 0.32))), A("fade", 260, delay + 180), show=on + " && sponsor.label",
            weight=600, color="#4A5262"),
        img("Sponsor logo", x + lw, y + pad, w - lw - pad, h - 2 * pad, "{sponsor.logo}", A("fade", 300, delay + 220, change="fade"), show=on + " && sponsor.logo && sponsor.label"),
        img("Sponsor logo (no label)", x + pad, y + pad, w - 2 * pad, h - 2 * pad, "{sponsor.logo}", A("fade", 300, delay + 220, change="fade"),
            show=on + " && sponsor.logo && !sponsor.label"),
        txt("Sponsor name", x + lw, y, w - lw - pad, h, "{sponsor.name}", max(14, int(h * 0.42)), A("fade", 260, delay + 220, change="fade"),
            show=on + " && !sponsor.logo && sponsor.label", weight=800, color="#121620", align="right"),
        txt("Sponsor name (no label)", x + pad, y, w - 2 * pad, h, "{sponsor.name}", max(14, int(h * 0.42)), A("fade", 260, delay + 220, change="fade"),
            show=on + " && !sponsor.logo && !sponsor.label", weight=800, color="#121620", align="center"),
    ]


# ---------------------------------------------------------------- styles
NETWORK = {
    "key": "network",
    "font": "$font2", "body": "$font2", "up": True, "radius": 3, "cardRadius": 4,
    "panel": "linear-gradient(180deg, #1D4280 0%, #0E2A5C 52%, #091D44 100%)",
    "panel2": "linear-gradient(180deg, #13305F, #0A2149)",
    "dark": "linear-gradient(180deg, #0A1A38, #050E22)",
    "strip": "linear-gradient(180deg, #FFFFFF, #D6DCE5)", "stripText": "#0A1F44",
    "val": "linear-gradient(180deg, #FFFFFF, #E1E6EE)", "valText": "#0A1F44",
    "hi": "$accent", "hiText": "#0A1F44", "line": "#FFFFFF@0.22",
    "shadow": "0 18px 40px rgba(0,0,0,.45)", "in": "wipe-right", "cardIn": "zoom-out",
    "teamGrad": "linear-gradient(180deg, color-mix(in srgb, {%s.color} 82%%, #fff), {%s.color} 45%%, color-mix(in srgb, {%s.color} 70%%, #000))",
    "showBg": "linear-gradient(160deg, color-mix(in srgb, $accentA 0%, #5BA9F0), #2C79D6 45%, #12408E)",
}
NIGHT = {
    "key": "night",
    "font": "$font", "body": "$font", "up": False, "radius": 14, "cardRadius": 24,
    "panel": "rgba(20,21,24,0.90)",
    "panel2": "rgba(34,36,40,0.90)",
    "dark": "rgba(10,11,13,0.92)",
    "strip": "rgba(255,255,255,0.94)", "stripText": "#16181C",
    "val": "rgba(255,255,255,0.08)", "valText": "#FFFFFF",
    "hi": "$accent", "hiText": "#16181C", "line": "#FFFFFF@0.18",
    "shadow": "0 30px 80px rgba(0,0,0,.45)", "in": "fade", "cardIn": "zoom-out",
    "teamGrad": "linear-gradient(180deg, color-mix(in srgb, {%s.color} 60%%, #1a1d22), color-mix(in srgb, {%s.color} 30%%, #121417) 60%%, color-mix(in srgb, {%s.color} 12%%, #121417))",
    "showBg": "",
}


def U(S, path, extra=""):
    """Binding with |upper in the network look."""
    return "{%s%s%s}" % (path, extra, "|upper" if S["up"] else "")


def L(S, text):
    """Upper-case the literal words only; {data tokens} keep their case."""
    if not S["up"]:
        return text
    import re
    return "".join(p if p.startswith("{") else p.upper() for p in re.split(r"(\{[^}]*\})", text))


def TG(S, team):
    return S["teamGrad"] % (team, team, team)


def card(S, name, x, y, w, h, delay=0, **kw):
    if S["key"] == "night":
        return box(name, x, y, w, h, "$card", A("zoom-out", 520, delay, out={"type": "fade", "dur": 300, "delay": 120, "ease": "in"}),
                   radius=S["cardRadius"], blur=22, shadow=S["shadow"], **kw)
    return box(name, x, y, w, h, None, A("zoom-out", 460, delay, out={"type": "fade", "dur": 280, "delay": 120, "ease": "in"}),
               bg=S["panel"], radius=S["cardRadius"], shadow=S["shadow"], borderW=2, borderColor="#FFFFFF@0.25", **kw)


LIVE = "inPlay"


# ================================================================ SCOREBUGS
def scorebug_network(S):
    """Stacked pitcher / batter rows over the score row, bases under the centre (network corner bug)."""
    X, W = 1430, 440
    f = S["font"]
    E = sponsor_tab(X, 814, W, 42, 560, radius=S["radius"], a_type="wipe-up")
    E += [
        box("Pitcher row", X, 860, W, 38, None, A("wipe-down", 300, 260), show=LIVE, bg=S["dark"]),
        txt("Pitcher", X + 14, 860, 280, 38, U(S, "pitcher.last"), 24, A("fade", 240, 420), show=both(LIVE, "pitcher.last"), font=f, weight=800),
        txt("P-S", X + 260, 860, W - 274, 38, "P-S {pitcher.today.pc|zero}-{pitcher.today.st|zero}", 24, A("fade", 240, 440, change="flash"),
            show=both(LIVE, "pitcher.last"), font=f, weight=800, align="right", color="$accent"),
        box("Batter row", X, 898, W, 38, None, A("wipe-down", 300, 320), show=LIVE, bg=S["panel2"]),
        txt("Batter", X + 14, 898, 300, 38, "{batter.slot|dot}" + U(S, "batter.last"), 24, A("fade", 240, 460), show=both(LIVE, "batter.last"), font=f, weight=800),
        txt("Batter line", X + 300, 898, W - 314, 38, "{batter.today.hab}", 24, A("fade", 240, 480, change="flash"), show=both(LIVE, "batter.last"),
            font=f, weight=800, align="right"),
        box("Away block", X, 936, 150, 82, None, A(S["in"], 380, 0), bg=TG(S, "away")),
        img("Away mark", X + 70, 940, 80, 74, "{away.logo}", A("fade", 300, 200), show="away.logo", opacity=0.32),
        txt("Away", X + 12, 938, 130, 30, U(S, "away.abbr"), 24, A("fade", 260, 260), font=f, weight=800, textShadow=True),
        txt("Away runs", X + 12, 964, 130, 54, "{away.runs}", 52, A("reveal-up", 320, 300, change="pop"), font=f, weight=800, textShadow=True),
        box("Centre", X + 150, 936, 140, 82, None, A("wipe-down", 360, 120), bg=S["strip"]),
        txt("Inning + count", X + 150, 938, 140, 40, "{arrow}{inning}  {count}", 28, A("fade", 260, 360, change="roll"), show=LIVE, font=f, weight=800,
            align="center", color=S["stripText"]),
        txt("Outs", X + 150, 974, 140, 40, "{outs} {outsWord}", 26, A("fade", 260, 380, change="flash"), show=LIVE, font=f, weight=800, align="center",
            color=S["stripText"]),
        txt("Final", X + 150, 936, 140, 82, "{statusText}", 26, A("fade", 260, 360), show="!" + LIVE, font=f, weight=800, align="center", color=S["stripText"]),
        box("Home block", X + 290, 936, 150, 82, None, A(S["in"], 380, 80), bg=TG(S, "home")),
        img("Home mark", X + 290, 940, 80, 74, "{home.logo}", A("fade", 300, 240), show="home.logo", opacity=0.32),
        txt("Home", X + 298, 938, 130, 30, U(S, "home.abbr"), 24, A("fade", 260, 300), font=f, weight=800, align="right", textShadow=True),
        txt("Home runs", X + 298, 964, 130, 54, "{home.runs}", 52, A("reveal-up", 320, 340, change="pop"), font=f, weight=800, align="right", textShadow=True),
        el("bases", "Bases", X + 160, 1016, 120, 44, A("pop", 380, 420), show=LIVE, bind="bases",
           style={"layout": "tight", "on": "$accent", "off": "#FFFFFF@0.85", "stroke": "#0A1F44@0.6", "strokeW": 2}),
    ]
    return {"name": "Scorebug: Network", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E}


def scorebug_bar(S):
    """Top-left bar: team blocks with pitcher / batter sub-row, bases + inning, count + outs."""
    X, Y = 50, 36
    f = S["font"]
    E = []
    for i, side in enumerate(("away", "home")):
        bx = X + i * 286
        d = 70 * i
        E += [
            box("%s block" % side, bx, Y, 282, 62, None, A("wipe-down", 360, d), bg=TG(S, side)),
            img("%s logo" % side, bx + 8, Y + 6, 56, 50, "{%s.logo}" % side, A("pop", 360, 200 + d), show="%s.logo" % side),
            txt("%s abbr" % side, bx + 70, Y, 120, 62, U(S, "%s.abbr" % side), 36, A("reveal-up", 300, 220 + d), font=f, weight=800, textShadow=True),
            box("%s runs bg" % side, bx + 196, Y + 6, 80, 50, None, A("fade", 260, 240 + d), bg=S["val"], radius=S["radius"]),
            txt("%s runs" % side, bx + 196, Y + 6, 80, 50, "{%s.runs}" % side, 42, A("reveal-up", 300, 300 + d, change="pop"), font=f, weight=800,
                align="center", color=S["valText"]),
            box("%s sub" % side, bx, Y + 62, 282, 34, None, A("wipe-down", 280, 300 + d), bg=S["dark"]),
            txt("%s pitcher" % side, bx + 10, Y + 62, 170, 34, U(S, "pitcher.last"), 21, A("fade", 240, 440 + d),
                show="fieldingSide==%s && pitcher.last && %s" % (side, LIVE), font=f, weight=700),
            txt("%s P-S" % side, bx + 166, Y + 62, 106, 34, "P-S {pitcher.today.pc|zero}-{pitcher.today.st|zero}", 21, A("fade", 240, 460 + d, change="flash"),
                show="fieldingSide==%s && pitcher.last && %s" % (side, LIVE), font=f, weight=800, align="right", color="$accent"),
            txt("%s batter" % side, bx + 10, Y + 62, 200, 34, "{batter.slot|dot}" + U(S, "batter.last"), 21, A("fade", 240, 440 + d),
                show="battingSide==%s && batter.last && %s" % (side, LIVE), font=f, weight=700),
            txt("%s line" % side, bx + 196, Y + 62, 76, 34, "{batter.today.hab}", 21, A("fade", 240, 460 + d, change="flash"),
                show="battingSide==%s && batter.last && %s" % (side, LIVE), font=f, weight=800, align="right"),
            txt("%s record" % side, bx + 10, Y + 62, 262, 34, "{%s.record}" % side, 20, A("fade", 240, 440 + d), show="!" + LIVE, font=f, weight=700, color="$dim"),
        ]
    E += [
        box("Situation", X + 572, Y, 150, 96, None, A("wipe-right", 360, 160), bg=S["strip"]),
        el("bases", "Bases", X + 584, Y + 6, 126, 54, A("pop", 380, 360), show=LIVE, bind="bases",
           style={"layout": "tight", "on": "#0A1F44", "off": "#0A1F44@0.18", "stroke": "#0A1F44@0.6", "strokeW": 2}),
        txt("Inning", X + 572, Y + 60, 150, 34, "{arrow}{inning}", 24, A("fade", 240, 420, change="flash"), show=LIVE, font=f, weight=800, align="center",
            color=S["stripText"]),
        box("Count bg", X + 724, Y, 110, 96, None, A("wipe-right", 360, 220), bg=S["dark"]),
        txt("Count", X + 724, Y + 4, 110, 52, "{count}", 34, A("reveal-up", 300, 440, change="roll"), show=LIVE, font=f, weight=800, align="center"),
        el("dots", "Outs", X + 740, Y + 58, 78, 30, A("fade", 240, 460), show=LIVE, bind="outs",
           style={"total": 2, "size": 14, "gap": 8, "on": "#FFFFFF", "off": "#FFFFFF@0.22", "align": "center"}),
        txt("Final", X + 572, Y, 262, 96, "{statusText}", 30, A("fade", 260, 360), show="!" + LIVE, font=f, weight=800, align="center", tracking=2,
            color=S["stripText"]),
    ] + sponsor_tab(X, Y + 100, 568, 40, 520, radius=S["radius"], a_type="wipe-down")
    return {"name": "Scorebug: Network Bar", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E}


def scorebug_logos(S):
    """Logo tiles at both ends, scores, centre inning / bases / outs / count (video-game style)."""
    X, Y, H = 1290, 950, 86
    f = S["font"]
    E = [box("Frame", X, Y, 580, H, None, A("wipe-center", 420, 0), bg=S["panel"], borderW=2, borderColor="#FFFFFF@0.35", radius=S["radius"],
             shadow=True)]
    for i, side in enumerate(("away", "home")):
        tx = X + (0 if i == 0 else 580 - H)
        sx = X + (H if i == 0 else 580 - H - 110)
        E += [box("%s tile" % side, tx, Y, H, H, None, A("pop", 360, 200 + i * 60), bg=TG(S, side), radius=S["radius"])]
        E += logo_or_abbr("%s mark" % side, tx + 8, Y + 8, H - 16, H - 16, side, 30, A("pop", 360, 300 + i * 60), S=S)
        E += [txt("%s runs" % side, sx, Y + 2, 110, 58, "{%s.runs}" % side, 50, A("reveal-up", 300, 360 + i * 60, change="pop"), font=f, weight=800, align="center"),
              txt("%s abbr" % side, sx, Y + 56, 110, 26, U(S, "%s.abbr" % side), 20, A("fade", 240, 420 + i * 60), font=f, weight=800, align="center", color="$dim")]
    cx = X + H + 110
    E += [
        box("Centre", cx, Y + 6, 580 - 2 * H - 220, H - 12, None, A("fade", 300, 240), bg=S["dark"], radius=S["radius"]),
        txt("Half", cx, Y + 6, 140, 24, "{halfShort} {inning}", 18, A("fade", 240, 420), show=LIVE, font=f, weight=800, align="center"),
        el("bases", "Bases", cx + 34, Y + 28, 72, 30, A("pop", 360, 440), show=LIVE, bind="bases",
           style={"layout": "tight", "on": "#FFFFFF", "off": "#FFFFFF@0.2", "stroke": "#FFFFFF@0.6", "strokeW": 2}),
        el("dots", "Outs", cx + 6, Y + 58, 56, 20, A("fade", 240, 460), show=LIVE, bind="outs",
           style={"total": 2, "size": 11, "gap": 6, "on": "#E5483B", "off": "#FFFFFF@0.22", "align": "center"}),
        txt("Count", cx + 64, Y + 56, 70, 24, "{count}", 20, A("fade", 240, 480, change="roll"), show=LIVE, font=f, weight=800, align="center", color="$accent"),
        txt("Final", cx, Y + 6, 140, H - 12, "{statusText}", 22, A("fade", 240, 420), show="!" + LIVE, font=f, weight=800, align="center"),
    ]
    return {"name": "Scorebug: Logos", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ================================================================ LOWER THIRDS
def lower_note(S, kind):
    """Name bar over a stat-note bar, with a footnote strip (Control panel > Notes: stat note / footnote)."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y = 236, 852
    default = ("{pitcher.today.line}" if kind == "pit" else "{batter.today.line}   ·   AVG {batter.season.avg|avg}   HR {batter.season.hr|zero}   RBI {batter.season.rbi|zero}")
    E = [
        box("Emblem", 112, 858, 132, 132, None, A("pop", 420, 0, out=OUT), bg=TG(S, team), rotate=45, borderW=4, borderColor="#FFFFFF", shadow=True),
    ] + logo_or_abbr("Emblem mark", 122, 868, 112, 112, team, 34, A("pop", 380, 160), S=S) + [
        box("Name bar", X, Y, 820, 68, None, A("wipe-right", 380, 120), bg=S["panel"], borderW=1, borderColor="#FFFFFF@0.2"),
        box("Number box", X + 40, Y + 6, 66, 56, None, A("fade", 260, 300), bg=S["dark"], radius=S["radius"]),
        txt("Number", X + 40, Y + 4, 66, 34, "{%s.number}" % who, 28, A("fade", 240, 340), font=f, weight=800, align="center"),
        txt("Pos", X + 40, Y + 36, 66, 24, U(S, "%s.pos" % who), 18, A("fade", 240, 360), font=f, weight=800, align="center", color="$dim"),
        txt("Name", X + 122, Y, 680, 68, U(S, "%s.name" % who), 50, A("reveal-up", 380, 300), font=f, weight=800),
        box("Note bar", X + 30, Y + 68, 790, 56, None, A("wipe-right", 380, 260), bg=S["panel2"]),
        txt("Stat note", X + 60, Y + 68, 740, 56, U(S, "notes.stat"), 30, A("fade", 300, 520), show="notes.stat", font=f, weight=700, color="$text"),
        txt("Default line", X + 60, Y + 68, 740, 56, default, 28, A("fade", 300, 520, change="flash"), show="!notes.stat", font=f, weight=700),
        box("Footnote bar", X + 30, Y + 124, 790, 32, None, A("wipe-down", 260, 520), show="notes.statFoot", bg=S["strip"]),
        txt("Footnote", X + 30, Y + 124, 790, 32, U(S, "notes.statFoot"), 20, A("fade", 240, 640), show="notes.statFoot", font=f, weight=800, align="center",
            color=S["stripText"], tracking=1),
    ] + sponsor_tab(X + 830, Y, 250, 68, 520, radius=S["radius"], a_type="wipe-right", label_w=100)
    return {"name": "Pitcher Lower Third (Note)" if kind == "pit" else "Batter Lower Third (Note)", "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E}


def stat_bar(S, kind):
    """Baseline bar: logo, number / position, first + LAST, four stat columns."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y, W, H = 420, 898, 1080, 88
    cols = ([("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
             ("SO", "{pitcher.season.k|zero}")] if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}"), ("OBP", "{batter.season.obp|avg}")])
    E = [
        box("Logo tile", X, Y, 110, H, None, A("pop", 360, 0, out=OUT), bg=S["strip"], radius=S["radius"]),
    ] + logo_or_abbr("Logo", X + 10, Y + 8, 90, H - 16, team, 30, A("fade", 300, 200), color=S["stripText"], S=S) + [
        box("Bar", X + 114, Y, W - 114, H, None, A("wipe-right", 420, 100), bg=TG(S, team)),
        box("Num box", X + 114, Y, 64, H, None, A("fade", 260, 260), bg="#000000@0.32"),
        txt("Number", X + 114, Y + 6, 64, 42, "{%s.number}" % who, 34, A("fade", 240, 320), font=f, weight=800, align="center"),
        txt("Pos", X + 114, Y + 48, 64, 32, U(S, "%s.pos" % who), 22, A("fade", 240, 340), font=f, weight=800, align="center"),
        txt("First", X + 192, Y + 4, 330, 32, U(S, "%s.first" % who), 24, A("fade", 260, 360), font=f, weight=600, color="$dim"),
        txt("Last", X + 192, Y + 30, 330, 56, U(S, "%s.last" % who), 50, A("reveal-up", 340, 340), font=f, weight=800),
        box("Stats bg", X + 530, Y, W - 530, H, None, A("fade", 300, 300), bg="#000000@0.38"),
    ]
    cw = (W - 530) / 4.0
    for i, (lab, val) in enumerate(cols):
        cx = int(X + 530 + i * cw)
        E += [txt("%s label" % lab, cx, Y + 4, int(cw), 26, lab, 18, A("fade", 240, 420 + i * 60), font=f, weight=700, align="center", color="$dim"),
              txt("%s value" % lab, cx, Y + 26, int(cw), 58, val, 46, A("reveal-up", 320, 440 + i * 60), font=f, weight=800, align="center")]
        if i:
            E.append(box("Divider %d" % i, cx, Y + 14, 2, H - 28, "#FFFFFF@0.3", A("grow-y", 260, 400 + i * 60)))
    E += sponsor_tab(X + W - 300, Y - 50, 300, 44, 600, radius=S["radius"], a_type="wipe-up")
    return {"name": "Pitcher Stat Bar" if kind == "pit" else "Batter Stat Bar", "group": "lower", "autoHide": 9, "side": "", "sided": False, "elements": E}


# ================================================================ CARDS
def stat_card_tonight(S, kind):
    """Studio stat card: sponsor tile + title band, player row, label / value rows, photo panel."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y, W, H = 300, 110, 1320, 800
    E = [
        card(S, "Card", X, Y, W, H),
        box("Sponsor tile", X + 18, Y + 18, 170, 130, None, A("pop", 360, 300), bg=S["strip"], radius=S["radius"], show="sponsor.on"),
        img("Sponsor", X + 30, Y + 30, 146, 106, "{sponsor.logo}", A("fade", 300, 420), show="sponsor.on && sponsor.logo"),
        txt("Sponsor name", X + 26, Y + 18, 154, 130, "{sponsor.name}", 28, A("fade", 300, 420), show="sponsor.on && !sponsor.logo", color=S["stripText"],
            align="center", wrap=True, fit=False, weight=800),
        img("Brand", X + 30, Y + 30, 146, 106, "{brand.logo}", A("fade", 300, 420), show="!sponsor.on && brand.logo"),
        txt("Title", X + 214, Y + 22, W - 240, 70, L(S, "{seasonYear} Season Statistics"), 52, A("reveal-up", 380, 260), font=f, weight=800),
        txt("Games", X + 216, Y + 90, W - 240, 44, L(S, "{%s.season.g} games" % who), 30, A("fade", 300, 380), show="%s.season.g" % who, font=f, weight=700,
            color="$dim"),
        box("Rule", X + 18, Y + 162, W - 36, 4, "$accent", A("grow-x", 420, 360)),
        box("Player band", X + 18, Y + 180, 760, 110, None, A("wipe-right", 380, 400), bg=S["dark"]),
    ] + logo_or_abbr("Team", X + 32, Y + 190, 110, 90, team, 30, A("pop", 360, 520), S=S) + [
        txt("Name", X + 160, Y + 180, 600, 110, U(S, "%s.name" % who), 60, A("reveal-up", 400, 540), font=f, weight=800),
        el("table", "Stats", X + 18, Y + 306, 760, H - 330, A("none", 1, 0, rows={"type": "slide-right", "dur": 360, "stagger": 70, "delay": 640, "dist": 30}),
           bind="%s.card" % who,
           columns=[{"label": "", "field": U(S, "row.label"), "w": 2, "align": "left", "fill": S["dark"], "padX": 22, "weight": 800},
                    {"label": "", "field": "value", "w": 1.15, "align": "center", "fill": S["val"], "color": S["valText"], "weight": 800, "size": 44}],
           style={"rowH": 76, "size": 34, "weight": 800, "color": "$text", "header": False, "padX": 0, "gap": 10, "maxRows": 5, "font": f}),
        box("Photo panel", X + 798, Y + 180, W - 816, H - 198, None, A("wipe-up", 420, 380), bg=TG(S, team)),
        img("Photo logo", X + 820, Y + 210, W - 860, H - 260, "{%s.logo}" % team, A("fade", 500, 520), show="%s.logo" % team, opacity=0.22),
        img("Photo", X + 798, Y + 200, W - 816, H - 218, "{%s.photo}" % who, A("slide-up", 520, 560, dist=40), show="%s.photo" % who, fit="contain",
            focus="center bottom"),
        txt("Number", X + 798, Y + 300, W - 816, 360, "{%s.number}" % who, 260, A("fade", 400, 560), show="!%s.photo" % who, align="center", weight=800,
            color="#FFFFFF@0.3", font=f, fit=False),
        box("Base line", X + 18, Y + H - 14, W - 36, 6, "{%s.color}" % team, A("grow-x", 420, 700)),
    ]
    return {"name": "Pitcher Stat Card" if kind == "pit" else "Batter Stat Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def tall_card(S, kind):
    """Tall side card: photo over name, season label, stat rows."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y, W = 1500, 120, 330
    E = [
        card(S, "Card", X, Y, W, 840),
        box("Photo bg", X + 10, Y + 10, W - 20, 250, None, A("fade", 400, 200), bg=TG(S, team)),
        img("Photo logo", X + 120, Y + 20, W - 140, 230, "{%s.logo}" % team, A("fade", 500, 300), show="%s.logo" % team, opacity=0.25),
        img("Photo", X + 10, Y + 20, 210, 240, "{%s.photo}" % who, A("slide-up", 480, 360, dist=30), show="%s.photo" % who, fit="cover", focus="center top"),
        txt("Number", X + 10, Y + 20, 210, 240, "{%s.number}" % who, 150, A("fade", 400, 360), show="!%s.photo" % who, align="center", weight=800,
            color="#FFFFFF@0.3", font=f, fit=False),
        txt("Hand", X + 220, Y + 190, 96, 50, ("{pitcher.throws|hand}" if kind == "pit" else U(S, "batter.pos")), 30, A("fade", 300, 480), font=f, weight=800,
            align="center"),
        txt("First", X + 24, Y + 270, W - 48, 36, U(S, "%s.first" % who), 28, A("fade", 300, 420), font=f, weight=600, color="$accent"),
        txt("Last", X + 24, Y + 302, W - 48, 66, U(S, "%s.last" % who), 58, A("reveal-up", 360, 440), font=f, weight=800),
        box("Season band", X + 10, Y + 376, W - 20, 50, None, A("wipe-right", 360, 520), bg=S["panel2"]),
        txt("Season", X + 10, Y + 376, W - 20, 50, L(S, "{seasonYear} Season"), 28, A("fade", 260, 600), font=f, weight=700, align="center"),
        el("table", "Rows", X + 24, Y + 436, W - 48, 390, A("none", 1, 0, rows={"type": "slide-up", "dur": 320, "stagger": 55, "delay": 620, "dist": 14}),
           bind="%s.card" % who,
           columns=[{"label": "", "field": U(S, "row.label"), "w": 1.6, "align": "left", "weight": 600, "color": "$dim"},
                    {"label": "", "field": "value", "w": 1, "align": "right", "weight": 800, "size": 40}],
           style={"rowH": 64, "size": 22, "weight": 700, "color": "$text", "header": False, "padX": 0, "gap": 0, "rowLine": "$accent@0.6",
                  "rowLineW": 2, "maxRows": 6, "font": f}),
    ]
    return {"name": "Pitcher Tall Card" if kind == "pit" else "Batter Tall Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def feature_card(S):
    """Feature: kicker, big title (or the batter's name), three bullets, photo, footnote."""
    f = S["font"]
    X, Y, W, H = 160, 150, 1600, 720
    E = [card(S, "Card", X, Y, W, H)]
    E += logo_or_abbr("Team", X + 40, Y + 36, 120, 110, "team", 40, A("pop", 360, 260), S=S)
    E += [
        box("Kicker bg", X + 180, Y + 44, 760, 50, None, A("wipe-right", 360, 300), bg=S["dark"], show="notes.kicker"),
        txt("Kicker", X + 196, Y + 44, 740, 50, U(S, "notes.kicker"), 32, A("fade", 260, 420), show="notes.kicker", font=f, weight=800, color="$accent"),
        txt("Title", X + 180, Y + 96, 800, 110, U(S, "notes.title"), 84, A("reveal-up", 420, 420), show="notes.title", font=f, weight=800),
        txt("Name", X + 180, Y + 96, 800, 110, U(S, "batter.name"), 84, A("reveal-up", 420, 420), show="!notes.title", font=f, weight=800),
        box("Rule", X + 40, Y + 222, 940, 4, "$accent", A("grow-x", 420, 520)),
    ]
    for i in range(3):
        y = Y + 260 + i * 110
        k = "notes.b%d" % (i + 1)
        E += [box("Bullet %d" % (i + 1), X + 66, y + 30, 30, 30, "$accent", A("pop", 320, 640 + i * 140), show=k, rotate=45),
              txt("Bullet text %d" % (i + 1), X + 130, y, 840, 90, U(S, k), 46, A("slide-right", 380, 660 + i * 140, dist=40), show=k, font=f, weight=800)]
    E += [
        box("Photo panel", X + 1010, Y + 20, W - 1030, H - 110, None, A("wipe-up", 420, 300), bg=TG(S, "team")),
        img("Photo logo", X + 1040, Y + 60, W - 1090, H - 200, "{team.logo}", A("fade", 500, 400), show="team.logo", opacity=0.2),
        img("Photo", X + 1010, Y + 40, W - 1030, H - 130, "{batter.photo}", A("slide-up", 520, 480, dist=40), show="batter.photo", focus="center bottom"),
        box("Footnote bar", X + 20, Y + H - 78, W - 40, 58, None, A("wipe-right", 380, 760), show="notes.foot", bg=S["strip"]),
        txt("Footnote", X + 40, Y + H - 78, W - 80, 58, U(S, "notes.foot"), 28, A("fade", 260, 900), show="notes.foot", font=f, weight=800, align="center",
            color=S["stripText"]),
    ] + sponsor_tab(X + W - 340, Y + H + 12, 340, 56, 900, radius=S["radius"])
    return {"name": "Feature Card", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E}


def compare_card(S, mode):
    """Starting pitchers side by side: photos, names, label rows with the better value highlighted."""
    f = S["font"]
    X, Y, W, H = 300, 120, 1320, 820
    bind = "spSeason" if mode == "season" else "spToday"
    title = "Starting Pitchers" if mode == "season" else "Starters Comparison"
    sub = "{seasonYear} Season" if mode == "season" else "Tonight"
    E = [card(S, "Card", X, Y, W, H),
         txt("Title", X + 200, Y + 14, W - 400, 70, L(S, title), 58, A("reveal-up", 400, 260), font=f, weight=800, align="center"),
         txt("Sub", X + 200, Y + 80, W - 400, 36, L(S, sub), 28, A("fade", 300, 380), font=f, weight=700, align="center", color="$accent")]
    for i, side in enumerate(("away", "home")):
        px = X + 20 if i == 0 else X + W - 360
        tx = X + 20 if i == 0 else X + W - 120
        E += [box("%s tile" % side, tx, Y + 20, 100, 100, None, A("pop", 340, 300), bg=TG(S, side), radius=S["radius"])]
        E += logo_or_abbr("%s logo" % side, tx + 8, Y + 28, 84, 84, side, 30, A("pop", 340, 400), S=S)
        E += [
            box("%s photo bg" % side, px, Y + 136, 340, 450, None, A("wipe-up", 420, 360 + i * 80), bg=TG(S, side)),
            img("%s photo logo" % side, px + 30, Y + 170, 280, 380, "{%s.logo}" % side, A("fade", 500, 460), show="%s.logo" % side, opacity=0.2),
            img("%s photo" % side, px, Y + 150, 340, 436, "{%s.sp.photo}" % side, A("slide-up", 480, 520 + i * 80, dist=30), show="%s.sp.photo" % side,
                fit="contain", focus="center bottom"),
            txt("%s number" % side, px, Y + 220, 340, 300, "{%s.sp.number}" % side, 200, A("fade", 400, 520), show="!%s.sp.photo" % side, align="center",
                weight=800, color="#FFFFFF@0.3", font=f, fit=False),
            box("%s name bg" % side, px, Y + 586, 340, 90, None, A("wipe-right", 360, 600 + i * 80), bg=S["dark"]),
            txt("%s first" % side, px + 16, Y + 590, 308, 32, U(S, "%s.sp.first" % side), 24, A("fade", 260, 700), font=f, weight=600, color="$dim"),
            txt("%s last" % side, px + 16, Y + 618, 308, 54, U(S, "%s.sp.last" % side), 46, A("reveal-up", 320, 700), font=f, weight=800),
        ]
    E += [
        el("table", "Rows", X + 372, Y + 140, W - 744, 620, A("none", 1, 0, rows={"type": "pop", "dur": 340, "stagger": 80, "delay": 620}), bind=bind,
           columns=[{"label": "", "field": "away", "w": 1, "align": "center", "fill": S["val"], "color": S["valText"], "fillIf": "awayHi", "fillOn": S["hi"],
                     "colorIf": "awayHi", "colorOn": S["hiText"], "weight": 800, "size": 44},
                    {"label": "", "field": "label", "w": 1.1, "align": "center", "weight": 800, "color": "$dim", "size": 26},
                    {"label": "", "field": "home", "w": 1, "align": "center", "fill": S["val"], "color": S["valText"], "fillIf": "homeHi", "fillOn": S["hi"],
                     "colorIf": "homeHi", "colorOn": S["hiText"], "weight": 800, "size": 44}],
           style={"rowH": 84, "size": 34, "weight": 800, "color": "$text", "header": False, "padX": 0, "gap": 14, "maxRows": 6, "font": f}),
        box("Footnote bar", X + 20, Y + H - 70, W - 40, 52, None, A("wipe-right", 360, 900), show="notes.foot", bg=S["strip"]),
        txt("Footnote", X + 30, Y + H - 70, W - 60, 52, U(S, "notes.foot"), 26, A("fade", 260, 1000), show="notes.foot", font=f, weight=800, align="center",
            color=S["stripText"]),
    ] + sponsor_tab(X + W - 340, Y + H + 12, 340, 56, 900, radius=S["radius"])
    return {"name": "Starting Pitchers" if mode == "season" else "Starters Comparison", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def final_card(S):
    """Game final: R H E, decisions, each starter's line with headshot, each team's top hitters."""
    f = S["font"]
    X, Y, W = 210, 70, 1500
    E = [card(S, "Card", X, Y, W, 900),
         box("Header", X + 14, Y + 14, W - 28, 96, None, A("wipe-right", 360, 200), bg=S["dark"]),
         txt("Final", X + 34, Y + 14, 300, 96, "{statusText}", 56, A("reveal-up", 380, 320), font=f, weight=800),
         txt("Venue", X + 340, Y + 14, 780, 96, U(S, "venue"), 30, A("fade", 300, 420), show="venue", font=f, weight=700, color="$dim", align="center"),
         txt("Time", X + W - 334, Y + 14, 300, 96, L(S, "Time: {duration}"), 30, A("fade", 300, 460), show="duration", font=f, weight=700, align="right")]
    for i, side in enumerate(("away", "home")):
        y = Y + 122 + i * 96
        other = "home" if side == "away" else "away"
        E += [box("%s row" % side, X + 14, y, 980, 88, None, A("wipe-right", 380, 300 + i * 80), bg=TG(S, side))]
        E += logo_or_abbr("%s logo" % side, X + 24, y + 6, 100, 76, side, 30, A("pop", 320, 420 + i * 80), S=S)
        E += [txt("%s name" % side, X + 140, y, 420, 88, U(S, "%s.name" % side), 46, A("reveal-up", 340, 440 + i * 80), font=f, weight=800, textShadow=True),
              txt("%s record" % side, X + 560, y, 110, 88, "{%s.record}" % side, 26, A("fade", 260, 520), show="%s.record" % side, font=f, weight=700)]
        for j, k in enumerate(("runs", "hits", "errors")):
            bx = X + 676 + j * 106
            d = 520 + j * 60 + i * 80
            plain = ("leader!=%s" % side) if k == "runs" else None
            E += [box("%s %s bg" % (side, k), bx, y + 6, 100, 76, None, A("pop", 300, d), bg=S["val"], radius=S["radius"], show=plain),
                  txt("%s %s" % (side, k), bx, y + 6, 100, 76, "{%s.%s}" % (side, k), 50, A("fade", 260, d + 80), show=plain, font=f, weight=800,
                      align="center", color=S["valText"])]
            if k == "runs":
                E += [box("%s runs win" % side, bx, y + 6, 100, 76, S["hi"], A("pop", 300, d), radius=S["radius"], show="leader==%s" % side),
                      txt("%s runs on win" % side, bx, y + 6, 100, 76, "{%s.runs}" % side, 50, A("fade", 260, d + 80), show="leader==%s" % side,
                          font=f, weight=800, align="center", color=S["hiText"])]
    E += [
        box("Decisions", X + 1006, Y + 122, W - 1020, 184, None, A("wipe-left", 380, 380), bg=S["dark"], show="hasDecisions"),
        txt("W", X + 1022, Y + 128, 40, 56, "W", 28, A("fade", 260, 600), show="decisions.w.name", font=f, weight=800, color="$accent"),
        txt("W text", X + 1062, Y + 128, W - 1092, 56, "{decisions.w.text}", 30, A("fade", 260, 620), show="decisions.w.name", font=f, weight=800),
        txt("L", X + 1022, Y + 186, 40, 56, "L", 28, A("fade", 260, 660), show="decisions.l.name", font=f, weight=800, color="$accent"),
        txt("L text", X + 1062, Y + 186, W - 1092, 56, "{decisions.l.text}", 30, A("fade", 260, 680), show="decisions.l.name", font=f, weight=800),
        txt("S", X + 1022, Y + 244, 40, 56, "S", 28, A("fade", 260, 720), show="decisions.s.name", font=f, weight=800, color="$accent"),
        txt("S text", X + 1062, Y + 244, W - 1092, 56, "{decisions.s.text}", 30, A("fade", 260, 740), show="decisions.s.name", font=f, weight=800),
    ]
    for i, side in enumerate(("away", "home")):
        y = Y + 320 + i * 262
        E += [
            box("%s section" % side, X + 14, y, W - 28, 252, None, A("wipe-right", 400, 700 + i * 120), bg=TG(S, side)),
            box("%s photo bg" % side, X + 28, y + 14, 180, 224, "#000000@0.25", A("fade", 300, 820 + i * 120), radius=S["radius"]),
            img("%s sp photo" % side, X + 28, y + 14, 180, 224, "{%s.sp.photo}" % side, A("fade", 400, 860 + i * 120), show="%s.sp.photo" % side, fit="cover",
                focus="center top", radius=S["radius"]),
            txt("%s sp" % side, X + 226, y + 14, 330, 56, U(S, "%s.sp.last" % side), 44, A("reveal-up", 320, 880 + i * 120), font=f, weight=800),
            txt("%s sp line 1" % side, X + 226, y + 76, 330, 46, L(S, "{%s.sp.ip} IP, {%s.sp.h} H" % (side, side)), 34, A("fade", 260, 940 + i * 120), font=f,
                weight=800, color="$accent"),
            txt("%s sp line 2" % side, X + 226, y + 122, 330, 46, L(S, "{%s.sp.er} ER, {%s.sp.k} K" % (side, side)), 34, A("fade", 260, 980 + i * 120), font=f,
                weight=800, color="$accent"),
            txt("%s sp line 3" % side, X + 226, y + 168, 330, 46, L(S, "{%s.sp.pc} pitches" % side), 34, A("fade", 260, 1020 + i * 120), font=f, weight=800),
            box("%s divider" % side, X + 566, y + 18, 3, 216, "#FFFFFF@0.35", A("grow-y", 300, 900 + i * 120)),
            el("table", "%s hitters" % side, X + 590, y + 14, W - 620, 226,
               A("none", 1, 0, rows={"type": "slide-right", "dur": 320, "stagger": 60, "delay": 960 + i * 120, "dist": 24}), bind="%s.topHitters" % side,
               columns=[{"label": "", "field": U(S, "row.last"), "w": 2.2, "align": "left", "weight": 800},
                        {"label": "", "field": "hab", "w": 0.9, "align": "left", "weight": 800},
                        {"label": "", "field": U(S, "row.notes"), "w": 2.4, "align": "left", "weight": 700, "color": "$dim"}],
               style={"rowH": 56, "size": 34, "weight": 800, "color": "$text", "header": False, "padX": 0, "gap": 0, "maxRows": 4, "font": f}),
        ]
    E += [box("Note bar", X + 14, Y + 846, W - 28, 44, None, A("wipe-right", 340, 1200), show="custom.line1", bg=S["dark"]),
          txt("Note", X + 34, Y + 846, W - 68, 44, U(S, "custom.line1"), 28, A("fade", 260, 1300), show="custom.line1", font=f, weight=800, color="$accent")]
    return {"name": "Game Final", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "final"}


def game_summary(S):
    """Full linescore with starter and finisher lines for each team and a note."""
    f = S["font"]
    X, Y, W = 160, 110, 1600
    E = [card(S, "Card", X, Y, W, 820),
         box("Title band", X + 14, Y + 14, W - 28, 110, None, A("wipe-center", 420, 200), bg=S["dark"]),
         txt("Title", X + 14, Y + 14, W - 28, 110, L(S, "Game Summary"), 82, A("reveal-up", 420, 360), font=f, weight=800, align="center"),
         el("linescore", "Linescore", X + 30, Y + 150, W - 60, 300,
            A("fade", 300, 400, rows={"type": "slide-right", "dur": 400, "stagger": 140, "delay": 500, "dist": 40}),
            style={"size": 58, "color": "$text", "headColor": "$dim", "headSize": 26, "rowFill": "#FFFFFF@0.06", "totalFill": "#000000@0.3",
                   "current": "$accent@0.25", "minInnings": 9, "teamW": 200, "font": f, "weight": 800})]
    for i, side in enumerate(("away", "home")):
        px = X + 14 + i * (W - 28) // 2
        pw = (W - 28) // 2
        E += [box("%s panel" % side, px, Y + 470, pw, 270, None, A("wipe-up", 400, 700 + i * 120), bg=TG(S, side))]
        for j, who in enumerate(("sp", "finisher")):
            y = Y + 486 + j * 124
            E += [
                img("%s %s photo" % (side, who), px + 18, y, 110, 110, "{%s.%s.photo}" % (side, who), A("fade", 360, 820 + i * 120 + j * 80),
                    show="%s.%s.photo" % (side, who), fit="cover", focus="center top", radius=S["radius"]),
                txt("%s %s name" % (side, who), px + 146, y + 6, pw - 170, 52, U(S, "%s.%s.name" % (side, who)), 40, A("reveal-up", 320, 860 + i * 120 + j * 80),
                    show="%s.%s.name" % (side, who), font=f, weight=800),
                txt("%s %s line" % (side, who), px + 146, y + 58, pw - 170, 44, U(S, "%s.%s.line" % (side, who)), 32, A("fade", 260, 920 + i * 120 + j * 80),
                    show="%s.%s.name" % (side, who), font=f, weight=700, color="$dim"),
            ]
    E += [box("Note bar", X + 14, Y + 752, W - 28, 54, None, A("wipe-right", 340, 1100), show="custom.line1", bg=S["dark"]),
          txt("Note", X + 14, Y + 752, W - 28, 54, U(S, "custom.line1"), 32, A("fade", 260, 1200), show="custom.line1", font=f, weight=700, align="center",
              italic=True, color="$dim")]
    return {"name": "Game Summary", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "final"}


def performers_card(S):
    """Four columns: the two best hitters on each side tonight (photo, name, season AVG / HR / RBI / OBP, tonight)."""
    f = S["font"]
    X, Y, W, H = 120, 100, 1680, 860
    E = [card(S, "Card", X, Y, W, H),
         box("Title band", X + 14, Y + 14, W - 28, 96, None, A("wipe-center", 420, 200), bg=S["dark"]),
         txt("Title", X + 14, Y + 14, W - 28, 96, L(S, "Top Performers"), 72, A("reveal-up", 420, 340), font=f, weight=800, align="center"),
         txt("Sub", X + 14, Y + 112, W - 28, 40, L(S, "Tonight"), 28, A("fade", 300, 460), font=f, weight=700, align="center", color="$accent")]
    cw = (W - 28 - 30) // 4
    for i in range(4):
        p = "performers.%d" % i
        cx = X + 14 + i * (cw + 10)
        d = 520 + i * 110
        E += [
            box("P%d photo bg" % (i + 1), cx, Y + 160, cw, 300, None, A("wipe-down", 400, d), show=p + ".name",
                bg="linear-gradient(180deg, color-mix(in srgb, {%s.color} 75%%, #fff), {%s.color} 55%%, color-mix(in srgb, {%s.color} 65%%, #000))" % (p, p, p)),
            img("P%d logo" % (i + 1), cx + 10, Y + 180, cw // 2, 160, "{%s.logo}" % p, A("fade", 400, d + 100), show=p + ".logo", opacity=0.85),
            img("P%d photo" % (i + 1), cx + cw // 3, Y + 170, cw - cw // 3, 290, "{%s.photo}" % p, A("slide-up", 460, d + 140, dist=30), show=p + ".photo",
                fit="contain", focus="center bottom"),
            box("P%d name bg" % (i + 1), cx, Y + 460, cw, 96, None, A("fade", 300, d + 160), show=p + ".name", bg=S["dark"]),
            box("P%d accent" % (i + 1), cx + 14, Y + 474, 4, 70, "$accent", A("grow-y", 260, d + 220), show=p + ".name"),
            txt("P%d first" % (i + 1), cx + 30, Y + 466, cw - 44, 32, U(S, p + ".first"), 22, A("fade", 260, d + 240), show=p + ".name", font=f, weight=600,
                color="$dim"),
            txt("P%d last" % (i + 1), cx + 30, Y + 494, cw - 44, 56, U(S, p + ".last"), 48, A("reveal-up", 320, d + 240), show=p + ".name", font=f, weight=800),
        ]
        for j, (lab, val) in enumerate((("AVG", "{%s.avg|avg}" % p), ("HR", "{%s.hr|zero}" % p), ("RBI", "{%s.rbi|zero}" % p), ("Tonight", "{%s.hab}" % p))):
            y = Y + 566 + j * 68
            E += [txt("P%d %s" % (i + 1, lab), cx + 24, y, cw // 2, 60, L(S, lab), 28, A("fade", 260, d + 300 + j * 50), show=p + ".name", font=f, weight=600,
                      color="$dim"),
                  txt("P%d %s v" % (i + 1, lab), cx + cw // 2, y, cw // 2 - 24, 60, val, 44, A("fade", 260, d + 320 + j * 50), show=p + ".name", font=f,
                      weight=800, align="right"),
                  box("P%d line %d" % (i + 1, j), cx + 24, y + 62, cw - 48, 2, "$accent@0.55", A("grow-x", 260, d + 320 + j * 50), show=p + ".name")]
    return {"name": "Top Performers", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ================================================================ MATCHUPS
def matchup_banner(S):
    """Lower banner: team halves with logo tiles and names, sponsor / brand emblem in the centre, venue strip."""
    f = S["font"]
    X, Y, W = 240, 742, 1440
    E = []
    for i, side in enumerate(("away", "home")):
        hx = X if i == 0 else X + W // 2 + 90
        hw = W // 2 - 90
        tile_x = hx if i == 0 else hx + hw - 190
        name_x = hx + 210 if i == 0 else hx + 20
        al = "left" if i == 0 else "right"
        E += [
            box("%s half" % side, hx, Y, hw, 170, None, A("slide-right" if i == 0 else "slide-left", 520, 0, dist=200), bg=TG(S, side),
                borderW=2, borderColor="#FFFFFF@0.25"),
            box("%s tile" % side, tile_x, Y - 24, 190, 194, None, A("pop", 420, 260), bg="#000000@0.28"),
        ] + logo_or_abbr("%s logo" % side, tile_x + 14, Y - 10, 162, 166, side, 54, A("pop", 420, 380), S=S) + [
            txt("%s record" % side, name_x, Y + 14, hw - 230, 40, "{%s.record}" % side, 30, A("fade", 300, 520), show="%s.record" % side, font=f, weight=700,
                align=al, color="$dim"),
            txt("%s name" % side, name_x, Y + 50, hw - 230, 104, U(S, "%s.name" % side), 70, A("reveal-up", 420, 460), font=f, weight=800, align=al,
                textShadow=True),
        ]
    cx = X + W // 2 - 90
    E += [
        box("Emblem", cx, Y - 20, 180, 180, None, A("pop", 460, 160), bg=S["strip"], radius=S["radius"] * 3, shadow=True),
        img("Sponsor", cx + 18, Y, 144, 140, "{sponsor.logo}", A("fade", 300, 420), show="sponsor.on && sponsor.logo"),
        txt("Sponsor name", cx + 10, Y - 20, 160, 180, "{sponsor.name}", 30, A("fade", 300, 420), show="sponsor.on && !sponsor.logo", color=S["stripText"],
            align="center", wrap=True, fit=False, weight=800),
        img("Brand", cx + 18, Y, 144, 140, "{brand.logo}", A("fade", 300, 420), show="!sponsor.on && brand.logo"),
        txt("VS", cx, Y - 20, 180, 180, "VS", 70, A("fade", 300, 420), show="!sponsor.on && !brand.logo", color=S["stripText"], align="center", font=f, weight=800),
        box("Venue strip", X + 160, Y + 176, W - 320, 50, None, A("wipe-center", 380, 600), show="venue || custom.line1", bg=S["dark"]),
        txt("Venue", X + 160, Y + 176, W - 320, 50, U(S, "venue"), 30, A("fade", 260, 760), show="venue && !custom.line1", font=f, weight=800, align="center"),
        txt("Line", X + 160, Y + 176, W - 320, 50, U(S, "custom.line1"), 30, A("fade", 260, 760), show="custom.line1", font=f, weight=800, align="center"),
    ]
    return {"name": "Matchup Banner", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "matchup"}


def tiled(name, x, y, w, h, team_path, S, size=150, rows=12, outline="rgba(255,255,255,0.16)", solid=None, scroll=-300, dur=9000, delay=0):
    """Repeating team-name type, scrolling vertically forever (pairs of rows = one loop)."""
    text = "\\n".join(["{%s|upper}" % team_path] * rows)
    st = {"color": solid or "transparent", "size": size, "weight": 800, "align": "left", "valign": "top", "padX": 0, "fit": False, "wrap": False,
          "lineH": 1.0, "font": S["font"], "tracking": -2}
    if not solid:
        st["textStroke"] = "2px %s" % outline
    e = {"id": nid("t"), "name": name, "type": "text", "x": x, "y": y, "w": w, "h": h, "text": text, "style": st,
         "anim": A("fade", 700, delay, loop={"type": "scroll-y", "dur": dur, "amount": scroll})}
    return e


def matchup_split(S):
    """Full screen split: each half in team colour with tiled team-name type, big logo, seam down the middle."""
    E = []
    for i, side in enumerate(("away", "home")):
        hx = i * 960
        E += [
            box("%s half" % side, hx, 0, 960, 1080, None, A("slide-down" if i == 0 else "slide-up", 640, 0, dist=300,
                                                               out={"type": "fade", "dur": 400, "delay": 200, "ease": "in"}),
                bg="linear-gradient(%ddeg, color-mix(in srgb, {%s.color} 70%%, #000), {%s.color})" % (90 if i == 0 else 270, side, side)),
            dict(tiled("%s type" % side, hx - 40, -300, 1100, 1800, "%s.name" % side, S, size=150, rows=12, scroll=-300 if i == 0 else 300,
                       dur=12000, delay=200), x=hx - 40),
        ]
        E += logo_or_abbr("%s logo" % side, hx + 180, 290, 600, 500, side, 220, A("zoom-out", 700, 420), S=S)
    E += [box("Seam", 952, 0, 16, 1080, None, A("grow-y", 600, 300), bg="linear-gradient(90deg, #DADFE6, #FFFFFF, #C9CFD8)", shadow=True),
          box("Seam stitch", 958, 0, 4, 1080, None, A("grow-y", 600, 420), bg="repeating-linear-gradient(180deg, #E5483B 0 14px, transparent 14px 26px)")]
    return {"name": "Matchup: Split", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ================================================================ SIDE PANELS (L-bar companions)
def side_header(S, X, tabs, active):
    f = S["font"]
    E = [box("Panel", X, 0, 1920 - X, 1080, None, A("wipe-left", 520, 0, out={"type": "wipe-right", "dur": 400, "delay": 100, "ease": "in"}),
             bg=S["panel"])]
    tw = (1920 - X - 40) // 3
    for i, team in enumerate(("brand", "away", "home")):
        tx = X + 14 + i * (tw + 6)
        E += [box("%s tile" % team, tx, 14, tw, 124, None, A("pop", 360, 260 + i * 80), bg=S["strip"] if team == "brand" else TG(S, team),
                  radius=S["radius"], borderW=2, borderColor="#FFFFFF@0.35")]
        if team == "brand":
            E += [img("Brand logo", tx + 12, 26, tw - 24, 100, "{brand.logo}", A("fade", 300, 400), show="brand.logo")]
        else:
            E += logo_or_abbr("%s logo" % team, tx + 12, 26, tw - 24, 100, team, 40, A("fade", 300, 420 + i * 80), S=S)
    E += [box("Tabs", X + 14, 148, 1920 - X - 28, 104, None, A("wipe-down", 360, 420), bg=S["dark"], radius=S["radius"])]
    n = len(tabs)
    for i, t in enumerate(tabs):
        w = (1920 - X - 28) // n
        E += [txt("Tab %d" % i, X + 14 + i * w, 148, w, 104, L(S, t), 34 if len(t) < 12 else 28, A("fade", 260, 540 + i * 60), font=f, weight=800,
                  align="center", color="$text" if i == active else "$dim", wrap=True, fit=False, lineH=0.95)]
    w = (1920 - X - 28) // n
    E += [box("Tab underline", X + 14 + active * w + 30, 236, w - 60, 5, "$accent", A("grow-x", 300, 700))]
    return E


def side_defense(S):
    """Right-side panel: brand + team tiles, tabs, defensive alignment, bench."""
    X = 1440
    f = S["font"]
    E = side_header(S, X, ["Starting Lineup", "Starting Pitcher", "Defense"], 2)
    E += [
        box("Field bg", X + 14, 262, 1920 - X - 28, 470, None, A("fade", 400, 560), bg=S["panel2"], radius=S["radius"]),
        el("field", "Field", X + 20, 268, 1920 - X - 40, 458, A("fade", 400, 620, rows={"type": "pop", "dur": 320, "stagger": 60, "delay": 760}),
           bind="team.defense", style={"grass": "#FFFFFF@0.03", "dirt": "#FFFFFF@0.06", "line": "#FFFFFF@0.35", "labelFill": "", "nameColor": "$text",
                                       "posColor": "$accent", "size": 19, "nameField": "last", "font": f}),
        box("Bench head", X + 14, 742, 1920 - X - 28, 64, None, A("wipe-right", 340, 800), bg=S["strip"]),
        txt("Bench title", X + 30, 742, 400, 64, L(S, "{team.abbr} Bench"), 34, A("fade", 260, 900), font=f, weight=800, color=S["stripText"]),
    ]
    for i in range(3):
        p = "team.bench.%d" % i
        y = 814 + i * 88
        E += [
            box("Bench %d bg" % i, X + 14, y, 1920 - X - 28, 82, None, A("slide-left", 320, 960 + i * 80, dist=40), show=p + ".name", bg=S["dark"]),
            img("Bench %d photo" % i, X + 20, y + 4, 92, 74, "{%s.photo}" % p, A("fade", 300, 1040 + i * 80), show=p + ".photo", fit="cover", focus="center top"),
            txt("Bench %d first" % i, X + 126, y + 4, 260, 30, U(S, p + ".first"), 22, A("fade", 260, 1040 + i * 80), show=p + ".name", font=f, weight=600,
                color="$dim"),
            txt("Bench %d last" % i, X + 126, y + 30, 260, 48, U(S, p + ".last"), 40, A("fade", 260, 1060 + i * 80), show=p + ".name", font=f, weight=800),
            box("Bench %d hand bg" % i, X + 400, y + 22, 50, 40, None, A("pop", 260, 1100 + i * 80), show=p + ".bats", bg=S["strip"], radius=S["radius"]),
            txt("Bench %d hand" % i, X + 400, y + 22, 50, 40, "{%s.bats}" % p, 28, A("pop", 260, 1100 + i * 80), show=p + ".bats", font=f, weight=800,
                align="center", color=S["stripText"]),
        ]
    return {"name": "Side Panel: Defense", "group": "panel", "autoHide": 0, "side": "fielding", "sided": True, "elements": E}


def side_plays(S):
    """Right-side panel: the most recent plays with headshots and outs."""
    X = 1440
    f = S["font"]
    E = side_header(S, X, ["Live Now", "All Plays", "Box Score"], 1)
    for i in range(6):
        p = "recentPlays.%d" % i
        y = 266 + i * 134
        E += [
            box("Play %d bg" % i, X + 14, y, 1920 - X - 28, 126, None, A("slide-left", 340, 640 + i * 90, dist=40), show=p + ".text", bg=S["dark"],
                radius=S["radius"], borderW=1, borderColor="#FFFFFF@0.18"),
            box("Play %d photo bg" % i, X + 22, y + 8, 100, 110, None, A("fade", 300, 700 + i * 90), show=p + ".text",
                bg="linear-gradient(180deg, color-mix(in srgb, {%s.color} 70%%, #fff), {%s.color})" % (p, p)),
            img("Play %d logo" % i, X + 26, y + 12, 50, 50, "{%s.logo}" % p, A("fade", 300, 720 + i * 90), show=p + ".logo && !" + p + ".photo", opacity=0.9),
            img("Play %d photo" % i, X + 22, y + 8, 100, 110, "{%s.photo}" % p, A("fade", 300, 740 + i * 90), show=p + ".photo", fit="cover", focus="center top"),
            txt("Play %d half" % i, X + 136, y + 4, 200, 26, "{%s.halfLabel}" % p, 18, A("fade", 260, 760 + i * 90), show=p + ".text", font=f, weight=700,
                color="$accent"),
            txt("Play %d text" % i, X + 136, y + 28, 1920 - X - 170, 70, U(S, p + ".text"), 30, A("fade", 260, 780 + i * 90), show=p + ".text", font=f, weight=800,
                wrap=True, fit=False, lineH=1.0, valign="top"),
            el("dots", "Play %d outs" % i, 1920 - 30 - 84, y + 96, 84, 24, A("fade", 260, 820 + i * 90), show=p + ".text", bind=p + ".outs",
               style={"total": 3, "size": 15, "gap": 6, "on": "#FFFFFF", "off": "#FFFFFF@0.2", "align": "right"}),
        ]
    return {"name": "Side Panel: Plays", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ================================================================ EVENT STINGERS (fire automatically)
def hr_event(S):
    """Marquee sign with chasing bulbs: HOME RUN! (GRAND SLAM! with the bases loaded)."""
    f = S["font"]
    X, Y = 640, 430
    glow = "0 0 10px #FFFFFF, 0 0 26px #FFD25A, 0 0 60px #FF9F1A"
    E = [
        box("Sign", X, Y, 640, 300, None, A("pop", 420, 0, out={"type": "scale", "dur": 300, "delay": 0, "ease": "in"}),
            bg="linear-gradient(180deg, #2A2F3A, #0B0E14)", radius=22, borderW=4, borderColor="#5A6578", shadow="0 20px 60px rgba(0,0,0,.6)"),
        img("Bulbs", X, Y, 640, 300, "/art/bulbs.svg", A("fade", 200, 160, loop={"type": "chase", "dur": 420, "amount": 0.3}), fit="fill"),
        txt("Home", X + 40, Y + 26, 560, 92, L(S, "Home"), 86, A("reveal-up", 360, 280), show="lastPlay.runs!=4", font=f, weight=800, align="center",
            color="transparent", textStroke="3px #7FC1FF", textShadow="0 0 18px #3D8BFD"),
        txt("Run", X + 40, Y + 110, 560, 170, L(S, "Run!"), 170, A("letters", 500, 420, stagger=70), show="lastPlay.runs!=4", font=f, weight=800,
            align="center", textShadow=glow),
        txt("Grand", X + 40, Y + 26, 560, 92, L(S, "Grand"), 86, A("reveal-up", 360, 280), show="lastPlay.runs==4", font=f, weight=800, align="center",
            color="transparent", textStroke="3px #7FC1FF", textShadow="0 0 18px #3D8BFD"),
        txt("Slam", X + 40, Y + 110, 560, 170, L(S, "Slam!"), 160, A("letters", 500, 420, stagger=70), show="lastPlay.runs==4", font=f, weight=800,
            align="center", textShadow=glow),
        box("Name bar", X + 20, Y + 308, 600, 56, None, A("wipe-center", 340, 700), show="lastPlay.batter.name", bg=S["dark"], radius=S["radius"]),
        txt("Name", X + 30, Y + 308, 580, 56, U(S, "lastPlay.batter.name") + "  ·  {lastPlay.label}", 28, A("fade", 260, 820), show="lastPlay.batter.name",
            font=f, weight=800, align="center"),
    ] + sponsor_tab(X + 140, Y + 372, 360, 52, 900, radius=S["radius"], a_type="wipe-down")
    return {"name": "Home Run!", "group": "event", "autoHide": 4.5, "side": "batting", "sided": False, "elements": E,
            "trigger": "HR", "sponsorSlot": "home_run"}


def hr_tracker(S):
    """Projected distance and exit velocity after a home run (Notes > HR distance / exit velo)."""
    f = S["font"]
    X, Y, W = 1430, 300, 450
    E = [
        box("Header", X, Y, W, 118, None, A("wipe-left", 400, 0), bg=TG(S, "batting"), borderW=2, borderColor="#FFFFFF@0.3"),
        txt("First", X + 20, Y + 10, W - 150, 34, U(S, "lastPlay.batter.name", "|first"), 28, A("fade", 260, 200), font=f, weight=600),
        txt("Last", X + 20, Y + 40, W - 150, 70, U(S, "lastPlay.batter.last"), 60, A("reveal-up", 340, 220), font=f, weight=800, textShadow=True),
        box("Logo diamond", X + W - 116, Y + 14, 90, 90, None, A("pop", 360, 300), bg=S["dark"], rotate=45, borderW=3, borderColor="#FFFFFF"),
    ] + logo_or_abbr("Logo", X + W - 110, Y + 22, 78, 74, "batting", 26, A("pop", 340, 380), S=S) + [
        box("Dist label", X, Y + 122, W, 46, None, A("wipe-right", 300, 400), show="lastPlay.distance", bg="#05080F"),
        txt("Dist label t", X + 18, Y + 122, W - 36, 46, L(S, "Projected HR distance"), 26, A("fade", 240, 480), show="lastPlay.distance", font=f, weight=800,
            color="$accent"),
        box("Dist value", X, Y + 168, W, 140, None, A("wipe-right", 360, 460), show="lastPlay.distance", bg=S["panel"]),
        txt("Dist", X + 20, Y + 168, W - 120, 140, "{lastPlay.distance}", 120, A("reveal-up", 420, 560), show="lastPlay.distance",
            font=f, weight=800, align="right"),
        txt("Ft", X + W - 92, Y + 168, 72, 140, L(S, "ft"), 44, A("fade", 260, 680), show="lastPlay.distance", font=f, weight=800, color="$accent"),
        box("EV label", X, Y + 314, W, 46, None, A("wipe-right", 300, 640), show="lastPlay.ev", bg="#05080F"),
        txt("EV label t", X + 18, Y + 314, W - 36, 46, L(S, "Exit velocity"), 26, A("fade", 240, 720), show="lastPlay.ev", font=f, weight=800, color="$accent"),
        box("EV value", X, Y + 360, W, 140, None, A("wipe-right", 360, 700), show="lastPlay.ev", bg=S["panel"]),
        txt("EV", X + 20, Y + 360, W - 140, 140, "{lastPlay.ev}", 120, A("reveal-up", 420, 800), show="lastPlay.ev", font=f, weight=800, align="right"),
        txt("MPH", X + W - 112, Y + 360, 100, 140, L(S, "mph"), 44, A("fade", 260, 920), show="lastPlay.ev", font=f, weight=800, color="$accent"),
    ]
    return {"name": "HR Tracker", "group": "event2", "autoHide": 8, "side": "batting", "sided": False, "elements": E,
            "trigger": "HR", "triggerDelay": 5, "triggerIf": "lastPlay.distance || lastPlay.ev"}


def wp_event(S):
    """Wild pitch / passed ball: the ball breaks the glass."""
    f = S["font"]
    X, Y = 120, 560
    E = [
        img("Glass", X, Y, 600, 420, "/art/glass.svg", A("zoom-out", 260, 120, out={"type": "fade", "dur": 300, "delay": 0, "ease": "in"}), fit="fill"),
        box("Backing", X + 40, Y + 40, 520, 340, "#000000@0.45", A("fade", 200, 100), radius=S["radius"]),
        img("Ball", X + 210, Y + 120, 180, 180, "/art/ball.svg", A("scale", 260, 0, ease="back", out={"type": "fade", "dur": 260, "delay": 0, "ease": "in"},
                                                              loop={"type": "spin", "dur": 9000})),
        txt("Word 1", X + 40, Y + 30, 360, 110, U(S, "lastPlay.word1"), 104, A("slide-right", 320, 260, dist=60), font=f, weight=800, textShadow=True),
        box("Bar 1", X + 330, Y + 76, 230, 16, "#FFFFFF", A("grow-x", 260, 360)),
        box("Bar 2", X + 40, Y + 334, 230, 16, "#FFFFFF", A("grow-x", 260, 400, origin="right center")),
        txt("Word 2", X + 200, Y + 280, 360, 110, U(S, "lastPlay.word2"), 104, A("slide-left", 320, 320, dist=60), font=f, weight=800, align="right",
            textShadow=True),
    ]
    return {"name": "Wild Pitch / Passed Ball", "group": "event", "autoHide": 3.5, "side": "", "sided": False, "elements": E, "trigger": "WP,PB"}


# ================================================================ SHOW GRAPHICS
def show_title(S, title, name):
    """Full-screen show title: kinetic vertical type columns, brand logo, script brand name, big title between rules."""
    f = S["font"]
    bg = S.get("titleBg") or ("linear-gradient(160deg, #78BDF6, #2E7FDB 45%, #123F8C)" if S["key"] == "network"
                              else "radial-gradient(ellipse at 70% 30%, rgba(104,140,150,0.6), rgba(12,16,19,0.98) 65%)")
    ink = "#0A1F44" if S["key"] == "network" else "#FFFFFF"
    word = title.upper()
    col = "  ".join([word] * 4)
    E = [
        box("Background", 0, 0, 1920, 1080, None, A("fade", 500, 0, out={"type": "fade", "dur": 500, "delay": 300, "ease": "in"},
                                                     loop={"type": "breathe", "dur": 9000, "amount": 0.04}), bg=bg),
        {"id": nid("t"), "name": "Column solid", "type": "text", "x": 10, "y": -1400, "w": 200, "h": 4200, "text": col,
         "style": {"color": ink, "size": 190, "weight": 800, "align": "left", "valign": "top", "padX": 0, "fit": False, "font": f, "vertical": True,
                   "tracking": -2, "lineH": 1},
         "anim": A("fade", 600, 200, loop={"type": "scroll-y", "dur": 16000, "amount": 900, "pingpong": True})},
        {"id": nid("t"), "name": "Column outline", "type": "text", "x": 200, "y": -1400, "w": 200, "h": 4200, "text": col,
         "style": {"color": "transparent", "size": 190, "weight": 800, "align": "left", "valign": "top", "padX": 0, "fit": False, "font": f, "vertical": True,
                   "tracking": -2, "lineH": 1, "textStroke": "2px " + ink},
         "anim": A("fade", 600, 300, loop={"type": "scroll-y", "dur": 16000, "amount": -900, "pingpong": True})},
        img("Brand logo", 860, 230, 200, 160, "{brand.logo}", A("pop", 520, 500), show="brand.logo"),
        txt("Brand name", 560, 380, 800, 100, "{brand.name}", 72, A("fade", 520, 760), font="Georgia, 'Times New Roman', serif", weight=600, italic=True,
            align="center", color=ink),
        box("Rule top", 520, 486, 880, 3, ink, A("grow-x", 520, 700, origin="center center")),
        txt("Title", 300, 500, 1320, 200, word, 190 if len(word) < 10 else 150, A("letters", 620, 900, stagger=45), font=f, weight=800, align="center",
            tracking=2, textShadow="0 6px 30px rgba(0,0,0,.25)"),
        box("Rule bottom", 520, 712, 880, 3, ink, A("grow-x", 520, 1000, origin="center center")),
        txt("Sub", 400, 730, 1120, 64, U(S, "show.sub"), 40, A("fade", 400, 1200), show="show.sub", font=f, weight=700, align="center", color=ink),
        img("League", 1700, 900, 180, 140, "{league.logo}", A("fade", 400, 1300), show="league.logo"),
    ] + sponsor_tab(760, 900, 400, 80, 1300, radius=S["radius"] * 2)
    return {"name": name, "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def team_title(S):
    """Branded team loop: tiled team-name rows (solid and outline, opposite directions) behind a big logo."""
    f = S["font"]
    E = [box("Background", 0, 0, 1920, 1080, None, A("fade", 500, 0, out={"type": "fade", "dur": 500, "delay": 300, "ease": "in"}),
             bg="linear-gradient(90deg, color-mix(in srgb, {team.color} 75%, #49A0F0), {team.color} 48%, color-mix(in srgb, {team.color} 70%, #000) 52%)")]
    for r in range(6):
        y = -40 + r * 190
        solid = r % 2 == 0
        E.append({"id": nid("t"), "name": "Row %d" % (r + 1), "type": "text", "x": -600, "y": y, "w": 4000, "h": 190,
                  "text": "  ".join(["{team.name|upper}"] * 8),
                  "style": {"color": "#000000@0.28" if solid else "transparent", "size": 180, "weight": 800, "align": "left", "valign": "center", "padX": 0,
                            "fit": False, "font": f, "tracking": -4, "lineH": 1, **({} if solid else {"textStroke": "2px rgba(255,255,255,0.22)"})},
                  "anim": A("fade", 600, 100 + r * 60, loop={"type": "scroll-x", "dur": 16000 + r * 1500, "amount": -900 if solid else 900, "pingpong": True})})
    E += logo_or_abbr("Logo", 560, 160, 800, 760, "team", 300, A("zoom-out", 800, 400, loop={"type": "breathe", "dur": 6000, "amount": 0.03}), S=S)
    E[-2]["style"]["shadow"] = True
    return {"name": "Team Title", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E}


def show_bug(S):
    """Corner show bug: brand logo + show name + pulsing LIVE."""
    f = S["font"]
    X, Y = 40, 40
    E = [box("Bug", X, Y, 420, 84, None, A("wipe-right", 420, 0), bg=S["panel"], radius=S["radius"], shadow=True, borderW=1, borderColor="#FFFFFF@0.25"),
         img("Brand", X + 10, Y + 8, 90, 68, "{brand.logo}", A("pop", 360, 200), show="brand.logo"),
         txt("Show", X + 112, Y + 4, 290, 50, U(S, "show.name"), 38, A("reveal-up", 340, 300), font=f, weight=800),
         box("Live dot", X + 114, Y + 58, 14, 14, "#E5483B", A("pop", 260, 500, loop={"type": "pulse", "dur": 900, "amount": 0.25}), show="show.live", radius=7),
         txt("Live", X + 136, Y + 50, 120, 30, L(S, "Live"), 22, A("fade", 260, 520), show="show.live", font=f, weight=800, color="#E5483B")]
    return {"name": "Show Bug", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def up_next(S):
    """Rundown card: Up Next with three numbered segments (Notes > Show)."""
    f = S["font"]
    X, Y, W = 1240, 560, 600
    E = [card(S, "Card", X, Y, W, 400),
         box("Head", X + 12, Y + 12, W - 24, 78, None, A("wipe-right", 360, 200), bg=S["dark"]),
         txt("Title", X + 30, Y + 12, W - 60, 78, L(S, "Up Next"), 52, A("reveal-up", 360, 320), font=f, weight=800, color="$accent")]
    for i in range(3):
        k = "show.next%d" % (i + 1)
        y = Y + 104 + i * 92
        E += [box("Num %d" % i, X + 26, y + 10, 64, 64, "$accent", A("pop", 300, 460 + i * 120), show=k, radius=S["radius"]),
              txt("Num %d t" % i, X + 26, y + 10, 64, 64, str(i + 1), 40, A("pop", 300, 460 + i * 120), show=k, font=f, weight=800, align="center",
                  color=S["hiText"]),
              txt("Item %d" % i, X + 110, y, W - 140, 84, U(S, k), 40, A("slide-right", 340, 500 + i * 120, dist=30), show=k, font=f, weight=800)]
    E += sponsor_tab(X + W - 320, Y - 60, 320, 52, 700, radius=S["radius"])
    return {"name": "Up Next", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def talent(S):
    """Talent lower third: one or two names with roles (Notes > Show: host / role)."""
    f = S["font"]
    X, Y = 120, 880
    E = []
    for i in range(2):
        x = X + i * 720
        h, r = "show.host%d" % (i + 1), "show.role%d" % (i + 1)
        E += [box("Bar %d" % i, x, Y, 680, 74, None, A("wipe-right", 380, i * 160), show=h, bg=S["panel"], radius=S["radius"]),
              box("Accent %d" % i, x, Y, 10, 74 + 44, "$accent", A("grow-y", 260, 200 + i * 160), show=h),
              txt("Name %d" % i, x + 30, Y, 630, 74, U(S, h), 50, A("reveal-up", 360, 260 + i * 160), show=h, font=f, weight=800),
              box("Role bar %d" % i, x + 10, Y + 74, 600, 44, None, A("wipe-right", 320, 380 + i * 160), show=r, bg=S["strip"]),
              txt("Role %d" % i, x + 30, Y + 74, 570, 44, U(S, r), 28, A("fade", 260, 480 + i * 160), show=r, font=f, weight=800, color=S["stripText"])]
    return {"name": "Talent", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def bp_info(S):
    """Batting-practice / pregame info bar: promo image, game time and gates open, the matchup, and a QR code from a link."""
    f = S["font"]
    Y, H = 846, 234
    top = 108
    accent_fill = "$accent"
    E = [
        # promotion panel (uploaded image, or the promotion title when there is no image)
        box("Promo bg", 0, Y, 460, H, None, A("wipe-up", 420, 0, out={"type": "wipe-down", "dur": 320, "delay": 100, "ease": "in"}), bg=S["dark"]),
        img("Promo image", 0, Y, 460, H, "{show.promoImage}", A("fade", 400, 240), show="show.promoImage", fit="cover", focus="center center"),
        txt("Promo title", 20, Y + 10, 420, H - 20, U(S, "show.promoTitle"), 64, A("reveal-up", 400, 300), show="!show.promoImage && show.promoTitle",
            font=f, weight=800, align="center", color="$accent", wrap=True, fit=False, lineH=0.95),
        # times
        box("Info band", 460, Y, 1000, top, accent_fill, A("wipe-right", 420, 120, out={"type": "wipe-left", "dur": 320, "delay": 80, "ease": "in"})),
    ]
    for i in range(2):
        y = Y + 6 + i * 50
        lab, val = "show.info%dLabel" % (i + 1), "show.info%d" % (i + 1)
        E += [txt("Info %d label" % (i + 1), 560, y, 330, 46, U(S, lab), 34, A("fade", 260, 360 + i * 90), show=val, font=f, weight=800, align="right",
                  color=S["hiText"], tracking=2),
              box("Info %d box" % (i + 1), 906, y + 2, 150, 44, "#000000@0.32", A("grow-x", 280, 400 + i * 90), show=val, radius=2),
              txt("Info %d value" % (i + 1), 906, y + 2, 150, 44, "{%s}" % val, 30, A("fade", 260, 460 + i * 90), show=val, font=f, weight=700, align="center")]
    E += [
        box("Matchup band", 460, Y + top, 1000, H - top, None, A("wipe-right", 420, 220, out={"type": "wipe-left", "dur": 320, "delay": 40, "ease": "in"}),
            bg="linear-gradient(180deg, #4A4D52, #26282C 55%, #18191C)"),
        txt("Away name", 480, Y + top + 4, 340, H - top - 8, U(S, "away.name"), 38, A("slide-right", 380, 520, dist=40), font=f, weight=800, align="right",
            color="#D9DCE1", wrap=True, fit=False, lineH=0.98),
    ] + logo_or_abbr("Away logo", 830, Y + top + 8, 110, H - top - 16, "away", 34, A("pop", 360, 600), S=S) + [
        txt("At", 940, Y + top, 40, H - top, "@", 44, A("fade", 260, 640), font=f, weight=800, align="center"),
    ] + logo_or_abbr("Home logo", 980, Y + top + 8, 110, H - top - 16, "home", 34, A("pop", 360, 660), S=S) + [
        txt("Home name", 1100, Y + top + 4, 340, H - top - 8, U(S, "home.name"), 38, A("slide-left", 380, 600, dist=40), font=f, weight=800, align="left",
            color="#D9DCE1", wrap=True, fit=False, lineH=0.98),
        # call to action + QR
        box("CTA bg", 1460, Y, 230, H, None, A("wipe-up", 420, 300, out={"type": "wipe-down", "dur": 320, "delay": 60, "ease": "in"}),
            bg="linear-gradient(180deg, #A9D3F5, #7DB8E8)", show="show.qrUrl"),
        txt("CTA", 1472, Y + 10, 206, H - 20, U(S, "show.qrText"), 44, A("fade", 380, 520), show="show.qrUrl", font=f, weight=800, align="center",
            color="#111418", wrap=True, fit=False, lineH=0.95),
        box("QR bg", 1690, Y, 230, H, "#FFFFFF", A("wipe-up", 420, 360, out={"type": "wipe-down", "dur": 320, "delay": 20, "ease": "in"}), show="show.qrUrl"),
        el("qr", "QR code", 1700, Y + 7, 210, 220, A("pop", 420, 620), show="show.qrUrl", text="{show.qrUrl}",
           style={"color": "#000000", "bg": "#FFFFFF", "quiet": 1, "ecc": "M"}),
        # no link: show the sponsor / brand there instead
        box("Right bg", 1460, Y, 460, H, None, A("wipe-up", 420, 300), show="!show.qrUrl", bg=S["dark"]),
        img("Right sponsor", 1480, Y + 20, 420, H - 40, "{sponsor.logo}", A("fade", 400, 520), show="!show.qrUrl && sponsor.on && sponsor.logo"),
        img("Right brand", 1480, Y + 20, 420, H - 40, "{brand.logo}", A("fade", 400, 520), show="!show.qrUrl && !(sponsor.on && sponsor.logo) && brand.logo"),
    ]
    return {"name": "BP Info Bar", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def league_bug(S):
    """Corner league mark with LIVE under it (top right)."""
    f = S["font"]
    E = [img("League", 1690, 22, 210, 92, "{league.logo}", A("fade", 500, 0), show="league.logo", shadow=True),
         txt("League name", 1600, 22, 300, 92, U(S, "league.name"), 44, A("fade", 500, 0), show="!league.logo && league.name", font=f, weight=800,
             align="right", textShadow=True),
         txt("Live", 1600, 108, 300, 56, L(S, "Live"), 50, A("reveal-up", 400, 300), show="show.live", font=f, weight=800, align="right", italic=True,
             textShadow="0 2px 10px rgba(0,0,0,.6)")]
    return {"name": "League Bug", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E}


def ticker_bar(S):
    """Bottom ticker that can stay on air: league / brand mark and label, then scores, standings and your notes scrolling."""
    f = S["font"]
    Y, H = 1014, 66
    E = [
        box("Bar", 0, Y, 1920, H, None, A("wipe-up", 420, 0, out={"type": "wipe-down", "dur": 320, "delay": 0, "ease": "in"}), bg=S["panel"],
            borderW=0, shadow="0 -6px 24px rgba(0,0,0,.35)"),
        box("Top line", 0, Y, 1920, 3, "$accent", A("grow-x", 420, 120)),
        box("Mark bg", 0, Y + 3, 290, H - 3, None, A("wipe-right", 360, 200), bg=S["dark"]),
        img("League", 14, Y + 9, 80, H - 18, "{league.logo}", A("pop", 320, 360), show="league.logo"),
        img("Brand", 14, Y + 9, 80, H - 18, "{brand.logo}", A("pop", 320, 360), show="!league.logo && brand.logo"),
        txt("Label", 104, Y + 3, 176, H - 3, U(S, "ticker.label"), 30, A("fade", 260, 440), show="ticker.label", font=f, weight=800),
        txt("Label fallback", 104, Y + 3, 176, H - 3, U(S, "league.name"), 30, A("fade", 260, 440), show="!ticker.label && league.name", font=f, weight=800),
        el("ticker", "Crawl", 300, Y + 3, 1620, H - 3, A("fade", 400, 500), bind="ticker.items",
           style={"size": 32, "weight": 800, "color": "$text", "font": f, "speed": 110, "headFill": "$accent", "headColor": S["hiText"], "upper": S["up"]}),
    ]
    return {"name": "Bottom Ticker", "group": "ticker", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ================================================================ COMPACT BUG / TAB LOWER THIRD / UMPIRES / DEFENSE BANNERS
def scorebug_compact(S, title=False):
    """Top-left compact bug: team rows (logo, abbr, score) each with a pitcher / batter sub-line, then inning, diamond,
    count and outs. title=True adds a header (Notes > Compact scorebug title) and a sponsor tile on the right."""
    f = S["font"]
    X, Y = 36, 30 + (36 if title else 0)
    TW, RH, SH = 340, 54, 28
    RB = 150
    E = []
    if title:
        E += [box("Title bar", X, Y - 36, TW + RB, 36, None, A("wipe-down", 320, 300), show="notes.bugTitle", bg=S["strip"]),
              txt("Title", X + 12, Y - 36, TW + RB - 24, 36, U(S, "notes.bugTitle"), 22, A("fade", 240, 420), show="notes.bugTitle", font=f, weight=800,
                  color=S["stripText"], tracking=1)]
    for i, side in enumerate(("away", "home")):
        y = Y + i * (RH + SH)
        d = i * 80
        E += [box("%s row" % side, X, y, TW, RH, None, A("wipe-right", 360, d), bg=TG(S, side)),
              box("%s logo tile" % side, X, y, 64, RH, "#FFFFFF@0.12", A("fade", 260, 160 + d))]
        E += logo_or_abbr("%s logo" % side, X + 6, y + 5, 52, RH - 10, side, 22, A("pop", 320, 220 + d), S=S)
        E += [txt("%s abbr" % side, X + 76, y, 160, RH, U(S, "%s.abbr" % side), 38, A("reveal-up", 300, 260 + d), font=f, weight=800, textShadow=True),
              txt("%s runs" % side, X + TW - 86, y, 76, RH, "{%s.runs}" % side, 44, A("reveal-up", 300, 300 + d, change="pop"), font=f, weight=800,
                  align="right", textShadow=True),
              box("%s sub" % side, X, y + RH, TW, SH, None, A("wipe-down", 260, 280 + d), bg=S["dark"]),
              txt("%s pitcher" % side, X + 12, y + RH, 200, SH, U(S, "pitcher.last"), 18, A("fade", 240, 420 + d),
                  show="fieldingSide==%s && pitcher.last && %s" % (side, LIVE), font=f, weight=800),
              txt("%s pc" % side, X + 200, y + RH, TW - 212, SH, "P: {pitcher.today.pc|zero}", 18, A("fade", 240, 440 + d, change="flash"),
                  show="fieldingSide==%s && pitcher.last && %s" % (side, LIVE), font=f, weight=800, align="right"),
              txt("%s batter" % side, X + 12, y + RH, 220, SH, "{batter.slot|dot}" + U(S, "batter.last"), 18, A("fade", 240, 420 + d),
                  show="battingSide==%s && batter.last && %s" % (side, LIVE), font=f, weight=800),
              txt("%s line" % side, X + 220, y + RH, TW - 232, SH, "{batter.today.hab}", 18, A("fade", 240, 440 + d, change="flash"),
                  show="battingSide==%s && batter.last && %s" % (side, LIVE), font=f, weight=800, align="right"),
              txt("%s record" % side, X + 12, y + RH, TW - 24, SH, "{%s.record}" % side, 18, A("fade", 240, 420 + d), show="!" + LIVE, font=f, weight=700,
                  color="$dim")]
    H = 2 * (RH + SH)
    rx = X + TW
    E += [box("Situation", rx, Y, RB, H, None, A("wipe-right", 360, 160), bg=S["dark"]),
          txt("Inning", rx + 6, Y + 4, RB - 14, 30, "{arrow}{inning}", 22, A("fade", 240, 380, change="flash"), show=LIVE, font=f, weight=800, align="right"),
          el("bases", "Bases", rx + 12, Y + 26, RB - 24, 62, A("pop", 360, 400), show=LIVE, bind="bases",
             style={"layout": "tight", "on": "#FFFFFF", "off": "#FFFFFF@0.08", "stroke": "#FFFFFF@0.9", "strokeW": 2.5}),
          txt("Count", rx, Y + 92, RB, 40, "{count}", 32, A("reveal-up", 300, 440, change="roll"), show=LIVE, font=f, weight=800, align="center"),
          el("dots", "Outs", rx, Y + 134, RB, 22, A("fade", 240, 460), show=LIVE, bind="outs",
             style={"total": 2, "size": 13, "gap": 8, "on": "#FFFFFF", "off": "#FFFFFF@0.22", "align": "center"}),
          txt("Final", rx, Y, RB, H, "{statusText}", 26, A("fade", 240, 380), show="!" + LIVE, font=f, weight=800, align="center", wrap=True, fit=False)]
    if title:
        E += [box("Sponsor tile", rx + RB, Y - 36, 170, H + 36, "#FFFFFF", A("wipe-right", 360, 260), show="sponsor.on"),
              img("Sponsor logo", rx + RB + 12, Y - 24, 146, H + 12, "{sponsor.logo}", A("fade", 300, 460, change="fade"), show="sponsor.on && sponsor.logo"),
              txt("Sponsor name", rx + RB + 10, Y - 36, 150, H + 36, "{sponsor.name}", 26, A("fade", 300, 460, change="fade"),
                  show="sponsor.on && !sponsor.logo", font=f, weight=800, color="#121620", align="center", wrap=True, fit=False)]
    else:
        E += sponsor_tab(X, Y + H + 4, TW + RB, 40, 520, radius=S["radius"], a_type="wipe-down")
    return {"name": "Scorebug: Compact%s" % (" + Title" if title else ""), "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "half_{halfKey}, scorebug"}


def lower_tab(S, kind):
    """Team-colour bar with logo, headshot, position / number, first + LAST, four stats and a tab (Notes > Lower-third tab)."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y, W, H = 430, 900, 1060, 80
    cols = ([("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
             ("SO", "{pitcher.season.k|zero}")] if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}"), ("OBP", "{batter.season.obp|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}")])
    E = [
        box("Bar", X + 80, Y, W - 80, H, None, A("wipe-right", 420, 0, out=OUT), bg=TG(S, team), shadow=True),
        box("Tab", X + 220, Y - 32, 300, 32, None, A("wipe-up", 300, 360), bg=S["dark"]),
        txt("Tab text", X + 232, Y - 32, 280, 32, U(S, "notes.tab"), 20, A("fade", 240, 460), show="notes.tab", font=f, weight=800, tracking=1),
        txt("Tab default", X + 232, Y - 32, 280, 32, L(S, "This season"), 20, A("fade", 240, 460), show="!notes.tab", font=f, weight=800, tracking=1),
    ] + logo_or_abbr("Logo", X, Y - 10, 110, H + 20, team, 34, A("pop", 380, 200), S=S) + [
        img("Headshot", X + 110, Y - 22, 110, H + 22, "{%s.photo}" % who, A("slide-up", 380, 300, dist=20), show="%s.photo" % who, fit="cover",
            focus="center top"),
        txt("Pos", X + 226, Y + 6, 50, 30, U(S, "%s.pos" % who), 20, A("fade", 240, 420), font=f, weight=800, align="center", color="$dim"),
        txt("Number", X + 226, Y + 34, 50, 40, "{%s.number}" % who, 28, A("fade", 240, 440), font=f, weight=800, align="center"),
        txt("First", X + 286, Y + 4, 260, 28, U(S, "%s.first" % who), 22, A("fade", 260, 440), font=f, weight=700),
        txt("Last", X + 286, Y + 26, 260, 52, U(S, "%s.last" % who), 46, A("reveal-up", 340, 420), font=f, weight=800),
    ]
    cw = (W - 560) / 4.0
    for i, (lab, val) in enumerate(cols):
        cx = int(X + 560 + i * cw)
        E += [txt("%s label" % lab, cx, Y + 4, int(cw), 26, lab, 20, A("fade", 240, 480 + i * 60), font=f, weight=700, align="center", color="$dim"),
              txt("%s value" % lab, cx, Y + 26, int(cw), 50, val, 42, A("reveal-up", 320, 500 + i * 60), font=f, weight=800, align="center")]
    E += sponsor_tab(X + W - 300, Y - 50, 300, 44, 640, radius=S["radius"], a_type="wipe-up")
    return {"name": ("Pitcher" if kind == "pit" else "Batter") + " Lower Third (Tab)", "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E}


def umpires_card(S):
    """Tonight's umpires: league / brand mark header, up to six rows of name, note and position (Custom panel > Umpires)."""
    f = S["font"]
    X, Y, W = 120, 110, 460
    E = [card(S, "Card", X, Y, W, 110 + 6 * 82),
         box("Head", X, Y, W, 96, None, A("wipe-right", 380, 200), bg=S["dark"], radius=S["cardRadius"]),
         img("League", X + 14, Y + 12, 130, 72, "{league.logo}", A("pop", 320, 360), show="league.logo"),
         img("Brand", X + 14, Y + 12, 130, 72, "{brand.logo}", A("pop", 320, 360), show="!league.logo && brand.logo"),
         txt("Title", X + 150, Y + 6, W - 166, 84, L(S, "Tonight's Umpires"), 34, A("reveal-up", 360, 420), font=f, weight=800, align="center",
             wrap=True, fit=False, lineH=1)]
    for i in range(6):
        p = "umps.%d" % i
        y = Y + 108 + i * 82
        E += [txt("Ump %d name" % i, X + 26, y + 6, W - 120, 38, U(S, p + ".name"), 30, A("slide-right", 320, 520 + i * 80, dist=30), show=p + ".name",
                  font=f, weight=800),
              txt("Ump %d note" % i, X + 26, y + 40, W - 120, 30, U(S, p + ".note"), 22, A("fade", 260, 560 + i * 80), show=p + ".note", font=f, weight=600,
                  color="$dim"),
              txt("Ump %d pos" % i, X + W - 90, y + 6, 66, 64, "{%s.pos}" % p, 30, A("pop", 280, 600 + i * 80), show=p + ".name", font=f, weight=800,
                  align="right", color="$accent")]
    return {"name": "Umpires", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E}


def defense_banner(S, which):
    """Defense banner: headshots of the outfield (LF CF RF) or infield (3B SS 2B 1B) on team-colour rays, name bar under each."""
    f = S["font"]
    pos = ["LF", "CF", "RF"] if which == "of" else ["3B", "SS", "2B", "1B"]
    X, W = 100, 1720
    Y, PH, NH = 560, 200, 92
    rays = ("repeating-conic-gradient(from 0deg at 50% 135%, color-mix(in srgb, {team.color} 70%, #000) 0deg 5deg, {team.color} 5deg 10deg)")
    E = [box("Rays", X, Y, W, PH, None, A("wipe-up", 460, 0, out={"type": "fade", "dur": 260, "delay": 160, "ease": "in"}), bg=rays,
             borderW=2, borderColor="#FFFFFF@0.3"),
         box("Glow", X, Y, W, PH, None, A("fade", 500, 200), bg="radial-gradient(ellipse at 50% 120%, rgba(255,255,255,.25), transparent 60%)"),
         box("Names", X, Y + PH, W, NH, None, A("wipe-right", 420, 160, out={"type": "fade", "dur": 260, "delay": 80, "ease": "in"}), bg=S["dark"])]
    sw = W / float(len(pos))
    for i, ps in enumerate(pos):
        p = "team.defense.%s" % ps
        cx = int(X + i * sw + sw / 2)
        d = 300 + i * 120
        E += [img("%s photo" % ps, cx - 120, Y + 6, 240, PH - 6, "{%s.photo}" % p, A("slide-up", 420, d, dist=30), show=p + ".photo", fit="contain",
                  focus="center bottom"),
              txt("%s no photo" % ps, cx - 120, Y, 240, PH, "{%s.number}" % p, 96, A("pop", 360, d), show="!%s.photo && %s.name" % (p, p), font=f, weight=800,
                  align="center", color="#FFFFFF@0.5"),
              box("%s pos tile" % ps, cx - 170, Y + PH + 10, 56, NH - 20, None, A("pop", 300, d + 160), show=p + ".name", bg=TG(S, "team"),
                  radius=S["radius"]),
              txt("%s pos" % ps, cx - 170, Y + PH + 10, 56, NH - 20, ps, 24, A("pop", 300, d + 160), show=p + ".name", font=f, weight=800, align="center"),
              txt("%s first" % ps, cx - 100, Y + PH + 6, 300, 38, U(S, p + ".first"), 30, A("fade", 260, d + 220), show=p + ".name", font=f, weight=700),
              txt("%s last" % ps, cx - 100, Y + PH + 40, 300, 46, U(S, p + ".last"), 40, A("reveal-up", 300, d + 240), show=p + ".name", font=f, weight=800)]
    return {"name": "Defense: %s" % ("Outfield" if which == "of" else "Infield"), "group": "full", "autoHide": 12, "side": "fielding", "sided": True,
            "elements": E}


# ================================================================ DEFENSE ON THE FIELD / DEFENSIVE LINEUP / MATCHUP / SPLIT CARD / BUMPER
FIELD_SPOTS = {"CF": (960, 268), "LF": (330, 318), "RF": (1590, 318), "SS": (660, 410), "2B": (1260, 410),
               "P": (960, 540), "3B": (330, 548), "1B": (1590, 548), "C": (960, 690)}


def defense_field(S):
    """Name plates placed on the field at each position, under a sponsor + team header (for the high home camera)."""
    f = S["font"]
    E = [box("Header", 150, 76, 1620, 92, None, A("wipe-right", 440, 0, out={"type": "fade", "dur": 260, "delay": 300, "ease": "in"}),
             bg=TG(S, "team"), borderW=3, borderColor="#FFFFFF@0.85", shadow=True),
         box("Sponsor box", 150, 76, 460, 92, "#FFFFFF", A("wipe-right", 380, 160), show="sponsor.on"),
         img("Sponsor logo", 172, 86, 416, 72, "{sponsor.logo}", A("fade", 300, 360, change="fade"), show="sponsor.on && sponsor.logo"),
         txt("Sponsor name", 172, 76, 416, 92, "{sponsor.name}", 44, A("fade", 300, 360, change="fade"), show="sponsor.on && !sponsor.logo", font=f,
             weight=800, color="#121620", align="center")]
    E += logo_or_abbr("Header logo", 640, 84, 90, 76, "team", 34, A("pop", 360, 300), S=S)
    E += [txt("Title", 750, 76, 980, 92, L(S, "{team.nick|upper} Defense"), 58, A("reveal-up", 380, 380), font=f, weight=800, textShadow=True)]
    for i, (ps, (cx, cy)) in enumerate(sorted(FIELD_SPOTS.items(), key=lambda kv: kv[1][1])):
        p = "team.defense.%s" % ps
        W = 380 if ps != "C" else 420
        x, y = cx - W // 2, cy - 33
        d = 500 + i * 90
        on = p + ".name"
        E += [box("%s plate" % ps, x, y, W, 66, None, A("pop", 340, d), show=on, bg=TG(S, "team"), borderW=3, borderColor="#FFFFFF@0.85",
                  shadow="0 22px 22px rgba(0,0,0,.35)"),
              img("%s logo" % ps, x + 8, y + 7, 54, 52, "{team.logo}", A("fade", 260, d + 120), show=both(on, "team.logo")),
              txt("%s num" % ps, x + 66, y + 4, 48, 30, "{%s.number}" % p, 22, A("fade", 240, d + 140), show=on, font=f, weight=700, align="center",
                  color="$dim"),
              txt("%s pos" % ps, x + 66, y + 32, 48, 30, ps, 22, A("fade", 240, d + 140), show=on, font=f, weight=700, align="center", color="$dim"),
              txt("%s first" % ps, x + 122, y + 4, W - 134, 28, U(S, p + ".first"), 22, A("fade", 240, d + 160), show=on, font=f, weight=700),
              txt("%s last" % ps, x + 122, y + 26, W - 134, 38, U(S, p + ".last"), 34, A("reveal-up", 280, d + 160), show=on, font=f, weight=800)]
    return {"name": "Defense: On the Field", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": E, "sponsorSlot": "defense"}


LINEUP_SPOTS = {"CF": (1208, 214), "LF": (964, 250), "RF": (1458, 250), "SS": (1110, 384), "2B": (1320, 384),
                "3B": (926, 470), "1B": (1496, 470), "P": (1208, 526), "C": (1208, 690)}


def defensive_lineup(S):
    """Defensive lineup card: big logo and team name on the left, headshot cards on a diamond outline on the right."""
    f = S["font"]
    E = [card(S, "Card", 162, 72, 1598, 900),
         box("Bottom rule", 162, 966, 1598, 6, "{team.color}", A("grow-x", 420, 300)),
         box("Left panel", 196, 198, 488, 658, None, A("fade", 400, 200), bg=S["panel2"], radius=S["cardRadius"], borderW=2,
             borderColor="color-mix(in srgb, {team.color} 70%, transparent)")]
    E += logo_or_abbr("Big logo", 226, 214, 428, 500, "team", 140, A("zoom-out", 520, 380), S=S)
    E += [txt("Team city", 196, 860, 488, 50, U(S, "team.city"), 44, A("fade", 300, 520), show="team.city", font=f, weight=800, align="center"),
          txt("Team nick", 196, 902, 488, 56, U(S, "team.nick"), 52, A("reveal-up", 340, 560), font=f, weight=800, align="center"),
          txt("Title", 790, 80, 836, 110, L(S, "Defensive Lineup"), 68, A("reveal-up", 400, 300), font=f, weight=800, align="center"),
          box("Field panel", 790, 198, 838, 658, None, A("fade", 400, 260), bg=S["dark"], radius=S["cardRadius"], borderW=2,
              borderColor="color-mix(in srgb, {team.color} 70%, transparent)"),
          box("Diamond", 1032, 400, 352, 352, None, A("fade", 500, 420), rotate=45, borderW=2, borderColor="#FFFFFF@0.28"),
          box("Outfield arc", 900, 230, 616, 400, None, A("fade", 500, 420), radius="50% 50% 0 0", borderW=2, borderColor="#FFFFFF@0.16")]
    for i, (ps, (cx, top)) in enumerate(sorted(LINEUP_SPOTS.items(), key=lambda kv: kv[1][1])):
        p = "team.defense.%s" % ps
        x, y = cx - 60, top
        d = 600 + i * 90
        on = p + ".name"
        E += [box("%s card" % ps, x, y, 120, 160, None, A("pop", 320, d), show=on, bg=S["panel"], radius=4, borderW=1, borderColor="#FFFFFF@0.25"),
              img("%s photo" % ps, x, y, 120, 104, "{%s.photo}" % p, A("fade", 300, d + 100), show=both(on, p + ".photo"), fit="cover", focus="center top"),
              box("%s tag" % ps, x + 4, y + 80, 72, 22, "#000000@0.7", A("fade", 240, d + 140), show=on, radius=2),
              txt("%s tag t" % ps, x + 4, y + 80, 72, 22, ps + " | {%s.number}" % p, 15, A("fade", 240, d + 140), show=on, font=f, weight=800, align="center"),
              txt("%s first" % ps, x + 2, y + 104, 116, 26, U(S, p + ".first"), 17, A("fade", 240, d + 160), show=on, font=f, weight=800, align="center"),
              txt("%s last" % ps, x + 2, y + 128, 116, 28, U(S, p + ".last"), 19, A("fade", 240, d + 180), show=on, font=f, weight=800, align="center")]
    return {"name": "Defensive Lineup", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": E, "sponsorSlot": "defense"}


def matchup_diamond(S):
    """Diamond backdrop with the brand logo on top, two team rows (logo tile, city, nickname), VS bar and venue."""
    f = S["font"]
    E = [box("Diamond", 692, 172, 536, 536, None, A("zoom-out", 520, 0, out={"type": "fade", "dur": 300, "delay": 200, "ease": "in"}), rotate=45,
             bg="repeating-linear-gradient(90deg, #FFFFFF10 0 18px, transparent 18px 36px), " + S["panel2"], borderW=10, borderColor="#FFFFFF@0.75",
             shadow=True),
         img("Brand", 830, 96, 260, 120, "{brand.logo}", A("pop", 420, 300), show="brand.logo", shadow=True)]
    for i, side in enumerate(("away", "home")):
        y = 330 + i * 236
        d = 420 + i * 160
        E += [box("%s tile" % side, 600, y, 180, 170, None, A("wipe-right", 380, d), bg="linear-gradient(180deg, #FFFFFF, #C9CED6)", borderW=3,
                  borderColor="#FFFFFF"),
              box("%s city bar" % side, 780, y, 540, 52, None, A("wipe-right", 380, d + 80), bg="linear-gradient(180deg, #F2F4F7, #BFC5CE)"),
              txt("%s city" % side, 800, y, 500, 52, U(S, "%s.city" % side), 30, A("fade", 260, d + 240), show="%s.city" % side, font=f, weight=800,
                  color="#13161B"),
              box("%s nick bar" % side, 780, y + 52, 540, 118, None, A("wipe-right", 400, d + 120), bg=TG(S, side), borderW=2, borderColor="#FFFFFF@0.6"),
              txt("%s nick" % side, 800, y + 52, 500, 118, U(S, "%s.nick" % side), 76, A("reveal-up", 360, d + 280), font=f, weight=800, textShadow=True)]
        E += logo_or_abbr("%s logo" % side, 612, y + 12, 156, 146, side, 50, A("pop", 360, d + 200), color="#13161B", S=S)
    E += [box("VS bar", 600, 506, 720, 54, "#06080C", A("grow-x", 380, 640)),
          txt("VS", 600, 506, 720, 54, L(S, "vs"), 34, A("pop", 300, 760), font=f, weight=800, align="center"),
          box("Venue bar", 700, 820, 520, 50, None, A("wipe-up", 360, 900), show="venue", bg="#0A0C10", borderW=2, borderColor="#FFFFFF@0.6"),
          txt("Venue", 700, 820, 520, 50, U(S, "venue"), 24, A("fade", 260, 1000), show="venue", font=f, weight=800, align="center", tracking=1)]
    return {"name": "Matchup: Diamond", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def split_card(S):
    """Two-column stat card: player photo, title, header with column labels, up to six rows and a footer (Custom panel > Split stat card)."""
    f = S["font"]
    X, Y, W = 560, 150, 1060
    rows = 6
    RH = 76
    H = 96 + 50 + rows * RH + 56
    E = [img("Team mark", 120, 300, 420, 420, "{batting.logo}", A("fade", 600, 0), show="batting.logo", opacity=0.9),
         card(S, "Card", X, Y, W, H),
         box("Title bar", X, Y, W, 96, None, A("wipe-right", 380, 200), bg=S["strip"]),
         txt("Title", X, Y, W, 96, U(S, "split.title"), 62, A("reveal-up", 360, 320), font=f, weight=800, align="center", color=S["stripText"]),
         box("Head bar", X, Y + 96, W, 50, None, A("wipe-right", 340, 300), bg=S["dark"]),
         txt("Sub", X + 20, Y + 96, 360, 50, U(S, "split.sub"), 26, A("fade", 260, 420), show="split.sub", font=f, weight=800),
         txt("Col1", X + W - 340, Y + 96, 160, 50, U(S, "split.col1"), 24, A("fade", 260, 440), font=f, weight=800, align="center"),
         txt("Col2", X + W - 170, Y + 96, 160, 50, U(S, "split.col2"), 24, A("fade", 260, 460), font=f, weight=800, align="center"),
         img("Photo", X + 10, Y + 150, 380, rows * RH, "{split.photo}", A("slide-right", 420, 400, dist=40), show="split.photo", fit="contain",
             focus="center bottom")]
    for i in range(rows):
        p = "split.rows.%d" % i
        y = Y + 146 + i * RH
        d = 520 + i * 80
        E += [box("Row %d" % i, X + 400, y + 4, W - 410, RH - 8, None, A("wipe-right", 300, d), show=p + ".label", bg=S["panel2"]),
              txt("Row %d label" % i, X + 420, y, 300, RH, U(S, p + ".label"), 36, A("fade", 240, d + 100), show=p + ".label", font=f, weight=800),
              box("Row %d a bg" % i, X + W - 340, y + 4, 160, RH - 8, None, A("fade", 240, d + 60), show=p + ".label", bg=S["val"]),
              txt("Row %d a" % i, X + W - 340, y, 160, RH, "{%s.a}" % p, 40, A("reveal-up", 280, d + 140), show=p + ".label", font=f, weight=800,
                  align="center", color=S["valText"]),
              box("Row %d b bg" % i, X + W - 172, y + 4, 162, RH - 8, None, A("fade", 240, d + 60), show=p + ".label", bg=S["val"]),
              txt("Row %d b" % i, X + W - 170, y, 160, RH, "{%s.b}" % p, 40, A("reveal-up", 280, d + 160), show=p + ".label", font=f, weight=800,
                  align="center", color=S["valText"])]
    E += [box("Foot bar", X, Y + H - 56, W, 56, None, A("wipe-up", 300, 1000), show="split.foot", bg=S["strip"]),
          txt("Foot", X, Y + H - 56, W, 56, U(S, "split.foot"), 28, A("fade", 260, 1100), show="split.foot", font=f, weight=800, align="center",
              color=S["stripText"])]
    return {"name": "Split Stat Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "batter_card"}


def brand_bumper(S):
    """Brand bumper: the short brand name stacked and scrolling on the left, pinstripes on the right, logo in a rounded frame."""
    f = S["font"]
    outA = {"type": "fade", "dur": 400, "delay": 200, "ease": "in"}
    E = [box("Background", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=outA), bg="linear-gradient(135deg, color-mix(in srgb, {brand.color} 80%, #fff), {brand.color} 50%, color-mix(in srgb, {brand.color} 60%, #000))"),
         box("Pinstripes", 960, 0, 960, 1080, None, A("wipe-right", 700, 200, out=outA),
             bg="repeating-linear-gradient(-60deg, transparent 0 22px, color-mix(in srgb, {brand.color2} 60%, transparent) 22px 24px)", opacity=0.55),
         box("Left field", 0, 0, 960, 1080, None, A("wipe-up", 600, 100, out=outA), bg="linear-gradient(180deg, color-mix(in srgb, {brand.color} 85%, #000), color-mix(in srgb, {brand.color} 60%, #000))")]
    for r in range(2):
        E.append({"id": nid("t"), "name": "Stack %d" % (r + 1), "type": "text", "x": -40 + r * 440, "y": -1200, "w": 600, "h": 3600,
                  "text": "\n".join(["{brand.short|upper}"] * 12),
                  "style": {"color": "color-mix(in srgb, {brand.color2} 85%, #fff)" if r else "{brand.color2}", "size": 300, "weight": 900, "align": "left", "valign": "top",
                            "padX": 0, "fit": False, "wrap": True, "font": f, "lineH": 0.82, "tracking": -6},
                  "anim": A("fade", 600, 200 + r * 150, out=outA, loop={"type": "scroll-y", "dur": 14000 + r * 3000, "amount": 600 if r else -600,
                                                                       "pingpong": True})})
    E += [box("Frame", 520, 330, 880, 420, "#FFFFFF", A("zoom-out", 600, 500, out=outA), radius=90, shadow="0 30px 80px rgba(0,0,0,.45)"),
          box("Frame inner", 568, 378, 784, 324, None, A("fade", 400, 650, out=outA), radius=56, bg="linear-gradient(90deg, {brand.color2}, {brand.color} 50%)"),
          img("Logo", 600, 400, 720, 280, "{brand.logo}", A("pop", 500, 800, out=outA), show="brand.logo"),
          txt("Name", 600, 400, 720, 280, "{brand.short|upper}", 180, A("pop", 500, 800, out=outA), show="!brand.logo", font=f, weight=900, align="center")]
    return {"name": "Brand Bumper", "group": "full", "autoHide": 6, "side": "", "sided": False, "elements": E}


# ================================================================ LIST CARDS (schedule, lineup results, projected lineup, pitchers,
# probables, lineup with featured player, one-column stat card) + WORD BUMPER
def list_frame(S, X, Y, W, H, title, sub, logo_team=None, foot=None, delay=0):
    """Header (logo tile, title bar, sponsor tile), sub strip, body panel and an optional footer line."""
    f = S["font"]
    E = [box("Body", X, Y + 96, W, H - 96, None, A("fade", 420, delay + 100, out={"type": "fade", "dur": 280, "delay": 120, "ease": "in"}),
             bg=S["panel"], shadow=S["shadow"])]
    tx = X
    if logo_team:
        E += [box("Logo tile", X, Y, 130, 96, None, A("wipe-right", 360, delay), bg=S["strip"])]
        E += logo_or_abbr("Logo", X + 12, Y + 8, 106, 80, logo_team, 34, A("pop", 360, delay + 200), color=S["stripText"], S=S)
        tx = X + 130
    E += [box("Title bar", tx, Y, X + W - tx, 96, None, A("wipe-right", 400, delay + 80), bg=S["dark"]),
          txt("Title", tx + 24, Y, X + W - tx - 220, 96, title, 64, A("reveal-up", 380, delay + 240), font=f, weight=800, align="center"),
          box("Sponsor tile", X + W - 180, Y, 180, 96, "#FFFFFF", A("wipe-left", 340, delay + 200), show="sponsor.on"),
          img("Sponsor logo", X + W - 168, Y + 10, 156, 76, "{sponsor.logo}", A("fade", 300, delay + 400, change="fade"), show="sponsor.on && sponsor.logo"),
          txt("Sponsor name", X + W - 172, Y, 164, 96, "{sponsor.name}", 28, A("fade", 300, delay + 400, change="fade"), show="sponsor.on && !sponsor.logo",
              font=f, weight=800, color="#121620", align="center", wrap=True, fit=False),
          box("Sub strip", X, Y + 96, W, 42, None, A("wipe-right", 360, delay + 200), bg="linear-gradient(180deg, #3D7BD0, #24569E)"),
          txt("Sub", X, Y + 96, W, 42, sub, 24, A("fade", 260, delay + 360), font=f, weight=700, align="center", tracking=1)]
    if foot:
        E += [box("Foot bar", X, Y + H, W, 44, None, A("wipe-down", 300, delay + 900), show=foot[1], bg=S["dark"]),
              txt("Foot", X + 20, Y + H, W - 40, 44, foot[0], 24, A("fade", 260, delay + 1000), show=foot[1], font=f, weight=800, align="center")]
    return E


def tonight_card(S):
    """Tonight on ...: time, show and talent for up to four shows, and a footer line (Custom panel > Tonight's schedule)."""
    f = S["font"]
    X, Y, W = 260, 120, 1400
    rows, RH = 4, 160
    title = "{schedule.title|upper}" if S["up"] else "{schedule.title}"
    E = list_frame(S, X, Y, W, 96 + 42 + rows * RH, "", L(S, "{schedule.sub}"), None, ("\u25B6 " + U(S, "schedule.foot"), "schedule.foot"))
    E = [e for e in E if e["name"] not in ("Title", "Sub")]
    E += [txt("Title", X + 24, Y, W - 230, 96, title, 64, A("reveal-up", 380, 240), show="schedule.title", font=f, weight=800, align="center"),
          txt("Title default", X + 24, Y, W - 230, 96, L(S, "Tonight on {brand.short|upper}"), 64, A("reveal-up", 380, 240),
              show="!schedule.title && brand.short", font=f, weight=800, align="center"),
          txt("Title plain", X + 24, Y, W - 230, 96, L(S, "Tonight"), 64, A("reveal-up", 380, 240), show="!schedule.title && !brand.short",
              font=f, weight=800, align="center"),
          txt("Sub", X, Y + 96, W, 42, U(S, "schedule.sub"), 24, A("fade", 260, 360), show="schedule.sub", font=f, weight=700, align="center", tracking=1),
          txt("Sub default", X, Y + 96, W, 42, L(S, "Upcoming shows"), 24, A("fade", 260, 360), show="!schedule.sub", font=f, weight=700, align="center",
              tracking=1)]
    E += [img("Brand", X + 30, Y + 190, 380, 520, "{brand.logo}", A("zoom-out", 600, 300, loop={"type": "breathe", "dur": 6000, "amount": 0.03}),
              show="brand.logo"),
          txt("Brand name", X + 30, Y + 190, 380, 520, "{brand.short|upper}", 120, A("zoom-out", 600, 300), show="!brand.logo", font=f, weight=900,
              align="center")]
    for i in range(rows):
        p = "schedule.rows.%d" % i
        y = Y + 138 + i * RH
        d = 500 + i * 140
        E += [box("Row %d line" % i, X + 450, y + RH - 2, W - 480, 2, "#FFFFFF@0.25", A("grow-x", 300, d), show=p + ".time"),
              txt("Row %d time" % i, X + 450, y, 170, RH, "{%s.time}" % p, 54, A("reveal-up", 320, d + 60), show=p + ".time", font=f, weight=800,
                  align="right"),
              txt("Row %d show" % i, X + 650, y + 10, 330, RH - 20, U(S, p + ".show"), 38, A("fade", 300, d + 120), show=p + ".time", font=f, weight=800,
                  align="center", color="$accent", wrap=True, fit=False, lineH=0.95),
              box("Row %d divider" % i, X + 1000, y + 20, 3, RH - 40, "#FFFFFF@0.6", A("grow-y", 260, d + 160), show=p + ".talent"),
              txt("Row %d talent" % i, X + 1030, y + 6, W - 1060, RH - 12, U(S, p + ".talent"), 32, A("slide-left", 340, d + 200, dist=30),
                  show=p + ".talent", font=f, weight=800, wrap=True, fit=False, lineH=1.05)]
    return {"name": "Tonight's Schedule", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def lineup_results(S):
    """Starting lineup with tonight's line and results in words (2-4 | Walk, 2 Singles, RBI); the batter up is highlighted."""
    f = S["font"]
    X, Y, W = 210, 110, 1500
    RH = 64
    H = 96 + 42 + 9 * RH + 10
    E = list_frame(S, X, Y, W, H, U(S, "team.name"), L(S, "Starting lineup today"), "team", ("\u25B6 " + U(S, "notes.listFoot"), "notes.listFoot"))
    for i in range(9):
        p = "team.lineup.%d" % i
        y = Y + 142 + i * RH
        d = 520 + i * 70
        E += [box("Row %d hi" % i, X + 8, y, W - 16, RH - 4, None, A("fade", 300, d), show=p + ".isUp", bg="linear-gradient(90deg, #3396F5, #1D6DD3)"),
              box("Row %d line" % i, X + 30, y + RH - 3, W - 60, 1, "#FFFFFF@0.18", A("grow-x", 300, d), show=p + ".name"),
              txt("Row %d pos" % i, X + 20, y, 90, RH - 4, "{%s.pos}" % p, 24, A("fade", 240, d + 60), show=p + ".name", font=f, weight=700, align="center",
                  color="$dim"),
              txt("Row %d name" % i, X + 120, y, 560, RH - 4, U(S, p + ".name"), 36, A("slide-right", 300, d + 80, dist=30), show=p + ".name", font=f,
                  weight=800),
              box("Row %d hab bg" % i, X + 690, y, 190, RH - 4, "#000000@0.18", A("fade", 240, d + 80), show=p + ".name"),
              txt("Row %d hab" % i, X + 690, y, 190, RH - 4, "{%s.hab}" % p, 38, A("reveal-up", 280, d + 120, change="flash"), show=p + ".hab", font=f,
                  weight=800, align="center"),
              txt("Row %d plays" % i, X + 910, y, W - 940, RH - 4, U(S, p + ".plays"), 32, A("fade", 260, d + 160, change="flash"), show=p + ".plays",
                  font=f, weight=800)]
    return {"name": "Lineup: Tonight's Results", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E,
            "sponsorSlot": "lineup"}


def lineup_projected(S):
    """Lineup list: bats hand, name, position column; season header; footer line (Notes > List footnote)."""
    f = S["font"]
    X, Y, W = 500, 130, 1060
    RH = 66
    H = 96 + 42 + 9 * RH + 10
    E = list_frame(S, X, Y, W, H, L(S, "{team.nick|upper} Lineup"), L(S, "{seasonYear} Season"), None, ("\u25B6 " + U(S, "notes.listFoot"), "notes.listFoot"))
    E += [img("Team mark", 90, 300, 400, 420, "{team.logo}", A("fade", 600, 0), show="team.logo", opacity=0.95)]
    for i in range(9):
        p = "team.lineup.%d" % i
        y = Y + 142 + i * RH
        d = 520 + i * 70
        E += [box("Row %d bg" % i, X + 12, y + 3, W - 200, RH - 6, None, A("wipe-right", 300, d), show=p + ".name", bg=S["panel2"]),
              txt("Row %d bats" % i, X + 20, y, 50, RH, "{%s.bats}" % p, 24, A("fade", 240, d + 80), show=p + ".name", font=f, weight=700, align="center",
                  color="$dim"),
              txt("Row %d name" % i, X + 80, y, W - 300, RH, U(S, p + ".name"), 36, A("slide-right", 300, d + 80, dist=30), show=p + ".name", font=f,
                  weight=800),
              box("Row %d pos bg" % i, X + W - 176, y + 3, 164, RH - 6, None, A("fade", 240, d + 60), show=p + ".name", bg=S["val"]),
              txt("Row %d pos" % i, X + W - 176, y, 164, RH, "{%s.pos}" % p, 34, A("reveal-up", 280, d + 120), show=p + ".name", font=f, weight=800,
                  align="center", color=S["valText"])]
    return {"name": "Lineup: Projected", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E, "sponsorSlot": "lineup"}


def pitchers_today(S):
    """Every pitcher used today with headshot, name and IP | R | P, four per row."""
    f = S["font"]
    X, Y, W = 160, 100, 1600
    CW, CH = 400, 300
    H = 96 + 42 + 2 * CH + 10
    E = list_frame(S, X, Y, W, H, L(S, "Pitching"), L(S, "{team.nick|upper} today"), "team")
    for i in range(8):
        p = "team.pitchers.%d" % i
        cx = X + (i % 4) * CW
        y = Y + 142 + (i // 4) * CH
        d = 520 + i * 90
        E += [box("P%d bg" % i, cx + 6, y + 4, CW - 12, CH - 8, None, A("pop", 320, d), show=p + ".name", bg=S["panel2"], borderW=1,
                  borderColor="#FFFFFF@0.2"),
              img("P%d photo" % i, cx + 6, y + 4, CW - 12, 190, "{%s.photo}" % p, A("fade", 300, d + 120), show=both(p + ".name", p + ".photo"),
                  fit="contain", focus="center bottom"),
              txt("P%d name" % i, cx + 10, y + 196, CW - 20, 46, U(S, p + ".name"), 30, A("fade", 260, d + 160), show=p + ".name", font=f, weight=800,
                  align="center"),
              box("P%d line bg" % i, cx + 6, y + 244, CW - 12, 52, "#000000@0.3", A("fade", 240, d + 160), show=p + ".name"),
              txt("P%d line" % i, cx + 10, y + 244, CW - 20, 52, "{%s.statline}" % p, 30, A("reveal-up", 280, d + 200, change="flash"), show=p + ".name",
                  font=f, weight=800, align="center")]
    return {"name": "Pitchers Today", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": E}


def probables_card(S):
    """Series probables: up to three starters with headshot, name, stat line and a second line (Custom panel > Series probables)."""
    f = S["font"]
    X, Y, W = 200, 110, 1520
    CW = W // 3
    H = 96 + 42 + 600
    title = "{probables.title|upper}" if S["up"] else "{probables.title}"
    E = list_frame(S, X, Y, W, H, title, U(S, "probables.sub"), "team", ("\u25B6 " + U(S, "probables.foot"), "probables.foot"))
    for i in range(3):
        p = "probables.rows.%d" % i
        cx = X + i * CW
        y = Y + 142
        d = 520 + i * 160
        E += [box("C%d glow" % i, cx + 8, y + 8, CW - 16, 300, None, A("fade", 400, d), show=p + ".name",
                  bg="radial-gradient(ellipse at 50% 60%, color-mix(in srgb, $accent 40%, transparent), transparent 70%)"),
              img("C%d mark" % i, cx + 40, y + 40, 200, 220, "{team.logo}", A("fade", 400, d + 60), show=both(p + ".name", "team.logo"), opacity=0.35),
              img("C%d photo" % i, cx + 8, y + 8, CW - 16, 300, "{%s.photo}" % p, A("slide-up", 400, d + 120, dist=30), show=both(p + ".name", p + ".photo"),
                  fit="contain", focus="center bottom"),
              box("C%d name bg" % i, cx + 8, y + 308, CW - 16, 104, None, A("wipe-right", 320, d + 200), show=p + ".name", bg=S["dark"]),
              txt("C%d first" % i, cx + 30, y + 312, CW - 60, 34, U(S, p + ".first"), 26, A("fade", 260, d + 300), show=p + ".name", font=f, weight=700),
              txt("C%d last" % i, cx + 30, y + 344, CW - 60, 64, U(S, p + ".last"), 54, A("reveal-up", 320, d + 320), show=p + ".name", font=f, weight=800),
              txt("C%d line" % i, cx + 20, y + 440, CW - 40, 60, "{%s.line}" % p, 32, A("fade", 280, d + 400), show=p + ".line", font=f, weight=800,
                  align="center"),
              txt("C%d line2" % i, cx + 20, y + 500, CW - 40, 50, U(S, p + ".line2"), 30, A("fade", 280, d + 440), show=p + ".line2", font=f, weight=800,
                  align="center")]
        if i:
            E.append(box("Divider %d" % i, cx, y + 300, 2, 290, "#FFFFFF@0.25", A("grow-y", 300, 700)))
    return {"name": "Series Probables", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E, "sponsorSlot": "show"}


def lineup_feature(S):
    """Starting lineup with a featured player: big photo and a note on the left (picked player, else a top hitter), lineup with AVG on the right."""
    f = S["font"]
    X, Y, W = 120, 90, 1680
    RH = 70
    H = 96 + 42 + 9 * RH + 14
    E = list_frame(S, X, Y, W, H, U(S, "team.name"), L(S, "Starting lineup"), "team")
    E += [img("Mark", X + 30, Y + 200, 560, 560, "{team.logo}", A("fade", 500, 300), show="team.logo", opacity=0.25),
          img("Feature photo", X + 20, Y + 142, 620, H - 150, "{team.feature.photo}", A("slide-right", 480, 400, dist=40), show="team.feature.photo",
              fit="contain", focus="center bottom"),
          box("Note shade", X, Y + H - 210, 660, 210, None, A("fade", 300, 650), show="team.feature.name",
              bg="linear-gradient(180deg, transparent, rgba(0,0,0,.8) 35%)"),
          txt("Feature name", X + 60, Y + H - 186, 580, 60, U(S, "team.feature.name"), 44, A("reveal-up", 320, 720), show="team.feature.name", font=f,
              weight=800),
          box("Note rule", X + 40, Y + H - 120, 4, 96, "$accent", A("grow-y", 260, 700), show="team.feature.line"),
          txt("Note title", X + 60, Y + H - 120, 560, 40, U(S, "team.feature.title"), 28, A("fade", 260, 760), show="team.feature.line", font=f, weight=700),
          txt("Note line", X + 60, Y + H - 82, 560, 58, U(S, "team.feature.line"), 40, A("reveal-up", 320, 800), show="team.feature.line", font=f,
              weight=800)]
    LX = X + 680
    for i in range(9):
        p = "team.lineup.%d" % i
        y = Y + 146 + i * RH
        d = 520 + i * 70
        E += [box("Row %d hi" % i, LX, y, W - 700, RH - 4, None, A("fade", 300, d), show=p + ".isFeature", bg="linear-gradient(90deg, #3396F5, #1D6DD3)"),
              box("Row %d line" % i, LX, y + RH - 3, W - 700, 1, "#FFFFFF@0.25", A("grow-x", 300, d), show=p + ".name"),
              txt("Row %d pos" % i, LX + 10, y, 70, RH - 4, "{%s.pos}" % p, 28, A("fade", 240, d + 60), show=p + ".name", font=f, weight=700, align="center",
                  color="$dim"),
              txt("Row %d name" % i, LX + 90, y, 640, RH - 4, U(S, p + ".name") + "  {%s.bats}" % p, 40, A("slide-right", 300, d + 80, dist=30),
                  show=p + ".name", font=f, weight=800),
              txt("Row %d avg" % i, X + W - 200, y, 170, RH - 4, "{%s.avg|avg}" % p, 44, A("reveal-up", 280, d + 120), show=p + ".name", font=f, weight=800,
                  align="right")]
    return {"name": "Lineup: Featured Player", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "lineup"}


def stat_card_one(S):
    """One-column stat card: photo, title, header line and up to five label / value rows (uses the Split stat card text, first value only)."""
    f = S["font"]
    X, Y, W = 440, 90, 1200
    RH = 108
    H = 96 + 50 + 5 * RH + 20
    E = [img("Team mark", 40, 260, 400, 440, "{batting.logo}", A("fade", 600, 0), show="batting.logo"),
         card(S, "Card", X, Y, W, H),
         box("Title bar", X, Y, W, 96, None, A("wipe-right", 380, 200), bg=S["strip"]),
         txt("Title", X, Y, W, 96, U(S, "split.title"), 62, A("reveal-up", 360, 320), font=f, weight=800, align="center", color=S["stripText"]),
         box("Head bar", X, Y + 96, W, 50, None, A("wipe-right", 340, 300), bg=S["dark"]),
         txt("Sub", X + 20, Y + 96, W - 40, 50, U(S, "split.sub"), 28, A("fade", 260, 420), show="split.sub", font=f, weight=800),
         img("Photo", X + 14, Y + 156, 500, 5 * RH, "{split.photo}", A("slide-right", 420, 400, dist=40), show="split.photo", fit="contain",
             focus="center bottom")]
    for i in range(5):
        p = "split.rows.%d" % i
        y = Y + 152 + i * RH
        d = 520 + i * 90
        E += [box("Row %d" % i, X + 530, y + 6, W - 544, RH - 12, None, A("wipe-right", 300, d), show=p + ".label", bg=S["panel2"]),
              txt("Row %d label" % i, X + 556, y, 420, RH, U(S, p + ".label"), 44, A("fade", 240, d + 100), show=p + ".label", font=f, weight=800),
              box("Row %d v bg" % i, X + W - 200, y + 6, 186, RH - 12, None, A("fade", 240, d + 60), show=p + ".label", bg=S["val"]),
              txt("Row %d v" % i, X + W - 200, y, 186, RH, "{%s.a}" % p, 48, A("reveal-up", 280, d + 140), show=p + ".label", font=f, weight=800,
                  align="center", color=S["valText"])]
    return {"name": "Stat Card (One Column)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "batter_card"}


def word_bumper(S):
    """Word bumper: one word (Notes > Bumper word, default LINEUP) stacked in big blocky rows sliding past each other."""
    f = S["font"]
    outA = {"type": "fade", "dur": 400, "delay": 200, "ease": "in"}
    E = [box("Background", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=outA), bg="linear-gradient(180deg, #2F86E8, #0F57C2 60%, #0B3F96)"),
         box("Floor", 0, 820, 1920, 260, None, A("wipe-up", 600, 200, out=outA),
             bg="repeating-linear-gradient(90deg, #3A93F0 0 150px, #1E6FD6 150px 160px)", opacity=0.9)]
    for r in range(3):
        y = 40 + r * 270
        word = "{notes.bumperWord|upper}"
        for nm, show in (("Word %d" % (r + 1), "notes.bumperWord"), ("Word %d default" % (r + 1), "!notes.bumperWord")):
            E.append({"id": nid("t"), "name": nm, "type": "text", "x": -200, "y": y, "w": 2320, "h": 290,
                      "text": word if show == "notes.bumperWord" else "LINEUP", "showIf": show,
                      "style": {"color": "#D9DCE0", "size": 300, "weight": 900, "align": "center", "valign": "center", "padX": 0, "fit": False, "font": f,
                                "tracking": -4, "lineH": 0.9,
                                "textShadow": "0 4px 0 #9EA4AC, 0 8px 0 #868C95, 0 12px 0 #6F7680, 0 18px 24px rgba(0,0,0,.45)"},
                      "anim": A("slide-left" if r % 2 == 0 else "slide-right", 900, 150 + r * 120, dist=500, out=outA,
                                loop={"type": "scroll-x", "dur": 7000 + r * 900, "amount": -120 if r % 2 == 0 else 120, "pingpong": True})})
    return {"name": "Word Bumper", "group": "full", "autoHide": 4, "side": "", "sided": False, "elements": E}



def lineup_bench(S):
    """Starting lineup (position, first LAST, bats) with a featured player box and the bench split by batting hand."""
    f = S["font"]
    X, Y, W = 240, 96, 1440
    RH = 62
    E = [box("Head logo", X, Y, 300, 150, None, A("wipe-right", 360, 0), bg=TG(S, "team"))]
    E += logo_or_abbr("Logo", X + 20, Y + 10, 260, 130, "team", 50, A("pop", 360, 200), S=S)
    E += [box("Head", X + 300, Y, W - 560, 96, None, A("wipe-right", 380, 80), bg=S["strip"]),
          txt("Head title", X + 330, Y, W - 620, 96, L(S, "Starting Lineup"), 60, A("reveal-up", 360, 260), font=f, weight=800, color=S["stripText"]),
          box("Head rule", X + 300, Y + 96, W - 560, 6, "$accent", A("grow-x", 300, 300)),
          box("Head sub", X + 300, Y + 102, W - 560, 48, None, A("wipe-right", 340, 200), bg=S["dark"]),
          txt("Head date", X + 330, Y + 102, W - 620, 48, U(S, "dateText"), 28, A("fade", 260, 420), show="dateText", font=f, weight=700),
          box("Sponsor tile", X + W - 260, Y, 260, 150, "#FFFFFF", A("wipe-left", 360, 160), show="sponsor.on"),
          img("Sponsor logo", X + W - 244, Y + 16, 228, 118, "{sponsor.logo}", A("fade", 300, 360, change="fade"), show="sponsor.on && sponsor.logo"),
          txt("Sponsor name", X + W - 250, Y, 240, 150, "{sponsor.name}", 34, A("fade", 300, 360, change="fade"), show="sponsor.on && !sponsor.logo",
              font=f, weight=800, color="#121620", align="center", wrap=True, fit=False),
          box("Body", X, Y + 166, W, 9 * RH + 40, None, A("fade", 420, 200), bg=S["panel"], borderW=2, borderColor="#FFFFFF@0.5", shadow=S["shadow"])]
    for i in range(9):
        p = "team.lineup.%d" % i
        y = Y + 186 + i * RH
        d = 480 + i * 70
        E += [box("Row %d hi" % i, X + 20, y + 2, 660, RH - 4, None, A("fade", 300, d), show=p + ".isFeature", bg="linear-gradient(90deg, #3396F5, #1D6DD3)"),
              box("Row %d line" % i, X + 30, y + RH - 2, 640, 1, "#FFFFFF@0.25", A("grow-x", 300, d), show=p + ".name"),
              box("Row %d num bg" % i, X + 30, y + 8, 60, RH - 16, None, A("pop", 260, d), show=p + ".number", bg=S["strip"]),
              txt("Row %d num" % i, X + 30, y + 8, 60, RH - 16, "{%s.number}" % p, 30, A("pop", 260, d), show=p + ".number", font=f, weight=800,
                  align="center", color=S["stripText"]),
              txt("Row %d pos" % i, X + 100, y, 60, RH, "{%s.pos}" % p, 26, A("fade", 240, d + 60), show=p + ".name", font=f, weight=700, align="center",
                  color="$dim"),
              txt("Row %d name" % i, X + 170, y, 460, RH, U(S, p + ".first") + "  " + U(S, p + ".last"), 36, A("slide-right", 300, d + 80, dist=30),
                  show=p + ".name", font=f, weight=800),
              txt("Row %d bats" % i, X + 620, y, 50, RH, "{%s.bats}" % p, 30, A("fade", 240, d + 120), show=p + ".name", font=f, weight=800,
                  align="center", color="$dim")]
    FX = X + 720
    E += [box("Feature photo bg", FX, Y + 186, 300, 300, None, A("fade", 360, 700), show="team.feature.name", bg=TG(S, "team")),
          img("Feature photo", FX, Y + 186, 300, 300, "{team.feature.photo}", A("slide-up", 420, 760, dist=20), show="team.feature.photo", fit="cover",
              focus="center top"),
          box("Feature name bg", FX + 300, Y + 186, 380, 110, None, A("wipe-right", 340, 760), show="team.feature.name", bg=S["strip"]),
          txt("Feature name", FX + 310, Y + 186, 360, 110, U(S, "team.feature.name"), 40, A("fade", 260, 860), show="team.feature.name", font=f,
              weight=800, align="center", color=S["stripText"], wrap=True, fit=False, lineH=1),
          box("Feature rule", FX + 300, Y + 296, 380, 6, "$accent", A("grow-x", 260, 860), show="team.feature.name"),
          box("Feature note bg", FX + 300, Y + 302, 380, 184, None, A("wipe-right", 340, 820), show="team.feature.name", bg=S["dark"]),
          txt("Feature title", FX + 310, Y + 320, 360, 40, U(S, "team.feature.title"), 26, A("fade", 260, 920), show="team.feature.title", font=f,
              weight=700, align="center", color="$dim"),
          txt("Feature line", FX + 310, Y + 360, 360, 110, U(S, "team.feature.line"), 36, A("reveal-up", 320, 960), show="team.feature.line", font=f,
              weight=800, align="center", wrap=True, fit=False, lineH=1.05),
          box("Bench box", FX, Y + 510, 680, 240, None, A("fade", 360, 900), show="team.benchBy.any", bg="#000000@0.2", borderW=2, borderColor="#FFFFFF@0.6"),
          txt("Bench title", FX, Y + 510, 680, 44, L(S, "On the bench"), 26, A("fade", 260, 980), show="team.benchBy.any", font=f, weight=800,
              align="center", tracking=3)]
    for j, (lab, key) in enumerate((("Left", "L"), ("Switch", "S"), ("Right", "R"))):
        cx = FX + j * 227
        E += [box("Bench %s head" % key, cx, Y + 554, 226, 36, None, A("fade", 260, 1000), show="team.benchBy.any", bg=S["panel2"],
                  borderW=1, borderColor="#FFFFFF@0.5"),
              txt("Bench %s label" % key, cx, Y + 554, 226, 36, L(S, lab), 22, A("fade", 260, 1040), show="team.benchBy.any", font=f, weight=800,
                  align="center", tracking=2),
              txt("Bench %s names" % key, cx + 6, Y + 596, 214, 150, U(S, "team.benchBy.%s" % key), 26, A("fade", 300, 1100 + j * 80),
                  show="team.benchBy.%s" % key, font=f, weight=800, align="center", valign="top", wrap=True, fit=False, lineH=1.15)]
        if j:
            E.append(box("Bench div %d" % j, cx, Y + 554, 2, 196, "#FFFFFF@0.5", A("grow-y", 260, 1000), show="team.benchBy.any"))
    return {"name": "Lineup + Bench", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "lineup"}



def road_ahead(S):
    """The Road Ahead: two weeks Monday first; each day shows the date, opponent logo (home / away coloured) and result or time + TV."""
    f = S["font"]
    X, Y, W = 140, 70, 1640
    CW = W // 7
    title = "{road.title|upper}" if S["up"] else "{road.title}"
    E = [box("Head", X + 300, Y, W - 300, 120, None, A("wipe-right", 380, 0), bg=S["dark"], shadow=S["shadow"]),
         txt("Title", X + 320, Y, W - 640, 80, title, 60, A("reveal-up", 360, 200), show="road.title", font=f, weight=800, align="center"),
         txt("Title default", X + 320, Y, W - 640, 80, L(S, "The Road Ahead"), 60, A("reveal-up", 360, 200), show="!road.title", font=f, weight=800,
             align="center"),
         box("Key away", X + 560, Y + 84, 90, 26, "#2A2E35", A("fade", 260, 400), radius=4, borderW=1, borderColor="#FFFFFF@0.5"),
         txt("Key away t", X + 660, Y + 78, 220, 38, L(S, "Away games"), 24, A("fade", 260, 420), font=f, weight=800),
         box("Key home", X + 900, Y + 84, 90, 26, "$accent", A("fade", 260, 440), radius=4),
         txt("Key home t", X + 1000, Y + 78, 220, 38, L(S, "Home games"), 24, A("fade", 260, 460), font=f, weight=800),
         box("Sponsor tile", X, Y, 290, 120, "#FFFFFF", A("wipe-right", 340, 120), show="sponsor.on"),
         img("Sponsor logo", X + 14, Y + 12, 262, 96, "{sponsor.logo}", A("fade", 300, 300, change="fade"), show="sponsor.on && sponsor.logo"),
         txt("Sponsor name", X + 10, Y, 270, 120, "{sponsor.name}", 34, A("fade", 300, 300, change="fade"), show="sponsor.on && !sponsor.logo", font=f,
             weight=800, color="#121620", align="center", wrap=True, fit=False),
         box("Body", X, Y + 136, W, 800, None, A("fade", 400, 200), bg=S["panel"], shadow=S["shadow"], borderW=2, borderColor="#FFFFFF@0.3")]
    for d, nm in enumerate(("Mon", "Tues", "Wed", "Thur", "Fri", "Sat", "Sun")):
        E.append(txt("Day %d" % d, X + d * CW, Y + 140, CW, 50, L(S, nm).upper(), 32, A("fade", 260, 300 + d * 40), font=f, weight=800, align="center"))
    for i in range(14):
        p = "road.cells.%d" % i
        wk, d = divmod(i, 7)
        x = X + d * CW + 4
        y = Y + 196 + wk * 370
        dl = 420 + i * 45
        for st, bg in (("home", "linear-gradient(180deg, color-mix(in srgb, $accent 80%, #fff), $accent 50%, color-mix(in srgb, $accent 60%, #000))"),
                       ("away", "linear-gradient(180deg, #4A4F58, #2A2E35 50%, #1A1D22)"), ("off", "linear-gradient(180deg, #2A2E35, #1A1D22)")):
            E += [box("C%d %s date" % (i, st), x, y, CW - 8, 52, None, A("fade", 240, dl), show=both(p + ".day", p + "." + st), bg=bg),
                  box("C%d %s info" % (i, st), x, y + 240, CW - 8, 110, None, A("fade", 240, dl), show=both(p + ".day", p + "." + st), bg=bg)]
        E += [box("C%d mid" % i, x, y + 52, CW - 8, 188, None, A("fade", 240, dl), show=p + ".day", bg=S["panel2"]),
              txt("C%d date" % i, x, y, CW - 8, 52, "{%s.day}" % p, 34, A("fade", 240, dl + 60), show=p + ".day", font=f, weight=800, align="center",
                  textShadow=True),
              img("C%d logo" % i, x + 14, y + 62, CW - 36, 168, "{%s.logo}" % p, A("pop", 300, dl + 120), show=both(p + ".opp", p + ".logo")),
              txt("C%d opp" % i, x, y + 52, CW - 8, 188, "{%s.opp}" % p, 52, A("pop", 300, dl + 120), show=p + ".opp && !" + p + ".logo", font=f, weight=800,
                  align="center"),
              txt("C%d info" % i, x + 6, y + 240, CW - 20, 110, U(S, p + ".info"), 32, A("fade", 260, dl + 160), show=p + ".info", font=f, weight=800,
                  align="center", wrap=True, fit=False, lineH=1.05, textShadow=True)]
    return {"name": "The Road Ahead", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def around_league(S):
    """Around the league: today's other games as score tiles, four across, from the league scoreboard."""
    f = S["font"]
    X, Y, W = 160, 120, 1600
    TW, TH = 392, 330
    E = list_frame(S, X, Y, W, 96 + 42 + 2 * TH + 20, L(S, "Around the League"), L(S, "{league.name|upper}"), None)
    E = [e for e in E if e["name"] != "Sub"] + [txt("Sub", X, Y + 96, W, 42, U(S, "league.name"), 24, A("fade", 260, 360), show="league.name", font=f,
                                                    weight=700, align="center", tracking=1)]
    for i in range(8):
        p = "around.%d" % i
        x = X + 8 + (i % 4) * (TW + 6)
        y = Y + 150 + (i // 4) * TH
        d = 500 + i * 80
        E += [box("G%d bg" % i, x, y, TW, TH - 14, None, A("pop", 320, d), show=p + ".home", bg=S["panel2"], borderW=1, borderColor="#FFFFFF@0.25")]
        for r, side in enumerate(("away", "home")):
            yy = y + 16 + r * 112
            E += [img("G%d %s logo" % (i, side), x + 16, yy, 96, 96, "{%s.%sLogo}" % (p, side), A("fade", 260, d + 100), show=both(p + ".home", "%s.%sLogo" % (p, side))),
                  txt("G%d %s abbr" % (i, side), x + 124, yy, 160, 96, "{%s.%s}" % (p, side), 46, A("fade", 260, d + 120), show=p + ".home", font=f, weight=800),
                  txt("G%d %s runs" % (i, side), x + TW - 110, yy, 90, 96, "{%s.%sRuns}" % (p, side), 60, A("reveal-up", 280, d + 160, change="pop"),
                      show=p + ".home", font=f, weight=800, align="right")]
        E += [box("G%d state bg" % i, x, y + TH - 74, TW, 60, None, A("fade", 240, d + 140), show=p + ".home", bg=S["dark"]),
              box("G%d live" % i, x + 18, y + TH - 52, 14, 14, "#E5483B", A("pop", 240, d + 200, loop={"type": "pulse", "dur": 900, "amount": 0.3}),
                  show=both(p + ".home", p + ".live"), radius=7),
              txt("G%d state" % i, x + 40, y + TH - 74, TW - 60, 60, U(S, p + ".state"), 30, A("fade", 240, d + 200, change="flash"), show=p + ".home",
                  font=f, weight=800, align="center")]
    return {"name": "Around the League", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}



# ================================================================ PRESET LAYOUTS (Custom panel > Presets)
# Each layout is a starting point; every preset made from it becomes its own take button (p_<id>) whose text,
# photo, logo, clock and list lines come from the preset (ctx.preset). Layout graphics themselves are hidden
# from the take grid ("layout": True) and can be restyled in the editor like any graphic.
def _lay(name, group, E, autoHide=0, **kw):
    d = {"name": "Layout: " + name, "group": group, "autoHide": autoHide, "side": "", "sided": False, "elements": E, "layout": True}
    d.update(kw)
    return d


def _sponsor_corner(S, x, y, w, h, delay=500):
    return [box("Sponsor tile", x, y, w, h, "#FFFFFF", A("wipe-left", 340, delay), show="sponsor.on"),
            img("Sponsor logo", x + 12, y + 10, w - 24, h - 20, "{sponsor.logo}", A("fade", 300, delay + 200, change="fade"), show="sponsor.on && sponsor.logo"),
            txt("Sponsor name", x + 8, y, w - 16, h, "{sponsor.name}", 30, A("fade", 300, delay + 200, change="fade"), show="sponsor.on && !sponsor.logo",
                font=S["font"], weight=800, color="#121620", align="center", wrap=True, fit=False)]


def lay_title(S):
    f = S["font"]
    X, Y, W, H = 260, 200, 1400, 640
    E = [card(S, "Card", X, Y, W, H),
         img("Photo", X, Y, 560, H, "{preset.photo}", A("slide-right", 460, 300, dist=40), show="preset.photo", fit="cover", focus="center top"),
         img("Logo", X + W - 260, Y + 30, 220, 140, "{preset.logo}", A("pop", 400, 400), show="preset.logo"),
         txt("Kicker", X + 600, Y + 150, W - 640, 50, U(S, "preset.kicker"), 34, A("fade", 300, 400), show="preset.kicker", font=f, weight=800, color="$accent",
             tracking=2),
         txt("Title", X + 600, Y + 200, W - 640, 200, U(S, "preset.title"), 88, A("reveal-up", 420, 480), font=f, weight=800, wrap=True, fit=False, lineH=0.95,
             valign="top"),
         box("Rule", X + 600, Y + 420, 300, 8, "$accent", A("grow-x", 300, 700)),
         txt("Sub", X + 600, Y + 444, W - 640, 160, "{preset.sub}", 40, A("fade", 320, 800), show="preset.sub", font=f, weight=700, wrap=True, fit=False,
             valign="top", color="$dim")]
    # without a photo the text spans the card
    for e in E:
        if e["name"] in ("Kicker", "Title", "Rule", "Sub"):
            e2 = dict(e, id=nid("t"), name=e["name"] + " (no photo)", x=X + 60, w=(W - 120) if e["name"] != "Rule" else 300, showIf=both("!preset.photo", e.get("showIf")))
            e["showIf"] = both("preset.photo", e.get("showIf"))
            E.append(e2)
    E += _sponsor_corner(S, X + W - 300, Y + H - 120, 280, 100, 700)
    return _lay("Title Card", "full", E)


def lay_list(S):
    f = S["font"]
    X, Y, W = 360, 120, 1200
    RH = 88
    E = list_frame(S, X, Y, W, 96 + 42 + 8 * RH + 16, U(S, "preset.title"), U(S, "preset.sub"), None, ("\u25B6 " + U(S, "preset.foot"), "preset.foot"))
    E += [img("Logo", X - 300, Y + 200, 260, 260, "{preset.logo}", A("fade", 500, 300), show="preset.logo")]
    for i in range(8):
        p = "preset.rows.%d" % i
        y = Y + 146 + i * RH
        d = 500 + i * 80
        E += [box("Row %d" % i, X + 16, y + 4, W - 32, RH - 8, None, A("wipe-right", 300, d), show=p + ".a", bg=S["panel2"]),
              txt("Row %d a" % i, X + 40, y, W - 380, RH, U(S, p + ".a"), 40, A("fade", 260, d + 100), show=p + ".a", font=f, weight=800),
              txt("Row %d b" % i, X + W - 340, y, 300, RH, U(S, p + ".b"), 40, A("reveal-up", 280, d + 140), show=p + ".b", font=f, weight=800, align="right",
                  color="$accent")]
    return _lay("List", "full", E)


def lay_two(S):
    f = S["font"]
    X, Y, W = 460, 130, 1200
    RH = 92
    E = list_frame(S, X, Y, W, 96 + 50 + 6 * RH + 20, U(S, "preset.title"), U(S, "preset.sub"), None, ("\u25B6 " + U(S, "preset.foot"), "preset.foot"))
    E += [img("Photo", X - 420, Y + 150, 420, 560, "{preset.photo}", A("slide-right", 420, 300, dist=40), show="preset.photo", fit="contain", focus="center bottom"),
          img("Logo", X - 400, Y + 200, 380, 380, "{preset.logo}", A("fade", 500, 300), show="preset.logo && !preset.photo"),
          txt("Col1", X + W - 380, Y + 138, 180, 44, U(S, "preset.col1"), 26, A("fade", 260, 420), font=f, weight=800, align="center", color="$accent"),
          txt("Col2", X + W - 190, Y + 138, 180, 44, U(S, "preset.col2"), 26, A("fade", 260, 440), font=f, weight=800, align="center", color="$accent")]
    for i in range(6):
        p = "preset.rows.%d" % i
        y = Y + 186 + i * RH
        d = 520 + i * 80
        E += [box("Row %d" % i, X + 16, y + 4, W - 32, RH - 8, None, A("wipe-right", 300, d), show=p + ".a", bg=S["panel2"]),
              txt("Row %d label" % i, X + 40, y, W - 460, RH, U(S, p + ".a"), 38, A("fade", 260, d + 100), show=p + ".a", font=f, weight=800),
              box("Row %d b bg" % i, X + W - 380, y + 8, 176, RH - 16, None, A("fade", 240, d + 60), show=p + ".a", bg=S["val"]),
              txt("Row %d b" % i, X + W - 380, y, 176, RH, "{%s.b}" % p, 40, A("reveal-up", 280, d + 140), show=p + ".a", font=f, weight=800, align="center",
                  color=S["valText"]),
              box("Row %d c bg" % i, X + W - 194, y + 8, 176, RH - 16, None, A("fade", 240, d + 60), show=p + ".c", bg=S["val"]),
              txt("Row %d c" % i, X + W - 194, y, 176, RH, "{%s.c}" % p, 40, A("reveal-up", 280, d + 160), show=p + ".c", font=f, weight=800, align="center",
                  color=S["valText"])]
    return _lay("Two-Column Stats", "full", E)


def lay_photo(S):
    """Photo + text (social wall, feature): big photo on the left, kicker / title / lines on the right."""
    f = S["font"]
    X, Y, W, H = 180, 150, 1560, 760
    E = [card(S, "Card", X, Y, W, H),
         box("Photo frame", X + 30, Y + 30, 820, H - 60, "#000000@0.3", A("fade", 400, 200)),
         img("Photo", X + 30, Y + 30, 820, H - 60, "{preset.photo}", A("zoom-out", 520, 300), show="preset.photo", fit="cover"),
         img("Logo", X + W - 250, Y + 40, 210, 120, "{preset.logo}", A("pop", 400, 400), show="preset.logo"),
         txt("Kicker", X + 890, Y + 170, W - 930, 60, "{preset.kicker}", 44, A("fade", 300, 400), show="preset.kicker", font=f, weight=800, color="$accent"),
         txt("Title", X + 890, Y + 230, W - 930, 150, U(S, "preset.title"), 64, A("reveal-up", 400, 480), font=f, weight=800, wrap=True, fit=False,
             valign="top", lineH=0.98),
         txt("Sub", X + 890, Y + 390, W - 930, 300, "{preset.sub}", 36, A("fade", 320, 700), show="preset.sub", font=f, weight=600, wrap=True, fit=False,
             valign="top", lineH=1.2)]
    E += _sponsor_corner(S, X + W - 300, Y + H - 120, 280, 100, 800)
    return _lay("Photo + Text", "full", E)


def lay_quote(S):
    f = S["font"]
    X, Y, W, H = 220, 200, 1480, 640
    E = [card(S, "Card", X, Y, W, H),
         img("Photo", X + 30, Y + 60, 420, 520, "{preset.photo}", A("slide-right", 420, 300, dist=40), show="preset.photo", fit="cover", focus="center top"),
         txt("Mark", X + 480, Y + 20, 160, 180, "\u201C", 240, A("pop", 400, 400), font=f, weight=900, color="$accent"),
         txt("Quote", X + 500, Y + 150, W - 560, 320, "{preset.sub}", 46, A("fade", 400, 520), font=f, weight=700, wrap=True, fit=False, valign="top",
             lineH=1.2, italic=True),
         box("Rule", X + 500, Y + 490, 260, 6, "$accent", A("grow-x", 300, 800)),
         txt("Name", X + 500, Y + 506, W - 560, 60, U(S, "preset.title"), 44, A("reveal-up", 340, 860), font=f, weight=800),
         txt("Role", X + 500, Y + 566, W - 560, 44, U(S, "preset.kicker"), 28, A("fade", 260, 920), show="preset.kicker", font=f, weight=700, color="$dim")]
    return _lay("Quote", "full", E)


def lay_countdown(S):
    """Full-screen clock: counts down to a time, down a duration (Back in 2:00), or up from when it is taken (rain delay)."""
    f = S["font"]
    E = [box("Background", 0, 0, 1920, 1080, None, A("fade", 400, 0), bg="radial-gradient(ellipse at 50% 40%, color-mix(in srgb, {brand.color} 80%, #fff), {brand.color} 70%)"),
         img("Photo", 0, 0, 1920, 1080, "{preset.photo}", A("fade", 500, 0), show="preset.photo", fit="cover", opacity=0.35),
         img("Broadcaster", 810, 110, 300, 160, "{brand.logo}", A("pop", 420, 200), show="brand.logo"),
         txt("Title", 160, 300, 1600, 110, U(S, "preset.title"), 90, A("reveal-up", 400, 300), font=f, weight=800, align="center"),
         el("clock", "Clock", 360, 420, 1200, 280, A("pop", 420, 450), mode="{preset.mode}", target="{preset.time}", since="{preset.since}", dur="{preset.dur}",
            done="{preset.done}", style={"color": "$text", "size": 240, "weight": 800, "align": "center", "font": f, "textShadow": "0 10px 40px rgba(0,0,0,.4)"}),
         box("Rule", 760, 710, 400, 8, "{brand.color2}", A("grow-x", 300, 600)),
         txt("Sub", 160, 730, 1600, 80, U(S, "preset.sub"), 48, A("fade", 300, 700), show="preset.sub", font=f, weight=700, align="center", color="$dim")]
    E += _sponsor_corner(S, 1560, 900, 320, 130, 800)
    return _lay("Countdown / Clock", "full", E, sponsorSlot="show")


def lay_clockbug(S):
    f = S["font"]
    X, Y = 1500, 40
    E = [box("Bug", X, Y, 380, 120, None, A("wipe-left", 380, 0), bg=S["panel"], radius=S["radius"], shadow=True, borderW=1, borderColor="#FFFFFF@0.25"),
         txt("Title", X + 20, Y + 4, 340, 40, U(S, "preset.title"), 26, A("fade", 260, 200), font=f, weight=800, color="$accent", align="center"),
         el("clock", "Clock", X + 20, Y + 40, 340, 76, A("fade", 260, 260), mode="{preset.mode}", target="{preset.time}", since="{preset.since}", dur="{preset.dur}",
            done="{preset.done}", style={"color": "$text", "size": 64, "weight": 800, "align": "center", "font": f})]
    return _lay("Clock Bug", "bug2", E)


def lay_carousel(S):
    f = S["font"]
    X, Y, W, H = 240, 110, 1440, 810
    E = [box("Frame", X - 12, Y - 12, W + 24, H + 24 + 80, None, A("zoom-out", 480, 0), bg=S["panel"], radius=S["cardRadius"], shadow=S["shadow"]),
         el("carousel", "Carousel", X, Y + 80, W, H, A("fade", 500, 300), bind="preset.items", interval="{preset.interval}",
            style={"fit": "cover", "capSize": 44, "capFill": "#000000@0.6", "font": f, "radius": 4}),
         txt("Title", X + 20, Y - 6, W - 360, 86, U(S, "preset.title"), 56, A("reveal-up", 380, 300), font=f, weight=800),
         img("Broadcaster", X + W - 200, Y, 190, 70, "{brand.logo}", A("fade", 300, 400), show="brand.logo && !sponsor.on")]
    E += _sponsor_corner(S, X + W - 320, Y - 6, 320, 82, 400)
    return _lay("Promo Carousel", "full", E, sponsorSlot="show")


def lay_lower(S):
    """Lower third: photo or logo, title + sub. With list lines, shows the current line (Next button) instead: name | detail."""
    f = S["font"]
    X, Y = 160, 860
    E = [box("Bar", X + 150, Y, 1150, 80, None, A("wipe-right", 400, 100), bg=S["panel"], shadow=True),
         box("Tile", X, Y - 30, 150, 150, None, A("pop", 380, 0), show="preset.photo || preset.logo || brand.logo", bg=S["strip"], radius=S["radius"]),
         img("Photo", X, Y - 30, 150, 150, "{preset.photo}", A("fade", 300, 200), show="preset.photo", fit="cover", focus="center top"),
         img("Logo", X + 10, Y - 20, 130, 130, "{preset.logo}", A("fade", 300, 200), show="preset.logo && !preset.photo"),
         img("Broadcaster", X + 10, Y - 20, 130, 130, "{brand.logo}", A("fade", 300, 200), show="!preset.logo && !preset.photo && brand.logo"),
         txt("Title", X + 180, Y, 1100, 80, U(S, "preset.title"), 52, A("reveal-up", 360, 300), show="!preset.count", font=f, weight=800),
         txt("Current", X + 180, Y, 1100, 80, U(S, "preset.current.a"), 52, A("reveal-up", 360, 300, change="roll"), show="preset.count", font=f, weight=800),
         box("Sub bar", X + 150, Y + 80, 1000, 50, None, A("wipe-right", 340, 260), show="preset.sub || preset.current.b", bg=S["strip"]),
         txt("Sub", X + 180, Y + 80, 960, 50, U(S, "preset.sub"), 30, A("fade", 260, 420), show="preset.sub && !preset.count", font=f, weight=800,
             color=S["stripText"]),
         txt("Current b", X + 180, Y + 80, 960, 50, U(S, "preset.current.b"), 30, A("fade", 260, 420, change="fade"), show="preset.count && preset.current.b",
             font=f, weight=800, color=S["stripText"])]
    E += sponsor_tab(X + 1310, Y, 260, 80, 520, radius=S["radius"], a_type="wipe-right", label_w=100)
    return _lay("Lower Third", "lower", E, autoHide=0)


def lay_anthem(S):
    """Anthem lower third: a waving American flag beside the singer's name and photo."""
    f = S["font"]
    X, Y = 140, 840
    E = [el("flag", "Flag", X, Y - 40, 300, 176, A("wipe-right", 600, 0), src="/art/us-flag.svg",
            style={"amp": 0.06, "speed": 0.9, "waves": 1.5, "shade": 0.24}),
         box("Bar", X + 310, Y, 1000, 84, None, A("wipe-right", 420, 200), bg=S["panel"], shadow=True),
         box("Stripe", X + 310, Y + 84, 1000, 6, "#B22234", A("grow-x", 360, 360)),
         box("Sub bar", X + 310, Y + 90, 820, 48, None, A("wipe-right", 360, 320), show="preset.sub", bg=S["strip"]),
         txt("Title", X + 340, Y, 940, 84, U(S, "preset.title"), 54, A("reveal-up", 380, 400), font=f, weight=800),
         txt("Sub", X + 340, Y + 90, 780, 48, U(S, "preset.sub"), 30, A("fade", 280, 520), show="preset.sub", font=f, weight=800, color=S["stripText"],
             tracking=1),
         img("Photo", X + 1310 - 150, Y - 66, 150, 150, "{preset.photo}", A("slide-up", 380, 440, dist=20), show="preset.photo", fit="cover",
             focus="center top", radius=S["radius"])]
    E += sponsor_tab(X + 1320, Y, 260, 84, 600, radius=S["radius"], a_type="wipe-right", label_w=100)
    return _lay("Anthem (Flag)", "lower", E)


def lay_bug(S):
    f = S["font"]
    X, Y = 1400, 190
    E = [box("Bug", X, Y, 480, 70, None, A("wipe-left", 360, 0), bg=S["panel"], shadow=True, borderW=2, borderColor="$accent"),
         box("Dot", X + 22, Y + 27, 16, 16, "$accent", A("pop", 240, 200, loop={"type": "pulse", "dur": 900, "amount": 0.3}), radius=8),
         txt("Title", X + 52, Y, 410, 70, U(S, "preset.title"), 36, A("fade", 260, 200), font=f, weight=800),
         txt("Sub", X, Y + 70, 480, 40, U(S, "preset.sub"), 24, A("wipe-down", 260, 300), show="preset.sub", font=f, weight=700, align="center",
             fill="#000000@0.6")]
    return _lay("Status Bug", "bug2", E)


def lay_keys(S):
    """Keys to the game: both teams side by side, one key per line "away key | home key"."""
    f = S["font"]
    X, Y, W = 180, 110, 1560
    CW = W // 2
    E = list_frame(S, X, Y, W, 96 + 42 + 140 + 4 * 130, U(S, "preset.title"), U(S, "preset.sub"), None)
    for j, side in enumerate(("away", "home")):
        cx = X + j * CW
        E += [box("%s head" % side, cx + 10, Y + 146, CW - 20, 120, None, A("wipe-right", 340, 400 + j * 120), bg=TG(S, side))]
        E += logo_or_abbr("%s logo" % side, cx + 24, Y + 156, 120, 100, side, 40, A("pop", 320, 500 + j * 120), S=S)
        E += [txt("%s name" % side, cx + 160, Y + 146, CW - 190, 120, U(S, "%s.name" % side), 46, A("fade", 260, 560 + j * 120), font=f, weight=800,
                  textShadow=True)]
        for i in range(4):
            p = "preset.rows.%d" % i
            k = p + (".a" if j == 0 else ".b")
            y = Y + 284 + i * 130
            d = 700 + i * 150 + j * 80
            E += [box("%s key %d n" % (side, i), cx + 24, y + 24, 70, 70, "$accent", A("pop", 280, d), show=k, radius=35),
                  txt("%s key %d nt" % (side, i), cx + 24, y + 24, 70, 70, str(i + 1), 40, A("pop", 280, d), show=k, font=f, weight=800, align="center",
                      color=S["hiText"]),
                  txt("%s key %d" % (side, i), cx + 110, y, CW - 140, 118, U(S, k), 38, A("fade", 300, d + 80), show=k, font=f, weight=800, wrap=True,
                      fit=False, lineH=1.05)]
    return _lay("Keys to the Game", "full", E)


def lay_trivia(S):
    """Trivia: the question; tick Reveal on the preset (or take the answer button) to show the answer."""
    f = S["font"]
    X, Y, W, H = 260, 200, 1400, 640
    E = [card(S, "Card", X, Y, W, H),
         box("Head", X, Y, W, 110, None, A("wipe-right", 380, 200), bg=S["dark"]),
         txt("Title", X + 30, Y, W - 360, 110, U(S, "preset.title"), 64, A("reveal-up", 360, 300), font=f, weight=800),
         txt("Question", X + 60, Y + 140, W - 120, 260, "{preset.sub}", 54, A("fade", 400, 500), font=f, weight=800, wrap=True, fit=False, valign="top",
             lineH=1.15),
         box("Answer bar", X + 40, Y + 440, W - 80, 160, None, A("wipe-right", 380, 0, change="fade"), show="preset.reveal", bg=S["strip"]),
         txt("Answer label", X + 70, Y + 450, 400, 40, L(S, "Answer"), 26, A("fade", 260, 200), show="preset.reveal", font=f, weight=800, color="$accent"),
         txt("Answer", X + 70, Y + 486, W - 140, 104, U(S, "preset.foot"), 52, A("reveal-up", 360, 260), show="preset.reveal", font=f, weight=800,
             color=S["stripText"])]
    E += _sponsor_corner(S, X + W - 300, Y + 6, 290, 98, 500)
    return _lay("Trivia", "full", E, sponsorSlot="show")


def lay_next(S):
    """Next game: opponent logo, date and time, probables (rows: away | home), and a QR code for tickets."""
    f = S["font"]
    X, Y, W, H = 200, 140, 1520, 760
    E = [card(S, "Card", X, Y, W, H),
         box("Head", X, Y, W, 110, None, A("wipe-right", 380, 200), bg=S["dark"]),
         txt("Title", X + 30, Y, W - 60, 110, U(S, "preset.title"), 64, A("reveal-up", 360, 300), font=f, weight=800, align="center"),
         img("Home logo", X + 120, Y + 160, 300, 260, "{home.logo}", A("pop", 400, 400), show="home.logo"),
         txt("Vs", X + 430, Y + 160, 160, 260, L(S, "vs"), 60, A("fade", 300, 500), font=f, weight=800, align="center"),
         img("Opponent logo", X + 600, Y + 160, 300, 260, "{preset.logo}", A("pop", 400, 560), show="preset.logo"),
         txt("When", X + 60, Y + 440, 880, 80, U(S, "preset.sub"), 52, A("fade", 300, 600), font=f, weight=800, align="center", color="$accent"),
         txt("Probables label", X + 60, Y + 530, 880, 44, L(S, "Probable starters"), 28, A("fade", 260, 700), show="preset.count", font=f, weight=700,
             align="center", color="$dim"),
         txt("Probable a", X + 60, Y + 574, 880, 54, U(S, "preset.rows.0.a"), 38, A("fade", 260, 760), show="preset.count", font=f, weight=800, align="center"),
         txt("Probable b", X + 60, Y + 628, 880, 54, U(S, "preset.rows.0.b"), 38, A("fade", 260, 800), show="preset.rows.0.b", font=f, weight=800,
             align="center"),
         box("QR bg", X + W - 460, Y + 150, 400, 400, "#FFFFFF", A("pop", 400, 600), show="preset.qr"),
         el("qr", "QR", X + W - 450, Y + 160, 380, 380, A("fade", 300, 700), show="preset.qr", text="{preset.qr}",
            style={"color": "#000000", "bg": "#FFFFFF", "quiet": 1, "ecc": "M"}),
         txt("QR text", X + W - 480, Y + 560, 440, 100, U(S, "preset.foot"), 34, A("fade", 300, 800), show="preset.qr", font=f, weight=800, align="center",
             wrap=True, fit=False)]
    return _lay("Next Game", "full", E, sponsorSlot="show")


def lay_open(S):
    """Segment open: the segment name big over the broadcaster colours, kicker above, sponsor below. Leaves on its own."""
    f = S["font"]
    outA = {"type": "fade", "dur": 400, "delay": 200, "ease": "in"}
    E = [box("Background", 0, 0, 1920, 1080, None, A("wipe-right", 520, 0, out=outA), bg="linear-gradient(135deg, {brand.color}, color-mix(in srgb, {brand.color} 60%, #000))"),
         box("Stripes", 0, 0, 1920, 1080, None, A("fade", 500, 200, out=outA), bg="repeating-linear-gradient(-60deg, transparent 0 26px, #FFFFFF10 26px 30px)"),
         img("Photo", 0, 0, 1920, 1080, "{preset.photo}", A("fade", 600, 200, out=outA), show="preset.photo", fit="cover", opacity=0.3),
         img("Broadcaster", 810, 150, 300, 160, "{brand.logo}", A("pop", 420, 300, out=outA), show="brand.logo"),
         txt("Kicker", 160, 330, 1600, 70, U(S, "preset.kicker"), 46, A("fade", 300, 400, out=outA), show="preset.kicker", font=f, weight=800, align="center",
             color="{brand.color2}", tracking=4),
         txt("Title", 60, 400, 1800, 240, U(S, "preset.title"), 190, A("letters", 520, 500, out=outA, stagger=30), font=f, weight=900, align="center",
             textShadow="0 10px 40px rgba(0,0,0,.4)"),
         box("Rule", 610, 650, 700, 8, "{brand.color2}", A("grow-x", 360, 800, out=outA)),
         txt("Sub", 160, 670, 1600, 70, U(S, "preset.sub"), 44, A("fade", 300, 900, out=outA), show="preset.sub", font=f, weight=700, align="center")]
    E += _sponsor_corner(S, 800, 820, 320, 130, 1000)
    return _lay("Segment Open", "full", E, autoHide=5, sponsorSlot="show")


def lay_video(S):
    """Video in a branded frame: an uploaded clip (highlight, sponsor spot) with a title bar."""
    f = S["font"]
    X, Y, W, H = 240, 150, 1440, 810
    E = [box("Frame", X - 14, Y - 90, W + 28, H + 104, None, A("zoom-out", 480, 0), bg=S["panel"], radius=S["cardRadius"], shadow=S["shadow"]),
         el("video", "Video", X, Y, W, H, A("fade", 400, 300), src="{preset.video}", loop=False, sound=True, style={"fit": "cover"}),
         txt("Title", X + 10, Y - 86, W - 360, 80, U(S, "preset.title"), 52, A("reveal-up", 360, 300), font=f, weight=800),
         img("Broadcaster", X + W - 200, Y - 82, 190, 70, "{brand.logo}", A("fade", 300, 400), show="brand.logo && !sponsor.on")]
    E += _sponsor_corner(S, X + W - 320, Y - 86, 320, 80, 400)
    return _lay("Video Frame", "full", E, sponsorSlot="show")


def layouts(S):
    return {"lay_title": lay_title(S), "lay_list": lay_list(S), "lay_two": lay_two(S), "lay_photo": lay_photo(S), "lay_quote": lay_quote(S),
            "lay_countdown": lay_countdown(S), "lay_clockbug": lay_clockbug(S), "lay_carousel": lay_carousel(S), "lay_lower": lay_lower(S), "lay_anthem": lay_anthem(S),
            "lay_bug": lay_bug(S), "lay_keys": lay_keys(S), "lay_trivia": lay_trivia(S), "lay_next": lay_next(S), "lay_open": lay_open(S),
            "lay_video": lay_video(S)}


# ================================================================ AUTOMATIC GAME GRAPHICS
def pitch_tracker(S):
    """Pitch count box: pitcher, pitches, strikes - balls, strike %, last pitch speed (feed or Notes > Pitch speed)."""
    f = S["font"]
    X, Y, W = 40, 640, 380
    E = [box("Box", X, Y, W, 300, None, A("wipe-right", 380, 0), bg=S["panel"], shadow=True, radius=S["radius"]),
         box("Head", X, Y, W, 56, None, A("wipe-right", 320, 100), bg=S["dark"], radius=S["radius"]),
         txt("Head t", X + 16, Y, W - 32, 56, L(S, "Pitch Count"), 28, A("fade", 240, 200), font=f, weight=800, color="$accent")]
    E += logo_or_abbr("Logo", X + W - 70, Y + 6, 56, 44, "fielding", 20, A("fade", 240, 220), S=S)
    E += [txt("Name", X + 16, Y + 60, W - 32, 50, U(S, "pitcher.name"), 34, A("fade", 260, 300), font=f, weight=800),
          txt("PC", X + 16, Y + 110, 160, 110, "{pitcher.today.pc|zero}", 96, A("reveal-up", 300, 360, change="pop"), font=f, weight=800),
          txt("PC label", X + 16, Y + 214, 160, 30, L(S, "Pitches"), 22, A("fade", 240, 400), font=f, weight=700, color="$dim"),
          txt("SB", X + 190, Y + 118, W - 206, 44, "{pitcher.today.st|zero} " + L(S, "St") + " - {pitcher.today.bl|zero} " + L(S, "B"), 30,
              A("fade", 240, 420, change="flash"), font=f, weight=800, align="right"),
          txt("Pct", X + 190, Y + 162, W - 206, 44, "{pitcher.today.stPct} " + L(S, "Strikes"), 28, A("fade", 240, 440, change="flash"),
              show="pitcher.today.stPct", font=f, weight=700, align="right", color="$dim"),
          box("Velo bar", X, Y + 250, W, 50, None, A("wipe-up", 280, 500), show="velo.ps", bg=S["strip"], radius=S["radius"]),
          txt("Velo", X + 16, Y + 250, W - 32, 50, L(S, "Last pitch") + " {velo.ps} MPH", 28, A("fade", 240, 600, change="flash"), show="velo.ps", font=f,
              weight=800, color=S["stripText"], align="center")]
    return {"name": "Pitch Count", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E}


def bvp_card(S):
    """Batter vs pitcher: both headshots and names, the career matchup (Notes > Batter vs pitcher) and tonight's results."""
    f = S["font"]
    X, Y, W = 330, 800, 1260
    E = [box("Bar", X, Y, W, 200, None, A("wipe-right", 420, 0), bg=S["panel"], shadow=True),
         box("Batter tile", X, Y, 180, 200, None, A("fade", 300, 100), bg=TG(S, "batting")),
         img("Batter", X, Y, 180, 200, "{batter.photo}", A("slide-up", 380, 200, dist=20), show="batter.photo", fit="cover", focus="center top"),
         box("Pitcher tile", X + W - 180, Y, 180, 200, None, A("fade", 300, 100), bg=TG(S, "fielding")),
         img("Pitcher", X + W - 180, Y, 180, 200, "{pitcher.photo}", A("slide-up", 380, 260, dist=20), show="pitcher.photo", fit="cover", focus="center top"),
         txt("Batter name", X + 200, Y + 10, 400, 50, U(S, "batter.name"), 36, A("fade", 260, 300), font=f, weight=800),
         txt("Vs", X + 600, Y + 10, 60, 50, L(S, "vs"), 30, A("fade", 260, 320), font=f, weight=800, align="center", color="$accent"),
         txt("Pitcher name", X + 660, Y + 10, 400, 50, U(S, "pitcher.name"), 36, A("fade", 260, 340), font=f, weight=800, align="right"),
         box("Line bar", X + 180, Y + 66, W - 360, 70, None, A("wipe-right", 340, 360), bg=S["strip"]),
         txt("Career", X + 200, Y + 66, W - 400, 70, U(S, "notes.bvp"), 40, A("reveal-up", 320, 480), show="notes.bvp", font=f, weight=800, align="center",
             color=S["stripText"]),
         txt("Career none", X + 200, Y + 66, W - 400, 70, L(S, "First career meeting"), 36, A("reveal-up", 320, 480), show="!notes.bvp", font=f, weight=800,
             align="center", color=S["stripText"]),
         txt("Tonight", X + 200, Y + 140, W - 400, 54, L(S, "Tonight: ") + "{batter.forText|upper}  {batter.playsText|upper}", 30, A("fade", 260, 600),
             show="batter.forText", font=f, weight=800, align="center")]
    return {"name": "Batter vs Pitcher", "group": "lower", "autoHide": 9, "side": "", "sided": False, "elements": E}


def scoring_summary(S):
    f = S["font"]
    X, Y, W = 260, 110, 1400
    RH = 100
    E = list_frame(S, X, Y, W, 96 + 42 + 8 * RH + 12, L(S, "Scoring Summary"), L(S, "{away.name|upper} at {home.name|upper}"), None)
    for i in range(8):
        p = "scoring.%d" % i
        y = Y + 142 + i * RH
        d = 500 + i * 90
        E += [box("Row %d" % i, X + 12, y + 4, W - 24, RH - 8, None, A("wipe-right", 300, d), show=p + ".text", bg=S["panel2"]),
              txt("Row %d inn" % i, X + 24, y, 130, RH, "{%s.label}" % p, 26, A("fade", 240, d + 80), show=p + ".text", font=f, weight=800, color="$accent"),
              img("Row %d logo" % i, X + 156, y + 14, 70, RH - 28, "{%s.logo}" % p, A("fade", 240, d + 100), show=both(p + ".text", p + ".logo")),
              txt("Row %d text" % i, X + 240, y + 4, W - 560, RH - 8, "{%s.text}" % p, 26, A("fade", 260, d + 120), show=p + ".text", font=f, weight=700,
                  wrap=True, fit=False, lineH=1.1),
              txt("Row %d score" % i, X + W - 310, y, 290, RH, "{%s.score}" % p, 30, A("reveal-up", 280, d + 160), show=p + ".text", font=f, weight=800,
                  align="right")]
    E += [txt("None", X, Y + 300, W, 100, L(S, "No scoring yet"), 50, A("fade", 300, 500), show="!hasScoring", font=f, weight=800, align="center", color="$dim")]
    return {"name": "Scoring Summary", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def inning_recap(S):
    """End-of-half recap (runs, hits, errors); comes up by itself when a half-inning ends (Graphics > AUTO)."""
    f = S["font"]
    X, Y = 560, 900
    E = [box("Bar", X, Y, 800, 90, None, A("wipe-right", 380, 0), bg=S["panel"], shadow=True),
         box("Tile", X, Y, 120, 90, None, A("pop", 320, 100), bg=TG(S, "halfRecap"))]
    E += logo_or_abbr("Logo", X + 10, Y + 8, 100, 74, "halfRecap", 30, A("pop", 320, 200), S=S)
    E += [txt("Label", X + 140, Y, 300, 90, L(S, "End of ") + "{halfRecap.label}", 30, A("fade", 260, 260), font=f, weight=800, color="$accent"),
          txt("Line", X + 430, Y, 350, 90, "{halfRecap.line}", 44, A("reveal-up", 300, 320), font=f, weight=800, align="right")]
    E += sponsor_tab(X, Y - 50, 800, 44, 520, radius=S["radius"], a_type="wipe-up")
    return {"name": "Inning Recap", "group": "lower", "autoHide": 7, "side": "", "sided": False, "elements": E, "trigger": "INNING", "triggerDelay": 2,
            "sponsorSlot": "half_{halfKey}"}


def potg_card(S):
    """Player of the game: the leading team's top hitter (or the picked player), photo and tonight's line."""
    f = S["font"]
    X, Y, W, H = 260, 160, 1400, 720
    E = [card(S, "Card", X, Y, W, H),
         box("Photo bg", X, Y, 600, H, None, A("fade", 400, 200), bg=TG(S, "home")),
         img("Photo", X, Y, 600, H, "{potg.photo}", A("slide-right", 460, 300, dist=40), show="potg.photo", fit="cover", focus="center top"),
         txt("Kicker", X + 650, Y + 140, W - 700, 60, L(S, "Player of the Game"), 40, A("fade", 300, 400), font=f, weight=800, color="$accent", tracking=2),
         txt("Name", X + 650, Y + 200, W - 700, 200, U(S, "potg.name"), 96, A("reveal-up", 420, 500), font=f, weight=800, wrap=True, fit=False, valign="top",
             lineH=0.95),
         box("Rule", X + 650, Y + 420, 300, 8, "$accent", A("grow-x", 300, 700)),
         txt("Line", X + 650, Y + 440, W - 700, 160, U(S, "potg.line"), 48, A("fade", 320, 800), font=f, weight=800, wrap=True, fit=False, valign="top"),
         txt("Team", X + 650, Y + 610, W - 700, 50, U(S, "potg.teamName"), 30, A("fade", 260, 900), show="potg.teamName", font=f, weight=700, color="$dim")]
    E += _sponsor_corner(S, X + W - 300, Y + 20, 280, 100, 700)
    return {"name": "Player of the Game", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "feature"}


def box_final(S):
    """Final with both teams' batting: each lineup with tonight's line and results."""
    f = S["font"]
    X, Y, W = 80, 70, 1760
    CW = W // 2
    RH = 74
    E = [box("Head", X, Y, W, 110, None, A("wipe-right", 400, 0), bg=S["dark"], shadow=S["shadow"]),
         txt("Final", X, Y, W, 110, L(S, "Final"), 64, A("reveal-up", 360, 200), font=f, weight=800, align="center")]
    for j, side in enumerate(("away", "home")):
        cx = X + j * CW
        E += [box("%s band" % side, cx + (0 if j == 0 else 4), Y + 120, CW - 4, 100, None, A("wipe-right", 360, 300 + j * 100), bg=TG(S, side))]
        E += logo_or_abbr("%s logo" % side, cx + 16, Y + 128, 110, 84, side, 34, A("pop", 320, 420 + j * 100), S=S)
        E += [txt("%s name" % side, cx + 140, Y + 120, CW - 300, 100, U(S, "%s.name" % side), 44, A("fade", 260, 460 + j * 100), font=f, weight=800,
                  textShadow=True),
              txt("%s runs" % side, cx + CW - 150, Y + 120, 130, 100, "{%s.runs}" % side, 76, A("reveal-up", 300, 500 + j * 100), font=f, weight=800,
                  align="right", textShadow=True),
              box("%s body" % side, cx + (0 if j == 0 else 4), Y + 224, CW - 4, 9 * RH + 16, None, A("fade", 300, 400), bg=S["panel"])]
        for i in range(9):
            p = "%s.lineup.%d" % (side, i)
            y = Y + 232 + i * RH
            d = 600 + i * 60 + j * 40
            E += [box("%s row %d" % (side, i), cx + 12, y + RH - 2, CW - 28, 1, "#FFFFFF@0.18", A("grow-x", 260, d), show=p + ".name"),
                  txt("%s %d pos" % (side, i), cx + 14, y, 60, RH, "{%s.pos}" % p, 22, A("fade", 240, d), show=p + ".name", font=f, weight=700, color="$dim",
                      align="center"),
                  txt("%s %d name" % (side, i), cx + 80, y, 320, RH, U(S, p + ".last"), 32, A("fade", 240, d + 40), show=p + ".name", font=f, weight=800),
                  txt("%s %d hab" % (side, i), cx + 400, y, 100, RH, "{%s.hab}" % p, 32, A("fade", 240, d + 60), show=p + ".hab", font=f, weight=800,
                      align="center"),
                  txt("%s %d plays" % (side, i), cx + 510, y, CW - 530, RH, U(S, p + ".plays"), 22, A("fade", 240, d + 80), show=p + ".plays", font=f,
                      weight=700, color="$dim")]
    return {"name": "Final: Box Score", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def auto_game(S):
    return {"pitch_count": pitch_tracker(S), "bvp": bvp_card(S), "scoring_summary": scoring_summary(S), "inning_recap": inning_recap(S),
            "potg": potg_card(S), "box_final": box_final(S)}



# ================================================================ DATA-FEED GRAPHICS: splits, bio, extended standings, next game, game info
def splits_lower(S, kind):
    """Season splits lower third: vs left / vs right, home / road, with runners in scoring position."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y, W = 300, 860, 1320
    cols = ([("vs LHB", "vsL"), ("vs RHB", "vsR"), ("Home", "home"), ("Road", "away")] if kind == "pit" else
            [("vs LHP", "vsL"), ("vs RHP", "vsR"), ("RISP", "risp"), ("Home", "home"), ("Road", "away")])
    E = [box("Name bar", X, Y, W, 70, None, A("wipe-right", 400, 0), bg=TG(S, team)),
         txt("Name", X + 24, Y, 700, 70, U(S, "%s.name" % who), 44, A("reveal-up", 340, 200), font=f, weight=800, textShadow=True),
         txt("Head", X + 740, Y, W - 760, 70, L(S, "Season splits"), 28, A("fade", 260, 300), font=f, weight=700, align="right", color="$dim"),
         box("Body", X, Y + 70, W, 110, None, A("wipe-right", 380, 160), bg=S["panel"])]
    cw = W / float(len(cols))
    for i, (lab, key) in enumerate(cols):
        cx = int(X + i * cw)
        p = "%s.splits.%s" % (who, key)
        v = ("{%s.avg}" % p)
        sub = ("{%s.era} ERA" % p) if kind == "pit" else ("{%s.h}-{%s.ab}  {%s.hr} HR" % (p, p, p))
        E += [txt("%s label" % lab, cx, Y + 74, int(cw), 30, L(S, lab), 22, A("fade", 240, 400 + i * 60), font=f, weight=800, align="center", color="$accent"),
              txt("%s value" % lab, cx, Y + 100, int(cw), 50, v, 44, A("reveal-up", 300, 420 + i * 60), show=p + ".ab", font=f, weight=800, align="center"),
              txt("%s sub" % lab, cx, Y + 148, int(cw), 30, sub, 22, A("fade", 260, 460 + i * 60), show=p + ".ab", font=f, weight=700, align="center",
                  color="$dim"),
              txt("%s none" % lab, cx, Y + 100, int(cw), 50, "-", 44, A("fade", 300, 420 + i * 60), show="!" + p + ".ab", font=f, weight=800,
                  align="center", color="$dim")]
        if i:
            E.append(box("Div %d" % i, cx, Y + 84, 2, 86, "#FFFFFF@0.2", A("grow-y", 260, 400)))
    if kind == "pit":
        E[-1:] = E[-1:]
    E += sponsor_tab(X + W - 300, Y - 50, 300, 44, 600, radius=S["radius"], a_type="wipe-up")
    return {"name": ("Pitcher" if kind == "pit" else "Batter") + " Splits", "group": "lower", "autoHide": 10, "side": "", "sided": False, "elements": E,
            "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def bio_lower(S, kind):
    """Player bio lower third: number, position, name and height | weight | age | bats/throws | hometown (from the roster)."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y = 300, 880
    E = [box("Num", X, Y, 120, 130, None, A("pop", 360, 0), bg=TG(S, team)),
         txt("Number", X, Y + 6, 120, 76, "{%s.number}" % who, 60, A("fade", 260, 200), font=f, weight=800, align="center", textShadow=True),
         txt("Pos", X, Y + 82, 120, 40, U(S, "%s.pos" % who), 28, A("fade", 260, 220), font=f, weight=800, align="center"),
         box("Bar", X + 120, Y, 1180, 76, None, A("wipe-right", 400, 100), bg=S["panel"]),
         txt("Name", X + 150, Y, 1120, 76, U(S, "%s.name" % who), 50, A("reveal-up", 340, 260), font=f, weight=800),
         box("Bio bar", X + 120, Y + 76, 1180, 54, None, A("wipe-right", 360, 220), bg=S["strip"]),
         txt("Bio", X + 150, Y + 76, 1120, 54, U(S, "%s.bioLine" % who), 30, A("fade", 260, 400), show="%s.bioLine" % who, font=f, weight=800,
             color=S["stripText"])]
    E += sponsor_tab(X + 1310, Y, 260, 76, 520, radius=S["radius"], a_type="wipe-right", label_w=100)
    return {"name": ("Pitcher" if kind == "pit" else "Batter") + " Bio", "group": "lower", "autoHide": 8, "side": "", "sided": False, "elements": E,
            "pickable": True}


def standings_ext(S):
    """Extended standings: W, L, PCT, GB, last 10, streak, home, road and run differential for the chosen group (divisions or league)."""
    f = S["font"]
    X, Y, W = 160, 90, 1600
    RH = 70
    E = list_frame(S, X, Y, W, 96 + 42 + 50 + 10 * RH + 10, U(S, "standingsGroup.name"), L(S, "{seasonYear} Standings"), None)
    for e in E:
        if e["name"] == "Body":
            e["growWith"] = {"bind": "standingsGroup.teams", "base": 42 + 50 + 14, "per": RH, "max": 10}
    E += [img("League", X + 14, Y + 8, 140, 80, "{league.logo}", A("pop", 300, 300), show="league.logo")]
    cols = [("W", "w", 100), ("L", "l", 100), ("PCT", "pct", 130), ("GB", "gb", 110), ("L10", "last10", 120), ("STRK", "streak", 120),
            ("HOME", "home", 130), ("ROAD", "road", 130), ("DIFF", "diff", 120)]
    x0 = X + W - sum(c[2] for c in cols) - 20
    x = x0
    for lab, key, w in cols:
        E.append(txt("H %s" % lab, x, Y + 140, w, 46, lab, 24, A("fade", 240, 400), font=f, weight=800, align="center", color="$accent"))
        x += w
    for i in range(10):
        p = "standingsGroup.teams.%d" % i
        y = Y + 190 + i * RH
        d = 480 + i * 60
        E += [box("R%d bg" % i, X + 12, y + 3, W - 24, RH - 6, None, A("wipe-right", 300, d), show=p + ".name", bg=S["panel2"]),
              box("R%d hi" % i, X + 12, y + 3, 8, RH - 6, "$accent", A("grow-y", 260, d + 60), show=both(p + ".name", p + ".isGame")),
              txt("R%d rank" % i, X + 30, y, 50, RH, "{%s.rank}" % p, 30, A("fade", 240, d + 80), show=p + ".name", font=f, weight=800, color="$dim",
                  align="center"),
              img("R%d logo" % i, X + 90, y + 8, 70, RH - 16, "{%s.logo}" % p, A("fade", 240, d + 100), show=both(p + ".name", p + ".logo")),
              txt("R%d name" % i, X + 175, y, x0 - X - 185, RH, U(S, p + ".name"), 34, A("fade", 260, d + 100), show=p + ".name", font=f, weight=800)]
        x = x0
        for lab, key, w in cols:
            E.append(txt("R%d %s" % (i, lab), x, y, w, RH, "{%s.%s}" % (p, key), 30, A("fade", 240, d + 140), show=p + ".name", font=f, weight=800,
                         align="center"))
            x += w
    return {"name": "Standings: Extended", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


def next_game_auto(S):
    """Next game: opponent, home or away, date and time, ballpark."""
    f = S["font"]
    X, Y, W, H = 360, 220, 1200, 600
    E = [card(S, "Card", X, Y, W, H),
         box("Head", X, Y, W, 100, None, A("wipe-right", 380, 200), bg=S["dark"]),
         txt("Title", X, Y, W, 100, L(S, "Next Game"), 60, A("reveal-up", 360, 300), font=f, weight=800, align="center"),
         img("Our logo", X + 120, Y + 140, 300, 240, "{home.logo}", A("pop", 400, 400), show="home.logo && nextGame.opp"),
         txt("Vs", X + 430, Y + 140, 340, 240, "{nextGame.home|upper}", 2, A("fade", 1, 0), show="never"),
         txt("At", X + 430, Y + 140, 340, 240, L(S, "vs"), 64, A("fade", 300, 500), show="nextGame.opp && nextGame.home", font=f, weight=800, align="center"),
         txt("At away", X + 430, Y + 140, 340, 240, "@", 80, A("fade", 300, 500), show="nextGame.opp && !nextGame.home", font=f, weight=800, align="center"),
         img("Opp logo", X + 780, Y + 140, 300, 240, "{nextGame.logo}", A("pop", 400, 560), show="nextGame.logo"),
         txt("Opp abbr", X + 780, Y + 140, 300, 240, "{nextGame.abbr}", 100, A("pop", 400, 560), show="nextGame.opp && !nextGame.logo", font=f, weight=800, align="center"),
         txt("Opp", X + 40, Y + 400, W - 80, 64, U(S, "nextGame.line"), 48, A("fade", 300, 600), font=f, weight=800, align="center"),
         txt("When", X + 40, Y + 464, W - 80, 56, U(S, "nextGame.when"), 40, A("fade", 300, 700), font=f, weight=800, align="center", color="$accent"),
         txt("Venue", X + 40, Y + 520, W - 80, 50, U(S, "nextGame.venue"), 30, A("fade", 300, 800), show="nextGame.venue", font=f, weight=700,
             align="center", color="$dim"),
         txt("None", X + 40, Y + 300, W - 80, 80, L(S, "Schedule not loaded"), 40, A("fade", 300, 400), show="!nextGame.opp", font=f, weight=800,
             align="center", color="$dim")]
    E = [e for e in E if e["name"] != "Vs"]
    E += _sponsor_corner(S, X + W - 300, Y + 6, 290, 88, 500)
    return {"name": "Next Game (Schedule)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def game_info(S):
    """Game information: ballpark, weather, attendance, time of game, umpires and official scorer."""
    f = S["font"]
    X, Y, W = 360, 150, 1200
    rows = [("Ballpark", "{venue}", "venue"), ("Weather", "{weather.temp}  {weather.wind}", "weather.temp || weather.wind"),
            ("Attendance", "{attendance}", "attendance"), ("Time of game", "{duration}", "duration"),
            ("Home plate", "{umps.0.name}", "umps.0.name"), ("Umpires", "{umps.1.name}  {umps.2.name}  {umps.3.name}", "umps.1.name"),
            ("Official scorer", "{scorer}", "scorer")]
    RH = 92
    E = list_frame(S, X, Y, W, 96 + 42 + len(rows) * RH + 14, L(S, "Game Information"), L(S, "{away.name|upper} at {home.name|upper}"), None)
    for i, (lab, val, sh) in enumerate(rows):
        y = Y + 146 + i * RH
        d = 500 + i * 80
        E += [box("R%d" % i, X + 16, y + 4, W - 32, RH - 8, None, A("wipe-right", 300, d), show=sh, bg=S["panel2"]),
              txt("R%d label" % i, X + 40, y, 340, RH, L(S, lab), 32, A("fade", 260, d + 80), show=sh, font=f, weight=800, color="$accent"),
              txt("R%d value" % i, X + 380, y, W - 420, RH, val, 34, A("fade", 260, d + 120), show=sh, font=f, weight=800, align="right")]
    return {"name": "Game Information", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def extra_graphics(S):
    return {"batter_splits": splits_lower(S, "bat"), "pitcher_splits": splits_lower(S, "pit"), "batter_bio": bio_lower(S, "bat"),
            "pitcher_bio": bio_lower(S, "pit"), "standings_ext": standings_ext(S), "next_game_auto": next_game_auto(S), "game_info": game_info(S)}



# ================================================================ TRANSITION FAMILY
# Same DNA (team-colour field, three skewed accent bars sweeping across, brand mark, big word on a rule),
# different entry direction and backdrop pattern per moment, so they read as one package.
TRANSITIONS = [
    # id, word, sub (data or text), wipe in, wipe out, bar direction, pattern
    ("tr_lineup", "Lineup", "{team.name}", "wipe-right", "wipe-right", 1, "words"),
    ("tr_defense", "Defense", "{team.name}", "diamond", "diamond", 1, "diamonds"),
    ("tr_bullpen", "Bullpen", "Pitching change", "wipe-up", "wipe-up", -1, "columns"),
    ("tr_replay", "Replay", "", "wipe-left", "wipe-left", -1, "scan"),
    ("tr_final", "Final", "{away.abbr} {away.runs}  -  {home.runs} {home.abbr}", "wipe-center", "wipe-center", 1, "rays"),
    ("tr_pregame", "Pregame", "{show.name}", "wipe-up", "wipe-down", 1, "stripes"),
    ("tr_postgame", "Postgame", "{show.name}", "wipe-down", "wipe-up", -1, "stripes"),
    ("tr_bp", "Batting Practice", "{show.name}", "wipe-right", "wipe-left", 1, "words"),
]
TR_OUT_AT = 1500   # every layer starts leaving at the same moment


def _tr_anim(t, dur, delay, out_t=None, dist=None):
    a = A(t, dur, delay, ease="in-out" if t.startswith("wipe") or t == "diamond" else "out", dist=dist,
          out={"type": out_t or t, "dur": 380, "delay": 0, "ease": "in-out"})
    a["hold"] = max(0, TR_OUT_AT - delay - dur)
    return a


def transition(S, tid, word, sub, win, wout, bar_dir, pattern):
    f = S["font"]
    team = "team"   # AWAY / HOME / NETWORK buttons on the tile (NETWORK = broadcaster colours and logo)
    default_side = "batting" if tid in ("tr_lineup",) else ("fielding" if tid in ("tr_defense", "tr_bullpen") else "network")
    E = [box("Field", 0, 0, 1920, 1080, None, _tr_anim(win, 460, 0, wout),
             bg="linear-gradient(135deg, color-mix(in srgb, {%s.color} 85%%, #fff) 0%%, {%s.color} 45%%, color-mix(in srgb, {%s.color} 55%%, #000) 100%%)"
                % (team, team, team))]
    # backdrop pattern (the part that changes per moment)
    if pattern == "words":
        for r in range(4):
            E.append({"id": nid("t"), "name": "Pattern word %d" % r, "type": "text", "x": -300, "y": -60 + r * 300, "w": 2520, "h": 300,
                      "text": "  ".join([word.upper()] * 4),
                      "style": {"color": "#FFFFFF@0.07", "size": 260, "weight": 900, "align": "left", "valign": "center", "padX": 0, "fit": False, "font": f,
                                "tracking": -4},
                      "anim": _tr_anim("slide-left" if r % 2 else "slide-right", 900, 60, "fade", dist=300)})
    elif pattern == "diamonds":
        for k, sz in enumerate((1400, 1000, 640)):
            E.append(box("Pattern diamond %d" % k, 960 - sz // 2, 540 - sz // 2, sz, sz, None, _tr_anim("scale", 600, 80 + k * 70, "fade"), rotate=45,
                         borderW=4, borderColor="#FFFFFF@0.16"))
    elif pattern == "columns":
        E.append(box("Pattern columns", 0, 0, 1920, 1080, None, _tr_anim("wipe-up", 600, 80, "fade"),
                     bg="repeating-linear-gradient(90deg, #FFFFFF14 0 6px, transparent 6px 120px)"))
    elif pattern == "scan":
        E.append(box("Pattern scan", 0, 0, 1920, 1080, None, _tr_anim("fade", 300, 60, "fade"),
                     bg="repeating-linear-gradient(0deg, #00000026 0 3px, transparent 3px 7px)"))
    elif pattern == "rays":
        E.append(box("Pattern rays", 0, 0, 1920, 1080, None, _tr_anim("scale", 700, 60, "fade"),
                     bg="repeating-conic-gradient(from 0deg at 50% 50%, #FFFFFF12 0deg 6deg, transparent 6deg 12deg)"))
    else:
        E.append(box("Pattern stripes", 0, 0, 1920, 1080, None, _tr_anim("fade", 400, 60, "fade"),
                     bg="repeating-linear-gradient(-60deg, transparent 0 26px, #FFFFFF12 26px 30px)"))
    # three skewed accent bars sweeping across (shared signature)
    cols = ["{%s.color2}" % team, "#FFFFFF", "color-mix(in srgb, {%s.color2} 55%%, #fff)" % team]
    for k in range(3):
        y = (170, 800, 900)[k]
        E.append(box("Bar %d" % (k + 1), -200, y, 2320, 70 - k * 18, cols[k], _tr_anim("wipe-right" if bar_dir > 0 else "wipe-left", 420, 80 + k * 70),
                     rotate=-8, opacity=0.85 - k * 0.2))
    # brand mark, word, rule, sub
    E += [img("Brand", 860, 120, 200, 120, "{team.logo}", _tr_anim("pop", 420, 260, "fade"), show="team.logo", shadow=True),
          box("Word plate", 0, 400, 1920, 260, "#000000@0.28", _tr_anim("wipe-right" if bar_dir > 0 else "wipe-left", 380, 200)),
          txt("Word", 60, 400, 1800, 230, word.upper(), 200, _tr_anim("letters", 460, 300, "fade"), font=f, weight=900,
              align="center", tracking=-2, textShadow="0 8px 30px rgba(0,0,0,.4)"),
          box("Rule", 560, 660, 800, 8, None, _tr_anim("grow-x", 360, 520, "fade"), bg="{team.color2}")]
    if sub:
        import re as _re
        sub_up = _re.sub(r"\{([^}|]+)\}", r"{\1|upper}", sub)
        sub_up = "".join(p_ if p_.startswith("{") else p_.upper() for p_ in _re.split(r"(\{[^}]*\})", sub_up))
        m = _re.match(r"^\{([^}|]+)[^}]*\}$", sub)
        E.append(txt("Sub", 60, 676, 1800, 80, sub_up, 48, _tr_anim("fade", 320, 600), show=(m.group(1) if m else None), font=f, weight=800,
                     align="center", tracking=3))
    if tid == "tr_replay":
        E += [box("Rec dot", 1640, 90, 34, 34, "#E5483B", _tr_anim("pop", 300, 400), radius=17),
              txt("Rec", 1690, 80, 180, 54, "REC", 34, _tr_anim("fade", 260, 420), font=f, weight=800)]
    return {"name": "Transition: %s" % word, "group": "stinger", "autoHide": round((TR_OUT_AT + 500) / 1000.0, 1), "side": default_side, "sided": True,
            "network": True, "elements": E}


def transitions(S):
    return dict((t[0], transition(S, *t)) for t in TRANSITIONS)


# ================================================================ ROB'S DESIGNS (custom set)
# Gray-gradient name bars over dark stat rows, square team-colour logo tiles, inset headshots,
# a black-frame scorebug with labelled Balls / Strikes / Outs dots, a two-team intro card and a
# top-left league bug. Built in either style (font comes from S); colours are fixed to the design.
C_GRAY = "linear-gradient(180deg, #F6F7F9 0%, #DADDE2 52%, #AEB3BB 100%)"
C_DARK = "linear-gradient(180deg, #2B2E34 0%, #17191D 100%)"
C_INK = "#15171B"
C_LABEL = "#9DA3AC"


def C_TEAM(team):
    return ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 72%%, #fff) 0%%, {%s.color} 55%%, "
            "color-mix(in srgb, {%s.color} 72%%, #000) 100%%)" % (team, team, team))


def C_TEAM2(team):
    return ("linear-gradient(90deg, color-mix(in srgb, {%s.color2} 88%%, #fff) 0%%, {%s.color2} 45%%, "
            "color-mix(in srgb, {%s.color2} 62%%, #000) 100%%)" % (team, team, team))


def c_lower(S, kind, six=False):
    """Lower third: team logo tile, gray name bar (position over name), dark stat row, headshot at the right end."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    f = S["font"]
    X, Y = 70, 846
    T, NB, PH, H1, H2 = 172, 820, 150, 100, 72
    if kind == "pit":
        cols = [("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
                ("SO", "{pitcher.season.k|zero}"), ("WHIP", "{pitcher.season.whip|dash}"), ("PC", "{pitcher.today.pc|zero}")]
        if not six:
            cols = cols[:4]
    else:
        cols = [("AVG", "{batter.season.avg|avg}"), ("OBP", "{batter.season.obp|avg}"), ("SLG", "{batter.season.slg|avg}"),
                ("OPS", "{batter.season.ops|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}")]
        if not six:
            cols = cols[:4]
    out = {"type": "fade", "dur": 260, "delay": 0, "ease": "in"}
    E = [
        box("Logo tile", X, Y, T, H1 + H2, None, A("pop", 420, 0, out=out), bg=C_TEAM(team), shadow="0 10px 28px rgba(0,0,0,.4)"),
    ] + logo_or_abbr("Logo", X + 14, Y + 14, T - 28, H1 + H2 - 28, team, 52, A("zoom-out", 420, 160), S=S) + [
        box("Name bar", X + T, Y, NB + PH, H1, None, A("wipe-right", 440, 120, out=out), bg=C_GRAY, shadow="0 10px 28px rgba(0,0,0,.35)"),
        txt("Position", X + T + 26, Y + 8, 300, 30, U(S, "%s.pos" % who), 26, A("fade", 260, 420), font=f, weight=800, color="#4B5059", tracking=1),
        txt("Name", X + T + 24, Y + 32, NB - 40, 64, "{%s.name}" % who, 58, A("reveal-up", 380, 380), font=f, weight=800, color=C_INK, lineH=1),
        box("Stat row", X + T, Y + H1, NB, H2, None, A("wipe-right", 420, 240, out=out), bg=C_DARK),
        box("Photo bg", X + T + NB, Y, PH, H1 + H2, None, A("fade", 360, 260, out=out), bg=C_TEAM(team)),
        img("Headshot", X + T + NB, Y, PH, H1 + H2, "{%s.photo}" % who, A("slide-left", 420, 420, dist=30), show="%s.photo" % who, fit="cover",
            focus="center top"),
        txt("Number (no photo)", X + T + NB, Y, PH, H1 + H2, "#{%s.number}" % who, 64, A("pop", 360, 440), show="!%s.photo && %s.number" % (who, who),
            font=f, weight=800, align="center", textShadow=True),
    ]
    cw = NB / float(len(cols))
    for i, (lab, val) in enumerate(cols):
        cx = int(X + T + i * cw)
        E += [txt("%s label" % lab, cx, Y + H1 + 4, int(cw), 24, lab, 19, A("fade", 240, 480 + i * 50), font=f, weight=700, align="center", color=C_LABEL,
                  tracking=1),
              txt("%s value" % lab, cx, Y + H1 + 26, int(cw), 42, val, 38, A("reveal-up", 300, 500 + i * 50, change="flash"), font=f, weight=800,
                  align="center", color="#FFFFFF")]
    E += sponsor_tab(X + T + NB + PH - 300, Y - 50, 300, 44, 640, radius=2, a_type="wipe-up")
    nm = ("Pitcher" if kind == "pit" else "Batter") + " Lower Third (Classic%s)" % (", 6 stats" if six else "")
    return {"name": nm, "group": "lower", "autoHide": 9, "side": "", "sided": False, "elements": E, "pickable": True}


def c_scorebug(S, info=False):
    """Black-frame scorebug: inning column, team tiles with logos, score boxes, big diamond, labelled B / S / O dots.
    info=True adds pitcher (name, pitches, pitch speed) and batter (name, AVG, exit velocity) rows above."""
    f = S["font"]
    X, W, RH = 1286, 600, 66
    Y = 1080 - 24 - 2 * RH
    IW, TW, SW, DW = 82, 176, 74, 128
    BW = W - IW - TW - SW - DW
    E = []
    if info:
        IY = Y - 2 * 40 - 4
        E += [box("Info frame", X, IY, W, 80, "#0B0C0E", A("wipe-up", 360, 300), show=LIVE, shadow="0 8px 22px rgba(0,0,0,.45)"),
              box("Pitcher row", X + 4, IY + 4, W - 8, 36, None, A("fade", 260, 380), show=LIVE, bg=C_DARK),
              box("Batter row", X + 4, IY + 42, W - 8, 34, None, A("fade", 260, 420), show=LIVE, bg=C_DARK)]
        for (ry, a, b, c, cshow) in ((IY + 4, "P: " + U(S, "pitcher.last"), "P: {pitcher.today.pc|zero}", "PS: {velo.ps} MPH", "velo.ps"),
                                     (IY + 42, "B: " + U(S, "batter.last"), "{batter.season.avg|avg}", "EV: {velo.ev} MPH", "velo.ev")):
            E += [txt(a[:2] + " name", X + 18, ry, 250, 36, a, 24, A("fade", 240, 520), show=LIVE, font=f, weight=800, color="#FFFFFF"),
                  txt(a[:2] + " mid", X + 270, ry, 130, 36, b, 24, A("fade", 240, 560, change="flash"), show=LIVE, font=f, weight=800, color="#FFFFFF",
                      align="center"),
                  txt(a[:2] + " speed", X + 400, ry, W - 418, 36, c, 24, A("fade", 240, 600, change="flash"), show=both(LIVE, cshow), font=f, weight=800,
                      color="$accent", align="right")]
    E += [
        box("Frame", X, Y, W, 2 * RH, "#050506", A("wipe-left", 420, 0), radius=3, shadow="0 12px 30px rgba(0,0,0,.5)"),
        box("Inning col", X + 3, Y + 3, IW - 3, 2 * RH - 6, None, A("fade", 300, 140), bg=C_DARK),
        txt("Half", X, Y + 10, IW, 32, "{halfShort}", 24, A("fade", 240, 360, change="flash"), show=LIVE, font=f, weight=800, align="center", color="#FFFFFF"),
        txt("Inning", X, Y + 40, IW, 80, "{inning}", 64, A("reveal-up", 320, 380, change="roll"), show=LIVE, font=f, weight=800, align="center",
            color="#FFFFFF"),
        txt("Final", X, Y, IW, 2 * RH, "{statusText}", 22, A("fade", 240, 360), show="!" + LIVE, font=f, weight=800, align="center", color="#FFFFFF",
            wrap=True, fit=False),
    ]
    for i, side in enumerate(("away", "home")):
        ry = Y + i * RH
        tx = X + IW
        E += [box("%s tile" % side, tx + 2, ry + 3, TW - 4, RH - 6 + (0 if i else 0), None, A("wipe-right", 380, 160 + i * 70), bg=C_TEAM(side))]
        E += logo_or_abbr("%s mark" % side, tx + 12, ry + 8, TW - 24, RH - 16, side, 34, A("fade", 300, 340 + i * 70), S=S)
        E += [box("%s score bg" % side, tx + TW, ry + 3, SW - 3, RH - 6, "#1E2025", A("fade", 260, 260 + i * 70)),
              txt("%s runs" % side, tx + TW, ry + 3, SW - 3, RH - 6, "{%s.runs}" % side, 50, A("reveal-up", 300, 420 + i * 70, change="pop"), font=f,
                  weight=800, align="center", color="#FFFFFF"),
              box("%s at-bat" % side, tx + 2, ry + 3, 6, RH - 6, "$accent", A("grow-y", 260, 500), show="battingSide==%s && %s" % (side, LIVE))]
    dx = X + IW + TW + SW
    E += [el("bases", "Bases", dx + 2, Y + 16, DW - 4, 2 * RH - 32, A("pop", 380, 420), show=LIVE, bind="bases",
             style={"layout": "tight", "on": "$accent", "off": "#FFFFFF@0.10", "stroke": "#FFFFFF@0.85", "strokeW": 3})]
    bx = dx + DW
    for j, (lab, key, tot, on) in enumerate((("Balls", "balls", 3, "#36C46B"), ("Strikes", "strikes", 2, "#E5483B"), ("Outs", "outs", 2, "#FFD23F"))):
        ry = Y + 8 + j * 39
        E += [txt(lab, bx + 4, ry, 92, 38, L(S, lab), 19, A("fade", 240, 460 + j * 50), show=LIVE, font=f, weight=800, color="#FFFFFF"),
              el("dots", lab + " dots", bx + 92, ry + 4, BW - 100, 30, A("fade", 240, 500 + j * 50), show=LIVE, bind=key,
                 style={"total": tot, "size": 15, "gap": 6, "on": on, "off": "#FFFFFF@0.18", "align": "left"})]
    E += [txt("Final score", dx, Y, DW + BW, 2 * RH, "{statusText}", 34, A("fade", 260, 420), show="!" + LIVE, font=f, weight=800, align="center",
              color="#FFFFFF")]
    E += sponsor_tab(X, (Y - 84 - 50) if info else (Y - 50), W, 44, 640, radius=2, a_type="wipe-up")
    return {"name": "Scorebug: Classic%s" % (" + Pitch Info" if info else ""), "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "half_{halfKey}, scorebug"}


def c_team_intro(S):
    """Two stacked team rows over the ballpark photo: logo tile, team name bar in the secondary colour, record and place."""
    f = S["font"]
    E = [box("Backdrop", 0, 0, 1920, 1080, None, A("fade", 500, 0, out={"type": "fade", "dur": 400, "delay": 300, "ease": "in"}),
             bg="linear-gradient(180deg, #23272E, #0E1013)"),
         img("Ballpark", 0, 0, 1920, 1080, "{home.bg}", A("fade", 600, 0, out={"type": "fade", "dur": 400, "delay": 300, "ease": "in"}), show="home.bg",
             fit="cover"),
         box("Shade", 0, 0, 1920, 1080, "#000000@0.30", A("fade", 600, 100), show="home.bg")]
    for i, side in enumerate(("away", "home")):
        y = 196 + i * 360
        d = i * 260
        E += [box("%s tile" % side, 230, y, 250, 250, None, A("pop", 460, 200 + d), bg=C_TEAM(side), shadow="0 18px 40px rgba(0,0,0,.5)")]
        E += logo_or_abbr("%s logo" % side, 250, y + 20, 210, 210, side, 80, A("zoom-out", 480, 380 + d), S=S)
        E += [box("%s name bar" % side, 480, y, 1210, 168, None, A("wipe-right", 480, 300 + d), bg=C_TEAM2(side), shadow="0 18px 40px rgba(0,0,0,.45)"),
              txt("%s name" % side, 520, y, 1140, 168, "{%s.name}" % side, 92, A("reveal-up", 420, 520 + d), font=f, weight=800, color=C_INK, lineH=1),
              box("%s sub bar" % side, 480, y + 168, 1210, 82, None, A("wipe-right", 440, 420 + d), bg=C_DARK),
              txt("%s record" % side, 520, y + 168, 300, 82, "{%s.record}" % side, 50, A("fade", 300, 640 + d), font=f, weight=800, color="#FFFFFF"),
              txt("%s place" % side, 800, y + 168, 860, 82, U(S, "%s.place" % side), 50, A("fade", 300, 700 + d), show="%s.place" % side, font=f,
                  weight=800, color="#FFFFFF")]
    return {"name": "Team Intro (Classic)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def c_league_bug(S):
    """Top-left league mark with LIVE beside it."""
    f = S["font"]
    E = [img("League", 30, 26, 170, 78, "{league.logo}", A("fade", 500, 0), show="league.logo", shadow=True, focus="left center"),
         txt("League name", 30, 26, 170, 78, U(S, "league.name"), 46, A("fade", 500, 0), show="!league.logo && league.name", font=f, weight=800,
             textShadow=True),
         box("Live dot", 212, 56, 16, 16, "#E5483B", A("pop", 260, 300, loop={"type": "pulse", "dur": 900, "amount": 0.25}), show="show.live", radius=8),
         txt("Live", 236, 26, 200, 78, L(S, "Live"), 52, A("reveal-up", 400, 300), show="show.live", font=f, weight=800, italic=True,
             textShadow="0 2px 10px rgba(0,0,0,.6)")]
    return {"name": "League Bug (Top Left)", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E}


def custom_designs(S):
    """Rob's designs, ids prefixed c_ (they get their own "Classic" section in the graphics panel)."""
    return {
        "c_scorebug": c_scorebug(S), "c_scorebug_info": c_scorebug(S, True),
        "c_batter": c_lower(S, "bat"), "c_batter6": c_lower(S, "bat", True),
        "c_pitcher": c_lower(S, "pit"), "c_pitcher6": c_lower(S, "pit", True),
        "c_team_intro": c_team_intro(S), "c_league_bug": c_league_bug(S),
    }



# ================================================================ GAME OPEN: STATION
def station_open(S):
    """Animated game open on a subway-station wall: white tile wall, a mosaic station sign with the home club, a wall
    of tiles flipping over to the home colour and revealing the logo, two team posters with VS, then a lockup with the
    broadcaster mark, the matchup on a mosaic sign, an arrow sign to the ballpark and the yellow platform edge."""
    f = S["font"]
    TOTAL = 11000
    TILE_WALL = ("linear-gradient(#C9C5BC 3px, transparent 3px) 0 0 / 120px 60px, "
                 "linear-gradient(90deg, #C9C5BC 3px, transparent 3px) 0 0 / 120px 60px, "
                 "linear-gradient(180deg, #F6F4EF 0%, #E8E4DB 100%)")
    MOSAIC = "repeating-conic-gradient({home.color} 0 25%, {home.color2} 0 50%) 0 0 / 24px 24px"
    OUTF = {"type": "fade", "dur": 500, "delay": 0, "ease": "in"}

    def H(t, dur, delay, until, **kw):
        a = A(t, dur, delay, out=kw.pop("out", OUTF), **kw)
        a["hold"] = max(0, until - delay - dur)
        return a
    E = [box("Wall", 0, 0, 1920, 1080, None, H("fade", 500, 0, TOTAL - 600), bg=TILE_WALL),
         box("Vignette", 0, 0, 1920, 1080, None, H("fade", 600, 0, TOTAL - 600), bg="radial-gradient(ellipse at 50% 45%, transparent 40%, rgba(0,0,0,.45) 100%)"),
         # 1. station sign
         box("Sign border", 360, 330, 1200, 300, None, H("zoom-out", 600, 300, 2700), bg=MOSAIC),
         box("Sign panel", 384, 354, 1152, 252, "#EFE6D2", H("zoom-out", 600, 360, 2700)),
         txt("Sign text", 400, 354, 1120, 252, U(S, "home.name"), 120, H("letters", 700, 700, 2200, stagger=40), font=f, weight=800, align="center",
             color="{home.color}"),
         txt("Sign arrow", 400, 640, 1120, 70, "→  " + U(S, "venue"), 44, H("slide-right", 500, 1200, 2700, dist=40), show="venue", font=f, weight=800,
             align="center", color="#2B2B2B")]
    # 2. tile wall flips to the home colour, diagonal sweep
    cols, rows, sz = 16, 9, 120
    for r in range(rows):
        for c in range(cols):
            d = 2700 + (r + c) * 45
            E.append(box("Tile %d-%d" % (r, c), c * sz, r * sz, sz - 4, sz - 4, None, H("flip-y", 380, d, 5600, out={"type": "flip-y", "dur": 300,
                         "delay": 0, "ease": "in"}),
                         bg="linear-gradient(180deg, color-mix(in srgb, {home.color} 75%, #fff), {home.color} 60%, color-mix(in srgb, {home.color} 70%, #000))",
                         radius=6))
    E += [img("Wall logo", 560, 160, 800, 620, "{home.logo}", H("zoom-out", 600, 3700, 5600), show="home.logo"),
          txt("Wall nick", 0, 760, 1920, 220, U(S, "home.nick"), 200, H("letters", 600, 4000, 5600, stagger=50), font=f, weight=800, align="center",
              color="transparent", textStroke="4px #FFFFFF", textShadow="0 10px 30px rgba(0,0,0,.4)")]
    # 3. posters
    for i, side in enumerate(("away", "home")):
        x = 210 if i == 0 else 1110
        d = 5800 + i * 250
        E += [box("%s poster frame" % side, x - 16, 150, 632, 780, "#1E1E1E", H("slide-up" if i == 0 else "slide-down", 500, d, 8000, dist=120),
                  radius=10, shadow="0 30px 60px rgba(0,0,0,.45)"),
              box("%s poster" % side, x, 166, 600, 748, None, H("fade", 300, d + 200, 8000),
                  bg="linear-gradient(180deg, color-mix(in srgb, {%s.color} 80%%, #fff), {%s.color} 55%%, color-mix(in srgb, {%s.color} 60%%, #000))" % (side, side, side)),
              img("%s poster logo" % side, x + 60, 220, 480, 420, "{%s.logo}" % side, H("zoom-out", 500, d + 400, 8000), show="%s.logo" % side),
              txt("%s poster city" % side, x + 20, 660, 560, 70, U(S, "%s.city" % side), 50, H("fade", 300, d + 600, 8000), font=f, weight=700,
                  align="center", color="#FFFFFF"),
              txt("%s poster nick" % side, x + 20, 720, 560, 130, U(S, "%s.nick" % side), 110, H("reveal-up", 400, d + 700, 8000), font=f, weight=800,
                  align="center", color="#FFFFFF", textShadow="0 6px 20px rgba(0,0,0,.4)"),
              txt("%s poster rec" % side, x + 20, 846, 560, 50, "{%s.record}" % side, 36, H("fade", 300, d + 800, 8000), show="%s.record" % side,
                  font=f, weight=700, align="center", color="#FFFFFF@0.85")]
    E += [box("VS disc", 880, 460, 160, 160, "#1E1E1E", H("pop", 400, 6600, 8000), radius=80, borderW=6, borderColor="#FFFFFF"),
          txt("VS", 880, 460, 160, 160, L(S, "vs"), 64, H("pop", 400, 6700, 8000), font=f, weight=800, align="center", color="#FFFFFF")]
    # 4. lockup
    E += [img("Brand", 760, 120, 400, 200, "{brand.logo}", H("zoom-out", 500, 8200, TOTAL - 600), show="brand.logo"),
          box("Lockup border", 260, 360, 1400, 260, None, H("zoom-out", 500, 8300, TOTAL - 600), bg=MOSAIC),
          box("Lockup panel", 284, 384, 1352, 212, "#EFE6D2", H("zoom-out", 500, 8350, TOTAL - 600)),
          txt("Lockup away", 300, 384, 560, 212, U(S, "away.nick"), 84, H("slide-right", 400, 8600, TOTAL - 600, dist=40), font=f, weight=800,
              align="right", color="{away.color}"),
          txt("Lockup at", 860, 384, 200, 212, L(S, "at"), 52, H("fade", 300, 8750, TOTAL - 600), font=f, weight=700, align="center", color="#2B2B2B"),
          txt("Lockup home", 1060, 384, 560, 212, U(S, "home.nick"), 84, H("slide-left", 400, 8600, TOTAL - 600, dist=40), font=f, weight=800,
              color="{home.color}"),
          box("Arrow sign", 560, 660, 800, 80, "#111111", H("wipe-right", 400, 9000, TOTAL - 600), radius=6, show="venue"),
          txt("Arrow text", 580, 660, 760, 80, "→  " + U(S, "venue"), 40, H("fade", 300, 9200, TOTAL - 600), show="venue", font=f, weight=700,
              color="#FFFFFF"),
          box("Platform", 0, 980, 1920, 100, None, H("wipe-up", 500, 8400, TOTAL - 600),
              bg="radial-gradient(circle, #C9A400 5px, transparent 6px) 0 0 / 26px 26px, linear-gradient(180deg, #FFD400, #E8BF00)"),
          box("Platform edge", 0, 970, 1920, 12, "#F7F3EA", H("grow-x", 500, 8400, TOTAL - 600))]
    E += sponsor_tab(1540, 120, 340, 80, 8600, radius=6)
    return {"name": "Show: Game Open (Station)", "group": "full", "autoHide": TOTAL / 1000.0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "show"}

def all_new(S, prefix=""):
    """Every new graphic, keyed by id. prefix keeps ids unique when a package already has some of these."""
    g = {
        "batter_note": lower_note(S, "bat"), "pitcher_note": lower_note(S, "pit"),
        "batter_bar": stat_bar(S, "bat"), "pitcher_bar": stat_bar(S, "pit"),
        "batter_tall": tall_card(S, "bat"), "pitcher_tall": tall_card(S, "pit"),
        "feature": feature_card(S), "sp_compare": compare_card(S, "season"), "sp_today": compare_card(S, "today"),
        "final": final_card(S), "summary": game_summary(S), "performers": performers_card(S),
        "matchup_banner": matchup_banner(S), "matchup_split": matchup_split(S),
        "side_defense": side_defense(S), "side_plays": side_plays(S),
        "hr_event": hr_event(S), "hr_tracker": hr_tracker(S), "wp_event": wp_event(S),
        "show_bp": show_title(S, "Batting Practice", "Show: Batting Practice"),
        "show_pregame": show_title(S, "Pregame", "Show: Pregame"),
        "show_postgame": show_title(S, "Postgame", "Show: Postgame"),
        "team_title": team_title(S), "show_bug": show_bug(S), "up_next": up_next(S), "talent": talent(S),
        "ticker": ticker_bar(S), "bp_info": bp_info(S), "league_bug": league_bug(S),
    }
    g.update({"bug_compact": scorebug_compact(S), "bug_compact_title": scorebug_compact(S, True),
              "batter_tab": lower_tab(S, "bat"), "pitcher_tab": lower_tab(S, "pit"),
              "umpires": umpires_card(S), "def_of": defense_banner(S, "of"), "def_if": defense_banner(S, "if"),
              "def_field": defense_field(S), "def_lineup": defensive_lineup(S), "matchup_diamond": matchup_diamond(S),
              "split_card": split_card(S), "brand_bumper": brand_bumper(S),
              "tonight": tonight_card(S), "lineup_results": lineup_results(S), "lineup_projected": lineup_projected(S),
              "pitchers_today": pitchers_today(S), "probables": probables_card(S), "lineup_feature": lineup_feature(S),
              "stat_card_one": stat_card_one(S), "word_bumper": word_bumper(S), "lineup_bench": lineup_bench(S),
              "road_ahead": road_ahead(S), "around_league": around_league(S)})
    g.update(transitions(S))
    g["open_station"] = station_open(S)
    g.update(layouts(S))
    g.update(auto_game(S))
    g.update(extra_graphics(S))
    g.update(custom_designs(S))
    g.update(pro_suite(S))
    for k in PICKABLE:
        if k in g:
            g[k]["pickable"] = True
    return dict((prefix + k, v) for k, v in g.items())


# Graphics that can show a player picked in the Custom panel instead of the current batter / pitcher
PICKABLE = ("batter_splits", "pitcher_splits", "batter_bio", "pitcher_bio", "batter_tab", "pitcher_tab", "batter_note", "pitcher_note", "batter_bar", "pitcher_bar", "batter_tall", "pitcher_tall", "feature",
            "batter", "pitcher", "batter_card", "pitcher_card", "spotlight")


SPONSOR_SLOTS = {
    "batter_note": "lineup_{batter.slot}, batter", "pitcher_note": "pitcher",
    "batter_bar": "lineup_{batter.slot}, batter", "pitcher_bar": "pitcher",
    "batter_tall": "lineup_{batter.slot}, batter_card", "pitcher_tall": "pitcher_card",
    "feature": "feature", "sp_compare": "compare", "sp_today": "compare",
    "hr_event": "home_run",
    "batter_tab": "lineup_{batter.slot}, batter", "pitcher_tab": "pitcher",
    "c_batter": "lineup_{batter.slot}, batter", "c_batter6": "lineup_{batter.slot}, batter", "c_pitcher": "pitcher", "c_pitcher6": "pitcher",
}


def graphic_hash(g):
    """Content fingerprint of one graphic (element ids and the stamp itself left out), used to tell untouched
    package graphics from ones edited in the editor, so updates can replace only the untouched ones."""
    import hashlib
    import json as _json
    c = {k: v for k, v in (g or {}).items() if k not in ("_src", "presetId", "cat", "style", "sport")}
    c["elements"] = [{k: v for k, v in e.items() if k != "id"} for e in c.get("elements", [])]
    return hashlib.md5(_json.dumps(c, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:16]


def stamp(doc):
    """Stamp every graphic with its fingerprint and record which graphics this package version has."""
    for g in (doc.get("graphics") or {}).values():
        g["_src"] = graphic_hash(g)
    doc["graphicsIndex"] = sorted((doc.get("graphics") or {}).keys())
    return doc


# ================================================================ PRO SUITE (control panel > GAME OPS)
# In-game operations, storylines, breaks, postgame and fan / sponsor graphics. Every style gets them through all_new.

def _row_table(S, name, x, y, w, h, bind, columns, rowH=70, size=34, maxRows=8, delay=500, highlight=None, header=False):
    st = {"rowH": rowH, "size": size, "weight": 800, "color": "$text", "header": header, "headerH": 40, "headerSize": 20, "headerColor": "$accent",
          "padX": 18, "gap": 2, "maxRows": maxRows, "font": S["font"], "rowFill": "#FFFFFF@0.04", "altFill": "#FFFFFF@0.09"}
    if highlight:
        st.update({"highlight": highlight, "highlightFill": "$accent@0.35"})
    return el("table", name, x, y, w, h, A("none", 1, 0, rows={"type": "slide-right", "dur": 320, "stagger": 60, "delay": delay, "dist": 24}),
              bind=bind, columns=columns, style=st)


def _col(field, w, align="left", **kw):
    c = {"label": kw.pop("label", ""), "field": field, "w": w, "align": align}
    c.update(kw)
    return c


def _list_card(S, name, title, sub, bind, columns, rows=8, rowH=76, logo_team=None, foot=None, side="", sided=False, highlight=None, header=False,
               sponsor="show"):
    X, Y, W = 260, 110, 1400
    H = 96 + 42 + 24 + rows * rowH + (40 if header else 0)
    E = list_frame(S, X, Y, W, H, title, sub, logo_team, foot)
    E += [_row_table(S, "Rows", X + 30, Y + 160, W - 60, H - 170, bind, columns, rowH=rowH, maxRows=rows, highlight=highlight, header=header)]
    return {"name": name, "group": "full", "autoHide": 0, "side": side, "sided": sided, "elements": E, "sponsorSlot": sponsor}


def pitching_change(S):
    """Now pitching: the new pitcher with his season line and who he replaces (the fielding team's previous pitcher)."""
    f = S["font"]
    X, Y, W = 300, 860, 1320
    E = [box("Tab", X, Y - 44, 300, 44, S["hi"], A("wipe-up", 300, 0, out=OUT), radius=S["radius"]),
         txt("Tab text", X + 16, Y - 44, 268, 44, L(S, "Now pitching"), 26, A("fade", 240, 120), font=f, weight=800, color=S["hiText"]),
         box("Tile", X, Y, 140, 130, None, A("wipe-right", 320, 60, out=OUT), bg=TG(S, "team"))]
    E += logo_or_abbr("Logo", X + 14, Y + 14, 112, 102, "team", 34, A("pop", 320, 200), S=S)
    E += [box("Name bar", X + 140, Y, 560, 80, None, A("wipe-right", 380, 120, out=OUT), bg=S["strip"]),
          txt("Number", X + 156, Y, 80, 80, "{pitcher.number}", 40, A("fade", 240, 300), font=f, weight=800, color=S["stripText"], align="center"),
          txt("Name", X + 244, Y, 440, 80, U(S, "pitcher.name"), 46, A("reveal-up", 320, 280), font=f, weight=800, color=S["stripText"]),
          box("Replaces bar", X + 140, Y + 80, 560, 50, None, A("wipe-right", 360, 200, out=OUT), bg=S["dark"]),
          txt("Replaces", X + 160, Y + 80, 520, 50, L(S, "Replaces {team.prevPitcher.name}"), 26, A("fade", 240, 420), show="team.prevPitcher.name",
              font=f, weight=700, color="$dim"),
          txt("Throws", X + 160, Y + 80, 520, 50, "{pitcher.throws|hand}", 26, A("fade", 240, 420), show="!team.prevPitcher.name", font=f, weight=700,
              color="$dim"),
          box("Stats", X + 700, Y, W - 700, 130, None, A("wipe-right", 400, 220, out=OUT), bg=S["panel"])]
    cols = [("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
            ("K", "{pitcher.season.k|zero}"), ("WHIP", "{pitcher.season.whip|dash}")]
    cw = (W - 700) // len(cols)
    for i, (lab, val) in enumerate(cols):
        x = X + 700 + i * cw
        E += [txt("%s label" % lab, x, Y + 14, cw, 36, lab, 24, A("fade", 240, 400 + i * 50), font=f, weight=700, color="$dim", align="center"),
              txt("%s value" % lab, x, Y + 50, cw, 66, val, 50, A("reveal-up", 300, 420 + i * 50), font=f, weight=800, align="center")]
    E += sponsor_tab(X + W - 300, Y - 50, 300, 46, 600)
    return {"name": "Pitching Change", "group": "lower", "autoHide": 10, "side": "fielding", "sided": False, "elements": E, "sponsorSlot": "pitcher"}


def sub_notice(S):
    """Substitution notice: pinch hitter / pinch runner / defensive change (GAME OPS > Substitution)."""
    f = S["font"]
    X, Y, W = 360, 900, 1200
    E = [box("Label", X, Y, 300, 90, S["hi"], A("wipe-right", 320, 0, out=OUT), radius=S["radius"]),
         txt("Label text", X + 12, Y, 276, 90, U(S, "ops.sub.label"), 32, A("fade", 240, 160), font=f, weight=800, color=S["hiText"], align="center",
             wrap=True, fit=False, lineH=0.95),
         box("Tile", X + 300, Y, 110, 90, None, A("wipe-right", 300, 80, out=OUT), bg="linear-gradient(180deg, {ops.sub.team.color}, color-mix(in srgb, {ops.sub.team.color} 70%, #000))"),
         img("Logo", X + 312, Y + 10, 86, 70, "{ops.sub.team.logo}", A("pop", 300, 220), show="ops.sub.team.logo"),
         txt("Abbr", X + 300, Y, 110, 90, "{ops.sub.team.abbr}", 30, A("pop", 300, 220), show="!ops.sub.team.logo", font=f, weight=800, align="center"),
         box("Bar", X + 410, Y, W - 410, 90, None, A("wipe-right", 380, 120, out=OUT), bg=S["strip"]),
         txt("Number", X + 426, Y, 70, 90, "{ops.sub.number}", 40, A("fade", 240, 300), font=f, weight=800, color=S["stripText"], align="center"),
         txt("Name", X + 506, Y + 4, 460, 52, U(S, "ops.sub.name"), 44, A("reveal-up", 320, 280), font=f, weight=800, color=S["stripText"]),
         txt("For", X + 506, Y + 52, 460, 34, L(S, "For {ops.sub.out}"), 24, A("fade", 240, 400), show="ops.sub.out", font=f, weight=700, color=S["stripText"]),
         txt("Pos", X + W - 200, Y, 180, 90, U(S, "ops.sub.pos"), 38, A("fade", 240, 360), show="ops.sub.pos", font=f, weight=800, color=S["stripText"],
             align="right")]
    return {"name": "Substitution", "group": "lower", "autoHide": 8, "side": "", "sided": False, "elements": E}


def strike_zone(S):
    """Pitch tracker: the strike zone with every pitch of the at-bat numbered (green ball, red strike, blue in play) and the list."""
    f = S["font"]
    X, Y, W, H = 40, 170, 420, 800
    E = [box("Panel", X, Y, W, H, None, A("wipe-right", 400, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Head", X, Y, W, 64, None, A("wipe-right", 340, 80), bg=S["dark"], radius=S["radius"]),
         txt("Title", X + 18, Y, W - 36, 64, L(S, "Pitch tracker"), 30, A("fade", 240, 200), font=f, weight=800, color="$accent"),
         txt("Pitcher", X + 18, Y + 68, W - 36, 40, U(S, "pitcher.name"), 28, A("fade", 240, 260), font=f, weight=800),
         txt("Vs", X + 18, Y + 104, W - 36, 34, L(S, "vs {batter.name}"), 22, A("fade", 240, 300), font=f, weight=700, color="$dim"),
         el("zone", "Zone", X + 40, Y + 140, W - 80, 380, A("fade", 300, 350), bind="ops.pitchRows",
            style={"ball": "#2FB463", "strike": "#E5484D", "inplay": "#3D8BFD", "line": "#FFFFFF@0.85", "fill": "#FFFFFF@0.06", "r": 15, "font": f}),
         _row_table(S, "Pitches", X + 14, Y + 530, W - 28, H - 540, "ops.pitchRows",
                    [_col("n", 0.5, "center", color="$accent"), _col("{row.type|upper}" if S["up"] else "type", 2.4), _col("mph", 0.9, "right"),
                     _col("{row.call|upper}" if S["up"] else "call", 2.2, "right", color="$dim")], rowH=36, size=20, maxRows=7, delay=500)]
    return {"name": "Pitch Tracker: Strike Zone", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E}


def last_pitch(S):
    f = S["font"]
    X, Y, W, H = 40, 960, 460, 80
    E = [box("Box", X, Y, W, H, None, A("wipe-right", 340, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Speed bg", X, Y, 170, H, None, A("wipe-right", 300, 80), bg=S["strip"], radius=S["radius"]),
         txt("Speed", X, Y, 170, H - 18, "{ops.lastPitch.mph}", 52, A("reveal-up", 300, 200, change="pop"), font=f, weight=800, color=S["stripText"],
             align="center"),
         txt("MPH", X, Y + H - 26, 170, 24, "MPH", 18, A("fade", 240, 260), font=f, weight=800, color=S["stripText"], align="center"),
         txt("Type", X + 186, Y + 6, W - 200, 40, U(S, "ops.lastPitch.type"), 32, A("fade", 240, 260, change="fade"), font=f, weight=800),
         txt("Call", X + 186, Y + 44, W - 200, 30, U(S, "ops.lastPitch.call"), 22, A("fade", 240, 300, change="fade"), font=f, weight=700, color="$dim")]
    return {"name": "Last Pitch", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E}


def pitch_clock(S):
    f = S["font"]
    X, Y, W = 1640, 40, 240
    E = [box("Box", X, Y, W, 210, None, A("wipe-left", 340, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Head", X, Y, W, 44, None, A("wipe-left", 300, 80), bg=S["dark"], radius=S["radius"]),
         txt("Title", X, Y, W, 44, L(S, "Pitch clock"), 24, A("fade", 240, 160), font=f, weight=800, color="$accent", align="center"),
         el("clock", "Clock", X, Y + 44, W, 100, A("fade", 240, 200), mode="game", src="ops.pclock",
            style={"secs": True, "color": "$text", "size": 84, "weight": 800, "align": "center", "font": f}),
         txt("Pickoffs", X + 10, Y + 144, W - 20, 30, L(S, "Pickoffs left: {ops.pickoffs}"), 20, A("fade", 240, 260), font=f, weight=700, color="$dim",
             align="center"),
         txt("Visits", X + 10, Y + 174, W - 20, 30, L(S, "Mound visits {away.abbr} {ops.visits.away}  {home.abbr} {ops.visits.home}"), 18, A("fade", 240, 280),
             font=f, weight=700, color="$dim", align="center")]
    return {"name": "Pitch Clock", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E}


def challenge_bug(S):
    f = S["font"]
    X, Y, W = 1460, 40, 420
    E = [box("Box", X, Y, W, 170, None, A("wipe-left", 340, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Head", X, Y, W, 44, None, A("wipe-left", 300, 80), bg=S["dark"], radius=S["radius"]),
         txt("Title", X, Y, W, 44, L(S, "Challenges left"), 24, A("fade", 240, 160), font=f, weight=800, color="$accent", align="center")]
    for i, side in enumerate(("away", "home")):
        x = X + i * (W // 2)
        E += logo_or_abbr("%s logo" % side, x + 16, Y + 56, 70, 60, side, 24, A("pop", 300, 200 + i * 60), S=S)
        E += [txt("%s count" % side, x + 96, Y + 50, W // 2 - 110, 72, "{ops.chal.%s}" % side, 60, A("reveal-up", 300, 260 + i * 60, change="pop"), font=f,
                  weight=800, align="center")]
    E += [box("Review bar", X, Y + 130, W, 40, S["hi"], A("wipe-down", 300, 300), show="ops.review.has", radius=S["radius"]),
          txt("Review", X + 10, Y + 130, W - 20, 40, U(S, "ops.review.status"), 24, A("fade", 240, 360, change="flash"), show="ops.review.has", font=f, weight=800,
              color=S["hiText"], align="center"),
          box("Call bar", X, Y + 170, W, 40, None, A("wipe-down", 300, 360), show="ops.review.has && ops.review.call", bg=S["dark"], radius=S["radius"]),
          txt("Call", X + 10, Y + 170, W - 20, 40, L(S, "{ops.review.team} challenge: {ops.review.call}"), 20, A("fade", 240, 420),
              show="ops.review.has && ops.review.call", font=f, weight=700, align="center")]
    return {"name": "Challenge / Review", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E}


def bullpen_board(S):
    up = S["up"]
    return _list_card(S, "Bullpen", L(S, "Bullpen"), U(S, "team.name"), "bullpen",
                      [_col("{row.name|upper}" if up else "name", 3.2), _col("hand", 0.7, "center", color="$dim"),
                       _col("{row.status|upper}" if up else "status", 1.8, "center", color="$accent"), _col("last3", 1.4, "right", label=L(S, "Last 3 days"))],
                      rows=8, rowH=74, logo_team="team", side="fielding", sided=True, highlight="warm", header=True,
                      foot=(L(S, "Pitches thrown the last three days, oldest first"), "bullpen.0.last3"))


def hit_data(S):
    f = S["font"]
    X, Y, W = 360, 880, 1200
    E = [box("Name bar", X, Y, 420, 120, None, A("wipe-right", 340, 0, out=OUT), bg=S["strip"]),
         txt("Name", X + 20, Y + 10, 380, 60, U(S, "batter.name"), 44, A("reveal-up", 300, 160), font=f, weight=800, color=S["stripText"]),
         txt("Label", X + 20, Y + 68, 380, 40, L(S, "Batted ball"), 26, A("fade", 240, 240), font=f, weight=700, color=S["stripText"])]
    cells = [("Exit velo", "{ops.hit.ev}", "MPH", "ops.hit.ev"), ("Launch angle", "{ops.hit.la}°", "", "ops.hit.la"),
             ("Distance", "{ops.hit.dist}", "FT", "ops.hit.dist")]
    cw = (W - 420) // 3
    E += [box("Stats", X + 420, Y, W - 420, 120, None, A("wipe-right", 380, 100, out=OUT), bg=S["panel"])]
    for i, (lab, val, unit, cond) in enumerate(cells):
        x = X + 420 + i * cw
        E += [txt("%s label" % lab, x, Y + 10, cw, 34, L(S, lab), 22, A("fade", 240, 300 + i * 60), font=f, weight=700, color="$dim", align="center"),
              txt("%s value" % lab, x, Y + 44, cw, 70, (val + " " + unit).strip(), 52, A("reveal-up", 300, 320 + i * 60, change="pop"), show=cond, font=f, weight=800,
                  align="center"),
              txt("%s none" % lab, x, Y + 44, cw, 70, "-", 52, A("fade", 240, 320), show="!" + cond, font=f, weight=800, align="center", color="$dim")]
    return {"name": "Hit Data", "group": "lower", "autoHide": 9, "side": "", "sided": False, "elements": E}


def spray_chart(S):
    f = S["font"]
    X, Y, W, H = 1340, 150, 540, 830
    E = [box("Panel", X, Y, W, H, None, A("wipe-left", 400, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Head", X, Y, W, 64, None, A("wipe-left", 340, 80), bg=S["dark"], radius=S["radius"]),
         txt("Title", X + 18, Y, W - 36, 64, L(S, "Spray chart"), 30, A("fade", 240, 200), font=f, weight=800, color="$accent"),
         txt("Name", X + 18, Y + 70, W - 36, 50, U(S, "batter.name"), 36, A("fade", 240, 260), font=f, weight=800),
         el("spray", "Spray", X + 10, Y + 130, W - 20, 440, A("fade", 400, 350), bind="batter.tm.spray", show="batter.tm.bip",
            style={"grass": "#1F6B3A@0.55", "dirt": "#B5835A@0.55", "line": "#FFFFFF@0.85", "hr": "$accent"}),
         txt("Empty", X + 20, Y + 280, W - 40, 120, L(S, "Import TrackMan data to plot balls in play"), 26, A("fade", 240, 350), show="!batter.tm.bip", font=f,
             weight=700, color="$dim", align="center", wrap=True, fit=False),
         txt("Legend", X + 18, Y + 580, W - 36, 36, L(S, "{batter.tm.1B} 1B   {batter.tm.2B} 2B   {batter.tm.3B} 3B   {batter.tm.HR} HR"), 24, A("fade", 240, 500),
             show="batter.tm.bip", font=f, weight=800, align="center")]
    cells = [("Avg exit velo", "{batter.tm.avgEv}"), ("Max exit velo", "{batter.tm.maxEv}"), ("Hard-hit", "{batter.tm.hardPct}")]
    cw = (W - 36) // 3
    for i, (lab, val) in enumerate(cells):
        x = X + 18 + i * cw
        E += [box("%s bg" % lab, x + 4, Y + 630, cw - 8, 180, None, A("pop", 300, 600 + i * 60), bg=S["dark"], radius=S["radius"], show="batter.tm.bip"),
              txt("%s value" % lab, x + 4, Y + 650, cw - 8, 90, val, 54, A("reveal-up", 300, 660 + i * 60), show="batter.tm.bip", font=f, weight=800, align="center"),
              txt("%s label" % lab, x + 8, Y + 740, cw - 16, 60, L(S, lab), 22, A("fade", 240, 700 + i * 60), show="batter.tm.bip", font=f, weight=700, color="$dim",
                  align="center", wrap=True, fit=False)]
    return {"name": "Spray Chart", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E, "pickable": True}


def pitch_mix(S):
    f = S["font"]
    X, Y, W, H = 40, 300, 560, 560
    E = [box("Panel", X, Y, W, H, None, A("wipe-right", 400, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Head", X, Y, W, 64, None, A("wipe-right", 340, 80), bg=S["dark"], radius=S["radius"]),
         txt("Title", X + 18, Y, W - 36, 64, L(S, "Pitch mix"), 30, A("fade", 240, 200), font=f, weight=800, color="$accent"),
         txt("Name", X + 18, Y + 70, W - 36, 50, U(S, "pitcher.name"), 36, A("fade", 240, 260), font=f, weight=800),
         _row_table(S, "Mix", X + 14, Y + 130, W - 28, H - 150, "pitcher.tm.mix",
                    [_col("{row.type|upper}" if S["up"] else "type", 2.6, label=L(S, "Pitch")), _col("pct", 1, "right", label=L(S, "Usage"), color="$accent"),
                     _col("avg", 1, "right", label=L(S, "Avg")), _col("max", 1, "right", label=L(S, "Max"), color="$dim")],
                    rowH=60, size=28, maxRows=6, header=True),
         txt("Empty", X + 20, Y + 200, W - 40, 160, L(S, "Import TrackMan data for the pitch mix"), 26, A("fade", 240, 350), show="!pitcher.tm.mix.0.type", font=f,
             weight=700, color="$dim", align="center", wrap=True, fit=False)]
    return {"name": "Pitch Mix", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E, "pickable": True}


def team_compare(S):
    f = S["font"]
    X, Y, W, rows, RH = 260, 110, 1400, 7, 84
    H = 96 + 42 + 110 + rows * RH
    E = list_frame(S, X, Y, W, H, U(S, "ops.cmpTitle"), L(S, "{away.name} vs {home.name}"))
    for i, side in enumerate(("away", "home")):
        x = X + 40 if i == 0 else X + W - 340
        E += logo_or_abbr("%s logo" % side, x, Y + 150, 300, 90, side, 40, A("pop", 320, 300 + i * 80), S=S)
    for i in range(rows):
        p = "ops.cmpRows.%d" % i
        y = Y + 250 + i * RH
        d = 500 + i * 80
        E += [box("Row %d" % i, X + 30, y, W - 60, RH - 6, "#FFFFFF@0.06", A("wipe-right", 300, d), show=p + ".label", radius=S["radius"]),
              txt("Row %d away" % i, X + 50, y, 300, RH - 6, "{%s.away}" % p, 44, A("fade", 260, d + 80), show=p + ".label", font=f, weight=800, align="center"),
              txt("Row %d label" % i, X + 360, y, W - 720, RH - 6, U(S, p + ".label"), 32, A("fade", 260, d + 60), show=p + ".label", font=f, weight=700,
                  color="$accent", align="center"),
              txt("Row %d home" % i, X + W - 350, y, 300, RH - 6, "{%s.home}" % p, 44, A("fade", 260, d + 80), show=p + ".label", font=f, weight=800,
                  align="center")]
    return {"name": "Team Comparison", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def season_series(S):
    f = S["font"]
    X, Y, W = 360, 220, 1200
    E = [card(S, "Card", X, Y, W, 620),
         box("Head", X + 14, Y + 14, W - 28, 90, None, A("wipe-right", 360, 200), bg=S["dark"]),
         txt("Title", X + 14, Y + 14, W - 28, 90, L(S, "Season series"), 54, A("reveal-up", 360, 320), font=f, weight=800, align="center")]
    for i, side in enumerate(("away", "home")):
        x = X + 60 if i == 0 else X + W - 400
        E += [box("%s tile" % side, x, Y + 130, 340, 240, None, A("pop", 360, 400 + i * 100), bg=TG(S, side), radius=S["radius"])]
        E += logo_or_abbr("%s logo" % side, x + 40, Y + 150, 260, 200, side, 70, A("zoom-out", 400, 500 + i * 100), S=S)
    E += [txt("Score", X + 400, Y + 130, W - 800, 240, "{ops.series.away} - {ops.series.home}", 130, A("pop", 400, 700), font=f, weight=800, align="center"),
          txt("Note", X + 40, Y + 390, W - 80, 60, U(S, "ops.series.note"), 34, A("fade", 300, 900), show="ops.series.note", font=f, weight=800, color="$accent",
              align="center"),
          txt("Last", X + 40, Y + 460, W - 80, 56, L(S, "Last meeting: ") + "{ops.series.last}", 30, A("fade", 300, 1000), show="ops.series.last", font=f,
              weight=700, align="center"),
          txt("Next", X + 40, Y + 520, W - 80, 56, L(S, "Next meeting: ") + "{ops.series.next}", 30, A("fade", 300, 1100), show="ops.series.next", font=f,
              weight=700, color="$dim", align="center")]
    return {"name": "Season Series", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def weather_bar(S):
    f = S["font"]
    X, Y, W = 360, 880, 1200
    E = [box("Label", X, Y, 300, 120, None, A("wipe-right", 320, 0, out=OUT), bg=S["dark"]),
         txt("Label t", X, Y + 10, 300, 50, L(S, "Game-time"), 28, A("fade", 240, 160), font=f, weight=700, color="$accent", align="center"),
         txt("Label t2", X, Y + 56, 300, 56, L(S, "Weather"), 44, A("reveal-up", 300, 200), font=f, weight=800, align="center"),
         box("Bar", X + 300, Y, W - 300, 120, None, A("wipe-right", 380, 100, out=OUT), bg=S["panel"])]
    cells = [("Temp", "{ops.wx.temp}", "ops.wx.temp"), ("Wind", "{ops.wx.wind}", "ops.wx.wind"), ("Sky", "{ops.wx.cond}", "ops.wx.cond"),
             ("Humidity", "{ops.wx.hum}", "ops.wx.hum")]
    cw = (W - 300) // 4
    for i, (lab, val, cond) in enumerate(cells):
        x = X + 300 + i * cw
        E += [txt("%s label" % lab, x, Y + 12, cw, 34, L(S, lab), 22, A("fade", 240, 300 + i * 60), font=f, weight=700, color="$dim", align="center"),
              txt("%s value" % lab, x + 8, Y + 46, cw - 16, 64, U(S, cond), 40, A("reveal-up", 300, 320 + i * 60), show=cond, font=f, weight=800, align="center")]
    E += sponsor_tab(X + W - 300, Y - 50, 300, 46, 500)
    return {"name": "Weather", "group": "lower", "autoHide": 9, "side": "", "sided": False, "elements": E, "sponsorSlot": "weather, show"}


def delay_screen(S):
    f = S["font"]
    E = [box("Background", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT), bg=S.get("titleBg") or S["panel"]),
         img("Broadcaster", 810, 90, 300, 150, "{brand.logo}", A("pop", 420, 200), show="brand.logo"),
         txt("Title", 160, 260, 1600, 130, U(S, "ops.delay.title"), 110, A("reveal-up", 400, 300), font=f, weight=800, align="center"),
         el("clock", "Clock", 460, 400, 1000, 220, A("pop", 420, 450), mode="{ops.delay.mode}", target="{ops.delay.resume}", since="{ops.delay.since}",
            style={"color": "$accent", "size": 180, "weight": 800, "align": "center", "font": f}),
         txt("Clock label", 160, 610, 1600, 50, L(S, "Delay so far"), 30, A("fade", 300, 500), show="!ops.delay.resume", font=f, weight=700, color="$dim", align="center"),
         txt("Clock label 2", 160, 610, 1600, 50, L(S, "Expected to resume at {ops.delay.resume}"), 30, A("fade", 300, 500), show="ops.delay.resume", font=f,
             weight=700, color="$dim", align="center"),
         txt("Message", 260, 680, 1400, 120, "{ops.delay.msg}", 40, A("fade", 300, 700), show="ops.delay.msg", font=f, weight=700, align="center", wrap=True, fit=False),
         box("Score bar", 560, 830, 800, 90, None, A("wipe-up", 360, 800), bg=S["dark"], radius=S["radius"]),
         txt("Score", 560, 830, 800, 90, "{away.abbr} {away.runs}   {home.abbr} {home.runs}   {statusText}", 40, A("fade", 300, 900), font=f, weight=800,
             align="center")]
    E += _sponsor_corner(S, 1560, 920, 320, 130, 900)
    return {"name": "Delay Screen", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def tech_slate(S):
    f = S["font"]
    E = [box("Background", 0, 0, 1920, 1080, None, A("fade", 300, 0, out=OUT), bg=S.get("titleBg") or S["panel"]),
         img("Broadcaster", 760, 220, 400, 220, "{brand.logo}", A("pop", 420, 100), show="brand.logo"),
         txt("Broadcaster name", 160, 260, 1600, 160, "{brand.short|upper}", 120, A("pop", 420, 100), show="!brand.logo && brand.short", font=f, weight=900,
             align="center"),
         txt("Title", 160, 480, 1600, 130, U(S, "ops.techTitle"), 96, A("reveal-up", 400, 300), font=f, weight=800, align="center"),
         box("Rule", 760, 620, 400, 8, "$accent", A("grow-x", 300, 500)),
         txt("Message", 160, 650, 1600, 90, U(S, "ops.techMsg"), 52, A("fade", 300, 600, loop={"type": "pulse", "dur": 2400, "amount": 0.35}), font=f, weight=700,
             color="$dim", align="center")]
    return {"name": "Technical Difficulties", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def three_stars(S):
    f = S["font"]
    X, Y, W = 160, 140, 1600
    E = [card(S, "Card", X, Y, W, 800),
         box("Head", X + 14, Y + 14, W - 28, 96, None, A("wipe-right", 360, 200), bg=S["dark"]),
         txt("Title", X + 14, Y + 14, W - 28, 96, L(S, "Stars of the game"), 60, A("reveal-up", 360, 320), font=f, weight=800, align="center")]
    cw = (W - 80) // 3
    for i in range(3):
        p = "ops.stars.%d" % i
        x = X + 40 + i * cw
        d = 500 + (2 - i) * 300
        E += [box("Star %d bg" % (i + 1), x + 10, Y + 140, cw - 20, 620, None, A("zoom-out", 420, d), show=p + ".name", bg=S["panel2"], radius=S["radius"]),
              txt("Star %d rank" % (i + 1), x + 10, Y + 160, cw - 20, 160, "★" * (i + 1), 90, A("pop", 400, d + 100), show=p + ".name", font=f, weight=800,
                  color="$accent", align="center"),
              txt("Star %d label" % (i + 1), x + 10, Y + 320, cw - 20, 50, L(S, ("First", "Second", "Third")[i] + " star"), 30, A("fade", 300, d + 150),
                  show=p + ".name", font=f, weight=700, color="$dim", align="center"),
              txt("Star %d name" % (i + 1), x + 30, Y + 380, cw - 60, 150, U(S, p + ".name"), 64, A("reveal-up", 400, d + 200), show=p + ".name", font=f,
                  weight=800, align="center", wrap=True, fit=False, lineH=0.95),
              txt("Star %d team" % (i + 1), x + 30, Y + 540, cw - 60, 50, U(S, p + ".team"), 34, A("fade", 300, d + 260), show=p + ".team", font=f, weight=800,
                  color="$accent", align="center"),
              txt("Star %d line" % (i + 1), x + 30, Y + 600, cw - 60, 140, "{%s.line}" % p, 34, A("fade", 300, d + 320), show=p + ".line", font=f, weight=700,
                  align="center", wrap=True, fit=False)]
    return {"name": "Three Stars", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "final"}


def k_counter(S):
    f = S["font"]
    X, Y, W = 1460, 40, 420
    E = [box("Box", X, Y, W, 150, None, A("wipe-left", 340, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Head", X, Y, W, 44, None, A("wipe-left", 300, 80), bg=S["dark"], radius=S["radius"]),
         txt("Title", X + 14, Y, W - 28, 44, U(S, "ops.k.title"), 24, A("fade", 240, 160), font=f, weight=800, color="$accent", align="center"),
         txt("Count", X + 10, Y + 44, 130, 106, "{ops.k.count}", 84, A("reveal-up", 300, 200, change="pop"), font=f, weight=800, align="center"),
         txt("Marks", X + 150, Y + 54, W - 164, 86, "{ops.k.marks}", 34, A("fade", 240, 260, change="flash"), font=f, weight=900, color="$accent", wrap=True,
             fit=False, tracking=2, lineH=1.0)]
    E += sponsor_tab(X, Y + 156, W, 54, 400)
    return {"name": "Strikeout Counter", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "kcounter, scorebug"}


def billboard(S):
    f = S["font"]
    E = [box("Background", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT), bg=S.get("titleBg") or S["panel"]),
         txt("Head", 160, 140, 1600, 70, L(S, "{sponsor.label}"), 44, A("fade", 300, 300), show="sponsor.label", font=f, weight=700, color="$dim", align="center"),
         txt("Head default", 160, 140, 1600, 70, L(S, "Brought to you by"), 44, A("fade", 300, 300), show="!sponsor.label", font=f, weight=700, color="$dim",
             align="center"),
         box("Plate", 460, 240, 1000, 520, "#FFFFFF", A("zoom-out", 500, 300), radius=S["cardRadius"], shadow=S["shadow"], show="sponsor.on"),
         img("Logo", 520, 280, 880, 440, "{sponsor.logo}", A("fade", 500, 600, change="fade"), show="sponsor.on && sponsor.logo"),
         txt("Name", 500, 260, 920, 480, "{sponsor.name}", 110, A("fade", 400, 600, change="fade"), show="sponsor.on && !sponsor.logo", font=f, weight=800,
             color="#121620", align="center", wrap=True, fit=False),
         txt("Tag", 160, 800, 1600, 100, "{ops.billTag}", 54, A("reveal-up", 400, 900), show="ops.billTag", font=f, weight=800, align="center"),
         img("Broadcaster", 860, 940, 200, 100, "{brand.logo}", A("fade", 300, 1100), show="brand.logo")]
    return {"name": "Sponsor Billboard", "group": "full", "autoHide": 15, "side": "", "sided": False, "elements": E, "sponsorSlot": "billboard, show"}


def shout_lower(S):
    f = S["font"]
    X, Y, W = 360, 900, 1200
    E = [box("Label", X, Y, 320, 100, S["hi"], A("wipe-right", 320, 0, out=OUT), radius=S["radius"]),
         txt("Label t", X + 14, Y, 292, 100, U(S, "ops.shoutsTitle"), 28, A("fade", 240, 160), font=f, weight=800, color=S["hiText"], align="center", wrap=True,
             fit=False, lineH=0.95),
         box("Bar", X + 320, Y, W - 320, 100, None, A("wipe-right", 380, 100, out=OUT), bg=S["strip"]),
         txt("Text", X + 344, Y + 6, W - 370, 56, "{ops.shout.text}", 42, A("reveal-up", 320, 260, change="fade"), font=f, weight=800, color=S["stripText"]),
         txt("Note", X + 344, Y + 60, W - 370, 34, "{ops.shout.note}", 24, A("fade", 240, 340, change="fade"), show="ops.shout.note", font=f, weight=700,
             color=S["stripText"])]
    E += sponsor_tab(X + W - 300, Y - 50, 300, 46, 500)
    return {"name": "Shout-out (Next)", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "fans, show"}


def poll_card(S):
    f = S["font"]
    X, Y, W = 360, 160, 1200
    E = [card(S, "Card", X, Y, W, 760),
         box("Head", X + 14, Y + 14, W - 28, 90, None, A("wipe-right", 360, 200), bg=S["dark"]),
         txt("Title", X + 14, Y + 14, W - 28, 90, L(S, "Fan poll"), 52, A("reveal-up", 360, 320), font=f, weight=800, align="center", color="$accent"),
         txt("Question", X + 50, Y + 120, W - 100, 140, "{podcast.poll}", 50, A("fade", 300, 400), font=f, weight=800, align="center", wrap=True, fit=False)]
    for i in range(4):
        p = "podcast.o%d" % (i + 1)
        y = Y + 280 + i * 110
        d = 500 + i * 100
        E += [box("Opt %d bg" % i, X + 50, y, W - 100, 90, "#FFFFFF@0.08", A("wipe-right", 300, d), show=p + ".text", radius=S["radius"]),
              box("Opt %d bar" % i, X + 50, y, W - 100, 90, "$accent@0.45", A("grow-x", 700, d + 200, origin="left", change="fade"), show=p + ".text",
                  radius=S["radius"], pct="{%s.pct}" % p),
              txt("Opt %d letter" % i, X + 66, y, 60, 90, "{%s.n}" % p, 44, A("fade", 240, d + 100), show=p + ".text", font=f, weight=800, color="$accent"),
              txt("Opt %d text" % i, X + 140, y, W - 380, 90, U(S, p + ".text"), 40, A("fade", 240, d + 120), show=p + ".text", font=f, weight=800),
              txt("Opt %d pct" % i, X + W - 240, y, 170, 90, "{%s.pctText}" % p, 44, A("fade", 240, d + 300, change="pop"), show=p + ".pctText", font=f,
                  weight=800, align="right")]
    E += [txt("Foot", X + 50, Y + 720, W - 100, 30, L(S, "Vote with us at {podcast.x}"), 24, A("fade", 240, 900), show="podcast.x", font=f, weight=700,
              color="$dim", align="center")]
    return {"name": "Fan Poll", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


def social_bar(S):
    f = S["font"]
    X, Y, W = 260, 920, 1400
    E = [box("Bar", X, Y, W, 100, None, A("wipe-right", 380, 0, out=OUT), bg=S["panel"], radius=S["radius"], shadow=True),
         box("Label", X, Y, 260, 100, S["hi"], A("wipe-right", 320, 60), radius=S["radius"]),
         txt("Label t", X + 10, Y, 240, 100, L(S, "Follow us"), 36, A("fade", 240, 200), font=f, weight=800, color=S["hiText"], align="center")]
    cw = (W - 280) // 5
    for i in range(5):
        p = "podcast.s%d" % (i + 1)
        x = X + 270 + i * cw
        E += [txt("Icon %d" % i, x, Y + 10, cw, 34, "{%s.icon}" % p, 22, A("fade", 240, 300 + i * 80), show=p + ".handle", font=f, weight=800, color="$accent",
                  align="center"),
              txt("Handle %d" % i, x + 6, Y + 44, cw - 12, 46, "{%s.handle}" % p, 30, A("fade", 240, 320 + i * 80), show=p + ".handle", font=f, weight=800,
                  align="center")]
    return {"name": "Social / Follow Us", "group": "lower", "autoHide": 10, "side": "", "sided": False, "elements": E}


def pro_suite(S):
    up = S["up"]
    g = {"pitching_change": pitching_change(S), "sub_notice": sub_notice(S), "strike_zone": strike_zone(S), "last_pitch": last_pitch(S),
         "pitch_clock": pitch_clock(S), "challenge_bug": challenge_bug(S), "bullpen_board": bullpen_board(S), "hit_data": hit_data(S),
         "spray_chart": spray_chart(S), "pitch_mix": pitch_mix(S), "team_compare": team_compare(S), "season_series_card": season_series(S),
         "weather_bar": weather_bar(S), "delay_screen": delay_screen(S), "tech_slate": tech_slate(S), "three_stars": three_stars(S),
         "k_counter": k_counter(S), "billboard": billboard(S), "shout_lower": shout_lower(S), "fan_poll": poll_card(S), "social_bar": social_bar(S)}
    g["streaks_card"] = _list_card(S, "Streak Tracker", L(S, "Streak watch"), L(S, "{away.name} vs {home.name}"), "ops.streakRows",
                                   [_col("{row.player|upper}" if up else "player", 3), _col("{row.label|upper}" if up else "label", 2.4, color="$dim"),
                                    _col("value", 1.4, "right", color="$accent")])
    g["milestones_card"] = _list_card(S, "Milestone Watch", L(S, "Milestone watch"), L(S, "{away.name} vs {home.name}"), "ops.msRows",
                                      [_col("{row.player|upper}" if up else "player", 3), _col("{row.label|upper}" if up else "label", 3, color="$accent"),
                                       _col("value", 1.4, "right", color="$dim")])
    g["moves_card"] = _list_card(S, "Roster Moves", U(S, "ops.movesTitle"), U(S, "home.name"), "ops.moveRows",
                                 [_col("date", 1.2, color="$dim"), _col("{row.player|upper}" if up else "player", 2.6),
                                  _col("{row.move|upper}" if up else "move", 3.4, color="$accent")], logo_team="home")
    g["promos_card"] = _list_card(S, "Upcoming Promotions", U(S, "ops.promosTitle"), U(S, "home.name"), "ops.promoRows",
                                  [_col("date", 1.3, color="$accent"), _col("opp", 1.5), _col("promo", 4.2)], logo_team="home", sponsor="promos, show")
    g["shouts_card"] = _list_card(S, "Shout-outs", U(S, "ops.shoutsTitle"), U(S, "venue"), "ops.shoutRows",
                                  [_col("text", 3.6), _col("note", 2, "right", color="$dim")], sponsor="fans, show")
    return g
