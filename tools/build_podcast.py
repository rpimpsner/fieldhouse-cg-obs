"""Builds the "Podcast" package: templates/packages/podcast.json.

Graphics a sports podcast needs, fed by the Podcast tab of the control panel (ui.podcast): show open and corner bug,
episode title, name bars for up to four hosts and a guest, an "on mic" tag, guest intro and panel cards, a topic bar,
the rundown, segment bumpers, coming up, quote, head to head, poll, mailbag / live chat question, top-5 countdown,
picks, hot take, follow us, sponsor read, QR code, starting soon / be right back / thanks for watching screens, and
frames for two, three or four remote guests (see-through windows: put the video calls under them in OBS).
Every broadcast graphic type is included too, redrawn in the same dark studio look (scores, standings, stat cards and
so on are useful on a sports podcast), plus basketball, football and hockey.
Run:  python tools/build_podcast.py   (after tools/build_night_game.py)
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
from broadcast_lib import A, box, txt, img, el, both  # noqa: E402

BG = "#0D1015"
BG_GRAD = "radial-gradient(ellipse at 75% 20%, #232A36 0%, #12161C 55%, #07090C 100%)"
PANEL = "linear-gradient(180deg, #1C222B 0%, #12161C 100%)"
PANEL2 = "linear-gradient(180deg, #252C37 0%, #1A1F27 100%)"
LIGHT = "linear-gradient(180deg, #FFFFFF 0%, #E9ECF1 100%)"
ACC = "$accent"
ACC_GRAD = "linear-gradient(90deg, color-mix(in srgb, $accent 100%, #000) 0%, color-mix(in srgb, $accent 78%, #000) 100%)"
INK = "#0D1015"
DIM = "#A9B1BD"
EDGE = "#FFFFFF@0.10"
SHADOW = "0 14px 34px rgba(0,0,0,.5)"
F = "$font"      # Inter: body and labels
F2 = "$font2"    # condensed: names and titles
OUT_ = {"type": "fade", "dur": 260, "delay": 0, "ease": "in"}
P = "podcast."

PS = dict(BL.NETWORK, key="podcast", font=F2, body=F, up=True, radius=6, cardRadius=10,
          panel=PANEL, panel2=PANEL2, dark=BG, strip=LIGHT, stripText=INK, val=LIGHT, valText=INK,
          hi=ACC, hiText="#FFFFFF", line="#FFFFFF@0.12", shadow=SHADOW, cardIn="zoom-out",
          teamGrad=("linear-gradient(180deg, color-mix(in srgb, {%s.color} 85%%, #fff) 0%%, {%s.color} 55%%, "
                    "color-mix(in srgb, {%s.color} 70%%, #000) 100%%)"),
          titleBg=BG_GRAD)


def G(name, group, E, autoHide=0, **kw):
    d = {"name": name, "group": group, "autoHide": autoHide, "side": "", "sided": False, "elements": E, "cat": "podcast", "sport": "all"}
    d.update(kw)
    return d


def T(name, x, y, w, h, text, size, a, show=None, **st):
    st.setdefault("font", F2)
    st.setdefault("weight", 800)
    return txt(name, x, y, w, h, text, size, a, show=show, **st)


def L(name, x, y, w, h, text, size, a, show=None, **st):
    """Small label type: Inter, spaced capitals."""
    st.setdefault("font", F)
    st.setdefault("weight", 700)
    st.setdefault("tracking", 2)
    return txt(name, x, y, w, h, text, size, a, show=show, **st)


def card(name, x, y, w, h, delay=0, **kw):
    return box(name, x, y, w, h, None, A("zoom-out", 460, delay, out=OUT_), bg=PANEL, radius=10, borderW=1, borderColor=EDGE, shadow=SHADOW, **kw)


def header(x, y, w, kicker, title, delay=0, title_size=64):
    """Accent kicker over a big condensed title, with an accent underline."""
    return [L("Kicker", x, y, w, 34, kicker, 22, A("fade", 260, delay + 200), color=ACC),
            T("Title", x, y + 30, w, 84, title, title_size, A("reveal-up", 400, delay + 260)),
            box("Title rule", x, y + 118, 120, 6, ACC, A("grow-x", 360, delay + 420), radius=3)]


def logo_mark(name, x, y, w, h, delay=0):
    """Show logo (Podcast tab), else the brand logo, else the show name in a block."""
    return [img(name, x, y, w, h, "{podcast.logo}", A("zoom-out", 420, delay), show=P + "logo"),
            img(name + " brand", x, y, w, h, "{brand.logo}", A("zoom-out", 420, delay), show="!podcast.logo && brand.logo")]


# ------------------------------------------------------------------ name bars
def name_bar(gname, who, autoHide=8):
    """Accent edge, dark bar: NAME, role in accent capitals, handle on the right; round photo when there is one."""
    X, Y, W, H = 120, 850, 1100, 112
    pre = P + who
    E = [box("Edge", X, Y, 12, H, ACC, A("grow-y", 300, 0, out=OUT_), show=pre + ".name"),
         box("Bar", X + 12, Y, W - 12, H, None, A("wipe-right", 440, 80, out=OUT_), show=pre + ".name", bg=PANEL, shadow=SHADOW, radius=6, borderW=1,
             borderColor=EDGE),
         box("Photo ring", X + 30, Y + 12, 88, 88, ACC, A("pop", 360, 300), show=pre + ".photo", radius=44),
         img("Photo", X + 34, Y + 16, 80, 80, "{%s.photo}" % pre, A("pop", 360, 320), show=pre + ".photo", fit="cover", radius=40),
         T("Name", X + 40, Y + 4, W - 360, 70, "{%s.name|upper}" % pre, 56, A("slide-right", 380, 260, dist=30), show="!" + pre + ".photo"),
         T("Name (photo)", X + 136, Y + 4, W - 456, 70, "{%s.name|upper}" % pre, 56, A("slide-right", 380, 260, dist=30), show=pre + ".photo"),
         L("Role", X + 42, Y + 70, W - 360, 34, "{%s.role|upper}" % pre, 22, A("fade", 260, 420), show="!" + pre + ".photo", color=ACC),
         L("Role (photo)", X + 138, Y + 70, W - 456, 34, "{%s.role|upper}" % pre, 22, A("fade", 260, 420), show=pre + ".photo", color=ACC),
         txt("Handle", X + W - 320, Y, 296, H, "{%s.handle}" % pre, 30, A("fade", 260, 480), show=pre + ".handle", font=F, weight=600, color=DIM,
             align="right")]
    return G(gname, "lower", E, autoHide)


def mic_tag():
    """Small corner tag that follows whoever is on the mic (Podcast tab > On mic)."""
    X, Y = 40, 40
    E = [box("Tag", X, Y, 420, 64, None, A("wipe-right", 360, 0, out=OUT_), bg=PANEL, radius=32, borderW=1, borderColor=EDGE, shadow=SHADOW),
         box("Dot", X + 20, Y + 22, 20, 20, "#FF3B30", A("pop", 300, 200, loop={"type": "pulse", "dur": 1200, "amount": 0.25}), radius=10),
         L("On mic", X + 52, Y, 110, 64, "ON MIC", 18, A("fade", 240, 260), color=DIM),
         T("Name", X + 150, Y, 250, 64, "{podcast.mic.name|upper}", 32, A("fade", 260, 300, change="flash"))]
    return G("On Mic Tag", "bug2", E)


# ------------------------------------------------------------------ show identity
def show_open():
    E = [box("Backdrop", 0, 0, 1920, 1080, None, A("fade", 500, 0, out=OUT_), bg=BG_GRAD),
         box("Glow", 960 - 700, 540 - 700, 1400, 1400, None, A("scale", 1200, 0), bg="radial-gradient(circle, color-mix(in srgb, $accent 30%, transparent) 0%, transparent 60%)"),
         box("Bar", 0, 760, 1920, 10, ACC, A("grow-x", 600, 300))]
    E += logo_mark("Logo", 760, 170, 400, 300, 300)
    E += [T("Show", 160, 480, 1600, 150, "{podcast.name|upper}", 140, A("letters", 600, 500, stagger=30), align="center"),
          L("Tagline", 160, 630, 1600, 50, "{podcast.tagline|upper}", 30, A("fade", 400, 1100), align="center", color=DIM, tracking=6),
          box("Ep chip", 810, 800, 300, 56, ACC, A("pop", 360, 1300), radius=28, show=P + "ep"),
          L("Ep", 810, 800, 300, 56, "EPISODE {podcast.ep}", 24, A("fade", 260, 1400), show=P + "ep", align="center", color="#FFFFFF"),
          T("Ep title", 160, 870, 1600, 80, "{podcast.epTitle}", 56, A("fade", 400, 1500), align="center", upper=False, weight=700)]
    return G("Show Open", "full", E)


def show_bug():
    X, Y = 1500, 40
    E = [box("Bug", X, Y, 380, 96, None, A("wipe-left", 400, 0, out=OUT_), bg=PANEL, radius=10, borderW=1, borderColor=EDGE, shadow=SHADOW)]
    E += logo_mark("Logo", X + 12, Y + 10, 96, 76, 200)
    E += [T("Show", X + 120, Y + 6, 246, 50, "{podcast.name|upper}", 34, A("fade", 260, 260)),
          L("Ep", X + 122, Y + 54, 160, 32, "EP {podcast.ep}", 18, A("fade", 260, 320), show=P + "ep", color=DIM),
          box("Live dot", X + 286, Y + 64, 12, 12, "#FF3B30", A("pop", 260, 360, loop={"type": "pulse", "dur": 1200, "amount": 0.25}), radius=6,
              show=P + "live"),
          L("Live", X + 302, Y + 54, 70, 32, "LIVE", 18, A("fade", 260, 380), show=P + "live", color="#FF3B30")]
    return G("Show Bug", "bug2", E)


def episode_bar():
    X, Y, W = 120, 860, 1300
    E = [box("Chip", X, Y, 240, 100, ACC, A("wipe-right", 380, 0, out=OUT_), radius=6),
         L("Ep label", X, Y + 10, 240, 30, "EPISODE", 20, A("fade", 240, 200), align="center", color="#FFFFFF"),
         T("Ep number", X, Y + 34, 240, 62, "{podcast.ep}", 56, A("reveal-up", 340, 240), align="center"),
         box("Bar", X + 240, Y, W - 240, 100, None, A("wipe-right", 440, 120, out=OUT_), bg=PANEL, radius=6, borderW=1, borderColor=EDGE, shadow=SHADOW),
         T("Title", X + 272, Y, W - 300, 100, "{podcast.epTitle}", 54, A("slide-right", 380, 300, dist=30), upper=False, weight=700)]
    return G("Episode Title", "lower", E, 8)


# ------------------------------------------------------------------ people cards
def guest_card():
    X, Y, W, H = 200, 140, 1520, 760
    E = [card("Card", X, Y, W, H),
         box("Photo bg", X + 30, Y + 30, 560, H - 60, None, A("wipe-up", 460, 200), bg="linear-gradient(180deg, #2A313D, #161A21)", radius=8),
         img("Photo", X + 30, Y + 30, 560, H - 60, "{podcast.guest.photo}", A("slide-up", 520, 360, dist=40), show=P + "guest.photo", fit="cover",
             radius=8),
         T("Initial", X + 30, Y + 30, 560, H - 60, "{podcast.guest.name|upper}", 70, A("fade", 400, 360), show="!" + P + "guest.photo", align="center",
           color="#FFFFFF@0.18", wrap=True, fit=False)]
    E += header(X + 640, Y + 50, W - 690, "TONIGHT'S GUEST", "{podcast.guest.name|upper}", 200, 84)
    E += [L("Role", X + 640, Y + 200, W - 690, 40, "{podcast.guest.role|upper}", 26, A("fade", 300, 600), color=DIM)]
    for i in range(3):
        k = P + "guest.b%d" % (i + 1)
        y = Y + 280 + i * 120
        E += [box("Bullet %d" % (i + 1), X + 644, y + 26, 16, 16, ACC, A("pop", 300, 700 + i * 140), show=k, rotate=45),
              txt("Fact %d" % (i + 1), X + 690, y, W - 740, 100, "{%s}" % k, 38, A("slide-right", 380, 720 + i * 140, dist=30), show=k, font=F,
                  weight=600, wrap=True, fit=False, valign="center")]
    E += [txt("Handle", X + 640, Y + H - 90, W - 690, 50, "{podcast.guest.handle}", 32, A("fade", 300, 1100), show=P + "guest.handle", font=F,
              weight=700, color=ACC)]
    return G("Guest Intro", "full", E)


def panel_card():
    """Everyone on today's show. Seats are centred for however many people are filled in (1 to 4)."""
    X, Y, W, H = 120, 120, 1680, 820
    E = [card("Card", X, Y, W, H)]
    E += header(X + 50, Y + 40, W - 100, "{podcast.name|upper}", "TODAY'S PANEL", 200)
    cw, gap = 370, 30
    for count in (1, 2, 3, 4):
        x0 = X + (W - (count * cw + (count - 1) * gap)) // 2
        only = "podcast.count==%d" % count if count > 1 else "podcast.count<=1"
        for i in range(count):
            n = i + 1
            pre = P + "p%d" % n
            x = x0 + i * (cw + gap)
            y = Y + 210
            d = 500 + i * 140
            tag = " (%d up)" % count
            sh = lambda *c: both(only, *c)
            E += [box("Seat %d%s" % (n, tag), x, y, cw, 560, None, A("slide-up", 420, d, dist=40), show=sh(pre + ".name"), bg=PANEL2, radius=8, borderW=1,
                      borderColor=EDGE),
                  img("Photo %d%s" % (n, tag), x, y, cw, 400, "{%s.photo}" % pre, A("fade", 400, d + 120), show=sh(pre + ".name", pre + ".photo"), fit="cover",
                      radius=8),
                  T("Initial %d%s" % (n, tag), x, y, cw, 400, "{%s.name|upper}" % pre, 40, A("fade", 400, d + 120), show=sh(pre + ".name", "!" + pre + ".photo"),
                    align="center", color="#FFFFFF@0.16", wrap=True, fit=False),
                  box("Seat rule %d%s" % (n, tag), x, y + 400, cw, 6, ACC, A("grow-x", 300, d + 200), show=sh(pre + ".name")),
                  T("Name %d%s" % (n, tag), x + 20, y + 414, cw - 40, 70, "{%s.name|upper}" % pre, 44, A("fade", 300, d + 240), show=sh(pre + ".name")),
                  L("Role %d%s" % (n, tag), x + 22, y + 482, cw - 40, 30, "{%s.role|upper}" % pre, 20, A("fade", 300, d + 280), show=sh(pre + ".name"),
                    color=ACC),
                  txt("Handle %d%s" % (n, tag), x + 22, y + 512, cw - 40, 34, "{%s.handle}" % pre, 22, A("fade", 300, d + 300), show=sh(pre + ".handle"),
                      font=F, weight=600, color=DIM)]
    return G("Panel Intro", "full", E)


