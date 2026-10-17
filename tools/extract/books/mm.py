"""Monster Manual (2014): every stat block creatures.py can read from your extracted pages."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import creatures


def build():
    cs = creatures.parse("mm", 1, 354)
    print("creatures: %d (%d with all six scores)" % (len(cs), sum("abilities" in c for c in cs)))
    return {"creatures": sorted(cs, key=lambda c: c["name"])}
