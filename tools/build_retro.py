"""Builds the "Retro" package: templates/packages/retro.json.

1980s character-generator look: no boxes, pale-yellow and white text in a blocky terminal face (VT323,
bundled in web/fonts) with hard drop shadows, cut-on or typed-on reveals. Scorebug, batter / pitcher ID,
due up, lineup, linescore, final, standings, matchup, custom lines, ticker and a scan-line transition.
Run:  python tools/build_retro.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import broadcast_lib as BL  # noqa: E402
from broadcast_lib import A, box, txt, img, el, both  # noqa: E402

F = "$font"
Y_ = "#F4EBB0"      # CG yellow
W_ = "#FFFFFF"
SH = "3px 3px 0 #000, 0 0 8px rgba(0,0,0,.65)"
CUT = {"type": "fade", "dur": 1, "delay": 0, "ease": "linear"}


def T(name, x, y, w, h, text, size=44, delay=0, show=None, color=Y_, align="left", typed=False, change=None, **st):
    """CG text: cut on (or typed on), cut off."""
    a = A("letters", 30 * max(1, min(24, len(text))), delay, out=CUT, stagger=28) if typed else A("fade", 1, delay, out=CUT)
    if change:
        a["change"] = change
    if typed:
        a["in"]["dist"] = 0
    return txt(name, x, y, w, h, text, size, a, show=show, font=F, weight=400, color=color, align=align, textShadow=SH, tracking=2, **st)


def scorebug():
    X, Y = 40, 26
    E = [T("Half", X, Y, 300, 40, "{halfShort} {inningOrd}", 38, 0, "inPlay", W_),
         T("Final", X, Y, 300, 40, "{statusText}", 38, 0, "!inPlay", W_),
         T("Away", X, Y + 40, 140, 48, "{away.abbr|upper}", 48, 80),
         T("Away runs", X + 150, Y + 40, 80, 48, "{away.runs}", 48, 80, align="right", change="flash"),
         T("Home", X, Y + 86, 140, 48, "{home.abbr|upper}", 48, 120),
         T("Home runs", X + 150, Y + 86, 80, 48, "{home.runs}", 48, 120, align="right", change="flash"),
         T("Count", X, Y + 136, 420, 30, "{balls} BALLS   {strikes} STRIKES", 26, 160, "inPlay", W_, change="flash"),
         T("Outs", X, Y + 166, 300, 40, "{outs} {outsWord|upper}", 36, 200, "inPlay", W_, change="flash")]
    return {"name": "Scorebug: Retro", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": E}


def player_id(kind):
    who = "pitcher" if kind == "pit" else "batter"
    Y = 800
    if kind == "pit":
        lines = [("{pitcher.today.ip|dash} IP  {pitcher.today.h|zero} H  {pitcher.today.r|zero} R  {pitcher.today.k|zero} K", "pitcher.name"),
                 ("ERA {pitcher.season.era|era}   {pitcher.today.pc|zero} PITCHES", "pitcher.name")]
    else:
        lines = [("{batter.forText|upper}", "batter.forText"), ("{batter.playsText}", "batter.playsText"),
                 ("AVG {batter.season.avg|avg}  HR {batter.season.hr|zero}  RBI {batter.season.rbi|zero}", "!batter.forText")]
    E = [T("Name", 260, Y, 1400, 70, "{%s.name}" % who, 64, 0, align="center", typed=True)]
    for i, (t, sh) in enumerate(lines):
        E.append(T("Line %d" % (i + 1), 260, Y + 72 + i * 56 if i < 2 else Y + 72, 1400, 56, t, 50 if i == 0 else 44, 500 + i * 250, sh,
                   W_ if i else Y_, align="center"))
    return {"name": "Pitcher ID (Retro)" if kind == "pit" else "Batter ID (Retro)", "group": "lower", "autoHide": 8, "side": "", "sided": False,
            "elements": E, "pickable": True}


def due_up():
    E = [T("Title", 260, 760, 1400, 64, "DUE UP FOR {team.abbr|upper}", 56, 0, align="center", color=W_)]
    for i in range(3):
        p = "team.dueUp.%d" % i
        E.append(T("Due %d" % i, 260, 830 + i * 58, 1400, 56, "{%s.name|upper}" % p, 50, 250 + i * 250, p + ".name", align="center"))
    return {"name": "Due Up (Retro)", "group": "lower", "autoHide": 10, "side": "batting", "sided": True, "elements": E}


def lineup():
    E = [T("Title", 260, 150, 1400, 76, "{team.name|upper}", 68, 0, align="center", color=W_),
         T("Sub", 260, 226, 1400, 50, "STARTING LINEUP", 44, 200, align="center")]
    for i in range(9):
        p = "team.lineup.%d" % i
        y = 300 + i * 66
        d = 400 + i * 160
        E += [T("Slot %d" % i, 420, y, 60, 60, str(i + 1) + ".", 50, d, p + ".name", W_, align="right"),
              T("Pos %d" % i, 500, y, 90, 60, "{%s.pos}" % p, 50, d, p + ".name", W_),
              T("Name %d" % i, 600, y, 700, 60, "{%s.name|upper}" % p, 50, d, p + ".name"),
              T("Avg %d" % i, 1300, y, 200, 60, "{%s.avg|avg}" % p, 50, d, p + ".name", W_, align="right")]
    return {"name": "Lineup (Retro)", "group": "full", "autoHide": 0, "side": "batting", "sided": True, "elements": E}


def linescore():
    X, Y = 300, 780
    CW = 76
    E = []
    for i in range(9):
        E.append(T("Inn %d" % (i + 1), X + 160 + i * CW, Y, CW, 50, str(i + 1), 44, 0, color=W_, align="center"))
    for j, lab in enumerate(("R", "H", "E")):
        E.append(T("Head %s" % lab, X + 160 + 9 * CW + 20 + j * CW, Y, CW, 50, lab, 44, 0, color=W_, align="center"))
    for r, side in enumerate(("away", "home")):
        y = Y + 56 + r * 60
        E.append(T("%s abbr" % side, X, y, 150, 56, "{%s.abbr|upper}" % side, 50, 150 + r * 150))
        for i in range(9):
            E.append(T("%s %d" % (side, i + 1), X + 160 + i * CW, y, CW, 56, "{linescore.%s.%d}" % (side, i), 50, 150 + r * 150, align="center",
                       change="flash"))
        for j, k in enumerate(("runs", "hits", "errors")):
            E.append(T("%s %s" % (side, k), X + 160 + 9 * CW + 20 + j * CW, y, CW, 56, "{%s.%s}" % (side, k), 50, 150 + r * 150, color=W_, align="center",
                       change="flash"))
    return {"name": "Linescore (Retro)", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


def final():
    E = [T("Final", 260, 300, 1400, 100, "FINAL", 100, 0, align="center", color=W_),
         T("Away", 560, 420, 600, 90, "{away.name|upper}", 70, 300),
         T("Away runs", 1160, 420, 200, 90, "{away.runs}", 80, 300, align="right"),
         T("Home", 560, 510, 600, 90, "{home.name|upper}", 70, 500),
         T("Home runs", 1160, 510, 200, 90, "{home.runs}", 80, 500, align="right"),
         T("W", 260, 640, 1400, 56, "W: {decisions.w.text}", 46, 900, "decisions.w.text", W_, align="center"),
         T("L", 260, 696, 1400, 56, "L: {decisions.l.text}", 46, 1100, "decisions.l.text", W_, align="center"),
         T("S", 260, 752, 1400, 56, "S: {decisions.s.text}", 46, 1300, "decisions.s.text", W_, align="center")]
    return {"name": "Final (Retro)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def standings():
    E = [T("Title", 260, 170, 1400, 76, "{standings.groups.0.name|upper}", 64, 0, "standings.groups.0.name", W_, align="center"),
         T("Head W", 980, 250, 100, 50, "W", 40, 200, color=W_, align="right"),
         T("Head L", 1090, 250, 100, 50, "L", 40, 200, color=W_, align="right"),
         T("Head GB", 1200, 250, 140, 50, "GB", 40, 200, color=W_, align="right")]
    for i in range(8):
        p = "standings.groups.0.teams.%d" % i
        y = 310 + i * 64
        d = 400 + i * 150
        E += [T("Team %d" % i, 560, y, 420, 60, "{%s.name|upper}" % p, 48, d, p + ".name"),
              T("W %d" % i, 980, y, 100, 60, "{%s.w}" % p, 48, d, p + ".name", W_, align="right"),
              T("L %d" % i, 1090, y, 100, 60, "{%s.l}" % p, 48, d, p + ".name", W_, align="right"),
              T("GB %d" % i, 1200, y, 140, 60, "{%s.gb}" % p, 48, d, p + ".name", W_, align="right")]
    return {"name": "Standings (Retro)", "group": "full", "autoHide": 0, "side": "", "sided": False, "groupPicker": True, "elements": E}


def matchup():
    E = [T("Away", 260, 360, 1400, 90, "{away.name|upper}", 84, 0, align="center", typed=True),
         T("At", 260, 455, 1400, 70, "AT", 56, 900, color=W_, align="center"),
         T("Home", 260, 530, 1400, 90, "{home.name|upper}", 84, 1100, align="center", typed=True),
         T("Venue", 260, 650, 1400, 60, "{venue|upper}", 46, 2000, "venue", W_, align="center"),
         T("Broadcaster", 260, 720, 1400, 56, "{brand.name|upper}", 40, 2300, "brand.name", W_, align="center")]
    return {"name": "Matchup (Retro)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}


def custom_lines():
    E = [T("Line 1", 260, 800, 1400, 64, "{custom.line1}", 58, 0, "custom.line1", align="center", typed=True),
         T("Line 2", 260, 868, 1400, 56, "{custom.line2}", 48, 600, "custom.line2", W_, align="center"),
         T("Line 3", 260, 926, 1400, 56, "{custom.line3}", 48, 900, "custom.line3", W_, align="center")]
    return {"name": "Custom Lines (Retro)", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E}


def ticker():
    E = [box("Bar", 0, 1020, 1920, 60, "#000000@0.82", A("fade", 1, 0, out=CUT)),
         el("ticker", "Crawl", 20, 1020, 1880, 60, A("fade", 1, 100, out=CUT), bind="ticker.items",
            style={"size": 40, "weight": 400, "color": Y_, "font": F, "speed": 90, "headFill": "transparent", "headColor": W_, "upper": True})]
    return {"name": "Bottom Ticker (Retro)", "group": "ticker", "autoHide": 0, "side": "", "sided": False, "elements": E}


def transition():
    hold = lambda a, h: dict(a, hold=h)
    E = [box("Black", 0, 0, 1920, 1080, "#05060A", hold(A("wipe-down", 360, 0, ease="linear", out={"type": "wipe-down", "dur": 360, "delay": 0, "ease": "linear"}), 1100)),
         box("Scan", 0, 0, 1920, 1080, None, hold(A("fade", 1, 100, out=CUT), 1300), bg="repeating-linear-gradient(0deg, #FFFFFF0D 0 2px, transparent 2px 6px)"),
         img("Broadcaster", 760, 300, 400, 220, "{brand.logo}", hold(A("fade", 1, 360, out=CUT), 1000), show="brand.logo"),
         txt("Name", 160, 540, 1600, 110, "{brand.name|upper}", 96, hold(A("letters", 500, 360, out=CUT, stagger=30), 600), show="brand.name", font=F,
             weight=400, color=Y_, align="center", textShadow=SH, tracking=4),
         txt("Baseball", 160, 650, 1600, 80, "BASEBALL", 70, hold(A("fade", 1, 800, out=CUT), 600), font=F, weight=400, color=W_, align="center",
             textShadow=SH, tracking=12)]
    return {"name": "Transition (Retro)", "group": "stinger", "autoHide": 2.2, "side": "", "sided": False, "elements": E}



# ---------------------------------------------------------------- every graphic type in the CG look
def stat_card(kind):
    who = "pitcher" if kind == "pit" else "batter"
    E = [T("Name", 260, 250, 1400, 90, "{%s.name|upper}" % who, 80, 0, align="center", typed=True),
         T("Sub", 260, 345, 1400, 56, "{seasonYear} SEASON", 46, 700, color=W_, align="center")]
    for i in range(6):
        p = "%s.card.%d" % (who, i)
        y = 430 + i * 66
        E += [T("Label %d" % i, 560, y, 520, 60, "{%s.label|upper}" % p, 50, 900 + i * 180, p + ".label", W_),
              T("Value %d" % i, 1080, y, 280, 60, "{%s.value}" % p, 54, 900 + i * 180, p + ".label", align="right")]
    return {"name": ("Pitcher" if kind == "pit" else "Batter") + " Season Card (Retro)", "group": "full", "autoHide": 0, "side": "",
            "sided": False, "elements": E, "pickable": True, "cat": "players"}


def pitching_line():
    cols = ("ip", "h", "r", "er", "bb", "k")
    E = [T("Title", 260, 200, 1400, 76, "{team.name|upper} PITCHING", 64, 0, align="center", color=W_)]
    for j, c in enumerate(cols):
        E.append(T("Head %s" % c, 1000 + j * 90, 290, 90, 50, c.upper(), 42, 200, color=W_, align="right"))
    for i in range(7):
        p = "team.pitchers.%d" % i
        y = 350 + i * 64
        d = 400 + i * 160
        E.append(T("Name %d" % i, 360, y, 640, 60, "{%s.name|upper}" % p, 48, d, p + ".name"))
        for j, c in enumerate(cols):
            E.append(T("%s %d" % (c, i), 1000 + j * 90, y, 90, 60, "{%s.%s}" % (p, c), 48, d, p + ".name", W_, align="right", change="flash"))
    return {"name": "Pitching Line (Retro)", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": E, "cat": "pitching"}


def starters():
    E = [T("Title", 260, 300, 1400, 80, "STARTING PITCHERS", 70, 0, align="center", color=W_, typed=True)]
    for r, side in enumerate(("away", "home")):
        y = 420 + r * 130
        E += [T("%s team" % side, 360, y, 220, 60, "{%s.abbr|upper}" % side, 54, 900 + r * 400, color=W_),
              T("%s name" % side, 580, y, 900, 60, "{%s.sp.name|upper}" % side, 56, 900 + r * 400, side + ".sp.name"),
              T("%s line" % side, 580, y + 62, 900, 50, "ERA {%s.sp.era|era}" % side, 44, 1100 + r * 400, side + ".sp.era", W_)]
    return {"name": "Starting Pitchers (Retro)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "cat": "pitching"}


POS9 = ("P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF")


def defense():
    E = [T("Title", 260, 200, 1400, 76, "{team.name|upper} DEFENSE", 64, 0, align="center", color=W_)]
    for i, pos in enumerate(POS9):
        p = "team.defense.%s" % pos
        y = 300 + i * 64
        E += [T("Pos %s" % pos, 560, y, 120, 60, pos, 50, 300 + i * 150, p + ".name", W_, align="right"),
              T("Name %s" % pos, 720, y, 700, 60, "{%s.name|upper}" % p, 50, 300 + i * 150, p + ".name")]
    return {"name": "Defense (Retro)", "group": "full", "autoHide": 0, "side": "fielding", "sided": True, "elements": E, "cat": "lineups"}


def show_title(word, gid):
    E = [box("Black", 0, 0, 1920, 1080, "#05060A@0.92", A("fade", 1, 0, out=CUT)),
         box("Scan", 0, 0, 1920, 1080, None, A("fade", 1, 0, out=CUT), bg="repeating-linear-gradient(0deg, #FFFFFF0B 0 2px, transparent 2px 6px)"),
         img("Broadcaster", 810, 220, 300, 170, "{brand.logo}", A("fade", 1, 200, out=CUT), show="brand.logo"),
         T("Brand", 160, 400, 1600, 80, "{brand.name|upper}", 64, 400, "brand.name", W_, align="center"),
         T("Title", 160, 490, 1600, 150, word, 140, 700, align="center", typed=True),
         T("Sub", 160, 650, 1600, 70, "{show.sub|upper}", 54, 1600, "show.sub", W_, align="center")]
    return {"name": "Show: %s (Retro)" % word.title(), "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E,
            "sponsorSlot": "show", "cat": "show"}


def up_next():
    E = [T("Title", 1180, 700, 680, 64, "UP NEXT", 58, 0, color=W_)]
    for i in range(3):
        k = "show.next%d" % (i + 1)
        E.append(T("Item %d" % i, 1180, 770 + i * 60, 680, 56, "%d. {%s|upper}" % (i + 1, k), 48, 300 + i * 250, k))
    return {"name": "Up Next (Retro)", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "cat": "show"}


def live_bug():
    E = [T("Brand", 40, 26, 420, 50, "{brand.short|upper}", 44, 0, "brand.short", W_),
         T("Show", 40, 26, 420, 50, "{show.name|upper}", 44, 0, "!brand.short && show.name", W_),
         T("Live", 40, 74, 200, 44, "* LIVE *", 40, 200, color="#FF5A4E")]
    E[-1]["anim"]["loop"] = {"type": "pulse", "dur": 900, "amount": 0.35}
    return {"name": "Live Bug (Retro)", "group": "bug2", "autoHide": 0, "side": "", "sided": False, "elements": E, "cat": "bugs"}


def umpires():
    E = [T("Title", 60, 200, 700, 64, "TONIGHT'S UMPIRES", 54, 0, color=W_)]
    for i in range(6):
        p = "umps.%d" % i
        y = 280 + i * 62
        E += [T("Pos %d" % i, 60, y, 100, 58, "{%s.pos}" % p, 46, 300 + i * 160, p + ".name", W_),
              T("Name %d" % i, 170, y, 600, 58, "{%s.name|upper}" % p, 46, 300 + i * 160, p + ".name")]
    return {"name": "Umpires (Retro)", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E, "cat": "panels"}


def pitch_count():
    E = [T("Name", 60, 720, 700, 56, "{pitcher.name|upper}", 50, 0),
         T("PC", 60, 780, 700, 56, "{pitcher.today.pc|zero} PITCHES", 50, 300, color=W_, change="flash"),
         T("SB", 60, 836, 700, 50, "{pitcher.today.st|zero} STRIKES  {pitcher.today.bl|zero} BALLS", 42, 500, color=W_, change="flash")]
    return {"name": "Pitch Count (Retro)", "group": "panel", "autoHide": 0, "side": "", "sided": False, "elements": E, "cat": "panels"}


def event(word1, word2, trigger, name, show=None):
    E = [T("W1", 160, 360, 1600, 150, word1, 150, 0, show, align="center", typed=True),
         T("W2", 160, 510, 1600, 150, word2, 150, 300, show, color=W_, align="center", typed=True),
         T("Who", 160, 690, 1600, 70, "{lastPlay.batter.name|upper}", 58, 900, "lastPlay.batter.name", align="center")]
    for e in E[:2]:
        e["anim"]["loop"] = {"type": "pulse", "dur": 500, "amount": 0.2}
    return {"name": name, "group": "event", "autoHide": 4.5, "side": "batting", "sided": False, "elements": E, "trigger": trigger, "cat": "events"}


def word_transition(gid, word, sub):
    t = transition()
    t["name"] = "Transition: %s (Retro)" % word.title()
    for e in t["elements"]:
        if e["name"] == "Name":
            e["text"] = word.upper()
            e.pop("showIf", None)
        if e["name"] == "Baseball":
            e["text"] = sub
            m = re.match(r"\{([a-z.]+)", sub)
            if m:
                e["showIf"] = m.group(1)
    t["cat"] = "transitions"
    return t


def talent():
    E = []
    for i in range(2):
        h, r = "show.host%d" % (i + 1), "show.role%d" % (i + 1)
        x = 200 + i * 800
        E += [T("Name %d" % i, x, 840, 720, 64, "{%s|upper}" % h, 56, i * 300, h, typed=True),
              T("Role %d" % i, x, 906, 720, 54, "{%s|upper}" % r, 44, 600 + i * 300, r, W_)]
    return {"name": "Talent (Retro)", "group": "lower", "autoHide": 0, "side": "", "sided": False, "elements": E, "cat": "lower_other"}


def scoring():
    E = [T("Title", 260, 200, 1400, 76, "SCORING SUMMARY", 64, 0, align="center", color=W_)]
    for i in range(8):
        p = "scoring.%d" % i
        y = 300 + i * 64
        E += [T("Inn %d" % i, 300, y, 200, 60, "{%s.label|upper}" % p, 46, 300 + i * 160, p + ".text", W_),
              T("Play %d" % i, 500, y, 1000, 60, "{%s.text|upper}" % p, 46, 300 + i * 160, p + ".text"),
              T("Score %d" % i, 1500, y, 160, 60, "{%s.score}" % p, 46, 300 + i * 160, p + ".text", W_, align="right")]
    return {"name": "Scoring Summary (Retro)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E, "cat": "scores"}

g = {"scorebug": scorebug(), "batter": player_id("bat"), "pitcher": player_id("pit"), "dueup": due_up(), "lineup": lineup(),
     "linescore": linescore(), "final": final(), "standings": standings(), "matchup": matchup(), "custom": custom_lines(),
     "ticker": ticker(), "stinger": transition()}
g.update({"batter_card": stat_card("bat"), "pitcher_card": stat_card("pit"), "pitching": pitching_line(), "sp_compare": starters(),
          "defense": defense(), "show_pregame": show_title("PREGAME", "show_pregame"), "show_postgame": show_title("POSTGAME", "show_postgame"),
          "show_bp": show_title("BATTING PRACTICE", "show_bp"), "up_next": up_next(), "show_bug": live_bug(), "umpires": umpires(),
          "pitch_count": pitch_count(), "talent": talent(), "scoring_summary": scoring(),
          "hr_event": event("HOME", "RUN!", "HR", "Home Run! (Retro)", "lastPlay.runs!=4"),
          "wp_event": event("WILD", "PITCH!", "WP,PB", "Wild Pitch / Passed Ball (Retro)")})
g["hr_event"]["elements"] += [dict(e, id=e["id"] + "g", showIf="lastPlay.runs==4", text=t) for e, t in zip(g["hr_event"]["elements"][:2], ("GRAND", "SLAM!"))]
g["wp_event"]["elements"][0]["text"] = "{lastPlay.word1|upper}"
g["wp_event"]["elements"][1]["text"] = "{lastPlay.word2|upper}"
for tid, word, sub in (("tr_lineup", "LINEUP", "{team.name|upper}"), ("tr_defense", "DEFENSE", "{team.name|upper}"), ("tr_bullpen", "BULLPEN", "PITCHING CHANGE"),
                       ("tr_replay", "REPLAY", "INSTANT REPLAY"), ("tr_final", "FINAL", "{away.abbr} {away.runs}  {home.abbr} {home.runs}"),
                       ("tr_pregame", "PREGAME", "{show.name|upper}"), ("tr_postgame", "POSTGAME", "{show.name|upper}"), ("tr_bp", "BATTING PRACTICE", "{show.name|upper}")):
    g[tid] = word_transition(tid, word, sub)
for gid, cat in (("dueup", "lineups"), ("linescore", "scores")):
    g[gid]["cat"] = cat
g["batter"]["sponsorSlot"] = "lineup_{batter.slot}, batter"
g["pitcher"]["sponsorSlot"] = "pitcher"
# Preset layouts (Custom panel > Presets) in a plain dark look with the retro face, so presets work in this package too
RS = dict(BL.NIGHT, key="retro", font="$font", radius=0, cardRadius=0, panel="rgba(0,0,0,0.78)", panel2="rgba(255,255,255,0.06)",
          dark="rgba(0,0,0,0.85)", strip="#F4EBB0", stripText="#05060A", val="rgba(255,255,255,0.08)", valText="#F4EBB0", shadow="none")
g.update(BL.layouts(RS))
import skin as SK  # noqa: E402
MS = dict(RS, **SK.MARKS)
g["open_station"] = BL.station_open(MS)

doc = {
    "version": 2,
    "name": "Retro",
    "description": "1980s character-generator look: pale-yellow and white text in a blocky terminal face with hard shadows, no boxes, "
                   "cut-on and typed-on reveals. Scorebug, batter / pitcher ID, due up, lineup, linescore, final, standings, matchup, "
                   "custom lines, ticker and a scan-line transition.",
    "theme": {
        "primary": "#05060A", "accent": "#F4EBB0", "text": "#FFFFFF", "dim": "rgba(255,255,255,0.8)", "line": "rgba(255,255,255,0.2)",
        "card": "rgba(0,0,0,0)", "panel": "rgba(0,0,0,0)", "panel2": "rgba(0,0,0,0)",
        "font": "'BBG VT323', 'Courier New', monospace", "font2": "'BBG VT323', 'Courier New', monospace",
        "logo": "", "brandName": "", "openerVideo": "",
    },
    "graphics": g,
}
import sports_lib as SL  # noqa: E402
g.update(SL.all_sports(MS))     # basketball, football, hockey
# Skin: the shared graphics lose their boxes and become CG type (yellow and white with hard shadows) like the rest of Retro.
K = dict(boxless=True, panel="transparent", panel2="transparent", dark="transparent", strip="transparent", stripText=Y_, val="transparent", ink=Y_,
         hi=Y_, hiText=W_, line=Y_, title="#05060A", shadow="none", team=lambda t: "transparent", rule=Y_, text2=Y_, radius=0,
         text={"textShadow": SH, "font": F, "weight": 400, "upper": True})
import rebuild as RB  # noqa: E402


def kit_frame_rt(X, Y, W, H, hb, sub_h, g):
    """No boxes: the title becomes a centred white CG line, the sub line yellow."""
    return {"elements": [], "title": {"font": F, "weight": 400, "color": W_, "textShadow": SH, "align": "center", "italic": False, "tracking": 2, "upper": True},
            "sub": {"font": F, "weight": 400, "color": Y_, "textShadow": SH, "align": "center", "tracking": 2}, "subText": {"color": Y_},
            "headText": {"color": W_, "textShadow": SH, "weight": 400}}


KIT = dict(frame=kit_frame_rt, bar=lambda b, main, role, g: [])

# Game-ops graphics (pitch tracker, pitch clock, bullpen, breaks, fan and sponsor pieces) in the same skin
PRO = BL.pro_suite(dict(RS, **SK.MARKS))
g.update(PRO)
_ONLY = set(k for k in g if k[:3] in ("bk_", "fb_", "hk_") and not k.endswith("scorebug")) | set(PRO)
g = RB.rebuild_all(g, KIT, only=_ONLY)
g = RB.strip_flags(SK.skin_all(g, K, only=_ONLY | {"open_station"}))
for _gid in PRO:
    for _e in g[_gid]["elements"]:
        if _e["type"] == "clock":
            _e["style"]["textShadow"] = SH
            _e["style"]["weight"] = 400


def sport_bug(sport):
    """Text-only CG scorebug, like the baseball one: teams and scores, period and running clock, situation line."""
    X, Y = 40, 26
    E = [T("Period", X, Y, 300, 40, "{sp.statusText}", 38, 0, None, W_),
         T("Away", X, Y + 40, 140, 48, "{away.abbr|upper}", 48, 80),
         T("Away score", X + 150, Y + 40, 90, 48, "{away.score}", 48, 80, align="right", change="flash"),
         T("Home", X, Y + 86, 140, 48, "{home.abbr|upper}", 48, 120),
         T("Home score", X + 150, Y + 86, 90, 48, "{home.score}", 48, 120, align="right", change="flash")]
    E.append(SL.clock("Clock", X + 260, Y + 52, 170, 70, "sp.clock", 58, A("fade", 1, 160, out=CUT), {"font": F}, color=W_, show="status!=FINAL",
                      align="left"))
    E[-1]["style"]["textShadow"] = SH
    E[-1]["style"]["weight"] = 400
    line = {"basketball": "FOULS {away.fouls}-{home.fouls}", "football": "{sp.downText|upper}", "hockey": "SOG {away.shots}-{home.shots}"}[sport]
    E.append(T("Situation", X, Y + 136, 460, 34, line, 30, 200, "status==LIVE", W_, change="flash"))
    if sport == "hockey":
        E.append(T("PP", X, Y + 170, 460, 34, "{sp.ppText} {sp.ppSide|upper}", 30, 240, "sp.ppSide", color="#FF5A4E"))
    if sport == "football":
        E.append(T("Flag", X, Y + 170, 460, 34, "* FLAG *", 30, 0, "sp.flag", color="#FFD400"))
    d = SL._g(RS, sport, "Scorebug (Retro)", "bug", E, "scorebugs")
    d["name"] = "%s: Scorebug (Retro)" % SL.LABEL[sport]
    return d


for sp_, pre_ in SL.PREFIX.items():
    g[pre_ + "scorebug"] = sport_bug(sp_)
doc["graphics"] = g
out = os.path.join(ROOT, "templates", "packages", "retro.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
