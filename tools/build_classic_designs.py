"""Builds the "Classic Frame" package: templates/packages/classic-designs.json.

Rob's own Classic designs (black-frame scorebug with pitch info, gray name bar lower thirds with a dark stat row,
team intro, league bug) as a complete style: every other graphic type is drawn in the same language
(team-colour tiles, light gray bars with dark ink, dark stat rows with gray labels, a black frame).
Run:  python tools/build_classic_designs.py   (after tools/build_night_game.py)
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
from broadcast_lib import A, box, txt, img, el, both, logo_or_abbr, sponsor_tab, C_GRAY, C_DARK, C_INK, C_LABEL, C_TEAM, C_TEAM2  # noqa: E402

CL = dict(BL.NETWORK, key="classic", font="$font", body="$font", up=False, radius=2, cardRadius=3,
          panel=C_DARK, panel2="linear-gradient(180deg, #25282E 0%, #141619 100%)", dark="#050506",
          strip=C_GRAY, stripText=C_INK, val=C_GRAY, valText=C_INK, hi="$accent", hiText="#111214", line="#FFFFFF@0.14",
          shadow="0 12px 30px rgba(0,0,0,.5)", cardIn="zoom-out",
          teamGrad=("linear-gradient(180deg, color-mix(in srgb, {%s.color} 72%%, #fff) 0%%, {%s.color} 55%%, "
                    "color-mix(in srgb, {%s.color} 72%%, #000) 100%%)"),
          titleBg="radial-gradient(ellipse at 70% 30%, #34383F, #17191D 55%, #050506)")
F = CL["font"]
OUT_ = {"type": "fade", "dur": 260, "delay": 0, "ease": "in"}
LIVE = "inPlay"


def due_up():
    """Logo tile and gray "Due Up" bar, then the next three hitters on dark rows."""
    X, Y, T, W = 70, 700, 172, 760
    E = [box("Logo tile", X, Y, T, 100, None, A("pop", 420, 0, out=OUT_), bg=C_TEAM("team"), shadow=CL["shadow"])]
    E += logo_or_abbr("Logo", X + 14, Y + 10, T - 28, 80, "team", 40, A("zoom-out", 400, 160), S=CL)
    E += [box("Head", X + T, Y, W - T, 100, None, A("wipe-right", 420, 120, out=OUT_), bg=C_GRAY, shadow=CL["shadow"]),
          txt("Team", X + T + 26, Y + 8, W - T - 50, 30, "{team.name|upper}", 24, A("fade", 260, 380), font=F, weight=800, color="#4B5059", tracking=1),
          txt("Due up", X + T + 24, Y + 32, W - T - 50, 64, "Due Up", 56, A("reveal-up", 360, 360), font=F, weight=800, color=C_INK, lineH=1)]
    for i in range(3):
        p = "team.dueUp.%d" % i
        y = Y + 100 + i * 72
        d = 420 + i * 110
        E += [box("Row %d" % i, X, y, W, 72, None, A("wipe-right", 380, d, out=OUT_), show=p + ".name", bg=C_DARK),
              txt("Slot %d" % i, X, y, 90, 72, "{%s.slot}" % p, 40, A("fade", 240, d + 120), show=p + ".name", font=F, weight=800, align="center",
                  color="$accent"),
              img("Photo %d" % i, X + 90, y + 4, 64, 64, "{%s.photo}" % p, A("fade", 240, d + 140), show=both(p + ".name", p + ".photo"), fit="cover",
                  focus="center top"),
              txt("Name %d" % i, X + 170, y, 400, 72, "{%s.name}" % p, 36, A("reveal-up", 300, d + 140), show=p + ".name", font=F, weight=800),
              txt("Today %d" % i, X + 560, y + 4, 90, 30, "TODAY", 16, A("fade", 240, d + 180), show=both(p + ".name", p + ".today"), font=F, weight=700,
                  color=C_LABEL, align="center", tracking=1),
              txt("Today v %d" % i, X + 560, y + 30, 90, 38, "{%s.today}" % p, 26, A("fade", 240, d + 200), show=both(p + ".name", p + ".today"), font=F,
                  weight=800, align="center"),
              txt("Avg l %d" % i, X + 660, y + 4, 90, 30, "AVG", 16, A("fade", 240, d + 180), show=p + ".name", font=F, weight=700, color=C_LABEL,
                  align="center", tracking=1),
              txt("Avg %d" % i, X + 660, y + 30, 90, 38, "{%s.avg|avg}" % p, 28, A("fade", 240, d + 200), show=p + ".name", font=F, weight=800,
                  align="center")]
    E += sponsor_tab(X + W - 300, Y - 50, 300, 44, 600, radius=2, a_type="wipe-up")
    return {"name": "Due Up (Classic)", "group": "lower", "autoHide": 0, "side": "batting", "sided": True, "elements": E,
            "sponsorSlot": "half_{halfKey}, dueup"}


def linescore():
    """Black frame: team tiles, dark inning cells, gray R H E boxes."""
    CW, TW, RW, RH = 70, 200, 86, 66
    W = 8 + TW + 9 * CW + 3 * RW
    X, Y = (1920 - W) // 2, 820
    E = [box("Frame", X, Y, W, 38 + 2 * RH + 8, "#050506", A("wipe-up", 420, 0), radius=3, shadow=CL["shadow"]),
         txt("Status", X + 14, Y, TW, 38, "{statusText}", 20, A("fade", 240, 200), font=F, weight=800, color="$accent")]
    for i in range(9):
        E.append(txt("Inn %d" % (i + 1), X + 4 + TW + i * CW, Y, CW, 38, str(i + 1), 20, A("fade", 240, 220 + i * 20), font=F, weight=800,
                     align="center", color=C_LABEL))
    for j, lab in enumerate(("R", "H", "E")):
        E.append(txt("Head " + lab, X + 4 + TW + 9 * CW + j * RW, Y, RW, 38, lab, 22, A("fade", 240, 420), font=F, weight=800, align="center",
                     color="#FFFFFF"))
    for r, side in enumerate(("away", "home")):
        y = Y + 38 + r * RH
        d = 200 + r * 120
        E += [box("%s tile" % side, X + 4, y + 2, TW - 4, RH - 4, None, A("wipe-right", 360, d), bg=C_TEAM(side))]
        E += logo_or_abbr("%s logo" % side, X + 12, y + 8, 70, RH - 16, side, 22, A("fade", 260, d + 160), S=CL)
        E += [txt("%s abbr" % side, X + 90, y, TW - 100, RH, "{%s.abbr}" % side, 34, A("fade", 260, d + 160), font=F, weight=800, textShadow=True)]
        for i in range(9):
            x = X + 4 + TW + i * CW
            E += [box("%s cell %d" % (side, i), x + 2, y + 2, CW - 4, RH - 4, None, A("fade", 220, d + 80 + i * 25), bg=C_DARK),
                  txt("%s %d" % (side, i + 1), x, y, CW, RH, "{linescore.%s.%d}" % (side, i), 32, A("fade", 220, d + 160 + i * 25, change="flash"),
                      font=F, weight=800, align="center")]
        for j, k in enumerate(("runs", "hits", "errors")):
            x = X + 4 + TW + 9 * CW + j * RW
            E += [box("%s %s bg" % (side, k), x + 2, y + 2, RW - 4, RH - 4, None, A("pop", 260, d + 300 + j * 40), bg=C_GRAY),
                  txt("%s %s" % (side, k), x, y, RW, RH, "{%s.%s}" % (side, k), 38, A("fade", 220, d + 360 + j * 40, change="pop"), font=F, weight=800,
                      align="center", color=C_INK)]
    return {"name": "Linescore (Classic)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def custom_lower():
    """Brand or league logo tile, gray bar with line 1, dark row with line 2."""
    X, Y, T, W = 70, 846, 172, 1140
    E = [box("Tile", X, Y, T, 172, None, A("pop", 420, 0, out=OUT_), bg=C_DARK, shadow=CL["shadow"]),
         img("Brand", X + 14, Y + 14, T - 28, 144, "{brand.logo}", A("zoom-out", 420, 160), show="brand.logo"),
         img("League", X + 14, Y + 14, T - 28, 144, "{league.logo}", A("zoom-out", 420, 160), show="!brand.logo && league.logo"),
         box("Bar", X + T, Y, W - T, 100, None, A("wipe-right", 440, 120, out=OUT_), bg=C_GRAY, shadow=CL["shadow"]),
         txt("Line 1", X + T + 26, Y, W - T - 50, 100, "{custom.line1}", 52, A("reveal-up", 380, 380), font=F, weight=800, color=C_INK),
         box("Row", X + T, Y + 100, W - T, 72, None, A("wipe-right", 420, 240, out=OUT_), bg=C_DARK),
         txt("Line 2", X + T + 26, Y + 100, W - T - 50, 72, "{custom.line2}", 32, A("fade", 260, 480), show="custom.line2", font=F, weight=700)]
    return {"name": "Custom Lower Third (Classic)", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


def standings():
    """Gray header bar with the division, dark rows with team tiles."""
    X, Y, W, RH = 520, 110, 880, 66
    E = [box("Header", X, Y, W, 100, None, A("wipe-right", 440, 0, out=OUT_), bg=C_GRAY, shadow=CL["shadow"]),
         img("League", X + 18, Y + 12, 120, 76, "{league.logo}", A("pop", 360, 200), show="league.logo"),
         txt("Season", X + 160, Y + 8, W - 190, 30, "{seasonYear} STANDINGS", 22, A("fade", 260, 380), font=F, weight=800, color="#4B5059", tracking=1),
         txt("Division", X + 158, Y + 32, W - 190, 64, "{standingsGroup.name}", 52, A("reveal-up", 360, 360), font=F, weight=800, color=C_INK),
         box("Head row", X, Y + 100, W, 40, "#050506", A("wipe-down", 300, 200))]
    for lab, x, w in (("W", 560, 80), ("L", 640, 80), ("PCT", 720, 90), ("GB", 810, 70)):
        E.append(txt("Head " + lab, X + x, Y + 100, w, 40, lab, 18, A("fade", 240, 360), font=F, weight=800, align="center", color=C_LABEL, tracking=1))
    for i in range(10):
        p = "standingsGroup.teams.%d" % i
        y = Y + 140 + i * RH
        d = 380 + i * 60
        E += [box("Row %d" % i, X, y, W, RH - 2, None, A("wipe-right", 300, d), show=p + ".name", bg=C_DARK),
              box("Game %d" % i, X, y, 8, RH - 2, "$accent", A("grow-y", 240, d + 100), show=both(p + ".name", p + ".isGame")),
              txt("Rank %d" % i, X + 10, y, 50, RH - 2, "{%s.rank}" % p, 26, A("fade", 220, d + 80), show=p + ".name", font=F, weight=800,
                  align="center", color=C_LABEL),
              img("Logo %d" % i, X + 66, y + 6, 70, RH - 14, "{%s.logo}" % p, A("fade", 220, d + 100), show=both(p + ".name", p + ".logo")),
              txt("Team %d" % i, X + 150, y, 400, RH - 2, "{%s.name}" % p, 30, A("fade", 220, d + 100), show=p + ".name", font=F, weight=800)]
        for k, x, w in (("w", 560, 80), ("l", 640, 80), ("pct", 720, 90), ("gb", 810, 70)):
            E.append(txt("%s %d" % (k, i), X + x, y, w, RH - 2, "{%s.%s}" % (p, k), 28, A("fade", 220, d + 120), show=p + ".name", font=F,
                         weight=800, align="center", color="$accent" if k == "gb" else "#FFFFFF"))
    return {"name": "Standings (Classic)", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
# Rob's designs, under standard ids so this style's set picks them first
g["scorebug"] = BL.c_scorebug(CL, True)
g["scorebug_basic"] = BL.c_scorebug(CL)
g["batter"] = BL.c_lower(CL, "bat", True)
g["pitcher"] = BL.c_lower(CL, "pit", True)
g["batter4"] = BL.c_lower(CL, "bat")
g["pitcher4"] = BL.c_lower(CL, "pit")
g["team_intro"] = dict(BL.c_team_intro(CL), cat="matchups")
g["league_bug"] = BL.c_league_bug(CL)
g["dueup"] = due_up()
g["linescore"] = linescore()
g["custom"] = custom_lower()
g["standings"] = standings()
MS = dict(CL, **SK.MARKS)
g["batter_card"] = BL.stat_card_tonight(MS, "bat")
g["pitcher_card"] = BL.stat_card_tonight(MS, "pit")
# Everything else from the shared library, drawn in the Classic language
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_bar", "pitcher_bar", "batter_tab", "pitcher_tab", "league_bug")
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP or gid in g:
        continue
    g[gid] = gdef
for gid in ("inning_sponsor", "lineup", "pitching", "defense", "spotlight", "note", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g.update(SL.all_sports(MS))
CUSTOM = ("scorebug", "scorebug_basic", "batter", "pitcher", "batter4", "pitcher4", "team_intro", "league_bug", "dueup", "linescore", "custom", "standings")
K = dict(panel=C_DARK, panel2="linear-gradient(180deg, #25282E 0%, #141619 100%)", dark="#050506", strip=C_GRAY, stripText=C_INK, val=C_GRAY,
         ink=C_INK, hi="$accent", hiText="#111214", hiDark=True, line="#FFFFFF@0.14", title=CL["titleBg"], shadow=CL["shadow"],
         team=lambda t: C_TEAM(t), rule="$accent", text2="#FFFFFF", radius=2, noBlur=True,
         panelBox={"radius": 2, "shadow": CL["shadow"]}, lightBox={"radius": 2}, hiBox={"radius": 2},
         text={"textShadow": ""}, textDark={"textShadow": ""})
import rebuild as RB  # noqa: E402


def kit_tr_cf(gid, g, TA):
    """Dark field, team-colour logo tile and a light gray word bar over a dark row, like the Classic lower thirds."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=CL["titleBg"]),
         box("Logo tile", 160, 380, 300, 300, None, TA("pop", 400, 120), bg=C_TEAM("team"), shadow=CL["shadow"]),
         box("Bar", 460, 380, 1300, 200, None, TA("wipe-right", 440, 160), bg=C_GRAY, shadow=CL["shadow"]),
         box("Row", 460, 580, 1300, 100, None, TA("wipe-right", 420, 240), bg=C_DARK)]
    return {"elements": E, "word": {"font": F, "weight": 800, "color": C_INK, "textShadow": "", "rect": (490, 380, 1250, 200), "align": "left"},
            "sub": {"font": F, "weight": 700, "color": "#FFFFFF", "textShadow": "", "rect": (490, 580, 1250, 100), "align": "left", "tracking": 1},
            "brand": {"rect": (190, 410, 240, 240)}}


