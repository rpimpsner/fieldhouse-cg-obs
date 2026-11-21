"""Basketball, football and hockey graphics, drawn in any package style (S from broadcast_lib).

Every graphic carries "sport" so the control panel and OBS only show the sport being broadcast. Data comes from
the Scoring panel's sport card (see sport_game in obs_baseball_graphics.py): {sp.*} for clocks, period and
situation, {away.score} / {home.score}, and per-team timeouts, fouls, bonus, shots, possession and power play.
"""
from broadcast_lib import A, box, txt, img, el, both, logo_or_abbr, sponsor_tab, card, U, L, TG

PREFIX = {"basketball": "bk_", "football": "fb_", "hockey": "hk_"}
LABEL = {"basketball": "Basketball", "football": "Football", "hockey": "Hockey"}
LIVE = "status==LIVE"


def _g(S, sport, name, group, E, cat, **kw):
    d = {"name": "%s: %s" % (LABEL[sport], name), "group": group, "autoHide": 0, "side": "", "sided": False, "elements": E,
         "sport": sport, "cat": cat}
    d.update(kw)
    return d


def clock(name, x, y, w, h, src, size, a, S, color="$text", tenths=True, secs=False, show=None, align="center"):
    return el("clock", name, x, y, w, h, a, show=show, mode="game", src=src,
              style={"color": color, "size": size, "weight": 800, "align": align, "font": S["font"], "tenths": tenths, "secs": secs})