# ------------------------------------------------------------------ topics
def topic_bar():
    """Top of screen: segment label and the current topic. Stays up while lower thirds come and go."""
    X, Y, W = 0, 0, 1920
    E = [box("Bar", X, Y, W, 72, None, A("wipe-down", 360, 0, out={"type": "wipe-up", "dur": 260, "delay": 0, "ease": "in"}), bg=PANEL,
             borderW=0, shadow="0 8px 22px rgba(0,0,0,.45)"),
         box("Seg", X, Y, 300, 72, ACC, A("wipe-right", 360, 120)),
         L("Seg text", X, Y, 300, 72, "{podcast.seg|upper}", 22, A("fade", 240, 260), align="center", color="#FFFFFF"),
         L("Now", X + 330, Y, 90, 72, "NOW", 20, A("fade", 240, 300), color=DIM),
         T("Topic", X + 410, Y, W - 760, 72, "{podcast.topic|upper}", 40, A("slide-right", 360, 320, dist=30, change="flash")),
         L("Show", X + W - 330, Y, 300, 72, "{podcast.name|upper}", 18, A("fade", 240, 360), align="right", color=DIM)]
    return G("Topic Bar", "topic", E, noLift=True)


def rundown():
    X, Y, W = 1400, 120, 470
    E = [card("Card", X, Y, W, 800)]
    E += [L("Kicker", X + 34, Y + 30, W - 60, 30, "{podcast.name|upper}", 18, A("fade", 260, 200), color=ACC),
          T("Title", X + 34, Y + 56, W - 60, 70, "RUNDOWN", 56, A("reveal-up", 360, 260)),
          box("Rule", X + 34, Y + 130, 80, 5, ACC, A("grow-x", 300, 400), radius=3),
          el("table", "Items", X + 24, Y + 160, W - 48, 610, A("none", 1, 0, rows={"type": "slide-right", "dur": 320, "stagger": 70, "delay": 500, "dist": 30}),
             bind=P + "agendaRows",
             columns=[{"label": "", "field": "n", "w": 0.5, "align": "center", "fillIf": "cur", "fillOn": ACC, "color": DIM, "colorIf": "cur",
                       "colorOn": "#FFFFFF", "weight": 800},
                      {"label": "", "field": "{row.text|upper}", "w": 4, "align": "left", "fillIf": "cur", "fillOn": "#FFFFFF@0.08", "padX": 18, "weight": 800}],
             style={"rowH": 64, "size": 28, "weight": 700, "color": "#FFFFFF", "header": False, "padX": 0, "gap": 8, "maxRows": 9, "font": F2,
                    "radius": 6})]
    return G("Rundown", "panel", E)


