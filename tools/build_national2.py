"""Builds the "National Broadcast 2" package: templates/packages/national-broadcast-2.json.

Inspired by the 2026 regional-sports-network baseball looks built on a graded trading-card motif that Rob sent: a compact
two-row scorebug (team-colour rows with the batter or pitcher under each team, a dark box with bases, inning, count and
outs), a lower third with a headshot over the team logo, a coloured LAST SEASON style tab and a team-colour stat bar,
a vertical pitcher / batter stat box, slabbed trading cards for the matchup and player intros, a VS card, a big-name
player screen with a signature, and a team badge on a glass diamond. No team, league or network marks are included:
logos come from your own team settings and the broadcaster spots use your broadcaster logo.
Run:  python tools/build_national2.py   (after tools/build_night_game.py)
"""
import theme_lib as TL
from theme_lib import A, box, img, el, logo_or_abbr, W, D_, net_mark, OUT_, LIVE, H, F, COND

ANTON = "'BBG Anton', 'Bebas Neue', Impact, sans-serif"
WIDE = "'BBG Archivo Black', 'Arial Black', sans-serif"
SIGN = "'BBG Mr Dafoe', cursive"
SCRIPT = "'BBG Pacifico', cursive"
INK = "#15171B"
YEL = "#FFC72C"
CHEV = ("repeating-linear-gradient(45deg, rgba(255,255,255,.06) 0 2px, transparent 2px 26px), "
        "repeating-linear-gradient(-45deg, rgba(0,0,0,.10) 0 2px, transparent 2px 26px)")
DIAMONDS = ("repeating-linear-gradient(45deg, rgba(0,0,0,.07) 0 2px, transparent 2px 46px), "
            "repeating-linear-gradient(-45deg, rgba(0,0,0,.07) 0 2px, transparent 2px 46px)")
GLASS = "linear-gradient(135deg, rgba(255,255,255,.55), rgba(205,210,218,.22) 38%, rgba(255,255,255,.08) 60%, rgba(255,255,255,.45))"
SHADOW = "0 12px 30px rgba(0,0,0,.5)"


def tc(t):
    return "%s, linear-gradient(180deg, {%s.color}, color-mix(in srgb, {%s.color} 78%%, #000))" % (CHEV, t, t)


def tc2(t):
    return "linear-gradient(180deg, {%s.color2}, color-mix(in srgb, {%s.color2} 82%%, #000))" % (t, t)


