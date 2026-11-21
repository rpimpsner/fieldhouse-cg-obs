"""Builds the "National Broadcast 1" package: templates/packages/national-broadcast-1.json.

Modelled on the layouts of a national postseason baseball package Rob sent: a corner scorebug with a series title strip,
team-colour logo tiles, white score boxes, count and outs, bases and inning, a network block in your broadcaster colour
and a pitcher bar; lower thirds with a team-colour logo tile, number and position, first over LAST name on a team-colour
bar and a dark four-stat panel (with an optional tag and a yellow note line); a matchup banner; a three-panel game
open; a team intro; a full-screen Due Up; stat cards with the player over a team-colour field and a dark stat panel;
a team resume card; a studio side panel; and a show open. No network or league marks are included: the network spots
use your broadcaster logo and colours (Custom > League & broadcaster logos). Every other graphic type is drawn in the
same glossy black and team-colour language.
Run:  python tools/build_national1.py   (after tools/build_night_game.py)
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

GLOSS = "linear-gradient(180deg, #34363C 0%, #1A1B1F 46%, #0B0B0D 54%, #141518 100%)"
BLACK = "linear-gradient(180deg, #1D1E22 0%, #0C0D0F 100%)"
PANEL = "linear-gradient(180deg, rgba(24,24,28,0.94) 0%, rgba(10,10,12,0.96) 100%)"
PANEL2 = "linear-gradient(180deg, #26272C 0%, #17181B 100%)"
WHITE = "linear-gradient(180deg, #FFFFFF 0%, #E3E6EA 100%)"
INK = "#111214"
YEL = "#F5C33B"
DIM = "#B9BEC6"
EDGE = "#FFFFFF@0.14"
SHADOW = "0 10px 26px rgba(0,0,0,.55)"
NET = "linear-gradient(180deg, color-mix(in srgb, {brand.color} 85%, #fff) 0%, {brand.color} 50%, color-mix(in srgb, {brand.color} 70%, #000) 100%)"
TEAM_V = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 82%%, #fff) 0%%, {%s.color} 50%%, "
          "color-mix(in srgb, {%s.color} 68%%, #000) 100%%)")
TEAM_H = "linear-gradient(90deg, {%s.color} 0%%, color-mix(in srgb, {%s.color} 55%%, #000) 100%%)"
WEAVE = "repeating-linear-gradient(45deg, rgba(255,255,255,0.05) 0 2px, transparent 2px 6px), repeating-linear-gradient(-45deg, rgba(0,0,0,0.12) 0 2px, transparent 2px 6px)"
F = "$font2"     # condensed: names, numbers, labels
H = "$font"      # wide heavy: big titles
LIVE = "inPlay"
OUT_ = {"type": "fade", "dur": 240, "delay": 0, "ease": "in"}

NB = dict(BL.NETWORK, key="national1", font=F, body=F, up=True, radius=2, cardRadius=4,
          panel=PANEL, panel2=PANEL2, dark=BLACK, strip=WHITE, stripText=INK, val=WHITE, valText=INK,
          hi=YEL, hiText=INK, line="#FFFFFF@0.14", shadow=SHADOW, cardIn="zoom-out",
          teamGrad=TEAM_V, titleBg="radial-gradient(ellipse at 50% 30%, #2A2C31, #121316 60%, #050506)")


def TV(t):
    return TEAM_V % (t, t, t)


def TH(t):
    return TEAM_H % (t, t)


def W(name, x, y, w, h, text, size, a, show=None, **st):
    st.setdefault("font", F)
    st.setdefault("weight", 800)
    return txt(name, x, y, w, h, text, size, a, show=show, **st)


def K_(name, x, y, w, h, text, size, a, show=None, **st):
    st.setdefault("color", INK)
    return W(name, x, y, w, h, text, size, a, show=show, **st)


def team_bg(name, x, y, w, h, team, a, **kw):
    """Team colour with a woven texture and the logo faint across it."""
    return [box(name, x, y, w, h, None, a, bg=TV(team), **kw),
            box(name + " weave", x, y, w, h, None, A("fade", 400, (a["in"].get("delay") or 0) + 100), bg=WEAVE, radius=kw.get("radius", 0)),
            img(name + " logo", x + w // 6, y + h // 8, w * 2 // 3, h * 3 // 4, "{%s.logo}" % team, A("fade", 600, (a["in"].get("delay") or 0) + 200),
                show="%s.logo" % team, opacity=0.12)]


def net_mark(name, x, y, w, h, a):
    """Your broadcaster logo (or short name) where the network mark sits."""
    return [img(name, x, y, w, h, "{brand.logo}", a, show="brand.logo"),
            W(name + " text", x, y, w, h, "{brand.short|upper}", int(h * 0.6), a, show="!brand.logo && brand.short", align="center"),
            img(name + " league", x, y, w, h, "{league.logo}", a, show="!brand.logo && !brand.short && league.logo")]


# ------------------------------------------------------------------ scorebug
def scorebug():
    X, Y = 52, 38
    W_ALL, TOP, RH, BOT = 500, 30, 44, 34
    y0 = Y + TOP
    E = [box("Title strip", X, Y, W_ALL, TOP, None, A("wipe-right", 380, 0, out=OUT_), bg=BLACK, radius=2),
         W("Title", X, Y, W_ALL, TOP, "{notes.bugTitle|upper}", 20, A("fade", 240, 200), show="notes.bugTitle", align="center"),
         W("Title (league)", X, Y, W_ALL, TOP, "{league.name|upper}", 20, A("fade", 240, 200), show="!notes.bugTitle", align="center"),
         box("Frame", X, y0, W_ALL, 2 * RH + 4, None, A("wipe-right", 420, 80, out=OUT_), bg=GLOSS, shadow=SHADOW)]
    for i, side in enumerate(("away", "home")):
        y = y0 + 2 + i * RH
        d = 200 + i * 70
        E += [box("%s tile" % side, X + 2, y, 56, RH - 2, None, A("wipe-right", 300, d), bg=TV(side))]
        E += logo_or_abbr("%s logo" % side, X + 6, y + 3, 48, RH - 8, side, 20, A("fade", 260, d + 120), S=NB)
        E += [box("%s score bg" % side, X + 60, y, 50, RH - 2, None, A("fade", 260, d + 60), bg=WHITE),
              K_("%s runs" % side, X + 60, y, 50, RH - 2, "{%s.runs}" % side, 34, A("reveal-up", 300, d + 160, change="pop"), align="center")]
    cx = X + 114
    E += [box("Count bg", cx, y0 + 4, 104, RH - 6, None, A("fade", 260, 300), bg=BLACK, borderW=1, borderColor=EDGE, show=LIVE),
          W("Count", cx, y0 + 4, 104, RH - 6, "{balls}-{strikes}", 28, A("fade", 240, 380, change="flash"), show=LIVE, align="center"),
          box("Outs bg", cx, y0 + RH + 2, 104, RH - 6, None, A("fade", 260, 320), bg=BLACK, borderW=1, borderColor=EDGE, show=LIVE),
          el("dots", "Outs", cx, y0 + RH + 2, 104, RH - 6, A("fade", 240, 400), show=LIVE, bind="outs",
             style={"total": 3, "size": 12, "gap": 9, "on": YEL, "off": "#FFFFFF@0.22", "shape": "circle", "align": "center"}),
          W("Status", cx, y0, 214, 2 * RH, "{statusText}", 24, A("fade", 240, 360), show="!" + LIVE, align="center", wrap=True, fit=False)]
    bx = cx + 108
    E += [el("bases", "Bases", bx, y0 + 4, 104, RH - 4, A("pop", 320, 420), show=LIVE, bind="bases",
             style={"layout": "tight", "on": YEL, "off": "#5B5E66", "stroke": "#0B0B0D", "strokeW": 2}),
          W("Inning", bx, y0 + RH + 2, 104, RH - 6, "{arrow}{inning}", 24, A("fade", 240, 440, change="roll"), show=LIVE, align="center")]
    nx = bx + 108
    E += [box("Network", nx, y0 + 2, X + W_ALL - nx - 2, 2 * RH, None, A("wipe-left", 360, 360), bg=NET, show="brand.color"),
          box("Network (plain)", nx, y0 + 2, X + W_ALL - nx - 2, 2 * RH, None, A("wipe-left", 360, 360), bg=PANEL2, show="!brand.color")]
    E += net_mark("Network mark", nx + 8, y0 + 8, X + W_ALL - nx - 18, RH + 6, A("fade", 260, 520))
    E += [W("Network tag", nx, y0 + RH + 12, X + W_ALL - nx - 2, RH - 12, "{brand.short|upper}", 18, A("fade", 260, 540), show="brand.logo && brand.short",
            align="center")]
    by = y0 + 2 * RH + 4
    E += [box("Pitcher bar", X, by, W_ALL, BOT, None, A("wipe-down", 300, 500, out=OUT_), bg=TH("fielding"), show=LIVE),
          W("Pitcher", X + 14, by, 330, BOT, "{pitcher.name|initial|upper}", 22, A("fade", 240, 600, change="fade"), show=LIVE),
          W("Pitch count", X + W_ALL - 120, by, 106, BOT, "P: {pitcher.today.pc|zero}", 22, A("fade", 240, 620, change="flash"), show=LIVE, align="right")]
    E += BL.sponsor_tab(X, by + BOT + 6, 300, 40, 700, radius=2, a_type="wipe-down")
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(kind):
    """Logo tile, number / position column, first over LAST on a team-colour bar, dark four-stat panel; tag and note line."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    cols = ([("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
             ("K", "{pitcher.season.k|zero}")] if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}"), ("OPS", "{batter.season.ops|avg}")])
    tag = "{pitcher.throws|hand}" if kind == "pit" else "{batter.pos}"
    X, Y, Hh = 400, 892, 80
    TL, NC, NB_, SW = 104, 54, 330, 560
    E = [box("Tile", X, Y, TL, Hh, None, A("wipe-right", 320, 0, out=OUT_), bg=TV(team), borderW=2, borderColor="#0B0B0D", shadow=SHADOW)]
    E += logo_or_abbr("Logo", X + 10, Y + 8, TL - 20, Hh - 16, team, 30, A("zoom-out", 340, 160), S=NB)
    x = X + TL
    E += [box("Num col", x, Y, NC, Hh, None, A("wipe-right", 300, 120, out=OUT_), bg=BLACK),
          W("Number", x, Y + 4, NC, 42, "{%s.number}" % who, 32, A("fade", 240, 300), align="center"),
          W("Tag", x, Y + 44, NC, 30, tag, 20, A("fade", 240, 320), align="center", color=DIM)]
    x += NC
    E += [box("Name bar", x, Y, NB_, Hh, None, A("wipe-right", 380, 180, out=OUT_), bg=TH(team)),
          W("First", x + 18, Y + 6, NB_ - 30, 32, "{%s.first|upper}" % who, 26, A("fade", 260, 380), weight=600),
          W("Last", x + 16, Y + 34, NB_ - 30, 44, "{%s.last|upper}" % who, 38, A("reveal-up", 320, 360))]
    x += NB_
    E += [box("Stats", x, Y, SW, Hh, None, A("wipe-right", 400, 260, out=OUT_), bg=PANEL, borderW=1, borderColor=EDGE)]
    cw = SW // 4
    for i, (lab, val) in enumerate(cols):
        E += [W("%s label" % lab, x + i * cw, Y + 6, cw, 28, lab, 22, A("fade", 240, 420 + i * 50), align="center", weight=700),
              W("%s value" % lab, x + i * cw, Y + 30, cw, 46, val, 38, A("reveal-up", 300, 440 + i * 50, change="flash"), align="center")]
    E += [box("Tag tab", x + SW - 230, Y - 30, 230, 30, None, A("wipe-up", 280, 500, out=OUT_), bg=BLACK, show="notes.tab"),
          W("Tag text", x + SW - 230, Y - 30, 222, 30, "{notes.tab|upper}", 20, A("fade", 240, 560), show="notes.tab", align="right"),
          box("Note row", X + TL + NC + NB_, Y + Hh, SW, 30, None, A("wipe-down", 280, 600, out=OUT_), bg=BLACK, show="notes.stat"),
          W("Note", X + TL + NC + NB_ + 10, Y + Hh, SW - 20, 30, "{notes.stat|upper}", 19, A("fade", 240, 680), show="notes.stat", align="right", color=YEL)]
    E += BL.sponsor_tab(X + TL + NC, Y - 44, 300, 40, 640, radius=2, a_type="wipe-up")
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


