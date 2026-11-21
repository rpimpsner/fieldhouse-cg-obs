"""Rebuild pass: redraws the shared graphics with a style's own chassis.

The skin pass (skin.py) only recolours. This pass runs first and swaps the structure: it finds each shared graphic's
frame (card or body panel), its header band and title, its sub strip, its lower-third bars, logo tiles, value boxes,
tables and transitions, then hands them to the style's kit, which draws them the way that style's own graphics are
drawn (Empire Blue's pattern bands and silver logo tile, Metro Chrome's chrome rail and chevrons, Y2K Blue's silver
header and halftone dots, Throwback 80s' pinstripe band, Playground's confetti bubble, and so on).

A kit is a dict of callables and style dicts (see KIT_KEYS). Elements a kit adds carry "_kit": True so the skin pass
leaves them alone; the flag is stripped at the end (strip_flags).

Bindings, visibility rules and data paths of the original elements are kept: titles, values and tables are moved and
restyled, never replaced, so every graphic keeps working with the same control panel fields.
"""
import copy

import skin as SK

KIT_KEYS = ("frame", "bar", "tile", "title", "sub", "table", "transition", "event", "bug", "lower_decor", "boxless")
FULL_GROUPS = ("full", "panel", "event", "event2")
LOWER_GROUPS = ("lower", "note")
BUG_GROUPS = ("bug", "bug2", "ticker")


def _r(e):
    return int(e.get("x") or 0), int(e.get("y") or 0), int(e.get("w") or 0), int(e.get("h") or 0)


def _area(e):
    return max(0, int(e.get("w") or 0)) * max(0, int(e.get("h") or 0))


def _fill(e):
    st = e.get("style") or {}
    for k in ("background", "fill"):
        if st.get(k):
            return SK._norm_fill(st[k])
    return None


def _role(e):
    if e.get("type") != "box":
        return None
    v = _fill(e)
    if not isinstance(v, str):
        return None
    if v.startswith("@@TEAM:"):
        return "TEAM"
    for r in SK.BOX_ROLES:
        if v.startswith("@@%s@@" % r):
            return r
    return None


def _screen(e):
    x, y, w, h = _r(e)
    return w >= 1900 and h >= 1000


def _offscreen(e):
    x, y, w, h = _r(e)
    return x + w <= 0 or y + h <= 0 or x >= 1920 or y >= 1080


def _union(E):
    E = [e for e in E if not _screen(e) and not _offscreen(e) and _area(e) > 0]
    if not E:
        return None
    x0 = min(_r(e)[0] for e in E)
    y0 = min(_r(e)[1] for e in E)
    x1 = max(_r(e)[0] + _r(e)[2] for e in E)
    y1 = max(_r(e)[1] + _r(e)[3] for e in E)
    return x0, y0, x1 - x0, y1 - y0


def _inside(e, R, pad=6):
    x, y, w, h = _r(e)
    X, Y, W, H = R
    return x >= X - pad and y >= Y - pad and x + w <= X + W + pad and y + h <= Y + H + pad


def _overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0, min(ay + ah, by + bh) - max(ay, by))


def _size(e):
    try:
        return float((e.get("style") or {}).get("size") or 32)
    except (TypeError, ValueError):
        return 32.0


def _name(e):
    return (e.get("name") or "").lower()


def _kit_flag(E):
    for e in E:
        e["_kit"] = True
    return E


def strip_flags(graphics):
    for g in graphics.values():
        for e in g.get("elements", []):
            e.pop("_kit", None)
    return graphics


