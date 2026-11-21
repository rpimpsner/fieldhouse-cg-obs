"""
OBS Baseball Graphics
=====================
An OBS Studio script plugin that serves HTML5 broadcast graphics (scorebug,
lower thirds, lineups, defense, pitching, linescore, matchup, due up and any
graphic you design in the visual editor) driven by manual scoring from the
control panel.

How it works
------------
* Loaded in OBS via Tools > Scripts (needs Python configured in OBS), this file
  starts a small local web server (default http://127.0.0.1:8765).
* Each graphic is an OBS Browser Source pointing at /overlay.html?g=<id>.
  Pages are transparent; only the designed elements draw, and they animate in
  and out with the Web Animations API.
* /control.html is the operator panel (add it as a Custom Browser Dock).
* /editor.html is the visual graphics editor.
* Data is pushed to every page over Server-Sent Events, so takes are instant.

It can also run outside OBS for testing or for a second machine:
    python obs_baseball_graphics.py [--port 8765] [--lan]

Only the Python standard library is used.
"""

import copy
import datetime
import gzip
import json
import mimetypes
import os
import queue
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import obspython as obs  # type: ignore
    IN_OBS = True
except ImportError:  # running standalone
    obs = None
    IN_OBS = False

VERSION = "1.25.2"
# Manual scoring edition: no internet calls at all; every number comes from the control panel.
EDITION = "manual"
MANUAL_ONLY = EDITION == "manual"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
TPL_DEFAULT = os.path.join(BASE_DIR, "templates", "default.json")
PKG_DIR = os.path.join(BASE_DIR, "templates", "packages")
USER_DIR = os.path.join(BASE_DIR, "user")
CONFIG_PATH = os.path.join(USER_DIR, "config.json")
UI_PATH = os.path.join(USER_DIR, "ui.json")
TPL_USER = os.path.join(USER_DIR, "templates.json")
SPONSOR_LOG_PATH = os.path.join(USER_DIR, "sponsor_log.json")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "port": 8765,
    "lan": False,                 # bind 0.0.0.0 so a tablet/phone can run the control panel
    "source": "manual",
    "poll_seconds": 2.0,          # live game state
    # Optional headshot URL pattern, e.g. https://example.com/headshots/{slug}.png
    # Fields: {slug} {first} {last} {name} {number} {team} {id}
    "photo_pattern": "",
    "photo_assign": {},           # player slug -> image URL or /media/photos/file chosen in the control panel
    "teams": {
        "away": {"color": "#3A4656", "color2": "#FFFFFF", "logo": "", "abbr": "", "name": ""},
        "home": {"color": "#0A2240", "color2": "#F5821F", "logo": "", "abbr": "", "name": ""},
    },
}

DEFAULT_UI = {
    "visible": {},
    "sides": {},                   # per-graphic team side: {"lineup": "home"}
    "groups": {},                  # per-graphic standings group index: {"standings": 1}
    "custom": {"line1": "", "line2": "", "line3": ""},
    # Feature / note text for the network graphics: feature card title + bullets, lower-third stat note,
    # and home-run distance / exit velocity typed in by the operator.
    "notes": {"kicker": "", "title": "", "b1": "", "b2": "", "b3": "", "foot": "", "stat": "", "statFoot": "", "dist": "", "ev": "", "ps": "", "tab": "", "bugTitle": "", "lfTitle": "", "lfLine": "", "listFoot": "", "bumperWord": "", "bvp": ""},
    "umpires": "",
    # Automatic stingers (graphics with a "trigger"): master switch + per-graphic off list.
    "triggers": {"enabled": True, "off": {}},
    # Show graphics (batting practice / pregame / postgame): subtitle, up-next rundown, talent
    # Player picker (Custom panel): put any rostered player on pickable graphics instead of the current batter / pitcher
    "pick": {"on": False, "side": "home", "id": ""},
    # League / brand marks (uploads or links) used by standings, ticker, show graphics
    "league": {"name": "", "logo": ""},
    "brand": {"name": "", "short": "", "logo": "", "color": "", "color2": ""},
    # Split stat card (two columns of numbers, typed in or season vs tonight)
    "split": {"title": "", "sub": "", "col1": "", "col2": "", "rows": "", "foot": ""},
    # Tonight's schedule ("5:00 | Pregame Live | Host, Analyst") and series probables ("Name | 2-1, 2.97 ERA | 5 starts")
    "schedule": {"title": "", "sub": "", "rows": "", "foot": ""},
    "probables": {"title": "", "sub": "", "rows": "", "foot": ""},
    # The road ahead: two weeks, Monday first, "29 | @MIL | W 4-2" per day
    "roadAhead": {"title": "", "rows": ""},
    # Graphics sets: named lists of graphics; the active set is all the Graphics panel and the OBS layers load.
    "sets": {}, "activeSet": "", "library": True,
    # LIVE tab hot buttons: up to 20 graphic ids, taken with keys 1-9, 0 (Shift for 11-20)
    "favorites": [],
    # Sport for this broadcast: baseball or basketball, football, hockey (manual scoring)
    "sport": "baseball", "sports": {},
    # Podcast package (control panel > Podcast). Placeholder text so every graphic shows something until it is filled in.
    "podcast": {
        "name": "Show Name", "tagline": "Sports talk", "ep": "1", "epTitle": "Episode title", "live": True, "logo": "",
        "p1n": "Host Name", "p1r": "Host", "p1h": "@host", "p1p": "", "p2n": "Co-host Name", "p2r": "Co-host", "p2h": "@cohost", "p2p": "",
        "p3n": "", "p3r": "", "p3h": "", "p3p": "", "p4n": "", "p4r": "", "p4h": "", "p4p": "", "speaker": "1",
        "gName": "Guest Name", "gTitle": "Former pitcher", "gHandle": "@guest", "gPhoto": "", "gB1": "First fact about the guest", "gB2": "Second fact",
        "gB3": "",
        "seg": "Segment 1", "topic": "Topic of discussion", "next": "Next up on the show",
        "agenda": "Opening\nLast night's games\nTrade talk\nMailbag\nPicks", "agendaIdx": 0,
        "quote": "Quote text goes here.", "quoteBy": "Who said it", "quoteSrc": "",
        "cmpTitle": "Head to head", "cmpL": "Player A", "cmpR": "Player B", "cmp": "AVG | .301 | .287\nHR | 31 | 24\nRBI | 98 | 102",
        "poll": "Who wins the division?", "pollOpts": "Team A | 48\nTeam B | 31\nTeam C | 21", "pollReveal": False,
        "qSource": "Mailbag", "qHandle": "@listener", "qText": "Your question for the show goes here.",
        "topTitle": "Top 5", "top": "Number one\nNumber two\nNumber three\nNumber four\nNumber five", "topReveal": 0,
        "picksTitle": "Tonight's picks", "picks": "Host Name | Team A | Starter is rolling\nCo-host Name | Team B | Bullpen edge",
        "take": "Your hot take goes here.", "takeBy": "Host Name",
        "x": "@show", "ig": "@show", "yt": "@show", "tt": "", "web": "", "cta": "Subscribe and turn on notifications",
        "adHead": "Brought to you by", "adText": "Sponsor message", "adCode": "", "adUrl": "",
        "soonTime": "7:00 PM", "soonMsg": "We start in", "brbMsg": "Be right back", "endMsg": "Thanks for watching", "qrUrl": "", "qrText": "Scan to subscribe",
    },
    # Game operations (control panel > GAME OPS): substitutions, pitch tracker, pitch clock, challenges, bullpen, hit data,
    # storylines, breaks, postgame and fan / sponsor features. Lists are one entry per line with "|" between columns.
    "ops": {
        "subType": "Pinch hitter", "subTeam": "batting", "subIn": "", "subInNum": "", "subPos": "", "subOut": "",
        "pitches": "", "pitchFeed": True, "pcSecs": 15, "pclock": {"ms": 15000, "running": False, "at": 0}, "pickoffs": 2, "visitsAway": 5, "visitsHome": 5,
        "chalAway": 2, "chalHome": 2, "revStatus": "", "revTeam": "home", "revCall": "",
        "bpAway": "", "bpHome": "", "hitEv": "", "hitLa": "", "hitDist": "",
        "streaks": "", "milestones": "", "cmpTitle": "Team comparison", "compare": "Batting average | .262 | .255\nHome runs | 98 | 87\nTeam ERA | 4.12 | 3.98",
        "seriesAway": "0", "seriesHome": "0", "seriesNote": "", "lastMeet": "", "nextMeet": "",
        "movesTitle": "Roster moves", "moves": "",
        "wxTemp": "", "wxWind": "", "wxCond": "", "wxHum": "",
        "delayTitle": "Rain delay", "delayMsg": "Stay with us. We will be back when play resumes.", "delaySince": 0, "delayResume": "",
        "techTitle": "Technical difficulties", "techMsg": "Please stand by",
        "star1": "", "star2": "", "star3": "",
        "kMode": "auto", "kCount": 0, "kTeam": "home", "kTitle": "Strikeout tracker",
        "billTag": "", "promosTitle": "Upcoming promotions", "promos": "", "shoutsTitle": "Welcome to the ballpark", "shouts": "", "shoutIdx": 0,
        "rundown": [], "rundownIdx": -1, "hotkeys": {},
    },
    # Bottom ticker: sections and your own tidbits (one per line)
    "ticker": {"label": "", "scores": True, "standings": True, "tidbits": "", "speed": 110},
    "show": {"promoImage": "", "promoTitle": "", "info1Label": "Game time", "info1": "", "info2Label": "Gates open", "info2": "",
             "qrUrl": "", "qrText": "Scan QR code to buy tickets", "sub": "", "next1": "", "next2": "", "next3": "", "host1": "", "role1": "", "host2": "", "role2": "", "live": True},
    # Sponsors: a library of logos and named slots that graphics point at (graphic "sponsorSlot").
    "sponsors": {"library": [], "slots": {}, "logOnlyWhenLive": True},
    "manual": {
        "away": {"name": "Visitors", "abbr": "VIS", "runs": 0, "hits": 0, "errors": 0},
        "home": {"name": "Home", "abbr": "HOM", "runs": 0, "hits": 0, "errors": 0},
        "inning": 1, "half": "top", "balls": 0, "strikes": 0, "outs": 0,
        "bases": {"1": False, "2": False, "3": False},
        "status": "LIVE",
        "batter": {"name": "", "number": "", "pos": "", "bats": "", "avg": "", "hr": "", "rbi": "", "ops": "", "line": ""},
        "pitcher": {"name": "", "number": "", "throws": "", "era": "", "pc": "", "ip": "", "k": "", "line": ""},
        "lineup_text": {"away": "", "home": ""},
        "standings_text": "",
        "linescore": {"away": [], "home": []},
    },
}


# Starter presets (Custom panel > Presets): edit, copy or delete them; each is its own take button.
PRESET_SEEDS = {
    # batting practice
    "first_pitch": {"layout": "countdown", "name": "Countdown: First Pitch", "title": "First pitch", "mode": "to", "time": "6:35 PM",
                    "sub": "{away.name} at {home.name}", "done": "PLAY BALL"},
    "gates_open": {"layout": "clockbug", "name": "Clock Bug: Gates Open", "title": "Gates open in", "mode": "to", "time": "5:30 PM", "done": "OPEN"},
    "promos": {"layout": "carousel", "name": "Promo Carousel", "title": "Tonight at the ballpark", "interval": 6,
               "text": "| Upload images or clips and list them here: link | caption"},
    "weather": {"layout": "list", "name": "Weather", "title": "Game-time weather", "sub": "{venue}",
                "text": "Temperature | {weather.temp}\nWind | {weather.wind}\nConditions | Clear"},
    "hit_it_here": {"layout": "lower", "name": "Hit It Here", "title": "Hit it here!", "sub": "Hit the sign and a fan wins a prize"},
    "trivia": {"layout": "trivia", "name": "Trivia", "title": "Trivia", "sub": "Who holds the club record for home runs in a season?",
               "foot": "Type the answer here", "reveal": False},
    "social": {"layout": "photo", "name": "Social Wall", "kicker": "#Gulls", "title": "Share your photos", "sub": "Tag us and you could be on the broadcast"},
    # pregame
    "season_series": {"layout": "two", "name": "Season Series", "title": "Season series", "col1": "{away.abbr}", "col2": "{home.abbr}",
                      "text": "Wins | 0 | 0\nRuns | 0 | 0\nLast meeting | - | -"},
    "keys": {"layout": "keys", "name": "Keys to the Game", "title": "Keys to the game",
             "text": "Work deep counts | Get ahead early\nRun the bases | Keep the ball down\nWin the late innings | Score first"},
    "milestones": {"layout": "list", "name": "Milestone Watch", "title": "Milestone watch", "text": "Player name | 2 HR from 100"},
    "anthem": {"layout": "anthem", "name": "National Anthem", "title": "Singer name", "sub": "Performing the national anthem"},
    "honoree": {"layout": "lower", "name": "Honoree", "title": "Name", "sub": "Tonight's honoree"},
    "first_pitch_honor": {"layout": "lower", "name": "Ceremonial First Pitch", "title": "Name", "sub": "Ceremonial first pitch"},
    "injuries": {"layout": "list", "name": "Injury Report", "title": "Injury report", "sub": "{home.name}", "text": "Player name | Status"},
    # in-game
    "fans": {"layout": "lower", "name": "Fan Shout-outs (Next)", "title": "Welcome", "text": "Happy birthday, Name! | Section 104\nWelcome, Group name! | Thanks for coming"},
    "fan_of_game": {"layout": "lower", "name": "Fan of the Game", "title": "Fan of the game", "sub": "Presented by our sponsor"},
    "sponsor_read": {"layout": "lower", "name": "Sponsor Read", "title": "Sponsor name", "sub": "Two lines of copy for the read"},
    "mound_visit": {"layout": "bug", "name": "Bug: Mound Visit", "title": "Mound visit"},
    "challenge": {"layout": "bug", "name": "Bug: Challenge", "title": "Play under review"},
    "ejection": {"layout": "bug", "name": "Bug: Ejection", "title": "Ejection"},
    "injury_delay": {"layout": "bug", "name": "Bug: Injury Delay", "title": "Injury delay"},
    "rain_delay": {"layout": "countdown", "name": "Rain Delay", "title": "Rain delay", "mode": "up", "sub": "Stay with us for updates"},
    "back_in": {"layout": "countdown", "name": "Back in 2:00", "title": "We'll be right back", "mode": "dur", "dur": 2, "done": "BACK SOON"},
    # postgame
    "next_game": {"layout": "next", "name": "Next Game", "title": "Next game", "sub": "Tomorrow 6:35 PM", "text": "Away starter | Home starter",
                  "qr": "", "foot": "Scan for tickets"},
    "quote": {"layout": "quote", "name": "Quote", "title": "Manager name", "kicker": "Manager", "sub": "Type the quote here."},
    # show-wide
    "open_pregame": {"layout": "open", "name": "Segment Open", "kicker": "Up next", "title": "Pregame", "sub": "{away.name} at {home.name}"},
    "highlight": {"layout": "video", "name": "Video Frame", "title": "Highlight"},
    "title_card": {"layout": "title", "name": "Title Card", "kicker": "Tonight", "title": "Title", "sub": "A line or two of text"},
}


