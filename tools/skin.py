"""Skin pass: redraws shared graphics in a package's own look.

The shared generators (broadcast_lib, sports_lib, and the Night Game graphics a package borrows) are built with
marker colours (MARKS). skin() then walks every element and, from the role each box or text played (panel, second
panel, dark band, light strip, value box, highlight, team block, thin rule), applies the style's real fills, corner
radius, borders, shadows, fonts, italics, outlines and text colours. A "boxless" style (Throwback 80s, Retro) drops
the boxes and keeps rules and type only, the way those looks work on air.
"""
import copy
import re

MARKS = {"panel": "@@PANEL@@", "panel2": "@@PANEL2@@", "dark": "@@DARK@@", "strip": "@@STRIP@@", "stripText": "@@STRIPINK@@",
         "val": "@@VAL@@", "valText": "@@INK@@", "hi": "@@HI@@", "hiText": "@@HITEXT@@", "line": "@@LINE@@",
         "teamGrad": "@@TEAM:%s|%s|%s@@", "titleBg": "@@TITLE@@", "shadow": "@@SHADOW@@"}

BOX_ROLES = ("PANEL", "PANEL2", "DARK", "STRIP", "VAL", "HI", "TEAM", "TITLE")
TEAM_RE = re.compile(r"@@TEAM:([a-zA-Z0-9_.]+)\|[^@]*@@")
NG_TEAM_RE = re.compile(r"^\{([a-zA-Z0-9_.]+)\.color\}(@[0-9.]+)?$")
TEAM_ANY_RE = re.compile(r"\{([a-zA-Z0-9_.]+)\.color\}")


def _norm_fill(v):
    """Night Game graphics use theme tokens; read them as roles too."""
    if not isinstance(v, str):
        return v
    s = v.strip()
    if s in ("$card", "$panel") or s.startswith("$panel@") or s.startswith("$card@"):
        return "@@PANEL@@"
    if s.startswith("$panel2"):
        return "@@PANEL2@@"
    if s.startswith("$primary"):
        return "@@DARK@@"
    if s.startswith("$accent") and "@0." not in s:
        return "@@HI@@"
    if s.upper().startswith("#FFFFFF@0.9") or s.startswith("rgba(255,255,255,0.9"):
        return "@@STRIP@@"
    m = NG_TEAM_RE.match(s)
    if m:
        return "@@TEAM:%s|x|x@@" % m.group(1)
    low = s.lower()
    if "#3396f5" in low or "#3d7bd0" in low:
        return "@@HI@@"
    if low in ("#121620", "#05080f", "#13161b", "#16181c", "#111111", "#1e1e1e", "#0a1f44"):
        return "@@DARK@@"
    if low in ("#ffffff", "linear-gradient(90deg, #dadfe6, #ffffff, #c9cfd8)", "linear-gradient(180deg, #ffffff, #c9ced6)"):
        return "@@STRIP@@"
    m = TEAM_ANY_RE.search(s)
    if m and "color-mix" in s and "brand." not in s:
        return "@@TEAM:%s|x|x@@" % m.group(1)
    return v


def _role(st):
    for k in ("background", "fill"):
        v = st.get(k)
        if isinstance(v, str):
            if v.startswith("@@TEAM:"):
                return "TEAM", TEAM_RE.match(v).group(1) if TEAM_RE.match(v) else "team"
            for r in BOX_ROLES:
                if v.startswith("@@%s@@" % r):
                    return r, None
    return None, None


def _resolve(obj, K):
    """Replace every marker left in strings (table, field and ticker styles, borders...)."""
    if isinstance(obj, dict):
        return dict((k, _resolve(v, K)) for k, v in obj.items())
    if isinstance(obj, list):
        return [_resolve(v, K) for v in obj]
    if isinstance(obj, str) and "@@" in obj:
        s = TEAM_RE.sub(lambda m: K["team"](m.group(1)), obj)
        for name, val in (("PANEL2", K["panel2"]), ("PANEL", K["panel"]), ("DARK", K["dark"]), ("STRIP", K["strip"]), ("VAL", K["val"]),
                          ("HITEXT", K["hiText"]), ("HI", K["hi"]), ("STRIPINK", K["stripText"]), ("INK", K["ink"]), ("LINE", K["line"]), ("TITLE", K["title"]),
                          ("SHADOW", K["shadow"])):
            s = s.replace("@@%s@@" % name, val)
        return s
    return obj