def segment_bumper():
    hold = lambda a_, h: dict(a_, hold=h)
    E = [box("Backdrop", 0, 0, 1920, 1080, None, hold(A("wipe-right", 420, 0, out={"type": "wipe-right", "dur": 360, "delay": 0, "ease": "in"}), 1700),
             bg=BG_GRAD),
         box("Band", 0, 420, 1920, 240, None, hold(A("wipe-right", 420, 120, out={"type": "wipe-left", "dur": 320, "delay": 0, "ease": "in"}), 1500), bg=ACC_GRAD),
         L("Segment", 0, 330, 1920, 70, "{podcast.seg|upper}", 40, hold(A("fade", 300, 300, out=OUT_), 1400), align="center", color=ACC, tracking=10),
         T("Topic", 80, 420, 1760, 240, "{podcast.topic|upper}", 150, hold(A("letters", 500, 380, stagger=25, out=OUT_), 1200), align="center")]
    E += logo_mark("Logo", 860, 700, 200, 150, 600)
    return G("Segment Bumper", "stinger", E, 2.6, cat="podcast")


def up_next():
    X, Y, W = 120, 860, 1200
    E = [box("Label", X, Y, 260, 100, ACC, A("wipe-right", 380, 0, out=OUT_), radius=6),
         L("Label t", X, Y, 260, 100, "COMING UP", 26, A("fade", 240, 200), align="center", color="#FFFFFF"),
         box("Bar", X + 260, Y, W - 260, 100, None, A("wipe-right", 440, 120, out=OUT_), bg=PANEL, radius=6, borderW=1, borderColor=EDGE, shadow=SHADOW),
         T("Next", X + 290, Y, W - 320, 100, "{podcast.next|upper}", 50, A("slide-right", 380, 300, dist=30))]
    return G("Coming Up", "lower", E, 8)