# ------------------------------------------------------------------ scorebug
def scorebug(S, sport):
    """Bottom-centre bar: each team's logo, name and score, then period and game clock (plus shot / play clock),
    with a situation strip under it: bonus, fouls and timeouts (basketball), down and distance, ball on and flag
    (football), shots on goal, power play and empty net (hockey)."""
    f = S["font"]
    W = 1140 if sport != "hockey" else 1060
    X, Y, H = (1920 - W) // 2, 914, 72
    E = []
    for i, side in enumerate(("away", "home")):
        x = X + i * 360
        d = i * 80
        E += [box("%s tile" % side, x, Y, 86, H, None, A(S["in"], 360, d), bg=TG(S, side))]
        E += logo_or_abbr("%s logo" % side, x + 8, Y + 6, 70, H - 12, side, 24, A("pop", 320, 180 + d), S=S)
        E += [box("%s name bg" % side, x + 86, Y, 174, H, None, A("wipe-right", 360, 80 + d), bg=S["panel"]),
              txt("%s name" % side, x + 100, Y, 150, H, U(S, "%s.abbr" % side), 38, A("fade", 260, 260 + d), font=f, weight=800),
              box("%s score bg" % side, x + 260, Y, 100, H, None, A("wipe-right", 360, 140 + d), bg=S["dark"]),
              txt("%s score" % side, x + 260, Y, 100, H, "{%s.score}" % side, 50, A("reveal-up", 300, 320 + d, change="pop"), font=f, weight=800,
                  align="center")]
        if sport in ("basketball", "football"):
            E += [box("%s poss" % side, x + 86, Y + H - 6, 174, 6, "$accent", A("grow-x", 240, 420), show="%s.hasPoss" % side)]
    cx = X + 720
    E += [box("Period bg", cx, Y, 120, H, None, A("wipe-right", 360, 200), bg=S["strip"]),
          txt("Period", cx, Y, 120, H, "{sp.statusText}", 30, A("fade", 260, 380, change="flash"), font=f, weight=800, align="center",
              color=S["stripText"]),
          box("Clock bg", cx + 120, Y, 180, H, None, A("wipe-right", 360, 240), bg=S["panel2"]),
          clock("Clock", cx + 120, Y, 180, H, "sp.clock", 44, A("fade", 260, 420), S, show="status!=FINAL"),
          txt("Final", cx + 120, Y, 180, H, L(S, "Final"), 34, A("fade", 260, 420), show="status==FINAL", font=f, weight=800, align="center")]
    if sport in ("basketball", "football"):
        E += [box("Shot bg", cx + 300, Y, 120, H, "$accent", A("wipe-right", 300, 280), show="sp.hasShot && status==LIVE"),
              clock("Shot", cx + 300, Y, 120, H, "sp.shot", 42, A("fade", 240, 460), S, color=S["hiText"], secs=True, tenths=sport == "basketball",
                    show="sp.hasShot && status==LIVE")]
    # situation strip
    SY, SH = Y + H, 34
    if sport == "basketball":
        for i, side in enumerate(("away", "home")):
            x = X + i * 360
            E += [box("%s strip" % side, x, SY, 360, SH, None, A("wipe-down", 260, 480), show=LIVE, bg=S["dark"]),
                  txt("%s fouls" % side, x + 12, SY, 160, SH, L(S, "Fouls {%s.fouls}" % side), 20, A("fade", 220, 560, change="flash"), show=LIVE,
                      font=f, weight=800, color="$dim"),
                  txt("%s TO" % side, x + 150, SY, 110, SH, L(S, "TOL {%s.timeouts}" % side), 20, A("fade", 220, 580, change="flash"), show=LIVE,
                      font=f, weight=800, color="$dim"),
                  box("%s bonus bg" % side, x + 262, SY + 4, 92, SH - 8, "$accent", A("pop", 260, 600), show=both(LIVE, "%s.bonus" % side),
                      radius=S["radius"]),
                  txt("%s bonus" % side, x + 262, SY + 4, 92, SH - 8, L(S, "Bonus"), 18, A("fade", 220, 620), show=both(LIVE, "%s.bonus" % side),
                      font=f, weight=800, align="center", color=S["hiText"])]
    elif sport == "football":
        E += [box("Strip", X, SY, W, SH, None, A("wipe-down", 260, 480), show=LIVE, bg=S["dark"])]
        for i, side in enumerate(("away", "home")):
            x = X + i * 360
            E += [el("dots", "%s timeouts" % side, x + 96, SY + 7, 80, 20, A("fade", 220, 560), show=LIVE, bind="%s.timeouts" % side,
                     style={"total": 3, "size": 10, "gap": 8, "on": "$accent", "off": "#FFFFFF@0.22", "shape": "square", "align": "left"})]
        E += [txt("Down", X + 720, SY, 300, SH, U(S, "sp.downText"), 22, A("fade", 220, 580, change="flash"), show=both(LIVE, "!sp.flag"), font=f,
                  weight=800, align="center", color="$accent"),
              txt("Ball on", X + 1000, SY, W - 1012, SH, L(S, "Ball on {sp.ballOn}"), 18, A("fade", 220, 600), show=both(LIVE, "sp.ballOn", "!sp.flag"),
                  font=f, weight=700, align="right", color="$dim"),
              box("Flag bg", X + 720, SY, W - 720, SH, "#FFD400", A("wipe-right", 220, 0, change="flash"), show=both(LIVE, "sp.flag")),
              txt("Flag", X + 720, SY, W - 720, SH, L(S, "Flag"), 24, A("fade", 200, 60), show=both(LIVE, "sp.flag"), font=f, weight=800,
                  align="center", color="#111111", tracking=4)]
    else:   # hockey
        for i, side in enumerate(("away", "home")):
            x = X + i * 360
            E += [box("%s strip" % side, x, SY, 360, SH, None, A("wipe-down", 260, 480), show=LIVE, bg=S["dark"]),
                  txt("%s SOG" % side, x + 12, SY, 150, SH, L(S, "SOG {%s.shots}" % side), 20, A("fade", 220, 560, change="flash"), show=LIVE,
                      font=f, weight=800, color="$dim"),
                  box("%s PP bg" % side, x + 160, SY + 3, 196, SH - 6, None, A("wipe-right", 260, 0), show=both(LIVE, "%s.onPP" % side),
                      bg=TG(S, side), radius=S["radius"]),
                  txt("%s PP" % side, x + 168, SY + 3, 110, SH - 6, U(S, "sp.ppText"), 17, A("fade", 200, 80), show=both(LIVE, "%s.onPP" % side),
                      font=f, weight=800),
                  clock("%s PP clock" % side, x + 276, SY + 3, 76, SH - 6, "sp.pp", 20, A("fade", 200, 100), S, tenths=False,
                        show=both(LIVE, "%s.onPP" % side), align="right"),
                  txt("%s EN" % side, x + 160, SY, 196, SH, L(S, "Empty net"), 18, A("fade", 200, 0, change="flash"),
                      show=both(LIVE, "%s.en" % side, "!%s.onPP" % side), font=f, weight=800, align="right", color="$accent")]
        E += [box("Strip right", X + 720, SY, W - 720, SH, None, A("wipe-down", 260, 480), show=LIVE, bg=S["dark"])]
    E += sponsor_tab(X + W - 300, Y - 44, 300, 44, 520, radius=S["radius"], a_type="wipe-up")
    return _g(S, sport, "Scorebug", "bug", E, "scorebugs", sponsorSlot="scorebug")


