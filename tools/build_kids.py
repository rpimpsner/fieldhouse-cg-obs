"""Builds the "Playground" package (kids broadcast): templates/packages/playground.json.

Bright, rounded and bouncy, after the kids-cast reference Rob sent: chunky rounded type (Fredoka, bundled) in white
with a thick dark outline, rounded team-colour bars, white pill rows, sunny yellow and pink accents, confetti dots on
full screens, pop-in animations. Every graphic type plus basketball, football and hockey.
Run:  python tools/build_kids.py   (after tools/build_night_game.py)
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
from broadcast_lib import A, box, txt, img, el, both, logo_or_abbr, sponsor_tab  # noqa: E402

NAVY = "#1B1F3B"
SKY = "linear-gradient(180deg, #5CC0FF 0%, #2D8BF0 100%)"
GRASS = "linear-gradient(180deg, #5BD67F 0%, #25A24F 100%)"
SUN = "#FFD43B"
PINK = "#FF5DA2"
CONFETTI = ("radial-gradient(circle, #FFD43B 4px, transparent 5px) 0 0 / 70px 70px, "
            "radial-gradient(circle, #FF5DA2 4px, transparent 5px) 35px 20px / 70px 70px, "
            "radial-gradient(circle, #5BD67F 3px, transparent 4px) 15px 45px / 70px 70px, "
            "linear-gradient(180deg, #2D8BF0 0%, #1C5FC9 100%)")
TEAM = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 85%%, #fff) 0%%, {%s.color} 60%%, "
        "color-mix(in srgb, {%s.color} 80%%, #000) 100%%)")
STROKE = "3px " + NAVY
POP = "0 5px 0 " + NAVY

KS = dict(BL.NETWORK, key="kids", font="$font", body="$font", up=True, radius=16, cardRadius=28,
          panel=SKY, panel2=GRASS, dark=NAVY, strip="#FFFFFF", stripText=NAVY, val=SUN, valText=NAVY,
          hi=PINK, hiText="#FFFFFF", line="#FFFFFF@0.5", shadow="0 8px 0 rgba(27,31,59,0.85)", cardIn="pop",
          teamGrad=TEAM, titleBg=CONFETTI)
KS["in"] = "pop"
F = "$font"
LIVE = "inPlay"
OUT_ = {"type": "scale", "dur": 260, "delay": 0, "ease": "in"}


def B(a):
    """Bouncy entrance."""
    a["in"]["ease"] = "back"
    return a


def K(name, x, y, w, h, text, size, a, show=None, color="#FFFFFF", **st):
    """Chunky outlined kid type."""
    st.setdefault("weight", 700)
    return txt(name, x, y, w, h, text, size, a, show=show, font=F, color=color, textStroke=STROKE, textShadow=POP, **st)


def pill(name, x, y, w, h, a, show=None, bg="#FFFFFF"):
    return box(name, x, y, w, h, None, a, show=show, bg=bg, radius=h // 2, borderW=4, borderColor=NAVY, shadow=KS["shadow"])


# ------------------------------------------------------------------ scorebug
def scorebug():
    X, Y = 40, 30
    E = []
    for i, side in enumerate(("away", "home")):
        x = X + i * 300
        E += [box("%s cap" % side, x + (0 if i == 0 else 180), Y, 110, 100, None, B(A("pop", 420, i * 120, out=OUT_)), bg=TEAM % (side, side, side),
                  radius=50, borderW=4, borderColor=NAVY, shadow=KS["shadow"])]
        E += logo_or_abbr("%s logo" % side, x + (10 if i == 0 else 190), Y + 10, 90, 80, side, 28, B(A("pop", 380, 200 + i * 120)), S=KS)
    E += [K("Score", X + 110, Y, 360, 100, "{away.runs}-{home.runs}", 92, B(A("pop", 460, 300, change="pop")), align="center"),
          pill("Info", X, Y + 112, 470, 54, B(A("pop", 380, 360)))]
    E += [txt("Inning", X + 18, Y + 112, 90, 54, "{arrow}{inning}", 30, A("fade", 240, 500, change="flash"), show=LIVE, font=F, weight=700, color=NAVY),
          txt("Count", X + 100, Y + 112, 110, 54, "{count}", 32, A("fade", 240, 520, change="flash"), show=LIVE, font=F, weight=700, color=NAVY,
              align="center"),
          el("bases", "Bases", X + 210, Y + 116, 80, 46, A("pop", 300, 540), show=LIVE, bind="bases",
             style={"layout": "tight", "on": PINK, "off": "#FFFFFF", "stroke": NAVY, "strokeW": 3}),
          el("dots", "Outs", X + 300, Y + 128, 70, 24, A("fade", 240, 560), show=LIVE, bind="outs",
             style={"total": 2, "size": 18, "gap": 8, "on": SUN, "off": "#D9DDE8", "align": "center", "border": NAVY}),
          txt("Outs word", X + 370, Y + 112, 90, 54, "{outs} OUT", 22, A("fade", 240, 580, change="flash"), show=LIVE, font=F, weight=700, color=NAVY),
          txt("Status", X, Y + 112, 470, 54, "{statusText}", 30, A("fade", 240, 500), show="!" + LIVE, font=F, weight=700, color=NAVY, align="center"),
          pill("Batter", X, Y + 178, 240, 44, B(A("pop", 360, 600)), show=LIVE, bg=TEAM % ("batting", "batting", "batting")),
          K("Batter t", X + 14, Y + 178, 214, 44, "{batter.slot}. {batter.last|upper}  {batter.season.avg|avg}", 20, A("fade", 240, 700), show=LIVE),
          pill("Pitcher", X + 252, Y + 178, 218, 44, B(A("pop", 360, 640)), show=LIVE, bg=TEAM % ("fielding", "fielding", "fielding")),
          K("Pitcher t", X + 266, Y + 178, 192, 44, "{pitcher.last|upper}  P:{pitcher.today.pc|zero}", 20, A("fade", 240, 740), show=LIVE)]
    E += sponsor_tab(X, Y + 236, 300, 44, 800, radius=22, a_type="pop")
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(kind):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    line1 = "TODAY: {pitcher.today.line|upper}" if kind == "pit" else "TODAY: {batter.today.line|upper}"
    line2 = ("THIS SEASON: {pitcher.season.era|era} ERA  |  {pitcher.season.w|zero}-{pitcher.season.l|zero}  |  {pitcher.season.k|zero} K" if kind == "pit"
             else "THIS SEASON: {batter.season.avg|avg} AVG  |  {batter.season.hr|zero} HR  |  {batter.season.rbi|zero} RBI")
    X, Y = 90, 840
    E = [box("Bar", X, Y + 92, 1740, 126, None, B(A("pop", 460, 120, out=OUT_)), bg=TEAM % (team, team, team), radius=30, borderW=5, borderColor=NAVY,
             shadow=KS["shadow"])]
    E += logo_or_abbr("Logo", X + 10, Y - 10, 230, 230, team, 64, B(A("pop", 460, 0)), S=KS)
    E += [box("Num", X + 240, Y + 2, 80, 84, "#FFFFFF", B(A("pop", 360, 260)), radius=16, borderW=4, borderColor=NAVY),
          txt("Num t", X + 240, Y + 4, 80, 40, "{%s.number}" % who, 34, A("fade", 220, 360), font=F, weight=700, color=NAVY, align="center"),
          txt("Pos t", X + 240, Y + 42, 80, 40, ("{pitcher.throws|hand}" if kind == "pit" else "{batter.pos}"), 28, A("fade", 220, 380), font=F,
              weight=700, color=NAVY, align="center"),
          K("Name", X + 340, Y - 6, 1300, 100, "{%s.name|upper}" % who, 88, B(A("pop", 420, 300))),
          K("Line 1", X + 340, Y + 96, 1380, 66, line1, 52, A("fade", 260, 520), show="%s.today.line" % who),
          K("Line 1 alt", X + 340, Y + 96, 1380, 66, "{%s.name|upper}" % who, 52, A("fade", 260, 520), show="!%s.today.line" % who),
          K("Line 2", X + 340, Y + 160, 1380, 48, line2, 34, A("fade", 260, 620))]
    E += sponsor_tab(X + 1440, Y + 30, 300, 54, 700, radius=27, a_type="pop")
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def custom_lower():
    X, Y = 140, 860
    E = [box("Bar", X, Y, 1640, 110, None, B(A("pop", 460, 0, out=OUT_)), bg=SKY, radius=55, borderW=5, borderColor=NAVY, shadow=KS["shadow"]),
         box("Star", X + 20, Y + 15, 80, 80, SUN, B(A("pop", 400, 200, loop={"type": "spin", "dur": 6000})), radius=12, rotate=45, borderW=4,
             borderColor=NAVY),
         K("Line 1", X + 130, Y, 1480, 110, "{custom.line1|upper}", 56, B(A("pop", 400, 300))),
         pill("Line 2 bg", X + 160, Y + 120, 1300, 56, B(A("pop", 360, 420)), show="custom.line2"),
         txt("Line 2", X + 190, Y + 120, 1240, 56, "{custom.line2|upper}", 32, A("fade", 240, 520), show="custom.line2", font=F, weight=700, color=NAVY)]
    return {"name": "Custom Lower Third", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


def hr_event():
    E = [box("Burst", 610, 240, 700, 700, None, B(A("pop", 420, 0, out=OUT_, loop={"type": "spin", "dur": 9000})), radius=60, rotate=45,
             bg="repeating-conic-gradient(from 0deg, #FFD43B 0deg 15deg, #FF9F1C 15deg 30deg)", borderW=8, borderColor=NAVY),
         K("Home", 360, 360, 1200, 200, "HOME", 190, B(A("pop", 420, 200)), align="center"),
         K("Run", 360, 540, 1200, 200, "RUN!", 210, B(A("pop", 420, 360, loop={"type": "pulse", "dur": 700, "amount": 0.08})), align="center",
           color=PINK, show="lastPlay.runs!=4"),
         K("Slam", 360, 540, 1200, 200, "GRAND SLAM!", 150, B(A("pop", 420, 360)), align="center", color=PINK, show="lastPlay.runs==4"),
         K("Who", 360, 760, 1200, 90, "{lastPlay.batter.name|upper}", 60, A("fade", 260, 700), show="lastPlay.batter.name", align="center")]
    return {"name": "Home Run!", "group": "event", "autoHide": 4.5, "side": "batting", "sided": False, "elements": E, "trigger": "HR",
            "sponsorSlot": "home_run"}


def standings():
    X, Y, W, RH = 360, 90, 1200, 72
    E = [box("Card", X, Y, W, 900, None, B(A("pop", 460, 0, out=OUT_)), bg=CONFETTI, radius=40, borderW=6, borderColor=NAVY, shadow=KS["shadow"]),
         K("Title", X + 40, Y + 20, W - 80, 100, "{standingsGroup.name|upper}", 72, B(A("pop", 420, 200)), align="center")]
    card = E[0]
    card["growWith"] = {"bind": "standingsGroup.teams", "base": 150, "per": RH + 6, "max": 10}
    for lab, x in (("W", 760), ("L", 880), ("GB", 1000)):
        E.append(K("Head " + lab, X + x, Y + 112, 120, 40, lab, 32, A("fade", 240, 400), align="center", color=SUN))
    for i in range(10):
        p = "standingsGroup.teams.%d" % i
        y = Y + 152 + i * (RH + 6)
        d = 400 + i * 80
        E += [pill("Row %d" % i, X + 40, y, W - 80, RH, B(A("pop", 340, d)), show=p + ".name"),
              img("Logo %d" % i, X + 56, y + 8, 70, RH - 16, "{%s.logo}" % p, A("fade", 220, d + 100), show=both(p + ".name", p + ".logo")),
              txt("Team %d" % i, X + 140, y, 600, RH, "{%s.name|upper}" % p, 34, A("fade", 220, d + 100), show=p + ".name", font=F, weight=700, color=NAVY)]
        for k, x in (("w", 760), ("l", 880), ("gb", 1000)):
            E.append(txt("%s %d" % (k, i), X + x, y, 120, RH, "{%s.%s}" % (p, k), 38, A("fade", 220, d + 140), show=p + ".name", font=F, weight=700,
                         color=NAVY if k != "gb" else PINK, align="center"))
    return {"name": "Standings", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


def ticker():
    Y, HH = 1016, 56
    E = [box("Bar", 0, Y, 1920, HH + 8, None, A("wipe-up", 400, 0, out={"type": "wipe-down", "dur": 300, "delay": 0, "ease": "in"}), bg=SKY,
             borderW=4, borderColor=NAVY),
         pill("Label", 20, Y + 6, 220, HH - 6, B(A("pop", 320, 200)), bg=SUN),
         txt("Label t", 20, Y + 6, 220, HH - 6, "{ticker.label|upper}", 28, A("fade", 220, 300), show="ticker.label", font=F, weight=700, color=NAVY,
             align="center"),
         el("ticker", "Crawl", 256, Y + 4, 1650, HH, A("fade", 400, 400), bind="ticker.items",
            style={"size": 30, "weight": 700, "color": "#FFFFFF", "font": F, "speed": 100, "headFill": PINK, "headColor": "#FFFFFF", "upper": True})]
    return {"name": "Bottom Ticker", "group": "ticker", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(KS, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("dueup", "inning_sponsor", "lineup", "pitching", "defense", "linescore", "spotlight", "note", "matchup", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g["batter_card"] = BL.stat_card_tonight(MS, "bat")
g["pitcher_card"] = BL.stat_card_tonight(MS, "pit")
g.update({"scorebug": scorebug(), "batter": lower("bat"), "pitcher": lower("pit"), "custom": custom_lower(), "hr_event": hr_event(),
          "standings": standings(), "ticker": ticker()})
g.update(SL.all_sports(MS))
CUSTOM = ("scorebug", "batter", "pitcher", "custom", "hr_event", "standings", "ticker")
K = dict(panel=SKY, panel2=GRASS, dark=NAVY, strip="#FFFFFF", stripText=NAVY, val=SUN, ink=NAVY, hi=PINK, hiText="#FFFFFF",
         line="#FFFFFF@0.5", title=CONFETTI, shadow=KS["shadow"], team=lambda t: TEAM % (t, t, t), rule=SUN, text2="#FFFFFF", radius=22,
         noBlur=True, panelBox={"radius": 22, "borderW": 4, "borderColor": NAVY, "shadow": KS["shadow"]},
         lightBox={"radius": 18, "borderW": 4, "borderColor": NAVY}, hiBox={"radius": 18, "borderW": 3, "borderColor": NAVY},
         text={"textStroke": "2px " + NAVY, "textShadow": "0 3px 0 " + NAVY, "font": F}, textDark={"textShadow": "", "font": F}, strokeMin=34)
import rebuild as RB  # noqa: E402


def kit_tr(gid, g, TA):
    """Confetti field, a big white bubble with a navy outline, chunky outlined word."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("scale", 460, 0), bg=CONFETTI),
         box("Bubble", 160, 340, 1600, 420, None, TA("pop", 460, 120), bg=SKY, radius=200, borderW=8, borderColor=NAVY, shadow=KS["shadow"]),
         box("Sun", 1580, 150, 180, 180, SUN, TA("pop", 380, 300), radius=90, borderW=6, borderColor=NAVY),
         box("Grass", 0, 960, 1920, 120, None, TA("wipe-up", 380, 160), bg=GRASS, borderW=6, borderColor=NAVY)]
    return {"elements": E, "word": {"font": F, "weight": 700, "color": "#FFFFFF", "textStroke": "5px " + NAVY, "textShadow": "0 8px 0 " + NAVY,
                                     "rect": (200, 360, 1520, 260)},
            "sub": {"font": F, "weight": 700, "color": SUN, "textStroke": STROKE, "textShadow": POP, "rect": (200, 610, 1520, 110)},
            "brand": {"rect": (860, 140, 200, 180)}}


