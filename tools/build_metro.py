"""Builds the "Metro Chrome" package: templates/packages/metro-chrome.json.

Late-2000s regional-network look, from Rob's reference frames: blue chrome rails with orange chevrons at the end,
glossy black "puffy" logo tiles, gunmetal name plates with a silver sheen, orange highlight for the featured row,
rounded stat pills (value over a silver label), a long top scorebug rail. No network or team marks are included.
Run:  python tools/build_metro.py   (after tools/build_night_game.py)
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

RAIL = "linear-gradient(180deg, #E3EAF4 0%, #93A8CC 16%, #34558F 48%, #1C376F 70%, #0E2048 100%)"
RAIL_D = "linear-gradient(180deg, #9AA1AC 0%, #50565F 18%, #24272D 55%, #121418 100%)"
PLATE = ("linear-gradient(180deg, rgba(255,255,255,0.28) 0%, rgba(255,255,255,0.06) 48%, rgba(0,0,0,0) 52%), "
         "linear-gradient(90deg, #8F96A1 0%, #3B4047 40%, #1D1F24 100%)")
PLATE_D = "linear-gradient(180deg, #5E636C 0%, #2E3137 46%, #17191D 54%, #24272C 100%)"
TILE = "radial-gradient(ellipse at 50% 0%, #70747C 0%, #2A2C31 42%, #0A0B0D 100%)"
SILVER = "linear-gradient(180deg, #FFFFFF 0%, #DADFE6 45%, #A9B0BB 100%)"
ORANGE = "linear-gradient(180deg, #FFC75A 0%, #F68B1F 50%, #C55A0B 100%)"
BLUE_P = "linear-gradient(180deg, #4E74C0 0%, #24468F 50%, #142C63 100%)"
INK = "#15171B"
SH = "0 2px 3px rgba(0,0,0,0.75)"
TEAM = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 78%%, #fff) 0%%, {%s.color} 50%%, "
        "color-mix(in srgb, {%s.color} 60%%, #000) 100%%)")

MC = dict(BL.NETWORK, key="metro", font="$font", body="$font", up=True, radius=8, cardRadius=10,
          panel=PLATE_D, panel2=RAIL_D, dark="#0E0F12", strip=SILVER, stripText=INK, val=SILVER, valText=INK,
          hi="#F68B1F", hiText="#15171B", line="#FFFFFF@0.2", shadow="0 10px 24px rgba(0,0,0,.6)", cardIn="zoom-out",
          teamGrad=TEAM, titleBg="radial-gradient(ellipse at 60% 20%, #4E74C0, #1C376F 50%, #0B1530 100%)")
F = "$font"
LIVE = "inPlay"
OUT_ = {"type": "fade", "dur": 240, "delay": 0, "ease": "in"}


def W_(name, x, y, w, h, text, size, a, show=None, **st):
    st.setdefault("font", F)
    st.setdefault("weight", 800)
    return txt(name, x, y, w, h, text, size, a, show=show, textShadow=SH, **st)


def tile(name, x, y, w, h, src, show, a, d=0):
    """Glossy black rounded logo tile."""
    return [box(name, x, y, w, h, None, a, bg=TILE, radius=16, borderW=2, borderColor="#A2A8B2", shadow="0 8px 18px rgba(0,0,0,.6)"),
            img(name + " logo", x + 12, y + 10, w - 24, h - 20, src, A("zoom-out", 380, d + 200), show=show)]


def chevrons(x, y, h, color="#F68B1F", delay=0):
    E = []
    for i in range(4):
        E.append(txt("Chevron %d" % i, x + i * 26, y, 40, h, "❯", int(h * 0.95), A("slide-right", 260, delay + i * 60, dist=20), font=F, weight=800,
                     color=color, opacity=None, align="center"))
        E[-1]["opacity"] = 0.4 + 0.2 * i
    return E


def rail(X, Y, W, Hh, title, delay=0, logo="{team.logo}", logo_show="team.logo", tile_x=None, size=40):
    """Blue chrome header rail with a glossy logo tile and orange chevrons."""
    tx = X + 150 if tile_x is None else tile_x
    E = [box("Rail", X, Y, W, Hh, None, A("wipe-right", 440, delay, out=OUT_), bg=RAIL, shadow="0 6px 16px rgba(0,0,0,.5)",
             borderW=1, borderColor="#FFFFFF@0.5")]
    E += tile("Tile", tx - 130, Y - 18, 120, Hh + 36, logo, logo_show, A("pop", 380, delay + 160), delay)
    E += [W_("Title", tx + 10, Y, W - (tx - X) - 160, Hh, title, size, A("fade", 260, delay + 300))]
    E += chevrons(X + W - 120, Y, Hh, delay=delay + 400)
    return E


# ------------------------------------------------------------------ scorebug
def scorebug():
    """Top rail with silver end caps: logo + abbreviation | score for each team, inning in orange, diamond, outs, speed, brand."""
    X, Y, W, Hh = 330, 28, 1260, 56
    E = [box("Cap L", X - 14, Y - 4, 22, Hh + 8, None, A("fade", 300, 0), bg=SILVER, radius=4),
         box("Cap R", X + W - 8, Y - 4, 22, Hh + 8, None, A("fade", 300, 0), bg=SILVER, radius=4),
         box("Rail", X, Y, W, Hh, None, A("wipe-center", 440, 60, out=OUT_), bg=RAIL, shadow="0 6px 16px rgba(0,0,0,.5)")]
    x = X + 22
    for i, side in enumerate(("away", "home")):
        d = 200 + i * 80
        E += [box("%s box" % side, x, Y + 8, 220, Hh - 16, None, A("pop", 300, d), bg="#0E0F12", radius=8, borderW=1, borderColor="#FFFFFF@0.35")]
        E += logo_or_abbr("%s logo" % side, x + 8, Y + 11, 46, Hh - 22, side, 16, A("fade", 240, d + 120), S=MC)
        E += [W_("%s abbr" % side, x + 58, Y + 8, 90, Hh - 16, "{%s.abbr|upper}" % side, 28, A("fade", 240, d + 140)),
              box("%s sep" % side, x + 150, Y + 14, 2, Hh - 28, "#FFFFFF@0.5", A("grow-y", 220, d + 160)),
              W_("%s runs" % side, x + 152, Y + 8, 66, Hh - 16, "{%s.runs}" % side, 32, A("fade", 240, d + 180, change="pop"), align="center")]
        x += 240
    E += [box("Inning box", x, Y + 8, 110, Hh - 16, None, A("pop", 300, 360), bg="#0E0F12", radius=8, borderW=1, borderColor="#FFFFFF@0.35"),
          txt("Inning", x, Y + 8, 110, Hh - 16, "{arrow}{inningOrd}", 28, A("fade", 240, 460, change="flash"), show=LIVE, font=F, weight=800,
              align="center", color="#F68B1F"),
          txt("Status", x, Y + 8, 110, Hh - 16, "{statusText}", 22, A("fade", 240, 460), show="!" + LIVE, font=F, weight=800, align="center",
              color="#F68B1F")]
    x += 124
    E += [box("Diamond", x + 10, Y - 6, Hh + 12, Hh + 12, None, A("pop", 360, 400), bg=SILVER, rotate=45, borderW=2, borderColor="#5A606A"),
          el("bases", "Bases", x + 2, Y + 4, Hh + 28, Hh - 8, A("pop", 360, 480), show=LIVE, bind="bases",
             style={"layout": "tight", "on": "#F68B1F", "off": "#3A3E45", "stroke": "#111111", "strokeW": 2})]
    x += Hh + 40
    E += [box("Outs box", x, Y + 8, 150, Hh - 16, None, A("pop", 300, 440), bg="#0E0F12", radius=8, borderW=1, borderColor="#FFFFFF@0.35"),
          W_("Outs", x, Y + 8, 150, Hh - 16, "{outs} {outsWord|upper}", 24, A("fade", 240, 520, change="flash"), show=LIVE, align="center"),
          box("Count box", x + 164, Y + 8, 90, Hh - 16, None, A("pop", 300, 460), bg="#0E0F12", radius=8, borderW=1, borderColor="#FFFFFF@0.35"),
          W_("Count", x + 164, Y + 8, 90, Hh - 16, "{count}", 24, A("fade", 240, 540, change="flash"), show=LIVE, align="center"),
          box("Speed box", x + 268, Y + 8, 140, Hh - 16, None, A("pop", 300, 480), bg="#0E0F12", radius=8, borderW=1, borderColor="#FFFFFF@0.35",
              show=both(LIVE, "velo.ps")),
          W_("Speed", x + 268, Y + 8, 140, Hh - 16, "{velo.ps} MPH", 24, A("fade", 240, 560, change="flash"), show=both(LIVE, "velo.ps"), align="center"),
          img("Brand", X + W - 150, Y + 8, 136, Hh - 16, "{brand.logo}", A("fade", 300, 600), show="brand.logo"),
          W_("Brand t", X + W - 150, Y + 8, 136, Hh - 16, "{brand.short|upper}", 28, A("fade", 300, 600), show="!brand.logo && brand.short",
             align="center", italic=True)]
    E += sponsor_tab(X + W - 320, Y + Hh + 10, 320, 40, 640, radius=8, a_type="wipe-down")
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def pill(name, x, y, w, val, lab, d):
    return [box(name + " top", x, y, w, 52, None, A("pop", 300, d), bg=PLATE_D, radius=8, borderW=2, borderColor="#B8BEC8"),
            W_(name + " v", x, y, w, 52, val, 34, A("fade", 240, d + 80, change="flash"), align="center"),
            box(name + " bottom", x + 4, y + 50, w - 8, 28, None, A("wipe-down", 240, d + 60), bg=SILVER, radius=4),
            txt(name + " l", x + 4, y + 50, w - 8, 28, lab, 20, A("fade", 220, d + 120), font=F, weight=800, align="center", color=INK)]


def lower(kind):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    cols = ([("{pitcher.season.era|era}", "ERA"), ("{pitcher.season.w|zero}-{pitcher.season.l|zero}", "W-L"), ("{pitcher.today.ip|dash}", "IP"),
             ("{pitcher.today.k|zero}", "SO")] if kind == "pit" else
            [("{batter.season.avg|avg}", "AVG"), ("{batter.season.hr|zero}", "HR"), ("{batter.season.rbi|zero}", "RBI"), ("{batter.season.obp|avg}", "OBP")])
    X, Y, W = 0, 830, 1500
    E = rail(X, Y, W, 58, "{%s.name|upper}" % who, logo="{%s.logo}" % team, logo_show="%s.logo" % team, tile_x=490, size=40)
    E.insert(len(E) - 4, W_("Tag", 1100, Y, 180, 58, ("{pitcher.throws|hand}" if kind == "pit" else "{batter.pos}"), 34, A("fade", 260, 360)))
    for i, (val, lab) in enumerate(cols):
        E += pill("Stat %d" % i, 590 + i * 196, Y + 72, 180, val, lab, 420 + i * 80)
    E += sponsor_tab(1220, Y - 46, 300, 40, 640, radius=8, a_type="wipe-up")
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def custom_lower():
    X, Y = 0, 860
    E = rail(X, Y, 1500, 58, "{custom.line1|upper}", logo="{brand.logo}", logo_show="brand.logo", tile_x=490, size=36)
    E += [box("Plate", 520, Y + 70, 900, 46, None, A("wipe-right", 360, 300), bg=PLATE, radius=8, show="custom.line2", borderW=1,
              borderColor="#FFFFFF@0.35"),
          W_("Line 2", 544, Y + 70, 860, 46, "{custom.line2|upper}", 26, A("fade", 240, 420), show="custom.line2")]
    return {"name": "Custom Lower Third", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ lineup / defense
def lineup():
    """Header rail, then a plate per hitter (position box, name, bats chip), the current hitter in orange and larger,
    a photo frame with a caption plate, and a sponsor plate."""
    X, Y = 300, 100
    E = rail(0, Y, 1460, 66, "STARTING LINEUP", tile_x=450, size=42)
    E += [box("Spine", X + 140, Y + 66, 640, 9 * 64 + 20, "#0E0F12@0.55", A("fade", 300, 200))]
    for i in range(9):
        p = "team.lineup.%d" % i
        y = Y + 82 + i * 64
        d = 360 + i * 60
        cur = p + ".isCurrent"
        E += [box("Pos %d" % i, X + 150, y, 70, 54, "#0E0F12", A("wipe-right", 240, d), show=both(p + ".name", "!" + cur), radius=6),
              box("Pos hi %d" % i, X + 150, y - 4, 86, 62, None, A("wipe-right", 240, d), show=both(p + ".name", cur), bg=ORANGE, radius=6),
              W_("Pos t %d" % i, X + 150, y, 70, 54, "{%s.pos}" % p, 30, A("fade", 220, d + 60), show=p + ".name", align="center"),
              box("Plate %d" % i, X + 224, y, 480, 54, None, A("wipe-right", 300, d + 40), show=both(p + ".name", "!" + cur), bg=PLATE, radius=6,
                  borderW=1, borderColor="#FFFFFF@0.3"),
              box("Plate hi %d" % i, X + 240, y - 4, 560, 62, None, A("wipe-right", 300, d + 40), show=both(p + ".name", cur), bg=PLATE, radius=6,
                  borderW=2, borderColor="#F68B1F"),
              W_("Name %d" % i, X + 260, y, 430, 54, "{%s.name|upper}" % p, 32, A("fade", 220, d + 100), show=p + ".name"),
              box("Bats %d" % i, X + 724, y + 10, 36, 34, "#0E0F12", A("pop", 220, d + 120), show=both(p + ".name", p + ".bats", "!" + cur), radius=5,
                  borderW=1, borderColor="#FFFFFF@0.6"),
              W_("Bats t %d" % i, X + 724, y + 10, 36, 34, "{%s.bats}" % p, 20, A("fade", 220, d + 140), show=both(p + ".name", p + ".bats", "!" + cur),
                 align="center")]
    E += [box("Photo frame", X + 840, Y + 120, 240, 240, None, A("pop", 360, 800), bg=TILE, radius=14, borderW=2, borderColor="#A2A8B2"),
          img("Photo", X + 852, Y + 132, 216, 216, "{picked.bat.photo}", A("fade", 300, 900), show="picked.bat.photo", fit="cover", focus="center top"),
          img("Logo", X + 872, Y + 152, 176, 176, "{team.logo}", A("fade", 300, 900), show="!picked.bat.photo && team.logo"),
          box("Caption", X + 830, Y + 372, 260, 110, "#0E0F12", A("wipe-down", 300, 1000), show="notes.lfLine", radius=10, borderW=2,
              borderColor="#A2A8B2"),
          W_("Caption t", X + 840, Y + 376, 240, 102, "{notes.lfTitle|upper}\n{notes.lfLine|upper}", 24, A("fade", 240, 1100), show="notes.lfLine",
             align="center", wrap=True, fit=False, lineH=1.15, whiteSpace="pre-line"),
          box("Sponsor plate", X + 150, Y + 82 + 9 * 64 + 16, 220, 80, None, A("pop", 300, 1000), show="sponsor.on", bg=SILVER, radius=12,
              borderW=2, borderColor="#5A606A"),
          img("Sponsor", X + 166, Y + 82 + 9 * 64 + 26, 188, 60, "{sponsor.logo}", A("fade", 260, 1100), show="sponsor.on && sponsor.logo")]
    return {"name": "Lineup", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E, "sponsorSlot": "lineup"}


def defense():
    X, Y = 420, 110
    E = rail(0, Y, 1500, 66, "STARTING DEFENSE", tile_x=520, size=42)
    E += [box("Panel", X, Y + 66, 1100, 640, None, A("fade", 400, 200), bg="linear-gradient(180deg, #2A2D33, #101114)", borderW=2,
              borderColor="#5A606A"),
          el("field", "Field", X + 20, Y + 86, 1060, 600, A("fade", 500, 300, rows={"type": "pop", "dur": 360, "stagger": 70, "delay": 500}),
             bind="team.defense",
             style={"grass": "#2E6B3A", "dirt": "#B88A5A", "line": "#FFFFFF@0.8", "labelFill": "#1D1F24", "nameColor": "#FFFFFF",
                    "posColor": "#F68B1F", "size": 28, "nameField": "last"}),
          box("Note", X - 10, Y + 716, 820, 50, None, A("wipe-right", 300, 900), show="notes.foot", bg=PLATE, radius=6, borderW=1,
              borderColor="#FFFFFF@0.4"),
          box("Note chip", X, Y + 726, 26, 30, None, A("pop", 220, 1000), show="notes.foot", bg=ORANGE, radius=4),
          W_("Note t", X + 40, Y + 716, 760, 50, "{notes.foot|upper}", 26, A("fade", 240, 1000), show="notes.foot")]
    return {"name": "Starting Defense", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": E}


# ------------------------------------------------------------------ matchups
def band(Y, H_):
    """Horizontal chrome band across the screen with chevrons pointing in from both sides."""
    E = [box("Band", 0, Y, 1920, H_, None, A("wipe-center", 460, 0, out=OUT_), bg=RAIL_D, borderW=1, borderColor="#FFFFFF@0.35"),
         box("Band rail top", 0, Y, 1920, 10, None, A("grow-x", 400, 100), bg=RAIL),
         box("Band rail bottom", 0, Y + H_ - 10, 1920, 10, None, A("grow-x", 400, 100), bg=RAIL)]
    for i in range(3):
        E.append(txt("In L %d" % i, 30 + i * 60, Y, 60, H_, "❯", int(H_ * 0.6), A("slide-right", 300, 200 + i * 60, dist=30), font=F, weight=800,
                     color="#6E8FD0"))
        E.append(txt("In R %d" % i, 1830 - i * 60, Y, 60, H_, "❮", int(H_ * 0.6), A("slide-left", 300, 200 + i * 60, dist=30), font=F, weight=800,
                     color="#6E8FD0"))
    return E


def matchup():
    Y, H_ = 640, 190
    E = band(Y, H_)
    for i, side in enumerate(("away", "home")):
        x = 310 if i == 0 else 970
        d = 300 + i * 160
        bg = PLATE_D if i == 0 else BLUE_P
        al = "right"
        E += [box("%s panel" % side, x, Y + 16, 640, H_ - 32, None, A("wipe-right" if i == 0 else "wipe-left", 380, d), bg=bg, radius=4,
                  borderW=2, borderColor="#FFFFFF@0.45")]
        E += tile("%s tile" % side, (x + 20) if i == 0 else (x + 400), Y - 120, 220, 150, "{%s.logo}" % side, "%s.logo" % side, A("pop", 360, d + 100), d)
        tx, tw = (330, 540) if i == 0 else (1050, 540)
        al = "right" if i == 0 else "left"
        E += [W_("%s city" % side, tx, Y + 26, tw, 40, "{%s.city|upper}" % side, 34, A("fade", 240, d + 200), align=al),
              W_("%s nick" % side, tx, Y + 60, tw, 76, "{%s.nick|upper}" % side, 70, A("reveal-up", 320, d + 240), align=al),
              W_("%s rec" % side, tx, Y + 132, tw, 36, "({%s.record})" % side, 28, A("fade", 240, d + 300), show="%s.record" % side, align=al)]
    E += [box("Puck", 890, Y + 50, 140, 90, None, A("pop", 360, 700), bg=TILE, radius=45, borderW=3, borderColor="#C9CED6"),
          img("Puck logo", 905, Y + 60, 110, 70, "{brand.logo}", A("fade", 300, 800), show="brand.logo"),
          W_("Puck t", 905, Y + 60, 110, 70, "VS", 40, A("fade", 300, 800), show="!brand.logo", align="center"),
          box("Venue", 560, Y + H_ + 14, 800, 48, None, A("wipe-center", 320, 900), show="venue", bg=PLATE, radius=6, borderW=2, borderColor="#C9CED6"),
          W_("Venue t", 560, Y + H_ + 14, 800, 48, "{venue|upper}", 28, A("fade", 240, 1000), show="venue", align="center")]
    return {"name": "Matchup", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def starters():
    """Starting pitchers across the band: each starter's photo above his panel, first name, big last name, record and ERA."""
    Y, H_ = 640, 190
    E = band(Y, H_)
    for i, side in enumerate(("away", "home")):
        x = 380 if i == 0 else 970
        d = 300 + i * 160
        E += [box("%s panel" % side, x, Y + 16, 580, H_ - 32, None, A("wipe-right" if i == 0 else "wipe-left", 380, d),
                  bg=PLATE_D if i == 0 else BLUE_P, radius=4, borderW=2, borderColor="#FFFFFF@0.45"),
              img("%s photo" % side, x + (20 if i == 0 else 330), Y - 160, 230, 190, "{%s.sp.photo}" % side, A("slide-up", 400, d + 120, dist=30),
                  show="%s.sp.photo" % side, fit="contain", focus="center bottom")]
        tx = x + 40
        al = "right" if i == 0 else "left"
        E += [W_("%s first" % side, tx, Y + 24, 500, 40, "{%s.sp.first|upper}" % side, 32, A("fade", 240, d + 200), align=al),
              W_("%s last" % side, tx, Y + 58, 500, 76, "{%s.sp.last|upper}" % side, 66, A("reveal-up", 320, d + 240), align=al),
              W_("%s line" % side, tx, Y + 128, 500, 40, "{%s.sp.record} {%s.sp.era|era} ERA" % (side, side), 30, A("fade", 240, d + 300),
                 show="%s.sp.name" % side, align=al)]
    return {"name": "Starting Pitchers", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ other full screens
def standings():
    X, Y, RH = 380, 110, 62
    E = rail(0, Y, 1540, 66, "{standingsGroup.name|upper}", logo="{league.logo}", logo_show="league.logo", tile_x=500, size=42)
    for lab, x in (("W", 760), ("L", 860), ("PCT", 960), ("GB", 1080)):
        E.append(W_("Head " + lab, X + x, Y + 80, 100, 40, lab, 26, A("fade", 240, 400), align="center"))
    for i in range(10):
        p = "standingsGroup.teams.%d" % i
        y = Y + 128 + i * RH
        d = 400 + i * 60
        E += [box("Rank %d" % i, X + 120, y, 60, RH - 8, None, A("wipe-right", 240, d), show=p + ".name", bg=ORANGE, radius=6),
              W_("Rank t %d" % i, X + 120, y, 60, RH - 8, "{%s.rank}" % p, 30, A("fade", 220, d + 60), show=p + ".name", align="center"),
              box("Plate %d" % i, X + 186, y, 1010, RH - 8, None, A("wipe-right", 300, d + 40), show=p + ".name", bg=PLATE, radius=6, borderW=1,
                  borderColor="#FFFFFF@0.3"),
              img("Logo %d" % i, X + 196, y + 4, 60, RH - 16, "{%s.logo}" % p, A("fade", 220, d + 80), show=both(p + ".name", p + ".logo")),
              W_("Team %d" % i, X + 270, y, 480, RH - 8, "{%s.name|upper}" % p, 30, A("fade", 220, d + 100), show=p + ".name")]
        for k, x in (("w", 760), ("l", 860), ("pct", 960), ("gb", 1080)):
            E.append(W_("%s %d" % (k, i), X + x, y, 100, RH - 8, "{%s.%s}" % (p, k), 30, A("fade", 220, d + 120), show=p + ".name", align="center",
                        color="#F68B1F" if k == "gb" else "#FFFFFF"))
    return {"name": "Standings", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


def due_up():
    X, Y = 0, 780
    E = rail(X, Y, 1300, 58, "DUE UP", tile_x=430, size=38)
    for i in range(3):
        p = "team.dueUp.%d" % i
        y = Y + 70 + i * 58
        d = 360 + i * 100
        E += [box("Slot %d" % i, 450, y, 60, 50, "#0E0F12", A("wipe-right", 240, d), show=p + ".name", radius=6),
              W_("Slot t %d" % i, 450, y, 60, 50, "{%s.slot}" % p, 28, A("fade", 220, d + 60), show=p + ".name", align="center"),
              box("Plate %d" % i, 516, y, 620, 50, None, A("wipe-right", 300, d + 40), show=p + ".name", bg=PLATE, radius=6, borderW=1,
                  borderColor="#FFFFFF@0.3"),
              W_("Name %d" % i, 540, y, 440, 50, "{%s.name|upper}" % p, 30, A("fade", 220, d + 100), show=p + ".name"),
              W_("Avg %d" % i, 980, y, 140, 50, "{%s.avg|avg}" % p, 28, A("fade", 220, d + 120), show=p + ".name", align="right", color="#F68B1F")]
    return {"name": "Due Up", "group": "lower", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "half_{halfKey}, dueup"}


def feature():
    X, Y = 300, 150
    E = rail(0, Y, 1500, 66, "{notes.title|upper}", tile_x=440, size=42)
    E[-5]["showIf"] = "notes.title"
    E.append(W_("Title name", 450, Y, 900, 66, "{batter.name|upper}", 42, A("fade", 260, 300), show="!notes.title"))
    E += [box("Kicker", X + 140, Y + 80, 900, 46, None, A("wipe-right", 300, 300), show="notes.kicker", bg=ORANGE, radius=6),
          txt("Kicker t", X + 160, Y + 80, 860, 46, "{notes.kicker|upper}", 26, A("fade", 240, 400), show="notes.kicker", font=F, weight=800,
              color=INK)]
    for i in range(3):
        k = "notes.b%d" % (i + 1)
        y = Y + 146 + i * 110
        E += [box("Plate %d" % i, X + 140, y, 900, 96, None, A("wipe-right", 300, 500 + i * 120), show=k, bg=PLATE, radius=8, borderW=1,
                  borderColor="#FFFFFF@0.3"),
              W_("Text %d" % i, X + 170, y, 850, 96, "{%s|upper}" % k, 36, A("fade", 240, 600 + i * 120), show=k, wrap=True, fit=False, lineH=1.05)]
    E += [box("Photo frame", X + 1080, Y + 100, 300, 360, None, A("pop", 360, 700), bg=TILE, radius=14, borderW=2, borderColor="#A2A8B2"),
          img("Photo", X + 1094, Y + 114, 272, 332, "{batter.photo}", A("fade", 300, 800), show="batter.photo", fit="cover", focus="center top"),
          img("Logo", X + 1110, Y + 160, 240, 240, "{team.logo}", A("fade", 300, 800), show="!batter.photo && team.logo"),
          box("Foot", X + 140, Y + 486, 1240, 50, "#0E0F12", A("wipe-right", 300, 1000), show="notes.foot", radius=8, borderW=1,
              borderColor="#FFFFFF@0.4"),
          W_("Foot t", X + 160, Y + 486, 1200, 50, "{notes.foot|upper}", 26, A("fade", 240, 1100), show="notes.foot", align="center")]
    return {"name": "Feature Card", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "feature"}


def linescore():
    TW, CW, RW, RH = 190, 66, 78, 58
    W = TW + 9 * CW + 3 * RW
    X, Y = (1920 - W) // 2, 840
    E = [box("Head", X, Y, W, 34, None, A("wipe-right", 360, 0, out=OUT_), bg=RAIL, radius=6),
         W_("Status", X + 12, Y, TW - 12, 34, "{statusText}", 20, A("fade", 220, 200), color="#F68B1F")]
    for i in range(9):
        E.append(W_("Inn %d" % (i + 1), X + TW + i * CW, Y, CW, 34, str(i + 1), 22, A("fade", 220, 200 + i * 20), align="center"))
    for j, lab in enumerate(("R", "H", "E")):
        E.append(W_("Head " + lab, X + TW + 9 * CW + j * RW, Y, RW, 34, lab, 24, A("fade", 220, 400), align="center"))
    for r, side in enumerate(("away", "home")):
        y = Y + 40 + r * (RH + 6)
        d = 200 + r * 120
        E += [box("%s plate" % side, X, y, TW + 9 * CW, RH, None, A("wipe-right", 380, d), bg=PLATE, radius=6, borderW=1, borderColor="#FFFFFF@0.3")]
        E += logo_or_abbr("%s logo" % side, X + 8, y + 6, 54, RH - 12, side, 18, A("fade", 220, d + 120), S=MC)
        E += [W_("%s abbr" % side, X + 70, y, TW - 76, RH, "{%s.abbr|upper}" % side, 30, A("fade", 220, d + 160)),
              box("%s totals" % side, X + TW + 9 * CW + 6, y, 3 * RW - 6, RH, None, A("wipe-right", 300, d + 160), bg=PLATE_D, radius=6, borderW=1,
                  borderColor="#F68B1F@0.7")]
        for i in range(9):
            E.append(W_("%s %d" % (side, i + 1), X + TW + i * CW, y, CW, RH, "{linescore.%s.%d}" % (side, i), 30, A("fade", 220, d + 200 + i * 25,
                        change="flash"), align="center"))
        for j, k in enumerate(("runs", "hits", "errors")):
            E.append(W_("%s %s" % (side, k), X + TW + 9 * CW + 6 + j * RW, y, RW - 2, RH, "{%s.%s}" % (side, k), 32, A("fade", 220, d + 400 + j * 40,
                        change="pop"), align="center"))
    return {"name": "Linescore", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


def ticker():
    Y, HH = 1022, 50
    E = [box("Bar", 0, Y - 4, 1920, HH + 8, None, A("wipe-up", 400, 0, out={"type": "wipe-down", "dur": 300, "delay": 0, "ease": "in"}), bg=RAIL_D),
         box("Rail", 0, Y - 4, 1920, 6, None, A("grow-x", 300, 100), bg=RAIL),
         box("Label", 24, Y + 4, 200, HH - 8, None, A("pop", 300, 200), bg=ORANGE, radius=6),
         txt("Label t", 24, Y + 4, 200, HH - 8, "{ticker.label|upper}", 26, A("fade", 240, 300), show="ticker.label", font=F, weight=800, align="center",
             color=INK),
         txt("League t", 24, Y + 4, 200, HH - 8, "{league.name|upper}", 22, A("fade", 240, 300), show="!ticker.label && league.name", font=F,
             weight=800, align="center", color=INK),
         el("ticker", "Crawl", 240, Y, 1480, HH, A("fade", 400, 400), bind="ticker.items",
            style={"size": 28, "weight": 800, "color": "#FFFFFF", "font": F, "speed": 110, "headFill": "#F68B1F", "headColor": INK, "upper": True}),
         img("Brand", 1736, Y + 4, 160, HH - 8, "{brand.logo}", A("fade", 300, 500), show="brand.logo")]
    return {"name": "Bottom Ticker", "group": "ticker", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(MC, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("inning_sponsor", "pitching", "spotlight", "note", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g.update({"scorebug": scorebug(), "batter": lower("bat"), "pitcher": lower("pit"), "custom": custom_lower(), "lineup": lineup(),
          "defense": defense(), "matchup": matchup(), "sp_compare": starters(), "standings": standings(), "dueup": due_up(),
          "feature": feature(), "linescore": linescore(), "ticker": ticker()})
g.update(SL.all_sports(MS))
CUSTOM = ("scorebug", "batter", "pitcher", "custom", "lineup", "defense", "matchup", "sp_compare", "standings", "dueup", "feature", "linescore", "ticker")
K = dict(panel=PLATE_D, panel2=PLATE, dark="#0E0F12", strip=SILVER, stripText=INK, val=SILVER, ink=INK, hi=ORANGE, hiText=INK, hiDark=True,
         line="#FFFFFF@0.25", title=MC["titleBg"], shadow=MC["shadow"], team=lambda t: TEAM % (t, t, t), rule="#F68B1F", text2="#FFFFFF", radius=8,
         noBlur=True, panelBox={"radius": 8, "borderW": 1, "borderColor": "#FFFFFF@0.35", "shadow": MC["shadow"]},
         lightBox={"radius": 8, "borderW": 2, "borderColor": "#5A606A"}, hiBox={"radius": 6},
         text={"textShadow": SH, "font": F}, textDark={"textShadow": "", "font": F})
import rebuild as RB  # noqa: E402


def kit_frame_decor(X, Y, W, H, hb, g):
    busy = [e for e in g["elements"] if e.get("type") in ("image", "text") and RB._r(e)[0] + RB._r(e)[2] > X + W - 150
            and RB._r(e)[1] < Y + hb and RB._r(e)[1] + RB._r(e)[3] > Y and RB._r(e)[2] < W * 0.4]
    return chevrons(X + W - 130, Y, hb, delay=400) if hb >= 50 and W >= 500 and not busy else []


def kit_bar_decor(R, g):
    x, y, w, h = R
    return chevrons(x + w + 8, y, min(h, 70), delay=500) if x + w + 120 < 1920 and h >= 40 else []


def kit_tr(gid, g, TA):
    """Dark chrome plate, blue chrome rail across the middle with chevrons, glossy logo tile."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=PLATE_D),
         box("Shine", 0, 0, 1920, 1080, None, TA("fade", 400, 80), bg="linear-gradient(180deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 40%)"),
         box("Rail", 0, 400, 1920, 260, None, TA("wipe-right", 420, 120), bg=RAIL, borderW=1, borderColor="#FFFFFF@0.5", shadow=MC["shadow"]),
         box("Edge top", 0, 392, 1920, 8, "#F68B1F", TA("grow-x", 360, 200)),
         box("Edge bottom", 0, 660, 1920, 8, "#F68B1F", TA("grow-x", 360, 240)),
         box("Tile", 850, 130, 220, 220, None, TA("pop", 380, 220), bg=TILE, radius=16, borderW=2, borderColor="#A2A8B2")]
    for i in range(4):
        for side, x0 in (("l", 60), ("r", 1750)):
            c = txt("Chevron %s%d" % (side, i), x0 + i * 26, 400, 40, 260, "❯", 120, TA("slide-right", 300, 300 + i * 60), font=F, weight=800, color="#F68B1F")
            c["opacity"] = 0.4 + 0.2 * i
            E.append(c)
    return {"elements": E, "word": {"font": F, "weight": 800, "color": "#FFFFFF", "textShadow": SH, "rect": (200, 410, 1520, 240)},
            "sub": {"font": F, "weight": 800, "color": "#FFFFFF", "textShadow": SH, "rect": (60, 690, 1800, 90)}, "brand": {"rect": (870, 150, 180, 180)}}


def kit_slab(R, slab, g):
    x, y, w, h = R
    E = [box("Edge top", 0, y - 8, 1920, 8, "#F68B1F", A("grow-x", 300, 100)),
         box("Edge bottom", 0, y + h, 1920, 8, "#F68B1F", A("grow-x", 300, 140)),
         dict(box("Shine", 0, y, 1920, h // 2, None, A("fade", 300, 200), bg="linear-gradient(180deg, rgba(255,255,255,0.28), rgba(255,255,255,0.04))"),
              _over=True)]
    for c in chevrons(1760, y, h, delay=400):
        c["_over"] = True
        E.append(c)
    return E

def kit_screen(bg, team, g):
    over = [box("Shine", 0, 0, 1920, 540, None, A("fade", 500, 100), bg="linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0))"),
            box("Rail top", 0, 0, 1920, 22, None, A("wipe-right", 400, 80), bg=RAIL),
            box("Edge top", 0, 22, 1920, 5, "#F68B1F", A("grow-x", 400, 160)),
            box("Edge bottom", 0, 1053, 1920, 5, "#F68B1F", A("grow-x", 400, 160)),
            box("Rail bottom", 0, 1058, 1920, 22, None, A("wipe-left", 400, 80), bg=RAIL)]
    return {"floor": RAIL, "replace": PLATE_D, "over": over}

KIT = RB.make_kit(dict(
    screen=kit_screen,
    slab=kit_slab,
    body=PLATE_D, bodyBox={"radius": 10, "borderW": 1, "borderColor": "#FFFFFF@0.35", "shadow": MC["shadow"]},
    headTile=TILE, headTileBox={"radius": 16, "borderW": 2, "borderColor": "#A2A8B2"},
    head=RAIL, headBox={"borderW": 1, "borderColor": "#FFFFFF@0.5", "radius": 10}, headRule="#F68B1F", sub=RAIL_D,
    title={"font": F, "weight": 800, "color": "#FFFFFF", "textShadow": SH, "italic": False},
    headText={"textShadow": SH}, subText={"font": F, "weight": 800, "color": "#FFFFFF", "textShadow": SH},
    frameDecor=kit_frame_decor,
    roles={"PANEL": PLATE_D, "PANEL2": PLATE, "DARK": "#0E0F12", "STRIP": SILVER}, barBox={"radius": 8},
    mainBox={"borderW": 1, "borderColor": "#FFFFFF@0.35", "shadow": MC["shadow"]}, barDecor=kit_bar_decor,
    tile={"background": TILE, "radius": 16, "borderW": 2, "borderColor": "#A2A8B2"}, tr=kit_tr))

g = RB.rebuild_all(g, KIT, only=set(g) - set(CUSTOM))
g = RB.strip_flags(SK.skin_all(g, K, only=set(g) - set(CUSTOM)))
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
for k, d in g.items():
    if not d.get("layout") and "Metro Chrome" not in d.get("name", ""):
        d["name"] = "%s (Metro Chrome)" % d.get("name", k)

theme = dict(night_doc["theme"])
theme.update({"primary": "#1C376F", "accent": "#F68B1F", "text": "#FFFFFF", "dim": "rgba(220,226,236,0.8)", "line": "rgba(255,255,255,0.22)",
              "card": "rgba(30,33,39,0.95)", "panel": "rgba(30,33,39,0.95)", "panel2": "rgba(44,48,56,0.95)",
              "font": "'Helvetica Neue', Helvetica, Arial, sans-serif", "font2": "'Helvetica Neue', Helvetica, Arial, sans-serif"})
doc = {"version": 2, "name": "Metro Chrome",
       "description": "Late-2000s regional-network look: blue chrome rails with orange chevrons, glossy black logo tiles, gunmetal plates, "
                      "orange highlights, rounded stat pills and a long top scorebug rail. Every graphic type, plus basketball, football and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "metro-chrome.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
