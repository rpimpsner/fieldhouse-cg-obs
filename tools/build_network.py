"""Builds the "Network" package: templates/packages/network.json.

National-broadcast look: bold condensed caps, navy panels with gold accents, team-colour blocks, white
stat strips. Scorebugs, lower thirds, cards, comparisons, game final / summary, top performers, matchups,
side panels, automatic event stingers and show graphics come from tools/broadcast_lib.py; Due Up,
lineup, pitching, defense, linescore, standings, inning sponsor, custom / note and transitions are
taken from the Night Game package and pick up this package's theme. Run:  python tools/build_network.py
(after tools/build_night_game.py).
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import broadcast_lib as BL  # noqa: E402

S = BL.NETWORK
night = json.load(open(os.path.join(ROOT, "templates", "packages", "night-game.json"), encoding="utf-8"))["graphics"]

g = {}
g["scorebug"] = BL.scorebug_network(S)
g["bug_bar"] = BL.scorebug_bar(S)
g["bug_logos"] = BL.scorebug_logos(S)
g["batter"] = BL.lower_note(S, "bat")
g["pitcher"] = BL.lower_note(S, "pit")
g["batter_card"] = BL.stat_card_tonight(S, "bat")
g["pitcher_card"] = BL.stat_card_tonight(S, "pit")
for gid in ("dueup", "inning_sponsor", "standings", "lineup", "pitching", "defense", "linescore", "spotlight", "custom", "note", "stinger", "opener"):
    g[gid] = copy.deepcopy(night[gid])
g["matchup"] = BL.matchup_banner(S)
new = BL.all_new(S)
for gid, gdef in new.items():
    if gid in ("batter_note", "pitcher_note", "matchup_banner"):
        continue
    g[gid] = gdef
g["batter"]["name"], g["pitcher"]["name"] = "Batter Lower Third", "Pitcher Lower Third"
g["matchup"]["name"] = "Matchup"

for gid in BL.PICKABLE:
    if gid in g:
        g[gid]["pickable"] = True
HALF = "half_{halfKey}"
slots = dict(BL.SPONSOR_SLOTS)
slots.update({"scorebug": HALF + ", scorebug", "bug_bar": HALF + ", scorebug", "bug_logos": HALF + ", scorebug",
              "batter": "lineup_{batter.slot}, batter", "pitcher": "pitcher", "batter_card": "lineup_{batter.slot}, batter_card",
              "pitcher_card": "pitcher_card", "dueup": HALF + ", dueup", "inning_sponsor": HALF, "spotlight": "lineup_{batter.slot}, spotlight"})
for gid, slot in slots.items():
    if gid in g:
        g[gid]["sponsorSlot"] = slot

doc = {
    "version": 2,
    "name": "Network",
    "description": "National-broadcast look: condensed caps, navy and gold, stat strips, comparisons, game final and summary, side panels, "
                   "automatic home run / wild pitch stingers and batting practice / pregame / postgame show graphics.",
    "theme": {
        "primary": "#0A1F44", "accent": "#F2B705", "text": "#FFFFFF", "dim": "rgba(255,255,255,0.74)", "line": "rgba(255,255,255,0.20)",
        "card": "rgba(10,31,68,0.94)", "panel": "rgba(10,31,68,0.94)", "panel2": "rgba(19,48,95,0.94)",
        "font": "'Inter Var', 'Segoe UI', Arial, sans-serif",
        "font2": "'Bahnschrift Condensed', 'Bahnschrift SemiCondensed', Bahnschrift, 'DIN Condensed', 'Roboto Condensed', 'Arial Narrow', 'Inter Var', sans-serif",
        "logo": "", "brandName": "", "openerVideo": "",
    },
    "graphics": g,
}
import sports_lib as SL  # noqa: E402
g.update(SL.all_sports(S))     # basketball, football, hockey
out = os.path.join(ROOT, "templates", "packages", "network.json")
BL.stamp(doc)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
print("wrote", out, "graphics:", len(g))