# ------------------------------------------------------------------ player lower third
def player_lower(S, sport):
    f = S["font"]
    X, Y = 236, 852
    E = [box("Team tile", X - 124, Y, 124, 124, None, A("pop", 380, 0), bg=TG(S, "team"))]
    E += logo_or_abbr("Team mark", X - 114, Y + 10, 104, 104, "team", 30, A("pop", 340, 160), S=S)
    E += [box("Name bar", X, Y, 840, 70, None, A("wipe-right", 380, 120), bg=S["panel"]),
          txt("Number", X + 20, Y, 90, 70, "#{sp.player.number}", 34, A("fade", 240, 320), show="sp.player.number", font=f, weight=800, color="$accent"),
          txt("Name", X + 120, Y, 560, 70, U(S, "sp.player.name"), 48, A("reveal-up", 360, 300), font=f, weight=800),
          txt("Pos", X + 680, Y, 140, 70, U(S, "sp.player.pos"), 28, A("fade", 240, 360), show="sp.player.pos", font=f, weight=800, align="right",
              color="$dim"),
          box("Line bar", X, Y + 70, 840, 54, None, A("wipe-right", 380, 240), bg=S["strip"]),
          txt("Line", X + 20, Y + 70, 800, 54, U(S, "sp.player.line"), 28, A("fade", 260, 480, change="flash"), font=f, weight=800,
              color=S["stripText"]),
          box("Note bar", X + 30, Y + 124, 810, 34, None, A("wipe-down", 240, 440), show="sp.player.note", bg=S["dark"]),
          txt("Note", X + 50, Y + 124, 780, 34, U(S, "sp.player.note"), 20, A("fade", 220, 560), show="sp.player.note", font=f, weight=700,
              color="$dim")]
    E += sponsor_tab(X + 850, Y, 240, 70, 520, radius=S["radius"], a_type="wipe-right", label_w=96)
    return _g(S, sport, "Player Lower Third", "lower", E, "lower_other", autoHide=9, side="home", sided=True, sponsorSlot="player")


# ------------------------------------------------------------------ team stats
def team_stats(S, sport):
    f = S["font"]
    X, Y, W = 560, 150, 800
    c_ = card(S, "Card", X, Y, W, 160 + 8 * 74)
    c_["growWith"] = {"bind": "sp.stats", "base": 146 + 14, "per": 74, "max": 8, "min": 300}
    E = [c_,
         box("Head", X + 12, Y + 12, W - 24, 120, None, A("wipe-right", 360, 200), bg=S["dark"])]
    for i, side in enumerate(("away", "home")):
        x = X + 30 if i == 0 else X + W - 150
        E += logo_or_abbr("%s logo" % side, x, Y + 22, 120, 76, side, 30, A("pop", 320, 320 + i * 80), S=S)
        E += [txt("%s abbr" % side, x, Y + 98, 120, 30, U(S, "%s.abbr" % side), 22, A("fade", 240, 380), font=f, weight=800, align="center")]
    E += [txt("Title", X + 170, Y + 12, W - 340, 120, L(S, "Team Stats"), 46, A("reveal-up", 360, 300), font=f, weight=800, align="center"),
          txt("Sub", X + 170, Y + 92, W - 340, 36, "{sp.statusText}", 22, A("fade", 240, 400), font=f, weight=700, align="center", color="$dim")]
    for i in range(8):
        p = "sp.stats.%d" % i
        y = Y + 146 + i * 74
        d = 480 + i * 80
        E += [box("Row %d" % i, X + 12, y, W - 24, 66, None, A("wipe-right", 300, d), show=p + ".label", bg=S["panel2"]),
              txt("Row %d away" % i, X + 30, y, 150, 66, "{%s.away}" % p, 36, A("fade", 240, d + 80), show=p + ".label", font=f, weight=800),
              txt("Row %d label" % i, X + 180, y, W - 360, 66, U(S, p + ".label"), 26, A("fade", 240, d + 80), show=p + ".label", font=f, weight=700,
                  align="center", color="$dim"),
              txt("Row %d home" % i, X + W - 180, y, 150, 66, "{%s.home}" % p, 36, A("fade", 240, d + 80), show=p + ".label", font=f, weight=800,
                  align="right")]
    return _g(S, sport, "Team Stats", "full", E, "scores", sponsorSlot="stats")