def kit_slab(R, slab, g):
    x, y, w, h = R
    return [box("Frame", 0, y - 8, 1920, h + 16, "#050506", A("wipe-right", 300, 0)),
            dict(box("Row", 0, y + h - 100, 1920, 100, None, A("wipe-right", 320, 200), bg=C_DARK), _over=True)]

def kit_screen(bg, team, g):
    over = [box("Frame", 0, 0, 1920, 1080, None, A("fade", 300, 0), borderW=14, borderColor="#050506"),
            box("Row", 0, 1000, 1920, 80, None, A("wipe-right", 380, 160), bg=C_DARK),
            box("Bar", 0, 990, 1920, 10, None, A("wipe-right", 380, 120), bg=C_GRAY)]
    return {"floor": C_GRAY, "replace": CL["titleBg"], "over": over}

KIT = RB.make_kit(dict(
    screen=kit_screen,
    slab=kit_slab,
    body=C_DARK, bodyBox={"radius": 3, "borderW": 4, "borderColor": "#050506", "shadow": CL["shadow"]},
    headTile=lambda t: C_TEAM(t) if t else C_DARK, head=C_GRAY, headBox={"shadow": CL["shadow"]}, headRule="$accent", sub="#050506",
    title={"font": F, "weight": 800, "color": C_INK, "textShadow": "", "italic": False},
    headText={"color": "#4B5059", "textShadow": ""}, subText={"font": F, "weight": 800, "color": C_LABEL, "textShadow": "", "tracking": 1},
    roles={"PANEL": C_DARK, "PANEL2": "linear-gradient(180deg, #25282E 0%, #141619 100%)", "DARK": "#050506", "STRIP": C_GRAY},
    barBox={"radius": 2}, mainBox={"shadow": CL["shadow"]},
    tile={"radius": 0, "borderW": 0}, tr=kit_tr_cf))

