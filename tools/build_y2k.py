"""Builds the "Y2K Blue" package: templates/packages/y2k-blue.json.

Early-2000s regional-network look, from Rob's 2002 reference frames: glossy silver bars with dark type, royal blue
glossy panels with white drop-shadowed type, a halftone dot strip, a diamond corner scorebug (and a bottom bar
scorebug with BOTTOM 1ST), black position chips, diamond bullets. No network or team marks are included.
Run:  python tools/build_y2k.py   (after tools/build_night_game.py)
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

SILV = "linear-gradient(180deg, #FFFFFF 0%, #EDF0F4 38%, #C5CBD5 78%, #EEF1F5 100%)"
ROYAL = ("radial-gradient(ellipse at 72% -20%, rgba(150,190,255,0.55), transparent 55%), "
         "linear-gradient(180deg, #3A5CEB 0%, #1E3AC8 45%, #0F2192 100%)")
ROYAL2 = "linear-gradient(180deg, #2C4BDA 0%, #16299F 100%)"
NIGHT_ = "#0A1460"
DOTS = "radial-gradient(circle, rgba(255,255,255,0.55) 1.5px, transparent 2.3px) 0 0 / 9px 9px"
LINES = "repeating-linear-gradient(90deg, rgba(255,255,255,0.85) 0 3px, transparent 3px 8px)"
INK = "#1A1E28"
SH = "2px 2px 0 rgba(0,0,0,0.55)"
TEAM = ("linear-gradient(180deg, color-mix(in srgb, {%s.color} 78%%, #fff) 0%%, {%s.color} 50%%, "
        "color-mix(in srgb, {%s.color} 60%%, #000) 100%%)")

YS = dict(BL.NETWORK, key="y2k", font="$font", body="$font", up=True, radius=2, cardRadius=2,
          panel=ROYAL, panel2=ROYAL2, dark=NIGHT_, strip=SILV, stripText=INK, val=SILV, valText=INK,
          hi="#FFFFFF", hiText="#0F2192", line="#FFFFFF@0.35", shadow="0 8px 18px rgba(0,0,0,.55)", cardIn="zoom-out",
          teamGrad=TEAM, titleBg="radial-gradient(ellipse at 70% 30%, #4B6BF0, #1E3AC8 50%, #0A1460 100%)")
F = "$font"
C = "$font2"
LIVE = "inPlay"
OUT_ = {"type": "fade", "dur": 240, "delay": 0, "ease": "in"}


def W_(name, x, y, w, h, text, size, a, show=None, **st):
    """White type with the period drop shadow."""
    st.setdefault("font", F)
    st.setdefault("weight", 800)
    return txt(name, x, y, w, h, text, size, a, show=show, textShadow=SH, **st)


def K_(name, x, y, w, h, text, size, a, show=None, **st):
    """Dark type on silver."""
    st.setdefault("font", F)
    st.setdefault("weight", 800)
    return txt(name, x, y, w, h, text, size, a, show=show, color=INK, **st)


def brand(name, x, y, w, h, a):
    return [img(name, x, y, w, h, "{brand.logo}", a, show="brand.logo"),
            txt(name + " text", x, y, w, h, "{brand.short|upper}", int(h * 0.75), a, show="!brand.logo && brand.short", font=F, weight=800,
                color="#FFFFFF", align="center", textShadow=SH, italic=True)]


# ------------------------------------------------------------------ scorebugs
def scorebug_diamond():
    """Corner diamond: inning on top, silver abbreviations beside blue score boxes, outs and count, brand mark."""
    X, Y, S_ = 70, 46, 196
    cx = X + S_ // 2
    E = [box("Diamond", X, Y, S_, S_, None, A("pop", 420, 0, out=OUT_), bg=ROYAL, rotate=45, borderW=4, borderColor="#E6EAF0",
             shadow="0 8px 20px rgba(0,0,0,.55)"),
         W_("Inning", cx - 70, Y + 14, 140, 28, "{arrow}{inningOrd|upper}", 24, A("fade", 240, 300, change="flash"), show=LIVE, align="center"),
         W_("Status", cx - 70, Y + 14, 140, 28, "{statusText}", 20, A("fade", 240, 300), show="!" + LIVE, align="center")]
    for i, side in enumerate(("away", "home")):
        y = Y + 46 + i * 34
        E += [box("%s abbr bg" % side, cx - 80, y, 96, 30, None, A("wipe-right", 260, 220 + i * 60), bg=SILV),
              K_("%s abbr" % side, cx - 80, y, 96, 30, "{%s.abbr|upper}" % side, 24, A("fade", 220, 320 + i * 60), align="center"),
              box("%s run bg" % side, cx + 20, y, 58, 30, None, A("wipe-right", 260, 260 + i * 60), bg=ROYAL2, borderW=1, borderColor="#FFFFFF@0.7"),
              W_("%s runs" % side, cx + 20, y, 58, 30, "{%s.runs}" % side, 24, A("fade", 220, 360 + i * 60, change="pop"), align="center")]
    E += [W_("Outs", cx - 82, Y + 116, 90, 24, "{outs} OUT", 18, A("fade", 220, 420, change="flash"), show=LIVE),
          W_("Count", cx + 6, Y + 116, 76, 24, "{count}", 18, A("fade", 220, 440, change="flash"), show=LIVE, align="right")]
    E += brand("Brand", cx - 50, Y + 142, 100, 34, A("fade", 260, 480))
    # base runners: a base at each corner of the diamond (second on top, first right, third left, home plate below)
    cy = Y + S_ // 2
    reach = int(S_ * 0.7071) - 24
    BS = 26
    for base, (bx, by) in (("2", (cx, cy - reach)), ("1", (cx + reach, cy)), ("3", (cx - reach, cy))):
        x0, y0 = bx - BS // 2, by - BS // 2
        E += [box("Base %s" % base, x0, y0, BS, BS, "#0A1460@0.55", A("pop", 260, 380), show=LIVE, rotate=45, borderW=2, borderColor="#E6EAF0"),
              box("Runner %s" % base, x0, y0, BS, BS, None, A("pop", 220, 400, change="pop"), show=both(LIVE, "bases.%s" % base), rotate=45, bg=SILV,
                  borderW=2, borderColor="#FFFFFF", shadow="0 0 10px rgba(255,255,255,.8)")]
    E += [box("Home plate", cx - 9, cy + reach - 9, 18, 18, "#E6EAF0", A("pop", 260, 380), show=LIVE, rotate=45)]
    E += sponsor_tab(X - 20, Y + S_ + 60, 240, 40, 600, radius=2, a_type="wipe-down")
    return {"name": "Scorebug: Diamond", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "half_{halfKey}, scorebug"}


def scorebug_bar():
    """Bottom bar: brand block, silver abbreviations, blue R H E for each team, BOTTOM 1ST strip."""
    X, Y, RH = 120, 906, 40
    E = [box("Brand block", X, Y, 190, 2 * RH, None, A("wipe-right", 360, 0, out=OUT_), bg=SILV, shadow=YS["shadow"])]
    E += [img("Brand", X + 12, Y + 6, 166, 2 * RH - 12, "{brand.logo}", A("fade", 260, 200), show="brand.logo"),
          K_("Brand text", X + 8, Y, 174, 2 * RH, "{brand.short|upper}", 52, A("fade", 260, 200), show="!brand.logo && brand.short", align="center",
             italic=True),
          box("Teams", X + 190, Y, 110, 2 * RH, None, A("wipe-right", 360, 100, out=OUT_), bg=SILV)]
    for i, side in enumerate(("away", "home")):
        y = Y + i * RH
        E += [K_("%s abbr" % side, X + 196, y, 100, RH, "{%s.abbr|upper}" % side, 32, A("fade", 240, 300 + i * 60), font=C)]
    E += [box("RHE", X + 300, Y, 210, 2 * RH, None, A("wipe-right", 360, 160, out=OUT_), bg=ROYAL),
          box("Mid line", X + 300, Y + RH - 1, 210, 2, "#FFFFFF@0.5", A("grow-x", 260, 300))]
    for i, side in enumerate(("away", "home")):
        y = Y + i * RH
        for j, k in enumerate(("runs", "hits", "errors")):
            E.append(W_("%s %s" % (side, k), X + 300 + j * 70, y, 70, RH, "{%s.%s}" % (side, k), 32, A("fade", 240, 360 + i * 60 + j * 30,
                        change="pop"), align="center"))
    E += [box("Strip", X + 210, Y + 2 * RH, 300, 32, None, A("wipe-down", 280, 420), bg=ROYAL2, show=LIVE),
          W_("Inning", X + 210, Y + 2 * RH, 300, 32, "{half|upper} {inningOrd|upper}", 22, A("fade", 220, 500, change="flash"), show=LIVE,
             align="center"),
          box("Strip final", X + 210, Y + 2 * RH, 300, 32, None, A("wipe-down", 280, 420), bg=ROYAL2, show="!" + LIVE),
          W_("Final", X + 210, Y + 2 * RH, 300, 32, "{statusText}", 22, A("fade", 220, 500), show="!" + LIVE, align="center")]
    return {"name": "Scorebug: Bottom Bar", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "half_{halfKey}, scorebug"}


# ------------------------------------------------------------------ lower thirds
def lower(kind):
    """Team logo, silver name bar with a black position chip, blue label row, silver value row, dotted stripes."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    cols = ([("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("K", "{pitcher.season.k|zero}")]
            if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}")])
    X, Y, W = 330, 870, 860
    E = [box("Stripes", X - 190, Y + 94, 160, 26, None, A("wipe-right", 300, 300), bg=LINES, opacity=0.8)]
    E += logo_or_abbr("Logo", X - 210, Y - 10, 190, 110, team, 40, A("slide-right", 380, 100, dist=40), S=YS)
    E += [box("Name bar", X, Y, W, 52, None, A("wipe-right", 420, 0, out=OUT_), bg=SILV, shadow=YS["shadow"]),
          K_("Name", X + 20, Y, W - 120, 52, "{%s.name}" % who, 38, A("fade", 260, 300), fit=True),
          box("Chip", X + W - 70, Y + 9, 52, 34, "#111111", A("pop", 260, 380), borderW=1, borderColor="#FFFFFF@0.6"),
          txt("Chip text", X + W - 70, Y + 9, 52, 34, ("{pitcher.throws|hand}" if kind == "pit" else "{batter.pos}"), 20, A("fade", 220, 420),
              font=F, weight=800, align="center", color="#FFFFFF"),
          box("Label row", X, Y + 52, W - 140, 28, None, A("wipe-right", 380, 160, out=OUT_), bg=ROYAL2),
          box("Value row", X, Y + 80, W - 140, 42, None, A("wipe-right", 380, 220, out=OUT_), bg=SILV)]
    cw = (W - 140) // len(cols)
    for i, (lab, val) in enumerate(cols):
        E += [W_("%s label" % lab, X + i * cw, Y + 52, cw, 28, lab, 20, A("fade", 220, 380 + i * 50), align="center", weight=700),
              K_("%s value" % lab, X + i * cw, Y + 80, cw, 42, val, 32, A("fade", 220, 420 + i * 50, change="flash"), align="center")]
    E += sponsor_tab(X + W - 300, Y - 46, 300, 40, 600, radius=2, a_type="wipe-up")
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def name_super(name, line1, line2, show1, show2=None, gid_name="Name Super"):
    """Silver name bar over a blue streak bar, brand mark on the left."""
    X, Y, W = 230, 890, 900
    E = [box("Stripes", X - 60, Y + 66, 150, 22, None, A("wipe-right", 300, 260), bg=LINES, opacity=0.8)]
    E += brand("Brand", X - 190, Y - 4, 170, 64, A("slide-right", 360, 80, dist=30))
    E += [box("Bar", X, Y, W, 56, None, A("wipe-right", 420, 0, out=OUT_), bg=SILV, shadow=YS["shadow"], show=show1),
          K_("Line 1", X + 24, Y, W - 48, 56, line1, 40, A("fade", 260, 280), show=show1),
          box("Streak", X - 20, Y + 56, W + 20, 40, None, A("wipe-right", 420, 160, out=OUT_), show=show1,
              bg="linear-gradient(90deg, #0F2192 0%, #2C4BDA 40%, #8FB0FF 52%, #2C4BDA 62%, #0F2192 100%)"),
          W_("Line 2", X + 24, Y + 56, W - 48, 40, line2, 28, A("fade", 240, 380), show=show2 or show1)]
    return E