# ------------------------------------------------------------------ score by period
def linescore(S, sport):
    f = S["font"]
    X, Y, CW = 520, 820, 96
    W = 260 + 6 * CW + 120
    E = [box("Head", X, Y, W, 44, None, A("wipe-up", 300, 0), bg=S["dark"]),
         txt("Status", X + 16, Y, 240, 44, U(S, "sp.statusText"), 22, A("fade", 240, 160), font=f, weight=800, color="$accent")]
    for j in range(6):
        E += [txt("Col %d" % j, X + 260 + j * CW, Y, CW, 44, "{sp.lineCols.%d}" % j, 20, A("fade", 240, 200 + j * 40), show="sp.lineCols.%d" % j,
                  font=f, weight=800, align="center", color="$dim")]
    E += [txt("Col T", X + 260 + 6 * CW, Y, 120, 44, L(S, "T"), 22, A("fade", 240, 440), font=f, weight=800, align="center", color="$accent")]
    for r, side in enumerate(("away", "home")):
        y = Y + 44 + r * 64
        d = 200 + r * 120
        E += [box("%s row" % side, X, y, W, 64, None, A("wipe-right", 340, d), bg=S["panel"] if r == 0 else S["panel2"]),
              box("%s chip" % side, X, y, 10, 64, "{%s.color}" % side, A("grow-y", 260, d + 100))]
        E += logo_or_abbr("%s logo" % side, X + 20, y + 6, 60, 52, side, 20, A("fade", 240, d + 160), S=S)
        E += [txt("%s name" % side, X + 90, y, 160, 64, U(S, "%s.abbr" % side), 34, A("fade", 240, d + 160), font=f, weight=800)]
        for j in range(6):
            E += [txt("%s %d" % (side, j), X + 260 + j * CW, y, CW, 64, "{linescore.%s.%d}" % (side, j), 34, A("fade", 240, d + 200 + j * 30,
                      change="flash"), show="sp.lineCols.%d" % j, font=f, weight=800, align="center")]
        E += [box("%s total bg" % side, X + 260 + 6 * CW, y, 120, 64, None, A("fade", 240, d + 260), bg=S["val"]),
              txt("%s total" % side, X + 260 + 6 * CW, y, 120, 64, "{%s.score}" % side, 40, A("fade", 240, d + 300, change="pop"), font=f, weight=800,
                  align="center", color=S["valText"])]
    return _g(S, sport, "Score by " + ("Period" if sport == "hockey" else "Quarter"), "lower", E, "scores")


# ------------------------------------------------------------------ final
def final(S, sport):
    f = S["font"]
    X, Y, W = 360, 200, 1200
    E = [card(S, "Card", X, Y, W, 490),
         box("Header", X + 14, Y + 14, W - 28, 100, None, A("wipe-right", 360, 200), bg=S["dark"]),
         txt("Final", X + 40, Y + 14, 500, 100, "{sp.statusText}", 60, A("reveal-up", 380, 320), font=f, weight=800),
         txt("Venue", X + 520, Y + 14, W - 560, 100, U(S, "venue"), 28, A("fade", 300, 420), show="venue", font=f, weight=700, color="$dim", align="right")]
    for i, side in enumerate(("away", "home")):
        y = Y + 132 + i * 170
        E += [box("%s row" % side, X + 14, y, W - 28, 156, None, A("wipe-right", 380, 300 + i * 100), bg=TG(S, side))]
        E += logo_or_abbr("%s logo" % side, X + 34, y + 14, 150, 128, side, 44, A("pop", 340, 420 + i * 100), S=S)
        E += [txt("%s name" % side, X + 210, y, 700, 110, U(S, "%s.name" % side), 56, A("reveal-up", 360, 460 + i * 100), font=f, weight=800,
                  textShadow=True),
              txt("%s record" % side, X + 210, y + 96, 400, 46, "{%s.record}" % side, 28, A("fade", 260, 560), show="%s.record" % side, font=f, weight=700),
              box("%s score bg" % side, X + W - 230, y + 14, 196, 128, None, A("pop", 320, 520 + i * 100), bg=S["val"], show="leader!=%s" % side,
                  radius=S["radius"]),
              box("%s score win" % side, X + W - 230, y + 14, 196, 128, S["hi"], A("pop", 320, 520 + i * 100), show="leader==%s" % side, radius=S["radius"]),
              txt("%s score" % side, X + W - 230, y + 14, 196, 128, "{%s.score}" % side, 96, A("fade", 260, 620 + i * 100), show="leader!=%s" % side,
                  font=f, weight=800, align="center", color=S["valText"]),
              txt("%s score w" % side, X + W - 230, y + 14, 196, 128, "{%s.score}" % side, 96, A("fade", 260, 620 + i * 100), show="leader==%s" % side,
                  font=f, weight=800, align="center", color=S["hiText"])]
    E += sponsor_tab(X + W - 360, Y + 490, 360, 64, 900, radius=S["radius"], a_type="wipe-down")
    return _g(S, sport, "Final", "full", E, "scores", sponsorSlot="final")


