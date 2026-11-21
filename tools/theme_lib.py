"""Shared builder for the theme packages (tools/build_themes.py).

A theme is a dict of colours, faces, textures and decoration hooks. build(T) makes a full package from it: the shared
library graphics restyled through the rebuild kit and skin, plus a themed scorebug, batter and pitcher lower thirds, a
show open, a home-run stinger, a player card and whatever extra signature graphics the theme adds.

Theme keys (all optional except key / name / desc):
  key, name, desc, font (main face stack), font2 (body face stack), deco (display face stack for big titles)
  bg, panel, panel2, dark, strip, stripText, val, valText, hi, hiText, ink, text, dim, edge, line, rule, shadow, r (radius)
  glow (textShadow for big titles), title (full-screen backdrop css), texture (overlay css on full screens)
  team(t) -> css for a team-colour fill; upper (bool) upper-case names
  bug_decor(X, Y, W, H) / lt_decor(X, Y, W, H) / open_decor() / hr_decor() / screen_over() -> lists of elements
  hr_word, open_kicker, card(T) -> graphic, extras(T) -> {gid: graphic}, bug_variant ("rows" | "bar"), bases on/off
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
import rebuild as RB  # noqa: E402
from broadcast_lib import A, box, txt, img, el, logo_or_abbr  # noqa: E402

LIVE = "inPlay"
OUT_ = {"type": "fade", "dur": 260, "delay": 0, "ease": "in"}
H = "$font"
F = "$font2"
NIGHT_DOC = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
COND = NIGHT_DOC["theme"]["font2"]


def team_v(t):
    return ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 80%%, #fff) 0%%, {%s.color} 50%%, "
            "color-mix(in srgb, {%s.color} 66%%, #000) 100%%)") % (t, t, t)


def defaults(T):
    D = dict(font=COND, font2=COND, bg="#0B0C0E", panel="linear-gradient(180deg, #23262B, #121418)", panel2="linear-gradient(180deg, #2E3137, #1A1C20)",
             dark="#0B0C0E", strip="linear-gradient(180deg, #FFFFFF, #E2E5EA)", stripText="#121418", val="linear-gradient(180deg, #FFFFFF, #E6E8EC)",
             valText="#121418", hi="#F2C230", hiText="#121418", ink="#121418", text="#FFFFFF", dim="#B9BEC6", edge="#FFFFFF@0.18",
             line="#FFFFFF@0.16", rule=None, shadow="0 10px 26px rgba(0,0,0,.55)", r=4, glow="", title="radial-gradient(ellipse at 50% 35%, #2A2C31, #0B0C0E 70%)",
             texture="", team=team_v, upper=True, hr_word="HOME RUN", open_kicker="", bug_variant="rows", base_on=None, base_off="#FFFFFF@0.25",
             frame=None, tile_border="#00000000", title_color=None, tracking=0, word_color=None)
    D.update(T)
    D["deco"] = D.get("deco") or D["font"]
    D["rule"] = D["rule"] or D["hi"]
    D["frame"] = D["frame"] or D["panel"]
    D["base_on"] = D["base_on"] or D["hi"]
    D["title_color"] = D["title_color"] or D["text"]
    D["word_color"] = D["word_color"] or D["title_color"]
    return D


def W(T, name, x, y, w, h, text, size, a, show=None, **st):
    st.setdefault("font", F)
    st.setdefault("weight", 800)
    st.setdefault("color", T["text"])
    return txt(name, x, y, w, h, text, size, a, show=show, **st)


def D_(T, name, x, y, w, h, text, size, a, show=None, **st):
    """Display-face text (the theme's deco face, glow, title colour)."""
    st.setdefault("font", T["deco"])
    st.setdefault("weight", 900)
    st.setdefault("color", T["title_color"])
    if T["glow"]:
        st.setdefault("textShadow", T["glow"])
    if T["tracking"]:
        st.setdefault("tracking", T["tracking"])
    return txt(name, x, y, w, h, text, size, a, show=show, **st)


def up(T, s):
    """Upper-case a binding string in themes that set upper: {tokens} get |upper, literal words are upper-cased."""
    if not T["upper"]:
        return s
    import re
    return "".join(p.replace("}", "|upper}") if p.startswith("{") else p.upper() for p in re.split(r"(\{[^}]*\})", s))


def backdrop(T, name="Backdrop", d=0):
    E = [box(name, 0, 0, 1920, 1080, None, A("fade", 400, d, out=OUT_), bg=T["title"])]
    if T["texture"]:
        E.append(box(name + " texture", 0, 0, 1920, 1080, None, A("fade", 600, d + 150), bg=T["texture"]))
    return E


def net_mark(T, name, x, y, w, h, a):
    return [img(name, x, y, w, h, "{brand.logo}", a, show="brand.logo"),
            W(T, name + " text", x, y, w, h, "{brand.short|upper}", int(h * 0.6), a, show="!brand.logo && brand.short", align="center"),
            img(name + " league", x, y, w, h, "{league.logo}", a, show="!brand.logo && !brand.short && league.logo")]


def call(T, k, *args):
    f = T.get(k)
    return list(f(*args)) if f else []


# ------------------------------------------------------------------ scorebug
def scorebug(T):
    if T["bug_variant"] == "bar":
        return scorebug_bar(T)
    X, Y, RH = 52, 46, 46
    TW, AW, SW, CW = 54, 92, 60, 104
    Wd = TW + AW + SW + 4 + CW * 2 + 8
    y0 = Y
    E = call(T, "bug_under", X, Y, Wd, 2 * RH + 40)
    E += [box("Frame", X, y0, Wd, 2 * RH + 4, None, A("wipe-right", 420, 0, out=OUT_), bg=T["frame"], radius=T["r"], borderW=2,
              borderColor=T["edge"], shadow=T["shadow"])]
    for i, side in enumerate(("away", "home")):
        y = y0 + 2 + i * RH
        d = 160 + i * 70
        E += [box("%s tile" % side, X + 2, y, TW, RH - 2, None, A("wipe-right", 300, d), bg=T["team"](side), radius=max(0, T["r"] - 2))]
        E += logo_or_abbr("%s logo" % side, X + 6, y + 4, TW - 8, RH - 10, side, 18, A("fade", 260, d + 120), S={"font": F})
        E += [W(T, "%s abbr" % side, X + TW + 10, y, AW - 12, RH - 2, "{%s.abbr}" % side, 28, A("fade", 260, d + 140), font=H),
              box("%s score bg" % side, X + TW + AW, y + 2, SW, RH - 6, None, A("fade", 260, d + 60), bg=T["val"], radius=max(0, T["r"] - 2)),
              W(T, "%s runs" % side, X + TW + AW, y + 2, SW, RH - 6, "{%s.runs}" % side, 32, A("reveal-up", 300, d + 160, change="pop"), align="center",
                color=T["valText"], font=H)]
    cx = X + TW + AW + SW + 6
    E += [W(T, "Count", cx, y0 + 2, CW, RH, "{balls}-{strikes}", 28, A("fade", 240, 380, change="flash"), show=LIVE, align="center", font=H),
          el("dots", "Outs", cx, y0 + RH + 2, CW, RH - 4, A("fade", 240, 400), show=LIVE, bind="outs",
             style={"total": 3, "size": 13, "gap": 9, "on": T["hi"], "off": "#FFFFFF@0.22", "shape": T.get("dot_shape", "circle"), "align": "center"}),
          W(T, "Status", cx, y0, CW * 2, 2 * RH, "{statusText}", 22, A("fade", 240, 360), show="!" + LIVE, align="center", wrap=True, fit=False, font=H)]
    bx = cx + CW
    E += [el("bases", "Bases", bx + 8, y0 + 6, CW - 16, RH - 6, A("pop", 320, 420), show=LIVE, bind="bases",
             style={"layout": "tight", "on": T["base_on"], "off": T["base_off"], "stroke": "#00000066", "strokeW": 2}),
          W(T, "Inning", bx, y0 + RH + 2, CW, RH - 6, "{arrow}{inning}", 24, A("fade", 240, 440, change="roll"), show=LIVE, align="center", font=H)]
    by = y0 + 2 * RH + 6
    E += [box("Pitcher bar", X, by, Wd, 34, None, A("wipe-down", 300, 500, out=OUT_), bg=T["dark"], radius=T["r"], show=LIVE, borderW=1,
              borderColor=T["edge"]),
          W(T, "Pitcher", X + 12, by, Wd - 130, 34, up(T, "{pitcher.name|initial}"), 20, A("fade", 240, 600, change="fade"), show=LIVE),
          W(T, "Pitch count", X + Wd - 118, by, 106, 34, "P: {pitcher.today.pc|zero}", 20, A("fade", 240, 620, change="flash"), show=LIVE, align="right",
            color=T["hi"])]
    E += call(T, "bug_decor", X, Y, Wd, 2 * RH + 40)
    E += BL.sponsor_tab(X, by + 40, 300, 40, 700, radius=T["r"], a_type="wipe-down")
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "half_{halfKey}, scorebug"}