# ------------------------------------------------------------------ matchup and opens
def matchup_banner():
    X, Y, W_ALL = 240, 790, 1440
    E = [box("Title bar", X, Y, W_ALL, 48, None, A("wipe-right", 400, 0, out=OUT_), bg=GLOSS, shadow=SHADOW),
         W("Title", X, Y, W_ALL, 48, "{notes.bugTitle|upper}", 30, A("fade", 260, 240), show="notes.bugTitle", align="center"),
         W("Title (league)", X, Y, W_ALL, 48, "{league.name|upper}", 30, A("fade", 260, 240), show="!notes.bugTitle", align="center")]
    half = (W_ALL - 160) // 2
    for i, side in enumerate(("away", "home")):
        x = X + (0 if i == 0 else half + 160)
        d = 160 + i * 100
        E += [box("%s block" % side, x, Y + 52, half, 104, None, A("wipe-right" if i == 0 else "wipe-left", 400, d, out=OUT_), bg=TV(side),
                  borderW=2, borderColor="#FFFFFF@0.25"),
              box("%s badge" % side, x + (20 if i == 0 else half - 140), Y + 56, 120, 96, None, A("pop", 360, d + 200), bg=BLACK, radius=48,
                  borderW=2, borderColor="#FFFFFF@0.3")]
        E += logo_or_abbr("%s logo" % side, x + (32 if i == 0 else half - 128), Y + 64, 96, 80, side, 30, A("zoom-out", 360, d + 260), S=NB)
        tx = x + (160 if i == 0 else 20)
        E += [W("%s city" % side, tx, Y + 56, half - 180, 40, "{%s.city|upper}" % side, 30, A("fade", 260, d + 300), align="center", weight=600),
              W("%s nick" % side, tx, Y + 92, half - 180, 60, "{%s.nick|upper}" % side, 50, A("reveal-up", 340, d + 320), align="center")]
    E += [box("Net", X + half, Y + 52, 160, 104, None, A("pop", 360, 300), bg=GLOSS, borderW=2, borderColor="#FFFFFF@0.25")]
    E += net_mark("Net mark", X + half + 14, Y + 66, 132, 76, A("fade", 300, 420))
    E += [box("Venue bar", X, Y + 160, W_ALL, 44, None, A("wipe-left", 400, 300, out=OUT_), bg=GLOSS),
          W("Venue", X, Y + 160, W_ALL, 44, "{venue|upper}", 28, A("fade", 260, 520), align="center")]
    return {"name": "Matchup Banner", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


def game_open():
    """Three panels: each team's colour with city and NAME, and a centre panel with the venue, the game title and a sponsor."""
    E = [box("Backdrop", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg=NB["titleBg"])]
    for i, side in enumerate(("away", "home")):
        x = 40 if i == 0 else 1290
        d = 200 + i * 150
        E += team_bg("%s panel" % side, x, 250, 590, 420, side, A("wipe-up", 460, d, out=OUT_))
        E += [box("%s rim" % side, x, 250, 590, 420, None, A("fade", 300, d), borderW=6, borderColor="#0B0B0D"),
              W("%s city" % side, x, 380, 590, 50, "{%s.city|upper}" % side, 34, A("fade", 300, d + 400), align="center", weight=600, tracking=4),
              W("%s nick" % side, x, 420, 590, 140, "{%s.nick|upper}" % side, 120, A("reveal-up", 420, d + 420), align="center")]
    E += [box("Centre", 650, 200, 620, 520, None, A("wipe-down", 460, 100, out=OUT_), bg=GLOSS, borderW=6, borderColor="#0B0B0D", shadow=SHADOW),
          W("Venue", 650, 220, 620, 50, "{venue|upper}", 30, A("fade", 300, 500), align="center", wrap=True, fit=False),
          box("Diamond", 860, 300, 200, 200, None, A("scale", 600, 600), rotate=45, borderW=4, borderColor="#FFFFFF@0.6"),
          box("Diamond in", 905, 345, 110, 110, None, A("scale", 600, 700), rotate=45, borderW=2, borderColor="#FFFFFF@0.35"),
          W("Game", 650, 560, 620, 120, "{notes.bugTitle|upper}", 84, A("reveal-up", 420, 800), show="notes.bugTitle", align="center"),
          W("Game (default)", 650, 560, 620, 120, "{away.abbr} AT {home.abbr}", 84, A("reveal-up", 420, 800), show="!notes.bugTitle", align="center"),
          box("Sponsor bg", 760, 730, 400, 110, None, A("wipe-down", 360, 1000), bg="linear-gradient(180deg, #E1342B, #B5221B)", show="sponsor.on"),
          W("Presented", 760, 734, 400, 26, "PRESENTED BY", 18, A("fade", 240, 1100), show="sponsor.on", align="center", tracking=3),
          img("Sponsor", 790, 760, 340, 74, "{sponsor.logo}", A("fade", 300, 1150), show="sponsor.on && sponsor.logo"),
          W("Sponsor name", 770, 760, 380, 74, "{sponsor.name|upper}", 40, A("fade", 300, 1150), show="sponsor.on && !sponsor.logo", align="center")]
    return {"name": "Game Open: Three Panels", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "open, show"}


def team_intro():
    """Team colour field with the logo large in the middle; city solid and NAME outlined either side."""
    E = team_bg("Field", 0, 0, 1920, 1080, "team", A("wipe-right", 500, 0, out=OUT_))
    E += [box("Shade", 0, 0, 1920, 1080, None, A("fade", 600, 100), bg="radial-gradient(ellipse at 50% 45%, transparent 30%, rgba(0,0,0,0.45) 100%)")]
    E += logo_or_abbr("Logo", 660, 220, 600, 560, "team", 220, A("zoom-out", 700, 300), S=NB)
    E += [W("City", 60, 470, 600, 110, "{team.city|upper}", 76, A("slide-right", 500, 700, dist=60), align="right"),
          W("Nick", 1260, 470, 600, 110, "{team.nick|upper}", 76, A("slide-left", 500, 800, dist=60), color="transparent", textStroke="2px #FFFFFF"),
          box("Net bg", 860, 900, 200, 80, None, A("fade", 400, 1000), show="brand.logo || brand.short || league.logo", borderW=2, borderColor="#FFFFFF@0.8", radius=6)]
    E += net_mark("Net mark", 876, 910, 168, 60, A("fade", 400, 1100))
    return {"name": "Team Intro", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E}


def show_open():
    """Show open: dark stage, team-colour banners hanging either side, the show name on a centre slab."""
    E = [box("Stage", 0, 0, 1920, 1080, None, A("fade", 500, 0, out=OUT_), bg=NB["titleBg"]),
         box("Floor lights", 0, 940, 1920, 140, None, A("fade", 600, 300), bg="repeating-linear-gradient(90deg, rgba(255,255,255,0.5) 0 10px, transparent 10px 60px)",
             opacity=0.25)]
    for i, (x, side) in enumerate(((250, "away"), (420, "home"), (1380, "away"), (1550, "home"))):
        d = 200 + i * 120
        E += [box("Banner %d" % (i + 1), x, -20, 130, 620, None, A("slide-down", 700, d, dist=200), bg=TV(side), rotate=(-4 if i < 2 else 4),
                  borderW=3, borderColor="#FFFFFF@0.5"),
              box("Banner stripe %d" % (i + 1), x, 380, 130, 30, "#FFFFFF@0.85", A("slide-down", 700, d, dist=200), rotate=(-4 if i < 2 else 4)),
              img("Banner logo %d" % (i + 1), x + 15, 440, 100, 100, "{%s.logo}" % side, A("fade", 400, d + 500), show="%s.logo" % side,
                  rotate=(-4 if i < 2 else 4))]
    E += [box("Slab", 660, 260, 600, 560, None, A("wipe-up", 600, 400), bg=GLOSS, borderW=4, borderColor="#FFFFFF@0.2", shadow=SHADOW),
          W("Show", 680, 380, 560, 220, "{show.name|upper}", 92, A("reveal-up", 500, 900), align="center", wrap=True, fit=False, lineH=0.95),
          W("Year", 680, 600, 560, 60, "{seasonYear}", 44, A("fade", 400, 1100), align="center", color=YEL, tracking=12),
          box("Rule", 860, 680, 200, 3, "#FFFFFF@0.6", A("grow-x", 400, 1200))]
    E += net_mark("Net mark", 860, 700, 200, 90, A("fade", 400, 1300))
    return {"name": "Show Open", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ player and team cards
def stat_card(kind):
    """Player over a textured team field with a black name plate; dark stat panel with title, sub, label / value rows."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    E = team_bg("Field", 0, 0, 1920, 1080, team, A("wipe-right", 460, 0, out=OUT_))
    E += [img("Photo", 60, 120, 900, 960, "{%s.photo}" % who, A("slide-up", 520, 300, dist=40), show="%s.photo" % who, fit="contain", focus="center bottom"),
          W("Number", 60, 220, 900, 600, "{%s.number}" % who, 420, A("fade", 400, 300), show="!%s.photo" % who, align="center", color="#FFFFFF@0.25",
            fit=False),
          box("Plate", 70, 820, 800, 110, None, A("wipe-right", 380, 500), bg=GLOSS, borderW=2, borderColor="#FFFFFF@0.3", shadow=SHADOW),
          W("Name", 70, 820, 800, 110, "{%s.name|upper}" % who, 70, A("reveal-up", 360, 620), align="center"),
          box("Panel", 1000, 0, 860, 1080, None, A("wipe-left", 460, 200, out=OUT_), bg=PANEL, borderW=0),
          box("Panel edge", 1000, 0, 4, 1080, "#FFFFFF@0.3", A("grow-y", 400, 300)),
          box("Head", 1004, 40, 856, 150, None, A("fade", 300, 400), bg=GLOSS),
          W("Title", 1004, 50, 856, 80, "{notes.title|upper}", 64, A("reveal-up", 360, 520), show="notes.title", align="center"),
          W("Title (default)", 1004, 50, 856, 80, "{seasonYear} SEASON", 64, A("reveal-up", 360, 520), show="!notes.title", align="center"),
          W("Sub", 1004, 128, 856, 50, "{notes.kicker|upper}", 34, A("fade", 300, 600), show="notes.kicker", align="center", color=DIM),
          el("table", "Rows", 1060, 250, 740, 600, A("none", 1, 0, rows={"type": "slide-left", "dur": 340, "stagger": 70, "delay": 700, "dist": 30}),
             bind="%s.card" % who,
             columns=[{"label": "", "field": "{row.label|upper}", "w": 2, "align": "left", "weight": 800},
                      {"label": "", "field": "value", "w": 1, "align": "right", "weight": 800}],
             style={"rowH": 96, "size": 52, "weight": 800, "color": "#FFFFFF", "header": False, "padX": 0, "gap": 0, "maxRows": 6, "font": F}),
          W("Foot", 1004, 870, 856, 60, "{notes.foot|upper}", 34, A("fade", 300, 1200), show="notes.foot", align="center", color=YEL),
          box("Net bar", 1000, 960, 860, 70, None, A("wipe-right", 380, 900), bg=GLOSS)]
    E += net_mark("Net mark", 1330, 966, 200, 58, A("fade", 300, 1000))
    return {"name": "%s Stat Card" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "pickable": True}


def team_resume():
    """Team resume: big title (team name solid, word outlined), team-colour band with three yellow lines, photo, logos below."""
    E = [box("Backdrop", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg=NB["titleBg"]),
         box("Weave", 0, 0, 1920, 1080, None, A("fade", 600, 100), bg=WEAVE),
         W("Team", 160, 70, 800, 110, "{team.nick|upper}", 86, A("slide-right", 400, 300, dist=40), align="right", font=H, weight=900),
         W("Word", 980, 70, 800, 110, "{notes.kicker|upper}", 86, A("slide-left", 400, 400, dist=40), font=H, weight=900, color="transparent",
           textStroke="2px #FFFFFF"),
         box("Band", 0, 270, 1920, 600, None, A("wipe-right", 460, 300, out=OUT_), bg=TV("team")),
         box("Band weave", 0, 270, 1920, 600, None, A("fade", 400, 500), bg=WEAVE),
         box("Photo frame", 1080, 210, 760, 720, "#0B0B0D", A("slide-up", 460, 500, dist=40), shadow=SHADOW),
         img("Photo", 1090, 220, 740, 700, "{batter.photo}", A("fade", 500, 700), show="batter.photo", fit="cover", focus="center top"),
         img("Photo logo", 1180, 330, 560, 480, "{team.logo}", A("fade", 500, 700), show="!batter.photo && team.logo"),
         W("Head", 100, 370, 940, 110, "{notes.title|upper}", 76, A("reveal-up", 400, 700)),
         W("Line 1", 120, 480, 920, 76, "{notes.b1|upper}", 56, A("slide-right", 360, 900, dist=30), show="notes.b1", color=YEL),
         W("Line 2", 120, 556, 920, 76, "{notes.b2|upper}", 56, A("slide-right", 360, 1000, dist=30), show="notes.b2", color=YEL),
         W("Line 3", 120, 632, 920, 76, "{notes.b3|upper}", 56, A("slide-right", 360, 1100, dist=30), show="notes.b3", color=YEL),
         img("Team logo", 140, 930, 260, 110, "{team.logo}", A("fade", 400, 1200), show="team.logo")]
    E += net_mark("Net mark", 1560, 940, 240, 90, A("fade", 400, 1200))
    return {"name": "Team Resume", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E}


def due_up_full():
    """Full-screen Due Up: the next batter over a textured team field, DUE UP / First (outlined) / LAST."""
    p = "team.dueUp.0"
    E = team_bg("Field", 0, 0, 1920, 1080, "team", A("wipe-right", 460, 0, out=OUT_))
    E += [img("Photo", 0, 60, 1000, 1020, "{%s.photo}" % p, A("slide-right", 520, 300, dist=60), show=p + ".photo", fit="contain", focus="center bottom"),
          W("Slot", 100, 260, 800, 560, "{%s.number}" % p, 380, A("fade", 400, 300), show="!" + p + ".photo", align="center", color="#FFFFFF@0.2", fit=False),
          W("Due up", 900, 300, 820, 90, "DUE UP", 70, A("slide-left", 400, 500, dist=40), align="right", font=H, weight=900),
          W("First", 700, 390, 1020, 150, "{%s.first|upper}" % p, 130, A("slide-left", 420, 650, dist=60), show=p + ".name", align="right", font=H,
            weight=900, color="transparent", textStroke="3px #FFFFFF"),
          W("Last", 700, 530, 1020, 170, "{%s.last|upper}" % p, 150, A("slide-left", 420, 800, dist=60), show=p + ".name", align="right", font=H,
            weight=900),
          W("Then", 700, 720, 1020, 60, "THEN {team.dueUp.1.last|upper}, {team.dueUp.2.last|upper}", 40, A("fade", 400, 1100),
            show="team.dueUp.1.name", align="right", color=DIM)]
    return {"name": "Due Up: Full Screen", "group": "full", "autoHide": 8, "side": "batting", "sided": True, "elements": E,
            "sponsorSlot": "half_{halfKey}, dueup"}


def side_matchup():
    """Studio side panel: your network mark on top, both teams' logos on stitched badges."""
    X, Y, Wd = 60, 0, 460
    E = [box("Panel", X, Y, Wd, 1080, None, A("wipe-down", 460, 0, out=OUT_), bg=PANEL, borderW=2, borderColor=EDGE),
         box("Weave", X, Y, Wd, 1080, None, A("fade", 400, 200), bg=WEAVE),
         box("Top bar", X, 50, Wd, 90, None, A("wipe-right", 360, 200), bg=GLOSS)]
    E += net_mark("Net mark", X + 130, 58, 200, 74, A("fade", 300, 400))
    for i, (side, y) in enumerate((("away", 200), ("home", 520))):
        d = 400 + i * 200
        x = X + (40 if i == 0 else 120)
        E += [box("%s badge" % side, x, y, 300, 300, None, A("pop", 420, d), bg=TV(side), radius=150, borderW=6, borderColor="#0B0B0D",
                  shadow=SHADOW),
              box("%s stitch" % side, x + 14, y + 14, 272, 272, None, A("fade", 300, d + 200), radius=136, borderW=2,
                  borderColor="#FFFFFF@0.5")]
        E += logo_or_abbr("%s logo" % side, x + 50, y + 50, 200, 200, side, 70, A("zoom-out", 400, d + 200), S=NB)
    E += [box("Bottom bar", X, 880, Wd, 60, None, A("wipe-right", 360, 800), bg=GLOSS),
          W("Bottom", X, 880, Wd, 60, "{notes.bugTitle|upper}", 28, A("fade", 260, 900), show="notes.bugTitle", align="center")]
    return {"name": "Side Panel: Matchup", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(NB, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("dueup", "inning_sponsor", "lineup", "pitching", "defense", "linescore", "spotlight", "note", "matchup", "standings", "custom", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g.update(SL.all_sports(MS))
CUSTOM_G = {"scorebug": scorebug(), "batter": lower("bat"), "pitcher": lower("pit"), "matchup_banner": matchup_banner(), "nb_open": game_open(),
            "nb_team_intro": team_intro(), "nb_show_open": show_open(), "batter_card": stat_card("bat"), "pitcher_card": stat_card("pit"),
            "nb_resume": team_resume(), "nb_dueup": due_up_full(), "nb_side_matchup": side_matchup()}
g.update(CUSTOM_G)
CUSTOM = set(CUSTOM_G)


def kit_tr(gid, g_, TA):
    """Team colour field with the woven texture, a glossy black band with the word, your network mark."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=TV("team")),
         box("Weave", 0, 0, 1920, 1080, None, TA("fade", 400, 80), bg=WEAVE),
         box("Band", 0, 400, 1920, 260, None, TA("wipe-right", 420, 120), bg=GLOSS, borderW=0),
         box("Rule top", 0, 396, 1920, 4, "#FFFFFF@0.4", TA("grow-x", 360, 200)),
         box("Rule bottom", 0, 660, 1920, 4, "#FFFFFF@0.4", TA("grow-x", 360, 240))]
    return {"elements": E, "word": {"font": H, "weight": 900, "color": "#FFFFFF", "textShadow": "", "rect": (60, 410, 1800, 190)},
            "sub": {"font": F, "weight": 800, "color": YEL, "textShadow": "", "rect": (60, 680, 1800, 80), "tracking": 3},
            "brand": {"rect": (860, 160, 200, 180)}}


def kit_slab(R, slab, g_):
    x, y, w, h = R
    return [box("Rule top", 0, y - 6, 1920, 6, "#0B0B0D", A("grow-x", 300, 100)),
            box("Rule bottom", 0, y + h, 1920, 6, "#0B0B0D", A("grow-x", 300, 140)),
            dict(box("Weave", 0, y, 1920, h, None, A("fade", 300, 200), bg=WEAVE), _over=True)]


def kit_screen(bg, team, g_):
    over = [box("Weave", 0, 0, 1920, 1080, None, A("fade", 500, 100), bg=WEAVE)]
    return {"floor": PANEL2, "replace": NB["titleBg"], "over": over}


KIT = RB.make_kit(dict(
    screen=kit_screen, slab=kit_slab,
    body=PANEL, bodyBox={"radius": 2, "borderW": 2, "borderColor": EDGE, "shadow": SHADOW},
    headTile=lambda t: TV(t) if t else BLACK, head=GLOSS, headRule="#FFFFFF@0.3", sub=BLACK,
    title={"font": F, "weight": 800, "color": "#FFFFFF", "textShadow": "", "italic": False},
    headText={"textShadow": ""}, subText={"font": F, "weight": 700, "color": DIM, "textShadow": "", "tracking": 1},
    roles={"PANEL": PANEL, "PANEL2": PANEL2, "DARK": BLACK, "STRIP": WHITE}, barBox={"radius": 2}, mainBox={"shadow": SHADOW},
    tile={"radius": 2, "borderW": 2, "borderColor": "#0B0B0D"}, tr=kit_tr))
SKIN = dict(panel=PANEL, panel2=PANEL2, dark=BLACK, strip=WHITE, stripText=INK, val=WHITE, ink=INK, hi=YEL, hiText=INK, hiDark=True, line="#FFFFFF@0.14",
            title=NB["titleBg"], shadow=SHADOW, team=TV, rule="#FFFFFF@0.4", text2="#FFFFFF", radius=2, noBlur=True,
            panelBox={"radius": 2, "borderW": 2, "borderColor": EDGE, "shadow": SHADOW}, lightBox={"radius": 2}, hiBox={"radius": 2},
            text={"textShadow": ""}, textDark={"textShadow": ""})
g = RB.rebuild_all(g, KIT, only=set(g) - CUSTOM)
g = RB.strip_flags(SK.skin_all(g, SKIN, only=set(g) - CUSTOM))
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
for k, d in g.items():
    if not d.get("layout") and "National Broadcast 1" not in d.get("name", ""):
        d["name"] = "%s (National Broadcast 1)" % d.get("name", k)

theme = dict(night_doc["theme"])
theme.update({"primary": "#0C0D0F", "accent": YEL, "text": "#FFFFFF", "dim": "rgba(255,255,255,0.75)", "line": "rgba(255,255,255,0.14)",
              "card": "rgba(14,14,16,0.95)", "panel": "rgba(14,14,16,0.95)", "panel2": "rgba(38,39,44,0.95)"})
doc = {"version": 2, "name": "National Broadcast 1",
       "description": "National postseason TV look: glossy black bars, team-colour tiles and woven team fields, white score boxes, yellow notes, "
                      "outlined type. Series-title scorebug with a network block, four-stat lower thirds, matchup banner, three-panel game open, "
                      "team intro, full-screen Due Up, player stat cards, team resume, studio side panel and show open. Network spots use your "
                      "broadcaster logo and colours. Every graphic type, plus basketball, football and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "national-broadcast-1.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, separators=(",", ":"))
print("wrote", out, "graphics:", len(g))