# ------------------------------------------------------------------ starting lineup
def lineup(S, sport):
    f = S["font"]
    rows = {"basketball": 12, "football": 11, "hockey": 12}[sport]
    X, Y, W, RH = 560, 90, 800, 66
    title = {"basketball": "Starting Lineup", "football": "Starters", "hockey": "Starting Lineup"}[sport]
    c_ = card(S, "Card", X, Y, W, 140 + rows * RH)
    c_["growWith"] = {"bind": "team.lineup", "base": 134 + 14, "per": RH, "max": rows, "min": 300}
    E = [c_,
         box("Head", X + 12, Y + 12, W - 24, 112, None, A("wipe-right", 360, 200), bg=TG(S, "team"))]
    E += logo_or_abbr("Logo", X + 26, Y + 20, 120, 96, "team", 30, A("pop", 320, 320), S=S)
    E += [txt("Team", X + 166, Y + 14, W - 190, 66, U(S, "team.name"), 46, A("reveal-up", 360, 340), font=f, weight=800, textShadow=True),
          txt("Title", X + 166, Y + 74, W - 190, 40, L(S, title), 26, A("fade", 260, 420), font=f, weight=700)]
    for i in range(rows):
        p = "team.lineup.%d" % i
        y = Y + 134 + i * RH
        d = 460 + i * 60
        E += [box("Row %d" % i, X + 12, y, W - 24, RH - 6, None, A("wipe-right", 280, d), show=p + ".name", bg=S["panel2"] if i % 2 else S["panel"]),
              txt("Num %d" % i, X + 26, y, 80, RH - 6, "{%s.number}" % p, 32, A("fade", 220, d + 60), show=p + ".name", font=f, weight=800,
                  color="$accent", align="center"),
              txt("Name %d" % i, X + 120, y, 460, RH - 6, U(S, p + ".name"), 32, A("fade", 220, d + 60), show=p + ".name", font=f, weight=800),
              txt("Pos %d" % i, X + 580, y, 90, RH - 6, "{%s.pos}" % p, 26, A("fade", 220, d + 60), show=p + ".name", font=f, weight=800,
                  color="$dim", align="center"),
              txt("Line %d" % i, X + 670, y, W - 700, RH - 6, "{%s.line}" % p, 22, A("fade", 220, d + 60), show=p + ".line", font=f, weight=700,
                  align="right")]
    return _g(S, sport, title, "full", E, "lineups", side="home", sided=True)