def custom_lower():
    E = name_super("Custom", "{custom.line1}", "{custom.line2}", "custom.line1", "custom.line2")
    return {"name": "Custom Lower Third", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


def talent():
    E = name_super("Talent", "{show.host1}", "{show.role1|upper}", "show.host1", "show.role1")
    return {"name": "Talent", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "show"}


# ------------------------------------------------------------------ panels with silver / blue headers
def header(X, Y, W, title, sub, logo="{team.logo}", logo_show="team.logo", silver=True, delay=0, logo_right=False):
    """Silver (or blue) title bar with a logo, then a blue (or silver) sub strip with the halftone dots."""
    bar_bg, sub_bg = (SILV, ROYAL2) if silver else (ROYAL, SILV)
    T_ = K_ if silver else W_
    S_ = W_ if silver else K_
    lx = X + W - 150 if logo_right else X + 10
    tx = X + 20 if logo_right else X + 170
    E = [box("Head", X, Y, W, 78, None, A("wipe-right", 400, delay, out=OUT_), bg=bar_bg, shadow=YS["shadow"]),
         img("Head logo", lx, Y - 18, 140, 110, logo, A("pop", 360, delay + 200), show=logo_show),
         T_("Title", tx, Y, W - 190, 78, title, 50, A("fade", 260, delay + 280)),
         box("Sub", X + (0 if logo_right else 150), Y + 78, W - 150, 34, None, A("wipe-right", 360, delay + 160, out=OUT_), bg=sub_bg),
         box("Dots", X + W - 330, Y + 78, 300, 34, None, A("fade", 300, delay + 360), bg=DOTS, opacity=0.8),
         S_("Sub text", tx, Y + 78, W - 360, 34, sub, 22, A("fade", 240, delay + 360))]
    return E


def stat_side(kind):
    """Right-side season card: blue name bar with logo, silver THIS SEASON strip, blue rows with a silver value column."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    X, Y, W, RH = 1170, 250, 600, 58
    E = header(X, Y, W, "{%s.name|upper}" % who, "THIS SEASON", logo="{%s.logo}" % team, logo_show="%s.logo" % team, silver=False, logo_right=True)
    body = box("Body", X + 40, Y + 112, W - 80, 8 * RH + 10, None, A("wipe-down", 420, 260, out=OUT_), bg=ROYAL, borderW=2, borderColor="#FFFFFF@0.6")
    body["growWith"] = {"bind": "%s.card" % who, "base": 10, "per": RH, "max": 8}
    col = box("Values", X + W - 190, Y + 112, 150, 8 * RH + 10, None, A("wipe-down", 420, 320, out=OUT_), bg=SILV)
    col["growWith"] = dict(body["growWith"])
    E += [body, col]
    for i in range(8):
        p = "%s.card.%d" % (who, i)
        y = Y + 118 + i * RH
        E += [W_("Label %d" % i, X + 60, y, W - 270, RH - 4, "{%s.label}" % p, 34, A("fade", 220, 420 + i * 60), show=p + ".label"),
              K_("Value %d" % i, X + W - 176, y, 130, RH - 4, "{%s.value}" % p, 34, A("fade", 220, 440 + i * 60), show=p + ".label"),
              box("Line %d" % i, X + 50, y + RH - 3, W - 250, 2, "#FFFFFF@0.45", A("grow-x", 220, 460 + i * 60), show=p + ".label")]
    return {"name": "%s Season Card" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


def player_card(kind):
    """Full card: blue backdrop, silver name bar with logo and a dotted sub strip, photo in a silver frame with number
    and position, four stat lines and a note."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    X, Y, W = 300, 110, 1320
    rows = ([("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
             ("K", "{pitcher.season.k|zero}")] if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}"), ("SLG", "{batter.season.slg|avg}")])
    E = [box("Backdrop", X - 40, Y - 30, W + 80, 860, None, A("fade", 500, 0), bg=ROYAL, radius=4, shadow=YS["shadow"])]
    E += header(X, Y, W, "{%s.name|upper}" % who, "{seasonYear} SEASON", logo="{%s.logo}" % team, logo_show="%s.logo" % team, delay=100)
    E += [box("Photo frame", X + 60, Y + 170, 380, 450, None, A("pop", 400, 400), bg=SILV, borderW=2, borderColor="#FFFFFF"),
          box("Photo bg", X + 74, Y + 184, 352, 422, None, A("fade", 300, 460), bg="linear-gradient(180deg, #C9D3E4, #8E9DB8)"),
          img("Photo", X + 74, Y + 184, 352, 422, "{%s.photo}" % who, A("fade", 400, 520), show="%s.photo" % who, fit="cover", focus="center top"),
          txt("Number big", X + 74, Y + 184, 352, 422, "{%s.number}" % who, 200, A("fade", 400, 520), show="!%s.photo" % who, font=F, weight=800,
              align="center", color="#FFFFFF@0.5", fit=False),
          box("Num bar", X + 60, Y + 628, 380, 52, None, A("wipe-right", 320, 600), bg=ROYAL2, borderW=2, borderColor="#FFFFFF@0.8"),
          W_("Num", X + 76, Y + 628, 360, 52, "{%s.number}  {%s.pos|upper}" % (who, who) if kind == "bat" else "{pitcher.number}  {pitcher.throws|hand}",
             32, A("fade", 240, 680))]
    for i, (lab, val) in enumerate(rows):
        y = Y + 200 + i * 80
        E += [W_("L %s" % lab, X + 560, y, 140, 76, lab, 52, A("slide-right", 300, 620 + i * 90, dist=20), font=C),
              W_("V %s" % lab, X + 720, y, 260, 76, val, 56, A("slide-right", 300, 640 + i * 90, dist=20), align="right")]
    E += [W_("Note", X + 560, Y + 540, 640, 60, "{notes.foot|upper}", 36, A("fade", 260, 1000), show="notes.foot", font=C, align="left")]
    return {"name": "%s Stat Card" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


def notes_card():
    """Scouting report / notes: blue name bar with logo, silver sub strip, blue panel of diamond bullets."""
    X, Y, W = 150, 220, 980
    E = header(X, Y, W, "{notes.title|upper}", "{notes.kicker|upper}", silver=False)
    E[2]["showIf"] = "notes.title"
    E.insert(3, W_("Title (name)", X + 170, Y, W - 190, 78, "{batter.name|upper}", 50, A("fade", 260, 280), show="!notes.title"))
    E += [box("Panel", X + 150, Y + 112, W - 150, 420, None, A("wipe-down", 420, 300, out=OUT_), bg=ROYAL, borderW=2, borderColor="#FFFFFF@0.6")]
    for i in range(3):
        k = "notes.b%d" % (i + 1)
        y = Y + 132 + i * 130
        E += [box("Bullet %d" % i, X + 176, y + 16, 16, 16, None, A("pop", 260, 500 + i * 140), show=k, rotate=45, borderW=2, borderColor="#FFFFFF",
                  bg="#3A5CEB"),
              W_("Text %d" % i, X + 210, y, W - 380, 120, "{%s|upper}" % k, 38, A("fade", 260, 520 + i * 140), show=k, wrap=True, fit=False, lineH=1.05,
                 valign="top"),
              box("Line %d" % i, X + 170, y + 122, W - 200, 2, "#FFFFFF@0.4", A("grow-x", 260, 560 + i * 140), show=k)]
    return {"name": "Scouting Report", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "feature"}


def standings():
    """Silver header with the league mark, blue sub strip with dots; silver abbreviation column, blue team names,
    silver W L GB column."""
    X, Y, W, RH = 200, 90, 1320, 72
    E = header(X, Y, W, "{standingsGroup.name|upper}", "{seasonYear} STANDINGS", logo="{league.logo}", logo_show="league.logo")
    gw = {"bind": "standingsGroup.teams", "base": 70, "per": RH, "max": 10}
    for nm, x, w, bg in (("Abbr col", X, 120, SILV), ("Names", X + 120, 720, ROYAL), ("Nums col", X + 840, W - 840, SILV)):
        b = box(nm, x, Y + 112, w, 70 + 6 * RH, None, A("wipe-down", 420, 300, out=OUT_), bg=bg)
        b["growWith"] = gw
        E.append(b)
    for lab, x in (("W", 870), ("L", 1010), ("GB", 1150)):
        E.append(K_("Head " + lab, X + x, Y + 118, 140, 56, lab, 30, A("fade", 240, 420), align="center", weight=700))
    for i in range(10):
        p = "standingsGroup.teams.%d" % i
        y = Y + 182 + i * RH
        d = 440 + i * 60
        E += [K_("Abbr %d" % i, X + 10, y, 100, RH, "{%s.abbr|upper}" % p, 22, A("fade", 220, d), show=p + ".name", align="center"),
              W_("Team %d" % i, X + 140, y, 690, RH, "{%s.name|upper}" % p, 42, A("fade", 220, d + 40), show=p + ".name")]
        for k, x in (("w", 870), ("l", 1010), ("gb", 1150)):
            E.append(K_("%s %d" % (k, i), X + x, y, 140, RH, "{%s.%s}" % (p, k), 50 if k != "gb" else 38, A("fade", 220, d + 80), show=p + ".name",
                        align="center"))
        E.append(box("Row line %d" % i, X + 840, y + RH - 1, W - 840, 2, "#9AA3B2", A("grow-x", 220, d + 80), show=p + ".name"))
    E += [img("Brand", X + W + 16, Y + 4, 110, 70, "{brand.logo}", A("fade", 300, 500), show="brand.logo")]
    return {"name": "Standings", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


def lineup():
    """Silver header with the city, blue STARTING LINEUP strip; silver position column, blue names, silver logo panel."""
    X, Y, W, RH = 230, 90, 1240, 66
    E = header(X, Y, W, "{team.city|upper}", "STARTING LINEUP", logo="{brand.logo}", logo_show="brand.logo")
    E[2]["showIf"] = "team.city"
    E.insert(3, K_("Title name", X + 170, Y, W - 190, 78, "{team.name|upper}", 50, A("fade", 260, 280), show="!team.city"))
    E += [box("Pos col", X, Y + 112, 90, 9 * RH + 20, None, A("wipe-down", 420, 300, out=OUT_), bg=SILV),
          box("Names", X + 90, Y + 112, 700, 9 * RH + 20, None, A("wipe-down", 420, 340, out=OUT_), bg=ROYAL),
          box("Logo panel", X + 790, Y + 112, W - 790, 9 * RH + 20, None, A("wipe-down", 420, 380, out=OUT_), bg=SILV),
          img("Logo", X + 830, Y + 180, W - 870, 9 * RH - 120, "{team.logo}", A("zoom-out", 500, 600), show="team.logo")]
    for i in range(9):
        p = "team.lineup.%d" % i
        y = Y + 122 + i * RH
        d = 420 + i * 70
        E += [K_("Pos %d" % i, X, y, 90, RH, "{%s.pos}" % p, 24, A("fade", 220, d), show=p + ".name", align="center"),
              W_("Name %d" % i, X + 110, y, 660, RH, "{%s.name}" % p, 40, A("slide-right", 280, d + 40, dist=20), show=p + ".name"),
              box("Line %d" % i, X + 100, y + RH - 2, 680, 2, "#FFFFFF@0.3", A("grow-x", 220, d + 60), show=p + ".name")]
    return {"name": "Lineup", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E}


def due_up():
    X, Y, W, RH = 130, 640, 640, 62
    E = header(X, Y, W, "DUE UP", "{team.name|upper}", silver=False)
    E += [box("Slots", X + 150, Y + 112, 70, 3 * RH + 10, None, A("wipe-down", 360, 300, out=OUT_), bg=SILV),
          box("Names", X + 220, Y + 112, W - 220, 3 * RH + 10, None, A("wipe-down", 360, 340, out=OUT_), bg=ROYAL)]
    for i in range(3):
        p = "team.dueUp.%d" % i
        y = Y + 117 + i * RH
        d = 420 + i * 100
        E += [K_("Slot %d" % i, X + 150, y, 70, RH, "{%s.slot}" % p, 32, A("fade", 220, d), show=p + ".name", align="center"),
              W_("Name %d" % i, X + 236, y, W - 360, RH, "{%s.name}" % p, 36, A("fade", 220, d + 40), show=p + ".name"),
              W_("Avg %d" % i, X + W - 120, y, 104, RH, "{%s.avg|avg}" % p, 30, A("fade", 220, d + 60), show=p + ".name", align="right")]
    return {"name": "Due Up", "group": "lower", "autoHide": 0, "side": "batting", "sided": True, "elements": E, "sponsorSlot": "half_{halfKey}, dueup"}


def matchup():
    """Diamond backdrop with the brand mark on top; each team as a silver logo tile, a silver city bar and a blue
    nickname bar; VS strip; venue strip."""
    X, Y = 470, 230
    E = [box("Diamond", 760, 90, 400, 400, None, A("pop", 500, 0), bg="linear-gradient(135deg, #DDE3EC, #8E9AAE)", rotate=45, borderW=6,
             borderColor="#FFFFFF", opacity=0.92),
         box("Diamond inner", 800, 130, 320, 320, None, A("fade", 400, 100), bg=ROYAL, rotate=45)]
    E += brand("Brand", 860, 92, 200, 76, A("fade", 400, 300))
    for i, side in enumerate(("away", "home")):
        y = Y + i * 260
        d = 300 + i * 260
        E += [box("%s tile" % side, X, y, 200, 190, None, A("pop", 360, d), bg=SILV, borderW=3, borderColor="#FFFFFF",
                  shadow=YS["shadow"])]
        E += logo_or_abbr("%s logo" % side, X + 18, y + 18, 164, 154, side, 60, A("zoom-out", 400, d + 120), color=INK, S=YS)
        E += [box("%s city bar" % side, X + 200, y, 780, 64, None, A("wipe-right", 380, d + 60), bg=SILV),
              K_("%s city" % side, X + 220, y, 740, 64, "{%s.city|upper}" % side, 40, A("fade", 240, d + 200)),
              box("%s nick bar" % side, X + 200, y + 64, 780, 126, None, A("wipe-right", 380, d + 120), bg=ROYAL),
              W_("%s nick" % side, X + 220, y + 64, 740, 126, "{%s.nick|upper}" % side, 76, A("fade", 260, d + 260))]
    E += [box("VS bar", X, Y + 196, 980, 54, "#05060A", A("wipe-center", 320, 600)),
          W_("VS", X, Y + 196, 980, 54, "VS", 40, A("pop", 300, 700), align="center"),
          box("Venue bar", X + 120, Y + 466, 740, 50, None, A("wipe-center", 320, 1000), bg=SILV, show="venue", borderW=2, borderColor="#05060A"),
          K_("Venue", X + 120, Y + 466, 740, 50, "{venue|upper}", 28, A("fade", 240, 1100), show="venue", align="center")]
    return {"name": "Matchup: Diamond", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def ticker():
    Y, HH = 1022, 50
    E = [box("Bar", 0, Y - 4, 1920, HH + 8, None, A("wipe-up", 400, 0, out={"type": "wipe-down", "dur": 300, "delay": 0, "ease": "in"}), bg=ROYAL),
         box("Label box", 30, Y + 4, 210, HH - 8, None, A("wipe-right", 300, 200), bg=SILV),
         K_("Label", 30, Y + 4, 210, HH - 8, "{ticker.label|upper}", 28, A("fade", 240, 300), show="ticker.label", align="center"),
         K_("League", 30, Y + 4, 210, HH - 8, "{league.name|upper}", 24, A("fade", 240, 300), show="!ticker.label && league.name", align="center"),
         el("ticker", "Crawl", 256, Y, 1440, HH, A("fade", 400, 400), bind="ticker.items",
            style={"size": 30, "weight": 800, "color": "#FFFFFF", "font": F, "speed": 110, "headFill": "#FFFFFF", "headColor": "#0F2192", "upper": True})]
    E += brand("Brand", 1720, Y + 2, 170, HH - 4, A("fade", 300, 500))
    return {"name": "Bottom Ticker", "group": "ticker", "autoHide": 0, "side": "", "sided": False, "elements": E}


def linescore():
    TW, CW, RW, RH = 170, 64, 76, 56
    W = TW + 9 * CW + 3 * RW
    X, Y = (1920 - W) // 2, 840
    E = [box("Head", X + TW, Y, W - TW, 34, None, A("wipe-right", 360, 0, out=OUT_), bg=ROYAL2)]
    for i in range(9):
        E.append(W_("Inn %d" % (i + 1), X + TW + i * CW, Y, CW, 34, str(i + 1), 22, A("fade", 220, 200 + i * 20), align="center", weight=700))
    for j, lab in enumerate(("R", "H", "E")):
        E.append(W_("Head " + lab, X + TW + 9 * CW + j * RW, Y, RW, 34, lab, 24, A("fade", 220, 400), align="center"))
    for r, side in enumerate(("away", "home")):
        y = Y + 34 + r * RH
        d = 200 + r * 120
        E += [box("%s tile" % side, X, y, TW, RH, None, A("wipe-right", 340, d), bg=SILV),
              K_("%s abbr" % side, X + 12, y, TW - 24, RH, "{%s.abbr|upper}" % side, 34, A("fade", 220, d + 160)),
              box("%s cells" % side, X + TW, y, 9 * CW, RH, None, A("wipe-right", 380, d + 60), bg=ROYAL),
              box("%s totals" % side, X + TW + 9 * CW, y, 3 * RW, RH, None, A("wipe-right", 300, d + 160), bg=SILV)]
        for i in range(9):
            E.append(W_("%s %d" % (side, i + 1), X + TW + i * CW, y, CW, RH, "{linescore.%s.%d}" % (side, i), 32, A("fade", 220, d + 200 + i * 25,
                        change="flash"), align="center"))
        for j, k in enumerate(("runs", "hits", "errors")):
            E.append(K_("%s %s" % (side, k), X + TW + 9 * CW + j * RW, y, RW, RH, "{%s.%s}" % (side, k), 34, A("fade", 220, d + 400 + j * 40,
                        change="pop"), align="center"))
    E += [box("Status", X, Y + 34 + 2 * RH, 300, 34, None, A("wipe-down", 280, 600), bg=ROYAL2),
          W_("Status t", X, Y + 34 + 2 * RH, 300, 34, "{statusText}", 22, A("fade", 220, 700), align="center")]
    return {"name": "Linescore", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(YS, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("inning_sponsor", "pitching", "defense", "spotlight", "note", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g.update({"scorebug": scorebug_diamond(), "bug_bar": scorebug_bar(), "batter": lower("bat"), "pitcher": lower("pit"),
          "custom": custom_lower(), "talent": talent(), "batter_tall": stat_side("bat"), "pitcher_tall": stat_side("pit"),
          "batter_card": player_card("bat"), "pitcher_card": player_card("pit"), "feature": notes_card(), "standings": standings(),
          "lineup": lineup(), "dueup": due_up(), "matchup": matchup(), "ticker": ticker(), "linescore": linescore()})
g.update(SL.all_sports(MS))
CUSTOM = ("scorebug", "bug_bar", "batter", "pitcher", "custom", "talent", "batter_tall", "pitcher_tall", "batter_card", "pitcher_card", "feature",
          "standings", "lineup", "dueup", "matchup", "ticker", "linescore")
K = dict(panel=ROYAL, panel2=ROYAL2, dark=NIGHT_, strip=SILV, stripText=INK, val=SILV, ink=INK, hi=SILV, hiText=INK, hiDark=True,
         line="#FFFFFF@0.4", title=YS["titleBg"], shadow=YS["shadow"], team=lambda t: TEAM % (t, t, t), rule="#E6EAF0", text2="#FFFFFF", radius=2,
         noBlur=True, panelBox={"radius": 2, "borderW": 2, "borderColor": "#E6EAF0", "shadow": YS["shadow"]},
         lightBox={"radius": 2, "borderW": 1, "borderColor": "#FFFFFF"}, hiBox={"radius": 2},
         text={"textShadow": SH, "font": F}, textDark={"textShadow": "", "font": F})
import rebuild as RB  # noqa: E402


def kit_tr(gid, g, TA):
    """Royal gel field with the stripe lines, silver word band, blue dotted sub strip."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=ROYAL),
         box("Stripes", 0, 0, 1920, 1080, None, TA("fade", 400, 80), bg=LINES, opacity=0.08),
         box("Band", 0, 380, 1920, 250, None, TA("wipe-right", 420, 120), bg=SILV, shadow=YS["shadow"]),
         box("Sub strip", 0, 630, 1920, 90, None, TA("wipe-left", 420, 180), bg=ROYAL2),
         box("Dots", 1300, 630, 620, 90, None, TA("fade", 300, 300), bg=DOTS, opacity=0.8),
         box("Lines", 0, 730, 520, 30, None, TA("wipe-right", 300, 260), bg=LINES, opacity=0.8)]
    return {"elements": E, "word": {"font": F, "weight": 800, "color": INK, "textShadow": "", "rect": (60, 392, 1800, 226)},
            "sub": {"font": F, "weight": 800, "color": "#FFFFFF", "textShadow": SH, "rect": (60, 630, 1800, 90)}, "brand": {"rect": (860, 150, 200, 200)}}


def kit_bar_decor(R, g):
    x, y, w, h = R
    return [box("Stripes", x - 150, y + h - 4, 140, 22, None, A("wipe-right", 300, 300, out=OUT_), bg=LINES, opacity=0.8)] if x > 170 else []


def kit_slab(R, slab, g):
    x, y, w, h = R
    return [box("Rail top", 0, y - 14, 1920, 14, None, A("wipe-right", 320, 60), bg=SILV),
            box("Rail bottom", 0, y + h, 1920, 14, None, A("wipe-left", 320, 60), bg=SILV),
            dict(box("Dots", 1300, y, 620, h, None, A("fade", 300, 300), bg=DOTS, opacity=0.5), _over=True),
            box("Lines", 0, y + h + 20, 520, 26, None, A("wipe-right", 300, 260), bg=LINES, opacity=0.8)]

def kit_screen(bg, team, g):
    over = [box("Stripes", 0, 0, 1920, 1080, None, A("fade", 500, 100), bg=LINES, opacity=0.06),
            box("Rail top", 0, 0, 1920, 16, None, A("wipe-right", 400, 80), bg=SILV),
            box("Rail bottom", 0, 1064, 1920, 16, None, A("wipe-left", 400, 80), bg=SILV),
            box("Dots", 1400, 1010, 520, 54, None, A("fade", 300, 300), bg=DOTS, opacity=0.7)]
    return {"floor": SILV, "replace": ROYAL, "over": over}

KIT = RB.make_kit(dict(
    screen=kit_screen,
    table={"highlightFill": "#8FB0FF@0.5"},
    slab=kit_slab,
    body=ROYAL, bodyBox={"borderW": 2, "borderColor": "#E6EAF0", "shadow": YS["shadow"], "radius": 2},
    head=SILV, headBox={"shadow": YS["shadow"]}, headRule="#E6EAF0", sub=ROYAL2, subOver=DOTS,
    title={"font": F, "weight": 800, "color": INK, "textShadow": "", "italic": False},
    headText={"color": INK, "textShadow": ""}, subText={"font": F, "weight": 800, "color": "#FFFFFF", "textShadow": SH},
    roles={"PANEL": ROYAL, "PANEL2": ROYAL2, "DARK": NIGHT_, "STRIP": SILV}, barBox={"radius": 2},
    mainBox={"borderW": 2, "borderColor": "#E6EAF0", "shadow": YS["shadow"]}, barDecor=kit_bar_decor,
    tile={"background": SILV, "radius": 2, "borderW": 1, "borderColor": "#FFFFFF"}, tileInk=INK, tr=kit_tr))

g = RB.rebuild_all(g, KIT, only=set(g) - set(CUSTOM))
g = RB.strip_flags(SK.skin_all(g, K, only=set(g) - set(CUSTOM)))
for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
for gid, slot in BL.SPONSOR_SLOTS.items():
    if gid in g:
        g[gid].setdefault("sponsorSlot", slot)
for k, d in g.items():
    if not d.get("layout") and "Y2K Blue" not in d.get("name", ""):
        d["name"] = "%s (Y2K Blue)" % d.get("name", k)

theme = dict(night_doc["theme"])
theme.update({"primary": "#0F2192", "accent": "#8FB0FF", "text": "#FFFFFF", "dim": "rgba(225,232,255,0.82)", "line": "rgba(255,255,255,0.3)",
              "card": "rgba(22,41,159,0.95)", "panel": "rgba(22,41,159,0.95)", "panel2": "rgba(44,75,218,0.95)",
              "font": "Arial, 'Helvetica Neue', Helvetica, sans-serif",
              "font2": "'Arial Narrow', 'Roboto Condensed', 'Helvetica Neue Condensed', Arial, sans-serif"})
doc = {"version": 2, "name": "Y2K Blue",
       "description": "Early-2000s regional-network look: glossy silver bars with dark type, royal blue panels with white shadowed type, "
                      "halftone dot strips, a diamond corner scorebug and a bottom bar scorebug, black position chips, diamond bullets. "
                      "Every graphic type, plus basketball, football and hockey.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "y2k-blue.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
