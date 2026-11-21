"""Manual edition tests: python tests/run_manual_tests.py
Checks that the manual edition never reaches the internet, that manual scoring drives the
graphics, and that the control panel hides every data-feed control."""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

PORT = 8798
BASE = "http://127.0.0.1:%d" % PORT
FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -> %r" % (detail,)))
    if not cond:
        FAILS.append(name)


def get(path):
    return json.load(urllib.request.urlopen(BASE + path, timeout=10))


def post(path, body, ok=True):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=10))
    except urllib.error.HTTPError as e:
        return {"_status": e.code, **json.loads(e.read().decode() or "{}")}


def wait_game(pred, secs=8):
    t, g = time.time(), None
    while time.time() - t < secs:
        g = get("/api/state")["game"]
        if pred(g):
            return g
        time.sleep(0.3)
    return g


def main():
    import obs_baseball_graphics as bbg
    check("edition flag is manual", bbg.EDITION == "manual" and bbg.MANUAL_ONLY, bbg.EDITION)
    # The manual zip keeps the fetch helpers but blocks them; the public build has none at all.
    for name, url in (("http_get_json", "https://example.com/"), ("http_get_bytes", "https://example.com/x.png")):
        fn, blocked = getattr(bbg, name, None), True
        if fn:
            try:
                fn(url)
                blocked = False
            except bbg.FetchError:
                pass
        check("%s is blocked or absent" % name, blocked)

    shutil.rmtree(os.path.join(ROOT, "user"), ignore_errors=True)
    srv = subprocess.Popen([sys.executable, os.path.join(ROOT, "obs_baseball_graphics.py"), "--port", str(PORT)], cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for _ in range(300):        # wait until the server answers (startup reads every package)
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/api/state?view=control" % PORT, timeout=2).read()
            break
        except Exception:
            time.sleep(0.2)
    try:
        st = get("/api/state")
        check("state reports manual edition and source", st.get("edition") == "manual" and st["config"]["source"] == "manual",
              (st.get("edition"), st["config"]["source"]))
        post("/api/config", {"source": "feed"})
        check("source cannot be switched to a data feed", get("/api/state")["config"]["source"] == "manual")
        r = post("/api/replay/load", {"source": "feed", "game_id": "abc"})
        check("replay of real games refused", r.get("_status") in (400, 404), r)
        r = post("/api/photos/pull", {"side": "home"})
        check("headshot pull refused", r.get("_status") in (400, 404), r)

        post("/api/ui", {"manual": {"away": {"name": "Visitors", "abbr": "VIS", "runs": 2}, "home": {"name": "Gulls", "abbr": "SI", "runs": 3},
                                    "inning": 6, "half": "bottom", "balls": 2, "strikes": 1, "outs": 1,
                                    "batter": {"name": "Al Jones", "number": "24", "avg": ".301"},
                                    "lineup_text": {"home": "1 Al Jones CF .301\n2 Bo Smith SS .270"},
                                    "standings_text": "North Division\nHarbor City Gulls 52 37\nRiverside Otters 48 41"}})
        g = wait_game(lambda g: g["home"]["runs"] == 3 and g["inningLabel"] == "BOT 6")
        check("manual score and inning", g["away"]["runs"] == 2 and g["home"]["runs"] == 3 and g["inningLabel"] == "BOT 6", g.get("inningLabel"))
        check("manual count", g["count"] == "2-1" and g["outs"] == 1, (g.get("count"), g.get("outs")))
        check("manual lineup", g["home"]["lineup"] and g["home"]["lineup"][0]["name"] == "Al Jones", g["home"].get("lineup"))
        grp = (g.get("standings") or {}).get("groups") or []
        check("manual standings", grp and grp[0]["name"] == "North Division" and grp[0]["teams"][1]["gb"] == "4", grp)
        post("/api/toggle", {"g": "scorebug", "on": True})
        check("take a graphic", get("/api/state")["ui"]["visible"].get("scorebug"))
        post("/api/toggle", {"g": "scorebug", "on": False})

        post("/api/ui", {"sport": "hockey"})
        post("/api/sport", {"op": "score", "side": "home", "n": 1})
        g = wait_game(lambda g: g.get("sport") == "hockey" and g["home"].get("score") == 1)
        check("hockey scoring works in the manual edition", g.get("sport") == "hockey" and g["home"].get("score") == 1, g.get("sport"))
        post("/api/ui", {"sport": "baseball"})
        wait_game(lambda g: not g.get("sport"))
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("SKIP browser checks (playwright not installed)")
            sync_playwright = None
        if sync_playwright:
            with sync_playwright() as p:
                b = p.chromium.launch()
                pg = b.new_page(viewport={"width": 1280, "height": 900})
                errs, reqs = [], []
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.on("request", lambda r: reqs.append(r.url))
                pg.goto(BASE + "/control.html"); pg.wait_for_timeout(1500)
                hidden = pg.evaluate("""() => ['srcCard', 'phPull', 'tkScores'].map(id => {
                    const e = document.getElementById(id); return !e || e.offsetParent === null; })""")
                check("control panel hides data-feed controls", all(hidden), hidden)
                check("manual scoring card is open", pg.evaluate("() => document.getElementById('manCard').open"))
                post("/api/toggle", {"g": "scorebug", "on": True})
                pg.goto(BASE + "/overlay.html?layer=bug"); pg.wait_for_timeout(1500)
                txt = pg.evaluate("() => document.getElementById('stage').innerText")
                check("overlay shows the manual score", "VIS" in txt and "SI" in txt, txt[:120])
                post("/api/toggle", {"g": "scorebug", "on": False})
                # LIVE tab pad: four balls walk the batter, a single moves him to second
                post("/api/ui", {"manual": {"balls": 0, "strikes": 0, "outs": 0, "bases": {"1": False, "2": False, "3": False}, "pitcher": {"pc": "0"}}})
                pg.goto(BASE + "/control.html?panel=live"); pg.wait_for_timeout(1500)
                for act in ("ball", "ball", "ball", "ball", "h1"):          # tapped quickly, as an operator would
                    pg.click("#lvPad [data-act=%s]" % act); pg.wait_for_timeout(40)
                pg.wait_for_timeout(1200)
                m = get("/api/state")["ui"]["manual"]
                check("LIVE pad: walk then single", m["bases"] == {"1": True, "2": True, "3": False} and m["pitcher"]["pc"] == "5" and m["balls"] == 0,
                      (m["bases"], m["pitcher"].get("pc"), m["balls"]))
                pg.click("#lvPad [data-act=undo]"); pg.wait_for_timeout(1000)
                m = get("/api/state")["ui"]["manual"]
                check("LIVE pad: undo", m["bases"] == {"1": True, "2": False, "3": False}, m["bases"])
                outside = [u for u in reqs if not u.startswith(BASE) and not u.startswith("data:")]
                check("pages request nothing outside this computer", not outside, outside[:5])
                check("no page errors", not errs, errs)
                b.close()
    finally:
        srv.terminate()
        out = srv.stdout.read().decode()
        if FAILS:
            print(out[-1500:])
        shutil.rmtree(os.path.join(ROOT, "user"), ignore_errors=True)
    print("\n%d failure(s)" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