def graphic_hash(g):
    """Same fingerprint as tools/broadcast_lib.graphic_hash (element ids and the stamp left out)."""
    import hashlib
    c = {k: v for k, v in (g or {}).items() if k not in ("_src", "presetId", "cat", "style", "sport")}
    c["elements"] = [{k: v for k, v in e.items() if k != "id"} for e in c.get("elements", [])]
    return hashlib.md5(json.dumps(c, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:16]


def upgrade_templates(user, pkg):
    """Bring saved templates up to a newer package: add graphics the package gained (but not ones the user deleted),
    and replace graphics whose fingerprint shows they were never edited. Returns (doc, list of changed ids)."""
    doc = dict(user)
    g = dict(doc.get("graphics") or {})
    known = set(doc.get("graphicsIndex") or [])
    changed = []
    for gid, pg in (pkg.get("graphics") or {}).items():
        ug = g.get(gid)
        if ug is None:
            if gid not in known:
                g[gid] = copy.deepcopy(pg)
                changed.append(gid)
        elif ug.get("_src") and graphic_hash(ug) == ug["_src"] and pg.get("_src") and ug["_src"] != pg["_src"]:
            g[gid] = copy.deepcopy(pg)
            changed.append(gid)
    doc["graphics"] = g
    if pkg.get("graphicsIndex"):
        doc["graphicsIndex"] = sorted(set(pkg["graphicsIndex"]) | known)
    return doc, changed


def preset_sig(ui):
    """What about the presets changes the graphic list: ids, layouts, names, groups (and the library switch), and colour changes."""
    pr = (ui or {}).get("presets") or {}
    return json.dumps([sorted((k, v.get("layout"), v.get("name"), v.get("autoHide")) for k, v in pr.items() if isinstance(v, dict)),
                       (ui or {}).get("library", True), (ui or {}).get("colors") or {}], sort_keys=True)


# ---- colours: every colour in a style can be swapped from the control panel (Custom > Colors).
# ui.colors = {"<style name>": {"#0a1530": "#112233", ...}}. Each listed colour is replaced wherever it appears in that
# style's graphics and theme (fills, gradient stops, text, borders, shadows, table fills), keeping its transparency.
COLOR_RE = re.compile(r"#[0-9a-fA-F]{8}(?![0-9a-zA-Z])|#[0-9a-fA-F]{6}(?![0-9a-zA-Z])|#[0-9a-fA-F]{3}(?![0-9a-zA-Z])|"
                      r"rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*(?:,\s*[\d.]+\s*)?\)")
COLOR_SKIP = ("text", "src", "name", "label", "field", "showIf", "bind", "id", "font", "font2", "body", "logo", "brandName", "brandShort",
              "openerVideo", "target", "since", "dur", "mode", "url", "interval", "done")


def color_key(m):
    """Normalised #rrggbb for a matched colour, and how to write a replacement in the same form (keeping alpha)."""
    t = m.lower()
    if t.startswith("#"):
        h = t[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return "#" + h[:6]
    nums = re.findall(r"[\d.]+", t)
    try:
        return "#%02x%02x%02x" % tuple(max(0, min(255, int(float(n)))) for n in nums[:3])
    except (TypeError, ValueError):
        return None


def color_swap(m, new):
    t = m.lower()
    if t.startswith("#"):
        h = t[1:]
        return new + (h[6:8] if len(h) == 8 else "")
    a = re.findall(r"[\d.]+", t)
    r, g, b = int(new[1:3], 16), int(new[3:5], 16), int(new[5:7], 16)
    return "rgba(%d,%d,%d,%s)" % (r, g, b, a[3]) if len(a) > 3 else "rgb(%d,%d,%d)" % (r, g, b)


def recolor_str(s, cmap):
    return COLOR_RE.sub(lambda m: color_swap(m.group(0), cmap[color_key(m.group(0))]) if color_key(m.group(0)) in cmap else m.group(0), s)


def _walk_colors(obj, fn, key=None):
    """Apply fn to every colour-bearing string in a style / columns / theme structure."""
    if isinstance(obj, dict):
        return dict((k, v if k in COLOR_SKIP else _walk_colors(v, fn, k)) for k, v in obj.items())
    if isinstance(obj, list):
        return [_walk_colors(v, fn, key) for v in obj]
    if isinstance(obj, str) and ("#" in obj or "rgb" in obj):
        return fn(obj, key)
    return obj


def recolor_graphic(d, cmap):
    d = dict(d)
    els = []
    for e in d.get("elements") or []:
        e = dict(e)
        if e.get("type") == "qr":      # QR codes stay black on white so they always scan
            els.append(e)
            continue
        for k in ("style", "columns"):
            if k in e:
                e[k] = _walk_colors(e[k], lambda s, _k: recolor_str(s, cmap))
        els.append(e)
    d["elements"] = els
    if isinstance(d.get("theme"), dict):
        d["theme"] = _walk_colors(d["theme"], lambda s, _k: recolor_str(s, cmap))
    return d


def color_map(ui, style_name):
    m = ((ui or {}).get("colors") or {}).get(style_name) or {}
    return dict((k.lower(), v.lower()) for k, v in m.items()
                if isinstance(v, str) and re.match(r"^#[0-9a-fA-F]{6}$", v) and re.match(r"^#[0-9a-fA-F]{6}$", k) and k.lower() != v.lower())


def palette(doc):
    """Every colour used in a style: [{hex, count, uses: [where]}], most used first."""
    seen = {}
    where = {"background": "panels", "fill": "boxes", "color": "text", "borderColor": "borders", "textStroke": "text outlines", "shadow": "shadows",
             "textShadow": "text shadows", "rowFill": "table rows", "altFill": "table rows", "headerFill": "table headers", "highlightFill": "highlights",
             "fillOn": "highlights", "colorOn": "highlights", "on": "bases and dots", "off": "bases and dots", "stroke": "bases", "headColor": "table headers",
             "current": "linescore", "totalFill": "linescore", "rowLine": "table lines", "headerColor": "table headers"}

    def note(s, k):
        for m in COLOR_RE.finditer(s):
            c = color_key(m.group(0))
            if not c:
                continue
            e = seen.setdefault(c, {"hex": c, "count": 0, "uses": set()})
            e["count"] += 1
            e["uses"].add(where.get(k, "theme" if k in ("primary", "accent", "text", "dim", "line", "card", "panel", "panel2") else "other"))
        return s
    for d in (doc.get("graphics") or {}).values():
        if isinstance(d, dict) and not d.get("libPkg") and not d.get("presetId"):
            for e in d.get("elements") or []:
                if e.get("type") == "qr":
                    continue
                for k in ("style", "columns"):
                    if k in e:
                        _walk_colors(e[k], note)
    _walk_colors(doc.get("theme") or {}, note)
    out = sorted(seen.values(), key=lambda e: -e["count"])
    for e in out:
        e["uses"] = sorted(e["uses"])
    return out


def strip_presets(doc):
    """Drop generated graphics (presets, other packages' library copies) so they are never saved into the user's templates."""
    doc = dict(doc)
    doc["graphics"] = dict((k, v) for k, v in (doc.get("graphics") or {}).items()
                           if not (isinstance(v, dict) and (v.get("presetId") or v.get("libPkg"))))
    return doc


# ---- categories: the Graphics panel and graphics sets group every graphic by what it is
CATEGORIES = [
    ("scorebugs", "Scorebugs", True), ("lower_batter", "Lower thirds: batters", True), ("lower_pitcher", "Lower thirds: pitchers", True),
    ("lower_other", "Lower thirds: other", False), ("players", "Player features and cards", False), ("lineups", "Lineups and defense", False),
    ("pitching", "Pitching", False), ("matchups", "Matchups and team intros", False), ("standings", "Standings", False),
    ("scores", "Scores and results", False), ("show", "Show graphics", False), ("bugs", "Corner bugs", False), ("panels", "Side panels", False),
    ("ticker", "Ticker", True), ("events", "Event stingers (fire automatically)", False), ("transitions", "Transitions and bumpers", False),
    ("podcast", "Podcast", False), ("presets", "Your presets", False), ("other", "Other", False),
]


def ops_commands(ui):
    """One-shot GAME OPS commands from the control panel, stamped with server time so every overlay agrees:
    pcCmd start / stop / reset (pitch clock), delayCmd start / stop (break clock), kCmd +1 / -1 / reset (strikeout counter)."""
    o = ui.get("ops")
    if not isinstance(o, dict):
        return
    now = int(time.time() * 1000)
    cmd = o.pop("pcCmd", None)
    if cmd:
        pc = o.get("pclock") if isinstance(o.get("pclock"), dict) else {}
        secs = max(1, ival(o.get("pcSecs"), 15))
        left = max(0, ival(pc.get("ms")) - ((now - ival(pc.get("at"))) if pc.get("running") and pc.get("at") else 0))
        if cmd == "start":
            o["pclock"] = {"ms": left if (pc.get("ms") and left > 0 and not pc.get("running")) else secs * 1000, "running": True, "at": now}
        elif cmd == "stop":
            o["pclock"] = {"ms": left, "running": False, "at": now}
        else:
            o["pclock"] = {"ms": secs * 1000, "running": False, "at": now}
    cmd = o.pop("delayCmd", None)
    if cmd == "start":
        o["delaySince"] = now
    elif cmd == "stop":
        o["delaySince"] = 0
    cmd = o.pop("kCmd", None)
    if cmd:
        o["kMode"] = "manual"
        o["kCount"] = 0 if cmd == "reset" else max(0, ival(o.get("kCount")) + (1 if cmd == "+1" else -1))
    cmd = o.pop("pitchCmd", None)
    if cmd == "clear":
        o["pitches"] = ""
    elif cmd == "undo":
        o["pitches"] = "\n".join(str(o.get("pitches") or "").split("\n")[:-1])


def category(gid, d):
    """Sort a graphic into a CATEGORIES key from its id, group and name."""
    d = d or {}
    if d.get("cat"):
        return d["cat"]
    if d.get("presetId"):
        return "presets"
    b = gid.split("__")[-1]
    g = d.get("group") or ""
    n = re.sub(r"\s*\([^)]*\)\s*$", "", (d.get("name") or "")).lower()  # drop the "(Style name)" suffix
    has = lambda *ws: any(w in b for w in ws)
    if g == "stinger" or "bumper" in b or b.startswith("tr_") or b in ("opener", "stinger"):
        return "transitions"
    if g == "ticker":
        return "ticker"
    if g in ("event", "event2"):
        return "events"
    if g == "bug":
        return "scorebugs"
    if g == "bug2":
        return "bugs"
    if "standings" in b:
        return "standings"
    if g == "panel":
        return "panels"
    if b.startswith("show_") or b in ("tonight", "road_ahead", "next_game_auto", "up_next", "bp_info", "team_title") or "show" in n.split(":")[0]:
        return "show"
    if has("matchup") or b in ("c_team_intro",):
        return "matchups"
    if g in ("lower", "note"):
        if has("pitcher"):
            return "lower_pitcher"
        if has("batter") or b in ("batter",):
            return "lower_batter"
        return "lower_other"
    if has("lineup", "defense", "dueup") or b.startswith("def_"):
        return "lineups"
    if has("sp_", "pitchers_today", "probables", "pitching"):
        return "pitching"
    if has("final", "summary", "linescore", "around", "game_info", "box_", "scoring", "performers"):
        return "scores"
    if has("tall", "card", "feature", "spotlight", "potg", "bio", "split", "leader"):
        return "players"
    return "other"


def library_packages():
    """Every package file (cached by modification time) for the cross-package library."""
    out = []
    try:
        names = sorted(f for f in os.listdir(PKG_DIR) if f.endswith(".json"))
    except OSError:
        return out
    for fn in names:
        path = os.path.join(PKG_DIR, fn)
        try:
            mt = os.path.getmtime(path)
        except OSError:
            continue
        hit = _LIB_CACHE.get(path)
        if not hit or hit[0] != mt:
            hit = (mt, load_json(path, None))
            _LIB_CACHE[path] = hit
        if hit[1] and isinstance(hit[1].get("graphics"), dict):
            out.append(hit[1])
    return out


_LIB_CACHE = {}


def with_presets(doc, ui):
    """The package plus one take-able graphic per Custom-panel preset (p_<id>), each a copy of its layout (lay_<name>)."""
    doc = strip_presets(doc or {"graphics": {}})
    own_map = color_map(ui, doc.get("name") or "Graphics")
    if own_map:
        doc["graphics"] = dict((k, recolor_graphic(v, own_map) if isinstance(v, dict) else v) for k, v in doc["graphics"].items())
        doc["theme"] = _walk_colors(doc.get("theme") or {}, lambda s, _k: recolor_str(s, own_map))
    g = doc["graphics"]
    for pid, p in sorted(((ui or {}).get("presets") or {}).items()):
        if not isinstance(p, dict):
            continue
        lay = g.get("lay_" + str(p.get("layout") or ""))
        if not lay:
            continue
        d = copy.deepcopy(lay)
        d.pop("layout", None)
        d["presetId"] = pid
        d["name"] = p.get("name") or d.get("name", pid)
        if p.get("autoHide") not in (None, ""):
            try:
                d["autoHide"] = float(p["autoHide"])
            except (TypeError, ValueError):
                pass
        g["p_" + pid] = d
    # Library: the other packages' graphics, each keeping its own look (theme), so a Retro scorebug can sit beside
    # Night Game graphics. Ids are "<package>__<id>". Turn off with ui.library = false.
    if (ui or {}).get("library", True):
        for pk in library_packages():
            if pk.get("name") == doc.get("name"):
                continue
            ps = slug(pk.get("name") or "pkg")
            for gid, pd in pk["graphics"].items():
                if pd.get("layout") or gid.startswith("lay_"):
                    continue
                d = copy.deepcopy(pd)
                d["libPkg"] = pk.get("name")
                d["theme"] = pk.get("theme") or {}
                pm = color_map(ui, pk.get("name"))
                if pm:
                    d = recolor_graphic(d, pm)
                if str(pk.get("name", "")).lower() not in str(d.get("name", "")).lower():
                    d["name"] = "%s (%s)" % (d.get("name") or gid, pk.get("name"))
                g["%s__%s" % (ps, gid)] = d
    own = doc.get("name") or "Graphics"
    for gid in list(g):
        if isinstance(g[gid], dict):
            g[gid] = dict(g[gid], cat=category(gid, g[gid]), style=g[gid].get("libPkg") or own)
            g[gid]["sport"] = sport_of(gid, g[gid])
    return doc


# ---- style sets: one graphics set per style (package), made automatically, with one graphic for each single-choice type
SPORT_PREFIX = {"basketball": "bk_", "football": "fb_", "hockey": "hk_"}
STYLE_PICK = {"scorebugs": "scorebug", "lower_batter": "batter", "lower_pitcher": "pitcher", "ticker": "ticker"}


def style_sets(tpl):
    """{"style_<slug>": {name, gids, auto}} for every style in the templates (the loaded package plus the library).
    Single-choice types (scorebug, batter / pitcher lower third, ticker) get one graphic per sport."""
    single = dict((k, one) for k, _l, one in CATEGORIES)
    by = {}
    presets = []
    for gid, d in sorted(((tpl or {}).get("graphics") or {}).items()):
        if not isinstance(d, dict) or d.get("layout"):
            continue
        if d.get("presetId"):
            presets.append(gid)
            continue
        by.setdefault(d.get("style") or "Graphics", []).append((gid, d.get("cat") or "other", d.get("sport") or "all"))
    out = {}
    for style, items in by.items():
        gids, taken = [], {}
        for key in sorted(set((c, sp) for _g, c, sp in items if single.get(c))):
            cands = [gid for gid, c, sp in items if (c, sp) == key]
            want = STYLE_PICK.get(key[0])
            if key[1] in SPORTS:
                want = SPORT_PREFIX[key[1]] + want
            taken[key] = next((x for x in cands if x.split("__")[-1] == want), cands[0])
        for gid, cat, sp in items:
            if single.get(cat) and taken.get((cat, sp)) != gid:
                continue
            gids.append(gid)
        out["style_" + slug(style)] = {"name": "%s style" % style, "gids": gids + presets, "auto": True}
    return out


def deep_merge(base, patch):
    """Recursively merge patch into base (in place) and return base."""
    for k, v in (patch or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return copy.deepcopy(fallback)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def log(msg):
    line = "[Baseball Graphics] " + str(msg)
    if IN_OBS:
        try:
            obs.script_log(obs.LOG_INFO, line)
            return
        except Exception:
            pass
    print(line, flush=True)


# ---------------------------------------------------------------------------
# HTTP client helpers
# ---------------------------------------------------------------------------
class FetchError(Exception):
    pass


IMG_EXT_BY_TYPE = {"image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/webp": ".webp", "image/gif": ".gif",
                   "image/svg+xml": ".svg"}


def sniff_image_ext(data, ctype=""):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if b"<svg" in data[:2048]:
        return ".svg"
    return IMG_EXT_BY_TYPE.get(ctype, "")


class TTLCache:
    def __init__(self):
        self._d = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            v = self._d.get(key)
            if v and v[0] > time.time():
                return v[1]
            return None

    def set(self, key, value, ttl):
        with self._lock:
            self._d[key] = (time.time() + ttl, value)

    def clear(self):
        with self._lock:
            self._d.clear()


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------
POS_WORDS = {
    "PITCHER": "P", "CATCHER": "C", "FIRST BASE": "1B", "FIRST BASEMAN": "1B",
    "SECOND BASE": "2B", "SECOND BASEMAN": "2B", "THIRD BASE": "3B", "THIRD BASEMAN": "3B",
    "SHORTSTOP": "SS", "SHORT STOP": "SS", "LEFT FIELD": "LF", "LEFT FIELDER": "LF",
    "CENTER FIELD": "CF", "CENTER FIELDER": "CF", "RIGHT FIELD": "RF", "RIGHT FIELDER": "RF",
    "DESIGNATED HITTER": "DH", "OUTFIELDER": "OF", "OUTFIELD": "OF", "INFIELDER": "IF",
    "INFIELD": "IF", "PINCH HITTER": "PH", "PINCH RUNNER": "PR", "UTILITY": "UT",
    "1": "P", "2": "C", "3": "1B", "4": "2B", "5": "3B", "6": "SS", "7": "LF", "8": "CF", "9": "RF",
    "10": "DH",
}
FIELD_POS = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]


def norm_pos(p):
    if p is None:
        return ""
    s = str(p).strip().replace("_", " ").upper()
    return POS_WORDS.get(s, s if len(s) <= 3 else s[:3])


def ival(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def split_name(full, first=None, last=None):
    full = " ".join((full or "").split())
    first = " ".join((first or "").split())
    last = " ".join((last or "").split())
    if not full:
        full = (first + " " + last).strip()
    if full and not last:
        parts = full.split()
        last = parts[-1] if parts else ""
        first = " ".join(parts[:-1]) if len(parts) > 1 else first
    return full, first, last


def outs_to_ip(outs):
    outs = max(0, ival(outs))
    return "%d.%d" % (outs // 3, outs % 3)


def today_line(ab, h, hr=0, rbi=0, bb=0, k=0, d2=0, d3=0, hbp=0, sb=0):
    if ab is None:
        return ""
    parts = []
    if hr:
        parts.append(("%d HR" % hr) if hr > 1 else "HR")
    if d3:
        parts.append(("%d 3B" % d3) if d3 > 1 else "3B")
    if d2:
        parts.append(("%d 2B" % d2) if d2 > 1 else "2B")
    if rbi:
        parts.append("%d RBI" % rbi)
    if bb:
        parts.append(("%d BB" % bb) if bb > 1 else "BB")
    if hbp:
        parts.append("HBP")
    if sb:
        parts.append(("%d SB" % sb) if sb > 1 else "SB")
    if k:
        parts.append(("%d K" % k) if k > 1 else "K")
    base = "%d-%d" % (ival(h), ival(ab))
    return base + (", " + ", ".join(parts) if parts else "")


def empty_team():
    return {"id": "", "name": "", "abbr": "", "runs": 0, "hits": 0, "errors": 0, "lob": 0,
            "record": "", "lineup": [], "defense": {}, "pitchers": [], "sp": {}, "dueUp": []}


def empty_player():
    return {"id": "", "name": "", "first": "", "last": "", "number": "", "pos": "",
            "bats": "", "throws": "", "photo": "",
            "today": {}, "season": {}}


TWO_WORD_NICKS = ("flying boxcars", "ghost peppers", "blue crabs", "dirty birds", "red sox", "white sox", "blue jays", "iron birds", "river dogs",
                  "sea dogs", "blue rocks", "rubber ducks", "tin caps", "sod poodles", "jumbo shrimp", "yard goats", "baby cakes", "big train")


def split_team_name(name, ov=None):
    """("Riverside", "Otters") from "Riverside Otters"; Teams > City / Nickname overrides win."""
    ov = ov or {}
    words = name.split()
    n = 2 if len(words) > 2 and " ".join(words[-2:]).lower() in TWO_WORD_NICKS else 1
    city = " ".join(words[:-n]) if len(words) > n else ""
    nick = " ".join(words[-n:]) if words else ""
    return ov.get("city") or city, ov.get("nick") or nick


def bio_line(p):
    """6'0" | 190 lbs | Age 31 | B/T R/R | La Romana, DR"""
    bits = []
    if p.get("height"):
        bits.append(str(p["height"]))
    if p.get("weight"):
        bits.append("%s lbs" % p["weight"])
    if p.get("age"):
        bits.append("Age %s" % p["age"])
    if p.get("bats") or p.get("throws"):
        bits.append("B/T %s/%s" % (p.get("bats") or "-", p.get("throws") or "-"))
    if p.get("hometown"):
        bits.append(p["hometown"])
    return " | ".join(bits)


def split_rows(ui, g):
    """Rows for the split stat card: typed "label, a, b" lines, else the batter's season next to tonight."""
    sp = ui.get("split") or {}
    rows = []
    for line in str(sp.get("rows") or "").splitlines():
        parts = [x.strip() for x in line.split(",")]
        if parts and parts[0]:
            rows.append({"label": parts[0], "a": parts[1] if len(parts) > 1 else "", "b": parts[2] if len(parts) > 2 else ""})
    picked = (g.get("picked") or {}).get("bat") if ((ui.get("pick") or {}).get("on")) else None
    p = picked or g.get("batter") or {}
    out = {"title": sp.get("title") or p.get("name", ""), "sub": sp.get("sub", ""), "col1": sp.get("col1", ""), "col2": sp.get("col2", ""),
           "foot": sp.get("foot", ""), "photo": p.get("photo", ""), "custom": bool(rows)}
    sp = p.get("splits") or {}
    if not rows and sp.get("vsL") and sp.get("vsR"):
        L_, R_ = sp["vsL"], sp["vsR"]
        rows = [{"label": "At-bats", "a": str(L_.get("ab", "")), "b": str(R_.get("ab", ""))},
                {"label": "Average", "a": L_.get("avg") or "-", "b": R_.get("avg") or "-"},
                {"label": "On-base %", "a": L_.get("obp") or "-", "b": R_.get("obp") or "-"},
                {"label": "Slugging", "a": L_.get("slg") or "-", "b": R_.get("slg") or "-"},
                {"label": "Home runs", "a": str(L_.get("hr", "")), "b": str(R_.get("hr", ""))},
                {"label": "RBI", "a": str(L_.get("rbi", "")), "b": str(R_.get("rbi", ""))}]
        out["col1"] = out["col1"] or "vs LHP"
        out["col2"] = out["col2"] or "vs RHP"
    if not rows:
        s, t = p.get("season") or {}, p.get("today") or {}
        dash = lambda v: "-" if v in (None, "") else str(v)
        tavg = fmt_rate(float(t["h"]) / float(t["ab"])) if t.get("ab") not in (None, "", 0, "0") and t.get("h") not in (None, "") else "-"
        rows = [{"label": "At-bats", "a": dash(s.get("ab")), "b": dash(t.get("ab"))},
                {"label": "Hits", "a": dash(s.get("h")), "b": dash(t.get("h"))},
                {"label": "Home runs", "a": dash(s.get("hr")), "b": dash(t.get("hr"))},
                {"label": "RBI", "a": dash(s.get("rbi")), "b": dash(t.get("rbi"))},
                {"label": "Average", "a": fmt_rate(s.get("avg")) if s.get("avg") not in (None, "") else "-", "b": tavg}]
        out["col1"] = out["col1"] or "Season"
        out["col2"] = out["col2"] or "Tonight"
    out["rows"] = rows[:6]
    return out


PLAY_WORDS = {"HR": ("Home run", "Home runs"), "BB": ("Walk", "Walks"), "K": ("Strikeout", "Strikeouts"), "2B": ("Double", "Doubles"),
              "3B": ("Triple", "Triples"), "1B": ("Single", "Singles"), "SB": ("Stolen base", "Stolen bases"), "R": ("Run", "Runs"),
              "RBI": ("RBI", "RBI"), "SF": ("Sac fly", "Sac flies"), "HBP": ("Hit by pitch", "Hit by pitch"), "CS": ("Caught stealing", "Caught stealing")}


def play_words(notes):
    """'2 HR, RBI, BB' -> '2 Home runs, RBI, Walk' for the lineup-with-results card."""
    out = []
    for part in [x.strip() for x in str(notes or "").split(",") if x.strip()]:
        m = re.match(r"^(\d+)\s+(.+)$", part)
        n, k = (int(m.group(1)), m.group(2)) if m else (1, part)
        w = PLAY_WORDS.get(k.upper())
        out.append(("%d %s" % (n, w[1]) if n > 1 else w[0]) if w else part)
    return ", ".join(out)


def typed_rows(text, n=3):
    """'a | b | c' lines -> [[a, b, c], ...] (Custom panel lists)."""
    rows = []
    for line in str(text or "").splitlines():
        parts = [x.strip() for x in line.split("|")]
        if any(parts):
            rows.append(parts + [""] * (n - len(parts)))
    return rows


def show_lists(ui, g):
    """Tonight's schedule, series probables and the lineup feature panel, from the Custom panel."""
    sc = ui.get("schedule") or {}
    sched = [{"time": r[0], "show": r[1], "talent": "\n".join(x.strip() for x in r[2].split(",") if x.strip())}
             for r in typed_rows(sc.get("rows"), 3)][:4]
    photos = {}
    for side in ("away", "home"):
        for p in list(g[side].get("roster", [])) + list(g[side].get("pitchers", [])) + list(g[side].get("lineup", [])):
            if p.get("photo") and p.get("name"):
                photos[slug(p["name"])] = p["photo"]
    pr = ui.get("probables") or {}
    probs = []
    for r in typed_rows(pr.get("rows"), 3)[:4]:
        nm = r[0].split()
        probs.append({"name": r[0], "first": " ".join(nm[:-1]), "last": nm[-1] if nm else "", "line": r[1], "line2": r[2],
                      "photo": photos.get(slug(r[0]), "")})
    g["schedule"] = {"title": sc.get("title", ""), "sub": sc.get("sub", ""), "foot": sc.get("foot", ""), "rows": sched}
    g["probables"] = {"title": pr.get("title", ""), "sub": pr.get("sub", ""), "foot": pr.get("foot", ""), "rows": probs}
    notes = ui.get("notes") or {}
    picked = (g.get("picked") or {}).get("bat") if (ui.get("pick") or {}).get("on") else None
    for side in ("away", "home"):
        t = g[side]
        f = picked if (picked and (g.get("picked") or {}).get("side") == side) else None
        if not f:
            f = next((p for p in (t.get("topHitters") or []) if p.get("photo")), None) or (t.get("topHitters") or [{}])[0] if t.get("topHitters") else {}
        s_ = (f or {}).get("season") or f or {}
        dflt = " | ".join(x for x in [("%s AVG" % fmt_rate(s_.get("avg"))) if s_.get("avg") not in (None, "") else "",
                                      ("%s HR" % s_.get("hr")) if s_.get("hr") not in (None, "") else "",
                                      ("%s RBI" % s_.get("rbi")) if s_.get("rbi") not in (None, "") else ""] if x)
        fname = slug((f or {}).get("name", ""))
        for r in t.get("lineup", []):
            r["isFeature"] = bool(fname) and slug(r.get("name")) == fname
        t["feature"] = {"name": (f or {}).get("name", ""), "photo": (f or {}).get("photo", ""), "pos": (f or {}).get("pos", ""),
                        "number": (f or {}).get("number", ""),
                        "title": notes.get("lfTitle") or ("This season" if dflt else ""), "line": notes.get("lfLine") or dflt}


def road_ahead(ui):
    """Two-week calendar cells from typed lines "29 | @MIL | W 4-2" (blank opponent = off day), Monday first."""
    ra = ui.get("roadAhead") or {}
    cells = []
    for r in typed_rows(ra.get("rows"), 3)[:14]:
        opp = r[1].strip()
        away = opp.startswith("@")
        abbr = opp.lstrip("@").strip()
        cells.append({"day": r[0], "opp": abbr, "away": away, "home": bool(abbr) and not away, "off": not abbr,
                      "logo": media_for("logos", abbr, abbr) if abbr else "", "info": r[2]})
    return {"title": ra.get("title", ""), "cells": cells}


def around_league(scoreboard, g):
    """Today's other games as tiles (from the league scoreboard the ticker uses)."""
    me = {slug(g["away"].get("abbr")), slug(g["home"].get("abbr"))}
    out = []
    for sg in scoreboard or []:
        if slug(sg.get("away")) in me and slug(sg.get("home")) in me:
            continue
        out.append({"away": sg.get("away", ""), "home": sg.get("home", ""),
                    "awayRuns": "" if sg.get("awayRuns") is None else sg.get("awayRuns"), "homeRuns": "" if sg.get("homeRuns") is None else sg.get("homeRuns"),
                    "state": sg.get("state", ""), "live": sg.get("status") == "LIVE",
                    "awayLogo": media_for("logos", sg.get("away"), sg.get("away")) or "", "homeLogo": media_for("logos", sg.get("home"), sg.get("home")) or ""})
    return out[:8]


def umpire_rows(text, feed):
    """Umpire crew: typed lines "HP, Sam Rivers (CC), 4th Wild Card" win."""
    rows = []
    for line in str(text or "").splitlines():
        parts = [x.strip() for x in line.split(",", 2)]
        if parts and parts[0]:
            if len(parts) == 1:
                parts = ["", parts[0]]
            rows.append({"pos": parts[0].upper(), "name": parts[1] if len(parts) > 1 else "", "note": parts[2] if len(parts) > 2 else ""})
    if not rows:
        rows = [dict(r) for r in feed if r.get("name")]
    order = {"HP": 0, "1B": 1, "2B": 2, "3B": 3, "LF": 4, "RF": 5}
    rows.sort(key=lambda r: order.get(r["pos"], 9))
    return rows[:6]


PLACE_WORDS = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"]


def team_places(g):
    """Each game team's standing in its division: rank, "Third Place" and games back (team intro card)."""
    for side in ("away", "home"):
        t = g.get(side) or {}
        t["rank"], t["place"], t["gb"], t["division"] = "", "", "", ""
        for grp in (g.get("standings") or {}).get("groups", []):
            for i, row in enumerate(grp.get("teams", [])):
                if slug(row.get("name")) == slug(t.get("name")) or (row.get("abbr") and slug(row.get("abbr")) == slug(t.get("abbr"))):
                    r = ival(row.get("rank"), i + 1)
                    t["rank"] = r
                    t["place"] = ("%s Place" % PLACE_WORDS[r - 1]) if 0 < r <= len(PLACE_WORDS) else "%s Place" % _ord(r)
                    t["gb"] = row.get("gb") or ""
                    t["division"] = grp.get("name", "")
                    if not t.get("record") and row.get("w") is not None:
                        t["record"] = "%s-%s" % (row.get("w"), row.get("l"))
                    break
            if t["place"]:
                break


def empty_extras():
    return {"decisions": {}, "lastPlay": {}, "venue": "", "duration": "", "recentPlays": [], "pitch": {"speed": "", "type": ""}, "hit": {"ev": ""}, "playLog": [],
            "weather": {"temp": "", "wind": ""}, "attendance": "", "scorer": "", "officials": [], "scheduledInnings": 9, "tiebreak": ""}


def _ord(n):
    return "%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def empty_game():
    return {
        "source": "", "status": "PRE", "statusText": "", "inning": 1, "half": "top",
        "balls": 0, "strikes": 0, "outs": 0, "bases": {"1": False, "2": False, "3": False},
        "away": empty_team(), "home": empty_team(),
        "batter": empty_player(), "pitcher": empty_player(),
        "linescore": {"innings": 9, "away": [], "home": []},
        **empty_extras(),
    }


def compute_due_up(team, batter_id, is_batting, last_slot):
    lineup = [p for p in team.get("lineup", []) if p.get("name")]
    if not lineup:
        return []
    lineup = sorted(lineup, key=lambda p: ival(p.get("slot"), 99))
    idx = None
    if is_batting and batter_id:
        for i, p in enumerate(lineup):
            if p.get("id") == batter_id:
                idx = i
                break
    if idx is None:
        if last_slot:
            for i, p in enumerate(lineup):
                if ival(p.get("slot")) == last_slot:
                    idx = (i + 1) % len(lineup)
                    break
        if idx is None:
            idx = 0
    return [lineup[(idx + n) % len(lineup)] for n in range(min(3, len(lineup)))]


MEDIA_DIRS = {"photos": os.path.join(BASE_DIR, "media", "photos"),
              "logos": os.path.join(BASE_DIR, "media", "logos"),
              "backgrounds": os.path.join(BASE_DIR, "media", "backgrounds"),
              "videos": os.path.join(BASE_DIR, "media", "videos"),
              "sponsors": os.path.join(BASE_DIR, "media", "sponsors"),
              "fonts": os.path.join(BASE_DIR, "media", "fonts")}
FONT_EXT = (".ttf", ".otf", ".woff", ".woff2")
MEDIA_EXT = (".png", ".webp", ".jpg", ".jpeg", ".gif", ".svg", ".webm", ".mp4", ".mov", ".ttf", ".otf", ".woff", ".woff2")
for _ext, _type in ((".woff2", "font/woff2"), (".woff", "font/woff"), (".ttf", "font/ttf"), (".otf", "font/otf"), (".webm", "video/webm"), (".mp4", "video/mp4"), (".svg", "image/svg+xml"), (".webp", "image/webp")):
    mimetypes.add_type(_type, _ext)
_media_cache = {"t": 0, "files": {}}


def slug(s):
    """alex-rivera style key. Accents are folded (Perez = Pérez) so file names match player names."""
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def media_index():
    """Map of kind -> {slug: url} for files dropped in media/photos, media/logos, media/backgrounds."""
    if time.time() - _media_cache["t"] < 5:
        return _media_cache["files"]
    out = {}
    for kind, d in MEDIA_DIRS.items():
        out[kind] = {}
        try:
            for fn in os.listdir(d):
                stem, ext = os.path.splitext(fn)
                if ext.lower() in MEDIA_EXT:
                    out[kind][slug(stem)] = "/media/%s/%s" % (kind, urllib.parse.quote(fn))
        except OSError:
            pass
    _media_cache.update(t=time.time(), files=out)
    return out


def font_list():
    """Font files in media/fonts. The family name is the file name without its extension,
    e.g. media/fonts/Gotham Bold.otf -> font family "Gotham Bold"."""
    out = []
    try:
        for fn in sorted(os.listdir(MEDIA_DIRS["fonts"])):
            stem, ext = os.path.splitext(fn)
            if ext.lower() in FONT_EXT:
                out.append({"family": stem, "url": "/media/fonts/" + urllib.parse.quote(fn),
                            "format": {".ttf": "truetype", ".otf": "opentype", ".woff": "woff", ".woff2": "woff2"}[ext.lower()]})
    except OSError:
        pass
    return out


def media_for(kind, *keys):
    idx = media_index().get(kind, {})
    for k in keys:
        s = slug(k)
        if s and s in idx:
            return idx[s]
    return ""


def photo_pattern_url(pattern, p, team_abbr):
    if not pattern or not p.get("name"):
        return ""
    q = lambda v: urllib.parse.quote(str(v or ""))
    first, last = p.get("first") or "", p.get("last") or ""
    try:
        return pattern.format(slug=q(slug(p.get("name"))), first=q(first), last=q(last), name=q(p.get("name")),
                              number=q(p.get("number")), team=q(str(team_abbr or "").lower()), id=q(p.get("id")),
                              first_lower=q(first.lower()), last_lower=q(last.lower()))
    except (KeyError, IndexError, ValueError):
        return ""


def resolve_photo(p, team_abbr, cfg):
    """Photo priority: assigned in the control panel > uploaded/local file > URL pattern > data feed."""
    if not isinstance(p, dict):
        return
    if "feedPhoto" not in p:
        p["feedPhoto"] = p.get("photo") or ""
    assigned = (cfg.get("photo_assign") or {}).get(slug(p.get("name")))
    if assigned:
        p["photo"], p["photoSource"] = assigned, "assigned"
        return
    num = str(p.get("number") or "")
    local = media_for("photos", p.get("name"), ("%s-%s" % (team_abbr, num)) if (team_abbr and num) else "")
    pat = photo_pattern_url(cfg.get("photo_pattern", ""), p, team_abbr)
    if local:
        p["photo"], p["photoSource"] = local, "uploaded"
    elif pat:
        p["photo"], p["photoSource"] = pat, "pattern"
    elif p["feedPhoto"]:
        p["photo"], p["photoSource"] = p["feedPhoto"], "feed"
    else:
        p["photo"], p["photoSource"] = "", ""


def fmt_rate(v, d=3):
    if v in (None, ""):
        return ""
    try:
        f = float(v)
    except Exception:
        return str(v)
    s = ("%." + str(d) + "f") % f
    return s[1:] if d == 3 and 0 <= f < 1 else s


def card_rows(player, kind):
    """Label/value rows for season stat cards. Only stats the feed actually supplied are listed."""
    s = player.get("season") or {}
    have = lambda k: s.get(k) not in (None, "")
    rows = []

    def add(label, value):
        rows.append({"label": label, "value": str(value)})
    if kind == "bat":
        if have("avg"): add("Average", fmt_rate(s["avg"]))
        if have("hr"): add("Home Runs", s["hr"])
        if have("rbi"): add("RBI", s["rbi"])
        if have("ops"): add("OPS", fmt_rate(s["ops"]))
        if have("obp"): add("On-Base %", fmt_rate(s["obp"]))
        if have("slg"): add("Slugging", fmt_rate(s["slg"]))
        if have("h"): add("Hits", s["h"])
        if have("sb"): add("Stolen Bases", s["sb"])
    else:
        if have("g") and have("gs"): add("Games/Starts", "%s/%s" % (s["g"], s["gs"]))
        elif have("gs"): add("Starts", s["gs"])
        if have("w") and have("l"): add("Record", "%s-%s" % (s["w"], s["l"]))
        if have("era"): add("ERA", fmt_rate(s["era"], 2))
        if have("ip"): add("Innings", s["ip"])
        if have("h"): add("Hits", s["h"])
        if have("k") and have("bb"): add("K/BB", "%s/%s" % (s["k"], s["bb"]))
        if have("oppAvg"): add("Opp. AVG", fmt_rate(s["oppAvg"]))
        if have("whip"): add("WHIP", fmt_rate(s["whip"], 2))
    return rows


def finalize(game, cfg, memory):
    """Apply team overrides and compute the derived fields every template can bind to."""
    g = game
    g["seasonYear"] = str(cfg.get("season_year") or datetime.date.today().year)
    for side in ("away", "home"):
        t = g.setdefault(side, empty_team())
        ov = cfg.get("teams", {}).get(side, {})
        if ov.get("name"):
            t["name"] = ov["name"]
        if ov.get("abbr"):
            t["abbr"] = ov["abbr"]
        if not t.get("abbr"):
            t["abbr"] = (t.get("name") or side)[:3].upper()
        t["color"] = ov.get("color") or "#333333"
        t["color2"] = ov.get("color2") or "#FFFFFF"
        # Logo priority: control-panel URL, then media/logos/<abbr or name>.png, then the feed.
        t["logo"] = ov.get("logo") or media_for("logos", t.get("abbr"), t.get("name")) or t.get("logo", "")
        t["bg"] = ov.get("bg") or media_for("backgrounds", t.get("abbr"), t.get("name")) or ""
        t["side"] = side
        t["city"], t["nick"] = split_team_name(t.get("name") or "", ov)
        for k in ("runs", "hits", "errors", "lob"):
            t[k] = ival(t.get(k), 0)
    half = (g.get("half") or "top").lower()
    if half.startswith("bot"):
        half = "bottom"
    elif half.startswith("mid"):
        half = "middle"
    elif half.startswith("end"):
        half = "end"
    else:
        half = "top"
    g["half"] = half
    inning = ival(g.get("inning"), 1) or 1
    g["inning"] = inning
    g["arrow"] = {"top": "▲", "bottom": "▼"}.get(half, "")
    g["halfShort"] = {"top": "TOP", "bottom": "BOT", "middle": "MID", "end": "END"}[half]
    g["inningLabel"] = "%s %d" % (g["halfShort"], inning)
    suffix = "th" if 10 <= inning % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(inning % 10, "th")
    g["inningOrd"] = "%d%s" % (inning, suffix)
    g["halfLong"] = {"top": "TOP", "bottom": "BOTTOM", "middle": "MIDDLE", "end": "END"}[half]
    # Half-inning sponsor key: the half being played, or the next one during a break (T1..B9, TX/BX for extras).
    nxt_top = half in ("top", "end")
    n = inning + 1 if half == "end" else inning
    g["halfKey"] = ("T" if nxt_top else "B") + (str(n) if n <= 9 else "X")
    g["nextHalfLabel"] = ("TOP" if nxt_top else "BOTTOM") + " " + ("%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")))
    g["balls"] = ival(g.get("balls"))
    g["strikes"] = ival(g.get("strikes"))
    g["outs"] = ival(g.get("outs"))
    g["count"] = "%d-%d" % (g["balls"], g["strikes"])
    g["outsWord"] = "OUT" if g["outs"] == 1 else "OUTS"
    b = g.get("bases") or {}
    g["bases"] = {"1": bool(b.get("1")), "2": bool(b.get("2")), "3": bool(b.get("3"))}
    g["runnersOn"] = sum(1 for v in g["bases"].values() if v)
    st = (g.get("status") or "PRE").upper()
    g["status"] = st
    g["isFinal"] = st == "FINAL"
    g["isLive"] = st == "LIVE"
    g["isPre"] = st == "PRE"
    g["inPlay"] = not g["isFinal"] and not g["isPre"]
    if not g.get("statusText"):
        g["statusText"] = {"FINAL": "FINAL", "PRE": "PREGAME"}.get(st, g["inningLabel"])
    # Middle of an inning: home bats next. End of an inning: away bats next.
    batting = "home" if half in ("bottom", "middle") else "away"
    g["battingSide"] = batting
    g["fieldingSide"] = "away" if batting == "home" else "home"
    g["batting"] = {"abbr": g[batting]["abbr"], "name": g[batting]["name"], "color": g[batting]["color"],
                    "color2": g[batting]["color2"], "logo": g[batting]["logo"], "runs": g[batting]["runs"],
                    "city": g[batting].get("city", ""), "nick": g[batting].get("nick", "")}
    fs = g["fieldingSide"]
    g["fielding"] = {"abbr": g[fs]["abbr"], "name": g[fs]["name"], "color": g[fs]["color"],
                     "color2": g[fs]["color2"], "logo": g[fs]["logo"], "runs": g[fs]["runs"],
                     "city": g[fs].get("city", ""), "nick": g[fs].get("nick", "")}
    # Leader / margin helpers
    a, h = g["away"]["runs"], g["home"]["runs"]
    g["leader"] = "away" if a > h else ("home" if h > a else "")
    # Current player flags, due up
    bid = (g.get("batter") or {}).get("id")
    pid = (g.get("pitcher") or {}).get("id")
    if bid:
        for p in g[batting].get("lineup", []):
            if p.get("id") == bid:
                memory["last_slot_" + batting] = ival(p.get("slot"))
    # Headshots: uploaded file (media/photos) > URL pattern > data feed.
    resolve_photo(g.get("batter"), g[batting].get("abbr", ""), cfg)
    resolve_photo(g.get("pitcher"), g[g["fieldingSide"]].get("abbr", ""), cfg)
    b = g.get("batter") or {}
    b["slot"] = ""
    for p in g[batting].get("lineup", []):
        if bid and p.get("id") == bid:
            b["slot"] = p.get("slot", "")
    bt = b.get("today") or {}
    b["today"] = bt
    bt["hab"] = ("%d-%d" % (ival(bt.get("h")), ival(bt.get("ab")))) if bt.get("ab") not in (None, "") else ""
    if not bt["hab"] and bt.get("line"):
        bt["hab"] = str(bt["line"]).split(",")[0]
    b["card"] = card_rows(b, "bat")
    p_ = g.get("pitcher") or {}
    p_["card"] = card_rows(p_, "pit")
    for side in ("away", "home"):
        t = g[side]
        ab = t.get("abbr", "")
        if not t.get("roster"):
            seen, roster = set(), []
            for p in list(t.get("lineup", [])) + list(t.get("pitchers", [])):
                k = slug(p.get("name"))
                if k and k not in seen:
                    seen.add(k)
                    roster.append({k2: p.get(k2, "") for k2 in ("id", "name", "first", "last", "number", "pos", "photo")})
            t["roster"] = roster
        # Make sure the current batter / pitcher can always be given a photo, even if the roster feed missed them.
        names_in = {slug(r.get("name")) for r in t["roster"]}
        for who, sd in (("batter", batting), ("pitcher", g["fieldingSide"])):
            pl = g.get(who) or {}
            if sd == side and pl.get("name") and slug(pl["name"]) not in names_in:
                t["roster"].append({k2: pl.get(k2, "") for k2 in ("id", "name", "first", "last", "number", "pos", "photo")})
        t["roster"] = sorted(t["roster"], key=lambda r: (str(r.get("last") or r.get("name") or "")).lower())
        for p in list(t.get("lineup", [])) + list(t.get("pitchers", [])) + list(t.get("roster", [])):
            resolve_photo(p, ab, cfg)
        for p in t.get("lineup", []):
            p["isCurrent"] = bool(bid) and p.get("id") == bid and side == batting
        for p in t.get("pitchers", []):
            p["isCurrent"] = bool(pid) and p.get("id") == pid
        t["dueUp"] = compute_due_up(t, bid, side == batting, memory.get("last_slot_" + side))
        t["lineupCount"] = len(t.get("lineup", []))
    ls = g.setdefault("linescore", {"innings": 9, "away": [], "home": []})
    n = max(9, len(ls.get("away", [])), len(ls.get("home", [])), inning)
    ls["innings"] = n
    for side in ("away", "home"):
        row = list(ls.get(side, []))
        row = [("" if v is None else v) for v in row]
        row += [""] * (n - len(row))
        ls[side] = row[:n]
    derive_extras(g)
    trackman_enrich(g)
    g["updated"] = time.time()
    return g


# ---------------------------------------------------------------- TrackMan import (spray charts, batted-ball and pitch data)
TM_PATH = os.path.join(USER_DIR, "trackman.json")
_TM = {"mt": None, "data": {}}


def tm_key(name):
    """'Last, First' or 'First Last' -> 'first last' (letters only) so TrackMan names match roster names."""
    n = str(name or "").strip()
    if "," in n:
        a, b = n.split(",", 1)
        n = b.strip() + " " + a.strip()
    return re.sub(r"[^a-z ]", "", n.lower()).strip()


def trackman_import(csv_text, replace=False):
    """Read a TrackMan CSV export (one or many games) and keep, per batter, balls in play (direction, distance, result,
    exit speed, launch angle) and, per pitcher, pitch types with speeds. Returns counts."""
    import csv
    import io
    rows = list(csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff"))))
    if not rows:
        raise ValueError("No rows found. Export the game or season CSV from TrackMan and upload that file.")
    cols = set(rows[0].keys())
    if not ({"Batter", "Pitcher"} <= cols):
        raise ValueError("This does not look like a TrackMan CSV (no Batter / Pitcher columns).")
    data = {} if replace else load_json(TM_PATH, {})
    bat, pit = data.setdefault("batters", {}), data.setdefault("pitchers", {})
    seen = set(data.get("seen") or [])
    fnum = lambda v: float(v) if str(v or "").strip() not in ("", "NaN", "nan") else None
    added = 0
    for r in rows:
        uid = r.get("PitchUID") or "%s|%s|%s|%s" % (r.get("Date"), r.get("Inning"), r.get("PAofInning"), r.get("PitchofPA"))
        if uid in seen:
            continue
        seen.add(uid)
        added += 1
        bk, pk = tm_key(r.get("Batter")), tm_key(r.get("Pitcher"))
        ev, la, dist, dirn = fnum(r.get("ExitSpeed")), fnum(r.get("Angle")), fnum(r.get("Distance")), fnum(r.get("Direction"))
        res = (r.get("PlayResult") or "").strip()
        if bk and r.get("PitchCall") == "InPlay":
            b = bat.setdefault(bk, {"name": r.get("Batter"), "bip": []})
            b["bip"].append({"d": round(dirn, 1) if dirn is not None else None, "f": round(dist) if dist is not None else None,
                             "ev": round(ev, 1) if ev is not None else None, "la": round(la, 1) if la is not None else None, "r": res,
                             "date": r.get("Date", "")})
            b["bip"] = b["bip"][-400:]
        spd = fnum(r.get("RelSpeed"))
        if pk and spd:
            pp = pit.setdefault(pk, {"name": r.get("Pitcher"), "types": {}})
            t = (r.get("TaggedPitchType") or r.get("AutoPitchType") or "Other").strip() or "Other"
            ty = pp["types"].setdefault(t, {"n": 0, "sum": 0.0, "max": 0.0})
            ty["n"] += 1
            ty["sum"] += spd
            ty["max"] = max(ty["max"], spd)
    data["seen"] = sorted(seen)[-200000:]
    os.makedirs(USER_DIR, exist_ok=True)
    with open(TM_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)
    _TM["mt"] = None
    return {"rows": len(rows), "added": added, "batters": len(bat), "pitchers": len(pit)}


def trackman_data():
    try:
        mt = os.path.getmtime(TM_PATH)
    except OSError:
        return {}
    if _TM["mt"] != mt:
        _TM["mt"], _TM["data"] = mt, load_json(TM_PATH, {})
    return _TM["data"]


HIT_KIND = {"Single": "1B", "Double": "2B", "Triple": "3B", "HomeRun": "HR"}


def tm_batter(b):
    bip = [x for x in (b or {}).get("bip", []) if x.get("d") is not None and x.get("f") is not None]
    evs = [x["ev"] for x in (b or {}).get("bip", []) if x.get("ev") is not None]
    spray = [{"d": x["d"], "f": x["f"], "k": HIT_KIND.get(x.get("r"), "OUT")} for x in bip[-120:]]
    out = {"spray": spray, "bip": str(len(bip)), "avgEv": ("%.1f" % (sum(evs) / len(evs))) if evs else "", "maxEv": ("%.1f" % max(evs)) if evs else "",
           "hardPct": ("%d%%" % round(100.0 * len([e for e in evs if e >= 95]) / len(evs))) if evs else ""}
    for k in ("1B", "2B", "3B", "HR"):
        out[k] = str(len([x for x in spray if x["k"] == k]))
    return out


def tm_pitcher(p):
    ty = (p or {}).get("types", {})
    tot = sum(v["n"] for v in ty.values()) or 1
    rows = sorted(({"type": k, "pct": "%d%%" % round(100.0 * v["n"] / tot), "avg": "%.1f" % (v["sum"] / v["n"]), "max": "%.1f" % v["max"], "n": v["n"]}
                   for k, v in ty.items() if v["n"]), key=lambda r: -r["n"])
    return {"mix": rows[:6]}


def trackman_enrich(g):
    """Attach TrackMan spray charts and batted-ball numbers to the current batter, and the pitch mix to the pitcher."""
    tm = trackman_data()
    if not tm:
        return
    b = (tm.get("batters") or {}).get(tm_key((g.get("batter") or {}).get("name")))
    if b and isinstance(g.get("batter"), dict):
        g["batter"]["tm"] = tm_batter(b)
    p = (tm.get("pitchers") or {}).get(tm_key((g.get("pitcher") or {}).get("name")))
    if p and isinstance(g.get("pitcher"), dict):
        g["pitcher"]["tm"] = tm_pitcher(p)


def parse_today(s):
    """'2-3, HR, 2 RBI, BB' -> counts. None when there is no line yet."""
    parts = [x.strip() for x in str(s or "").split(",") if x.strip()]
    mm = re.match(r"^(\d+)-(\d+)$", parts[0]) if parts else None
    if not mm:
        return None
    out = {"h": int(mm.group(1)), "ab": int(mm.group(2)), "hr": 0, "rbi": 0, "bb": 0, "k": 0, "d2": 0, "d3": 0, "sb": 0,
           "hab": parts[0], "notes": ", ".join(parts[1:])}
    for p in parts[1:]:
        m2 = re.match(r"^(\d+)\s+(.+)$", p)
        n, k = (int(m2.group(1)), m2.group(2)) if m2 else (1, p)
        key = {"HR": "hr", "RBI": "rbi", "BB": "bb", "K": "k", "2B": "d2", "3B": "d3", "SB": "sb"}.get(k.upper())
        if key:
            out[key] += n
    return out


def _num(v):
    """Numeric value for comparisons; innings like '6.1' count thirds."""
    if v in (None, ""):
        return None
    s = str(v)
    try:
        if re.match(r"^\d+\.[012]$", s):
            whole, part = s.split(".")
            return int(whole) + int(part) / 3.0
        return float(s)
    except ValueError:
        return None


def compare_rows(a, h, spec):
    """Rows {label, away, home, awayHi, homeHi} for side-by-side cards. spec: (label, key|fn, formatter, 'high'|'low'|None)."""
    rows = []
    for label, key, fmt_, better in spec:
        get_ = key if callable(key) else (lambda d, k=key: (d or {}).get(k))
        va, vh = get_(a), get_(h)
        if va in (None, "") and vh in (None, ""):
            continue
        row = {"label": label, "away": fmt_(va) if va not in (None, "") else "-", "home": fmt_(vh) if vh not in (None, "") else "-",
               "awayHi": False, "homeHi": False}
        na, nh = _num(va), _num(vh)
        if better and na is not None and nh is not None and na != nh:
            a_wins = (na > nh) if better == "high" else (na < nh)
            row["awayHi"], row["homeHi"] = a_wins, not a_wins
        rows.append(row)
    return rows


POS_WORD = {"P": "pitcher", "C": "catcher", "1B": "first base", "2B": "second base", "3B": "third base", "SS": "shortstop",
            "LF": "left field", "CF": "center field", "RF": "right field"}


def play_text(p, name):
    """'GROUNDS OUT TO SHORTSTOP' style sentence for a play from the event log."""
    t, f, bb = p.get("type") or "", p.get("fielder") or "", p.get("bb") or ""
    to = (" to " + POS_WORD[f]) if f in POS_WORD else ""
    verb = {"1B": "singles" + to, "2B": "doubles" + to, "3B": "triples" + to, "HR": "homers" + to, "BB": "walks", "IBB": "is intentionally walked",
            "HBP": "is hit by a pitch", "K": "strikes out", "FC": "reaches on a fielder's choice", "ROE": "reaches on an error" + (" by the " + POS_WORD[f] if f in POS_WORD else ""),
            "CI": "reaches on catcher's interference", "SB": "steals a base", "CS": "is caught stealing", "WP": "wild pitch", "PB": "passed ball",
            "BK": "balk", "PO": "pickoff attempt"}.get(t)
    if t == "OUT" or not verb:
        verb = {"GB": "grounds out", "FB": "flies out", "LD": "lines out", "PU": "pops out", "BU": "bunts out"}.get(str(bb).upper(), "is out") + to
    if t in ("WP", "PB", "BK", "PO"):
        return PLAY_LABEL.get(t, verb).capitalize() if t != "PO" else "Pickoff attempt"
    return ("%s %s" % (name, verb)).strip()


HR_LABEL = {1: "SOLO HOME RUN", 2: "2-RUN HOME RUN", 3: "3-RUN HOME RUN", 4: "GRAND SLAM"}
PLAY_LABEL = {"WP": "WILD PITCH", "PB": "PASSED BALL", "1B": "SINGLE", "2B": "DOUBLE", "3B": "TRIPLE", "BB": "WALK", "IBB": "INTENTIONAL WALK",
              "HBP": "HIT BY PITCH", "K": "STRIKEOUT", "SB": "STOLEN BASE", "CS": "CAUGHT STEALING", "BK": "BALK", "E": "ERROR",
              "ROE": "REACHES ON ERROR", "FC": "FIELDER'S CHOICE", "CI": "CATCHER'S INTERFERENCE", "OUT": "OUT"}


HIT_TYPES = ("1B", "2B", "3B", "HR")


def play_summaries(g):
    """Scoring summary (every scoring play with the score after it), the last completed half-inning's recap,
    player of the game, and pitch-count splits, all from the play log."""
    log = g.get("playLog") or []
    score = {"away": 0, "home": 0}
    scoring = []
    for p in log:
        if p.get("runs"):
            score[p["side"]] += ival(p["runs"])
            scoring.append({"label": "%s %s" % ("TOP" if p.get("half") == "top" else "BOT", _ord(ival(p.get("inning"), 1))), "text": p.get("text", ""),
                            "side": p["side"], "logo": g[p["side"]].get("logo", ""), "abbr": g[p["side"]].get("abbr", ""),
                            "score": "%s %d, %s %d" % (g["away"].get("abbr", ""), score["away"], g["home"].get("abbr", ""), score["home"])})
    g["scoring"] = scoring[-8:]
    g["hasScoring"] = bool(scoring)
    # recap of the most recent completed half: when the current half is middle / end, it is this inning's half just played
    half = g.get("half")
    inning = ival(g.get("inning"), 1)
    rh = None
    if half in ("middle", "end"):
        rh = ("top" if half == "middle" else "bottom", inning)
    elif half == "bottom" and inning >= 1:
        rh = ("top", inning)
    elif half == "top" and inning > 1:
        rh = ("bottom", inning - 1)
    rec = {}
    if rh:
        hp = [p for p in log if p.get("half") == rh[0] and ival(p.get("inning")) == rh[1]]
        side = "away" if rh[0] == "top" else "home"
        ls = (g.get("linescore") or {}).get(side) or []
        runs = ls[rh[1] - 1] if len(ls) >= rh[1] and ls[rh[1] - 1] not in ("", None) else sum(ival(p.get("runs")) for p in hp)
        hits = sum(1 for p in hp if p.get("type") in HIT_TYPES)
        errs = sum(1 for p in hp if p.get("type") in ("E", "ROE"))
        rec = {"label": "%s %s" % ("TOP" if rh[0] == "top" else "BOTTOM", _ord(rh[1])), "side": side, "abbr": g[side].get("abbr", ""),
               "name": g[side].get("name", ""), "logo": g[side].get("logo", ""), "color": g[side].get("color", ""),
               "runs": ival(runs), "hits": hits, "errors": errs, "line": "%d R  %d H  %d E" % (ival(runs), hits, errs)}
    g["halfRecap"] = rec
    # player of the game: the leading (or winning) team's top hitter
    lead = "home" if ival(g["home"].get("runs")) > ival(g["away"].get("runs")) else ("away" if ival(g["away"].get("runs")) > ival(g["home"].get("runs")) else "")
    th = (g.get(lead) or {}).get("topHitters") or [] if lead else []
    best = th[0] if th and th[0].get("hab") else {}
    g["potg"] = dict(best, line=", ".join(x for x in (best.get("hab", "").replace("-", " for "), play_words(best.get("notes", ""))) if x),
                     teamName=(g.get(lead) or {}).get("name", "") if best else "") if best else {}
    # pitch-count splits for the pitch tracker
    pt = (g.get("pitcher") or {}).get("today") or {}
    pc, st = ival(pt.get("pc")), ival(pt.get("st"))
    pt["bl"] = max(0, pc - st)
    pt["stPct"] = ("%d%%" % round(100.0 * st / pc)) if pc else ""


def derive_extras(g):
    """Fields for the network graphics: top hitters, decisions, pitcher comparisons, last-play headline."""
    for side in ("away", "home"):
        t = g[side]
        rows = []
        for p in t.get("lineup", []):
            d = parse_today(p.get("today"))
            if not d:
                continue
            score = d["h"] * 3 + d["hr"] * 5 + d["rbi"] * 2 + d["d2"] + d["d3"] * 2 + d["bb"] + d["sb"]
            rows.append((-score, ival(p.get("slot"), 99), {"slot": p.get("slot"), "name": p.get("name", ""), "last": p.get("last", ""),
                                                           "first": p.get("first", ""), "number": p.get("number", ""), "pos": p.get("pos", ""),
                                                           "hab": d["hab"], "notes": d["notes"], "photo": p.get("photo", ""),
                                                           "avg": p.get("avg"), "hr": p.get("hr"), "rbi": p.get("rbi"), "obp": p.get("obp"),
                                                           "side": side, "color": t.get("color"), "logo": t.get("logo")}))
        rows.sort(key=lambda r: (r[0], r[1]))
        t["topHitters"] = [r[2] for r in rows[:4]]
        if not t["topHitters"]:
            # Before first pitch: the lineup's best season hitters (by OPS, then AVG)
            pre = sorted([p for p in t.get("lineup", []) if p.get("name")],
                         key=lambda p: (-(_num(p.get("ops")) or 0), -(_num(p.get("avg")) or 0), ival(p.get("slot"), 99)))
            t["topHitters"] = [{"slot": p.get("slot"), "name": p.get("name", ""), "last": p.get("last", ""), "first": p.get("first", ""),
                                "number": p.get("number", ""), "pos": p.get("pos", ""), "hab": "", "notes": "", "photo": p.get("photo", ""),
                                "avg": p.get("avg"), "hr": p.get("hr"), "rbi": p.get("rbi"), "obp": p.get("obp"), "side": side,
                                "color": t.get("color"), "logo": t.get("logo")} for p in pre[:4]]
        bid = str((g.get("batter") or {}).get("id") or "").lower()
        for p in t.get("lineup", []):
            d = parse_today(p.get("today"))
            p["hab"] = d["hab"] if d else ""
            p["plays"] = play_words(d["notes"]) if d else ""
            p["isUp"] = bool(bid) and str(p.get("id") or "").lower() == bid and g.get("battingSide") == side
        for p in t.get("pitchers", []):
            p["line"] = "%s IP, %d H, %d R, %d K" % (p.get("ip") or "0.0", ival(p.get("h")), ival(p.get("r")), ival(p.get("k")))
            p["statline"] = "%s IP | %d R | %d P" % (p.get("ip") or "0.0", ival(p.get("r")), ival(p.get("pc")))
        pl = t.get("pitchers", [])
        t["finisher"] = pl[-1] if len(pl) > 1 else {}
        t["kTotal"] = sum(ival(p.get("k")) for p in pl)
        t["prevPitcher"] = pl[-2] if len(pl) > 1 else {}
        used = set(str(p.get("id") or "").lower() for p in list(t.get("lineup", [])) + list(pl))
        bench, pen = [], []
        for p in t.get("roster", []):
            if str(p.get("id") or "").lower() in used or not p.get("name"):
                continue
            (pen if str(p.get("pos") or "").upper() in ("P", "SP", "RP") else bench).append(p)
        t["bench"], t["bullpen"] = bench[:6], pen[:8]
        # Bench grouped by batting hand for the lineup + bench card (last names, one per line)
        by = {"L": [], "S": [], "R": []}
        for p in bench:
            hnd = str(p.get("bats") or "").upper()[:1]
            hnd = {"B": "S"}.get(hnd, hnd)
            if hnd in by:
                by[hnd].append(p.get("last") or p.get("name", ""))
        t["benchBy"] = {k: "\n".join(v[:6]) for k, v in by.items()}
        t["benchBy"]["any"] = bool(by["L"] or by["S"] or by["R"])
        sp = t.get("sp") or {}
        sp.setdefault("season", {})
        t["sp"] = sp
    # Headshots for plays / decisions from the already-resolved lineups, rosters and pitchers
    photo_by = {}
    for side in ("away", "home"):
        for p in list(g[side].get("roster", [])) + list(g[side].get("lineup", [])) + list(g[side].get("pitchers", [])):
            if p.get("photo"):
                photo_by[slug(p.get("name"))] = p["photo"]
                if p.get("id"):
                    photo_by[str(p["id"]).lower()] = p["photo"]
    for p in g.get("recentPlays") or []:
        p["photo"] = photo_by.get(slug(p.get("batter"))) or p.get("photo") or ""
        p["logo"] = g[p.get("side") or "home"].get("logo", "")
        p["color"] = g[p.get("side") or "home"].get("color", "")
    # defense: headshots / first names for the defense banners (outfield, infield)
    for side in ("away", "home"):
        by = {}
        for p in list(g[side].get("roster", [])) + list(g[side].get("lineup", [])) + list(g[side].get("pitchers", [])):
            if p.get("id"):
                by.setdefault(str(p["id"]).lower(), p)
            by.setdefault(slug(p.get("name")), p)
        for pos, d in (g[side].get("defense") or {}).items():
            src = by.get(str(d.get("id") or "").lower()) or by.get(slug(d.get("name"))) or {}
            d["pos"] = pos
            d["photo"] = d.get("photo") or src.get("photo") or photo_by.get(slug(d.get("name"))) or ""
            nm = (d.get("name") or "").split(" ")
            d["first"] = d.get("first") or src.get("first") or (" ".join(nm[:-1]) if len(nm) > 1 else "")
            d["number"] = d.get("number") or src.get("number") or ""
    # performers: the two best hitters on each side, for four-column comparison cards
    g["performers"] = (g["away"].get("topHitters") or [])[:2] + (g["home"].get("topHitters") or [])[:2]
    dec = g.get("decisions") or {}
    for k, p in list(dec.items()):
        p["photo"] = photo_by.get(str(p.get("id") or "").lower()) or photo_by.get(slug(p.get("name"))) or p.get("photo") or ""
        p["text"] = decision_line(p, k)
        p["record"] = ("%s-%s" % (p["w"], p["l"])) if p.get("w") not in (None, "") and p.get("l") not in (None, "") else ""
    g["decisions"] = dec
    g["hasDecisions"] = bool(dec.get("w") or dec.get("l"))
    a, h = g["away"].get("sp") or {}, g["home"].get("sp") or {}
    sa, sh = a.get("season") or {}, h.get("season") or {}
    rec = lambda s: ("%s-%s" % (s.get("w"), s.get("l"))) if s.get("w") not in (None, "") and s.get("l") not in (None, "") else None
    wdiff = lambda s: (ival(s.get("w")) - ival(s.get("l"))) if rec(s) else None
    kbb = lambda s: ("%s-%s" % (s.get("k"), s.get("bb"))) if s.get("k") not in (None, "") and s.get("bb") not in (None, "") else None
    g["spSeason"] = compare_rows(sa, sh, [
        ("RECORD", rec, str, None), ("ERA", "era", lambda v: fmt_rate(v, 2), "low"), ("IP", "ip", str, "high"),
        ("K-BB", kbb, str, None), ("WHIP", "whip", lambda v: fmt_rate(v, 2), "low"), ("OPP AVG", "oppAvg", fmt_rate, "low")])
    # highlight W-L by win margin
    for row in g["spSeason"]:
        if row["label"] == "RECORD" and wdiff(sa) is not None and wdiff(sh) is not None and wdiff(sa) != wdiff(sh):
            row["awayHi"], row["homeHi"] = wdiff(sa) > wdiff(sh), wdiff(sh) > wdiff(sa)
    g["spToday"] = compare_rows(a, h, [
        ("INNINGS", "ip", str, "high"), ("HITS", "h", str, "low"), ("EARNED RUNS", "er", str, "low"),
        ("WALKS", "bb", str, "low"), ("STRIKEOUTS", "k", str, "high"), ("PITCHES", "pc", str, None)])
    play_summaries(g)
    lp = g.get("lastPlay") or {}
    if lp.get("type"):
        t = lp["type"]
        lp["isHR"] = t == "HR"
        lp["isWP"] = t in ("WP", "PB")
        lp["label"] = HR_LABEL.get(max(1, min(4, ival(lp.get("runs"), 1))), "HOME RUN") if t == "HR" else PLAY_LABEL.get(t, t)
        try:
            lp["distance"] = str(int(round(float(lp["distance"])))) if lp.get("distance") not in (None, "") else ""
        except (TypeError, ValueError):
            pass
        try:
            lp["ev"] = ("%.1f" % float(lp["ev"])).rstrip("0").rstrip(".") if lp.get("ev") not in (None, "") else ""
        except (TypeError, ValueError):
            pass
        w = lp["label"].split(" ", 1)
        lp["word1"], lp["word2"] = w[0], (w[1] if len(w) > 1 else "")
        g["lastPlay"] = lp


# ---------------------------------------------------------------------------
# Standings (shared shape for every source)
#   {"groups": [{"name": "North Division", "teams": [{rank, name, abbr, w, l, pct, gb, streak, last10, logo, color}]}]}
# ---------------------------------------------------------------------------
def fmt_pct(w, l, pct=None):
    if pct not in (None, ""):
        try:
            f = float(pct)
            f = f / 100.0 if f > 1 else f
            return fmt_rate(f)
        except Exception:
            return str(pct)
    w, l = ival(w), ival(l)
    return fmt_rate(w / float(w + l)) if (w + l) else ".000"


def finish_standings(groups):
    """Sort, rank and compute games back where the feed did not give them."""
    out = []
    for g in groups:
        teams = [t for t in g.get("teams", []) if t.get("name")]
        teams.sort(key=lambda t: (-(ival(t["w"]) / float(max(1, ival(t["w"]) + ival(t["l"])))), -ival(t["w"])))
        if teams:
            lw, ll = ival(teams[0]["w"]), ival(teams[0]["l"])
            for i, t in enumerate(teams):
                t["rank"] = i + 1
                if t.get("gb") in (None, ""):
                    gb = ((lw - ival(t["w"])) + (ival(t["l"]) - ll)) / 2.0
                    t["gb"] = "-" if gb <= 0 else (("%d" % gb) if gb == int(gb) else ("%.1f" % gb))
                else:
                    try:
                        f = float(str(t["gb"]).replace("+", ""))
                        t["gb"] = "-" if f <= 0 else (("%d" % f) if f == int(f) else ("%.1f" % f))
                    except ValueError:
                        t["gb"] = str(t["gb"])
                t["pct"] = fmt_pct(t["w"], t["l"], t.get("pct"))
                t["w"], t["l"] = ival(t["w"]), ival(t["l"])
                t["record"] = "%d-%d" % (t["w"], t["l"])
        out.append({"name": g.get("name") or "Standings", "teams": teams})
    return {"groups": [g for g in out if g["teams"]], "updated": time.time()}


def parse_standings_text(text):
    """Manual standings. A line without numbers starts a group; team lines are NAME W L [GB]:
        North Division
        Harbor City Gulls 52 37
        Riverside Otters 48 41 4"""
    groups, cur = [], None
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"[\t,]+|\s{2,}", line) if ("," in line or "\t" in line) else line.split()
        nums = []
        while parts and re.fullmatch(r"-|\d+(\.\d+)?", parts[-1].strip()):
            nums.insert(0, parts.pop().strip())
        if len(nums) < 2:
            cur = {"name": line, "teams": []}
            groups.append(cur)
            continue
        if cur is None:
            cur = {"name": "Standings", "teams": []}
            groups.append(cur)
        name = " ".join(p.strip() for p in parts)
        cur["teams"].append({"name": name, "abbr": "", "w": nums[0], "l": nums[1], "gb": nums[2] if len(nums) > 2 else None})
    return finish_standings(groups)


# ---------------------------------------------------------------------------
# Picker, ticker and play helpers
# ---------------------------------------------------------------------------
def pick_player(g, pick):
    """The player chosen in the Custom panel, shaped like batter / pitcher (season stats + card rows)."""
    side = "away" if (pick or {}).get("side") == "away" else "home"
    pid = str((pick or {}).get("id") or "").lower()
    if not pid:
        return {}
    t = g.get(side) or {}
    found = None
    for p in list(t.get("roster", [])) + list(t.get("lineup", [])) + list(t.get("pitchers", [])):
        if str(p.get("id") or "").lower() == pid or slug(p.get("name")) == pid:
            found = dict(found or {}, **{k: v for k, v in p.items() if v not in (None, "")})
    if not found:
        return {}
    base = {k: found.get(k, "") for k in ("id", "name", "first", "last", "number", "pos", "photo", "bats", "throws", "height", "weight", "age", "hometown")}
    bat = dict(found.get("bat") or {})
    for k in ("avg", "obp", "slg", "ops", "hr", "rbi"):
        if bat.get(k) in (None, "") and found.get(k) not in (None, ""):
            bat[k] = found[k]
    pit = dict(found.get("pit") or found.get("season") or {})
    for k in ("era", "whip"):
        if pit.get(k) in (None, "") and found.get(k) not in (None, ""):
            pit[k] = found[k]
    b = dict(base, season=bat, today={"line": found.get("today") if isinstance(found.get("today"), str) else ""})
    p = dict(base, season=pit, today={})
    b["card"], p["card"] = card_rows(b, "bat"), card_rows(p, "pit")
    return {"side": side, "name": base["name"], "bat": b, "pit": p,
            "isPitcher": str(base.get("pos") or "").upper() in ("P", "SP", "RP") or (bool(pit) and not bat)}


def ticker_items(g, ui, scoreboard):
    """Items for the bottom ticker: league scores, standings, your tidbits."""
    tk = (ui or {}).get("ticker") or {}
    items = []
    if tk.get("scores", True) and scoreboard:
        items.append({"head": True, "text": "SCORES"})
        for s in scoreboard:
            items.append({"text": "%s %s  %s %s  %s" % (s.get("away", ""), s.get("awayRuns", "") if s.get("awayRuns") is not None else "",
                                                         s.get("home", ""), s.get("homeRuns", "") if s.get("homeRuns") is not None else "", s.get("state", "")),
                          "live": s.get("status") == "LIVE"})
    groups = ((g.get("standings") or {}).get("groups")) or []
    if tk.get("standings", True) and groups:
        for grp in [x for x in groups if not x.get("overall")] or groups:
            items.append({"head": True, "text": (grp.get("name") or "STANDINGS").upper()})
            for t in grp.get("teams", [])[:8]:
                items.append({"text": "%s. %s %s-%s%s" % (t.get("rank", ""), t.get("abbr") or t.get("name", ""), t.get("w", 0), t.get("l", 0),
                                                         ("  GB %s" % t["gb"]) if t.get("gb") not in (None, "", "-") else "")})
    lines = [ln.strip() for ln in str(tk.get("tidbits") or "").splitlines() if ln.strip()]
    if lines:
        items.append({"head": True, "text": "NOTES"})
        items += [{"text": ln} for ln in lines]
    return items


def play_with_notes(lp, notes):
    """Last play with manual distance / exit velocity (control panel notes) filling what the feed lacks."""
    lp = dict(lp or {})
    notes = notes or {}
    if lp.get("isHR"):
        if not lp.get("distance") and notes.get("dist"):
            lp["distance"] = str(notes["dist"]).strip()
        if not lp.get("ev") and notes.get("ev"):
            lp["ev"] = str(notes["ev"]).strip()
    return lp


def py_cond(expr, ctx):
    """Minimal showIf evaluator for trigger conditions: a, !a, a && b, a || b (path truthiness)."""
    def term(t):
        t = t.strip()
        neg = t.startswith("!")
        v = get_path(ctx, t.lstrip("!").strip())
        ok = v not in (None, "", 0, False, [], {})
        return not ok if neg else ok
    return any(all(term(x) for x in part.split("&&")) for part in str(expr).split("||"))


def decision_line(p, kind):
    """W: LAST (1-0, 2.57)   L: LAST (0-1, 1.50)   S: LAST (1)"""
    if not p or not p.get("name"):
        return ""
    last = (p.get("last") or p.get("name") or "").upper()
    if kind == "s":
        return "%s (%s)" % (last, p["sv"]) if p.get("sv") not in (None, "") else last
    rec = ("%s-%s" % (p["w"], p["l"])) if p.get("w") not in (None, "") and p.get("l") not in (None, "") else ""
    era = fmt_rate(p.get("era"), 2) if p.get("era") not in (None, "") else ""
    inner = ", ".join(x for x in (rec, era) if x)
    return "%s (%s)" % (last, inner) if inner else last




class _NoReplay:
    """Stand-in when this build has no feed code: replay of finished games needs a data feed."""
    active = False

    def info(self, full=False):
        return {"active": False}

    def stop(self):
        pass


if "REPLAY" not in globals():
    REPLAY = _NoReplay()


# ---------------------------------------------------------------------------
# Manual source
# ---------------------------------------------------------------------------
def parse_lineup_text(text):
    """Lines like: '1 Alex Rivera CF .312' or '1, Alex Rivera, CF, .312'."""
    rows = []
    for i, line in enumerate((text or "").splitlines()):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in re.split(r"\s*,\s*|\t", line) if p.strip()]
        if len(parts) == 1:
            parts = line.split()
        slot = i + 1
        if parts and re.fullmatch(r"\d{1,2}\.?", parts[0]):
            slot = int(parts[0].rstrip("."))
            parts = parts[1:]
        avg = ""
        if parts and re.fullmatch(r"\.?\d{3}|\d\.\d{3}", parts[-1]):
            avg = parts.pop()
        pos = ""
        if parts and norm_pos(parts[-1]) in FIELD_POS + ["DH", "PH", "PR"] and len(parts[-1]) <= 3:
            pos = norm_pos(parts.pop())
        name = " ".join(parts)
        full, first, last = split_name(name)
        rows.append({"slot": slot, "id": "m%d" % slot, "name": full, "first": first, "last": last,
                     "number": "", "pos": pos, "avg": avg, "ops": "", "hr": "", "rbi": "", "today": "", "sub": False})
    return rows


def manual_game(m):
    g = empty_game()
    g["source"] = "manual"
    for side in ("away", "home"):
        src = m.get(side) or {}
        g[side].update({"name": src.get("name", ""), "abbr": src.get("abbr", ""),
                        "runs": src.get("runs", 0), "hits": src.get("hits", 0), "errors": src.get("errors", 0)})
        lineup = parse_lineup_text((m.get("lineup_text") or {}).get(side, ""))
        g[side]["lineup"] = lineup
        g[side]["defense"] = {p["pos"]: {"name": p["name"], "last": p["last"], "number": ""} for p in lineup if p["pos"] in FIELD_POS}
        g["linescore"][side] = list((m.get("linescore") or {}).get(side, []))
    for k in ("inning", "half", "balls", "strikes", "outs", "bases", "status"):
        if k in m:
            g[k] = copy.deepcopy(m[k])
    b = m.get("batter") or {}
    full, first, last = split_name(b.get("name"))
    g["batter"].update({"id": "mb", "name": full, "first": first, "last": last, "number": str(b.get("number", "")),
                        "pos": b.get("pos", ""), "bats": b.get("bats", ""),
                        "today": {"line": b.get("line", "")},
                        "season": {"avg": b.get("avg"), "hr": b.get("hr"), "rbi": b.get("rbi"), "ops": b.get("ops")}})
    p = m.get("pitcher") or {}
    full, first, last = split_name(p.get("name"))
    g["pitcher"].update({"id": "mp", "name": full, "first": first, "last": last, "number": str(p.get("number", "")),
                         "throws": p.get("throws", ""),
                         "today": {"pc": ival(p.get("pc")), "ip": p.get("ip", ""), "k": ival(p.get("k")), "line": p.get("line", "")},
                         "season": {"era": p.get("era")}})
    for side in ("away", "home"):
        fld = "home" if (g["half"] == "top") else "away"
        if side == fld and full:
            g[side]["defense"]["P"] = {"name": full, "last": last, "number": str(p.get("number", ""))}
    return g


# ---------------------------------------------------------------------------
# Other sports (manual scoring): basketball, football, hockey
# ---------------------------------------------------------------------------
# Each sport keeps its own state in ui["sports"][sport]. Running clocks are stored as milliseconds left at the
# moment "at" (server time, ms); overlays count down from there by themselves, so nothing is sent while a clock runs.
SPORTS = {
    "basketball": {"label": "Basketball", "periods": 4, "periodMin": 10, "otMin": 5, "shotLen": 24, "shotShort": 14, "timeouts": 4,
                   "periodWord": "Quarter", "points": [1, 2, 3]},
    "football": {"label": "Football", "periods": 4, "periodMin": 15, "otMin": 10, "shotLen": 40, "shotShort": 25, "timeouts": 3,
                 "periodWord": "Quarter", "points": [6, 3, 2, 1]},
    "hockey": {"label": "Hockey", "periods": 3, "periodMin": 20, "otMin": 5, "shotLen": 0, "shotShort": 0, "timeouts": 1,
               "periodWord": "Period", "points": [1]},
}
SPORT_KEYS = ("baseball",) + tuple(SPORTS)


def sport_default(sport):
    d = SPORTS[sport]
    team = lambda nm, ab: {"name": nm, "abbr": ab, "score": 0, "timeouts": d["timeouts"], "fouls": 0, "shots": 0, "pens": [], "en": False}
    return {"away": team("Visitors", "VIS"), "home": team("Home", "HOM"), "period": 1, "status": "PRE", "poss": "",
            "clock": {"ms": d["periodMin"] * 60000, "at": 0, "running": False}, "shot": {"ms": d["shotLen"] * 1000},
            "down": 1, "dist": "10", "ballOn": "", "flag": False,
            "periods": d["periods"], "periodMin": d["periodMin"], "otMin": d["otMin"], "shotLen": d["shotLen"], "shotShort": d["shotShort"],
            "timeoutsPer": d["timeouts"], "bonusAt": 5,
            "lines": {"away": [], "home": []}, "last": {"n": 0}, "lineup_text": {"away": "", "home": ""}, "stats_text": "",
            "standings_text": "", "player": {"side": "home", "name": "", "number": "", "pos": "", "line": "", "note": ""}}


def sport_state(ui, sport):
    sp = (ui.setdefault("sports", {})).get(sport)
    base = sport_default(sport)
    if not isinstance(sp, dict):
        ui["sports"][sport] = base
        return base
    for k, v in base.items():
        sp.setdefault(k, copy.deepcopy(v))
    for side in ("away", "home"):
        for k, v in base[side].items():
            sp[side].setdefault(k, copy.deepcopy(v))
    return sp


def _now_ms():
    return int(time.time() * 1000)


def sport_settle(st, now=None):
    """Move the running clocks forward to now (clock, shot / play clock, penalties). Stops at 0:00."""
    now = now or _now_ms()
    c = st["clock"]
    if c.get("running") and c.get("at"):
        e = max(0, now - int(c["at"]))
        e = min(e, int(c["ms"]))          # nothing runs past the end of the period
        c["ms"] = int(c["ms"]) - e
        st["shot"]["ms"] = max(0, int(st["shot"].get("ms") or 0) - e)
        for side in ("away", "home"):
            pens = []
            for p in st[side].get("pens") or []:
                p["ms"] = int(p.get("ms") or 0) - e
                if p["ms"] > 0:
                    pens.append(p)
            st[side]["pens"] = pens
        if c["ms"] <= 0:
            c["ms"], c["running"] = 0, False
    c["at"] = now
    return st


def sport_next_event(st):
    """Server time (ms) of the next moment the state must be settled: period end or a penalty running out."""
    c = st["clock"]
    if not c.get("running") or not c.get("at"):
        return None
    left = [int(c["ms"])] + [int(p.get("ms") or 0) for s in ("away", "home") for p in (st[s].get("pens") or [])]
    return int(c["at"]) + max(0, min(left))


def parse_clock(v):
    """"12:00", "45.3", "90" (seconds) -> ms."""
    s = str(v or "").strip()
    m = re.fullmatch(r"(\d+):(\d{1,2})(?:\.(\d))?", s)
    if m:
        return (int(m.group(1)) * 60 + int(m.group(2))) * 1000 + int(m.group(3) or 0) * 100
    try:
        return int(float(s) * 1000)
    except ValueError:
        return None


def period_length(st, period):
    return (st["periodMin"] if period <= st["periods"] else st["otMin"]) * 60000


def sport_op(st, sport, op):
    """Apply one scoring-panel action. Returns a play dict when it should fire stingers."""
    sport_settle(st)
    a = op.get("op")
    side = op.get("side") if op.get("side") in ("away", "home") else None
    n = op.get("n")
    try:
        n = int(n) if n is not None else None
    except (TypeError, ValueError):
        n = None
    c = st["clock"]
    play = None
    if a in ("start", "stop", "toggle"):
        on = (a == "start") or (a == "toggle" and not c.get("running"))
        if on and c["ms"] <= 0:
            on = False
        c["running"] = bool(on)
        if on and st.get("status") == "PRE":
            st["status"] = "LIVE"
    elif a == "clock_set":
        ms = parse_clock(op.get("value"))
        if ms is not None:
            c["ms"] = max(0, ms)
    elif a == "clock_adj":
        c["ms"] = max(0, c["ms"] + int(n or 0) * 1000)
    elif a == "shot_reset":
        st["shot"]["ms"] = int(n if n is not None else st["shotLen"]) * 1000
    elif a == "shot_set":
        ms = parse_clock(op.get("value"))
        if ms is not None:
            st["shot"]["ms"] = max(0, ms)
    elif a == "score" and side and n:
        t = st[side]
        t["score"] = max(0, int(t["score"]) + n)
        lines = st["lines"].setdefault(side, [])
        while len(lines) < st["period"]:
            lines.append(0)
        lines[st["period"] - 1] = max(0, lines[st["period"] - 1] + n)
        if n > 0 and sport == "hockey":
            # a power-play goal ends the shortest minor penalty on the short-handed team
            opp = st["home" if side == "away" else "away"]
            if len(opp.get("pens") or []) > len(t.get("pens") or []):
                minors = [x for x in opp["pens"] if float(x.get("min") or 2) <= 2]
                if minors:
                    opp["pens"].remove(min(minors, key=lambda x: x["ms"]))
        if n > 0:
            kind = {"hockey": {1: "GOAL"}, "football": {6: "TD", 3: "FG", 2: "SCORE2", 1: "PAT"},
                    "basketball": {3: "3PT"}}.get(sport, {}).get(n, "SCORE")
            if op.get("kind"):
                kind = str(op["kind"]).upper()
            st["last"] = {"n": int(st["last"].get("n") or 0) + 1, "type": kind, "side": side, "points": n}
            play = st["last"]
            st["lastScore"] = side
            if st.get("status") == "PRE":
                st["status"] = "LIVE"
    elif a in ("timeouts", "fouls", "shots") and side:
        st[side][a] = max(0, int(st[side].get(a) or 0) + int(n or 0))
    elif a == "poss":
        st["poss"] = "" if st.get("poss") == side or not side else side
    elif a == "period":
        p = max(1, int(st["period"]) + int(n or 0))
        st["period"] = p
        c["ms"], c["running"] = period_length(st, p), False
        st["shot"]["ms"] = st["shotLen"] * 1000
        st["flag"] = False
        if sport == "basketball":
            st["away"]["fouls"] = st["home"]["fouls"] = 0
    elif a == "down":
        st["down"] = min(4, max(1, int(n or 1)))
    elif a == "first_down":
        st["down"], st["dist"] = 1, "10"
    elif a == "flag":
        st["flag"] = not st.get("flag")
    elif a == "status":
        st["status"] = str(op.get("value") or "LIVE").upper()
        if st["status"] == "FINAL":
            c["running"] = False
    elif a == "penalty_add" and side:
        mins = float(op.get("min") or 2)
        st[side].setdefault("pens", []).append({"ms": int(mins * 60000), "label": str(op.get("label") or "")[:40], "min": mins})
        st["last"] = {"n": int(st["last"].get("n") or 0) + 1, "type": "PEN", "side": side, "label": str(op.get("label") or "")}
        play = st["last"]
    elif a == "penalty_clear" and side:
        pens = st[side].get("pens") or []
        i = int(n or 0)
        if 0 <= i < len(pens):
            pens.pop(i)
    elif a == "en" and side:
        st[side]["en"] = not st[side].get("en")
    elif a == "new_game":
        keep = {k: st[k] for k in ("periods", "periodMin", "otMin", "shotLen", "shotShort", "timeoutsPer", "bonusAt", "lineup_text",
                                    "stats_text", "standings_text", "player")}
        names = {s: {"name": st[s]["name"], "abbr": st[s]["abbr"]} for s in ("away", "home")}
        st.clear()
        st.update(sport_default(sport))
        st.update(keep)
        for s in ("away", "home"):
            st[s].update(names[s])
            st[s]["timeouts"] = st["timeoutsPer"]
        st["clock"]["ms"] = st["periodMin"] * 60000
        st["shot"]["ms"] = st["shotLen"] * 1000
    c["at"] = _now_ms()
    return play


def ordinal(n):
    n = int(n)
    return "%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def parse_roster_text(text):
    """"12 Jane Doe G 18 PTS" -> number, name, pos, line (number and pos optional)."""
    out = []
    for line in (text or "").splitlines():
        parts = [p.strip() for p in (line.split(",") if "," in line else line.split()) if p.strip()]
        if not parts:
            continue
        num = parts.pop(0) if re.fullmatch(r"#?\d{1,3}", parts[0]) else ""
        pos, rest = "", []
        for i, p in enumerate(parts):
            if i >= 1 and re.fullmatch(r"[A-Z]{1,3}(/[A-Z]{1,3})?", p) and not pos:
                pos = p
                rest = parts[i + 1:]
                parts = parts[:i]
                break
        name = " ".join(parts)
        full, first, last = split_name(name)
        out.append({"number": num.lstrip("#"), "name": full, "first": first, "last": last, "pos": pos, "line": " ".join(rest),
                    "slot": len(out) + 1})
    return out


def sport_game(sport, st, now=None):
    """The game dict graphics bind to, for a non-baseball sport (team score also in runs, so shared graphics work)."""
    now = now or _now_ms()
    d = SPORTS[sport]
    g = empty_game()
    g["source"] = "manual"
    g["sport"] = sport
    p = int(st["period"])
    reg = int(st["periods"])
    if p <= reg:
        plab = ordinal(p).upper()
        ptext = "%s %s" % (ordinal(p), d["periodWord"])
    else:
        k = p - reg
        plab = "OT" if k == 1 else "%dOT" % k
        if sport == "hockey" and k >= 2:
            plab = "SO"
        ptext = {"OT": "Overtime", "SO": "Shootout"}.get(plab, plab)
    c = st["clock"]
    status = (st.get("status") or "PRE").upper()
    ended = c["ms"] <= 0 and status == "LIVE"
    half = sport != "hockey" and reg == 4 and p == 2 and ended
    if status == "FINAL":
        stext = "FINAL" if p <= reg else "FINAL/" + plab
    elif status == "PRE":
        stext = "PREGAME"
    elif half:
        stext = "HALFTIME"
    elif ended:
        stext = "END " + plab
    else:
        stext = plab
    pens = {s: st[s].get("pens") or [] for s in ("away", "home")}
    n_a, n_h = len(pens["away"][:2]), len(pens["home"][:2])
    pp_side, pp = "", {}
    if sport == "hockey" and n_a != n_h:
        pp_side = "home" if n_a > n_h else "away"
        short = "away" if pp_side == "home" else "home"
        rem = min(int(x["ms"]) for x in pens[short])
        pp = {"ms": rem, "at": c["at"], "running": c.get("running", False)}
    sk = {"5v3": "5 ON 3", "5v4": "POWER PLAY", "4v3": "4 ON 3"}
    skaters = {"away": 5 - n_a, "home": 5 - n_h}
    pp_text = ""
    if pp_side:
        pp_text = sk.get("%dv%d" % (max(skaters.values()), min(skaters.values())), "POWER PLAY")
    for side in ("away", "home"):
        t = st[side]
        opp = st["home" if side == "away" else "away"]
        g[side].update({"name": t.get("name", ""), "abbr": t.get("abbr", ""), "runs": ival(t.get("score")), "score": ival(t.get("score")),
                        "timeouts": ival(t.get("timeouts")), "timeoutsUsed": max(0, ival(st["timeoutsPer"]) - ival(t.get("timeouts"))),
                        "fouls": ival(t.get("fouls")), "shots": ival(t.get("shots")),
                        "bonus": sport == "basketball" and ival(opp.get("fouls")) >= ival(st.get("bonusAt") or 5),
                        "hasPoss": st.get("poss") == side, "onPP": pp_side == side, "en": bool(t.get("en")),
                        "penCount": len(pens[side]),
                        "penLast": (pens[side][-1].get("label") or "%s:00" % int(pens[side][-1].get("min") or 2)) if pens[side] else "",
                        "lineup": parse_roster_text((st.get("lineup_text") or {}).get(side, ""))})
        g[side]["pens"] = [{"label": x.get("label", ""), "min": x.get("min"), "clock": {"ms": int(x["ms"]), "at": c["at"], "running": c.get("running", False)}}
                           for x in pens[side]]
        g["linescore"][side] = list((st.get("lines") or {}).get(side) or [])
    n_cols = max(reg, p)
    for side in ("away", "home"):
        row = g["linescore"][side]
        g["linescore"][side] = [row[i] if i < len(row) else ("" if i >= p else 0) for i in range(n_cols)]
    g["linescore"]["innings"] = n_cols
    g["status"] = "FINAL" if status == "FINAL" else ("PRE" if status == "PRE" else "LIVE")
    g["statusText"] = stext
    down = int(st.get("down") or 1)
    dist = str(st.get("dist") or "").strip()
    g["scorerSide"] = st.get("lastScore") or (st.get("last") or {}).get("side") or ""
    g["sp"] = {
        "sport": sport, "label": d["label"], "period": p, "periodLabel": plab, "periodText": ptext, "statusText": stext,
        "isOT": p > reg, "ended": ended, "halftime": half,
        "clock": {"ms": int(c["ms"]), "at": int(c["at"] or now), "running": bool(c.get("running"))},
        "shot": {"ms": int(st["shot"].get("ms") or 0), "at": int(c["at"] or now), "running": bool(c.get("running"))},
        "hasShot": bool(st.get("shotLen")),
        "now": now, "poss": st.get("poss") or "",
        "down": down, "dist": dist, "ballOn": str(st.get("ballOn") or ""),
        "downText": ("%s & %s" % (ordinal(down), dist or "10")) if sport == "football" else "",
        "flag": bool(st.get("flag")),
        "pp": pp, "ppSide": pp_side, "ppText": pp_text,
        "stats": parse_stat_rows(st.get("stats_text") or ""),
        "player": dict(st.get("player") or {}),
        "last": dict(st.get("last") or {}),
        "lineCols": [ordinal(i + 1).upper() if i < reg else ("OT" if i == reg else "%dOT" % (i - reg + 1)) for i in range(n_cols)],
    }
    pl = g["sp"]["player"]
    full, first, last = split_name(pl.get("name"))
    pl.update({"name": full, "first": first, "last": last})
    pt = g.get(pl.get("side") or "home") or {}
    pl["team"] = {k: pt.get(k) for k in ("name", "abbr")}
    lp = st.get("last") or {}
    if lp.get("type"):
        tm = st.get(lp.get("side") or "home") or {}
        g["lastPlay"] = {"id": "sp:%s:%s" % (sport, lp.get("n")), "type": lp["type"], "runs": lp.get("points", 0),
                         "team": lp.get("side"), "teamName": tm.get("name", ""), "teamAbbr": tm.get("abbr", ""), "label": lp.get("label", "")}
    return g


def parse_stat_rows(text):
    """Team stat comparison lines: "Shots on goal | 12 | 9"."""
    rows = []
    for line in (text or "").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3 and parts[0]:
            rows.append({"label": parts[0], "away": parts[1], "home": parts[2]})
    return rows[:8]


def sport_of(gid, d):
    """Which sport a graphic belongs to: its "sport" field, else baseball for baseball-only types, else "all"."""
    d = d or {}
    if d.get("sport"):
        return d["sport"]
    b = gid.split("__")[-1]
    cat = d.get("cat") or category(gid, d)
    if cat in ("scorebugs", "lower_batter", "lower_pitcher", "lineups", "pitching", "players", "scores", "events", "panels"):
        return "baseball"
    if b in ("bvp", "inning_sponsor", "inning_recap", "bp_info"):
        return "baseball"
    return "all"


def sample_game():
    """Placeholder data for the editor and for testing. Not real players."""
    m = copy.deepcopy(DEFAULT_UI["manual"])
    m.update({
        "away": {"name": "Visitors", "abbr": "VIS", "runs": 3, "hits": 7, "errors": 1},
        "home": {"name": "Home Club", "abbr": "HOM", "runs": 4, "hits": 9, "errors": 0},
        "inning": 7, "half": "bottom", "balls": 2, "strikes": 1, "outs": 1,
        "bases": {"1": True, "2": False, "3": True}, "status": "LIVE",
        "batter": {"name": "Alex Rivera", "number": "24", "pos": "CF", "bats": "R", "avg": 0.312, "hr": 12,
                   "rbi": 41, "ops": 0.909, "line": "2-3, HR, 2 RBI"},
        "pitcher": {"name": "Cole Hartwell", "number": "32", "throws": "L", "era": 3.42, "pc": 87, "ip": "6.1",
                    "k": 7, "line": "6.1 IP, 5 H, 2 ER, 1 BB, 7 K"},
        "lineup_text": {
            "away": "1 Jordan Pike SS .287\n2 Marco Delgado 2B .301\n3 Tyler Brandt RF .276\n4 Sam Okafor 1B .298\n"
                    "5 Luis Ortega DH .265\n6 Evan Moss 3B .244\n7 Nate Coyle LF .259\n8 Drew Fenn C .231\n9 Kai Lowell CF .248",
            "home": "1 Ben Castillo 2B .294\n2 Alex Rivera CF .312\n3 Mason Reed 1B .305\n4 Dante Price RF .281\n"
                    "5 Owen Hale DH .270\n6 Ryan Teague 3B .262\n7 Chris Vail LF .255\n8 Jake Monroe C .240\n9 Theo Grant SS .233",
        },
        "linescore": {"away": [0, 1, 0, 0, 2, 0, 0], "home": [1, 0, 0, 2, 0, 0, 1]},
    })
    g = manual_game(m)
    g["source"] = "sample"
    g["standings"] = parse_standings_text(
        "North Division\nHome Club 52 37\nVisitors 48 41\nHarbor City Gulls 50 39\nRiver Valley Kings 44 45\nCapital Rail 39 50\n"
        "South Division\nBay Pelicans 55 34\nPiedmont Owls 47 42\nCoastal Herons 45 44\nMountain Elk 41 48\nDelta Ravens 36 53")
    g["away"]["record"] = "48-41"
    g["home"]["record"] = "52-37"
    # Richer sample stats so every binding renders something in the editor
    for side, rows in (("away", g["away"]["lineup"]), ("home", g["home"]["lineup"])):
        for i, r in enumerate(rows):
            r["number"] = str(10 + i * 3)
            r["hr"] = 3 + i
            r["rbi"] = 20 + i * 4
            r["ops"] = round(0.700 + 0.02 * (9 - i), 3)
            r["today"] = ["1-3", "0-2, BB", "2-3, 2B", "1-3, RBI", "0-3, K", "1-2", "0-3", "1-2, BB", "0-2"][i % 9]
    g["batter"]["photo"] = ""
    g["batter"]["today"].update({"ab": 3, "h": 2, "hr": 1, "rbi": 2})
    g["batter"]["season"].update({"obp": 0.384, "slg": 0.525, "h": 96, "sb": 14, "g": 82})
    g["pitcher"]["today"].update({"h": 5, "r": 2, "er": 2, "bb": 1, "st": 58})
    g["pitcher"]["season"].update({"w": 9, "l": 4, "whip": 1.12, "ip": "121.2", "k": 118, "sv": 0, "bb": 30,
                                   "g": 20, "gs": 20, "h": 104, "oppAvg": 0.226})
    g["away"]["pitchers"] = [
        {"id": "ap1", "name": "Cole Hartwell", "last": "Hartwell", "number": "32", "ip": "6.1", "h": 5, "r": 2, "er": 2,
         "bb": 1, "k": 7, "hr": 1, "pc": 87, "st": 58, "era": 3.42, "whip": 1.12}]
    g["away"]["sp"] = g["away"]["pitchers"][0]
    g["home"]["pitchers"] = [
        {"id": "hp1", "name": "Victor Lane", "last": "Lane", "number": "41", "ip": "5.0", "h": 6, "r": 3, "er": 3,
         "bb": 2, "k": 4, "hr": 0, "pc": 92, "st": 57, "era": 4.05, "whip": 1.31},
        {"id": "hp2", "name": "Gabe Sutter", "last": "Sutter", "number": "55", "ip": "2.0", "h": 1, "r": 0, "er": 0,
         "bb": 0, "k": 3, "hr": 0, "pc": 27, "st": 19, "era": 2.18, "whip": 0.98}]
    g["home"]["sp"] = g["home"]["pitchers"][0]
    g["home"]["defense"]["P"] = {"name": "Gabe Sutter", "last": "Sutter", "number": "55"}
    g["away"]["defense"]["P"] = {"name": "Cole Hartwell", "last": "Hartwell", "number": "32"}
    g["pitcher"]["id"] = "ap1"
    for r in g["home"]["lineup"]:
        if r["name"] == "Alex Rivera":
            g["batter"]["id"] = r["id"]
    return g


# ---------------------------------------------------------------------------
# Sponsors
# ---------------------------------------------------------------------------
def get_path(obj, path):
    for k in str(path).split("."):
        if isinstance(obj, dict):
            obj = obj.get(k)
        elif isinstance(obj, list) and k.isdigit() and int(k) < len(obj):
            obj = obj[int(k)]
        else:
            return None
    return obj


def sponsor_for(ui, spec, now=None, ctx=None):
    """Sponsor for a graphic's sponsor spec. A spec is one slot name or a comma list tried in
    order, and may contain {tokens} from the game, e.g. "half_{halfKey}, scorebug" or
    "lineup_{batter.slot}, batter": the first slot that is switched on with a sponsor wins.
    Rotation is a pure function of the clock, so the exposure log and every overlay agree.
    Must match sponsorFor() in web/engine.js."""
    off = {"on": False, "id": "", "name": "", "logo": "", "label": "", "slot": ""}
    for part in str(spec or "").split(","):
        part = part.strip()
        if not part:
            continue
        missing = [False]

        def fill(m):
            v = get_path(ctx or {}, m.group(1).strip())
            if v in (None, ""):
                missing[0] = True
                return ""
            return str(v)
        name = re.sub(r"\{([^{}]+)\}", fill, part)
        if missing[0]:
            continue
        r = _sponsor_slot(ui, name, now)
        if r["on"]:
            return r
    return off


def _sponsor_slot(ui, slot, now=None):
    off = {"on": False, "id": "", "name": "", "logo": "", "label": "", "slot": slot}
    if not slot:
        return off
    sp = (ui or {}).get("sponsors") or {}
    st = (sp.get("slots") or {}).get(slot) or {}
    if not st.get("enabled"):
        return off
    lib = {x.get("id"): x for x in (sp.get("library") or []) if x.get("id") and x.get("active", True)}
    items = [lib[i] for i in (st.get("ids") or []) if i in lib]
    if not items:
        return off
    now = time.time() if now is None else now
    rot = float(st.get("rotate") or 0)
    idx = int(now // rot) % len(items) if rot > 0 and len(items) > 1 else 0
    it = items[idx]
    return {"on": True, "id": it["id"], "name": it.get("name", ""), "logo": it.get("logo", ""), "label": st.get("label", ""), "slot": slot}


def graphic_ctx(game, ui, gid, d):
    """Python mirror of makeCtx() in engine.js, enough to resolve sponsor specs."""
    game = game or {}
    side = ((ui or {}).get("sides") or {}).get(gid) or (d or {}).get("side") or "home"
    if side == "batting":
        side = game.get("battingSide") or "away"
    if side == "fielding":
        side = game.get("fieldingSide") or "home"
    ctx = dict(game)
    ctx["team"] = game.get(side) or {}
    ctx["opp"] = game.get("away" if side == "home" else "home") or {}
    ctx["side"] = side
    return ctx


def graphic_sponsors(game, ui, gid, d, now=None):
    """All sponsors a graphic is showing: its own slot plus per-row sponsors (Lineup)."""
    ctx = graphic_ctx(game, ui, gid, d)
    out = []
    sp = sponsor_for(ui, (d or {}).get("sponsorSlot"), now, ctx)
    if sp["on"]:
        out.append(sp)
    if (d or {}).get("rowSponsors"):
        rows = get_path(ctx, d.get("rowBind") or "team.lineup") or []
        for row in rows if isinstance(rows, list) else []:
            r = sponsor_for(ui, d["rowSponsors"], now, dict(ctx, row=row))
            if r["on"]:
                out.append(r)
    return out


def save_photo(key, ext, raw):
    d = MEDIA_DIRS["photos"]
    os.makedirs(d, exist_ok=True)
    # Replace any earlier photo for this player, whatever its format.
    for fn in os.listdir(d):
        stem, e = os.path.splitext(fn)
        if slug(stem) == key and e.lower() in MEDIA_EXT and fn != key + ext:
            os.makedirs(os.path.join(d, "_replaced"), exist_ok=True)
            os.replace(os.path.join(d, fn), os.path.join(d, "_replaced", fn))
    with open(os.path.join(d, key + ext), "wb") as f:
        f.write(raw)
    _media_cache["t"] = 0
    return "/media/photos/" + key + ext


def remove_photo(key, team=None, number=None):
    """Moves a player's uploaded photo(s) to media/photos/_removed (recoverable)."""
    d = MEDIA_DIRS["photos"]
    keys = {key}
    if team and number:
        keys.add(slug("%s-%s" % (team, number)))
    n = 0
    try:
        for fn in os.listdir(d):
            stem, e = os.path.splitext(fn)
            if slug(stem) in keys and e.lower() in MEDIA_EXT:
                os.makedirs(os.path.join(d, "_removed"), exist_ok=True)
                os.replace(os.path.join(d, fn), os.path.join(d, "_removed", fn))
                n += 1
    except OSError:
        pass
    _media_cache["t"] = 0
    return n




class SponsorLog:
    """On-air time and takes per sponsor, per day and per graphic, for sponsor reporting.
    Counts a second for each second a sponsored graphic is taken in. When running inside OBS
    and logOnlyWhenLive is on, it only counts while OBS is streaming or recording."""

    def __init__(self):
        self.lock = threading.Lock()
        self.data = load_json(SPONSOR_LOG_PATH, {"days": {}})
        self.dirty = False
        self.last_save = time.time()

    def _row(self, day, sponsor, gid):
        d = self.data.setdefault("days", {}).setdefault(day, {})
        s = d.setdefault(sponsor["id"], {"name": sponsor["name"], "seconds": 0, "takes": 0, "graphics": {}})
        s["name"] = sponsor["name"] or s.get("name", "")
        return s, s["graphics"].setdefault(gid, {"seconds": 0, "takes": 0})

    def tick(self, hub):
        if not obs_is_live(hub):
            return
        day = datetime.date.today().isoformat()
        now = time.time()
        with hub.lock:
            vis = [g for g, v in (hub.ui.get("visible") or {}).items() if v]
            graphics = hub.templates.get("graphics") or {}
            ui = hub.ui
            game = hub.game
        with self.lock:
            for gid in vis:
                for sp in graphic_sponsors(game, ui, gid, graphics.get(gid), now):
                    s, g = self._row(day, sp, gid)
                    s["seconds"] += 1
                    g["seconds"] += 1
                    self.dirty = True
            if self.dirty and now - self.last_save > 10:
                self.save()

    def take(self, hub, gid):
        if not obs_is_live(hub):
            return
        with hub.lock:
            sps = graphic_sponsors(hub.game, hub.ui, gid, (hub.templates.get("graphics") or {}).get(gid))
        if not sps:
            return
        with self.lock:
            for sp in sps:
                s, g = self._row(datetime.date.today().isoformat(), sp, gid)
                s["takes"] += 1
                g["takes"] += 1
            self.dirty = True

    def save(self):
        save_json(SPONSOR_LOG_PATH, self.data)
        self.dirty = False
        self.last_save = time.time()

    def reset(self):
        with self.lock:
            if os.path.exists(SPONSOR_LOG_PATH):
                os.replace(SPONSOR_LOG_PATH, SPONSOR_LOG_PATH + ".bak")
            self.data = {"days": {}}
            self.save()

    def csv(self):
        lines = ["date,sponsor,graphic,seconds,minutes,takes"]
        with self.lock:
            for day in sorted(self.data.get("days", {})):
                for sid, s in sorted(self.data["days"][day].items(), key=lambda kv: kv[1].get("name", "")):
                    for gid, g in sorted(s.get("graphics", {}).items()):
                        name = '"%s"' % str(s.get("name", sid)).replace('"', '""')
                        lines.append("%s,%s,%s,%d,%.1f,%d" % (day, name, gid, g["seconds"], g["seconds"] / 60.0, g["takes"]))
        return "\n".join(lines) + "\n"


def obs_is_live(hub):
    if REPLAY.active:
        return False   # rehearsing with a replayed game never counts as sponsor exposure
    if not IN_OBS or not ((hub.ui.get("sponsors") or {}).get("logOnlyWhenLive", True)):
        return True
    try:
        return bool(obs.obs_frontend_streaming_active() or obs.obs_frontend_recording_active())
    except Exception:
        return True


class SponsorTicker:
    def __init__(self):
        self.stop_evt = threading.Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_evt.clear()

        def run():
            nxt = time.time()
            while not self.stop_evt.is_set():
                try:
                    HUB.sponsor_log.tick(HUB)
                except Exception as e:
                    log("Sponsor log error: %s" % e)
                nxt += 1.0
                self.stop_evt.wait(max(0.05, nxt - time.time()))
            try:
                HUB.sponsor_log.save()
            except Exception:
                pass
        self.thread = threading.Thread(target=run, name="bbg-sponsors", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_evt.set()
        if self.thread:
            self.thread.join(timeout=3)


SPONSOR_TICKER = SponsorTicker()


# ---------------------------------------------------------------------------
# Hub: shared state + pub/sub to browser pages
# ---------------------------------------------------------------------------
class Hub:
    def __init__(self):
        self.lock = threading.RLock()
        self.cfg = deep_merge(copy.deepcopy(DEFAULT_CONFIG), load_json(CONFIG_PATH, {}))
        if MANUAL_ONLY:
            self.cfg["source"] = "manual"
        self.ui = deep_merge(copy.deepcopy(DEFAULT_UI), load_json(UI_PATH, {}))
        if not self.ui.get("presetsSeeded"):
            self.ui.setdefault("presets", {})
            for k, v in PRESET_SEEDS.items():
                self.ui["presets"].setdefault(k, dict(v))
            self.ui["presetsSeeded"] = True
            save_json(UI_PATH, self.ui)
        # one-time upgrades of starter presets made by earlier versions
        pr_ = self.ui.get("presets") or {}
        if not self.ui.get("presetsV2"):
            if (pr_.get("anthem") or {}).get("layout") == "lower":
                pr_["anthem"].update({"layout": "anthem", "name": "National Anthem"})
                if pr_["anthem"].get("sub") in ("", None, "National anthem"):
                    pr_["anthem"]["sub"] = "Performing the national anthem"
            pr_.setdefault("honoree", dict(PRESET_SEEDS["honoree"]))
            self.ui["presetsV2"] = True
        if not self.ui.get("presetsV3"):
            w_ = pr_.get("weather") or {}
            if w_.get("text", "").startswith("Temperature | 72"):
                w_["text"] = PRESET_SEEDS["weather"]["text"]
            self.ui["presetsV3"] = True
            save_json(UI_PATH, self.ui)
        self.base_templates = self._load_templates()
        self.templates = with_presets(self.base_templates, self.ui)
        if self._sync_style_sets():
            save_json(UI_PATH, self.ui)
        self.game = finalize(empty_game(), self.cfg, {})
        self.status = {"ok": False, "message": "Starting", "updated": 0, "source": self.cfg["source"]}
        self.subs = []
        self.memory = {}
        self.closing = False
        self.timers = {}
        self.adapter = None
        self.sponsor_log = SponsorLog()
        self.standings = {"groups": []}
        self._last_play_id = None
        self._last_recap = None

    def _load_templates(self):
        default = load_json(TPL_DEFAULT, {"graphics": {}})
        user = load_json(TPL_USER, None) if os.path.exists(TPL_USER) else None
        if not (user and isinstance(user.get("graphics"), dict)):
            return default
        # Saved templates (editor) follow package updates: new graphics are added and graphics the editor never
        # changed are replaced with the updated versions; edited graphics are left exactly as saved.
        pkg = None
        try:
            for fn in sorted(os.listdir(PKG_DIR)):
                if fn.endswith(".json"):
                    d = load_json(os.path.join(PKG_DIR, fn), None)
                    if d and d.get("name") == user.get("name"):
                        pkg = d
                        break
        except OSError:
            pass
        if pkg is None and default.get("name") == user.get("name"):
            pkg = default
        if pkg:
            up, changed = upgrade_templates(user, pkg)
            if changed:
                save_json(TPL_USER, up)
                print("[Baseball Graphics] Saved templates updated from the %s package: %s" % (pkg.get("name"), ", ".join(changed[:12]) + (" ..." if len(changed) > 12 else "")))
            return up
        return user

    # -- pub/sub ----------------------------------------------------------
    def subscribe(self, view="all", layer=None, ids=None):
        """view: "overlay" (a browser source: only the graphics it can show), "control" (control panel: names and
        groups, no artwork), or "all" (the editor and anything else: everything)."""
        q = queue.Queue(maxsize=200)
        q.view = view if view in ("overlay", "control") else "all"
        q.layer = layer if layer in LAYER_KEYS else None
        q.ids = tuple(sorted(set(i for i in (ids or "").split(",") if i))) or None
        with self.lock:
            self.subs.append(q)
        return q

    def unsubscribe(self, q):
        with self.lock:
            if q in self.subs:
                self.subs.remove(q)

    def publish(self, kind, payload, views=None):
        """Send to every subscriber. Templates go out per view, so an overlay gets only the graphics it can show
        and the control panel gets no artwork (the whole library is several MB of artwork)."""
        with self.lock:
            subs = list(self.subs)
        if kind != "templates":
            msg = json.dumps({"type": kind, "data": payload}, default=str)
            for q in subs:
                try:
                    q.put_nowait(msg)
                except queue.Full:
                    pass
            return
        cache = {}
        for q in subs:
            v, ly, ids_ = getattr(q, "view", "all"), getattr(q, "layer", None), getattr(q, "ids", None)
            if views and v not in views:
                continue
            key = (v, ly, ids_) if v == "overlay" else (v,)
            if key not in cache:
                cache[key] = json.dumps({"type": kind, "data": self.templates_view(v, ly, payload, ids_)}, default=str)
            try:
                q.put_nowait(cache[key])
            except queue.Full:
                pass

    def lean_ids(self, tpl=None, ui=None, layer=None, ids=None):
        """Graphics an overlay needs: this package's own, the active graphics set's, and anything on air."""
        tpl = tpl if tpl is not None else self.templates
        ui = ui if ui is not None else self.ui
        gr = tpl.get("graphics") or {}
        a = ui.get("activeSet")
        st = (ui.get("sets") or {}).get(a) if a else None
        if isinstance(st, dict) and st.get("gids"):
            want = set(st.get("gids") or [])            # a graphics set is picked: only its graphics are loaded
            want.update(g for g, d in gr.items() if d.get("presetId"))
        else:
            want = set(g for g, d in gr.items() if not d.get("libPkg"))
        want.update(g for g, on in (ui.get("visible") or {}).items() if on)
        if ids and "all" not in ids:
            want = set(g for g in want if g in ids or (ui.get("visible") or {}).get(g)) | set(ids)
        if layer:
            want = set(g for g in want if g in gr and layer_of(gr[g].get("group")) == layer)
        return set(g for g in want if g in gr)

    def templates_view(self, view, layer=None, tpl=None, ids=None):
        tpl = tpl if tpl is not None else self.templates
        if view == "control":
            out = dict(tpl)
            out["graphics"] = dict((g, dict((k, v) for k, v in d.items() if k != "elements")) for g, d in (tpl.get("graphics") or {}).items())
            return out
        if view == "overlay":
            ids = self.lean_ids(tpl, None, layer, ids)
            out = dict(tpl)
            out["graphics"] = dict((g, d) for g, d in (tpl.get("graphics") or {}).items() if g in ids)
            out["lean"] = True
            return out
        return tpl

    def snapshot(self, view="all", layer=None, ids=None):
        with self.lock:
            return {"game": self.game, "ui": self.ui, "templates": self.templates_view(view, layer, None, ids),
                    "status": self.status, "replay": REPLAY.info(), "config": self.public_config(), "version": VERSION, "edition": EDITION, "serverNow": int(time.time() * 1000),
                    "sports": [{"key": k, "label": v["label"], "points": v["points"]} for k, v in SPORTS.items()], "fonts": font_list(),
                    "categories": [{"key": k, "label": lab, "single": one} for k, lab, one in CATEGORIES]}

    def public_config(self):
        return copy.deepcopy(self.cfg)

    # -- mutations --------------------------------------------------------
    def set_game(self, game, message="Live data OK"):
        with self.lock:
            self.game = finalize(game, self.cfg, self.memory)
            lp_ = self.game.get("lastPlay") or {}
            sc_ = self.game.get("scorerSide") or lp_.get("team")
            if self.game.get("sport") and sc_ in ("away", "home"):
                self.game["scorer"] = self.game[sc_]
            self.game["standings"] = self._standings_view()
            team_places(self.game)
            _d = datetime.date.today()
            self.game["dateText"] = "%s %d, %d" % (_d.strftime("%B"), _d.day, _d.year)
            self.game["umps"] = umpire_rows(self.ui.get("umpires") or "", self.game.get("officials") or [])
            notes = self.ui.get("notes") or {}
            self.game["velo"] = {"ps": str((self.game.get("pitch") or {}).get("speed") or notes.get("ps") or ""),
                                 "ev": str((self.game.get("hit") or {}).get("ev") or notes.get("ev") or "")}
            pk = self.ui.get("pick") or {}
            self.game["picked"] = pick_player(self.game, pk) if pk.get("on") else {}
            try:
                self.game["split"] = split_rows(self.ui, self.game)
            except Exception as e:
                print("[Baseball Graphics] split card:", e)
                self.game["split"] = {"rows": []}
            self.game["road"] = road_ahead(self.ui)
            ra_ = getattr(self, "road_auto", None) or {}
            if not self.game["road"]["cells"] and ra_.get("cells"):
                self.game["road"]["cells"] = ra_["cells"]
            self.game["nextGame"] = ra_.get("next") or {}
            if (self.game.get("picked") or {}).get("bat") and self.game.get("pickedSplits"):
                self.game["picked"]["bat"]["splits"] = self.game["pickedSplits"].get("bat") or {}
                self.game["picked"]["pit"]["splits"] = self.game["pickedSplits"].get("pit") or {}
            for who in ("batter", "pitcher"):
                pl_ = self.game.get(who) or {}
                pl_["bioLine"] = bio_line(pl_)
            if (self.game.get("picked") or {}).get("bat"):
                for k_ in ("bat", "pit"):
                    self.game["picked"][k_]["bioLine"] = bio_line(self.game["picked"][k_])
            self.game["around"] = around_league(getattr(self, "scoreboard", []), self.game)
            b_ = self.game.get("batter") or {}
            up_ = next((p for p in (self.game.get(self.game.get("battingSide") or "away") or {}).get("lineup", []) if p.get("isUp")), {})
            d_ = parse_today(up_.get("today")) or parse_today((b_.get("today") or {}).get("hab"))
            b_["forText"] = ("%d for %d" % (d_["h"], d_["ab"])) if d_ else ""
            b_["playsText"] = play_words(d_["notes"]) if d_ else ""
            if (self.game.get("picked") or {}).get("bat") and (self.ui.get("pick") or {}).get("on"):
                pb = self.game["picked"]["bat"]
                pt = self.game.get(self.game["picked"].get("side") or "home") or {}
                row = next((r for r in pt.get("lineup", []) if r.get("name") == pb.get("name")), {})
                d2 = parse_today(row.get("today"))
                self.game["potg"] = {"name": pb.get("name", ""), "photo": pb.get("photo", ""), "teamName": pt.get("name", ""),
                                     "line": ", ".join(x for x in ((d2["hab"].replace("-", " for ") if d2 else ""), play_words(d2["notes"]) if d2 else "") if x)}
            try:
                show_lists(self.ui, self.game)
            except Exception as e:
                print("[Baseball Graphics] show lists:", e)
            self.game["ticker"] = {"items": ticker_items(self.game, self.ui, getattr(self, "scoreboard", []) if not self.game.get("sport") else []),
                                   "label": (self.ui.get("ticker") or {}).get("label", ""),
                                   "speed": (self.ui.get("ticker") or {}).get("speed", 110)}
            self.status = {"ok": True, "message": message, "updated": time.time(), "source": self.cfg["source"],
                           "replay": bool(game.get("replay"))}
        self.publish("game", self.game)
        self.publish("status", self.status)
        try:
            self.check_triggers(self.game)
            self.check_state_triggers(self.game)
        except Exception as e:
            print("[Baseball Graphics] trigger error:", e)

    def set_standings(self, st):
        with self.lock:
            self.standings = st
            self.game["standings"] = self._standings_view()
            team_places(self.game)
        self.publish("game", self.game)

    def _standings_view(self):
        """Standings with logos / colours filled in from team settings and media/logos."""
        st = copy.deepcopy(self.standings or {"groups": []})
        game = self.game or {}
        by_name = {}
        for side in ("away", "home"):
            t = game.get(side) or {}
            for k in (t.get("name"), t.get("abbr")):
                if k:
                    by_name[slug(k)] = t
        for g in st.get("groups", []):
            for t in g.get("teams", []):
                gt = by_name.get(slug(t.get("name"))) or by_name.get(slug(t.get("abbr"))) or {}
                if gt.get("name"):
                    t["name"] = gt["name"]   # the club's own spelling (Teams settings) over the feed's
                t["logo"] = gt.get("logo") or media_for("logos", t.get("abbr"), t.get("name")) or ""
                t["color"] = gt.get("color") or ""
                t["isGame"] = bool(gt)
                if not t.get("abbr"):
                    t["abbr"] = gt.get("abbr") or (t.get("name") or "")[:3].upper()
        return st

    def refinalize(self):
        """Re-derive the current game (e.g. after a headshot upload) without waiting for the next poll."""
        with self.lock:
            g = copy.deepcopy(self.game)
        if g.get("source"):
            self.set_game(g)

    def set_error(self, message):
        with self.lock:
            self.status = {"ok": False, "message": message, "updated": time.time(), "source": self.cfg["source"]}
        self.publish("status", self.status)

    def save_ui(self):
        save_json(UI_PATH, self.ui)

    def update_ui(self, patch):
        tpl_changed = False
        replay_stopped = False
        with self.lock:
            vis_before = dict(self.ui.get("visible", {}))
            before = preset_sig(self.ui)
            sport_before = self.ui.get("sport")
            deep_merge(self.ui, patch)
            ops_commands(self.ui)
            if self.ui.get("sport") not in SPORT_KEYS:
                self.ui["sport"] = "baseball"
            if self.ui.get("sport") != sport_before:
                self._last_play_id = None
                self._last_recap = None
            if self.ui.get("sport") in SPORTS:
                sport_state(self.ui, self.ui["sport"])
                if self.ui.get("sport") != sport_before and REPLAY.active:
                    REPLAY.stop()        # a baseball replay ends when another sport takes over
                    replay_stopped = True     # fill in defaults so the panel has every field
            # presets: a null value deletes; a clock preset starts timing when it is taken
            sets_ = self.ui.get("sets")
            if isinstance(sets_, dict):
                gone = self.ui.setdefault("styleSetsRemoved", [])
                for k in [k for k, v in sets_.items() if not isinstance(v, dict)]:
                    del sets_[k]
                    if k.startswith("style_") and k not in gone:
                        gone.append(k)      # a deleted style set stays deleted until Restore style sets
                for k, v in ((patch.get("sets") or {}).items()):
                    if isinstance(v, dict) and isinstance(v.get("gids"), list):
                        sets_[k]["gids"] = list(v["gids"])
                        if "auto" not in v:
                            sets_[k]["auto"] = False   # edited by hand: future updates leave it alone
            if patch.get("styleSetsReset"):
                self.ui.pop("styleSetsReset", None)
                self.ui["styleSetsRemoved"] = []
                for k in [k for k in (self.ui.get("sets") or {}) if k.startswith("style_")]:
                    del self.ui["sets"][k]
                tpl_changed = True
            pr = self.ui.get("presets")
            if isinstance(pr, dict):
                for k in [k for k, v in pr.items() if not isinstance(v, dict)]:
                    del pr[k]
                for gid, on in (patch.get("visible") or {}).items():
                    if on and not vis_before.get(gid) and gid.startswith("p_") and gid[2:] in pr:
                        p_ = pr[gid[2:]]
                        if p_.get("mode") in ("up", "dur") and not p_.get("hold"):
                            p_["since"] = int(time.time() * 1000)
            cols_ = self.ui.get("colors")
            if isinstance(cols_, dict):
                for sn_ in list(cols_):
                    m_ = cols_[sn_]
                    if not isinstance(m_, dict):
                        del cols_[sn_]
                        continue
                    for k_ in [k_ for k_, v_ in m_.items() if not isinstance(v_, str)]:
                        del m_[k_]      # a null value resets that colour
                    if not m_:
                        del cols_[sn_]
            if preset_sig(self.ui) != before:
                self.templates = with_presets(self.base_templates, self.ui)
                tpl_changed = True
            if tpl_changed:
                self._sync_style_sets()
            if self.ui.get("activeSet") and self.ui["activeSet"] not in (self.ui.get("sets") or {}):
                self.ui["activeSet"] = ""
            self.save_ui()
            ui = copy.deepcopy(self.ui)
            tpl = self.templates
            lean = self.lean_ids()
            lean_changed = lean != getattr(self, "_lean_ids", None)
            self._lean_ids = lean
        if tpl_changed:
            self.publish("templates", tpl)
        elif lean_changed:
            self.publish("templates", tpl, views=("overlay",))    # a new set, or a graphic taken from outside it
        self.publish("ui", ui)
        for g, on in (patch.get("visible") or {}).items():
            if on and not vis_before.get(g):
                self._arm_autohide(g)
                self.sponsor_log.take(self, g)
        if any(k in patch for k in ("pick", "ticker", "umpires", "split", "schedule", "probables", "roadAhead")) or any(k in (patch.get("notes") or {}) for k in ("ps", "ev", "lfTitle", "lfLine")):
            self.refinalize()
        if replay_stopped:
            self.publish("replay", REPLAY.info())
        if "sport" in patch or "sports" in patch:
            if self.current_sport() != "baseball" and ("sport" in patch or any("standings_text" in (v or {}) for v in (patch.get("sports") or {}).values())):
                POLLER.poll_standings("sport:" + self.current_sport(), True)
            elif "sport" in patch:
                POLLER.kick()
            POLLER.nudge()
        if "manual" in patch and self.cfg["source"] == "manual" and self.current_sport() == "baseball":
            self.set_game(manual_game(self.ui["manual"]))
            if "standings_text" in (patch.get("manual") or {}):
                POLLER.poll_standings("manual", True)

    def _arm_autohide(self, gid):
        secs = float(((self.templates.get("graphics") or {}).get(gid) or {}).get("autoHide") or 0)
        if secs <= 0:
            return
        token = object()
        self.timers[gid] = token

        def fire():
            if self.timers.get(gid) is token and self.ui.get("visible", {}).get(gid):
                self.update_ui({"visible": {gid: False}})
        t = threading.Timer(secs, fire)
        t.daemon = True
        t.start()

    def toggle(self, gid, on=None):
        with self.lock:
            cur = bool(self.ui.get("visible", {}).get(gid))
        target = (not cur) if on is None else bool(on)
        patch = {"visible": {gid: target}}
        # Exclusive groups: taking a graphic clears others in the same group (e.g. lower thirds)
        group = ((self.templates.get("graphics") or {}).get(gid) or {}).get("group")
        if target and group:
            for other, d in (self.templates.get("graphics") or {}).items():
                if other != gid and d.get("group") == group and self.ui.get("visible", {}).get(other):
                    patch["visible"][other] = False
        self.update_ui(patch)
        return target

    def resolve_gid(self, gid):
        """A graphic id typed for any style (e.g. strike_zone) -> this install's id in the active set, else as given."""
        gid = str(gid or "")
        graphics = self.templates.get("graphics") or {}
        with self.lock:
            sets_, act = self.ui.get("sets") or {}, self.ui.get("activeSet") or ""
        gids = list(((sets_.get(act) or {}).get("gids") or [])) if act else []
        for g in gids:
            if g == gid or g.endswith("__" + gid):
                return g
        return gid if gid in graphics else gid

    def rundown(self, op, index=None):
        """Rundown (GAME OPS > Rundown): next / prev take the neighbouring item and clear the one on air; take /
        clear act on the current item; goto jumps to an item."""
        with self.lock:
            o = self.ui.setdefault("ops", {})
            items = [g for g in (o.get("rundown") or []) if isinstance(g, str) and g]
            idx = ival(o.get("rundownIdx"), -1)
            vis = dict(self.ui.get("visible") or {})
        if not items:
            return -1
        cur = items[idx] if 0 <= idx < len(items) else None
        if op in ("next", "prev", "goto"):
            new = idx + 1 if op == "next" else (idx - 1 if op == "prev" else ival(index, 0))
            new = max(0, min(len(items) - 1, new))
            patch = {"ops": {"rundownIdx": new}, "visible": {}}
            if cur and vis.get(cur):
                patch["visible"][cur] = False
            self.update_ui(patch)
            if new != idx or not vis.get(items[new]):
                self.toggle(items[new], True)
            return new
        if op == "take" and cur:
            self.toggle(cur, True)
        elif op == "clear" and cur:
            self.toggle(cur, False)
        return idx

    def command(self, do, arg=None):
        """One-word commands for Stream Deck, Bitfocus Companion or any tool that can open a URL (GET /api/cmd?do=...)."""
        do = str(do or "").lower()
        if do in ("toggle", "on", "off"):
            g = self.resolve_gid(arg)
            return self.toggle(g, None if do == "toggle" else do == "on")
        if do == "alloff":
            return self.all_off()
        if do in ("next", "prev", "take", "clear", "goto"):
            return self.rundown(do, arg)
        ops = {"clock_start": {"pcCmd": "start"}, "clock_stop": {"pcCmd": "stop"}, "clock_reset": {"pcCmd": "reset"},
               "delay_start": {"delayCmd": "start"}, "delay_stop": {"delayCmd": "stop"}, "k_up": {"kCmd": "+1"}, "k_down": {"kCmd": "-1"},
               "shout_next": None}
        if do == "shout_next":
            with self.lock:
                o = self.ui.get("ops") or {}
                n = len([x for x in str(o.get("shouts") or "").split("\n") if x.strip()])
                i = (ival(o.get("shoutIdx")) + 1) % max(1, n)
            return self.update_ui({"ops": {"shoutIdx": i}})
        if do in ops:
            return self.update_ui({"ops": ops[do]})
        raise ValueError("Unknown command: %s" % do)

    def all_off(self, keep=None):
        keep = set(keep or [])
        with self.lock:
            patch = {"visible": {g: False for g, v in self.ui.get("visible", {}).items() if v and g not in keep}}
        self.update_ui(patch)

    def set_templates(self, doc):
        if not isinstance(doc, dict) or not isinstance(doc.get("graphics"), dict):
            raise ValueError("Template document must contain a 'graphics' object")
        doc = strip_presets(doc)
        with self.lock:
            self.base_templates = doc
            save_json(TPL_USER, doc)
            self.templates = with_presets(doc, self.ui)
            doc = self.templates
            changed = self._sync_style_sets()
            ui = copy.deepcopy(self.ui)
        self.publish("templates", doc)
        if changed:
            save_json(UI_PATH, ui)
            self.publish("ui", ui)
        if IN_OBS:
            request_scene_sync()

    def reset_templates(self):
        if os.path.exists(TPL_USER):
            os.replace(TPL_USER, TPL_USER + ".bak")
        with self.lock:
            self.base_templates = self._load_templates()
            self.templates = with_presets(self.base_templates, self.ui)
            changed = self._sync_style_sets()
            ui = copy.deepcopy(self.ui)
        self.publish("templates", self.templates)
        if changed:
            save_json(UI_PATH, ui)
            self.publish("ui", ui)
        if IN_OBS:
            request_scene_sync()

    def current_sport(self):
        sp = self.ui.get("sport") or "baseball"
        return sp if sp in SPORTS else "baseball"

    def sport_tick(self):
        """Poller step for basketball / football / hockey: settle clocks at period end or a penalty running out, then publish."""
        sport = self.current_sport()
        with self.lock:
            st = sport_state(self.ui, sport)
            ev = sport_next_event(st)
            if ev and _now_ms() >= ev:
                sport_settle(st)
                save_json(UI_PATH, self.ui)
            g = sport_game(sport, st)
            running = st["clock"].get("running")
        self.set_game(g, "%s: manual scoring" % SPORTS[sport]["label"])
        return running

    def sport_action(self, body):
        sport = body.get("sport") or self.current_sport()
        if sport not in SPORTS:
            raise ValueError("Unknown sport")
        with self.lock:
            st = sport_state(self.ui, sport)
            sport_op(st, sport, body)
            save_json(UI_PATH, self.ui)
            ui = copy.deepcopy(self.ui)
            g = sport_game(sport, st) if sport == self.current_sport() else None
        self.publish("ui", ui)
        if g is not None:
            self.set_game(g, "%s: manual scoring" % SPORTS[sport]["label"])
        return st

    def _sync_style_sets(self):
        """Keep one automatic graphics set per style. Sets edited by hand (auto False) or deleted are left alone."""
        sets_ = self.ui.setdefault("sets", {})
        gone = set(self.ui.get("styleSetsRemoved") or [])
        want = style_sets(self.templates)
        changed = False
        for k, v in want.items():
            cur = sets_.get(k)
            if k in gone or (isinstance(cur, dict) and cur.get("auto") is False):
                continue
            if cur != v:
                sets_[k] = v
                changed = True
        for k in [k for k, v in sets_.items() if k.startswith("style_") and isinstance(v, dict) and v.get("auto") and k not in want]:
            del sets_[k]
            changed = True
        if self.ui.get("activeSet") and self.ui["activeSet"] not in sets_:
            self.ui["activeSet"] = ""
            changed = True
        return changed

    def reset_triggers(self):
        """Forget the last play seen, so a newly selected game never fires a stinger for an old play."""
        self._last_play_id = None
        self._last_recap = None

    def _trigger_allowed(self, graphics):
        """Graphics that may fire on their own: the active set's, or (no set) this package's own, never other packages' copies."""
        with self.lock:
            a = self.ui.get("activeSet") or ""
            st = (self.ui.get("sets") or {}).get(a) or {}
        ids = st.get("gids") if a else None
        if ids:
            return set(ids)
        return set(g for g, d in graphics.items() if not (d or {}).get("libPkg"))

    def check_state_triggers(self, game):
        """Graphics with trigger "INNING" come up when a half-inning ends (the inning recap)."""
        key = (game.get("halfRecap") or {}).get("label") or ""
        prev, self._last_recap = getattr(self, "_last_recap", None), key
        if not key or prev is None or key == prev:
            return []
        rp = game.get("replay") or {}
        if rp and not rp.get("fresh"):
            return []
        with self.lock:
            tr = self.ui.get("triggers") or {}
            graphics = dict((self.templates.get("graphics") or {}))
        if not tr.get("enabled", True):
            return []
        fired = []
        allowed = self._trigger_allowed(graphics)
        for gid, d in graphics.items():
            spec = [x.strip().upper() for x in str(d.get("trigger") or "").split(",")]
            if "INNING" in spec and not (tr.get("off") or {}).get(gid) and gid in allowed:
                delay = float(d.get("triggerDelay") or 0)
                t = threading.Timer(max(0.05, delay), lambda gid=gid: self.toggle(gid, True))
                t.daemon = True
                t.start()
                fired.append(gid)
        return fired

    def check_triggers(self, game):
        """Take graphics that have a "trigger" (play types, e.g. "HR" or "WP,PB") when a new play of that type happens."""
        lp = game.get("lastPlay") or {}
        pid = lp.get("id") or ""
        prev, self._last_play_id = self._last_play_id, pid
        if not pid or prev is None or pid == prev:
            return []
        rp = game.get("replay") or {}
        if rp and not rp.get("fresh"):
            return []
        with self.lock:
            tr = self.ui.get("triggers") or {}
            graphics = dict((self.templates.get("graphics") or {}))
            notes = dict(self.ui.get("notes") or {})
        if not tr.get("enabled", True):
            return []
        ctx = dict(game)
        ctx["lastPlay"] = play_with_notes(lp, notes)
        fired = []
        allowed = self._trigger_allowed(graphics)
        for gid, d in graphics.items():
            spec = d.get("trigger")
            if not spec or (tr.get("off") or {}).get(gid) or gid not in allowed:
                continue
            if (d.get("sport") or "baseball") not in (game.get("sport") or "baseball", "all"):
                continue
            if str(lp.get("type", "")).upper() not in [s.strip().upper() for s in str(spec).split(",") if s.strip()]:
                continue
            if d.get("triggerIf") and not py_cond(d["triggerIf"], ctx):
                continue
            delay = float(d.get("triggerDelay") or 0)
            if delay > 0:
                t = threading.Timer(delay, lambda gid=gid: self.toggle(gid, True))
                t.daemon = True
                t.start()
            else:
                self.toggle(gid, True)
            fired.append(gid)
        return fired

    def update_config(self, patch):
        if MANUAL_ONLY and isinstance(patch, dict):
            patch = dict(patch)
            patch.pop("source", None)
        with self.lock:
            deep_merge(self.cfg, patch)
            save_json(CONFIG_PATH, self.cfg)
            self.memory = {}
        self.publish("config", self.public_config())
        POLLER.kick()


HUB = None


# ---------------------------------------------------------------------------
# Poller
# ---------------------------------------------------------------------------
class Poller:
    def __init__(self):
        self.thread = None
        self.stop_evt = threading.Event()
        self.kick_evt = threading.Event()
        self.adapters = {}

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_evt.clear()
        self.thread = threading.Thread(target=self.run, name="bbg-poller", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_evt.set()
        self.kick_evt.set()
        if self.thread:
            self.thread.join(timeout=3)

    def kick(self):
        for a in self.adapters.values():
            a.cache.clear()
        self.soft = False
        self.kick_evt.set()

    def nudge(self):
        """Re-render now without refetching standings (replay seeks)."""
        self.soft = True
        self.kick_evt.set()

    def poll_standings(self, src, force=False):
        now = time.time()
        if not force and now - getattr(self, "_st_t", 0) < 300 and getattr(self, "_st_src", None) == src:
            return
        self._st_t, self._st_src = now, src
        try:
            if src.startswith("sport:"):
                st = parse_standings_text(sport_state(HUB.ui, src[6:]).get("standings_text", ""))
            elif src == "manual":
                st = parse_standings_text((HUB.ui.get("manual") or {}).get("standings_text", ""))
            st["error"] = ""
        except Exception as e:
            st = dict(HUB.standings or {"groups": []})
            st["error"] = str(e)
        HUB.set_standings(st)

    def run(self):
        while not self.stop_evt.is_set():
            forced = self.kick_evt.is_set() and not getattr(self, "soft", False)
            self.soft = False
            self.kick_evt.clear()
            src = "manual"
            sport = HUB.current_sport()
            if sport != "baseball":
                src = "sport:" + sport
            self.poll_standings(src, forced)
            try:
                if sport != "baseball":
                    running = HUB.sport_tick()
                    wait = 1.0 if running else 2.0
                elif src == "manual":
                    HUB.set_game(manual_game(HUB.ui["manual"]))
                    wait = 5.0
            except Exception as e:
                HUB.set_error(str(e))
                wait = max(3.0, float(HUB.cfg.get("poll_seconds", 2)))
            self.kick_evt.wait(wait)


POLLER = Poller()


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "BaseballGraphics/" + VERSION
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # keep OBS log quiet
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, default=str).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return {}
        raw = self.rfile.read(n)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        path, qs = u.path, urllib.parse.parse_qs(u.query)
        try:
            if path in ("/", "/index.html"):
                return self._send(302, "", extra={"Location": "/control.html"})
            view_ = (qs.get("view") or ["all"])[0]
            layer_ = (qs.get("layer") or [None])[0]
            ids_ = (qs.get("g") or [""])[0]
            if path == "/api/cmd":
                try:
                    res = HUB.command((qs.get("do") or [""])[0], (qs.get("g") or qs.get("i") or [None])[0])
                except ValueError as e:
                    return self._send(400, {"error": str(e)})
                return self._send(200, {"ok": True, "result": res})
            if path == "/ws":
                return self._websocket(view_, layer_, ids_)
            if path == "/events":
                return self._sse(view_, layer_, ids_)
            if path == "/api/state":
                return self._send(200, HUB.snapshot(view_, layer_, tuple(i for i in ids_.split(",") if i) or None))
            if path == "/api/templates":
                return self._send(200, HUB.templates)
            if path == "/api/templates/default":
                return self._send(200, load_json(TPL_DEFAULT, {"graphics": {}}))
            if path == "/api/packages":
                out = []
                try:
                    for fn in sorted(os.listdir(PKG_DIR)):
                        if fn.endswith(".json"):
                            d = load_json(os.path.join(PKG_DIR, fn), {})
                            out.append({"id": fn[:-5], "name": d.get("name", fn[:-5]), "description": d.get("description", ""),
                                        "graphics": len(d.get("graphics", {}))})
                except OSError:
                    pass
                return self._send(200, {"packages": out})
            if path.startswith("/api/packages/"):
                pid = re.sub(r"[^a-zA-Z0-9_-]", "", path.rsplit("/", 1)[-1])
                fp = os.path.join(PKG_DIR, pid + ".json")
                if not os.path.isfile(fp):
                    return self._send(404, {"error": "no such package"})
                pd_ = load_json(fp, {})
                with HUB.lock:
                    cm_ = color_map(HUB.ui, pd_.get("name"))
                if cm_:      # your colour changes (Custom > Colors) apply to exports too
                    pd_["graphics"] = dict((k, recolor_graphic(v, cm_)) for k, v in (pd_.get("graphics") or {}).items())
                    pd_["theme"] = _walk_colors(pd_.get("theme") or {}, lambda s_, _k: recolor_str(s_, cm_))
                return self._send(200, pd_)
            if path == "/api/palette":
                with HUB.lock:
                    base_ = HUB.base_templates
                    over_ = copy.deepcopy((HUB.ui.get("colors") or {}))
                styles_ = [base_.get("name") or "Graphics"] + [pk.get("name") for pk in library_packages() if pk.get("name") != base_.get("name")]
                want_ = (qs.get("style") or [styles_[0]])[0]
                src_ = base_ if want_ == (base_.get("name") or "Graphics") else next((pk for pk in library_packages() if pk.get("name") == want_), None)
                if src_ is None:
                    return self._send(404, {"error": "no such style"})
                return self._send(200, {"style": want_, "styles": styles_, "colors": palette(src_), "overrides": over_.get(want_) or {}})
            if path == "/api/sponsors/log":
                with HUB.sponsor_log.lock:
                    return self._send(200, HUB.sponsor_log.data)
            if path == "/api/sponsors/log.csv":
                return self._send(200, HUB.sponsor_log.csv(), "text/csv; charset=utf-8",
                                  {"Content-Disposition": "attachment; filename=sponsor-exposure.csv"})
            if path == "/api/fonts":
                return self._send(200, {"fonts": font_list()})
            if path == "/api/media":
                return self._send(200, media_index())
            if path.startswith("/media/"):
                parts = path.split("/")
                if len(parts) == 4 and parts[2] in MEDIA_DIRS:
                    return self._file(MEDIA_DIRS[parts[2]], urllib.parse.unquote(parts[3]))
                return self._send(404, {"error": "not found"})
            if path == "/api/sample":
                return self._send(200, finalize(sample_game(), HUB.cfg, {}))
            return self._static(path)
        except BrokenPipeError:
            pass
        except Exception as e:
            try:
                self._send(500, {"error": str(e)})
            except Exception:
                pass

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        body = self._body()
        try:
            if path == "/api/ui":
                HUB.update_ui(body)
                return self._send(200, {"ok": True})
            if path == "/api/sport":
                try:
                    HUB.sport_action(body)
                except ValueError as e:
                    return self._send(400, {"error": str(e)})
                return self._send(200, {"ok": True})
            if path == "/api/trackman":
                try:
                    res = trackman_import(str(body.get("csv") or ""), bool(body.get("replace")))
                except ValueError as e:
                    return self._send(400, {"error": str(e)})
                HUB.refinalize()
                return self._send(200, dict(res, ok=True))
            if path == "/api/cmd":
                try:
                    res = HUB.command(body.get("do"), body.get("g") if body.get("g") is not None else body.get("i"))
                except ValueError as e:
                    return self._send(400, {"error": str(e)})
                return self._send(200, {"ok": True, "result": res})
            if path == "/api/toggle":
                on = HUB.toggle(body.get("g"), body.get("on"))
                return self._send(200, {"ok": True, "on": on})
            if path == "/api/alloff":
                HUB.all_off(body.get("keep"))
                return self._send(200, {"ok": True})
            if path == "/api/templates":
                HUB.set_templates(body)
                return self._send(200, {"ok": True})
            if path == "/api/templates/reset":
                HUB.reset_templates()
                return self._send(200, {"ok": True})
            if path == "/api/config":
                body.pop("port", None)
                HUB.update_config(body)
                return self._send(200, {"ok": True})
            if path == "/api/sponsors/upload":
                # Logo upload from the control panel: {"filename": "acme.png", "data": "<base64>"}
                import base64
                fn = os.path.basename(str(body.get("filename") or ""))
                stem, ext = os.path.splitext(fn)
                if ext.lower() not in (".png", ".webp", ".jpg", ".jpeg", ".gif", ".svg") or not stem:
                    return self._send(400, {"error": "Use a PNG, SVG, WebP, JPG or GIF logo"})
                raw = base64.b64decode(str(body.get("data") or "").split(",")[-1])
                if len(raw) > 15 * 1024 * 1024:
                    return self._send(400, {"error": "Logo file is larger than 15 MB"})
                d = MEDIA_DIRS["sponsors"]
                os.makedirs(d, exist_ok=True)
                safe = slug(stem) + ext.lower()
                with open(os.path.join(d, safe), "wb") as f:
                    f.write(raw)
                _media_cache["t"] = 0
                return self._send(200, {"ok": True, "url": "/media/sponsors/" + safe})
            if path == "/api/media/upload":
                # Logo / background / video upload: {"kind": "logos", "filename": "ducks.png", "name": "LI", "data": "<base64>"}
                # Saved as media/<kind>/<name>.<ext>; a team logo named after its abbreviation is picked up automatically.
                import base64
                kind = str(body.get("kind") or "logos")
                if kind not in ("logos", "backgrounds", "videos", "photos"):
                    return self._send(400, {"error": "Unknown media kind"})
                fn = os.path.basename(str(body.get("filename") or ""))
                stem, ext = os.path.splitext(fn)
                raw = base64.b64decode(str(body.get("data") or "").split(",")[-1])
                ext = (sniff_image_ext(raw) or ext.lower()) if kind != "videos" else ext.lower()
                allowed = (".webm", ".mp4", ".mov") if kind == "videos" else (".png", ".webp", ".jpg", ".jpeg", ".gif", ".svg")
                if ext not in allowed:
                    return self._send(400, {"error": "Use %s" % ", ".join(a.strip(".").upper() for a in allowed)})
                if len(raw) > (400 if kind == "videos" else 15) * 1024 * 1024:
                    return self._send(400, {"error": "File is too large"})
                key = slug(body.get("name") or stem) or "file"
                d = MEDIA_DIRS[kind]
                os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, key + ext), "wb") as fh:
                    fh.write(raw)
                _media_cache["t"] = 0
                HUB.refinalize()
                return self._send(200, {"ok": True, "url": "/media/%s/%s" % (kind, urllib.parse.quote(key + ext))})
            if path == "/api/fonts/upload":
                # Font upload from the editor: {"filename": "Gotham Bold.otf", "data": "<base64>"}
                import base64
                fn = os.path.basename(str(body.get("filename") or "")).replace("/", "").replace("\\", "")
                stem, ext = os.path.splitext(fn)
                if ext.lower() not in FONT_EXT or not stem.strip():
                    return self._send(400, {"error": "Use a TTF, OTF, WOFF or WOFF2 font file"})
                raw = base64.b64decode(str(body.get("data") or "").split(",")[-1])
                if len(raw) > 30 * 1024 * 1024:
                    return self._send(400, {"error": "Font file is larger than 30 MB"})
                stem = re.sub(r"[^A-Za-z0-9 _.-]", "", stem).strip() or "font"
                os.makedirs(MEDIA_DIRS["fonts"], exist_ok=True)
                with open(os.path.join(MEDIA_DIRS["fonts"], stem + ext.lower()), "wb") as f:
                    f.write(raw)
                fonts = font_list()
                HUB.publish("fonts", fonts)
                return self._send(200, {"ok": True, "family": stem, "fonts": fonts})
            if path == "/api/photos/upload":
                # Headshot upload: {"name": "Alex Rivera", "filename": "x.png", "data": "<base64>"}
                # With no name, the file name is used, so bulk uploads named "alex-rivera.png" match players.
                import base64
                fn = os.path.basename(str(body.get("filename") or ""))
                stem, ext = os.path.splitext(fn)
                raw = base64.b64decode(str(body.get("data") or "").split(",")[-1])
                ext = sniff_image_ext(raw) or ext.lower()
                if ext not in (".png", ".webp", ".jpg", ".jpeg", ".gif", ".svg"):
                    return self._send(400, {"error": "Use a PNG, JPG, WebP, GIF or SVG image"})
                if len(raw) > 15 * 1024 * 1024:
                    return self._send(400, {"error": "Image is larger than 15 MB"})
                key = slug(body.get("name") or stem)
                if not key:
                    return self._send(400, {"error": "No player name"})
                saved = save_photo(key, ext, raw)
                HUB.refinalize()
                return self._send(200, {"ok": True, "url": saved, "key": key})
            if path == "/api/photos/assign":
                key = slug(body.get("name"))
                url = str(body.get("url") or "").strip()
                if not key:
                    return self._send(400, {"error": "No player name"})
                with HUB.lock:
                    pa = HUB.cfg.setdefault("photo_assign", {})
                    if url:
                        pa[key] = url
                    else:
                        pa.pop(key, None)
                    save_json(CONFIG_PATH, HUB.cfg)
                HUB.publish("config", HUB.public_config())
                HUB.refinalize()
                return self._send(200, {"ok": True})
            if path == "/api/photos/remove":
                n = remove_photo(slug(body.get("name")), body.get("team"), body.get("number"))
                HUB.refinalize()
                return self._send(200, {"ok": True, "removed": n})
            if path == "/api/sponsors/log/reset":
                HUB.sponsor_log.reset()
                return self._send(200, {"ok": True})
            if path == "/api/refresh":
                POLLER.kick()
                return self._send(200, {"ok": True})
            return self._send(404, {"error": "unknown route"})
        except Exception as e:
            return self._send(400, {"error": str(e)})

    def _static(self, path):
        return self._file(WEB_DIR, urllib.parse.unquote(path).lstrip("/"))

    def _file(self, root, relpath):
        rel = os.path.normpath(relpath)
        if rel.startswith("..") or os.path.isabs(rel):
            return self._send(403, {"error": "forbidden"})
        full = os.path.join(root, rel)
        if not os.path.realpath(full).startswith(os.path.realpath(root)):
            return self._send(403, {"error": "forbidden"})
        if not os.path.isfile(full):
            return self._send(404, {"error": "not found", "path": path})
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        with open(full, "rb") as f:
            self._send(200, f.read(), ctype)

    def _websocket(self, view="all", layer=None, ids=None):
        """Minimal server-to-client WebSocket (RFC 6455). OBS runs every browser source in one
        Chromium profile, which allows only 6 HTTP connections per host; a held-open SSE stream
        per overlay used them all up. WebSockets are not counted against that limit."""
        import base64
        import hashlib
        import struct
        key = self.headers.get("Sec-WebSocket-Key")
        if not key or "websocket" not in (self.headers.get("Upgrade") or "").lower():
            return self._send(400, {"error": "websocket upgrade required"})
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        self.close_connection = True
        sock = self.connection
        wlock = threading.Lock()

        def frame(opcode, payload):
            n = len(payload)
            if n < 126:
                head = struct.pack("!BB", 0x80 | opcode, n)
            elif n < 65536:
                head = struct.pack("!BBH", 0x80 | opcode, 126, n)
            else:
                head = struct.pack("!BBQ", 0x80 | opcode, 127, n)
            with wlock:
                sock.sendall(head + payload)

        alive = [True]

        def reader():
            # Drain client frames (pongs, close). Any read failure ends the session.
            try:
                while alive[0]:
                    h = self.rfile.read(2)
                    if len(h) < 2:
                        break
                    op, ln = h[0] & 0x0F, h[1] & 0x7F
                    if ln == 126:
                        ln = struct.unpack("!H", self.rfile.read(2))[0]
                    elif ln == 127:
                        ln = struct.unpack("!Q", self.rfile.read(8))[0]
                    mask = self.rfile.read(4) if h[1] & 0x80 else b""
                    data = self.rfile.read(ln)
                    if op == 0x8:
                        break
                    if op == 0x9 and mask:
                        data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
                        frame(0xA, data)
            except Exception:
                pass
            alive[0] = False

        q = HUB.subscribe(view, layer, ids)
        threading.Thread(target=reader, daemon=True).start()
        try:
            frame(0x1, json.dumps({"type": "full", "data": HUB.snapshot(q.view, q.layer, q.ids)}, default=str).encode("utf-8"))
            while alive[0] and not HUB.closing:
                try:
                    msg = q.get(timeout=10)
                    frame(0x1, msg.encode("utf-8"))
                except queue.Empty:
                    frame(0x9, b"")
        except Exception:
            pass
        finally:
            alive[0] = False
            HUB.unsubscribe(q)
            try:
                frame(0x8, b"")
            except Exception:
                pass

    def _sse(self, view="all", layer=None, ids=None):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        q = HUB.subscribe(view, layer, ids)
        try:
            self.wfile.write(("data: %s\n\n" % json.dumps({"type": "full", "data": HUB.snapshot(q.view, q.layer, q.ids)}, default=str)).encode("utf-8"))
            self.wfile.flush()
            while not HUB.closing:
                try:
                    msg = q.get(timeout=10)
                    self.wfile.write(("data: %s\n\n" % msg).encode("utf-8"))
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                self.wfile.flush()
        except Exception:
            pass
        finally:
            HUB.unsubscribe(q)


class Server:
    def __init__(self):
        self.httpd = None
        self.thread = None

    def start(self, port, lan=False):
        self.stop()
        host = "0.0.0.0" if lan else "127.0.0.1"
        ThreadingHTTPServer.daemon_threads = True
        ThreadingHTTPServer.allow_reuse_address = True
        self.httpd = ThreadingHTTPServer((host, port), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, name="bbg-http", daemon=True)
        self.thread.start()
        log("Serving on http://%s:%d  (control: /control.html, editor: /editor.html)" % ("127.0.0.1" if not lan else host, port))

    def stop(self):
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception:
                pass
            self.httpd = None


SERVER = Server()


def start_all(port=None, lan=None):
    global HUB
    if HUB is None:
        HUB = Hub()
    else:
        HUB.closing = False
    if port is not None:
        HUB.cfg["port"] = port
    if lan is not None:
        HUB.cfg["lan"] = lan
    SERVER.start(int(HUB.cfg["port"]), bool(HUB.cfg.get("lan")))
    POLLER.start()
    SPONSOR_TICKER.start()


def stop_all():
    if HUB:
        HUB.closing = True
        HUB.publish("bye", {})
    POLLER.stop()
    SPONSOR_TICKER.stop()
    SERVER.stop()


def base_url():
    return "http://127.0.0.1:%d" % int(HUB.cfg["port"]) if HUB else "http://127.0.0.1:8765"


# ---------------------------------------------------------------------------
# OBS integration
# ---------------------------------------------------------------------------
HOTKEYS = {}
SCENE_NAME = "Baseball Graphics"
SOURCE_PREFIX = "BBG - "
LAYER_PREFIX = "BBG Layer - "
# One browser source per layer (bottom to top). Each shows every graphic whose group belongs to it,
# so new graphics never need new sources and OBS runs a handful of browsers instead of dozens.
LAYERS = [("full", "Full Screen", ("full",)), ("panel", "Side Panels", ("panel",)), ("lower", "Lower Thirds", ("lower", "note")),
          ("ticker", "Ticker", ("ticker",)), ("bug", "Scorebugs", ("bug", "bug2")), ("event", "Event Stingers", ("event", "event2")), ("stinger", "Transitions", ("stinger",))]


LAYER_KEYS = tuple(k for k, _, _ in LAYERS)


def layer_of(group):
    for key, _, groups in LAYERS:
        if (group or "") in groups:
            return key
    return "lower"


def script_description():
    return ("<b>Baseball Broadcast Graphics</b> v%s<br>"
            "HTML5 scorebug, lower thirds, lineups, defense, pitching, linescore and custom graphics "
            "driven by manual scoring.<br><br>"
            "1. Click <b>Create / Update Graphics Scene</b>.<br>"
            "2. Add the control panel as a dock: Docks menu &gt; Custom Browser Docks, URL "
            "<code>http://127.0.0.1:%d/control.html</code>.<br>"
            "3. Design graphics with <b>Open Graphics Editor</b>." % (VERSION, int(HUB.cfg["port"]) if HUB else 8765))


def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "port", 8765)
    obs.obs_data_set_default_bool(settings, "lan", False)