# ------------------------------------------------------------------ detection
def find_frame(E):
    """The card or body panel that holds the graphic, plus header bands stacked directly on top of it."""
    U = _union(E)
    if not U:
        return None
    cands = [e for e in E if e.get("type") == "box" and not _screen(e) and not _offscreen(e)
             and (_role(e) in ("PANEL", "PANEL2", "DARK", "TITLE") or _name(e) in ("card", "body", "frame", "panel", "bg", "background"))]
    cands.sort(key=_area, reverse=True)
    if not cands:
        return None
    c = cands[0]
    if _area(c) < 0.42 * U[2] * U[3]:
        return None
    X, Y, W, H = _r(c)
    # header bands sitting on top of a body panel (list frames: title bar over body)
    above = [e for e in E if e is not c and e.get("type") == "box" and _role(e) and abs(_r(e)[1] + _r(e)[3] - Y) <= 2
             and _r(e)[2] >= 0.3 * W and _r(e)[1] >= Y - 200 and _r(e)[0] >= X - 4 and _r(e)[0] + _r(e)[2] <= X + W + 4]
    top = Y
    for e in above:
        top = min(top, _r(e)[1])
    # a stack of bands (title bar over a sub strip over the body)
    changed = True
    while changed:
        changed = False
        for e in E:
            if e is c or e.get("type") != "box" or not _role(e):
                continue
            ex, ey, ew, eh = _r(e)
            if abs(ey + eh - top) <= 2 and ew >= 0.3 * W and ey >= top - 200 and ex >= X - 4 and ex + ew <= X + W + 4 and ey < top:
                top = ey
                changed = True
    return {"el": c, "rect": (X, top, W, Y + H - top), "body": (X, Y, W, H)}


