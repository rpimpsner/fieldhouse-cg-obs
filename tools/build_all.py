"""Rebuild every style package in dependency order (Night Game first: the others copy some of its graphics).
Run:  python tools/build_all.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["build_night_game.py", "build_network.py", "build_classic.py", "build_classic_designs.py", "build_retro.py", "build_empire.py", "build_y2k.py",
         "build_metro.py", "build_kids.py", "build_80s.py", "build_winter.py", "build_podcast.py", "build_national1.py", "build_national2.py", "build_caribbean.py",
         "build_themes.py"]

for f in ORDER:
    r = subprocess.run([sys.executable, os.path.join(HERE, f)], capture_output=True, text=True)
    print(f, "ok" if r.returncode == 0 else "FAILED")
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-4000:])
        sys.exit(1)