def script_properties():
    p = obs.obs_properties_create()
    obs.obs_properties_add_int(p, "port", "Local server port", 1024, 65535, 1)
    obs.obs_properties_add_bool(p, "lan", "Allow the control panel from other devices on this network")
    obs.obs_properties_add_button(p, "btn_scene", "Create / Update Graphics Scene", _cb_create_scene)
    obs.obs_properties_add_button(p, "btn_control", "Open Control Panel", lambda *_: webbrowser.open(base_url() + "/control.html") and False)
    obs.obs_properties_add_button(p, "btn_editor", "Open Graphics Editor", lambda *_: webbrowser.open(base_url() + "/editor.html") and False)
    obs.obs_properties_add_button(p, "btn_alloff", "Take All Graphics Out", lambda *_: HUB.all_off() and False)
    return p


_LOADED_SETTINGS = None


def script_load(settings):
    global _LOADED_SETTINGS
    _LOADED_SETTINGS = settings
    port = obs.obs_data_get_int(settings, "port") or 8765
    lan = obs.obs_data_get_bool(settings, "lan")
    try:
        start_all(port, lan)
    except OSError as e:
        log("Could not start server on port %d: %s" % (port, e))
    _register_hotkeys(settings)
    request_scene_sync()
    obs.timer_add(_sync_tick, 1000)