g = RB.rebuild_all(g, KIT, only=set(g) - set(CUSTOM))
g = RB.strip_flags(SK.skin_all(g, K, only=set(g) - set(CUSTOM)))
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
g["batter4"]["pickable"] = g["pitcher4"]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
g["batter"]["sponsorSlot"] = g["batter4"]["sponsorSlot"] = "lineup_{batter.slot}, batter"
g["pitcher"]["sponsorSlot"] = g["pitcher4"]["sponsorSlot"] = "pitcher"
# Every tile says which style it is
for k, d in g.items():
    nm = d.get("name", k).replace(" (Classic)", "").replace("(Classic, ", "(").replace(" (Classic Bar)", "")
    nm = nm.replace("Scorebug: Classic + Pitch Info", "Scorebug + Pitch Info").replace("Scorebug: Classic", "Scorebug")
    nm = nm.replace("(6 stats)", "(6 stats)").replace(" ()", "")
    if not d.get("layout"):
        nm = "%s (Classic Frame)" % nm if "(" not in nm else nm.replace(")", ", Classic Frame)", 1) if nm.endswith(")") and "6 stats" in nm else "%s (Classic Frame)" % nm
    d["name"] = nm

theme = dict(night_doc["theme"])
doc = {"version": 2, "name": "Classic Frame",
       "description": "Your Classic designs as a full style: black-frame scorebug with pitch info, gray name bar lower thirds with a dark stat row, "
                      "team-colour tiles, and every other graphic type drawn the same way, plus basketball, football and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "classic-designs.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