# ------------------------------------------------------------------ discussion
def quote_card():
    X, Y, W, H = 260, 200, 1400, 680
    E = [card("Card", X, Y, W, H),
         T("Mark", X + 60, Y + 10, 200, 220, "“", 280, A("pop", 420, 200), color=ACC, font=F),
         txt("Quote", X + 120, Y + 150, W - 240, 340, "{podcast.quote}", 56, A("fade", 500, 400), font=F, weight=700, wrap=True, fit=False,
             lineH=1.15, valign="center", italic=True),
         box("Rule", X + 120, Y + 520, 100, 6, ACC, A("grow-x", 300, 700), radius=3),
         T("By", X + 120, Y + 540, W - 240, 60, "{podcast.quoteBy|upper}", 42, A("slide-right", 360, 800, dist=30)),
         L("Source", X + 122, Y + 600, W - 240, 40, "{podcast.quoteSrc|upper}", 22, A("fade", 300, 900), show=P + "quoteSrc", color=DIM)]
    return G("Quote", "full", E)


def compare_card():
    X, Y, W, H = 360, 120, 1200, 820
    E = [card("Card", X, Y, W, H)]
    E += [L("Kicker", X, Y + 40, W, 34, "{podcast.name|upper}", 20, A("fade", 260, 200), align="center", color=ACC),
          T("Title", X, Y + 70, W, 80, "{podcast.cmpTitle|upper}", 64, A("reveal-up", 400, 260), align="center"),
          box("Left", X + 40, Y + 180, 520, 90, None, A("wipe-right", 380, 400), bg=PANEL2, radius=6),
          T("Left t", X + 40, Y + 180, 520, 90, "{podcast.cmpL|upper}", 46, A("fade", 260, 520), align="center"),
          box("Right", X + W - 560, Y + 180, 520, 90, None, A("wipe-left", 380, 400), bg=PANEL2, radius=6),
          T("Right t", X + W - 560, Y + 180, 520, 90, "{podcast.cmpR|upper}", 46, A("fade", 260, 520), align="center"),
          L("VS", X + W // 2 - 50, Y + 180, 100, 90, "VS", 26, A("pop", 300, 560), align="center", color=ACC),
          el("table", "Rows", X + 40, Y + 300, W - 80, 480, A("none", 1, 0, rows={"type": "pop", "dur": 320, "stagger": 80, "delay": 620}),
             bind=P + "cmpRows",
             columns=[{"label": "", "field": "l", "w": 1, "align": "center", "fill": LIGHT, "color": INK, "weight": 800, "size": 46},
                      {"label": "", "field": "{row.label|upper}", "w": 1.2, "align": "center", "color": DIM, "size": 24, "weight": 700},
                      {"label": "", "field": "r", "w": 1, "align": "center", "fill": LIGHT, "color": INK, "weight": 800, "size": 46}],
             style={"rowH": 84, "size": 34, "weight": 800, "color": "#FFFFFF", "header": False, "padX": 0, "gap": 14, "maxRows": 5, "font": F2,
                    "radius": 6})]
    return G("Head to Head", "full", E)


def poll_card():
    X, Y, W, H = 360, 140, 1200, 800
    E = [card("Card", X, Y, W, H)]
    E += header(X + 60, Y + 40, W - 120, "POLL", "{podcast.poll}", 200, 60)
    for i in range(4):
        o = P + "o%d" % (i + 1)
        y = Y + 220 + i * 130
        d = 500 + i * 120
        E += [box("Track %d" % (i + 1), X + 60, y, W - 120, 104, None, A("wipe-right", 380, d), show=o + ".text", bg=PANEL2, radius=8),
              box("Bar %d" % (i + 1), X + 60, y, W - 120, 104, None, A("fade", 300, d + 100), show=o + ".text", bg=ACC_GRAD, radius=8, pct="{%s.pct}" % o),
              box("Letter bg %d" % (i + 1), X + 76, y + 20, 64, 64, "#FFFFFF", A("pop", 300, d + 120), show=o + ".text", radius=32),
              T("Letter %d" % (i + 1), X + 76, y + 20, 64, 64, "{%s.n}" % o, 34, A("fade", 240, d + 160), show=o + ".text", align="center", color=INK),
              T("Option %d" % (i + 1), X + 164, y, W - 420, 104, "{%s.text|upper}" % o, 44, A("slide-right", 340, d + 140, dist=24), show=o + ".text"),
              T("Pct %d" % (i + 1), X + W - 260, y, 180, 104, "{%s.pctText}" % o, 52, A("fade", 300, d + 200, change="pop"), show=o + ".pctText",
                align="right")]
    return G("Poll", "full", E)


def question_card():
    X, Y, W, H = 120, 690, 1100, 290
    E = [box("Card", X, Y, W, H, None, A("slide-up", 420, 0, dist=40, out=OUT_), bg=PANEL, radius=10, borderW=1, borderColor=EDGE, shadow=SHADOW),
         box("Source", X + 30, Y - 26, 230, 52, ACC, A("pop", 340, 200), radius=26),
         L("Source t", X + 30, Y - 26, 230, 52, "{podcast.qSource|upper}", 22, A("fade", 240, 300), align="center", color="#FFFFFF"),
         txt("Handle", X + 40, Y + 40, W - 80, 50, "{podcast.qHandle}", 34, A("fade", 260, 360), font=F, weight=700, color=ACC),
         txt("Question", X + 40, Y + 96, W - 80, 170, "{podcast.qText}", 40, A("fade", 360, 440), font=F, weight=600, wrap=True, fit=False,
             valign="top", lineH=1.2)]
    return G("Mailbag / Chat Question", "lower", E)


def top_list():
    X, Y, W, H = 360, 100, 1200, 880
    E = [card("Card", X, Y, W, H)]
    E += header(X + 60, Y + 40, W - 120, "{podcast.name|upper}", "{podcast.topTitle|upper}", 200, 70)
    E += [el("table", "List", X + 50, Y + 200, W - 100, 640, A("none", 1, 0, rows={"type": "slide-right", "dur": 360, "stagger": 0, "delay": 400, "dist": 30}),
             bind=P + "topRows",
             columns=[{"label": "", "field": "n", "w": 0.6, "align": "center", "fill": ACC, "color": "#FFFFFF", "weight": 800, "size": 52},
                      {"label": "", "field": "{row.text|upper}", "w": 4.4, "align": "left", "padX": 24, "weight": 800, "size": 46},
                      {"label": "", "field": "{row.note}", "w": 1.6, "align": "right", "padX": 20, "weight": 600, "size": 26, "color": DIM}],
             style={"rowH": 112, "size": 40, "weight": 800, "color": "#FFFFFF", "header": False, "padX": 0, "gap": 14, "maxRows": 5, "font": F2,
                    "rowFill": "#FFFFFF@0.05", "radius": 8})]
    return G("Top 5 Countdown", "full", E)


def picks_card():
    X, Y, W, H = 260, 140, 1400, 800
    E = [card("Card", X, Y, W, H)]
    E += header(X + 60, Y + 40, W - 120, "{podcast.name|upper}", "{podcast.picksTitle|upper}", 200, 70)
    E += [el("table", "Picks", X + 50, Y + 210, W - 100, 560, A("none", 1, 0, rows={"type": "slide-right", "dur": 340, "stagger": 90, "delay": 500, "dist": 30}),
             bind=P + "pickRows",
             columns=[{"label": "", "field": "{row.who|upper}", "w": 2.2, "align": "left", "padX": 24, "weight": 800, "fill": "#FFFFFF@0.06"},
                      {"label": "", "field": "{row.pick|upper}", "w": 2, "align": "center", "fill": ACC, "color": "#FFFFFF", "weight": 800, "size": 44},
                      {"label": "", "field": "{row.note}", "w": 3, "align": "left", "padX": 24, "weight": 600, "size": 28, "color": DIM}],
             style={"rowH": 104, "size": 40, "weight": 800, "color": "#FFFFFF", "header": False, "padX": 0, "gap": 14, "maxRows": 5, "font": F2,
                    "radius": 8})]
    return G("Picks", "full", E)


def hot_take():
    X, Y, W = 0, 400, 1920
    E = [box("Band", X, Y, W, 280, None, A("wipe-right", 340, 0, out={"type": "wipe-right", "dur": 320, "delay": 0, "ease": "in"}),
             bg="linear-gradient(90deg, #FF3B1F 0%, #FF7A1A 55%, #FFB21A 100%)"),
         box("Shade", X, Y + 180, W, 100, "#000000@0.28", A("fade", 300, 200)),
         T("Label", 100, Y + 10, 860, 180, "HOT TAKE", 150, A("letters", 500, 200, stagger=40), italic=True, textShadow="0 6px 0 rgba(0,0,0,.25)"),
         txt("Take", 1020, Y + 20, 800, 160, "{podcast.take}", 46, A("fade", 400, 700), font=F, weight=800, wrap=True, fit=False, valign="center",
             lineH=1.1),
         T("By", 120, Y + 180, 1700, 100, "{podcast.takeBy|upper}", 50, A("slide-right", 360, 800, dist=30))]
    return G("Hot Take", "event", E, 7)


# ------------------------------------------------------------------ calls to action
def follow_bar():
    X, Y, W = 120, 870, 1680
    E = [box("Bar", X, Y, W, 100, None, A("wipe-right", 440, 0, out=OUT_), bg=PANEL, radius=10, borderW=1, borderColor=EDGE, shadow=SHADOW),
         box("CTA", X, Y, 420, 100, ACC, A("wipe-right", 380, 100), radius=10),
         T("CTA t", X + 20, Y, 380, 100, "FOLLOW THE SHOW", 40, A("fade", 260, 300), align="center")]
    cw = (W - 460) // 5
    for i in range(5):
        s_ = P + "s%d" % (i + 1)
        x = X + 440 + i * cw
        d = 360 + i * 90
        E += [box("Icon %d" % (i + 1), x, Y + 26, 64, 48, "#FFFFFF@0.12", A("pop", 300, d), show=s_ + ".handle", radius=8),
              L("Icon t %d" % (i + 1), x, Y + 26, 64, 48, "{%s.icon}" % s_, 18, A("fade", 240, d + 60), show=s_ + ".handle", align="center", tracking=0),
              txt("Handle %d" % (i + 1), x + 74, Y, cw - 84, 100, "{%s.handle}" % s_, 30, A("fade", 260, d + 80), show=s_ + ".handle", font=F,
                  weight=700)]
    E += [L("Ask", X + 440, Y + 100, W - 460, 40, "{podcast.cta|upper}", 20, A("fade", 260, 900), show=P + "cta", color=DIM)]
    return G("Follow / Subscribe", "lower", E, 10)


def sponsor_read():
    X, Y, W = 120, 820, 1500
    E = [box("Bar", X, Y, W, 150, None, A("wipe-right", 440, 0, out=OUT_), bg=PANEL, radius=10, borderW=1, borderColor=EDGE, shadow=SHADOW),
         box("Logo bg", X + 20, Y + 20, 300, 110, "#FFFFFF", A("pop", 360, 200), radius=6),
         img("Sponsor", X + 34, Y + 28, 272, 94, "{sponsor.logo}", A("fade", 300, 320, change="fade"), show="sponsor.on && sponsor.logo"),
         txt("Sponsor name", X + 30, Y + 20, 280, 110, "{sponsor.name}", 30, A("fade", 300, 320), show="sponsor.on && !sponsor.logo", font=F2,
             weight=800, color=INK, align="center", wrap=True, fit=False),
         L("Head", X + 350, Y + 18, 700, 34, "{podcast.adHead|upper}", 20, A("fade", 260, 300), color=ACC),
         T("Text", X + 350, Y + 46, W - 640, 64, "{podcast.adText}", 44, A("slide-right", 360, 360, dist=24), upper=False),
         box("Code bg", X + 350, Y + 108, 300, 34, ACC, A("pop", 300, 500), radius=17, show=P + "adCode"),
         L("Code", X + 350, Y + 108, 300, 34, "CODE {podcast.adCode|upper}", 18, A("fade", 240, 560), show=P + "adCode", align="center", color="#FFFFFF"),
         txt("Url", X + 670, Y + 108, W - 960, 34, "{podcast.adUrl}", 24, A("fade", 260, 600), show=P + "adUrl", font=F, weight=600, color=DIM),
         box("QR bg", X + W - 140, Y + 14, 122, 122, "#FFFFFF", A("pop", 360, 500), show=P + "adUrl", radius=6),
         el("qr", "QR", X + W - 134, Y + 20, 110, 110, A("fade", 300, 600), show=P + "adUrl", text="{podcast.adUrl}",
            style={"color": "#000000", "bg": "#FFFFFF", "quiet": 1, "ecc": "M"})]
    return G("Sponsor Read", "lower", E, 12, sponsorSlot="podcast, show")


def qr_card():
    X, Y = 1500, 560
    E = [box("Card", X, Y, 340, 420, None, A("slide-left", 420, 0, dist=40, out=OUT_), bg=PANEL, radius=12, borderW=1, borderColor=EDGE, shadow=SHADOW),
         box("QR bg", X + 30, Y + 30, 280, 280, "#FFFFFF", A("pop", 360, 200), radius=8),
         el("qr", "QR", X + 40, Y + 40, 260, 260, A("fade", 300, 300), text="{podcast.qrUrl}", style={"color": "#000000", "bg": "#FFFFFF", "quiet": 1, "ecc": "M"}),
         txt("Text", X + 20, Y + 320, 300, 90, "{podcast.qrText|upper}", 26, A("fade", 260, 400), font=F2, weight=800, align="center", wrap=True,
             fit=False)]
    return G("QR Code", "panel", E)


# ------------------------------------------------------------------ full-screen holds
def hold_screen(name, msg, clock=False, socials=False):
    E = [box("Backdrop", 0, 0, 1920, 1080, None, A("fade", 500, 0, out=OUT_), bg=BG_GRAD),
         box("Glow", 960 - 700, 380 - 700, 1400, 1400, None, A("fade", 900, 0), bg="radial-gradient(circle, color-mix(in srgb, $accent 22%, transparent) 0%, transparent 60%)"),
         box("Floor", 0, 1050, 1920, 30, ACC, A("grow-x", 600, 200))]
    E += logo_mark("Logo", 810, 120, 300, 220, 200)
    E += [T("Show", 160, 350, 1600, 110, "{podcast.name|upper}", 90, A("fade", 400, 300), align="center"),
          L("Msg", 160, 480, 1600, 70, msg, 40, A("fade", 400, 500), align="center", color=ACC, tracking=10)]
    if clock:
        E.append(el("clock", "Countdown", 560, 560, 800, 230, A("fade", 400, 700), mode="to", target="{podcast.soonTime}", done="LIVE",
                    style={"color": "#FFFFFF", "size": 200, "weight": 800, "align": "center", "font": F2}))
    else:
        E.append(T("Ep title", 160, 580, 1600, 90, "{podcast.epTitle}", 60, A("fade", 400, 700), align="center", upper=False, weight=700, color=DIM))
    if socials:
        for i in range(5):
            s_ = P + "s%d" % (i + 1)
            x = 260 + i * 290
            E += [L("Icon %d" % (i + 1), x, 820, 270, 40, "{%s.icon}" % s_, 22, A("fade", 300, 900 + i * 80), show=s_ + ".handle", align="center",
                    color=DIM),
                  txt("Handle %d" % (i + 1), x, 860, 270, 60, "{%s.handle}" % s_, 34, A("fade", 300, 940 + i * 80), show=s_ + ".handle", font=F,
                      weight=700, align="center")]
    return G(name, "full", E)


# ------------------------------------------------------------------ remote guest frames
def remote(n):
    """Background with see-through windows for video calls, frame edges and name plates. In OBS, put each video call
    source in the Baseball Graphics scene below the graphics, at the window positions listed in the guide."""
    M, TOPB, BOT = 60, 110, 110
    if n == 2:
        wins = [(60, 180, 880, 660), (980, 180, 880, 660)]
    elif n == 3:
        wins = [(60, 220, 586, 586), (667, 220, 586, 586), (1274, 220, 586, 586)]
    else:
        wins = [(260, 120, 690, 388), (970, 120, 690, 388), (260, 540, 690, 388), (970, 540, 690, 388)]
    holes = "; ".join("%d,%d,%d,%d" % w for w in wins)
    E = [box("Backdrop", 0, 0, 1920, 1080, None, A("fade", 400, 0, out=OUT_), bg=BG_GRAD, holes=holes)]
    for i, (x, y, w, h) in enumerate(wins):
        k = i + 1
        pre = P + "p%d" % k
        d = 200 + i * 100
        E += [box("Frame %d" % k, x - 4, y - 4, w + 8, h + 8, None, A("fade", 300, d), borderW=4, borderColor="#FFFFFF@0.18", radius=6),
              box("Mic %d" % k, x - 4, y - 4, w + 8, h + 8, None, A("fade", 200, d), show="podcast.speaker==%d" % k, borderW=6, borderColor=ACC, radius=6),
              box("Plate %d" % k, x, y + h - 70, min(w, 520), 70, None, A("wipe-right", 360, d + 200), bg=PANEL, show=pre + ".name"),
              box("Plate edge %d" % k, x, y + h - 70, 8, 70, ACC, A("grow-y", 260, d + 300), show=pre + ".name"),
              T("Name %d" % k, x + 22, y + h - 70, min(w, 520) - 40, 44, "{%s.name|upper}" % pre, 32, A("fade", 260, d + 360), show=pre + ".name"),
              L("Role %d" % k, x + 24, y + h - 32, min(w, 520) - 40, 26, "{%s.role|upper}" % pre, 16, A("fade", 260, d + 400), show=pre + ".name",
                color=ACC)]
    E += logo_mark("Logo", 40, 1080 - BOT + 14, 110, 82, 300)
    E += [T("Show", 170, 1080 - BOT + 10, 700, 50, "{podcast.name|upper}", 36, A("fade", 300, 400)),
          T("Topic", 170, 1080 - BOT + 56, 1500, 44, "{podcast.topic|upper}", 30, A("fade", 300, 460, change="flash"), color=DIM)]
    return G("Remote Frame: %d Up" % n, "full", E, noLift=True)


# ------------------------------------------------------------------ assemble
night_doc = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))
night = night_doc["graphics"]
g = {}
SKIP = ("bug_compact", "bug_compact_title", "batter_note", "pitcher_note", "batter_tab", "pitcher_tab")
MS = dict(PS, **SK.MARKS)
for gid, gdef in BL.all_new(MS).items():
    if gid.startswith("c_") or gid in SKIP:
        continue
    g[gid] = gdef
