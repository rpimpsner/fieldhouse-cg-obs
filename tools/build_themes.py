"""Builds the theme packages: Stars & Stripes, Hyperspace, '90s Throwback, Shaolin Cipher, Vegas Showroom, Noir Detective,
Arcade 8-Bit, Old-Time Radio, Spaghetti Western, Halloween, Holiday, Synthwave, Comic Book and Ballpark Scoreboard.

Each one is inspired by a style or era only: no film, artist, group or brand logos, characters, likenesses or titles.
Every package has the full graphic library restyled in its look plus a themed scorebug, lower thirds, show open,
home-run stinger, player cards and its own signature pieces.
Run:  python tools/build_themes.py [key ...]   (after tools/build_night_game.py)
"""
import sys

import theme_lib as TL
from theme_lib import A, box, img, el, logo_or_abbr, W, D_, up, backdrop, net_mark, OUT_, LIVE, H, F, COND


def fs(name, fb=None):
    return "'BBG %s', %s" % (name, fb or COND)


def solid_team(t, dark=72):
    return "linear-gradient(180deg, {%s.color}, color-mix(in srgb, {%s.color} %d%%, #000))" % (t, t, dark)


def burst(name, cx, cy, r, col, d, spin=None):
    """Firework / sunburst: a conic ray disc."""
    return box(name, cx - r, cy - r, 2 * r, 2 * r, None, A("pop", 500, d, loop={"type": "spin", "dur": spin} if spin else {"type": "breathe", "dur": 900,
               "amount": 0.08}), bg="repeating-conic-gradient(%s 0 4deg, transparent 4deg 18deg)" % col, radius="50%")


def star_burst(name, cx, cy, r, col, d, border="#000000"):
    """Comic 'POW' burst: four rotated squares make a 16-point star."""
    E = []
    for i, rot in enumerate((0, 22.5, 45, 67.5)):
        E.append(box("%s %d" % (name, i + 1), cx - r, cy - r, 2 * r, 2 * r, col, A("pop", 360, d + i * 30), rotate=rot, borderW=6, borderColor=border))
    E.append(box(name + " core", cx - r + 18, cy - r + 18, 2 * r - 36, 2 * r - 36, col, A("pop", 360, d + 120), radius="50%"))
    return E