def script_update(settings):
    if HUB is None:
        return
    port = obs.obs_data_get_int(settings, "port") or 8765
    lan = obs.obs_data_get_bool(settings, "lan")
    if port != int(HUB.cfg["port"]) or lan != bool(HUB.cfg.get("lan")):
        HUB.cfg["port"], HUB.cfg["lan"] = port, lan
        save_json(CONFIG_PATH, HUB.cfg)
        try:
            SERVER.start(port, lan)
        except OSError as e:
            log("Could not restart server on port %d: %s" % (port, e))


def script_save(settings):
    for key, hid in HOTKEYS.items():
        arr = obs.obs_hotkey_save(hid)
        obs.obs_data_set_array(settings, key, arr)
        obs.obs_data_array_release(arr)


def script_unload():
    try:
        obs.timer_remove(_sync_tick)
    except Exception:
        pass
    stop_all()


def _register_hotkeys(settings):
    graphics = (HUB.templates.get("graphics") or {}) if HUB else {}
    entries = [("bbg_alloff", "Baseball Graphics: All Out", lambda: HUB.all_off()),
               ("bbg_rundown_next", "Baseball Graphics: Rundown next", lambda: HUB.command("next")),
               ("bbg_rundown_prev", "Baseball Graphics: Rundown previous", lambda: HUB.command("prev")),
               ("bbg_rundown_clear", "Baseball Graphics: Rundown clear current", lambda: HUB.command("clear")),
               ("bbg_pclock_start", "Baseball Graphics: Pitch clock start", lambda: HUB.command("clock_start")),
               ("bbg_pclock_reset", "Baseball Graphics: Pitch clock reset", lambda: HUB.command("clock_reset")),
               ("bbg_k_up", "Baseball Graphics: Strikeout counter +1", lambda: HUB.command("k_up")),
               ("bbg_shout_next", "Baseball Graphics: Next shout-out", lambda: HUB.command("shout_next")),
               ("bbg_clock", "Baseball Graphics: Game clock start / stop (basketball, football, hockey)",
                lambda: HUB.current_sport() != "baseball" and HUB.sport_action({"op": "toggle"})),
               ("bbg_shot", "Baseball Graphics: Shot / play clock reset",
                lambda: HUB.current_sport() != "baseball" and HUB.sport_action({"op": "shot_reset"}))]
    for gid, d in graphics.items():
        if d.get("layout"):
            continue
        entries.append(("bbg_toggle_" + gid, "Baseball Graphics: Toggle " + d.get("name", gid),
                        (lambda g: (lambda: HUB.toggle(g)))(gid)))
    for key, label, fn in entries:
        def cb(pressed, fn=fn):
            if pressed:
                fn()
        hid = obs.obs_hotkey_register_frontend(key, label, cb)
        HOTKEYS[key] = hid
        arr = obs.obs_data_get_array(settings, key)
        obs.obs_hotkey_load(hid, arr)
        obs.obs_data_array_release(arr)


