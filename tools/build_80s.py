"""Builds the "Throwback 80s" package: templates/packages/throwback-80s.json.

1980s TV baseball, after the throwback frames Rob sent: a navy band with red pinstripes across the top of full
screens, heavy italic type (Archivo Black Italic, bundled) in white and pale yellow with a hard black drop shadow,
no boxes, text-only scorebug with dashed count marks, a red rule under lower-third names, gray studio backdrop.
Run:  python tools/build_80s.py   (after tools/build_night_game.py)
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

NAVY = "#14295B"
RED = "#D9364A"
YEL = "#F4E66A"
WHT = "#FFFFFF"
SH = "5px 5px 0 #000000"
SH_S = "3px 3px 0 #000000"
BAND = ("linear-gradient(180deg, transparent 0 8%, " + RED + " 8% 18%, #F2F2F2 18% 22%, " + NAVY + " 22% 78%, #F2F2F2 78% 82%, "
        + RED + " 82% 92%, transparent 92% 100%)")
GRAY = "linear-gradient(180deg, #5E5F63 0%, #4D4E52 100%)"
TEAM = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 80%%, #fff) 0%%, {%s.color} 55%%, "
        "color-mix(in srgb, {%s.color} 65%%, #000) 100%%)")

TS = dict(BL.NETWORK, key="eighties", font="$font", body="$font", up=True, radius=0, cardRadius=0,
          panel="linear-gradient(180deg, #23397A 0%, #14295B 100%)", panel2="linear-gradient(180deg, #303A52 0%, #20283B 100%)", dark="#0B1430",
          strip=YEL, stripText="#111111", val=WHT, valText="#111111", hi=RED, hiText=WHT, line="#FFFFFF@0.3",
          shadow="6px 6px 0 rgba(0,0,0,.9)", cardIn="wipe-right", teamGrad=TEAM, titleBg=GRAY)
F = "$font"
LIVE = "inPlay"
CUT = {"type": "fade", "dur": 120, "delay": 0, "ease": "linear"}


def T(name, x, y, w, h, text, size, delay=0, show=None, color=WHT, align="left", sh=SH, a=None, **st):
    """Heavy italic type with the hard black drop shadow."""
    st.setdefault("weight", 900)
    return txt(name, x, y, w, h, text, size, a or A("slide-right", 260, delay, dist=40, out=CUT), show=show, font=F, color=color, align=align,
               italic=True, textShadow=sh, **st)


def band(Y, title, delay=0, size=96, logo_right=True):
    E = [box("Band", 0, Y, 1920, 130, None, A("wipe-right", 380, delay, out=CUT), bg=BAND),
         T("Band title", 60, Y - 10, 1500, 150, title, size, delay + 200, align="left")]
    if logo_right:
        E += [img("Band logo", 1640, Y - 10, 230, 150, "{league.logo}", A("fade", 300, delay + 300, out=CUT), show="league.logo")]
    return E


# ------------------------------------------------------------------ scorebug
def scorebug():
    X, Y = 60, 40
    E = [T("Half", X, Y, 260, 50, "{half|upper} {inningOrd}", 38, 0, LIVE, sh=SH_S),
         T("Status", X, Y, 260, 50, "{statusText}", 38, 0, "!" + LIVE, sh=SH_S),
         T("Outs", X + 280, Y, 220, 50, "{outs} OUTS", 38, 60, LIVE, sh=SH_S, align="right")]
    E += logo_or_abbr("Away", X, Y + 56, 110, 96, "away", 40, A("fade", 200, 100, out=CUT), S=TS)
    E += [T("Score", X + 110, Y + 50, 290, 110, "{away.runs}-{home.runs}", 96, 120, None, YEL, "center", a=A("fade", 200, 120, out=CUT, change="flash"))]
    E += logo_or_abbr("Home", X + 400, Y + 56, 110, 96, "home", 40, A("fade", 200, 140, out=CUT), S=TS)
    E += [T("Balls", X, Y + 166, 220, 46, "{balls} BALLS", 32, 180, LIVE, sh=SH_S),
          box("Ball dash", X, Y + 160, 60, 4, WHT, A("fade", 100, 180, out=CUT), show=LIVE),
          el("bases", "Bases", X + 220, Y + 160, 90, 52, A("fade", 200, 200, out=CUT), show=LIVE, bind="bases",
             style={"layout": "tight", "on": YEL, "off": "transparent", "stroke": "#111111", "strokeW": 3}),
          T("Strikes", X + 320, Y + 166, 200, 46, "{strikes} STRIKES", 32, 220, LIVE, sh=SH_S, align="right"),
          box("Strike dash", X + 460, Y + 160, 60, 4, WHT, A("fade", 100, 220, out=CUT), show=LIVE)]
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(kind):
    who = "pitcher" if kind == "pit" else "batter"
    if kind == "pit":
        head = "{pitcher.number} - {pitcher.name|upper}"
        tag = "{pitcher.throws|hand}"
        cols = [("WON", "{pitcher.season.w|zero}"), ("LOST", "{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"), ("ERA", "{pitcher.season.era|era}")]
    else:
        head = "{batter.number}-{batter.name|upper}"
        tag = "{batter.pos}"
        cols = [("BA", "{batter.season.avg|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}")]
    X, Y, W = 460, 740, 1000
    E = [T("Name", X, Y, W - 160, 84, head, 64, 0, None, YEL),
         T("Tag", X + W - 170, Y, 170, 84, tag, 56, 80, None, WHT, "right"),
         box("Rule", X, Y + 88, W, 8, RED, A("wipe-right", 260, 160, out=CUT)),
         T("Season", X, Y + 100, W, 60, "THIS SEASON ({%s.season.g} GAMES)" % who if kind == "bat" else "THIS SEASON ({pitcher.season.gs} STARTS)", 44,
           220, "%s.season.g" % who if kind == "bat" else "pitcher.season.gs", align="center"),
         T("Season plain", X, Y + 100, W, 60, "THIS SEASON", 44, 220, "!%s.season.g" % who if kind == "bat" else "!pitcher.season.gs", align="center")]
    cw = W // len(cols)
    for i, (lab, val) in enumerate(cols):
        E += [T("%s label" % lab, X + i * cw, Y + 164, cw, 56, lab, 44, 300 + i * 60, align="center"),
              T("%s value" % lab, X + i * cw, Y + 222, cw, 60, val, 48, 360 + i * 60, None, YEL, "center")]
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def custom_lower():
    X, Y, W = 360, 820, 1200
    E = [T("Line 1", X, Y, W, 90, "{custom.line1|upper}", 66, 0, "custom.line1", YEL, "center"),
         box("Rule", X + 100, Y + 94, W - 200, 8, RED, A("wipe-right", 260, 160, out=CUT), show="custom.line2"),
         T("Line 2", X, Y + 106, W, 70, "{custom.line2|upper}", 48, 220, "custom.line2", WHT, "center")]
    return {"name": "Custom Lower Third", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ full screens
def standings():
    E = [box("Backdrop", 0, 0, 1920, 1080, "#000000@0.35", A("fade", 300, 0, out=CUT))]
    E += band(50, "{standingsGroup.name|upper} STANDINGS", size=100)
    E += [T("Head WL", 1180, 210, 260, 60, "W-L", 44, 300, align="center", sh=SH_S),
          T("Head GB", 1500, 210, 200, 60, "GB", 44, 320, align="center", sh=SH_S)]
    for i in range(8):
        p = "standingsGroup.teams.%d" % i
        y = 270 + i * 100
        d = 400 + i * 120
        E += [T("Team %d" % i, 250, y, 900, 96, "{%s.nick|upper}" % p, 78, d, both(p + ".name", p + ".nick"), YEL),
              T("Team full %d" % i, 250, y, 900, 96, "{%s.name|upper}" % p, 70, d, both(p + ".name", "!" + p + ".nick"), YEL),
              T("WL %d" % i, 1140, y, 340, 96, "{%s.w}-{%s.l}" % (p, p), 78, d + 60, p + ".name", align="center"),
              T("GB %d" % i, 1480, y, 240, 96, "{%s.gb}" % p, 78, d + 80, p + ".name", align="center")]
    return {"name": "Standings", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


POS = {"CF": (960, 330), "LF": (380, 420), "RF": (1540, 420), "SS": (640, 530), "2B": (1280, 510), "3B": (360, 660),
       "1B": (1560, 650), "P": (960, 730), "C": (960, 880)}


def defense():
    E = [box("Shade", 0, 0, 1920, 1080, "#000000@0.25", A("fade", 300, 0, out=CUT))]
    E += band(110, "", size=96, logo_right=False)
    E += logo_or_abbr("Team", 760, 100, 400, 150, "team", 110, A("pop", 300, 200, out=CUT), S=TS)
    for i, (pos, (cx, cy)) in enumerate(POS.items()):
        p = "team.defense.%s" % pos
        E.append(T("D %s" % pos, cx - 270, cy, 540, 80, "{%s.name|upper}" % p, 50, 400 + i * 90, p + ".name", YEL, "center"))
    return {"name": "Defense", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": E}


def lineup():
    E = [box("Backdrop", 0, 0, 1920, 1080, GRAY, A("fade", 300, 0, out=CUT))]
    E += band(50, "{team.nick|upper} LINEUP", size=96)
    for i in range(9):
        p = "team.lineup.%d" % i
        y = 220 + i * 92
        d = 300 + i * 90
        E += [T("Slot %d" % i, 200, y, 80, 88, "%d." % (i + 1), 62, d, p + ".name", WHT, "right"),
              T("Name %d" % i, 320, y, 1000, 88, "{%s.name|upper}" % p, 66, d, p + ".name", YEL),
              T("Pos %d" % i, 1330, y, 160, 88, "{%s.pos}" % p, 62, d + 40, p + ".name"),
              T("Avg %d" % i, 1520, y, 220, 88, "{%s.avg|avg}" % p, 62, d + 60, p + ".name", WHT, "right")]
    return {"name": "Lineup", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E}


def matchup():
    E = []
    for i, side in enumerate(("away", "home")):
        x = 140 if i == 0 else 1040
        E += logo_or_abbr("%s logo" % side, x, 260, 740, 300, side, 160, A("pop", 360, i * 200, out=CUT), S=TS)
        E += [T("%s rec" % side, x, 580, 740, 90, "({%s.record})" % side, 72, 500 + i * 100, "%s.record" % side, YEL, "center")]
    E += [T("VS", 860, 360, 200, 100, "VS", 64, 400, align="center", sh=SH_S),
          T("Venue", 260, 760, 1400, 100, "{venue|upper}", 72, 800, "venue", WHT, "center"),
          img("Brand", 60, 40, 320, 150, "{brand.logo}", A("fade", 300, 200, out=CUT), show="brand.logo")]
    return {"name": "Matchup", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def feature():
    """Notes card on the gray studio backdrop: band title, kicker in yellow, framed photo, big lines."""
    E = [box("Backdrop", 0, 0, 1920, 1080, GRAY, A("fade", 300, 0, out=CUT))]
    E += band(110, "{notes.title|upper}", size=90, logo_right=False)
    E[2]["showIf"] = "notes.title"
    E.append(T("Band name", 60, 100, 1500, 150, "{batter.name|upper}", 90, 200, "!notes.title"))
    E += [T("Kicker", 360, 250, 1300, 70, "{notes.kicker|upper}", 52, 300, "notes.kicker", YEL),
          box("Frame", 80, 330, 860, 640, None, A("fade", 300, 300, out=CUT), bg="#EDEDED", radius=24, borderW=10, borderColor=RED),
          img("Photo", 96, 346, 828, 608, "{batter.photo}", A("fade", 300, 400, out=CUT), show="batter.photo", fit="cover", focus="center top"),
          img("Logo", 220, 420, 580, 460, "{team.logo}", A("fade", 300, 400, out=CUT), show="!batter.photo && team.logo")]
    for i in range(3):
        k = "notes.b%d" % (i + 1)
        E.append(T("Line %d" % i, 990, 420 + i * 150, 880, 140, "{%s|upper}" % k, 62, 500 + i * 140, k, YEL if i % 2 == 0 else WHT, wrap=True,
                   fit=False, lineH=1.0))
    return {"name": "Feature Card", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "feature"}


def hr_event():
    E = [T("HR", 360, 840, 1200, 180, "HOME RUN", 170, 0, "lastPlay.runs!=4", WHT, "center", sh="8px 8px 0 #000",
           a=A("zoom-out", 300, 0, out=CUT)),
         T("GS", 360, 840, 1200, 180, "GRAND SLAM", 160, 0, "lastPlay.runs==4", YEL, "center", sh="8px 8px 0 #000", a=A("zoom-out", 300, 0, out=CUT))]
    return {"name": "Home Run!", "group": "event", "autoHide": 4, "side": "batting", "sided": False, "elements": E, "trigger": "HR",
            "sponsorSlot": "home_run"}


def due_up():
    X, Y, W = 460, 720, 1000
    E = [T("Title", X, Y, W, 84, "DUE UP FOR {team.nick|upper}", 64, 0, None, WHT, "center"),
         box("Rule", X, Y + 88, W, 8, RED, A("wipe-right", 260, 160, out=CUT))]
    for i in range(3):
        p = "team.dueUp.%d" % i
        E += [T("Due %d" % i, X, Y + 104 + i * 74, W, 72, "{%s.slot}-{%s.name|upper}  {%s.avg|avg}" % (p, p, p), 52, 260 + i * 120, p + ".name", YEL,
                "center")]
    return {"name": "Due Up", "group": "lower", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "half_{halfKey}, dueup"}


def ticker():
    Y, HH = 1020, 56
    E = [box("Bar", 0, Y - 6, 1920, HH + 12, NAVY, A("wipe-up", 300, 0, out=CUT)),
         box("Stripe", 0, Y - 6, 1920, 6, RED, A("grow-x", 300, 100, out=CUT)),
         T("Label", 30, Y, 260, HH, "{ticker.label|upper}", 36, 200, "ticker.label", YEL, sh=SH_S),
         el("ticker", "Crawl", 300, Y, 1600, HH, A("fade", 300, 300, out=CUT), bind="ticker.items",
            style={"size": 32, "weight": 900, "color": WHT, "font": F, "speed": 110, "headFill": RED, "headColor": WHT, "upper": True})]
    return {"name": "Bottom Ticker", "group": "ticker", "autoHide": 0, "side": "", "sided": False, "elements": E}


def word_transition(word, sub):
    """Navy pinstripe band sweeping across with the big italic word, then off."""
    hold = lambda a_, h: dict(a_, hold=h)
    E = [box("Shade", 0, 0, 1920, 1080, "#000000@0.55", hold(A("fade", 200, 0, out=CUT), 1500)),
         box("Band", 0, 380, 1920, 320, None, hold(A("wipe-right", 380, 0, out={"type": "wipe-right", "dur": 320, "delay": 0, "ease": "in"}), 1300),
             bg=BAND),
         T("Word", 0, 400, 1920, 230, word, 200 if len(word) < 9 else 150, 0, None, WHT, "center", sh="10px 10px 0 #000",
           a=hold(A("slide-right", 360, 200, dist=120, out=CUT), 1100)),
         T("Sub", 0, 640, 1920, 90, sub, 64, 0, sub.strip("{}").split("|")[0] if sub.startswith("{") else None, YEL, "center",
           a=hold(A("fade", 200, 450, out=CUT), 900))]
    return E


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(TS, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("inning_sponsor", "pitching", "linescore", "spotlight", "note", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g["batter_card"] = BL.stat_card_tonight(MS, "bat")
g["pitcher_card"] = BL.stat_card_tonight(MS, "pit")
g.update({"scorebug": scorebug(), "batter": lower("bat"), "pitcher": lower("pit"), "custom": custom_lower(), "standings": standings(),
          "defense": defense(), "lineup": lineup(), "matchup": matchup(), "feature": feature(), "hr_event": hr_event(), "dueup": due_up(),
          "ticker": ticker()})
g.update(SL.all_sports(MS))
CUSTOM = ("scorebug", "batter", "pitcher", "custom", "standings", "defense", "lineup", "matchup", "feature", "hr_event", "dueup", "ticker")
K = dict(boxless=True, panel="transparent", panel2="transparent", dark="transparent", strip="transparent", stripText=YEL, val="transparent", ink=YEL,
         hi=RED, hiText=WHT, line=RED, title=GRAY, shadow="none", team=lambda t: "transparent", rule=RED, text2=YEL, radius=0,
         text={"italic": True, "weight": 900, "textShadow": SH_S, "font": F})
import rebuild as RB  # noqa: E402


def kit_frame_80s(X, Y, W, H, hb, sub_h, g):
    """The pinstripe band across the screen behind the title; the body has no boxes."""
    E = []
    if hb:
        bh = max(110, min(150, hb + 30))
        bx, bw = (0, 1920) if W >= 1000 else (X, W)
        E.append(box("Band", bx, Y + hb // 2 - bh // 2, bw, bh, None, A("wipe-right", 380, 0, out=CUT), bg=BAND))
    E.append(box("Rule", X, Y + H - 6, W, 6, RED, A("grow-x", 300, 300, out=CUT)))
    return {"elements": E, "title": {"font": F, "weight": 900, "italic": True, "color": WHT, "textShadow": SH},
            "sub": {"font": F, "weight": 900, "italic": True, "color": YEL, "textShadow": SH_S}, "subText": {"color": YEL},
            "headText": {"italic": True, "weight": 900, "textShadow": SH_S}}


def kit_lower_80s(U, M, g):
    x, y, w, h = M
    return [box("Red rule", x, y + h + 2, w, 6, RED, A("grow-x", 300, 200, out=CUT)),
            box("White rule", x, y + h + 10, w, 3, WHT, A("grow-x", 300, 260, out=CUT))]


def kit_slab_80s(R, slab, g):
    x, y, w, h = R
    return [box("Band", 0, y, 1920, h, None, A("wipe-right", 320, 0, out=CUT), bg=BAND)]


def kit_screen_80s(bg, team, g):
    over = [box("Band top", 0, -30, 1920, 130, None, A("wipe-right", 380, 0, out=CUT), bg=BAND),
            box("Band bottom", 0, 980, 1920, 130, None, A("wipe-left", 380, 0, out=CUT), bg=BAND)]
    return {"floor": BAND, "replace": "linear-gradient(180deg, #23397A 0%, #14295B 100%)", "over": over}


KIT = dict(screen=kit_screen_80s, frame=kit_frame_80s, bar=lambda b, main, role, g: [], lower_decor=kit_lower_80s, event=kit_slab_80s)

g = RB.rebuild_all(g, KIT, only=set(g) - set(CUSTOM))
g = RB.strip_flags(SK.skin_all(g, K, only=set(g) - set(CUSTOM)))
# transitions: the pinstripe band instead of the shared design
for tid, word, sub, *_r in BL.TRANSITIONS:
    sub_ = {"{show.name}": "{show.name|upper}", "{team.name}": "{team.name|upper}"}.get(sub, sub.upper())
    g[tid] = {"name": "Transition: %s" % word.title(), "group": "stinger", "autoHide": 2.2, "side": "team", "sided": True,
              "elements": word_transition(word.upper(), sub_), "cat": "transitions"}
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
for k, d in g.items():
    if not d.get("layout") and "Throwback 80s" not in d.get("name", ""):
        d["name"] = "%s (Throwback 80s)" % d.get("name", k)

theme = dict(night_doc["theme"])
theme.update({"primary": NAVY, "accent": YEL, "text": WHT, "dim": "rgba(255,255,255,0.85)", "line": "rgba(255,255,255,0.3)",
              "card": "rgba(20,41,91,0.95)", "panel": "rgba(20,41,91,0.95)", "panel2": "rgba(48,58,82,0.95)",
              "font": "'BBG Archivo', 'Arial Black', Impact, sans-serif", "font2": "'BBG Archivo', 'Arial Black', Impact, sans-serif"})
doc = {"version": 2, "name": "Throwback 80s",
       "description": "1980s TV baseball: navy band with red pinstripes, heavy italic white and yellow type with hard black shadows, no boxes, "
                      "text-only scorebug, red rule lower thirds. Every graphic type, plus basketball, football and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "throwback-80s.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