def bulbs(name, x, y, w, h, d, col="#FFF3C4", glow="#FFC94A"):
    """Marquee bulb strip: two staggered rows of bulbs, one chasing and one twinkling."""
    s = h
    bg = "radial-gradient(circle, %s 0 %dpx, %s %dpx, transparent %dpx) 0 0/%dpx %dpx repeat-x" % (col, s // 4, glow, s // 4 + 2, s // 2, s * 2, s)
    bg2 = "radial-gradient(circle, %s 0 %dpx, %s %dpx, transparent %dpx) %dpx 0/%dpx %dpx repeat-x" % (col, s // 4, glow, s // 4 + 2, s // 2, s, s * 2, s)
    return [box(name, x, y, w, h, None, A("fade", 300, d, loop={"type": "chase", "dur": 900, "amount": 0.2}), bg=bg),
            box(name + " b", x, y, w, h, None, A("fade", 300, d, loop={"type": "pulse", "dur": 450, "amount": 0.25}), bg=bg2)]


# ====================================================================== 1. STARS & STRIPES
NAVY, RED, GOLD = "#0A2240", "#BF1E2E", "#F2C94C"
FLAG = "repeating-linear-gradient(180deg, %s 0 10px, #FFFFFF 10px 20px)" % RED


def usa_bunting(d=0):
    E = []
    for i in range(5):
        E.append(box("Bunting %d" % (i + 1), i * 384, -6, 384, 150, None, A("slide-down", 500, d + i * 80, dist=60),
                     bg="linear-gradient(180deg, %s 0 34%%, #FFFFFF 34%% 66%%, %s 66%%)" % (NAVY, RED), radius="0 0 50% 50% / 0 0 100% 100%",
                     borderW=3, borderColor="#00000044"))
        E.append(W(USA, "Bunting star %d" % (i + 1), i * 384, 0, 384, 50, "★", 36, A("fade", 300, d + 300 + i * 80), align="center"))
    return E


def usa_fireworks(d=0):
    return [burst("Firework 1", 300, 260, 180, GOLD, d, spin=9000), burst("Firework 2", 1640, 220, 150, "#FFFFFF", d + 200, spin=7000),
            burst("Firework 3", 1500, 820, 130, RED, d + 400, spin=8000), burst("Firework 4", 420, 860, 120, "#8FC2FF", d + 300, spin=6000)]


def usa_extras(T):
    post = backdrop(T) + usa_fireworks(300)
    post += [box("Postcard", 260, 160, 1400, 760, "#F6EEDC", A("zoom-out", 600, 0, out=OUT_), rotate=-2, borderW=14, borderColor="#FFFFFF", shadow=T["shadow"]),
             box("Postcard stripe", 300, 760, 1320, 40, None, A("wipe-right", 500, 400), bg=FLAG, rotate=-2),
             W(T, "Greetings", 320, 220, 900, 90, "GREETINGS FROM", 64, A("slide-right", 500, 500, dist=40), color=NAVY, font=fs("Pacifico", "cursive"),
               weight=400, rotate=-2),
             D_(T, "Venue", 320, 330, 1280, 300, "{venue|upper}", 150, A("zoom-out", 600, 700), color=RED, textStroke="3px " + NAVY, glow="",
                wrap=True, lineH=0.95, textShadow="6px 6px 0 " + NAVY),
             box("Stamp", 1400, 200, 190, 220, "#FFFFFF", A("pop", 400, 900), borderW=6, borderColor=RED, rotate=4)]
    post += net_mark(T, "Stamp mark", 1420, 230, 150, 150, A("fade", 300, 1000))
    post += [W(T, "Postmark", 1180, 640, 420, 80, up(T, "{away.nick} at {home.nick} · {seasonYear}"), 30, A("fade", 400, 1100), color=NAVY,
               align="right")]
    anth = backdrop(T) + usa_bunting(0)
    anth += [D_(T, "Rise", 160, 330, 1600, 140, "PLEASE RISE", 130, A("reveal-up", 600, 500), align="center"),
             W(T, "For", 160, 480, 1600, 70, "FOR THE NATIONAL ANTHEM", 52, A("fade", 500, 900), align="center", color=GOLD, tracking=6),
             box("Rule", 760, 580, 400, 6, None, A("grow-x", 400, 1100), bg=FLAG),
             W(T, "Performer label", 160, 620, 1600, 50, "PERFORMED BY", 32, A("fade", 400, 1200), show="notes.kicker", align="center", color=T["dim"]),
             D_(T, "Performer", 160, 670, 1600, 110, "{notes.kicker|upper}", 80, A("reveal-up", 500, 1300), show="notes.kicker", align="center")]
    return {"postcard": {"name": "Postcard: Greetings From", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": post},
            "anthem": {"name": "Please Rise (Anthem)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": anth}}


USA = TL.defaults(dict(
    key="usa", file="stars-and-stripes", name="Stars & Stripes", font=fs("Alfa Slab One"), deco=fs("Alfa Slab One"),
    desc="Fourth of July and Americana: navy and red with white stars, flag-stripe ribbons, bunting, fireworks. Firework home-run "
         "stinger, a vintage postcard venue card and a Please Rise anthem card. Every graphic type, plus basketball, football and hockey.",
    bg=NAVY, panel="linear-gradient(180deg, #13305F, #0A2240)", panel2="linear-gradient(180deg, #1B3B70, #0F2A52)", dark="#081A33", head=RED,
    strip="linear-gradient(180deg, #FFFFFF, #E9EBF1)", stripText=NAVY, val="linear-gradient(180deg, #FFFFFF, #E9EBF1)", valText=NAVY, hi=GOLD, hiText=NAVY,
    edge="#FFFFFF@0.35", r=4, title="linear-gradient(180deg, #0A2240 0%, #13305F 55%, #0A2240 100%)",
    texture="radial-gradient(circle, rgba(255,255,255,.16) 1.8px, transparent 2.4px) 0 0/52px 52px",
    rule=RED, hr_word="HOME RUN!", hr_band="linear-gradient(180deg, #13305F, #0A2240)", open_kicker="★  {seasonYear}  ★",
    bug_under=lambda X, Y, Wd, Hh: [box("Ribbon", X + 8, Y - 8, Wd - 16, 10, None, A("wipe-right", 400, 100), bg=FLAG)],
    lt_decor=lambda X, Y, Wd, Hh: [box("Ribbon", X + 106, Y - 8, 560, 8, None, A("wipe-right", 400, 300), bg="linear-gradient(90deg, %s 0 33%%, "
                                       "#FFFFFF 33%% 66%%, %s 66%%)" % (NAVY, RED))],
    open_decor=lambda: usa_bunting(200) + usa_fireworks(600), hr_decor=lambda: usa_fireworks(200),
    hr_under=lambda: [box("Stripes", 0, 300, 1920, 480, None, A("wipe-center", 300, 0, out=OUT_), bg=FLAG)],
    extras=usa_extras))


# ====================================================================== 2. HYPERSPACE
STARS = ("radial-gradient(1.6px 1.6px at 20px 30px, #fff, transparent) 0 0/180px 180px, radial-gradient(1.2px 1.2px at 90px 110px, #cfe3ff, transparent) "
         "0 0/180px 180px, radial-gradient(1px 1px at 140px 60px, #fff, transparent) 0 0/120px 120px, radial-gradient(1.4px 1.4px at 50px 150px, #fff, "
         "transparent) 0 0/240px 240px")
SPACE = STARS + ", radial-gradient(ellipse at 50% 120%, #10204A 0%, #000 60%)"
CYAN = "#7FD4FF"
GOLDY = "#FFD54A"


def hud(X, Y, Wd, Hh, d=300, c=CYAN, L=22):
    E = []
    for i, (x, y) in enumerate(((X - 6, Y - 6), (X + Wd + 2, Y - 6), (X - 6, Y + Hh + 2), (X + Wd + 2, Y + Hh + 2))):
        sx = x if i % 2 == 0 else x - L + 4
        sy = y if i < 2 else y - L + 4
        E += [box("Bracket %d h" % (i + 1), sx, y, L, 4, c, A("grow-x", 300, d)), box("Bracket %d v" % (i + 1), x, sy, 4, L, c, A("grow-y", 300, d))]
    return E


def streaks(d=0):
    return [box("Streaks", 0, 0, 1920, 1080, None, A("wipe-center", 600, d, out=OUT_),
                bg="repeating-linear-gradient(0deg, transparent 0 13px, rgba(190,220,255,.65) 13px 14px, transparent 14px 31px, rgba(255,255,255,.4) 31px 32px)"),
            box("Streak core", 0, 0, 1920, 1080, None, A("fade", 400, d + 100), bg="radial-gradient(ellipse at center, #000 0 18%, rgba(0,0,0,.6) 40%, transparent 70%)")]


def saber(name, x, y, w, h, col, d, vertical=False):
    g = "linear-gradient(%s, transparent, %s 30%%, #FFFFFF 50%%, %s 70%%, transparent)" % ("90deg" if vertical else "180deg", col, col)
    return box(name, x, y, w, h, None, A("grow-y" if vertical else "grow-x", 500, d, loop={"type": "pulse", "dur": 160, "amount": 0.85}), bg=g)


def hyper_extras(T):
    crawl = [box("Space", 0, 0, 1920, 1080, None, A("fade", 600, 0, out=OUT_), bg=SPACE),
             D_(T, "Show", 160, 120, 1600, 160, "{show.name|upper}", 110, A("zoom-out", 1600, 300), align="center"),
             W(T, "Kicker", 160, 290, 1600, 60, "TONIGHT · {away.nick|upper} AT {home.nick|upper}", 36, A("fade", 800, 1200), align="center", color=CYAN,
               font=H, tracking=4),
             W(T, "Crawl", 360, 400, 1200, 620, "{notes.b1}\n\n{notes.b2}\n\n{notes.b3}", 54, A("slide-up", 14000, 1800, dist=700, ease="linear"),
               align="center", color=GOLDY, wrap=True, fit=False, lineH=1.2, font=H, valign="top"),
             box("Fade top", 0, 360, 1920, 140, None, A("fade", 400, 0), bg="linear-gradient(180deg, #000, transparent)")]
    vs = [box("Space", 0, 0, 1920, 1080, None, A("fade", 500, 0, out=OUT_), bg=SPACE)]
    for i, side in enumerate(("away", "home")):
        x = 0 if i == 0 else 980
        vs += [box("%s glow" % side, x, 0, 940, 1080, None, A("fade", 600, 200 + i * 150),
                   bg="radial-gradient(ellipse at %s 50%%, color-mix(in srgb, {%s.color} 55%%, transparent), transparent 70%%)" % ("30%" if i == 0 else "70%",
                                                                                                                            side))]
        vs += logo_or_abbr("%s logo" % side, x + 220, 240, 500, 420, side, 160, A("zoom-out", 700, 500 + i * 200), S={"font": H})
        vs += [D_(T, "%s nick" % side, x + 40, 700, 860, 120, "{%s.nick|upper}" % side, 80, A("reveal-up", 500, 800 + i * 200), align="center"),
               W(T, "%s record" % side, x + 40, 820, 860, 60, "{%s.record}" % side, 40, A("fade", 400, 1000 + i * 200), align="center", color=CYAN)]
    vs += [saber("Saber", 950, 80, 20, 920, CYAN, 300, vertical=True), D_(T, "Vs", 860, 470, 200, 140, "VS", 100, A("pop", 400, 1200), align="center")]
    return {"crawl": {"name": "Opening Crawl", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": crawl},
            "versus": {"name": "Versus Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": vs}}


HYPER = TL.defaults(dict(
    key="hyper", file="hyperspace", name="Hyperspace", font=fs("Orbitron"), deco=fs("Orbitron"),
    desc="Space-opera look: starfields, gold titles, cyan cockpit brackets and glowing energy-blade rules. Hyperspace streak transitions, "
         "an opening text crawl, a glowing Versus card and a holographic flicker on the lower thirds. Every graphic type, plus basketball, "
         "football and hockey.",
    bg="#000000", panel="linear-gradient(180deg, rgba(10,16,30,.95), rgba(3,6,12,.96))", panel2="linear-gradient(180deg, rgba(16,26,46,.95), rgba(6,10,20,.96))",
    dark="rgba(2,4,8,.96)", strip="linear-gradient(90deg, rgba(14,28,52,.96), rgba(4,8,16,.96))", stripText="#E8F6FF", val="#05080F", valText=GOLDY,
    hi=GOLDY, hiText="#000", edge=CYAN + "@0.55", title_color=GOLDY, glow="0 0 18px rgba(255,213,74,.45)", r=2, title=SPACE, rule=CYAN,
    team=lambda t: "linear-gradient(180deg, color-mix(in srgb, {%s.color} 70%%, #000), #04060C)" % t, base_on=GOLDY, base_off=CYAN + "@0.25",
    shadow="0 0 18px rgba(127,212,255,.25)", hr_word="HOME RUN", hr_band="rgba(0,0,0,.85)",
    bug_decor=lambda X, Y, Wd, Hh: hud(X, Y, Wd, Hh) + [box("Radar", X + 54 + 92 + 60 + 6 + 104 + 18, Y + 2, 68, 68, None, A("scale", 500, 400,
                                                         loop={"type": "spin", "dur": 6000}), radius="50%", borderW=1, borderColor=CYAN + "@0.5",
                                                         bg="conic-gradient(from 0deg, rgba(127,212,255,.35), transparent 25%)", show=LIVE)],
    lt_decor=lambda X, Y, Wd, Hh: [saber("Blade", X + 110, Y - 4, 560, 6, CYAN, 400),
                                   box("Holo", X + 110, Y, 560, Hh, None, A("fade", 300, 500, loop={"type": "pulse", "dur": 2200, "amount": 0.55}),
                                       bg="repeating-linear-gradient(0deg, rgba(127,212,255,.12) 0 2px, transparent 2px 5px)")] + hud(X, Y, Wd, Hh, 600),
    open_decor=lambda: streaks(100), hr_under=lambda: [box("Space", 0, 0, 1920, 1080, None, A("fade", 300, 0, out=OUT_), bg=SPACE)] + streaks(0), tr_decor=lambda TA: [dict(e, anim=TA("wipe-center", 500, 0)) for e in streaks(0)[:1]],
    hr_decor=lambda: [saber("Blade top", 0, 324, 1920, 8, CYAN, 300), saber("Blade bottom", 0, 748, 1920, 8, "#FF4A4A", 400)],
    extras=hyper_extras))


# ====================================================================== 3. '90s
TEAL, PURP, MAG, YEL9 = "#00B3B3", "#5B2A86", "#FF2E93", "#FFE600"
MEMPHIS = ("radial-gradient(circle, %s 3px, transparent 3.5px) 0 0/80px 80px, radial-gradient(circle, %s 4px, transparent 4.5px) 40px 40px/80px 80px, "
           "repeating-linear-gradient(45deg, transparent 0 34px, rgba(255,46,147,.22) 34px 38px)") % (YEL9, TEAL)


def squiggles(d=0):
    E = []
    for i, (x, y, c, rot) in enumerate(((120, 120, MAG, 20), (1640, 160, TEAL, -15), (1700, 820, YEL9, 35), (180, 860, TEAL, -30))):
        E += [box("Zig %d" % (i + 1), x, y, 180, 40, None, A("pop", 400, d + i * 90, loop={"type": "drift", "dur": 2400, "amount": 10}), rotate=rot,
                  bg="linear-gradient(135deg, transparent 33%%, %s 33%% 50%%, transparent 50%%) 0 0/40px 40px, linear-gradient(45deg, transparent 33%%, %s 33%% 50%%,"
                     " transparent 50%%) 20px 0/40px 40px" % (c, c)),
              box("Tri %d" % (i + 1), x + 60, y + 90, 70, 70, None, A("pop", 400, d + 200 + i * 90, loop={"type": "spin", "dur": 9000}), rotate=rot,
                  borderW=6, borderColor=YEL9 if c != YEL9 else MAG)]
    return E


def nineties_extras(T):
    pager = [box("Case", 52, 40, 470, 120, None, A("wipe-right", 380, 0, out=OUT_), bg="linear-gradient(180deg, #3A3A3A, #151515)", radius=18, borderW=3,
                 borderColor="#000", shadow="6px 6px 0 " + MAG),
             box("LCD", 70, 54, 434, 92, None, A("fade", 300, 200), bg="linear-gradient(180deg, #B8C99A, #9DB07E)", radius=6),
             W(T, "Line 1", 84, 56, 410, 46, "{away.abbr} {away.runs}  {home.abbr} {home.runs}", 46, A("letters", 500, 400), color="#1F2A12",
               font=fs("VT323", "monospace"), weight=400),
             W(T, "Line 2", 84, 100, 410, 44, "{arrow}{inning}  B{balls} S{strikes}  {outs} OUT", 40, A("letters", 500, 700), show=LIVE, color="#1F2A12",
               font=fs("VT323", "monospace"), weight=400),
             W(T, "Line 2 status", 84, 100, 410, 44, "{statusText|upper}", 40, A("letters", 500, 700), show="!" + LIVE, color="#1F2A12",
               font=fs("VT323", "monospace"), weight=400)]
    trade = [box("Field", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg=MEMPHIS + ", " + T["title"])]
    trade += [box("Holo", 600, 70, 720, 940, None, A("zoom-out", 600, 100, loop={"type": "shine", "dur": 2600}),
                  bg="linear-gradient(110deg, %s, %s, %s, %s, %s, %s)" % (MAG, YEL9, TEAL, PURP, MAG, YEL9), radius=22, shadow="12px 12px 0 #000"),
              box("Card", 628, 98, 664, 884, None, A("fade", 300, 300), bg=T["team"]("batting"), radius=12),
              img("Photo", 640, 110, 640, 640, "{batter.photo}", A("fade", 400, 500), show="batter.photo", fit="cover", focus="center top"),
              W(T, "Num", 640, 110, 640, 640, "{batter.number}", 300, A("fade", 400, 500), show="!batter.photo", align="center", color="#FFFFFF@0.35", font=H,
                fit=False),
              box("Name bar", 600, 740, 720, 110, YEL9, A("skew-in", 400, 700), skew=-8, borderW=4, borderColor="#000"),
              W(T, "Name", 620, 740, 680, 110, "{batter.name|upper}", 60, A("fade", 300, 850), align="center", color="#000", font=H),
              W(T, "Team", 640, 860, 640, 50, "{batting.nick|upper} · {batter.pos}", 34, A("fade", 300, 950), align="center", font=H),
              W(T, "Stats", 640, 912, 640, 56, "{batter.season.avg|avg} AVG  {batter.season.hr|zero} HR  {batter.season.rbi|zero} RBI", 34,
                A("fade", 300, 1050), align="center", color=YEL9)]
    load = [box("Screen", 460, 330, 1000, 420, "#C0C0C0", A("zoom-out", 400, 0, out=OUT_), borderW=4, borderColor="#000", shadow="10px 10px 0 " + MAG),
            box("Title bar", 466, 336, 988, 50, None, A("fade", 200, 100), bg="linear-gradient(90deg, #000080, #1084D0)"),
            W(T, "Title", 482, 336, 900, 50, "Instant Replay", 30, A("fade", 200, 150), font=COND, weight=700),
            W(T, "Connecting", 500, 420, 920, 80, "CONNECTING TO REPLAY...", 52, A("letters", 600, 300), color="#000", font=fs("VT323", "monospace"), weight=400),
            box("Bar frame", 500, 540, 920, 70, "#FFFFFF", A("fade", 200, 300), borderW=3, borderColor="#808080"),
            box("Bar", 508, 548, 904, 54, None, A("grow-x", 2600, 500, origin="left"),
                bg="repeating-linear-gradient(90deg, #000080 0 34px, transparent 34px 42px)"),
            W(T, "Speed", 500, 640, 920, 60, "56K · PLEASE STAND BY", 40, A("fade", 300, 900, loop={"type": "pulse", "dur": 700, "amount": 0.3}),
              color="#000", font=fs("VT323", "monospace"), weight=400)]
    return {"pager": {"name": "Pager Scorebug", "group": "bug", "autoHide": 0, "side": "", "sided": False, "elements": pager},
            "trading_card": {"name": "Trading Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": trade, "pickable": True},
            "replay_loading": {"name": "Replay Loading (Dial-Up)", "group": "full", "autoHide": 5, "side": "", "sided": False, "elements": load}}


NINETIES = TL.defaults(dict(
    key="nineties", file="nineties", name="'90s Throwback", font=fs("Bungee"), deco=fs("Bungee"),
    desc="Mid-'90s Saturday sports-show energy: Memphis squiggles and dots, teal, purple, magenta and yellow, chunky type with hard "
         "drop shadows. VHS-glitch transitions, a pager-style LCD scorebug, a holographic trading card and a dial-up replay stinger. "
         "Every graphic type, plus basketball, football and hockey.",
    bg="#1A0A2B", panel="linear-gradient(180deg, #2B1145, #1A0A2B)", panel2="linear-gradient(180deg, #3A1A5C, #241038)", dark="#12061F", head=TEAL,
    head_text="#12061F", strip="linear-gradient(180deg, #2ED3D3, %s)" % TEAL, stripText="#12061F", val=YEL9, valText="#000", hi=YEL9, hiText="#000",
    edge="#000000", tile_border="#000000", r=10, shadow="6px 6px 0 " + MAG, glow="5px 5px 0 " + MAG, title="linear-gradient(135deg, %s, #2B1145)" % PURP,
    texture=MEMPHIS, rule=MAG, hr_word="HOME RUN!", hr_band="linear-gradient(135deg, %s, #2B1145)" % PURP, title_color=YEL9, word_color=YEL9,
    open_decor=lambda: squiggles(300), hr_decor=lambda: squiggles(100),
    bug_decor=lambda X, Y, Wd, Hh: [box("Dot", X + Wd - 18, Y - 14, 30, 30, MAG, A("pop", 300, 600), radius="50%", borderW=3, borderColor="#000"),
                                    box("Tri", X - 14, Y + Hh - 10, 28, 28, None, A("pop", 300, 650), rotate=20, borderW=5, borderColor=YEL9)],
    lt_decor=lambda X, Y, Wd, Hh: [box("Zig", X + 120, Y - 20, 220, 18, None, A("wipe-right", 300, 500),
                                       bg="linear-gradient(135deg, transparent 33%%, %s 33%% 50%%, transparent 50%%) 0 0/18px 18px, linear-gradient(45deg, "
                                          "transparent 33%%, %s 33%% 50%%, transparent 50%%) 9px 0/18px 18px" % (MAG, MAG))],
    tr_decor=lambda TA: [box("Tracking", 0, 0, 1920, 1080, None, TA("fade", 200, 0), bg="repeating-linear-gradient(0deg, rgba(0,0,0,.25) 0 2px, transparent 2px 5px)"),
                         box("Glitch 1", 0, 300, 1920, 24, MAG + "@0.6", TA("wipe-right", 160, 0)),
                         box("Glitch 2", 0, 760, 1920, 16, TEAL + "@0.6", TA("wipe-left", 160, 80))],
    extras=nineties_extras))


# ====================================================================== 4. SHAOLIN CIPHER
GOLDK, BLK, CHOP = "#F2B705", "#070707", "#B3121B"
GRIT = ("repeating-radial-gradient(circle at 20% 30%, rgba(255,255,255,.035) 0 1px, transparent 1px 4px), "
        "repeating-linear-gradient(95deg, rgba(255,255,255,.025) 0 2px, transparent 2px 9px)")
BRUSH = fs("Permanent Marker", "cursive")


def chop(name, x, y, s, text, d, rot=-6):
    return [box(name, x, y, s, s, CHOP, A("pop", 300, d), rotate=rot, borderW=3, borderColor="#F7E3C0@0.5", radius=4),
            W(SHAOLIN, name + " text", x, y, s, s, text, int(s * 0.42), A("fade", 200, d + 120), align="center", color="#F7E3C0", font=fs("Black Ops One"),
              weight=400, rotate=rot)]


def shaolin_extras(T):
    title = backdrop(T)
    title += [box("Banner", 120, 0, 150, 1080, None, A("wipe-down", 600, 200), bg="linear-gradient(90deg, #8E0E15, %s, #8E0E15)" % CHOP),
              W(T, "Banner text", 120, 60, 150, 960, "{batting.nick|upper}", 90, A("fade", 500, 700), vertical=True, align="center", color=GOLDK,
                font=fs("Black Ops One"), weight=400),
              W(T, "Starring", 400, 200, 1400, 70, "STARRING", 44, A("fade", 500, 500), align="center", color=T["dim"], tracking=14),
              D_(T, "Name", 400, 290, 1400, 240, "{batter.name|upper}", 170, A("zoom-out", 800, 700), align="center", fit=True),
              box("Brush rule", 700, 560, 800, 18, GOLDK, A("grow-x", 500, 1200), skew=-20, radius=9),
              W(T, "As", 400, 610, 1400, 80, "AS THE SLUGGER OF {batting.city|upper}", 56, A("reveal-up", 500, 1400), align="center", color=GOLDK,
                font=fs("Black Ops One"), weight=400),
              W(T, "Stats", 400, 720, 1400, 70, "{batter.season.avg|avg} · {batter.season.hr|zero} HR · {batter.season.rbi|zero} RBI", 48,
                A("fade", 500, 1700), align="center")]
    title += chop("Chop", 1640, 840, 140, "{batter.number}", 1900)
    vinyl = backdrop(T)
    vinyl += [box("Sleeve", 160, 140, 800, 800, None, A("slide-right", 600, 0, dist=80), bg=T["team"]("batting"), borderW=4, borderColor=GOLDK,
                  shadow=T["shadow"]),
              box("Sleeve grit", 160, 140, 800, 800, None, A("fade", 400, 300), bg=GRIT),
              D_(T, "Sleeve name", 200, 180, 720, 200, "{batter.last|upper}", 130, A("reveal-up", 500, 500), align="left"),
              W(T, "Sleeve team", 200, 380, 720, 60, "{batting.nick|upper}", 44, A("fade", 400, 700), color=GOLDK, font=fs("Black Ops One"), weight=400),
              el("table", "Tracklist", 200, 470, 720, 440, A("none", 1, 0, rows={"type": "slide-right", "dur": 300, "stagger": 70, "delay": 900, "dist": 20}),
                 bind="batter.card", columns=[{"label": "", "field": "{row.label|upper}", "w": 2, "align": "left"}, {"label": "", "field": "value", "w": 1,
                                                                                                                     "align": "right"}],
                 style={"rowH": 72, "size": 38, "weight": 400, "color": "#FFFFFF", "header": False, "padX": 0, "gap": 0, "maxRows": 6, "font": fs("Black Ops One")}),
              box("Record", 900, 180, 720, 720, None, A("slide-left", 800, 300, dist=300, loop={"type": "spin", "dur": 5000}),
                  bg="radial-gradient(circle, transparent 0 15%, rgba(0,0,0,.2) 15.5%), repeating-radial-gradient(circle, #2E2E2E 0 3px, #161616 3px 6px)", radius="50%",
                  borderW=4, borderColor=GOLDK + "@0.5", shadow=T["shadow"]),
              box("Label", 1140, 420, 240, 240, None, A("pop", 400, 900, loop={"type": "spin", "dur": 5000}), bg=T["team"]("batting"), radius="50%",
                  borderW=4, borderColor=GOLDK)]
    vinyl += logo_or_abbr("Label logo", 1180, 460, 160, 160, "batting", 50, A("fade", 300, 1000), S={"font": H})
    vinyl += chop("Chop", 830, 170, 110, "{batter.number}", 1300)
    return {"title_card": {"name": "Kung Fu Title Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": title, "pickable": True},
            "vinyl": {"name": "Vinyl Stat Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": vinyl, "pickable": True}}


SHAOLIN = TL.defaults(dict(
    key="shaolin", file="shaolin-cipher", name="Shaolin Cipher", font=fs("Black Ops One"), deco=BRUSH,
    desc="Kung fu cinema meets gritty New York: black and gold, stencil and brush type, concrete grit, red chop-mark stamps (decorative only). "
         "A martial-arts film title card for player intros, a vinyl-record stat card and brush-stroke wipes. Every graphic type, plus "
         "basketball, football and hockey.",
    bg=BLK, panel="linear-gradient(180deg, #161616, #070707)", panel2="linear-gradient(180deg, #202020, #0E0E0E)", dark="#050505", head=GOLDK,
    head_text=BLK, strip="linear-gradient(180deg, #F7CB3C, #D99A06)", stripText=BLK, val="linear-gradient(180deg, #F7CB3C, #D99A06)", valText=BLK, hi=GOLDK,
    hiText=BLK, edge=GOLDK + "@0.55", r=0, title="radial-gradient(ellipse at 50% 40%, #241D0B, #050505 70%)", texture=GRIT, title_color=GOLDK,
    team=lambda t: "linear-gradient(180deg, color-mix(in srgb, {%s.color} 70%%, #000), #080808)" % t, rule=GOLDK, hr_word="HOME RUN", hr_band=BLK, tr_word=BLK,
    lt_decor=lambda X, Y, Wd, Hh: [box("Brush", X + 96, Y - 14, 600, 16, GOLDK, A("wipe-right", 400, 200), skew=-24, radius=8)] +
    chop("Chop", X + 106 + 560 - 70, Y - 34, 60, "{batter.number}", 700),
    hr_decor=lambda: [box("Brush 1", 100, 330, 1720, 30, GOLDK, A("wipe-right", 300, 100), skew=-30, radius=15),
                      box("Brush 2", 100, 720, 1720, 30, GOLDK, A("wipe-left", 300, 200), skew=-30, radius=15)] + chop("Chop", 1660, 560, 130, "HR", 900),
    open_decor=lambda: [box("Seal", 610, 190, 700, 700, None, A("scale", 900, 100, loop={"type": "spin", "dur": 30000}), radius="50%", borderW=6,
                            borderColor=GOLDK + "@0.35", bg="repeating-conic-gradient(rgba(242,183,5,.08) 0 6deg, transparent 6deg 12deg)")],
    tr_decor=lambda TA: [box("Brush sweep", -100, 380, 2120, 300, GOLDK + "@0.9", TA("wipe-right", 380, 60), skew=-18, radius=150)],
    extras=shaolin_extras))


# ====================================================================== 5. VEGAS SHOWROOM
VRED, VGOLD = "#6E0B14", "#E8C15A"
GOLDG = "linear-gradient(180deg, #FCE7A6, #E8C15A 50%, #B98A2C)"
VELVET = "repeating-linear-gradient(90deg, rgba(0,0,0,.28) 0 18px, rgba(255,255,255,.05) 18px 36px)"
SCRIPT = fs("Pacifico", "cursive")


def vegas_extras(T):
    rec = backdrop(T)
    rec += [box("Spot", 460, 80, 1000, 1000, None, A("fade", 800, 0), bg="radial-gradient(circle, rgba(255,240,200,.25), transparent 65%)"),
            box("Record", 610, 180, 700, 700, None, A("zoom-out", 700, 200, loop={"type": "spin", "dur": 9000}),
                bg="radial-gradient(circle, transparent 0 16%, #9C7322 16.5%), repeating-radial-gradient(circle, #F7DD8A 0 3px, #C9982F 3px 6px)", radius="50%",
                shadow="0 0 60px rgba(255,214,120,.55)"),
            box("Label", 840, 410, 240, 240, None, A("pop", 400, 700), bg=T["team"]("team"), radius="50%", borderW=4, borderColor="#FFF4D6")]
    rec += logo_or_abbr("Label logo", 880, 450, 160, 160, "team", 48, A("fade", 300, 800), S={"font": H})
    rec += [D_(T, "Title", 160, 60, 1600, 130, "{notes.title}", 100, A("reveal-up", 500, 900), align="center", font=SCRIPT, weight=400),
            W(T, "Line", 160, 900, 1600, 80, "{notes.kicker|upper}", 56, A("fade", 500, 1100), align="center", color=VGOLD, font=H)]
    rec += bulbs("Bulbs top", 0, 0, 1920, 24, 300) + bulbs("Bulbs bottom", 0, 1056, 1920, 24, 300)
    end = backdrop(T)
    end += [box("Marquee", 260, 180, 1400, 560, None, A("zoom-out", 600, 0, out=OUT_), bg="linear-gradient(180deg, #2A0408, #120204)", radius=24,
                borderW=8, borderColor=VGOLD, shadow="0 0 60px rgba(255,214,120,.4)")]
    end += bulbs("Bulbs top", 290, 196, 1340, 28, 200) + bulbs("Bulbs bottom", 290, 696, 1340, 28, 200)
    end += [W(T, "Final", 260, 250, 1400, 70, "{statusText|upper}", 48, A("fade", 400, 400), align="center", color=VGOLD, font=H),
            D_(T, "Score", 260, 320, 1400, 200, "{away.abbr} {away.runs}   {home.abbr} {home.runs}", 150, A("letters", 700, 600), align="center"),
            D_(T, "Line", 260, 540, 1400, 130, "Goodnight, {home.city}!", 90, A("reveal-up", 500, 1300), align="center", font=SCRIPT, weight=400),
            W(T, "Gone", 160, 800, 1600, 70, "THE BALLGAME HAS LEFT THE BUILDING", 50, A("fade", 500, 1700), align="center", color=VGOLD, tracking=4, font=H)]
    return {"gold_record": {"name": "Gold Record Milestone", "group": "full", "autoHide": 0, "side": "home", "sided": True, "elements": rec},
            "end_card": {"name": "Show's Over End Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": end}}


def vegas_card(T, kind="bat"):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    E = backdrop(T)
    E += [box("Jukebox", 560, 60, 800, 980, None, A("zoom-out", 600, 0, out=OUT_), bg="linear-gradient(180deg, #F3D27A, #B98A2C)", radius="400px 400px 30px 30px",
              shadow="0 0 60px rgba(255,214,120,.45)"),
          box("Juke inner", 600, 100, 720, 900, None, A("fade", 300, 200), bg="linear-gradient(180deg, #3A050B, #120204)", radius="360px 360px 20px 20px"),
          box("Arch glow", 640, 130, 640, 320, None, A("fade", 400, 300, loop={"type": "shine", "dur": 3000}),
              bg="linear-gradient(90deg, #FF4D6D, #FFD873, #7FE3FF, #FF4D6D)", radius="320px 320px 0 0", opacity=0.9),
          box("Photo disc", 760, 170, 400, 400, None, A("pop", 500, 500), bg=T["team"](team), radius="50%", borderW=6, borderColor=VGOLD),
          img("Photo", 760, 170, 400, 400, "{%s.photo}" % who, A("fade", 400, 650), show="%s.photo" % who, fit="cover", focus="center top", radius=200),
          W(T, "Num", 760, 170, 400, 400, "{%s.number}" % who, 180, A("fade", 400, 650), show="!%s.photo" % who, align="center", font=H),
          D_(T, "Name", 600, 590, 720, 100, "{%s.name}" % who, 70, A("reveal-up", 500, 800), align="center", font=SCRIPT, weight=400),
          el("table", "Rows", 650, 700, 620, 280, A("none", 1, 0, rows={"type": "slide-up", "dur": 300, "stagger": 60, "delay": 1000, "dist": 20}),
             bind="%s.card" % who, columns=[{"label": "", "field": "{row.label|upper}", "w": 2, "align": "left"},
                                             {"label": "", "field": "value", "w": 1, "align": "right"}],
             style={"rowH": 46, "size": 30, "weight": 700, "color": "#FFF4D6", "header": False, "padX": 6, "gap": 0, "maxRows": 6, "font": F})]
    return {"name": "%s Jukebox Card" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


VEGAS = TL.defaults(dict(
    key="vegas", file="vegas-showroom", name="Vegas Showroom", font=fs("Limelight"), deco=fs("Limelight"),
    desc="Classic Vegas showroom: red velvet, gold, marquee bulb borders that chase and twinkle, rhinestone stripes, script and showbill type. "
         "A Tonight Only show open, a jukebox player card, a gold-record milestone graphic and a Show's Over end card. Every graphic type, "
         "plus basketball, football and hockey.",
    bg="#2A0408", panel="linear-gradient(180deg, #7A0E19, #3A050B)", panel2="linear-gradient(180deg, #8A1422, #4A0710)", dark="#1E0306", head=GOLDG,
    head_text="#2A0408", strip=GOLDG, stripText="#2A0408", val="linear-gradient(180deg, #FFF8E6, #F1DDA6)", valText="#2A0408", hi="#FFD873",
    hiText="#2A0408", edge=VGOLD, tile_border=VGOLD, r=8, title="radial-gradient(ellipse at 50% 30%, #8E1420, #2A0408 70%)", texture=VELVET,
    title_color="#FFE9A8", glow="0 0 14px rgba(255,214,120,.7)", rule=VGOLD, open_kicker="TONIGHT ONLY", hr_word="HOME RUN!", hr_band="#3A050B",
    shadow="0 0 26px rgba(255,214,120,.35)",
    bug_decor=lambda X, Y, Wd, Hh: bulbs("Bulbs top", X, Y - 16, Wd, 14, 500) + bulbs("Bulbs bottom", X, Y + 2 * 46 + 4 + 40 + 2, Wd, 14, 520),
    lt_decor=lambda X, Y, Wd, Hh: [box("Rhinestones", X + 110, Y + Hh - 10, 560, 8, None, A("wipe-right", 400, 500, loop={"type": "shine", "dur": 1800}),
                                       bg="repeating-linear-gradient(90deg, #FFFFFF 0 4px, rgba(255,255,255,.2) 4px 8px, #CFE8FF 8px 11px, transparent 11px 16px)")],
    open_decor=lambda: bulbs("Bulbs top", 0, 0, 1920, 30, 200) + bulbs("Bulbs bottom", 0, 1050, 1920, 30, 200) +
    [box("Curtain L", 0, 0, 260, 1080, None, A("slide-right", 800, 0, dist=-260), bg="repeating-linear-gradient(90deg, #5A0812 0 30px, #8E1420 30px 60px)"),
     box("Curtain R", 1660, 0, 260, 1080, None, A("slide-left", 800, 0, dist=-260), bg="repeating-linear-gradient(90deg, #5A0812 0 30px, #8E1420 30px 60px)")],
    hr_decor=lambda: bulbs("Bulbs top", 0, 312, 1920, 22, 200) + bulbs("Bulbs bottom", 0, 746, 1920, 22, 200),
    card=vegas_card, extras=vegas_extras))


# ====================================================================== 6. NOIR DETECTIVE
TYPE = fs("Special Elite", "'Courier New', monospace")
BLINDS = "repeating-linear-gradient(172deg, rgba(0,0,0,.5) 0 34px, rgba(255,255,255,.05) 34px 60px)"
NRED = "#C8102E"


def rain(d=0):
    return [box("Rain", 0, 0, 1920, 1080, None, A("fade", 400, d, loop={"type": "shine", "dur": 900}),
                bg="repeating-linear-gradient(100deg, rgba(255,255,255,.10) 0 1px, transparent 1px 16px)")]


def noir_card(T, kind="bat"):
    who = "pitcher" if kind == "pit" else "batter"
    E = backdrop(T)
    E += [box("Folder tab", 300, 90, 380, 80, "#C9AE72", A("slide-up", 500, 0, dist=40), radius="14px 14px 0 0"),
          W(T, "Tab", 320, 90, 340, 80, "CASE No. {%s.number}" % who, 36, A("fade", 300, 300), color="#2A2112", font=TYPE, weight=400),
          box("Folder", 300, 160, 1320, 840, "#D9C08A", A("slide-up", 500, 0, dist=40), radius=6, shadow=T["shadow"]),
          box("Paper", 820, 200, 760, 760, "#F2EFE6", A("slide-left", 500, 300, dist=40), rotate=1.5, shadow="0 6px 18px rgba(0,0,0,.35)"),
          box("Photo back", 380, 240, 400, 500, "#FFFFFF", A("fade", 300, 400), rotate=-3, shadow="0 6px 18px rgba(0,0,0,.4)"),
          img("Photo", 400, 260, 360, 400, "{%s.photo}" % who, A("fade", 400, 500), show="%s.photo" % who, fit="cover", focus="center top", rotate=-3, grayscale=True),
          box("Clip", 540, 214, 60, 100, None, A("fade", 300, 600), borderW=6, borderColor="#8A8A8A", radius=30),
          W(T, "Photo caption", 390, 670, 380, 60, up(T, "{%s.name}" % who), 34, A("fade", 300, 600), color="#111", font=TYPE, weight=400, rotate=-3,
            align="center"),
          W(T, "Head", 860, 230, 680, 60, "PERSON OF INTEREST", 44, A("letters", 600, 700), color="#111", font=TYPE, weight=400),
          W(T, "Sub", 860, 290, 680, 50, up(T, "{%s.name} · {%s.pos}" % (who, who)), 32, A("letters", 600, 1000), color="#333", font=TYPE, weight=400),
          el("table", "Rows", 860, 360, 680, 480, A("none", 1, 0, rows={"type": "fade", "dur": 200, "stagger": 160, "delay": 1300}),
             bind="%s.card" % who, columns=[{"label": "", "field": "{row.label|upper}", "w": 2, "align": "left"},
                                             {"label": "", "field": "value", "w": 1, "align": "right"}],
             style={"rowH": 64, "size": 36, "weight": 400, "color": "#111", "header": False, "padX": 0, "gap": 0, "maxRows": 6, "font": TYPE}),
          box("Stamp", 1180, 840, 380, 110, None, A("pop", 300, 2300), rotate=-8, borderW=6, borderColor=NRED, radius=8),
          W(T, "Stamp text", 1180, 840, 380, 110, "CONFIDENTIAL", 46, A("pop", 300, 2300), rotate=-8, color=NRED, font=TYPE, weight=400, align="center")]
    E += rain(200)
    return {"name": "%s Case File" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


def noir_extras(T):
    caption = [box("Card", 0, 0, 1920, 1080, "#000000", A("fade", 400, 0, out=OUT_)),
               box("Frame", 240, 200, 1440, 680, None, A("fade", 400, 200), borderW=4, borderColor="#FFFFFF@0.8"),
               box("Frame in", 260, 220, 1400, 640, None, A("fade", 400, 300), borderW=1, borderColor="#FFFFFF@0.5"),
               W(T, "Line 1", 300, 280, 1320, 160, "{notes.title}", 76, A("fade", 700, 600), show="notes.title", align="center", font=TYPE, weight=400, wrap=True),
               W(T, "Line 2", 300, 470, 1320, 260, "{notes.b1}\n{notes.b2}", 52, A("fade", 700, 1300), align="center", font=TYPE, weight=400, wrap=True,
                 fit=False, color="#DDDDDD"),
               W(T, "Foot", 300, 760, 1320, 70, "{notes.foot}", 36, A("fade", 700, 2000), show="notes.foot", align="center", font=TYPE, weight=400,
                 color="#AAAAAA")]
    return {"title_card": {"name": "Silent-Film Title Card", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": caption}}


NOIR = TL.defaults(dict(
    key="noir", file="noir-detective", name="Noir Detective", font=TYPE, font2=TYPE, deco=TYPE, upper=True,
    desc="Film noir: black and white, typewriter type, venetian-blind shadows, rain and a single blood-red accent. A Case File player card "
         "with a paper-clipped mug shot and CONFIDENTIAL stamp, and a silent-film title card for notes. Every graphic type, plus basketball, "
         "football and hockey.",
    bg="#0A0A0A", panel="linear-gradient(180deg, #1E1E1E, #0B0B0B)", panel2="linear-gradient(180deg, #2A2A2A, #141414)", dark="#050505",
    head="linear-gradient(180deg, #F2EFE6, #D9D4C7)", head_text="#111111", strip="linear-gradient(180deg, #F2EFE6, #D9D4C7)", stripText="#111111",
    val="linear-gradient(180deg, #F2EFE6, #D9D4C7)", valText="#111111", hi=NRED, hiText="#FFFFFF", edge="#FFFFFF@0.3", r=0,
    title="radial-gradient(ellipse at 30% 30%, #3A3A3A, #050505 70%)", texture=BLINDS, title_color="#F2EFE6",
    team=lambda t: "linear-gradient(180deg, color-mix(in srgb, {%s.color} 30%%, #2A2A2A), #0D0D0D)" % t, base_on="#F2EFE6", rule="#F2EFE6",
    hr_word="HOME RUN", hr_band="#0A0A0A", open_decor=lambda: rain(300), hr_decor=lambda: rain(0), screen_over=lambda: rain(300),
    tr_decor=lambda TA: [box("Rain", 0, 0, 1920, 1080, None, TA("fade", 300, 0), bg="repeating-linear-gradient(100deg, rgba(255,255,255,.10) 0 1px, "
                                                                                      "transparent 1px 16px)")],
    card=noir_card, extras=noir_extras))


# ====================================================================== 7. ARCADE 8-BIT
PIX = fs("Press Start 2P", "monospace")
VT = fs("VT323", "monospace")
NCY, NMG, NYL, NGR = "#29F3FF", "#FF3EA5", "#FFE600", "#39FF14"
PIXGRID = ("linear-gradient(rgba(41,243,255,.07) 1px, transparent 1px) 0 0/16px 16px, linear-gradient(90deg, rgba(41,243,255,.07) 1px, transparent 1px) "
           "0 0/16px 16px")
SCAN = "repeating-linear-gradient(0deg, rgba(0,0,0,.35) 0 2px, transparent 2px 4px)"


def arcade_card(T, kind="bat"):
    who = "pitcher" if kind == "pit" else "batter"
    team = "fielding" if kind == "pit" else "batting"
    bars = ([("ERA", "{pitcher.season.era|era}", "pct(4.5-pitcher.season.era)"), ("K", "{pitcher.season.k|zero}", "")] if kind == "pit" else
            [("AVG", "{batter.season.avg|avg}", ""), ("HR", "{batter.season.hr|zero}", ""), ("RBI", "{batter.season.rbi|zero}", ""),
             ("OPS", "{batter.season.ops|avg}", "")])
    E = backdrop(T)
    E += [W(T, "Player", 160, 80, 1600, 90, "PLAYER 1" if kind == "bat" else "PLAYER 2", 64, A("fade", 200, 200, loop={"type": "pulse", "dur": 600,
            "amount": 0.2}), align="center", font=PIX, weight=400, color=NYL),
          box("Frame", 200, 220, 640, 700, None, A("wipe-down", 500, 200), bg=T["team"](team), borderW=8, borderColor=NCY),
          img("Photo", 208, 228, 624, 684, "{%s.photo}" % who, A("fade", 300, 500), show="%s.photo" % who, fit="cover", focus="center top"),
          W(T, "Num", 208, 228, 624, 684, "{%s.number}" % who, 260, A("fade", 300, 500), show="!%s.photo" % who, align="center", font=PIX, weight=400,
            color="#FFFFFF@0.35", fit=False),
          box("Scan", 208, 228, 624, 684, None, A("fade", 300, 500), bg=SCAN),
          W(T, "Name", 900, 230, 860, 90, up(T, "{%s.last}" % who), 56, A("letters", 600, 600), font=PIX, weight=400, color="#FFFFFF"),
          W(T, "Team", 900, 330, 860, 60, up(T, "{%s.nick} · {%s.pos}" % (team, who)), 40, A("letters", 600, 900), font=VT, weight=400, color=NCY)]
    for i, (lab, val, _) in enumerate(bars):
        y = 430 + i * 120
        E += [W(T, lab + " label", 900, y, 220, 70, lab, 34, A("fade", 200, 1100 + i * 150), font=PIX, weight=400, color=NMG),
              box(lab + " bar", 1130, y + 14, 420, 42, None, A("grow-x", 600, 1150 + i * 150, origin="left"),
                  bg="repeating-linear-gradient(90deg, %s 0 26px, transparent 26px 32px)" % NGR),
              W(T, lab + " value", 1570, y, 200, 70, val, 34, A("fade", 200, 1300 + i * 150), font=PIX, weight=400, align="right")]
    return {"name": "%s Player Select" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


def arcade_extras(T):
    coin = backdrop(T)
    coin += [W(T, "Inning", 160, 260, 1600, 100, "{statusText|upper}", 60, A("fade", 200, 200), align="center", font=PIX, weight=400, color=NCY),
             W(T, "Insert", 160, 420, 1600, 160, "INSERT COIN", 110, A("fade", 200, 400, loop={"type": "chase", "dur": 1000, "amount": 0}), align="center",
               font=PIX, weight=400, color=NYL, textShadow="0 0 12px rgba(255,230,0,.6)"),
             W(T, "Continue", 160, 600, 1600, 80, "TO CONTINUE", 48, A("fade", 200, 600), align="center", font=PIX, weight=400),
             W(T, "Score", 160, 760, 1600, 80, "{away.abbr} {away.runs}  -  {home.runs} {home.abbr}", 44, A("fade", 200, 800), align="center", font=PIX,
               weight=400, color=NMG)]
    over = backdrop(T)
    over += [W(T, "Game over", 160, 200, 1600, 180, "GAME OVER", 140, A("letters", 900, 200), align="center", font=PIX, weight=400, color=NMG,
               textShadow="0 0 18px rgba(255,62,165,.7)"),
             W(T, "Final", 160, 460, 1600, 120, "{away.abbr} {away.runs}  -  {home.runs} {home.abbr}", 80, A("fade", 200, 1300), align="center", font=PIX,
               weight=400),
             W(T, "High", 160, 650, 1600, 70, "HIGH SCORES", 44, A("fade", 200, 1700), align="center", font=PIX, weight=400, color=NYL),
             W(T, "Lines", 460, 730, 1000, 260, "1ST  {notes.b1|upper}\n2ND  {notes.b2|upper}\n3RD  {notes.b3|upper}", 44, A("letters", 900, 1900), font=VT,
               weight=400, wrap=True, fit=False, lineH=1.3, valign="top", color=NCY)]
    return {"insert_coin": {"name": "Insert Coin (Between Innings)", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": coin},
            "game_over": {"name": "Game Over + High Scores", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": over}}


ARCADE = TL.defaults(dict(
    key="arcade", file="arcade-8-bit", name="Arcade 8-Bit", font=VT, font2=VT, deco=PIX,
    desc="Coin-op arcade: pixel type, neon cyan, magenta, yellow and green on black, scanlines and pixel grids, square out lights. Player "
         "Select cards with segmented stat bars, an INSERT COIN between-innings screen and a GAME OVER final with high scores. Every graphic "
         "type, plus basketball, football and hockey.",
    bg="#000000", panel="linear-gradient(180deg, #050510, #000000)", panel2="linear-gradient(180deg, #0A0A22, #03030C)", dark="#000000", head="#2121DE",
    strip="linear-gradient(180deg, #2B2BEE, #1414A8)", stripText="#FFFFFF", val="#000000", valText=NYL, hi=NYL, hiText="#000000", edge=NCY, r=0,
    title="linear-gradient(180deg, #000000, #05051A)", texture=PIXGRID, title_color=NYL, glow="0 0 10px rgba(41,243,255,.6)", rule=NMG, dot_shape="square",
    base_on=NYL, base_off=NCY + "@0.3", shadow="0 0 0 rgba(0,0,0,0)", hr_word="HOME RUN!", hr_band="#000000", hr_anim="pop",
    hr_loop={"type": "chase", "dur": 500, "amount": 0.35}, open_kicker="PRESS START", tracking=2, num_hi=True,
    screen_over=lambda: [box("Scan", 0, 0, 1920, 1080, None, A("fade", 300, 0), bg=SCAN)],
    lt_decor=lambda X, Y, Wd, Hh: [box("Scan", X, Y, Wd, Hh, None, A("fade", 300, 400), bg=SCAN)],
    hr_decor=lambda: [W(ARCADE, "Bonus", 60, 260, 1800, 70, "+1000", 50, A("slide-up", 600, 800, dist=60), align="right", font=PIX, weight=400, color=NGR)],
    tr_decor=lambda TA: [box("Pixels", 0, 0, 1920, 1080, None, TA("diamond", 500, 0), bg="repeating-conic-gradient(#29F3FF22 0 25%, transparent 0 50%) 0 0/64px 64px")],
    card=arcade_card, extras=arcade_extras))


# ====================================================================== 8. OLD-TIME RADIO
WAL, CREAM, BRASS = "#3B2314", "#F3E6C4", "#C9A44C"
GRILLE = "repeating-linear-gradient(0deg, rgba(0,0,0,.28) 0 3px, transparent 3px 9px)"
DECO = fs("Monoton", "serif")


def radio_extras(T):
    news = [box("Sepia", 0, 0, 1920, 1080, None, A("fade", 300, 0, out=OUT_), bg="radial-gradient(ellipse at center, #CDB48A, #6B5032 80%)"),
            box("Grain", 0, 0, 1920, 1080, None, A("fade", 200, 0, loop={"type": "shine", "dur": 300}),
                bg="repeating-linear-gradient(90deg, rgba(0,0,0,.08) 0 1px, transparent 1px 7px)"),
            box("Ring outer", 560, 140, 800, 800, None, A("scale", 400, 0), radius="50%", borderW=10, borderColor="#2A1C0E"),
            box("Ring inner", 640, 220, 640, 640, None, A("scale", 400, 100), radius="50%", borderW=4, borderColor="#2A1C0E"),
            box("Sweep", 560, 140, 800, 800, None, A("fade", 200, 100, loop={"type": "spin", "dur": 1000}), radius="50%",
                bg="conic-gradient(rgba(0,0,0,.35) 0 90deg, transparent 90deg)"),
            box("Cross h", 400, 538, 1120, 4, "#2A1C0E", A("grow-x", 300, 0)), box("Cross v", 958, 100, 4, 880, "#2A1C0E", A("grow-y", 300, 0)),
            W(T, "Count", 560, 140, 800, 800, "3", 520, A("fade", 100, 200), align="center", color="#2A1C0E", font=fs("Limelight"), weight=400, fit=False),
            box("Title plate", 0, 0, 1920, 1080, "#1C1009", A("fade", 300, 1400)),
            W(T, "Presents", 160, 260, 1600, 80, "{league.name|upper} PRESENTS", 46, A("fade", 400, 1700), align="center", color=BRASS, tracking=10),
            D_(T, "Title", 160, 360, 1600, 260, "{show.name|upper}", 140, A("zoom-out", 900, 1900), align="center", wrap=True),
            W(T, "Game", 160, 700, 1600, 80, "{away.nick|upper} AT {home.nick|upper}", 52, A("fade", 500, 2500), align="center", color=CREAM)]
    paper = [box("Desk", 0, 0, 1920, 1080, "#1C1009", A("fade", 300, 0, out=OUT_)),
             box("Paper", 260, 60, 1400, 980, "#EFE6CF", A("zoom-out", 600, 0, loop=None), rotate=-1.5, shadow="0 20px 50px rgba(0,0,0,.6)"),
             W(T, "Masthead", 300, 90, 1320, 130, "{show.name}", 100, A("fade", 400, 400), color="#1A1A1A", font=fs("Limelight"), weight=400, align="center",
               rotate=-1.5),
             box("Rule", 300, 230, 1320, 6, "#1A1A1A", A("grow-x", 400, 500), rotate=-1.5),
             W(T, "Extra", 300, 240, 1320, 60, "EXTRA! EXTRA! · {seasonYear} · FINAL EDITION", 36, A("fade", 400, 600), color="#1A1A1A", align="center",
               rotate=-1.5),
             W(T, "Headline", 300, 320, 1320, 360, "{notes.title|upper}", 120, A("reveal-up", 600, 800), color="#1A1A1A", font=fs("Alfa Slab One"), weight=400,
               align="center", wrap=True, rotate=-1.5, lineH=0.95, show="notes.title"),
             W(T, "Headline (game)", 300, 320, 1320, 360, "{away.nick|upper} MEET {home.nick|upper} TONIGHT", 110, A("reveal-up", 600, 800),
               color="#1A1A1A", font=fs("Alfa Slab One"), weight=400, align="center", wrap=True, rotate=-1.5, lineH=0.95, show="!notes.title"),
             W(T, "Deck", 300, 700, 1320, 120, "{notes.kicker}", 48, A("fade", 400, 1300), color="#333", align="center", wrap=True, rotate=-1.5,
               font=fs("Special Elite"), weight=400),
             W(T, "Body", 340, 830, 1240, 160, "{notes.b1} · {notes.b2} · {notes.b3}", 32, A("fade", 400, 1600), color="#444", wrap=True, fit=False,
               rotate=-1.5, font=fs("Special Elite"), weight=400, align="center")]
    dial = [box("Cabinet", 610, 120, 700, 860, None, A("zoom-out", 600, 0, out=OUT_), bg="linear-gradient(180deg, #6B4426, %s)" % WAL,
                radius="350px 350px 30px 30px", shadow="0 20px 60px rgba(0,0,0,.6)", borderW=8, borderColor=BRASS + "@0.6"),
            box("Grille", 680, 190, 560, 360, None, A("fade", 400, 300), bg="repeating-linear-gradient(90deg, #2A1708 0 10px, #C9A44C 10px 14px)",
                radius="280px 280px 0 0", borderW=4, borderColor=BRASS),
            box("Dial", 680, 600, 560, 200, CREAM, A("fade", 400, 500), radius=12, borderW=4, borderColor=BRASS),
            box("Ticks", 700, 610, 520, 40, None, A("fade", 300, 600), bg="repeating-linear-gradient(90deg, #3B2314 0 2px, transparent 2px 26px)"),
            W(T, "Score", 680, 650, 560, 140, "{away.abbr} {away.runs} · {home.abbr} {home.runs}", 70, A("fade", 400, 700), align="center", color=WAL,
              font=fs("Limelight"), weight=400),
            box("Needle", 950, 604, 6, 190, "#B3121B", A("slide-right", 1200, 700, dist=-200)),
            box("Knob L", 700, 840, 100, 100, None, A("pop", 300, 900), bg="radial-gradient(circle at 40% 35%, #F3D27A, #8A6A22)", radius="50%"),
            box("Knob R", 1120, 840, 100, 100, None, A("pop", 300, 950), bg="radial-gradient(circle at 40% 35%, #F3D27A, #8A6A22)", radius="50%"),
            W(T, "Status", 810, 850, 300, 80, "{statusText|upper}", 34, A("fade", 400, 1000), align="center", color=CREAM)]
    return {"newsreel": {"name": "Newsreel Open", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": news},
            "extra": {"name": "Extra! Headline", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": paper},
            "dial": {"name": "Radio Dial Score", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": dial}}


RADIO = TL.defaults(dict(
    key="radio", file="old-time-radio", name="Old-Time Radio", font=fs("Limelight"), deco=DECO,
    desc="1930s golden-age radio and newsreels: walnut bakelite, brass, cream dial faces, speaker-grille textures and art-deco type. A "
         "newsreel countdown open, an EXTRA! newspaper headline card and a cathedral-radio dial score. Every graphic type, plus basketball, "
         "football and hockey.",
    bg="#1C1009", panel="linear-gradient(180deg, #5A3820, #2E1B0F)", panel2="linear-gradient(180deg, #6B4426, #3B2314)", dark="#1C1009", head=BRASS,
    head_text="#1C1009", strip="linear-gradient(180deg, #F8EED3, #E3D1A6)", stripText="#2E1B0F", val=CREAM, valText="#2E1B0F", hi=BRASS, hiText="#1C1009",
    edge=BRASS + "@0.6", tile_border=BRASS, r=6, title="radial-gradient(ellipse at 50% 30%, #6B4426, #1C1009 70%)", texture=GRILLE, title_color=CREAM,
    rule=BRASS, hr_word="HOME RUN", hr_band="#2E1B0F",
    bug_under=lambda X, Y, Wd, Hh: [box("Deco top", X + 20, Y - 10, Wd - 40, 4, BRASS, A("grow-x", 400, 200)),
                                    box("Deco top 2", X + 50, Y - 4, Wd - 100, 2, BRASS, A("grow-x", 400, 250))],
    open_decor=lambda: [box("Fan", 460, 560, 1000, 500, None, A("scale", 800, 100), radius="500px 500px 0 0",
                            bg="repeating-conic-gradient(from -90deg at 50% 100%, rgba(201,164,76,.28) 0 4deg, transparent 4deg 12deg)")],
    extras=radio_extras))


# ====================================================================== 9. SPAGHETTI WESTERN
WOOD = "repeating-linear-gradient(90deg, #5A3A22 0 6px, #6B4428 6px 30px, #4E321D 30px 34px, #6B4428 34px 70px)"
PARCH = "linear-gradient(180deg, #F1E2BF, #D8BF8A)"
RYE = fs("Rye", "serif")
DUST = "radial-gradient(circle, rgba(60,30,10,.18) 1px, transparent 1.5px) 0 0/9px 9px"
DESERT = "linear-gradient(180deg, #F2B45A 0%, #D9672C 45%, #6E2A14 75%, #2A120A 100%)"


def tumbleweed(name, y, d, TA=None):
    a = (TA or A)("slide-right", 1400, d, dist=-1600) if TA else A("slide-right", 1400, d, dist=-1600, loop={"type": "spin", "dur": 1200})
    return box(name, 1500, y, 200, 200, None, a, radius="50%",
               bg="repeating-radial-gradient(circle at 45% 55%, transparent 0 8px, rgba(110,70,30,.85) 8px 11px), repeating-conic-gradient(rgba(90,55,25,.7) 0 6deg, "
                  "transparent 6deg 30deg)")


def western_card(T, kind="bat"):
    who = "pitcher" if kind == "pit" else "batter"
    E = [box("Wall", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg=WOOD),
         box("Poster", 560, 50, 800, 980, None, A("zoom-out", 500, 100), bg=PARCH + ", " + DUST, rotate=-1.5, shadow="0 18px 40px rgba(0,0,0,.6)"),
         box("Nail", 945, 66, 30, 30, "#2A1A0E", A("pop", 200, 400), radius="50%"),
         W(T, "Wanted", 560, 90, 800, 170, "WANTED", 150, A("fade", 300, 500), align="center", color="#3A2414", font=RYE, weight=400, rotate=-1.5),
         W(T, "For", 560, 250, 800, 50, "FOR CRIMES AGAINST %s" % ("HITTERS" if kind == "pit" else "PITCHERS"), 34, A("fade", 300, 650), align="center",
           color="#5A3A22", font=RYE, weight=400, rotate=-1.5),
         box("Photo frame", 700, 320, 520, 440, None, A("fade", 300, 700), bg=solid_team("fielding" if kind == "pit" else "batting"), rotate=-1.5,
             borderW=6, borderColor="#3A2414"),
         img("Photo", 706, 326, 508, 428, "{%s.photo}" % who, A("fade", 400, 800), show="%s.photo" % who, fit="cover", focus="center top", rotate=-1.5),
         W(T, "Num", 706, 326, 508, 428, "{%s.number}" % who, 220, A("fade", 400, 800), show="!%s.photo" % who, align="center", color="#FFFFFF@0.4",
           font=RYE, weight=400, rotate=-1.5, fit=False),
         W(T, "Name", 580, 770, 760, 100, "{%s.name|upper}" % who, 70, A("reveal-up", 400, 1000), align="center", color="#3A2414", font=RYE, weight=400,
           rotate=-1.5),
         W(T, "Reward", 580, 870, 760, 60, "REWARD", 40, A("fade", 300, 1200), align="center", color="#8A2E12", font=RYE, weight=400, rotate=-1.5),
         W(T, "Bounty", 580, 930, 760, 70, ("{pitcher.season.k|zero} K · {pitcher.season.era|era} ERA" if kind == "pit" else
                                            "{batter.season.hr|zero} HR · {batter.season.rbi|zero} RBI · {batter.season.avg|avg}"), 44,
           A("fade", 300, 1300), align="center", color="#3A2414", font=RYE, weight=400, rotate=-1.5)]
    return {"name": "%s Wanted Poster" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


def western_extras(T):
    duel = [box("Sky", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg=DESERT),
            box("Sun", 810, 300, 300, 300, None, A("slide-up", 1200, 0, dist=200), bg="radial-gradient(circle, #FFE7A6, #F2B45A 60%, transparent 70%)",
                radius="50%"),
            box("Ground", 0, 820, 1920, 260, None, A("fade", 400, 200), bg="linear-gradient(180deg, #3A1A0C, #1A0A05)"),
            W(T, "Title", 160, 60, 1600, 140, "SHOWDOWN", 130, A("zoom-out", 700, 300), align="center", color="#2A120A", font=RYE, weight=400,
              textShadow="3px 3px 0 #F2B45A"),
            W(T, "Sub", 160, 200, 1600, 60, "AT {venue|upper}", 40, A("fade", 400, 700), align="center", color="#2A120A", font=RYE, weight=400)]
    for i, (who, team) in enumerate((("batter", "batting"), ("pitcher", "fielding"))):
        x = 120 if i == 0 else 1180
        duel += [box("%s frame" % who, x, 300, 620, 520, None, A("slide-%s" % ("right" if i == 0 else "left"), 600, 500, dist=80), bg=solid_team(team),
                     borderW=8, borderColor="#2A120A"),
                 img("%s photo" % who, x + 8, 308, 604, 504, "{%s.photo}" % who, A("fade", 400, 800), show="%s.photo" % who, fit="cover", focus="center top"),
                 W(T, "%s num" % who, x + 8, 308, 604, 504, "{%s.number}" % who, 220, A("fade", 400, 800), show="!%s.photo" % who, align="center",
                   color="#FFFFFF@0.35", font=RYE, weight=400, fit=False),
                 box("%s plate" % who, x, 830, 620, 110, None, A("wipe-up", 400, 1000), bg=PARCH, borderW=4, borderColor="#2A120A"),
                 W(T, "%s name" % who, x, 830, 620, 110, "{%s.name|upper}" % who, 56, A("fade", 300, 1100), align="center", color="#3A2414", font=RYE, weight=400)]
    duel += [W(T, "Vs", 760, 480, 400, 160, "VS", 120, A("pop", 400, 1300), align="center", color=CREAM, font=RYE, weight=400, textShadow="4px 4px 0 #2A120A"),
             tumbleweed("Tumbleweed", 860, 1600)]
    return {"showdown": {"name": "High Noon Showdown", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": duel}}


WESTERN = TL.defaults(dict(
    key="western", file="spaghetti-western", name="Spaghetti Western", font=RYE, deco=RYE,
    desc="Frontier town: weathered saloon wood, parchment, rust and desert-sunset gradients, slab-serif poster type. WANTED poster player "
         "cards, a High Noon Showdown batter-versus-pitcher card and rolling-tumbleweed transitions. Every graphic type, plus basketball, "
         "football and hockey.",
    bg="#2A120A", panel=WOOD, panel2="linear-gradient(180deg, #6B4428, #4E321D)", dark="#2A1A0E", head=PARCH, head_text="#3A2414", strip=PARCH,
    stripText="#3A2414", val=PARCH, valText="#3A2414", hi="#E8A13A", hiText="#2A120A", edge="#2A1A0E", tile_border="#2A1A0E", r=2, title=DESERT,
    texture=DUST, title_color="#FFF1D6", glow="3px 3px 0 #2A120A", rule="#E8A13A", team=solid_team, hr_word="HOME RUN!", hr_band=WOOD,
    open_decor=lambda: [tumbleweed("Tumbleweed", 860, 800)], hr_decor=lambda: [tumbleweed("Tumbleweed", 780, 400)],
    tr_decor=lambda TA: [box("Tumbleweed", 1500, 820, 200, 200, None, TA("slide-right", 900, 0, dist=-1600), radius="50%",
                             bg="repeating-radial-gradient(circle at 45% 55%, transparent 0 8px, rgba(110,70,30,.85) 8px 11px)")],
    lt_decor=lambda X, Y, Wd, Hh: [box("Nail L", X + 120, Y + 6, 10, 10, "#2A1A0E", A("pop", 200, 500), radius="50%"),
                                   box("Nail R", X + 106 + 560 - 16, Y + 6, 10, 10, "#2A1A0E", A("pop", 200, 520), radius="50%")],
    card=western_card, extras=western_extras))


# ====================================================================== 10. HALLOWEEN
ORG, SPK_P, SLIME = "#FF7518", "#3B1260", "#7CFC00"
CREEP = fs("Creepster", "cursive")
MOON = ("radial-gradient(circle at 78% 22%, #FFF4C2 0 90px, #F4D27A 92px, rgba(244,210,122,.25) 110px, transparent 170px), "
        "radial-gradient(ellipse at 50% 70%, #3B1260, #0A0310 75%)")
WEB = ("repeating-radial-gradient(circle at 0 0, transparent 0 70px, rgba(255,255,255,.08) 70px 72px), "
       "repeating-conic-gradient(from 0deg at 0 0, rgba(255,255,255,.07) 0 1deg, transparent 1deg 15deg)")


def pumpkin(name, x, y, s, d):
    e = s // 5
    return [box(name, x, y, s, int(s * 0.85), None, A("pop", 400, d, loop={"type": "breathe", "dur": 1400, "amount": 0.04}),
                bg="radial-gradient(ellipse at 50%% 40%%, #FFA44A, %s 60%%, #B34A00)" % ORG, radius="50%"),
            box(name + " stem", x + s // 2 - e // 4, y - e // 2, e // 2, e, "#3E6B1F", A("pop", 300, d + 100), radius=4),
            box(name + " eye L", x + s // 4, y + s // 4, e, e, "#2A0A00", A("fade", 200, d + 200, loop={"type": "pulse", "dur": 700, "amount": 0.6}), rotate=45),
            box(name + " eye R", x + s - s // 4 - e, y + s // 4, e, e, "#2A0A00", A("fade", 200, d + 200, loop={"type": "pulse", "dur": 700, "amount": 0.6}),
                rotate=45),
            box(name + " mouth", x + s // 4, y + s // 2, s // 2, e, "#2A0A00", A("fade", 200, d + 250), radius="0 0 %dpx %dpx" % (e, e))]


def spooky_card(T, kind="bat"):
    who = "pitcher" if kind == "pit" else "batter"
    E = [box("Night", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg=MOON),
         box("Ground", 0, 900, 1920, 180, None, A("fade", 400, 100), bg="linear-gradient(180deg, #1A0A26, #050108)"),
         box("Stone", 610, 140, 700, 860, None, A("slide-up", 700, 200, dist=200), bg="linear-gradient(180deg, #8A8F99, #5A5F69)",
             radius="350px 350px 10px 10px", shadow="0 20px 50px rgba(0,0,0,.7)", borderW=6, borderColor="#3A3F49"),
         box("Moss", 610, 900, 700, 100, None, A("fade", 400, 600), bg="linear-gradient(180deg, transparent, rgba(60,120,30,.6))"),
         W(T, "Here", 640, 220, 640, 80, "HERE STANDS", 50, A("fade", 400, 700), align="center", color="#2A2E36", font=CREEP, weight=400),
         W(T, "Name", 640, 300, 640, 140, "{%s.name|upper}" % who, 90, A("reveal-up", 500, 900), align="center", color="#1A1D24", font=CREEP, weight=400),
         el("table", "Rows", 680, 470, 560, 400, A("none", 1, 0, rows={"type": "fade", "dur": 300, "stagger": 120, "delay": 1200}),
            bind="%s.card" % who, columns=[{"label": "", "field": "{row.label|upper}", "w": 2, "align": "left"}, {"label": "", "field": "value", "w": 1,
                                                                                                                 "align": "right"}],
            style={"rowH": 64, "size": 34, "weight": 800, "color": "#1A1D24", "header": False, "padX": 0, "gap": 0, "maxRows": 6, "font": COND})]
    E += pumpkin("Pumpkin", 1340, 840, 200, 1500)
    E += [box("Fog", 0, 840, 1920, 240, None, A("fade", 800, 600, loop={"type": "drift", "dur": 6000, "amount": 60}),
              bg="radial-gradient(ellipse at 30% 60%, rgba(220,220,255,.25), transparent 60%), radial-gradient(ellipse at 75% 50%, rgba(220,220,255,.2), "
                 "transparent 60%)")]
    return {"name": "%s Tombstone" % ("Pitcher" if kind == "pit" else "Batter"), "group": "full", "autoHide": 0, "side": "", "sided": False,
            "elements": E, "pickable": True}


SPOOKY = TL.defaults(dict(
    key="spooky", file="halloween", name="Halloween", font=CREEP, deco=CREEP,
    desc="Halloween and October theme nights: midnight purple, pumpkin orange, slime-green glow, moonlit skies, cobwebs, fog and dripping "
         "type. Tombstone player cards, glowing jack-o'-lanterns and a spooky home-run stinger. Every graphic type, plus basketball, football "
         "and hockey.",
    bg="#0A0310", panel="linear-gradient(180deg, #2A0D45, #120520)", panel2="linear-gradient(180deg, #3B1260, #1C0830)", dark="#0A0310", head=ORG,
    head_text="#120520", strip="linear-gradient(180deg, #FF9A4A, %s)" % ORG, stripText="#120520", val="#FFE7C2", valText="#120520", hi=SLIME,
    hiText="#120520", edge=ORG + "@0.6", r=8, title=MOON, texture=WEB, title_color=ORG, glow="0 0 16px rgba(124,252,0,.55)", rule=ORG, base_on=ORG,
    hr_word="HOME RUN!", hr_band="linear-gradient(180deg, #2A0D45, #0A0310)",
    open_decor=lambda: pumpkin("Pumpkin L", 120, 820, 200, 900) + pumpkin("Pumpkin R", 1600, 840, 180, 1000),
    hr_decor=lambda: pumpkin("Pumpkin", 1660, 560, 160, 600),
    bug_decor=lambda X, Y, Wd, Hh: [box("Web", X + Wd - 70, Y - 4, 74, 74, None, A("fade", 300, 600), bg=WEB.replace("at 0 0", "at 100% 0"))],
    lt_decor=lambda X, Y, Wd, Hh: [box("Drip", X + 110, Y + Hh - 2, 560, 22, None, A("wipe-down", 600, 500),
                                       bg="radial-gradient(circle at 50%% 0, %s 0 9px, transparent 10px) 0 0/46px 22px, radial-gradient(circle at 50%% 0, %s 0 5px, "
                                          "transparent 6px) 23px 0/46px 14px" % (SLIME, SLIME))],
    card=spooky_card))


# ====================================================================== 11. HOLIDAY
HRED, HGRN, HGOLD = "#B3121B", "#0F5132", "#E8C15A"
CANE = "repeating-linear-gradient(45deg, %s 0 12px, #FFFFFF 12px 24px)" % HRED
SNOW = ("radial-gradient(circle, rgba(255,255,255,.85) 1.6px, transparent 2.2px) 0 0/60px 60px, radial-gradient(circle, rgba(255,255,255,.55) 1.1px, "
        "transparent 1.6px) 30px 20px/44px 44px")
MOC = fs("Mountains of Christmas", "serif")


def snowfall(d=0):
    return [box("Snow", 0, 0, 1920, 1080, None, A("fade", 600, d, loop={"type": "scroll-y", "dur": 6000, "amount": 60}), bg=SNOW),
            box("Snow 2", 0, 0, 1920, 1080, None, A("fade", 600, d, loop={"type": "scroll-y", "dur": 4000, "amount": 44}),
                bg="radial-gradient(circle, rgba(255,255,255,.7) 2.4px, transparent 3px) 10px 10px/88px 88px")]


def ornament(name, x, y, s, col, d):
    return [box(name + " string", x + s // 2 - 1, -10, 2, y + 10, HGOLD, A("grow-y", 400, d)),
            box(name + " cap", x + s // 2 - s // 8, y - s // 8, s // 4, s // 6, HGOLD, A("slide-down", 500, d, dist=60), radius=3),
            box(name, x, y, s, s, None, A("slide-down", 500, d, dist=60, loop={"type": "drift", "dur": 2400, "amount": 6}),
                bg="radial-gradient(circle at 35%% 30%%, #FFFFFF 0 6%%, %s 40%%, color-mix(in srgb, %s 60%%, #000))" % (col, col), radius="50%")]


def holiday_extras(T):
    greet = backdrop(T) + ornament("Ornament 1", 260, 160, 140, HRED, 200) + ornament("Ornament 2", 520, 90, 100, HGOLD, 300) + \
        ornament("Ornament 3", 1300, 120, 120, "#1E63D6", 250) + ornament("Ornament 4", 1560, 200, 150, HRED, 350)
    greet += [D_(T, "Greetings", 160, 400, 1600, 200, "Season's Greetings", 150, A("zoom-out", 700, 600), align="center"),
              W(T, "From", 160, 610, 1600, 70, "FROM ALL OF US AT", 40, A("fade", 400, 1000), align="center", color=HGOLD, tracking=6),
              W(T, "Team", 160, 680, 1600, 120, "{home.city|upper} {home.nick|upper}", 90, A("reveal-up", 500, 1200), align="center"),
              box("Cane", 560, 820, 800, 22, None, A("grow-x", 500, 1400), bg=CANE, radius=11)]
    greet += snowfall(300)
    return {"greetings": {"name": "Season's Greetings", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": greet},
            "snowfall": {"name": "Snowfall Overlay", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": snowfall(0)}}


HOLIDAY = TL.defaults(dict(
    key="holiday", file="holiday", name="Holiday", deco=MOC, deco_digits=False,
    desc="Holiday and winter-ball cheer: evergreen and cranberry, gold, candy-cane stripes, hanging ornaments, gift-tag lower thirds and "
         "falling snow. A Season's Greetings card and a transparent Snowfall overlay you can lay over any shot. Every graphic type, plus "
         "basketball, football and hockey.",
    bg="#062216", panel="linear-gradient(180deg, #14603E, #0A3824)", panel2="linear-gradient(180deg, #1B6B46, #0F4A30)", dark="#05180F", head=HRED,
    strip="linear-gradient(180deg, #FFFFFF, #EEF0F2)", stripText="#7A0C12", val="#FFFFFF", valText=HRED, hi=HGOLD, hiText="#062216",
    edge=HGOLD + "@0.6", tile_border=HGOLD, r=10, title="radial-gradient(ellipse at 50% 30%, #1B6B46, #062216 75%)", texture=SNOW, title_color="#FFFFFF",
    glow="0 0 12px rgba(232,193,90,.6)", rule=HRED, hr_word="HOME RUN!", hr_band="linear-gradient(180deg, #8E0E15, #5A080D)",
    bug_under=lambda X, Y, Wd, Hh: [box("Cane", X + 6, Y - 10, Wd - 12, 12, None, A("wipe-right", 400, 100), bg=CANE, radius=6)],
    lt_decor=lambda X, Y, Wd, Hh: [box("Ribbon", X + 40, Y - 6, 26, Hh + 12, None, A("grow-y", 400, 300), bg="linear-gradient(90deg, #8E0E15, %s, #8E0E15)" % HRED),
                                   box("Bow L", X + 18, Y - 26, 34, 26, HRED, A("pop", 300, 600), radius="50%", rotate=-20),
                                   box("Bow R", X + 54, Y - 26, 34, 26, HRED, A("pop", 300, 620), radius="50%", rotate=20),
                                   box("Tag hole", X + 106 + 540, Y + Hh // 2 - 8, 16, 16, None, A("fade", 200, 500), radius="50%", borderW=3,
                                       borderColor=HGOLD)],
    open_decor=lambda: ornament("Ornament 1", 200, 120, 120, HRED, 200) + ornament("Ornament 2", 1600, 160, 130, HGOLD, 300) + snowfall(100),
    hr_decor=lambda: snowfall(0), screen_over=lambda: snowfall(200),
    extras=holiday_extras))


# ====================================================================== 12. SYNTHWAVE
PINK, CY2, DEEP = "#FF2E93", "#21E6FF", "#12002B"
AUDIO = fs("Audiowide")
GRID = ("linear-gradient(rgba(255,46,147,.55) 2px, transparent 2px) 0 0/100% 48px, linear-gradient(90deg, rgba(255,46,147,.55) 2px, transparent 2px) "
        "0 0/96px 100%")
NEON = "0 0 8px %s, 0 0 22px rgba(255,46,147,.6)" % PINK


def sunset(d=0):
    E = [box("Sky", 0, 0, 1920, 1080, None, A("fade", 400, d, out=OUT_), bg="linear-gradient(180deg, #12002B 0%, #3B0A5F 40%, #8C1A6E 60%, #12002B 60.2%)"),
         box("Sun", 660, 200, 600, 600, None, A("slide-up", 1200, d + 100, dist=200), bg="linear-gradient(180deg, #FFE66D 0%%, #FF9A3C 45%%, %s 100%%)" % PINK,
             radius="50%", shadow="0 0 80px rgba(255,46,147,.6)")]
    for i in range(6):
        E.append(box("Sun cut %d" % (i + 1), 640, 480 + i * 34, 640, 6 + i * 3, "#3B0A5F", A("fade", 300, d + 400)))
    E += [box("Horizon", 0, 646, 1920, 434, DEEP, A("fade", 300, d)),
          box("Floor", -480, 650, 2880, 430, None, A("fade", 500, d + 200, loop={"type": "scroll-y", "dur": 900, "amount": 48}), bg=GRID),
          box("Horizon glow", 0, 640, 1920, 14, PINK, A("grow-x", 600, d + 300), shadow="0 0 30px " + PINK)]
    return E


def synth_extras(T):
    sign = sunset(0) + [box("Sign", 360, 160, 1200, 420, None, A("zoom-out", 500, 400), bg="rgba(18,0,43,.75)", radius=24, borderW=4,
                            borderColor=CY2, shadow="0 0 24px " + CY2),
                        W(T, "Away", 400, 200, 520, 120, "{away.abbr}", 90, A("fade", 300, 700, loop={"type": "pulse", "dur": 2600, "amount": 0.85}),
                          align="center", font=AUDIO, color="#FFFFFF", textShadow=NEON),
                        W(T, "Home", 1000, 200, 520, 120, "{home.abbr}", 90, A("fade", 300, 800, loop={"type": "pulse", "dur": 2400, "amount": 0.85}),
                          align="center", font=AUDIO, color="#FFFFFF", textShadow=NEON),
                        W(T, "Away runs", 400, 310, 520, 200, "{away.runs}", 200, A("pop", 400, 900), align="center", font=AUDIO, color=CY2,
                          textShadow="0 0 10px %s, 0 0 30px rgba(33,230,255,.6)" % CY2),
                        W(T, "Home runs", 1000, 310, 520, 200, "{home.runs}", 200, A("pop", 400, 1000), align="center", font=AUDIO, color=CY2,
                          textShadow="0 0 10px %s, 0 0 30px rgba(33,230,255,.6)" % CY2),
                        W(T, "Status", 360, 520, 1200, 56, "{statusText|upper}", 36, A("fade", 300, 1200), align="center", font=AUDIO, color=PINK,
                          textShadow=NEON)]
    return {"neon_score": {"name": "Neon Score Sign", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": sign}}


SYNTH = TL.defaults(dict(
    key="synth", file="synthwave", name="Synthwave", font=AUDIO, deco=AUDIO,
    desc="Retro-future neon: hot pink and cyan glow, sunset sun with scan cuts, a scrolling laser grid floor, deep purple panels. A sunset "
         "show open, a neon score sign and glowing lower thirds. Every graphic type, plus basketball, football and hockey.",
    bg=DEEP, panel="linear-gradient(180deg, rgba(43,10,79,.95), rgba(18,0,43,.96))", panel2="linear-gradient(180deg, rgba(60,16,100,.95), rgba(28,4,60,.96))",
    dark="#0A0018", head="linear-gradient(90deg, %s, #8C2BFF)" % PINK, strip="linear-gradient(90deg, %s, #8C2BFF)" % PINK, stripText="#FFFFFF", val=DEEP,
    valText=CY2, hi=CY2, hiText=DEEP, edge=CY2, r=4, title="linear-gradient(180deg, #12002B 0%, #3B0A5F 55%, #8C1A6E 100%)", texture=GRID.replace(".55", ".18"),
    title_color="#FFE3F3", glow=NEON, rule=PINK, base_on=PINK, base_off=CY2 + "@0.3", shadow="0 0 22px rgba(33,230,255,.35)", hr_word="HOME RUN",
    hr_band="rgba(18,0,43,.9)", open_decor=lambda: sunset(0)[1:], hr_under=lambda: sunset(0),
    lt_decor=lambda X, Y, Wd, Hh: [box("Neon line", X, Y + Hh + 2, Wd, 3, CY2, A("grow-x", 500, 500), shadow="0 0 12px " + CY2)],
    bug_decor=lambda X, Y, Wd, Hh: [box("Neon line", X, Y - 6, Wd, 3, PINK, A("grow-x", 500, 300), shadow="0 0 12px " + PINK)],
    tr_decor=lambda TA: [box("Grid", -480, 660, 2880, 420, None, TA("fade", 300, 0), bg=GRID)],
    extras=synth_extras))


# ====================================================================== 13. COMIC BOOK
CYEL, CRED, CBLU = "#FFD400", "#E62429", "#1E63D6"
BANG = fs("Bangers", "Impact, sans-serif")
DOTS = "radial-gradient(circle, rgba(0,0,0,.18) 2px, transparent 2.6px) 0 0/12px 12px"
INKS = "6px 6px 0 #000"


def comic_extras(T):
    k = [box("Panel", 0, 0, 1920, 1080, None, A("fade", 200, 0, out=OUT_), bg="radial-gradient(circle, rgba(230,36,41,.3) 3px, transparent 3.6px) 0 0/16px 16px, "
                                                                                 "radial-gradient(ellipse at 50% 50%, #FFE45C, #FFB800)")]
    k += [box("Rays", 0, 0, 1920, 1080, None, A("fade", 300, 100, loop={"type": "spin", "dur": 20000}),
              bg="repeating-conic-gradient(from 0deg at 50% 50%, rgba(255,255,255,.35) 0 6deg, transparent 6deg 18deg)")]
    k += star_burst("Burst", 960, 480, 380, CRED, 200)
    k += [W(T, "Word", 360, 300, 1200, 300, "STRUCK OUT!", 200, A("pop", 360, 600), align="center", font=BANG, weight=400, color=CYEL, rotate=-6,
            textStroke="6px #000", textShadow=INKS),
          box("Caption", 560, 820, 800, 110, "#FFFFFF", A("wipe-right", 300, 900), borderW=5, borderColor="#000", rotate=-2),
          W(T, "Caption text", 580, 820, 760, 110, "{pitcher.name|upper} STRIKES AGAIN!", 50, A("fade", 200, 1000), align="center", color="#000", font=BANG,
            weight=400, rotate=-2)]
    cover = [box("Cover", 0, 0, 1920, 1080, None, A("fade", 300, 0, out=OUT_), bg=DOTS + ", linear-gradient(160deg, %s, #0E3A8A)" % CBLU),
             box("Masthead", 0, 0, 1920, 220, CRED, A("wipe-down", 400, 100), borderW=0),
             W(T, "Title", 60, 10, 1500, 200, "{show.name|upper}", 170, A("zoom-out", 500, 300), font=BANG, weight=400, color=CYEL, textStroke="5px #000",
               textShadow=INKS),
             box("Issue", 1600, 30, 260, 160, "#FFFFFF", A("pop", 300, 500), borderW=5, borderColor="#000"),
             W(T, "Issue text", 1600, 30, 260, 160, "NO. {seasonYear}", 46, A("fade", 200, 600), align="center", color="#000", font=BANG, weight=400, wrap=True)]
    for i, side in enumerate(("away", "home")):
        x = 120 if i == 0 else 1000
        cover += [box("%s panel" % side, x, 300, 800, 600, None, A("zoom-out", 400, 600 + i * 150), bg=solid_team(side), borderW=8, borderColor="#000",
                      rotate=-2 if i == 0 else 2, shadow="10px 10px 0 #000")]
        cover += logo_or_abbr("%s logo" % side, x + 200, 380, 400, 340, side, 140, A("pop", 400, 800 + i * 150), S={"font": BANG})
        cover += [W(T, "%s nick" % side, x, 740, 800, 120, "{%s.nick|upper}" % side, 90, A("reveal-up", 300, 1000 + i * 150), align="center", font=BANG,
                    weight=400, color="#FFFFFF", textStroke="4px #000", rotate=-2 if i == 0 else 2)]
    cover += star_burst("Vs burst", 960, 600, 120, CYEL, 1300)
    cover += [W(T, "Vs", 860, 540, 200, 120, "VS!", 80, A("pop", 300, 1400), align="center", font=BANG, weight=400, color=CRED, textStroke="3px #000")]
    return {"strikeout": {"name": "Strikeout Burst", "group": "full", "autoHide": 5, "side": "", "sided": False, "elements": k},
            "cover": {"name": "Comic Cover Matchup", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": cover}}


COMIC = TL.defaults(dict(
    key="comic", file="comic-book", name="Comic Book", font=BANG, deco=BANG,
    desc="Comic-book pages: primary yellow, red and blue, halftone dots, thick black ink outlines and hard shadows, action bursts. KA-POW "
         "home-run stinger, a STRUCK OUT! burst, speech-bubble lower thirds and a comic-cover matchup. Every graphic type, plus basketball, "
         "football and hockey.",
    bg="#0E3A8A", panel="linear-gradient(180deg, #2A74E8, #174FB0)", panel2="linear-gradient(180deg, #3C82F0, #1E5BC4)", dark="#0B1F4A", head=CRED,
    strip=CYEL, stripText="#000000", val="#FFFFFF", valText="#000000", hi=CYEL, hiText="#000000", edge="#000000", tile_border="#000000", r=0,
    shadow=INKS, title=DOTS + ", linear-gradient(160deg, %s, #0E3A8A)" % CBLU, texture=DOTS, title_color=CYEL, glow=INKS, rule="#000000",
    hr_word="KA-POW!", hr_band=CRED, hr_anim="pop", word_color=CRED, word_stroke="5px #000", hr_name_color="#000000",
    hr_decor=lambda: star_burst("Burst", 960, 500, 330, CYEL, 100),
    lt_decor=lambda X, Y, Wd, Hh: [box("Tail", X + 180, Y + Hh - 16, 40, 40, CYEL, A("pop", 300, 400), rotate=45, borderW=0),
                                   box("Caption", X + 110, Y - 40, 380, 36, "#FFFFFF", A("wipe-right", 300, 600), borderW=3, borderColor="#000"),
                                   W(COMIC_T, "Caption text", X + 120, Y - 40, 360, 36, "MEANWHILE, AT THE PLATE...", 24, A("fade", 200, 700), color="#000",
                                     font=BANG, weight=400)],
    open_decor=lambda: star_burst("Burst", 960, 420, 420, CRED, 200),
    tr_decor=lambda TA: [box("Burst %d" % i, 560, 140, 800, 800, CYEL, TA("pop", 300, i * 40), rotate=i * 22.5, borderW=8, borderColor="#000")
                         for i in range(4)],
    extras=comic_extras))
COMIC_T = COMIC


# ====================================================================== 14. BALLPARK SCOREBOARD (hand-operated)
BGRN, TIN = "#1F4D2B", "#141414"
SLAB = fs("Alfa Slab One")
SEAMS = "repeating-linear-gradient(90deg, rgba(0,0,0,.18) 0 3px, transparent 3px 160px), repeating-linear-gradient(0deg, rgba(0,0,0,.12) 0 2px, transparent 2px 120px)"


def board_extras(T):
    E = [box("Board", 60, 60, 1800, 960, None, A("zoom-out", 500, 0, out=OUT_), bg="linear-gradient(180deg, #245A33, #173D22)", borderW=14,
             borderColor="#0E2414", shadow="0 20px 60px rgba(0,0,0,.6)"),
         box("Seams", 74, 74, 1772, 932, None, A("fade", 300, 200), bg=SEAMS),
         box("Header", 460, 90, 1000, 110, "#F4F1E8", A("wipe-down", 400, 200), borderW=4, borderColor="#0E2414"),
         W(T, "Header text", 460, 90, 1000, 110, "{venue|upper}", 60, A("fade", 300, 400), align="center", color=BGRN, font=SLAB, weight=400),
         el("linescore", "Linescore", 120, 240, 1680, 300, A("wipe-right", 600, 500),
            style={"size": 54, "color": "#FFFFFF", "headColor": "#F4F1E8", "headSize": 30, "rowFill": TIN, "totalFill": "#0A0A0A", "current": "#F7D23E@0.35",
                   "minInnings": 9, "teamW": 260, "font": SLAB})]
    for i, (lab, bind, tot) in enumerate((("BALL", "balls", 3), ("STRIKE", "strikes", 2), ("OUT", "outs", 2))):
        x = 160 + i * 420
        E += [W(T, lab, x, 600, 380, 70, lab, 44, A("fade", 300, 800 + i * 100), align="center", color="#F4F1E8", font=SLAB, weight=400),
              box(lab + " housing", x + 40, 680, 300, 90, TIN, A("fade", 300, 800 + i * 100), radius=8),
              el("dots", lab + " lights", x + 40, 680, 300, 90, A("fade", 300, 900 + i * 100), bind=bind,
                 style={"total": tot, "size": 56, "gap": 24, "on": "#F7D23E", "off": "#3A3A2A", "shape": "circle", "align": "center"})]
    E += [W(T, "At bat label", 1420, 600, 300, 70, "AT BAT", 44, A("fade", 300, 1100), align="center", color="#F4F1E8", font=SLAB, weight=400),
          box("At bat tin", 1460, 680, 220, 160, TIN, A("fade", 300, 1100), radius=6),
          W(T, "At bat", 1460, 680, 220, 160, "{batter.number}", 110, A("letters", 400, 1200), align="center", font=SLAB, weight=400),
          box("Clock", 860, 860, 200, 140, "#F4F1E8", A("pop", 400, 1300), radius="50%", borderW=8, borderColor="#0E2414")]
    E += net_mark(T, "Clock mark", 890, 880, 140, 100, A("fade", 300, 1400))
    return {"full_board": {"name": "Full Manual Scoreboard", "group": "full", "autoHide": 0, "side": "", "sided": False, "elements": E}}


BOARD = TL.defaults(dict(
    key="board", file="ballpark-scoreboard", name="Ballpark Scoreboard", font=SLAB, deco=SLAB, bug_variant="bar",
    desc="Old hand-operated ballpark scoreboard: painted green boards with seams, black number tins, cream header boards, yellow ball / strike "
         "/ out bulbs and slab numerals. A long scoreboard-strip scorebug and a full manual scoreboard with linescore, B-S-O lights and the "
         "AT BAT tin. Every graphic type, plus basketball, football and hockey.",
    bg="#163A20", panel="linear-gradient(180deg, #245A33, #173D22)", panel2="linear-gradient(180deg, #2B6A3C, #1C4A29)", dark=TIN, head="#F4F1E8",
    head_text=BGRN, strip="linear-gradient(180deg, #F4F1E8, #E2DCCB)", stripText=BGRN, val=TIN, valText="#FFFFFF", hi="#F7D23E", hiText=TIN,
    edge="#0E2414", tile_border="#0E2414", r=2, title="linear-gradient(180deg, #245A33, #163A20)", texture=SEAMS, title_color="#F4F1E8", rule="#F4F1E8",
    team=solid_team, base_on="#F7D23E", base_off="#3A3A2A", hr_word="HOME RUN", hr_band="linear-gradient(180deg, #245A33, #173D22)",
    extras=board_extras))

THEMES = [USA, HYPER, NINETIES, SHAOLIN, VEGAS, NOIR, ARCADE, RADIO, WESTERN, SPOOKY, HOLIDAY, SYNTH, COMIC, BOARD]

if __name__ == "__main__":
    want = set(sys.argv[1:])
    for T in THEMES:
        if not want or T["key"] in want or T["file"] in want:
            TL.build(T)