def scorebug_bar(T):
    """One long bar across the top left: AWAY score | HOME score | inning | bases | count and outs."""
    X, Y, Hh = 52, 40, 60
    E = call(T, "bug_under", X, Y, 760, Hh)
    E += [box("Frame", X, Y, 760, Hh, None, A("wipe-right", 420, 0, out=OUT_), bg=T["frame"], radius=T["r"], borderW=2, borderColor=T["edge"],
              shadow=T["shadow"])]
    x = X + 4
    for i, side in enumerate(("away", "home")):
        d = 160 + i * 80
        E += [box("%s tile" % side, x, Y + 4, 150, Hh - 8, None, A("wipe-right", 300, d), bg=T["team"](side), radius=max(0, T["r"] - 2))]
        E += logo_or_abbr("%s logo" % side, x + 4, Y + 8, 44, Hh - 16, side, 16, A("fade", 260, d + 100), S={"font": F})
        E += [W(T, "%s abbr" % side, x + 52, Y + 4, 96, Hh - 8, "{%s.abbr}" % side, 28, A("fade", 260, d + 120), font=H),
              box("%s score bg" % side, x + 154, Y + 4, 64, Hh - 8, None, A("fade", 260, d + 60), bg=T["val"], radius=max(0, T["r"] - 2)),
              W(T, "%s runs" % side, x + 154, Y + 4, 64, Hh - 8, "{%s.runs}" % side, 36, A("reveal-up", 300, d + 160, change="pop"), align="center",
                color=T["valText"], font=H)]
        x += 224
    E += [W(T, "Inning", x, Y, 90, Hh, "{arrow}{inning}", 28, A("fade", 240, 400, change="roll"), show=LIVE, align="center", font=H),
          el("bases", "Bases", x + 90, Y + 6, 76, Hh - 12, A("pop", 320, 420), show=LIVE, bind="bases",
             style={"layout": "tight", "on": T["base_on"], "off": T["base_off"], "stroke": "#00000066", "strokeW": 2}),
          W(T, "Count", x + 166, Y + 2, 96, 34, "{balls}-{strikes}", 26, A("fade", 240, 440, change="flash"), show=LIVE, align="center", font=H),
          el("dots", "Outs", x + 166, Y + 36, 96, 18, A("fade", 240, 460), show=LIVE, bind="outs",
             style={"total": 3, "size": 11, "gap": 8, "on": T["hi"], "off": "#FFFFFF@0.22", "shape": T.get("dot_shape", "circle"), "align": "center"}),
          W(T, "Status", x, Y, 300, Hh, "{statusText}", 22, A("fade", 240, 360), show="!" + LIVE, align="center", font=H),
          box("Pitcher bar", X, Y + Hh + 4, 420, 32, None, A("wipe-down", 300, 500, out=OUT_), bg=T["dark"], radius=T["r"], show=LIVE),
          W(T, "Pitcher", X + 12, Y + Hh + 4, 300, 32, up(T, "{pitcher.name|initial}"), 19, A("fade", 240, 600, change="fade"), show=LIVE),
          W(T, "Pitch count", X + 300, Y + Hh + 4, 108, 32, "P: {pitcher.today.pc|zero}", 19, A("fade", 240, 620, change="flash"), show=LIVE, align="right",
            color=T["hi"])]
    E += call(T, "bug_decor", X, Y, 760, Hh)
    E += BL.sponsor_tab(X + 430, Y + Hh + 4, 300, 34, 700, radius=T["r"], a_type="wipe-down")
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(T, kind):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    cols = ([("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
             ("K", "{pitcher.season.k|zero}")] if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}"), ("OPS", "{batter.season.ops|avg}")])
    X, Y, Hh = 360, 872, 90
    TL, NP, SW = 106, 560, 460
    Wd = TL + NP + SW
    E = call(T, "lt_under", X, Y, Wd, Hh)
    E += [box("Tile", X, Y, TL, Hh, None, A("wipe-right", 320, 0, out=OUT_), bg=T["team"](team), radius=T["r"], borderW=2, borderColor=T["tile_border"],
              shadow=T["shadow"])]
    E += logo_or_abbr("Logo", X + 10, Y + 10, TL - 20, Hh - 20, team, 30, A("zoom-out", 340, 160), S={"font": F})
    x = X + TL + 4
    E += [box("Plate", x, Y, NP, Hh, None, A("wipe-right", 380, 120, out=OUT_), bg=T["strip"], radius=T["r"], shadow=T["shadow"]),
          W(T, "Number", x + 14, Y, 70, Hh, "{%s.number}" % who, 40, A("fade", 240, 300), color=T["hi"] if T.get("num_hi") else T["stripText"], font=H,
            align="center"),
          W(T, "First", x + 96, Y + 8, NP - 120, 30, up(T, "{%s.first}" % who), 24, A("fade", 260, 380), color=T["stripText"], weight=600),
          W(T, "Last", x + 94, Y + 36, NP - 120, 50, up(T, "{%s.last}" % who), 42, A("reveal-up", 320, 360), color=T["stripText"], font=H),
          W(T, "Pos", x + NP - 110, Y + 8, 96, 30, "{%s.pos}" % who if kind == "bat" else "{pitcher.throws|hand}", 20, A("fade", 240, 420),
            color=T["stripText"], align="right", weight=700)]
    x += NP + 4
    E += [box("Stats", x, Y, SW, Hh, None, A("wipe-right", 400, 260, out=OUT_), bg=T["panel"], radius=T["r"], borderW=2, borderColor=T["edge"],
              shadow=T["shadow"])]
    cw = SW // 4
    for i, (lab, val) in enumerate(cols):
        E += [W(T, "%s label" % lab, x + i * cw, Y + 8, cw, 26, lab, 20, A("fade", 240, 420 + i * 50), align="center", color=T["dim"], weight=700),
              W(T, "%s value" % lab, x + i * cw, Y + 34, cw, 48, val, 38, A("reveal-up", 300, 440 + i * 50, change="flash"), align="center", font=H)]
    E += [box("Note row", X + TL + 4, Y + Hh + 4, NP + 4 + SW, 32, None, A("wipe-down", 280, 600, out=OUT_), bg=T["dark"], radius=T["r"], show="notes.stat"),
          W(T, "Note", X + TL + 18, Y + Hh + 4, NP + SW - 24, 32, up(T, "{notes.stat}"), 19, A("fade", 240, 680), show="notes.stat", color=T["hi"])]
    E += call(T, "lt_decor", X, Y, Wd, Hh)
    E += BL.sponsor_tab(X + TL + 4, Y - 46, 300, 40, 640, radius=T["r"], a_type="wipe-up")
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


# ------------------------------------------------------------------ open, stinger, card
def show_open(T):
    E = backdrop(T) + call(T, "open_decor")
    E += [D_(T, "Show", 160, 300, 1600, 260, "{show.name}" if not T["upper"] else "{show.name|upper}", 150, A("zoom-out", 700, 600), align="center",
             wrap=True, fit=True, lineH=0.95),
          W(T, "Kicker", 160, 230, 1600, 60, T["open_kicker"] or "{seasonYear}", 40, A("fade", 500, 400), align="center", color=T["hi"], tracking=8, font=H)]
    for i, side in enumerate(("away", "home")):
        x = 360 if i == 0 else 1260
        E += logo_or_abbr("%s logo" % side, x, 620, 300, 260, side, 90, A("pop", 500, 1000 + i * 150), S={"font": H})
    E += [D_(T, "Vs", 760, 680, 400, 140, "VS", 90, A("pop", 400, 1300), align="center"),
          W(T, "Matchup", 160, 900, 1600, 60, up(T, "{away.nick} at {home.nick}"), 40, A("fade", 400, 1400), align="center"),
          W(T, "Venue", 160, 960, 1600, 50, up(T, "{venue}"), 30, A("fade", 400, 1500), align="center", color=T["dim"])]
    return {"name": "Show Open", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "open, show"}


def hr_stinger(T):
    E = call(T, "hr_under")
    E += [box("Band", 0, 330, 1920, 420, None, A("wipe-center", 360, 0, out=OUT_), bg=T.get("hr_band") or T["team"]("batting"))]
    if T["texture"]:
        E.append(box("Band texture", 0, 330, 1920, 420, None, A("fade", 300, 120), bg=T["texture"]))
    E += call(T, "hr_decor")
    E += [D_(T, "Word", 60, 360, 1800, 270, T["hr_word"], 220, A(T.get("hr_anim", "zoom-out"), 520, 250, loop=T.get("hr_loop")), align="center",
             color=T["word_color"], **({"textStroke": T["word_stroke"]} if T.get("word_stroke") else {})),
          W(T, "Batter", 60, 640, 1800, 90, up(T, "{batter.name}"), 64, A("reveal-up", 400, 700), align="center", font=H,
            color=T.get("hr_name_color") or T["text"])]
    return {"name": "Home Run Stinger", "group": "full", "autoHide": 5, "side": "", "sided": False, "elements": E}


def player_card(T, kind="bat"):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    E = backdrop(T)
    E += [box("Photo field", 120, 140, 700, 800, None, A("wipe-up", 460, 200), bg=T["team"](team), radius=T["r"], borderW=4, borderColor=T["edge"],
              shadow=T["shadow"]),
          img("Photo", 120, 160, 700, 780, "{%s.photo}" % who, A("fade", 500, 450), show="%s.photo" % who, fit="contain", focus="center bottom"),
          W(T, "Number", 120, 160, 700, 780, "{%s.number}" % who, 360, A("fade", 400, 450), show="!%s.photo" % who, align="center", color="#FFFFFF@0.3",
            font=H, fit=False),
          box("Name plate", 80, 860, 780, 120, None, A("wipe-right", 380, 600), bg=T["strip"], radius=T["r"], shadow=T["shadow"]),
          W(T, "Name", 80, 860, 780, 120, up(T, "{%s.name}" % who), 64, A("reveal-up", 360, 720), align="center", color=T["stripText"], font=H),
          D_(T, "Title", 900, 120, 920, 120, up(T, "{seasonYear} season"), 80, A("slide-left", 420, 400, dist=40),
             **({} if T.get("deco_digits", True) else {"font": H})),
          box("Panel", 900, 260, 920, 640, None, A("wipe-left", 460, 300), bg=T["panel"], radius=T["r"], borderW=2, borderColor=T["edge"],
              shadow=T["shadow"]),
          el("table", "Rows", 940, 290, 840, 580, A("none", 1, 0, rows={"type": "slide-left", "dur": 340, "stagger": 70, "delay": 700, "dist": 30}),
             bind="%s.card" % who,
             columns=[{"label": "", "field": "{row.label|upper}" if T["upper"] else "{row.label}", "w": 2, "align": "left", "weight": 800},
                      {"label": "", "field": "value", "w": 1, "align": "right", "weight": 800}],
             style={"rowH": 94, "size": 48, "weight": 800, "color": T["text"], "header": False, "padX": 0, "gap": 0, "maxRows": 6, "font": H}),
          W(T, "Foot", 900, 920, 920, 60, up(T, "{notes.foot}"), 32, A("fade", 300, 1200), show="notes.foot", align="center", color=T["hi"])]
    E += call(T, "screen_over")
    return {"name": "%s Card" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "pickable": True}


# ------------------------------------------------------------------ assemble
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")


def build(T0):
    T = defaults(T0)
    key = T["key"]
    S = dict(BL.NETWORK, key=key, font=F, body=F, up=T["upper"], radius=T["r"], cardRadius=T["r"] + 2, panel=T["panel"], panel2=T["panel2"],
             dark=T["dark"], strip=T["strip"], stripText=T["stripText"], val=T["val"], valText=T["valText"], hi=T["hi"], hiText=T["hiText"],
             line=T["line"], shadow=T["shadow"], cardIn="zoom-out", teamGrad=team_v("%s").replace("%s", "%s"), titleBg=T["title"])
    S["teamGrad"] = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 80%%, #fff) 0%%, {%s.color} 50%%, "
                     "color-mix(in srgb, {%s.color} 66%%, #000) 100%%)")
    night = NIGHT_DOC["graphics"]
    g = {}
    MS = dict(S, **SK.MARKS)
    for gid, gdef in BL.all_new(MS).items():
        if gid.startswith("c_") or gid in SKIP:
            continue
        g[gid] = gdef
    for gid in ("dueup", "inning_sponsor", "lineup", "pitching", "defense", "linescore", "spotlight", "note", "matchup", "standings", "custom",
                "stinger", "opener"):
        g[gid] = copy.deepcopy(night[gid])
    g.update(SL.all_sports(MS))
    custom = {"scorebug": scorebug(T), "batter": lower(T, "bat"), "pitcher": lower(T, "pit"), key + "_open": show_open(T), key + "_hr": hr_stinger(T),
              "batter_card": (T["card"](T, "bat") if T.get("card") else player_card(T, "bat")),
              "pitcher_card": (T["card"](T, "pit") if T.get("card") else player_card(T, "pit"))}
    if T.get("extras"):
        custom.update({(gid if gid.startswith(key + "_") else key + "_" + gid): gd for gid, gd in T["extras"](T).items()})
    if T.get("override"):
        custom.update(T["override"](T))
    g.update(custom)
    CUSTOM = set(custom)

    def kit_tr(gid, g_, TA):
        E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=T["title"])]
        if T["texture"]:
            E.append(box("Texture", 0, 0, 1920, 1080, None, TA("fade", 400, 80), bg=T["texture"]))
        E += [box("Band", 0, 400, 1920, 260, None, TA("wipe-right", 420, 120), bg=T.get("tr_band") or T["panel"]),
              box("Rule top", 0, 394, 1920, 6, T["rule"], TA("grow-x", 360, 200)),
              box("Rule bottom", 0, 660, 1920, 6, T["rule"], TA("grow-x", 360, 240))]
        E += [dict(e) for e in call(T, "tr_decor", TA)]
        return {"elements": E, "word": {"font": T["deco"], "weight": 900, "color": T.get("tr_word") or T["word_color"], "textShadow": T["glow"],
                         **({"textStroke": T["word_stroke"]} if T.get("word_stroke") else {}), "rect": (60, 410, 1800, 190)},
                "sub": {"font": F, "weight": 800, "color": T["hi"], "textShadow": "", "rect": (60, 690, 1800, 80), "tracking": 3},
                "brand": {"rect": (860, 160, 200, 180)}}

    def kit_slab(R, slab, g_):
        x, y, w, h = R
        E = [box("Rule top", 0, y - 6, 1920, 6, T["rule"], A("grow-x", 300, 100)), box("Rule bottom", 0, y + h, 1920, 6, T["rule"], A("grow-x", 300, 140))]
        if T["texture"]:
            E.append(dict(box("Texture", 0, y, 1920, h, None, A("fade", 300, 200), bg=T["texture"]), _over=True))
        return E

    def kit_screen(bg, team, g_):
        over = []
        if T["texture"]:
            over.append(box("Texture", 0, 0, 1920, 1080, None, A("fade", 500, 100), bg=T["texture"]))
        over += call(T, "screen_over")
        return {"floor": T["panel2"], "replace": T["title"], "over": over}

    KIT = RB.make_kit(dict(
        screen=kit_screen, slab=kit_slab,
        body=T["panel"], bodyBox={"radius": T["r"], "borderW": 2, "borderColor": T["edge"], "shadow": T["shadow"]},
        headTile=lambda t: T["team"](t) if t else T["dark"], head=T.get("head") or T["dark"], headRule=T["rule"], sub=T.get("sub") or T["panel2"],
        title={"font": T.get("head_font", H), "weight": 900, "color": T.get("head_text") or T["title_color"], "textShadow": T["glow"], "italic": False},
        headText={"textShadow": ""}, subText={"font": F, "weight": 700, "color": T["dim"], "textShadow": "", "tracking": 1},
        roles={"PANEL": T["panel"], "PANEL2": T["panel2"], "DARK": T["dark"], "STRIP": T["strip"]}, barBox={"radius": T["r"]},
        mainBox={"shadow": T["shadow"]}, tile={"radius": T["r"], "borderW": 2, "borderColor": T["tile_border"]}, tr=kit_tr))
    SKIN = dict(panel=T["panel"], panel2=T["panel2"], dark=T["dark"], strip=T["strip"], stripText=T["stripText"], val=T["val"], ink=T["ink"], hi=T["hi"],
                hiText=T["hiText"], hiDark=T.get("hiDark", True), line=T["line"], title=T["title"], shadow=T["shadow"], team=T["team"], rule=T["rule"],
                text2=T["text"], radius=T["r"], noBlur=True,
                panelBox={"radius": T["r"], "borderW": 2, "borderColor": T["edge"], "shadow": T["shadow"]}, lightBox={"radius": T["r"]},
                hiBox={"radius": T["r"]}, text={"textShadow": ""}, textDark={"textShadow": ""})
    g = RB.rebuild_all(g, KIT, only=set(g) - CUSTOM)
    g = RB.strip_flags(SK.skin_all(g, SKIN, only=set(g) - CUSTOM))
    for gid in BL.PICKABLE:
        if gid in g:
            g[gid]["pickable"] = True
    for gid, slot in BL.SPONSOR_SLOTS.items():
        if gid in g:
            g[gid].setdefault("sponsorSlot", slot)
    for k, d in g.items():
        if not d.get("layout") and T["name"] not in d.get("name", ""):
            d["name"] = "%s (%s)" % (d.get("name", k), T["name"])
    theme = dict(NIGHT_DOC["theme"])
    theme.update({"primary": T.get("primary") or T["bg"], "accent": T["hi"], "text": T["text"], "dim": T.get("dim_rgba", "rgba(255,255,255,0.75)"),
                  "line": "rgba(255,255,255,0.16)", "card": T.get("card_rgba", "rgba(14,14,16,0.95)"), "panel": T.get("card_rgba", "rgba(14,14,16,0.95)"),
                  "panel2": T.get("panel2_rgba", "rgba(38,39,44,0.95)"), "font": T["font"], "font2": T["font2"]})
    doc = {"version": 2, "name": T["name"], "description": T["desc"], "theme": theme, "graphics": g}
    out = os.path.join(ROOT, "templates", "packages", "%s.json" % T["file"])
    BL.stamp(doc)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, separators=(",", ":"))
    print("wrote", out, "graphics:", len(g), "custom:", len(CUSTOM))
    return out