for gid in ("scorebug", "batter", "pitcher", "dueup", "inning_sponsor", "lineup", "pitching", "defense", "linescore", "spotlight", "note", "matchup",
            "standings", "custom", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g["batter_card"] = BL.stat_card_tonight(MS, "bat")
g["pitcher_card"] = BL.stat_card_tonight(MS, "pit")
g.update(SL.all_sports(MS))
POD = {
    "pod_open": show_open(), "pod_bug": show_bug(), "pod_episode": episode_bar(), "pod_mic": mic_tag(),
    "pod_name": name_bar("Name Bar: On Mic", "mic"), "pod_p1": name_bar("Name Bar: Person 1", "p1"), "pod_p2": name_bar("Name Bar: Person 2", "p2"),
    "pod_p3": name_bar("Name Bar: Person 3", "p3"), "pod_p4": name_bar("Name Bar: Person 4", "p4"), "pod_guest_bar": name_bar("Name Bar: Guest", "guest"),
    "pod_guest": guest_card(), "pod_panel": panel_card(), "pod_topic": topic_bar(), "pod_rundown": rundown(), "pod_segment": segment_bumper(),
    "pod_upnext": up_next(), "pod_quote": quote_card(), "pod_compare": compare_card(), "pod_poll": poll_card(), "pod_question": question_card(),
    "pod_top": top_list(), "pod_picks": picks_card(), "pod_take": hot_take(), "pod_follow": follow_bar(), "pod_sponsor": sponsor_read(),
    "pod_qr": qr_card(), "pod_soon": hold_screen("Starting Soon", "{podcast.soonMsg|upper}", clock=True),
    "pod_brb": hold_screen("Be Right Back", "{podcast.brbMsg|upper}"), "pod_end": hold_screen("Thanks for Watching", "{podcast.endMsg|upper}", socials=True),
    "pod_remote2": remote(2), "pod_remote3": remote(3), "pod_remote4": remote(4),
}
g.update(POD)
# Talent in this style shows persons 1 and 2 from the Podcast tab (other styles use Custom > Show > Talent).
_t = json.dumps(g["talent"])
for a_, b_ in (("show.host1", "podcast.p1n"), ("show.role1", "podcast.p1r"), ("show.host2", "podcast.p2n"), ("show.role2", "podcast.p2r")):
    _t = _t.replace(a_, b_)
g["talent"] = json.loads(_t)
g["talent"]["cat"] = "podcast"
CUSTOM = set(POD)


def kit_tr(gid, g_, TA):
    """Dark studio field, an accent band with the word, the show logo above."""
    E = [box("Field", 0, 0, 1920, 1080, None, TA("wipe-right", 460, 0), bg=BG_GRAD),
         box("Band", 0, 400, 1920, 260, None, TA("wipe-right", 420, 120), bg=ACC_GRAD),
         box("Shade", 0, 600, 1920, 60, "#000000@0.25", TA("fade", 300, 200))]
    return {"elements": E, "word": {"font": F2, "weight": 800, "color": "#FFFFFF", "textShadow": "", "rect": (60, 410, 1800, 190)},
            "sub": {"font": F, "weight": 700, "color": "#FFFFFF", "textShadow": "", "rect": (60, 600, 1800, 60), "tracking": 4},
            "brand": {"rect": (860, 170, 200, 180)}}


def kit_slab(R, slab, g_):
    x, y, w, h = R
    return [dict(box("Edge", 0, y, 1920, 8, ACC, A("grow-x", 300, 120)), _over=True)]


def kit_screen(bg, team, g_):
    over = [box("Floor", 0, 1050, 1920, 30, ACC, A("grow-x", 500, 200))]
    return {"floor": PANEL2, "replace": BG_GRAD, "over": over}


KIT = RB.make_kit(dict(
    screen=kit_screen, slab=kit_slab,
    body=PANEL, bodyBox={"radius": 10, "borderW": 1, "borderColor": EDGE, "shadow": SHADOW},
    head=PANEL2, headBox={"radius": 10}, headRule=ACC, headRuleH=5, sub=ACC_GRAD,
    title={"font": F2, "weight": 800, "color": "#FFFFFF", "textShadow": "", "italic": False},
    headText={"textShadow": ""}, subText={"font": F, "weight": 700, "color": "#FFFFFF", "textShadow": "", "tracking": 2},
    roles={"PANEL": PANEL, "PANEL2": PANEL2, "DARK": BG, "STRIP": LIGHT}, barBox={"radius": 6}, mainBox={"shadow": SHADOW, "borderW": 1, "borderColor": EDGE},
    tile={"radius": 8, "borderW": 0}, tr=kit_tr))
SKIN = dict(panel=PANEL, panel2=PANEL2, dark=BG, strip=LIGHT, stripText=INK, val=LIGHT, ink=INK, hi=ACC, hiText="#FFFFFF", line="#FFFFFF@0.12",
            title=BG_GRAD, shadow=SHADOW, team=lambda t: PS["teamGrad"] % (t, t, t), rule=ACC, text2="#FFFFFF", radius=6, noBlur=True,
            panelBox={"radius": 10, "borderW": 1, "borderColor": EDGE, "shadow": SHADOW}, lightBox={"radius": 6}, hiBox={"radius": 6},
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
    if not d.get("layout") and "Podcast" not in d.get("name", ""):
        d["name"] = "%s (Podcast)" % d.get("name", k)

theme = dict(night_doc["theme"])
theme.update({"primary": BG, "accent": "#FF5A1F", "text": "#FFFFFF", "dim": "rgba(233,236,241,0.72)", "line": "rgba(255,255,255,0.12)",
              "card": "rgba(28,34,43,0.96)", "panel": "rgba(28,34,43,0.96)", "panel2": "rgba(37,44,55,0.96)"})
doc = {"version": 2, "name": "Podcast",
       "description": "Sports podcast studio look: show open and bug, name bars for hosts and guests, on-mic tag, guest and panel intros, topic bar, "
                      "rundown, segment bumpers, quote, head to head, poll, mailbag, top 5, picks, hot take, follow us, sponsor read, QR, "
                      "starting soon / be right back / thanks screens and remote guest frames. Filled from the Podcast tab. Every broadcast "
                      "graphic type too, in the same look.",
       "theme": theme, "graphics": g}
out = os.path.join(ROOT, "templates", "packages", "podcast.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