def _cb_create_scene(props, prop):
    try:
        create_scene(convert=True)
    except Exception as e:
        log("Scene creation failed: %s" % e)
    return False


def _browser_settings(url):
    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "url", url)
    obs.obs_data_set_int(settings, "width", 1920)
    obs.obs_data_set_int(settings, "height", 1080)
    # Follow OBS's own frame rate: seven full-HD layers forced to 60 fps on a 30 fps canvas doubled the render work
    # for nothing and made OBS and its docks sluggish.
    obs.obs_data_set_bool(settings, "fps_custom", False)
    obs.obs_data_set_bool(settings, "shutdown", False)
    obs.obs_data_set_bool(settings, "restart_when_active", False)
    obs.obs_data_set_string(settings, "css", "body { background-color: rgba(0,0,0,0); margin: 0; overflow: hidden; }")
    return settings


def _scene_item_names(scene):
    names = []
    items = obs.obs_scene_enum_items(scene) or []
    for it in items:
        names.append((obs.obs_source_get_name(obs.obs_sceneitem_get_source(it)), it))
    return names, items


def _add_browser(scene, name, url, sx, sy):
    settings = _browser_settings(url)
    existing = obs.obs_get_source_by_name(name)
    if existing:
        obs.obs_source_update(existing, settings)
        source = existing
    else:
        source = obs.obs_source_create("browser_source", name, settings, None)
    added = 0
    if not obs.obs_scene_find_source(scene, name):
        added = 1
        item = obs.obs_scene_add(scene, source)
        if item and (sx != 1 or sy != 1):
            v = obs.vec2()
            v.x, v.y = sx, sy
            obs.obs_sceneitem_set_scale(item, v)
    obs.obs_source_release(source)
    obs.obs_data_release(settings)
    return added


