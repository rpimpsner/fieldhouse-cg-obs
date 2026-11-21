"""Builds the "Winter Ball" package: templates/packages/winter-ball.json.

Modelled on the layout of a winter-league TV broadcast Rob sent: a black-framed corner scorebug with the batter and his
line across the top, team-colour rows with the logo and a white score box, an inning column with up / down arrows, bases,
count and red out dots on the right, the pitcher and pitch count across the bottom; and a lower third made of a
team-colour logo tile, a light gray name bar (number, NAME, position) and a dark end tab. No network or league marks
are included; logos come from your own team settings. Every other graphic type is drawn in the same language.
Run:  python tools/build_winter.py   (after tools/build_night_game.py)
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
from broadcast_lib import A, box, txt, img, el, both, logo_or_abbr  # noqa: E402

BLACK = "#0B0C0E"
FRAME = "linear-gradient(180deg, #1A1C20 0%, #0B0C0E 100%)"
PANEL = "linear-gradient(180deg, #22252A 0%, #121418 100%)"
PANEL2 = "linear-gradient(180deg, #2C2F35 0%, #1A1C20 100%)"
LIGHT = "linear-gradient(180deg, #FAFBFC 0%, #E6E8EC 55%, #CDD1D7 100%)"
SCORE = "linear-gradient(180deg, #FFFFFF 0%, #E9EBEE 100%)"
INK = "#14161A"
RED = "#E3262F"
GRAY = "#9AA0A8"
EDGE = "#2C2F35"
SHADOW = "0 8px 22px rgba(0,0,0,.55)"
TEAM = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 82%%, #fff) 0%%, {%s.color} 48%%, "
        "color-mix(in srgb, {%s.color} 70%%, #000) 100%%)")
F = "$font"
LIVE = "inPlay"
OUT_ = {"type": "fade", "dur": 240, "delay": 0, "ease": "in"}

WB = dict(BL.NETWORK, key="winter", font=F, body=F, up=True, radius=4, cardRadius=6,
          panel=PANEL, panel2=PANEL2, dark=BLACK, strip=LIGHT, stripText=INK, val=SCORE, valText=INK,
          hi=RED, hiText="#FFFFFF", line="#FFFFFF@0.16", shadow=SHADOW, cardIn="wipe-right",
          teamGrad=TEAM, titleBg="radial-gradient(ellipse at 70% 30%, #2C2F35, #121418 55%, #050506)")


def T(team):
    return TEAM % (team, team, team)


def W(name, x, y, w, h, text, size, a, show=None, **st):
    st.setdefault("font", F)
    st.setdefault("weight", 800)
    return txt(name, x, y, w, h, text, size, a, show=show, **st)


def K_(name, x, y, w, h, text, size, a, show=None, **st):
    st.setdefault("color", INK)
    return W(name, x, y, w, h, text, size, a, show=show, **st)


# ------------------------------------------------------------------ scorebug
def scorebug():
    X, Y, Wd = 40, 36, 474
    TOP, RH, BOT = 34, 58, 34
    y0 = Y + TOP
    E = [box("Frame", X, Y, Wd, TOP + 2 * RH + BOT, None, A("wipe-right", 420, 0, out={"type": "wipe-left", "dur": 300, "delay": 120, "ease": "in"}),
             bg=FRAME, radius=6, borderW=2, borderColor=EDGE, shadow=SHADOW),
         # batter and his line today across the top
         W("Batter", X + 12, Y, 300, TOP, "{batter.name|upper}", 20, A("fade", 240, 300, change="fade"), show=LIVE),
         W("Batter today", X + Wd - 112, Y, 100, TOP, "{batter.today.hab}", 20, A("fade", 240, 320, change="flash"), show=LIVE, align="right"),
         W("Top status", X + 12, Y, Wd - 24, TOP, "{statusText}", 20, A("fade", 240, 300), show="!" + LIVE)]
    for i, side in enumerate(("away", "home")):
        y = y0 + i * RH
        d = 160 + i * 80
        E += [box("%s color" % side, X + 4, y + 2, 196, RH - 4, None, A("wipe-right", 360, d), bg=T(side), radius=2)]
        E += logo_or_abbr("%s logo" % side, X + 14, y + 6, 176, RH - 12, side, 34, A("fade", 260, d + 160), S=WB)
        E += [box("%s score bg" % side, X + 202, y + 2, 74, RH - 4, None, A("fade", 260, d + 100), bg=SCORE, radius=2),
              K_("%s runs" % side, X + 202, y + 2, 74, RH - 4, "{%s.runs}" % side, 44, A("reveal-up", 300, d + 200, change="pop"), align="center")]
    E += [box("Row rule", X + 202, y0 + RH - 1, 74, 2, "#B9BEC6", A("grow-x", 260, 300))]
    # inning column: up arrow, number, down arrow (the current half lights red)
    ix = X + 280
    E += [W("Up on", ix, y0 + 2, 52, 34, "▲", 22, A("fade", 220, 420), show=both(LIVE, "half==top"), color=RED, align="center"),
          W("Up off", ix, y0 + 2, 52, 34, "▲", 22, A("fade", 220, 420), show=both(LIVE, "half!=top"), color="#FFFFFF@0.25", align="center"),
          W("Inning", ix, y0 + 30, 52, 56, "{inning}", 42, A("fade", 240, 440, change="roll"), show=LIVE, align="center"),
          W("Down on", ix, y0 + 2 * RH - 36, 52, 34, "▼", 22, A("fade", 220, 460), show=both(LIVE, "half==bottom"), color=RED, align="center"),
          W("Down off", ix, y0 + 2 * RH - 36, 52, 34, "▼", 22, A("fade", 220, 460), show=both(LIVE, "half!=bottom"), color="#FFFFFF@0.25",
            align="center"),
          box("Divider", ix + 54, y0 + 8, 2, 2 * RH - 16, "#FFFFFF@0.18", A("grow-y", 260, 400))]
    # bases, count and outs
    rx = ix + 60
    rw = X + Wd - rx - 6
    E += [el("bases", "Bases", rx + 8, y0 + 6, rw - 16, 60, A("pop", 320, 480), show=LIVE, bind="bases",
             style={"on": "#FFFFFF", "off": "transparent", "stroke": "#FFFFFF", "strokeW": 3}),
          W("Count", rx, y0 + 68, rw // 2 + 6, 40, "{balls}-{strikes}", 30, A("fade", 240, 520, change="flash"), show=LIVE, align="center"),
          el("dots", "Outs", rx + rw // 2, y0 + 76, rw // 2, 24, A("fade", 240, 540), show=LIVE, bind="outs",
             style={"total": 2, "size": 16, "gap": 8, "on": RED, "off": "#FFFFFF@0.25", "shape": "circle", "align": "center"}),
          W("Status", ix, y0, X + Wd - ix, 2 * RH, "{statusText}", 26, A("fade", 240, 460), show="!" + LIVE, align="center", wrap=True, fit=False)]
    # pitcher and pitch count across the bottom
    by = y0 + 2 * RH
    E += [box("Bottom rule", X + 6, by, Wd - 12, 1, "#FFFFFF@0.14", A("grow-x", 260, 500)),
          W("Pitcher", X + 12, by, 320, BOT, "{pitcher.name|upper}", 20, A("fade", 240, 560, change="fade"), show=LIVE),
          W("Pitch count", X + Wd - 112, by, 100, BOT, "P-{pitcher.today.pc|zero}", 20, A("fade", 240, 580, change="flash"), show=LIVE,
            align="right")]
    E += BL.sponsor_tab(X, Y + TOP + 2 * RH + BOT + 8, 300, 40, 700, radius=4, a_type="wipe-down")
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(kind):
    """Team-colour logo tile, light gray name bar (number, NAME, position), dark end tab, a dark stat row under it."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    tag = "{pitcher.throws|hand}" if kind == "pit" else "{batter.pos}"
    stats = ("TODAY  {pitcher.today.line|upper}     ERA {pitcher.season.era|era}   W-L {pitcher.season.w|zero}-{pitcher.season.l|zero}   SO {pitcher.season.k|zero}"
             if kind == "pit" else
             "TODAY  {batter.today.line|upper}     AVG {batter.season.avg|avg}   HR {batter.season.hr|zero}   RBI {batter.season.rbi|zero}")
    X, Y, TL, BW, TB, H = 360, 870, 150, 860, 150, 96
    E = [box("Tile", X, Y, TL, H + 14, None, A("wipe-right", 380, 0, out=OUT_), bg=T(team), radius=2, shadow=SHADOW)]
    E += logo_or_abbr("Logo", X + 12, Y + 8, TL - 24, H - 2, team, 40, A("zoom-out", 380, 180), S=WB)
    E += [box("Bar", X + TL, Y + 7, BW, H, None, A("wipe-right", 440, 120, out=OUT_), bg=LIGHT, shadow=SHADOW),
          K_("Number", X + TL + 22, Y + 7, 100, H, "#{%s.number}" % who, 40, A("fade", 260, 380), show="%s.number" % who),
          K_("Name", X + TL + 128, Y + 7, BW - 330, H, "{%s.name|upper}" % who, 48, A("reveal-up", 360, 360)),
          K_("Position", X + TL + BW - 190, Y + 7, 170, H, tag, 40, A("fade", 260, 440), align="center"),
          box("End tab", X + TL + BW, Y + 7, TB, H, "#000000@0.72", A("wipe-right", 360, 260, out=OUT_)),
          img("Sponsor", X + TL + BW + 12, Y + 17, TB - 24, H - 20, "{sponsor.logo}", A("fade", 300, 600, change="fade"), show="sponsor.on && sponsor.logo"),
          W("Sponsor name", X + TL + BW + 6, Y + 7, TB - 12, H, "{sponsor.name|upper}", 22, A("fade", 300, 600, change="fade"),
            show="sponsor.on && !sponsor.logo", align="center", wrap=True, fit=False),
          box("Stat row", X + TL, Y + 7 + H, BW + TB, 40, BLACK + "@0.86", A("wipe-down", 320, 420, out=OUT_)),
          box("Stat accent", X + TL, Y + 7 + H, 6, 40, RED, A("grow-y", 260, 500)),
          W("Stats", X + TL + 22, Y + 7 + H, BW + TB - 40, 40, stats, 22, A("fade", 260, 560, change="flash"), color="#FFFFFF")]
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def custom_lower():
    X, Y, TL, BW, H = 360, 880, 150, 1010, 96
    E = [box("Tile", X, Y, TL, H, None, A("wipe-right", 380, 0, out=OUT_), bg=PANEL, radius=2, shadow=SHADOW),
         img("Brand", X + 14, Y + 10, TL - 28, H - 20, "{brand.logo}", A("zoom-out", 380, 180), show="brand.logo"),
         img("League", X + 14, Y + 10, TL - 28, H - 20, "{league.logo}", A("zoom-out", 380, 180), show="!brand.logo && league.logo"),
         box("Bar", X + TL, Y, BW, H, None, A("wipe-right", 440, 120, out=OUT_), bg=LIGHT, shadow=SHADOW),
         K_("Line 1", X + TL + 24, Y, BW - 48, H, "{custom.line1|upper}", 44, A("reveal-up", 360, 360)),
         box("Row", X + TL, Y + H, BW, 40, BLACK + "@0.86", A("wipe-down", 320, 420, out=OUT_), show="custom.line2"),
         box("Row accent", X + TL, Y + H, 6, 40, RED, A("grow-y", 260, 500), show="custom.line2"),
         W("Line 2", X + TL + 22, Y + H, BW - 40, 40, "{custom.line2|upper}", 22, A("fade", 260, 560), show="custom.line2")]
    return {"name": "Custom Lower Third", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(WB, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("dueup", "inning_sponsor", "lineup", "pitching", "defense", "linescore", "spotlight", "note", "matchup", "standings", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g["batter_card"] = BL.stat_card_tonight(MS, "bat")
g["pitcher_card"] = BL.stat_card_tonight(MS, "pit")
g.update({"scorebug": scorebug(), "batter": lower("bat"), "pitcher": lower("pit"), "custom": custom_lower()})
g.update(SL.all_sports(MS))
CUSTOM = ("scorebug", "batter", "pitcher", "custom")


def kit_tr(gid, g_, TA):
    """Black field; team-colour logo tile, light gray word bar and a black row with a red edge, like the lower thirds."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=WB["titleBg"]),
         box("Logo tile", 160, 380, 300, 300, None, TA("pop", 400, 120), bg=T("team"), shadow=SHADOW),
         box("Bar", 460, 380, 1300, 200, None, TA("wipe-right", 440, 160), bg=LIGHT, shadow=SHADOW),
         box("Row", 460, 580, 1300, 100, None, TA("wipe-right", 420, 240), bg=BLACK),
         box("Row accent", 460, 580, 10, 100, RED, TA("grow-y", 300, 320))]
    return {"elements": E, "word": {"font": F, "weight": 800, "color": INK, "textShadow": "", "rect": (500, 380, 1230, 200), "align": "left"},
            "sub": {"font": F, "weight": 700, "color": "#FFFFFF", "textShadow": "", "rect": (500, 580, 1230, 100), "align": "left", "tracking": 1},
            "brand": {"rect": (190, 410, 240, 240)}}


def kit_slab(R, slab, g_):
    x, y, w, h = R
    return [box("Frame", 0, y - 8, 1920, h + 16, BLACK, A("wipe-right", 300, 0)),
            dict(box("Accent", 0, y + h - 8, 1920, 8, RED, A("grow-x", 300, 200)), _over=True)]


def kit_screen(bg, team, g_):
    over = [box("Frame", 0, 0, 1920, 1080, None, A("fade", 300, 0), borderW=12, borderColor=BLACK),
            box("Accent", 0, 1068, 1920, 12, RED, A("grow-x", 380, 160))]
    return {"floor": PANEL2, "replace": WB["titleBg"], "over": over}


KIT = RB.make_kit(dict(
    screen=kit_screen, slab=kit_slab,
    body=PANEL, bodyBox={"radius": 6, "borderW": 2, "borderColor": EDGE, "shadow": SHADOW},
    headTile=lambda t: T(t) if t else BLACK, head=LIGHT, headBox={"shadow": SHADOW}, headRule=RED, sub=BLACK,
    title={"font": F, "weight": 800, "color": INK, "textShadow": "", "italic": False},
    headText={"color": "#3A3F47", "textShadow": ""}, subText={"font": F, "weight": 800, "color": GRAY, "textShadow": "", "tracking": 1},
    roles={"PANEL": PANEL, "PANEL2": PANEL2, "DARK": BLACK, "STRIP": LIGHT}, barBox={"radius": 2}, mainBox={"shadow": SHADOW},
    tile={"radius": 2, "borderW": 0}, tr=kit_tr))
SKIN = dict(panel=PANEL, panel2=PANEL2, dark=BLACK, strip=LIGHT, stripText=INK, val=SCORE, ink=INK, hi=RED, hiText="#FFFFFF", line="#FFFFFF@0.14",
            title=WB["titleBg"], shadow=SHADOW, team=T, rule=RED, text2="#FFFFFF", radius=2, noBlur=True,
            panelBox={"radius": 6, "borderW": 2, "borderColor": EDGE, "shadow": SHADOW}, lightBox={"radius": 2}, hiBox={"radius": 2},
            text={"textShadow": ""}, textDark={"textShadow": ""})
g = RB.rebuild_all(g, KIT, only=set(g) - set(CUSTOM))
g = RB.strip_flags(SK.skin_all(g, SKIN, only=set(g) - set(CUSTOM)))
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
for k, d in g.items():
    if not d.get("layout") and "Winter Ball" not in d.get("name", ""):
        d["name"] = "%s (Winter Ball)" % d.get("name", k)

theme = dict(night_doc["theme"])
COND = night_doc["theme"]["font2"]
theme.update({"primary": BLACK, "accent": RED, "text": "#FFFFFF", "dim": "rgba(255,255,255,0.72)", "line": "rgba(255,255,255,0.16)",
              "card": "rgba(18,20,24,0.95)", "panel": "rgba(18,20,24,0.95)", "panel2": "rgba(34,37,42,0.95)", "font": COND, "font2": COND})
doc = {"version": 2, "name": "Winter Ball",
       "description": "Winter-league TV look: black-framed corner scorebug (batter and line on top, team-colour rows with logos and white score "
                      "boxes, inning arrows, bases, count, red out dots, pitcher and pitch count below), team-tile lower thirds with a light gray "
                      "name bar and a dark end tab, condensed type. Every graphic type, plus basketball, football and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "winter-ball.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