# ------------------------------------------------------------------ scoring stingers
def stinger(S, sport, word1, word2, trigger, name, show=None):
    f = S["font"]
    Y, H = 380, 320
    E = [box("Slab", 0, Y, 1920, H, None, A("wipe-right", 320, 0, out={"type": "wipe-right", "dur": 320, "delay": 0, "ease": "in"}), bg=TG(S, "scorer")),
         box("Rule top", 0, Y, 1920, 10, "$accent", A("grow-x", 300, 120)),
         box("Rule bottom", 0, Y + H - 10, 1920, 10, "$accent", A("grow-x", 300, 160))]
    E += logo_or_abbr("Logo", 140, Y + 40, 260, 240, "scorer", 60, A("pop", 400, 260), S=S)
    E += [txt("Word", 440, Y + 10, 1340, 200, L(S, word1), 190 if len(word1) < 10 else 150, A("letters", 500, 300, stagger=45), font=f, weight=800,
              textShadow=True, show=show),
          txt("Team", 440, Y + 200, 1340, 100, U(S, "scorer.name") + ("  " + word2 if word2 else ""), 52, A("fade", 300, 700), font=f, weight=800,
              textShadow=True)]
    return _g(S, sport, name, "event", E, "events", autoHide=4, trigger=trigger, sponsorSlot="score_event")


def timeout_bug(S, sport):
    f = S["font"]
    X, Y, W = 1440, 640, 420
    E = [box("Card", X, Y, W, 170, None, A("wipe-left", 380, 0), bg=TG(S, "team"), radius=S["radius"], shadow=True)]
    E += logo_or_abbr("Logo", X + 16, Y + 16, 110, 88, "team", 30, A("pop", 320, 200), S=S)
    E += [txt("Timeout", X + 140, Y + 10, W - 156, 64, L(S, "Timeout"), 50, A("reveal-up", 340, 260), font=f, weight=800, textShadow=True),
          txt("Team", X + 140, Y + 66, W - 156, 44, U(S, "team.name"), 28, A("fade", 260, 360), font=f, weight=800),
          box("Strip", X, Y + 120, W, 50, None, A("wipe-down", 260, 400), bg=S["dark"]),
          txt("Left", X + 16, Y + 120, W - 32, 50, L(S, "{team.timeouts} timeouts left"), 26, A("fade", 240, 480), font=f, weight=800, color="$accent")]
    return _g(S, sport, "Timeout", "panel", E, "panels", side="home", sided=True, autoHide=8)


def penalty_lower(S):
    """Hockey penalty: team, what it was (Scoring > Penalty label) and the minutes."""
    f = S["font"]
    X, Y = 236, 870
    E = [box("Tile", X - 110, Y, 110, 110, None, A("pop", 360, 0), bg=TG(S, "team"))]
    E += logo_or_abbr("Mark", X - 100, Y + 10, 90, 90, "team", 28, A("pop", 320, 160), S=S)
    E += [box("Bar", X, Y, 780, 62, None, A("wipe-right", 360, 120), bg=S["panel"]),
          txt("Word", X + 20, Y, 260, 62, L(S, "Penalty"), 40, A("reveal-up", 340, 300), font=f, weight=800, color="$accent"),
          txt("Team", X + 280, Y, 480, 62, U(S, "team.name"), 32, A("fade", 260, 340), font=f, weight=800, align="right"),
          box("Line bar", X, Y + 62, 780, 48, None, A("wipe-right", 360, 240), bg=S["strip"]),
          txt("Label", X + 20, Y + 62, 740, 48, U(S, "team.penLast"), 28, A("fade", 240, 420), show="team.penLast", font=f, weight=800,
              color=S["stripText"])]
    return _g(S, "hockey", "Penalty", "lower", E, "lower_other", side="home", sided=True, autoHide=7)


def sport_graphics(S, sport):
    p = PREFIX[sport]
    g = {p + "scorebug": scorebug(S, sport), p + "player": player_lower(S, sport), p + "stats": team_stats(S, sport),
         p + "linescore": linescore(S, sport), p + "final": final(S, sport), p + "lineup": lineup(S, sport),
         p + "timeout": timeout_bug(S, sport)}
    if sport == "hockey":
        g[p + "goal"] = stinger(S, sport, "Goal!", "", "GOAL", "Goal!")
        g[p + "penalty"] = penalty_lower(S)
    elif sport == "football":
        g[p + "td"] = stinger(S, sport, "Touchdown!", "", "TD", "Touchdown!")
        g[p + "fg"] = stinger(S, sport, "Field Goal", "", "FG", "Field Goal")
    else:
        g[p + "three"] = stinger(S, sport, "3 Pointer!", "", "3PT", "3-Pointer!")
    return g


def all_sports(S):
    g = {}
    for sport in PREFIX:
        g.update(sport_graphics(S, sport))
    return g