def create_scene(only_missing=False, create_if_absent=True, convert=False):
    """Builds the graphics scene.
    Layer mode (default): one browser source per layer. convert=True (the Create / Update button) also
    removes older one-source-per-graphic items. The automatic sync (only_missing=True) never removes
    anything: a scene still on per-graphic sources keeps getting per-graphic sources until the button is clicked."""
    graphics = HUB.templates.get("graphics") or {}
    ovi = obs.obs_video_info()
    obs.obs_get_video_info(ovi)
    sx, sy = ovi.base_width / 1920.0, ovi.base_height / 1080.0
    mode = HUB.cfg.get("source_mode", "layers")

    src = obs.obs_get_source_by_name(SCENE_NAME)
    created = False
    if src:
        scene = obs.obs_scene_from_source(src)
    elif not create_if_absent:
        return 0
    else:
        scene = obs.obs_scene_create(SCENE_NAME)
        created = True
    added = 0
    try:
        names, items = _scene_item_names(scene)
        legacy = [(n, it) for n, it in names if n.startswith(SOURCE_PREFIX)]
        per_graphic = mode != "layers"
        if mode == "layers" and legacy and not convert:
            # Older scene with one source per graphic: leave it as is (never add dozens of sources
            # automatically); the Create / Update button converts it to layer sources.
            log("New graphics are ready. Click Create / Update Graphics Scene (Tools > Scripts) to switch to "
                "one source per layer, which also adds them.")
        elif per_graphic:
            for gid, d in graphics.items():
                name = SOURCE_PREFIX + d.get("name", gid)
                if only_missing and obs.obs_scene_find_source(scene, name):
                    continue
                added += _add_browser(scene, name, base_url() + "/overlay.html?g=" + urllib.parse.quote(gid), sx, sy)
        else:
            removed = 0
            if convert:
                for n, it in legacy:
                    obs.obs_sceneitem_remove(it)
                    removed += 1
            for key, label, _ in LAYERS:
                added += _add_browser(scene, LAYER_PREFIX + label, base_url() + "/overlay.html?layer=" + key, sx, sy)
            if removed:
                log("Replaced %d per-graphic sources with %d layer sources." % (removed, len(LAYERS)))
        if items:
            obs.sceneitem_list_release(items)
        if not only_missing:
            log("Graphics scene ready: '%s'. Add it as a nested source in your program scenes." % SCENE_NAME)
        elif added:
            log("Added %d source(s) to '%s'." % (added, SCENE_NAME))
    finally:
        if created:
            obs.obs_scene_release(scene)
        else:
            obs.obs_source_release(src)
    return added


# Automatic scene sync: whenever the graphics package changes (and once after OBS starts), add
# browser sources for graphics that do not have one yet. Runs on OBS's main thread via a timer.
_SYNC = {"pending": True, "tries": 0}


def request_scene_sync():
    _SYNC["pending"], _SYNC["tries"] = True, 0


def _sync_tick():
    if not _SYNC["pending"] or HUB is None:
        return
    _SYNC["tries"] += 1
    try:
        src = obs.obs_get_source_by_name(SCENE_NAME)
        if not src:
            # Scene collection may still be loading right after OBS starts; keep trying for ~30 s.
            if _SYNC["tries"] > 30:
                _SYNC["pending"] = False
            return
        obs.obs_source_release(src)
        _SYNC["pending"] = False
        create_scene(only_missing=True, create_if_absent=False)
    except Exception as e:
        _SYNC["pending"] = False
        log("Scene sync failed: %s" % e)


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__" and not IN_OBS:
    args = sys.argv[1:]
    port = None
    if "--port" in args:
        port = int(args[args.index("--port") + 1])
    start_all(port, "--lan" in args)
    log("Standalone mode. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()