def kit_slab(R, slab, g):
    x, y, w, h = R
    slab["style"]["borderW"] = 8
    slab["style"]["borderColor"] = NAVY
    slab["_kit"] = True
    return [dict(box("Confetti", 0, y, 1920, h, None, A("fade", 300, 200), bg=CONFETTI.rsplit(", linear-gradient", 1)[0]), _over=True),
            dict(box("Sun", 1700, y - 60, 160, 160, SUN, B(A("pop", 380, 300)), radius=80, borderW=6, borderColor=NAVY), _over=True)]

def kit_screen(bg, team, g):
    over = [box("Confetti", 0, 0, 1920, 1080, None, A("fade", 500, 100), bg=CONFETTI.rsplit(", linear-gradient", 1)[0]),
            box("Grass", -10, 990, 1940, 100, None, A("wipe-up", 380, 160), bg=GRASS, borderW=6, borderColor=NAVY)]
    return {"floor": GRASS, "replace": CONFETTI, "over": over}

KIT = RB.make_kit(dict(
    screen=kit_screen,
    slab=kit_slab,
    body=CONFETTI, bodyIn="pop", bodyBox={"radius": 40, "borderW": 6, "borderColor": NAVY, "shadow": KS["shadow"]},
    head=PINK, headBox={"radius": 30, "borderW": 5, "borderColor": NAVY}, sub=SUN,
    title={"font": F, "weight": 700, "color": "#FFFFFF", "textStroke": "2px " + NAVY, "textShadow": POP, "italic": False},
    headText={"font": F, "textStroke": "", "textShadow": "0 2px 0 " + NAVY}, subText={"font": F, "weight": 700, "color": NAVY, "textShadow": "", "textStroke": ""},
    roles={"PANEL": SKY, "PANEL2": GRASS, "DARK": NAVY, "STRIP": "#FFFFFF"}, barBox={"radius": 22, "borderW": 4, "borderColor": NAVY},
    mainBox={"shadow": KS["shadow"]},
    tile={"background": "#FFFFFF", "radius": 30, "borderW": 4, "borderColor": NAVY}, tileInk=NAVY, tr=kit_tr))

g = RB.rebuild_all(g, KIT, only=set(g) - set(CUSTOM))
g = RB.strip_flags(SK.skin_all(g, K, only=set(g) - set(CUSTOM)))
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
for k, d in g.items():
    if not d.get("layout") and "Playground" not in d.get("name", ""):
        d["name"] = "%s (Playground)" % d.get("name", k)

theme = dict(night_doc["theme"])
theme.update({"primary": NAVY, "accent": SUN, "text": "#FFFFFF", "dim": "rgba(255,255,255,0.9)", "line": "rgba(255,255,255,0.4)",
              "card": "rgba(45,139,240,0.96)", "panel": "rgba(45,139,240,0.96)", "panel2": "rgba(37,162,79,0.96)",
              "font": "'BBG Fredoka', 'Arial Rounded MT Bold', 'Comic Sans MS', sans-serif",
              "font2": "'BBG Fredoka', 'Arial Rounded MT Bold', 'Comic Sans MS', sans-serif"})
doc = {"version": 2, "name": "Playground",
       "description": "Kids broadcast: bright rounded shapes, chunky outlined type, team-colour bars, white pill rows, confetti, bouncy pop-ins. "
                      "Every graphic type, plus basketball, football and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "playground.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