def skin_graphic(g, K):
    g = copy.deepcopy(g)
    boxless = K.get("boxless")
    for e in g.get("elements", []):
        st = e.setdefault("style", {})
        t = e.get("type")
        if e.get("_kit"):
            e.update(_resolve(dict((k, v) for k, v in e.items() if k != "anim"), K))
            continue
        if t == "box":
            for k in ("background", "fill"):
                if k in st:
                    st[k] = _norm_fill(st[k])
            role, team = _role(st)
            thin = min(int(e.get("w") or 0), int(e.get("h") or 0)) <= 12
            full = int(e.get("w") or 0) >= 1900 and int(e.get("h") or 0) >= 1000
            if boxless and not role and not full and not thin:
                bgv = str(st.get("background") or st.get("fill") or "")
                if bgv and "url(" not in bgv and "conic" not in bgv and "{brand." not in bgv:
                    st.pop("background", None)
                    st["fill"] = "transparent"
                    for k in ("shadow", "borderW", "borderColor", "blur"):
                        st.pop(k, None)
            if role and not full:
                if thin:
                    st.pop("background", None)
                    st["fill"] = K["rule"]
                    st.pop("radius", None)
                elif boxless and role != "TITLE":
                    st.pop("background", None)
                    st["fill"] = "transparent"
                    for k in ("shadow", "borderW", "borderColor", "blur", "radius"):
                        st.pop(k, None)
                else:
                    kind = "light" if role in ("STRIP", "VAL") else ("hi" if role == "HI" else "panel")
                    extra = K.get(kind + "Box") or {}
                    if "radius" in st or role in ("PANEL", "PANEL2", "TEAM") or kind == "light":
                        st["radius"] = extra.get("radius", K.get("radius", st.get("radius", 0)))
                    for k in ("borderW", "borderColor", "shadow"):
                        if k in extra:
                            st[k] = extra[k]
                    st.pop("blur", None) if K.get("noBlur") else None
            elif role == "TITLE" and boxless:
                pass
        elif t == "text":
            c = st.get("color", "$text")
            if isinstance(c, str) and c.startswith("$primary"):
                c = st["color"] = "@@INK@@"
            dark = isinstance(c, str) and (c == "@@INK@@" or (c == "@@STRIPINK@@" and K.get("stripDark", True))
                                           or (c == "@@HITEXT@@" and K.get("hiDark", False))
                                           or c.lower() in ("#0a1f44", "#16181c", "#121620", "#15171b", "#4a5262"))
            if boxless:
                if dark:
                    st["color"] = K["text2"]
                spec = K.get("text") or {}
            else:
                spec = (K.get("textDark") if dark else K.get("text")) or {}
            small = float(st.get("size") or 32) < float(K.get("strokeMin", 0))
            for k, v in spec.items():
                if k == "textShadow" and st.get("textStroke") and k in st:
                    continue
                if small and k in ("textStroke", "textShadow") and K.get("strokeMin"):
                    continue
                st[k] = v
        elif t == "table":
            if boxless:
                for k in ("rowFill", "altFill", "headerFill", "highlightFill"):
                    if k in st:
                        st[k] = "transparent"
                st["textShadow"] = (K.get("text") or {}).get("textShadow", "")
                cols = e.get("columns") or []
                for ccol in cols:
                    if ccol.get("fill"):
                        ccol["fill"] = "transparent"
                    if isinstance(ccol.get("color"), str) and ccol["color"] in ("@@INK@@", "@@HITEXT@@", "@@STRIPINK@@"):
                        ccol["color"] = K["text2"]
            for k in ("italic", "font"):
                if k in (K.get("text") or {}):
                    st[k] = K["text"][k]
        e.update(_resolve(dict((k, v) for k, v in e.items() if k != "anim"), K))
    return _resolve(g, K)


def skin_all(graphics, K, only=None):
    """Skin every graphic in graphics (dict), or just the ids in only."""
    out = {}
    for gid, g in graphics.items():
        out[gid] = skin_graphic(g, K) if (only is None or gid in only) else g
    return out