def find_title(E, R):
    X, Y, W, H = R
    zone = (X, Y - 10, W, min(230, H // 2 + 10))
    named = [e for e in E if e.get("type") == "text" and _name(e) in ("title", "band title", "head title", "final", "header title")
             and _overlap(_r(e), zone) > 0]
    if named:
        return sorted(named, key=lambda e: (_r(e)[1], -_size(e)))[0]
    big = [e for e in E if e.get("type") == "text" and _size(e) >= 40 and _overlap(_r(e), zone) > 0.6 * _area(e)]
    if big:
        return sorted(big, key=lambda e: -_size(e))[0]
    return None


def header_bands(E, R, title, frame_el):
    X, Y, W, H = R
    tx, ty, tw, th = _r(title)
    cy = ty + th / 2.0
    out = []
    for e in E:
        if e is frame_el or e.get("type") != "box" or _screen(e):
            continue
        ex, ey, ew, eh = _r(e)
        if ey <= cy <= ey + eh and ew >= 0.35 * W and ey < Y + 240 and eh <= 200 and _role(e):
            out.append(e)
    return out


def find_sub(E, R, hb_bottom, title):
    X, Y, W, H = R
    best = None
    for e in E:
        if e is title or e.get("type") != "text":
            continue
        n = _name(e)
        ex, ey, ew, eh = _r(e)
        if (n.startswith("sub") or n in ("season", "kicker")) and Y - 10 <= ey <= hb_bottom + 60 and ew >= 0.25 * W:
            if best is None or ey < _r(best)[1]:
                best = e
    return best


def sub_band(E, R, sub, skip):
    if not sub:
        return None
    sx, sy, sw, sh = _r(sub)
    cy = sy + sh / 2.0
    for e in E:
        if e in skip or e.get("type") != "box":
            continue
        ex, ey, ew, eh = _r(e)
        if ey <= cy <= ey + eh and eh <= 70 and ew >= 0.3 * R[2] and _role(e):
            return e
    return None


def logo_tiles(E):
    """Small boxes that hold a team, league or brand logo."""
    out = []
    imgs = [e for e in E if e.get("type") == "image" and "logo" in str(e.get("src") or "")]
    for b in E:
        if b.get("type") != "box" or not _role(b):
            continue
        bx, by, bw, bh = _r(b)
        if bw > 240 or bh > 240 or bw < 40 or bh < 40 or (b.get("style") or {}).get("rotate"):
            continue
        for i in imgs:
            if _inside(i, _r(b), 4) and _area(i) >= 0.3 * _area(b):
                out.append(b)
                break
    return out


# ------------------------------------------------------------------ rebuild
def _insert_before(E, anchor, new):
    i = E.index(anchor) if anchor in E else 0
    E[i:i] = new


def _restyle_text(e, spec, rect=None):
    if not spec or e is None:
        return
    st = e.setdefault("style", {})
    for k, v in spec.items():
        if k == "scale":
            st["size"] = int(round(_size(e) * v))
        elif k == "color" and isinstance(v, str) and v == "keep":
            continue
        else:
            st[k] = v
    e["_kit"] = True
    if rect:
        e["x"], e["y"], e["w"], e["h"] = rect


def rebuild_full(g, K):
    E = g["elements"]
    F = find_frame(E)
    if not F:
        return rebuild_header_only(g, K)
    fr = F["el"]
    X, Y, W, H = F["rect"]
    title = None if g.get("layout") else find_title(E, F["rect"])
    if title is not None and _r(title)[1] - Y > 130:
        title = None
    remove = [fr]
    hb = 0
    sub = None
    subb = None
    if title is not None:
        bands = header_bands(E, F["rect"], title, fr)
        tb = _r(title)[1] + _r(title)[3]
        bottom = max([tb] + [_r(b)[1] + _r(b)[3] for b in bands])
        hb = max(56, min(200, bottom - Y))
        sub = find_sub(E, F["rect"], Y + hb, title)
        subb = sub_band(E, F["rect"], sub, [fr] + bands)
        if subb is not None:
            hb = max(hb, _r(subb)[1] - Y)
            remove.append(subb)
        elif sub is not None and _r(sub)[1] < Y + hb:
            pass
        remove += bands
    sub_h = _r(subb)[3] if subb is not None else 0
    res = K["frame"](X, Y, W, H, hb, sub_h, g)
    new = _kit_flag(res["elements"])
    if title is not None and res.get("title"):
        tr = res["title"]
        rect = tr.get("rect")
        spec = dict((k, v) for k, v in tr.items() if k != "rect")
        _restyle_text(title, spec, rect(_r(title)) if callable(rect) else None)
    if sub is not None and res.get("sub"):
        sr = res["sub"]
        rect = sr.get("rect")
        spec = dict((k, v) for k, v in sr.items() if k != "rect")
        if subb is None and _r(sub)[1] + _r(sub)[3] / 2.0 < Y + hb and res.get("headText"):
            spec.update(res["headText"])
        _restyle_text(sub, spec, rect(_r(sub)) if callable(rect) else None)
    # other text in the header and sub strip takes the header / sub colours
    tiles = [b for b in E if b.get("type") == "box" and b.get("_kit") and _r(b)[2] <= 260]
    for e in E:
        if e.get("type") != "text" or e is title or e is sub or e.get("_kit"):
            continue
        ex, ey, ew, eh = _r(e)
        cx, cy = ex + ew / 2.0, ey + eh / 2.0
        if any(_inside(e, _r(t), 4) for t in tiles):
            continue
        if X <= cx <= X + W and Y <= cy < Y + hb and res.get("headText"):
            _restyle_text(e, res["headText"])
        elif sub_h and X <= cx <= X + W and Y + hb <= cy <= Y + hb + sub_h and res.get("subText"):
            _restyle_text(e, res["subText"])
    _insert_before(E, fr, new)
    for e in remove:
        if e in E:
            E.remove(e)
    return True


def rebuild_header_only(g, K):
    """No single frame (two-column layouts): a wide header band across the top still gets the style's header."""
    E = g["elements"]
    U = _union(E)
    if not U:
        return False
    heads = [e for e in E if e.get("type") == "box" and _role(e) and _r(e)[2] >= 0.6 * U[2] and _r(e)[1] <= U[1] + 6 and 40 <= _r(e)[3] <= 200]
    if not heads:
        return False
    hd = heads[0]
    X, Y, W, hb = _r(hd)
    title = find_title(E, (X, Y, W, hb))
    if title is None:
        return False
    res = K["frame"](X, Y, W, hb, hb, 0, g)
    new = [e for e in res["elements"] if _name(e) not in ("band bottom", "band bottom line", "body pattern")]
    tr = res.get("title") or {}
    _restyle_text(title, dict((k, v) for k, v in tr.items() if k != "rect"))
    for e in E:
        if e.get("type") == "text" and e is not title and not e.get("_kit") and res.get("headText"):
            ex, ey, ew, eh = _r(e)
            if X <= ex + ew / 2.0 <= X + W and Y <= ey + eh / 2.0 < Y + hb:
                _restyle_text(e, res["headText"])
    _insert_before(E, hd, _kit_flag(new))
    E.remove(hd)
    return True


def rebuild_screen(g, K):
    """Full-screen titles and bumpers: the style's own backdrop and edge decoration."""
    if not K.get("screen"):
        return False
    E = g["elements"]
    bgs = [e for e in E[:3] if e.get("type") == "box" and _screen(e)]
    if not bgs:
        return False
    bg = bgs[0]
    v = str(_fill(bg) or "")
    team = "{" in v and ("color" in v)
    res = K["screen"](bg, team, g) or {}
    under = res.get("under") or []
    over = res.get("over") or []
    if res.get("replace") and not team:
        st = bg["style"]
        st.pop("fill", None)
        st["background"] = res["replace"]
        bg["_kit"] = True
    if res.get("floor"):
        for e in E:
            if e.get("type") == "box" and _name(e) == "floor":
                e["style"].pop("fill", None)
                e["style"]["background"] = res["floor"]
                e["_kit"] = True
    i = E.index(bg)
    E[i:i] = _kit_flag(under)
    i = E.index(bg) + 1
    E[i:i] = _kit_flag(over)
    return True


def rebuild_lower(g, K):
    E = g["elements"]
    bars = [e for e in E if e.get("type") == "box" and _role(e) in ("PANEL", "PANEL2", "DARK", "TEAM", "STRIP") and _r(e)[2] >= 280
            and _r(e)[3] >= 24 and not _screen(e)]
    if not bars:
        return False
    bars.sort(key=_area, reverse=True)
    main = bars[0]
    U = _union(E)
    extra = []
    for b in bars:
        m = SK.TEAM_RE.match(str(SK._norm_fill(_fill(b)) or ""))
        if m:
            b["_team"] = m.group(1)
        r = K["bar"](b, b is main, _role(b), g)
        b.pop("_team", None)
        if r:
            extra += r
    if K.get("lower_decor"):
        extra += K["lower_decor"](U, _r(main), g)
    _insert_before(E, main, _kit_flag([e for e in extra if e.get("_under")]))
    E.extend(_kit_flag([e for e in extra if not e.get("_under")]))
    for e in E:
        e.pop("_under", None)
    return True


def rebuild_bug(g, K):
    if not K.get("bug"):
        return False
    E = g["elements"]
    boxes = [e for e in E if e.get("type") == "box" and _role(e) and not _screen(e)]
    if not boxes:
        return False
    boxes.sort(key=_area, reverse=True)
    extra = K["bug"](boxes[0], _union(E), g) or []
    E.extend(_kit_flag(extra))
    return True


def restyle_common(g, K):
    E = g["elements"]
    tile = K.get("tile")
    if tile:
        for b in logo_tiles(E):
            r = tile(b, g)
            if r:
                i = E.index(b)
                E[i + 1:i + 1] = _kit_flag(r)
            b["_kit"] = True
    tspec = K.get("table")
    if tspec:
        for e in E:
            if e.get("type") == "table":
                st = e.setdefault("style", {})
                for k, v in tspec.items():
                    if k in ("rowFill", "altFill", "rowLine", "rowLineW") and k not in st and k != "rowLine":
                        continue
                    st[k] = v


def rebuild_transition(gid, g, K):
    """Keep the word, sub line, logo and REC marks (their text, bindings and timing); the kit draws the rest."""
    if not K.get("transition"):
        return False
    E = g.get("elements", [])
    keep = dict((_name(e), e) for e in E if _name(e) in ("word", "sub", "brand", "rec", "rec dot"))
    if "word" not in keep:
        return False
    res = K["transition"](gid, g)
    if not res:
        return False
    new = _kit_flag(list(res["elements"]))
    for k in ("word", "sub", "brand"):
        e = keep.get(k)
        spec = res.get(k)
        if e is None:
            continue
        if spec is False:
            continue
        if spec:
            spec = dict(spec)
            rect = spec.pop("rect", None)
            _restyle_text(e, spec, rect) if e.get("type") == "text" else None
            if rect and e.get("type") != "text":
                e["x"], e["y"], e["w"], e["h"] = rect
        e["_kit"] = True
        new.append(e)
    for k in ("rec dot", "rec"):
        if k in keep:
            keep[k]["_kit"] = True
            new.append(keep[k])
    new += _kit_flag(list(res.get("after") or []))
    g["elements"] = new
    return True


REPORT = {}


def rebuild_graphic(gid, g, K):
    g = copy.deepcopy(g)
    REPORT[gid] = "none"
    grp = g.get("group") or ""
    if gid.startswith("tr_"):
        if rebuild_transition(gid, g, K):
            REPORT[gid] = "transition"
        return g
    if grp == "stinger" or g.get("layout") == "open" or gid in ("open_station", "opener", "lay_open", "lay_video"):
        return g
    if grp == "full" and any(e.get("type") == "box" and _screen(e) for e in g.get("elements", [])[:3]):
        if rebuild_screen(g, K):
            REPORT[gid] = "screen"
            return g
    restyle_common(g, K)
    done = False
    if grp in FULL_GROUPS:
        done = rebuild_full(g, K)
        if not done and grp.startswith("event") and K.get("event"):
            slabs = [e for e in g["elements"] if e.get("type") == "box" and _r(e)[2] >= 1900 and 120 <= _r(e)[3] <= 520]
            if slabs:
                res = K["event"](_r(slabs[0]), slabs[0], g) or []
                under = [e for e in res if not e.get("_over")]
                over = [e for e in res if e.get("_over")]
                for e in over:
                    e.pop("_over", None)
                _insert_before(g["elements"], slabs[0], _kit_flag(under))
                i = g["elements"].index(slabs[0]) + 1
                g["elements"][i:i] = _kit_flag(over)
                done = True
    if not done and grp in LOWER_GROUPS + ("full",):
        U = _union(g["elements"])
        if U and (grp in LOWER_GROUPS or U[3] <= 320):
            done = rebuild_lower(g, K)
    if done:
        REPORT[gid] = "frame/lower/event"
    if not done and grp in BUG_GROUPS + ("panel", "full"):
        if rebuild_bug(g, K):
            REPORT[gid] = "bug"
    return g


def rebuild_all(graphics, K, only=None):
    out = {}
    for gid, g in graphics.items():
        out[gid] = rebuild_graphic(gid, g, K) if (only is None or gid in only) else g
    return out


# ------------------------------------------------------------------ kit factory
def make_kit(P):
    """Build a kit from a style description P (see the builders). Missing keys fall back to sensible defaults.

    P keys: body (bg), bodyOver (pattern bg over the body), bodyBox (radius / border / shadow), head (title bar bg),
    headTile (logo tile bg or None), headRule (thin line under the header when there is no sub strip), headBox,
    sub (sub strip bg), subOver, bands (pattern bg for bands outside the frame), bandLine, title / subText (text specs),
    roles (role -> bg for lower-third and bug bars), mainBox (style for the main bar), teamMain (bg for a team-colour
    main bar, or None to keep the team colour), teamStripe (height of a team-colour stripe under a recoloured bar),
    tile (logo tile style), tileInk (text colour on tiles), frameDecor(X, Y, W, H, hb) and lowerDecor(U, M, g)
    (extra elements), tr (transition description), boxless.
    """
    from broadcast_lib import A, box, _tr_anim as TA
    OUT = {"type": "fade", "dur": 260, "delay": 0, "ease": "in"}

    def frame(X, Y, W, H, hb, sub_h, g):
        E = []
        bands = P.get("bands")
        if bands and Y >= 44:
            E += [box("Band top", X, Y - 40, W, 37, None, A("wipe-right", 420, 0, out=OUT), bg=bands)]
            if P.get("bandLine"):
                E.append(box("Band top line", X, Y - 3, W, 3, P["bandLine"], A("grow-x", 420, 120, out=OUT)))
        if not P.get("boxless"):
            E.append(box("Body", X, Y, W, H, None, A(P.get("bodyIn", "fade"), 400, 100, out=OUT), bg=P["body"], **(P.get("bodyBox") or {})))
            if P.get("bodyOver"):
                E.append(box("Body pattern", X, Y + hb, W, H - hb, None, A("fade", 600, 300, out=OUT), bg=P["bodyOver"],
                             radius=(P.get("bodyBox") or {}).get("radius", 0)))
        if hb:
            tw = 0
            if P.get("headTile"):
                logo = [e for e in g["elements"] if e.get("type") == "image" and "logo" in str(e.get("src")) and "sponsor" not in str(e.get("src")) and _r(e)[1] < Y + hb
                        and _r(e)[0] < X + 260 and _r(e)[1] + _r(e)[3] > Y]
                if logo:
                    lx, ly, lw, lh = _r(logo[0])
                    tw = min(260, lx + lw + 14 - X)
                    tb = P["headTile"]
                    if callable(tb):
                        import re as _re
                        m = _re.search(r"\{([a-zA-Z]+)\.logo", str(logo[0].get("src")))
                        tb = tb(m.group(1) if m and m.group(1) in ("away", "home", "team", "batting", "fielding", "scorer") else None)
                    E.append(box("Tile", X, Y, tw, hb, None, A("fade", 360, 160, out=OUT), bg=tb, **(P.get("headTileBox") or {})))
            if P.get("head"):
                E.append(box("Title bar", X + tw, Y, W - tw, hb, None, A("wipe-right", 420, 160, out=OUT), bg=P["head"], **(P.get("headBox") or {})))
            if sub_h and P.get("sub"):
                E.append(box("Sub strip", X, Y + hb, W, sub_h, None, A("wipe-right", 380, 260, out=OUT), bg=P["sub"]))
                if P.get("subOver"):
                    E.append(box("Sub pattern", X + W - min(320, W // 2), Y + hb, min(320, W // 2), sub_h, None, A("fade", 300, 360, out=OUT),
                                 bg=P["subOver"]))
            elif P.get("headRule"):
                E.append(box("Header line", X, Y + hb - P.get("headRuleH", 3), W, P.get("headRuleH", 3), P["headRule"], A("grow-x", 380, 300, out=OUT)))
        if P.get("frameDecor"):
            E += P["frameDecor"](X, Y, W, H, hb, g)
        if bands and Y + H <= 1040:
            if P.get("bandLine"):
                E.append(box("Band bottom line", X, Y + H, W, 3, P["bandLine"], A("grow-x", 420, 200, out=OUT)))
            E.append(box("Band bottom", X, Y + H + 3, W, 34, None, A("wipe-right", 420, 120, out=OUT), bg=bands))
        return {"elements": E, "title": P.get("title"), "sub": P.get("subText"), "subText": P.get("subText"),
                "headText": P.get("headText")}

    def bar(b, main, role, g):
        st = b["style"]
        lower = (g.get("group") in ("lower", "note")) or g.get("group") == "full"
        extra = []
        if role == "TEAM":
            if not (main and lower and P.get("teamMain")):
                return []
            st.pop("fill", None)
            st["background"] = P["teamMain"]
            if P.get("teamStripe"):
                x, y, w, h = _r(b)
                s_ = P["teamStripe"]
                extra.append(box("Team stripe", x, y + h - s_, w, s_, "{%s.color}" % (b.get("_team") or "team"), A("grow-x", 300, 300, out=OUT)))
        else:
            bg = (P.get("roles") or {}).get(role)
            if bg is None:
                return []
            st.pop("fill", None)
            st.pop("blur", None)
            st["background"] = bg
        st.update((P.get("barBox") or {}))
        if main:
            st.update(P.get("mainBox") or {})
        b["_kit"] = True
        if main and P.get("barDecor") and g.get("group") in ("lower", "note"):
            U = _union(g["elements"])
            x, y, w, h = _r(b)
            if U and x + w >= U[0] + U[2] - 12:
                extra += P["barDecor"](_r(b), g)
        return extra

    def tile(b, g):
        if not P.get("tile"):
            return []
        st = b["style"]
        st.pop("fill", None)
        st.pop("background", None)
        st.update(P["tile"])
        for e in g["elements"]:
            if e.get("type") == "text" and _inside(e, _r(b), 4) and P.get("tileInk"):
                e.setdefault("style", {})["color"] = P["tileInk"]
                e["style"]["textShadow"] = ""
                e["_kit"] = True
        return []

    def transition(gid, g):
        T = P.get("tr")
        if not T:
            return None
        return T(gid, g, TA)

    def event(R, slab, g):
        if not P.get("slab"):
            return []
        return P["slab"](R, slab, g)

    K = dict(frame=frame, bar=bar, tile=tile, transition=transition, lower_decor=P.get("lowerDecor"), event=event, screen=P.get("screen"),
             bug=lambda b, U, g: bar(b, True, _role(b) or "PANEL", g))
    if P.get("table"):
        K["table"] = P["table"]
    return K