# ------------------------------------------------------------------ scorebug
def scorebug(T):
    X, Y, RH, TW, BW = 52, 40, 56, 250, 132
    E = [box("Frame", X, Y, TW + BW, 2 * RH, None, A("wipe-right", 400, 0, out=OUT_), bg=INK, radius=4, shadow=SHADOW)]
    for i, side in enumerate(("away", "home")):
        y = Y + i * RH
        d = 120 + i * 80
        bat = "half==top" if side == "away" else "half==bottom"
        fld = "half==bottom" if side == "away" else "half==top"
        E += [box("%s row" % side, X, y, TW, RH, None, A("wipe-right", 360, d), bg=tc(side), radius="4px 0 0 4px" if i == 0 else "0 0 0 4px")]
        E += logo_or_abbr("%s logo" % side, X + 6, y + 5, 46, RH - 10, side, 18, A("fade", 260, d + 120), S={"font": WIDE})
        E += [W(T, "%s abbr" % side, X + 58, y + 2, 110, 32, "{%s.abbr|upper}" % side, 28, A("fade", 260, d + 140), font=WIDE, weight=400),
              W(T, "%s runs" % side, X + TW - 74, y, 66, RH, "{%s.runs}" % side, 38, A("reveal-up", 300, d + 160, change="pop"), align="right", font=WIDE,
                weight=400),
              W(T, "%s batter" % side, X + 58, y + 32, 180, 20, "{batter.slot|dot}{batter.last|upper}  {batter.today.hab}", 15, A("fade", 240, d + 200,
                change="fade"), show=LIVE + " && " + bat, weight=700, color="#FFFFFF@0.9"),
              W(T, "%s pitcher" % side, X + 58, y + 32, 180, 20, "{pitcher.last|upper}  P:{pitcher.today.pc|zero}", 15, A("fade", 240, d + 200,
                change="fade"), show=LIVE + " && " + fld, weight=700, color="#FFFFFF@0.9")]
    bx = X + TW
    E += [el("bases", "Bases", bx + 14, Y + 6, BW - 44, 50, A("pop", 320, 380), show=LIVE, bind="bases",
             style={"layout": "tight", "on": "#FFFFFF", "off": "#FFFFFF@0.18", "stroke": "#FFFFFF@0.8", "strokeW": 2}),
          W(T, "Inning", bx + BW - 40, Y + 4, 36, 24, "{arrow}{inning}", 17, A("fade", 240, 420, change="roll"), show=LIVE, align="right"),
          W(T, "Count", bx, Y + 58, BW, 30, "{balls}-{strikes}", 26, A("fade", 240, 440, change="flash"), show=LIVE, align="center", font=WIDE, weight=400),
          el("dots", "Outs", bx, Y + 88, BW, 16, A("fade", 240, 460), show=LIVE, bind="outs",
             style={"total": 2, "size": 11, "gap": 8, "on": "#FFFFFF", "off": "#FFFFFF@0.22", "shape": "circle", "align": "center"}),
          W(T, "Status", bx, Y, BW, 2 * RH, "{statusText|upper}", 20, A("fade", 240, 380), show="!" + LIVE, align="center", wrap=True, fit=False,
            font=WIDE, weight=400)]
    E += BL_sponsor(X, Y + 2 * RH + 6, TW + BW)
    return {"name": "Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E, "sponsorSlot": "half_{halfKey}, scorebug"}


def BL_sponsor(x, y, w):
    return TL.BL.sponsor_tab(x, y, min(300, w), 40, 700, radius=4, a_type="wipe-down")


# ------------------------------------------------------------------ lower third
def lower(T, kind):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    cols = ([("ERA", "{pitcher.season.era|era}"), ("W-L", "{pitcher.season.w|zero}-{pitcher.season.l|zero}"), ("IP", "{pitcher.season.ip|dash}"),
             ("K", "{pitcher.season.k|zero}")] if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}"), ("OBP", "{batter.season.obp|avg}"), ("HR", "{batter.season.hr|zero}"), ("RBI", "{batter.season.rbi|zero}")])
    X, Y, Hh = 280, 912, 72
    BX, BW = X + 220, 820
    E = [img("Team logo", X, Y - 40, 130, 118, "{%s.logo}" % team, A("fade", 300, 100), show="%s.logo" % team),
         img("Headshot", X + 74, Y - 58, 140, 130, "{%s.photo}" % who, A("slide-up", 400, 200, dist=20), show="%s.photo" % who, fit="contain",
             focus="center bottom"),
         box("Tab", BX, Y - 32, 190, 32, None, A("wipe-up", 280, 400, out=OUT_), bg=tc2(team), radius="4px 4px 0 0", show="notes.tab"),
         W(T, "Tab text", BX, Y - 32, 190, 32, "{notes.tab|upper}", 19, A("fade", 240, 480), show="notes.tab", align="center", color=INK, font=WIDE,
           weight=400),
         box("Bar", BX, Y, BW, Hh, None, A("wipe-right", 420, 160, out=OUT_), bg=tc(team), radius="0 4px 4px 4px", shadow=SHADOW),
         W(T, "Pos", BX + 10, Y + 6, 44, 28, "{%s.pos}" % who if kind == "bat" else "{pitcher.throws|hand}", 18, A("fade", 240, 360), align="center",
           weight=800),
         W(T, "Number", BX + 10, Y + 34, 44, 32, "{%s.number}" % who, 24, A("fade", 240, 380), align="center", weight=800),
         W(T, "First", BX + 64, Y + 4, 320, 24, "{%s.first|upper}" % who, 20, A("fade", 260, 400), weight=700),
         W(T, "Last", BX + 62, Y + 22, 330, 50, "{%s.last|upper}" % who, 46, A("reveal-up", 320, 380), font=ANTON, weight=400)]
    cw = 100
    sx = BX + BW - 4 * cw - 10
    for i, (lab, val) in enumerate(cols):
        x = sx + i * cw
        E += [box("%s rule" % lab, x, Y + 10, 2, Hh - 20, "#FFFFFF@0.35", A("grow-y", 260, 420 + i * 40), skew=-14),
              W(T, "%s label" % lab, x, Y + 6, cw, 24, lab, 19, A("fade", 240, 440 + i * 50), align="center", weight=800),
              W(T, "%s value" % lab, x, Y + 28, cw, 42, val, 36, A("reveal-up", 300, 460 + i * 50, change="flash"), align="center", font=WIDE, weight=400)]
    E += BL_sponsor(BX + 200, Y - 46, 300)
    return {"name": "%s Lower Third" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 9, "side": "", "sided": False,
            "elements": E, "pickable": True, "sponsorSlot": "pitcher" if kind == "pit" else "lineup_{batter.slot}, batter"}


def stat_box(T, kind):
    """Vertical stat box (left side): logo and name header, label / value rows, a team-colour note footer."""
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    X, Y, Wd = 64, 300, 440
    E = [box("Tab", X + 130, Y - 30, 200, 30, None, A("wipe-up", 280, 300, out=OUT_), bg=tc2(team), radius="4px 4px 0 0", show="notes.tab"),
         W(T, "Tab text", X + 130, Y - 30, 200, 30, "{notes.tab|upper}", 18, A("fade", 240, 380), show="notes.tab", align="center", color=INK, font=WIDE,
           weight=400),
         box("Head", X, Y, Wd, 100, None, A("wipe-down", 380, 0, out=OUT_), bg=tc(team), radius="4px 4px 0 0", shadow=SHADOW)]
    E += logo_or_abbr("Logo", X + 10, Y + 10, 100, 80, team, 30, A("zoom-out", 340, 200), S={"font": WIDE})
    E += [W(T, "First", X + 130, Y + 8, 180, 30, "{%s.first|upper}" % who, 24, A("fade", 260, 300), weight=700),
          W(T, "Tag", X + 300, Y + 8, 130, 30, "{%s.number}|%s" % (who, "{pitcher.throws|hand}" if kind == "pit" else "{batter.pos}"), 20,
            A("fade", 260, 320), align="right", weight=700),
          W(T, "Last", X + 128, Y + 36, Wd - 140, 60, "{%s.last|upper}" % who, 54, A("reveal-up", 320, 340), font=ANTON, weight=400),
          box("Body", X, Y + 100, Wd, 330, None, A("wipe-down", 420, 120, out=OUT_), bg="linear-gradient(180deg, color-mix(in srgb, {%s.color} 82%%, #000), "
                                                                                       "color-mix(in srgb, {%s.color} 62%%, #000))" % (team, team)),
          box("Body texture", X, Y + 100, Wd, 330, None, A("fade", 300, 300), bg=CHEV),
          el("table", "Rows", X + 18, Y + 112, Wd - 36, 310, A("none", 1, 0, rows={"type": "slide-right", "dur": 300, "stagger": 60, "delay": 500, "dist": 20}),
             bind="%s.card" % who, columns=[{"label": "", "field": "{row.label|upper}", "w": 2, "align": "left"}, {"label": "", "field": "value", "w": 1,
                                                                                                                 "align": "right"}],
             style={"rowH": 60, "size": 32, "weight": 800, "color": "#FFFFFF", "header": False, "padX": 0, "gap": 2, "maxRows": 5, "font": COND,
                    "rowLine": "#FFFFFF@0.25"}),
          box("Foot", X, Y + 430, Wd, 40, None, A("wipe-down", 300, 600, out=OUT_), bg=tc2(team), radius="0 0 4px 4px", show="notes.foot"),
          W(T, "Foot text", X + 10, Y + 430, Wd - 20, 40, "{notes.foot|upper}", 19, A("fade", 240, 700), show="notes.foot", align="center", color=INK,
            weight=800)]
    return {"name": "%s Stat Box" % ("Pitcher" if kind == "pit" else "Batter"), "group": "lower", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


# ------------------------------------------------------------------ slabbed cards
def slab(name, x, y, w, h, team, a_main, d, label="{%s.city}", rot=0, body=None, label_font=SCRIPT, label_size=60):
    """A graded-card case: clear plastic shell, team-colour label up top, card body below."""
    t = team
    E = [box(name + " shell", x, y, w, h, None, a_main, bg=GLASS, radius=22, borderW=4, borderColor="#FFFFFF@0.75", shadow=SHADOW, rotate=rot),
         box(name + " label", x + 22, y + 22, w - 44, 120, None, A("fade", 300, d + 150), bg=tc(t), radius=8, borderW=3, borderColor="#FFFFFF@0.6", rotate=rot),
         W(TT, name + " label text", x + 30, y + 22, w - 60, 120, label % t if "%s" in label else label, label_size, A("fade", 300, d + 250), align="center",
           font=label_font, weight=400, color="{%s.color2}" % t, textShadow="2px 2px 0 rgba(0,0,0,.4)", rotate=rot),
         box(name + " body", x + 30, y + 160, w - 60, h - 190, None, A("fade", 300, d + 200), bg=body or ("%s, linear-gradient(180deg, #23262C, #121418)" % CHEV),
             radius=6, borderW=3, borderColor="#FFFFFF@0.5", rotate=rot)]
    return E


def matchup_slabs(T):
    E = []
    for i, side in enumerate(("away", "home")):
        x = 150 if i == 0 else 1270
        d = 100 + i * 120
        rs = -1 if i == 0 else 1
        for j in (2, 1):
            E += [box("%s case %d" % (side, j), x - rs * 40 * j, 80 + 10 * j, 500, 780, None, A("fade", 400, d), bg=GLASS, radius=22, borderW=3,
                      borderColor="#FFFFFF@0.5", rotate=rs * 4 * j, opacity=0.8),
                  box("%s case %d label" % (side, j), x - rs * 40 * j + 22, 102 + 10 * j, 456, 110, None, A("fade", 400, d), bg=tc(side), radius=8,
                      rotate=rs * 4 * j, opacity=0.8)]
        E += slab(side, x, 60, 500, 800, side, A("slide-%s" % ("right" if i == 0 else "left"), 520, d, dist=120, out=OUT_), d)
        E += logo_or_abbr("%s logo" % side, x + 70, 300, 360, 400, side, 140, A("zoom-out", 500, d + 400), S={"font": WIDE})
    E += [box("Diamond", 810, 330, 300, 300, None, A("pop", 500, 500, out=OUT_), bg="linear-gradient(135deg, #2A2D33, #0E0F12)", rotate=45, borderW=4,
              borderColor="#FFFFFF@0.7", shadow=SHADOW)]
    E += net_mark(T, "Diamond mark", 920, 340, 80, 50, A("fade", 300, 800))
    E += [W(T, "Title", 790, 400, 340, 130, "{notes.bugTitle|upper}", 52, A("reveal-up", 400, 850), show="notes.bugTitle", align="center", font=ANTON,
            weight=400, wrap=True, fit=True, lineH=1.0),
          W(T, "Title (default)", 790, 400, 340, 130, "{away.abbr} AT {home.abbr}", 52, A("reveal-up", 400, 850), show="!notes.bugTitle", align="center",
            font=ANTON, weight=400),
          box("Diamond rule", 880, 534, 160, 2, "#FFFFFF@0.6", A("grow-x", 300, 950)),
          W(T, "Venue", 820, 540, 280, 50, "{venue|upper}", 18, A("fade", 300, 1000), align="center", weight=800, wrap=True)]
    return {"name": "Matchup: Card Slabs", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def vs_card(T):
    E = []
    for i, side in enumerate(("away", "home")):
        x = 30 if i == 0 else 980
        d = 100 + i * 120
        E += [box("%s case" % side, x, 30, 910, 1020, None, A("slide-%s" % ("right" if i == 0 else "left"), 520, d, dist=200, out=OUT_), bg=GLASS, radius=20,
                  borderW=4, borderColor="#FFFFFF@0.7", shadow=SHADOW),
              box("%s panel" % side, x + 30, 60, 850, 960, None, A("fade", 300, d + 200), bg=tc(side), radius=8, borderW=3, borderColor="#FFFFFF@0.5"),
              box("%s glow" % side, x + 30, 60, 850, 960, None, A("fade", 400, d + 300), bg="radial-gradient(ellipse at 50% 40%, rgba(255,255,255,.18), "
                                                                                          "transparent 60%)")]
        E += logo_or_abbr("%s logo" % side, x + 160, 220, 590, 520, side, 200, A("zoom-out", 600, d + 400), S={"font": WIDE})
        E += [W(T, "%s abbr" % side, x + 30, 820, 850, 120, "{%s.abbr|upper}" % side, 90, A("reveal-up", 400, d + 600), align="center", font=WIDE, weight=400)]
    E += [box("VS glass", 900, 480, 120, 120, None, A("pop", 400, 800), bg=GLASS, rotate=45, borderW=3, borderColor="#FFFFFF@0.8"),
          box("VS core", 920, 500, 80, 80, INK, A("pop", 400, 850), radius="50%"),
          W(T, "VS", 920, 500, 80, 80, "VS", 34, A("fade", 200, 950), align="center", font=ANTON, weight=400)]
    return {"name": "VS Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def player_slab(T, kind="bat"):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    E = [box("Field", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg="%s, linear-gradient(180deg, {%s.color}, color-mix(in srgb, {%s.color} 70%%, #000))"
         % (DIAMONDS, team, team))]
    for i, (x, rot) in enumerate(((330, -8), (1090, 8))):
        E += slab("Side %d" % (i + 1), x, 150, 500, 760, team, A("slide-%s" % ("right" if i == 0 else "left"), 520, 200, dist=150), 200, rot=rot,
                  body="%s, %s" % (CHEV, tc2(team).replace("linear-gradient(180deg,", "linear-gradient(180deg,")))
        E += [img("Side %d logo" % (i + 1), x + 120, 400, 260, 300, "{%s.logo}" % team, A("fade", 300, 500), show="%s.logo" % team, rotate=rot)]
    E += slab("Card", 640, 60, 640, 960, team, A("zoom-out", 560, 400, out=OUT_), 400, body="linear-gradient(180deg, #2A2D33, #0E0F12)")
    E += [img("Photo", 670, 220, 580, 770, "{%s.photo}" % who, A("fade", 500, 700), show="%s.photo" % who, fit="cover", focus="center top"),
          W(T, "Num", 670, 220, 580, 770, "{%s.number}" % who, 360, A("fade", 400, 700), show="!%s.photo" % who, align="center", color="#FFFFFF@0.25",
            font=ANTON, weight=400, fit=False),
          W(T, "First", 670, 560, 580, 90, "{%s.first|upper}" % who, 76, A("slide-right", 400, 900, dist=40), align="center", font=WIDE, weight=400,
            color="{%s.color2}" % team, textShadow="0 4px 14px rgba(0,0,0,.5)"),
          W(T, "Last", 650, 640, 620, 320, "{%s.last|upper}" % who, 190, A("reveal-up", 500, 1000), align="center", font=ANTON, weight=400,
            textShadow="0 6px 24px rgba(0,0,0,.55)")]
    return {"name": "%s Card Intro" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


def big_name(T):
    who, team = "batter", "batting"
    E = [box("Field", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg="%s, linear-gradient(180deg, color-mix(in srgb, {%s.color2} 92%%, #fff), "
         "{%s.color2})" % (DIAMONDS, team, team)),
         img("Logo", 1240, 40, 760, 760, "{%s.logo}" % team, A("zoom-out", 700, 200), show="%s.logo" % team),
         img("Photo", 1060, 120, 760, 960, "{%s.photo}" % who, A("slide-left", 600, 400, dist=60), show="%s.photo" % who, fit="contain", focus="center bottom"),
         W(T, "Number", 120, 90, 300, 90, "{%s.number}" % who, 72, A("fade", 400, 500), font=WIDE, weight=400, color=INK),
         W(T, "First", 120, 180, 1000, 150, "{%s.first|upper}" % who, 140, A("slide-right", 500, 600, dist=60), font=WIDE, weight=400, color="#FFFFFF",
           textShadow="0 4px 12px rgba(0,0,0,.2)"),
         W(T, "Last", 100, 330, 1000, 480, "{%s.last|upper}" % who, 330, A("reveal-up", 600, 700), font=ANTON, weight=400, color=INK, lineH=1.0),
         W(T, "Signature", 160, 830, 900, 200, "{%s.name}" % who, 120, A("letters", 1400, 1300), font=SIGN, weight=400, color="#FFFFFF", fit=True,
           rotate=-6)]
    return {"name": "Big Name Player Screen", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "pickable": True}


def team_badge(T):
    E = [box("Paper", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg="%s, #E7E8EA" % DIAMONDS.replace(".07", ".035")),
         box("Band", 110, 250, 1700, 580, None, A("wipe-right", 600, 200), bg="%s, {team.color}" % CHEV.replace(".06", ".04")),
         W(T, "Name", 110, 250, 1700, 580, "{team.city|upper} {team.nick|upper}", 400, A("fade", 600, 500), align="center", font=ANTON, weight=400,
           color="{team.color2}", fit=True),
         box("Glass", 660, 240, 600, 600, None, A("scale", 700, 600), bg="rgba(255,255,255,.18)", rotate=45, borderW=4, borderColor="#FFFFFF@0.85",
             shadow="0 0 40px rgba(255,255,255,.3)", blur=6),
         box("Ring", 700, 280, 520, 520, None, A("pop", 600, 900), bg="{team.color2}", radius="50%", shadow=SHADOW),
         box("Stitches", 716, 296, 488, 488, None, A("fade", 400, 1100), bg="repeating-conic-gradient(rgba(255,255,255,.9) 0 2deg, transparent 2deg 7deg)",
             radius="50%"),
         box("Stitch cover", 722, 302, 476, 476, None, A("fade", 400, 1100), bg="{team.color2}", radius="50%"),
         box("Inner", 770, 350, 380, 380, None, A("pop", 500, 1000), bg=tc("team"), radius="50%", borderW=4, borderColor="#FFFFFF@0.6")]
    E += logo_or_abbr("Logo", 810, 390, 300, 300, "team", 120, A("zoom-out", 500, 1200), S={"font": WIDE})
    E += [W(T, "Script", 1440, 920, 420, 120, "{team.nick}", 70, A("fade", 500, 1400), font=SCRIPT, weight=400, color=INK, align="right")]
    E += net_mark(T, "Mark", 900, 160, 120, 60, A("fade", 400, 1200))
    return {"name": "Team Badge", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": E}


def override(T):
    return {"scorebug": scorebug(T), "batter": lower(T, "bat"), "pitcher": lower(T, "pit"), "batter_card": player_slab(T, "bat"),
            "pitcher_card": player_slab(T, "pit"), "nb2_pitcher_box": stat_box(T, "pit"), "nb2_batter_box": stat_box(T, "bat"),
            "nb2_matchup": matchup_slabs(T), "nb2_vs": vs_card(T), "nb2_big_name": big_name(T), "nb2_badge": team_badge(T)}


TT = TL.defaults(dict(
    key="nb2", file="national-broadcast-2", name="National Broadcast 2", font=ANTON, deco=ANTON, upper=True,
    desc="Regional-network look built on graded trading cards: clear plastic card slabs with team-colour labels, chevron-textured team "
         "panels, tall condensed names with wide first names, a compact two-row scorebug with the batter or pitcher under each team, a "
         "headshot lower third with a coloured tab, vertical stat boxes, slab matchup and player intros, a VS card, a big-name screen with "
         "a signature and a stitched team badge on a glass diamond. Every graphic type, plus basketball, football and hockey.",
    bg=INK, panel="linear-gradient(180deg, #25282E, #15171B)", panel2="linear-gradient(180deg, #2E3138, #1C1E23)", dark="#0E0F12", head="#0E0F12",
    strip="linear-gradient(180deg, #FFFFFF, #E4E6EA)", stripText=INK, val="#FFFFFF", valText=INK, hi=YEL, hiText=INK, edge="#FFFFFF@0.25", r=4,
    title="%s, linear-gradient(180deg, #23262C, #121418)" % CHEV, texture="", title_color="#FFFFFF", rule="#FFFFFF@0.6", team=tc,
    hr_word="HOME RUN", tr_band=GLASS, open_kicker="{seasonYear}",
    override=override))

if __name__ == "__main__":
    TL.build(TT)
