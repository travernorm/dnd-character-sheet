"""Shared helpers for book definition files: find where a subclass or feat is in the
extracted pages and fill feature text from there."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fx import slug
import text as T


class Book:
    def __init__(self, book, first, last, body=None):
        """body: first page after the table of contents (headings before it are ignored by locate)."""
        self.book, self.first, self.last, self.body = book, first, last, body or first
        self.found, self.missing = 0, []

    def locate(self, title):
        """First page where `title` is a heading line, or None."""
        ls = T.lines(self.book, self.first, self.last)
        hits = [i for i, (p, s) in enumerate(ls) if p >= self.body and T.is_heading(s, [title])]
        prose = [i for i in hits if any(len(s) > 40 for _, s in ls[i + 1:i + 3])]  # a list entry is followed by more short lines
        caps = [i for i in prose if ls[i][1].isupper()]  # the heading in capitals before a table row ("College of Glamour", "3rd", a blurb)
        table = [i for i, (p, s) in enumerate(ls) if p >= self.body and s.isupper() and T.is_heading(s, [title + " Features"])]
        for i in caps + table + prose:  # a decorative heading the scan misreads ("SaouT") still has its "SCOUT FEATURES" table
            return ls[i][0]
        return ls[hits[0]][0] if hits else None

    def fill(self, feats, title=None, span=6, stops=(), limit=2400):
        """Fill each feature's text from the pages after `title` (or the whole book)."""
        start = self.locate(title) if title else None
        a, b = (max(self.first, start - 1), min(self.last, start + span)) if start else (self.first, self.last)
        names = [f["name"] for f in feats] + list(stops)
        for f in feats:
            heads = [f["name"]] + ([f["name"].split(": ", 1)[1]] if ": " in f["name"] else [])
            others = [n for n in names if n != f["name"]] + [n.split(": ", 1)[1] for n in names if ": " in n and n != f["name"]]
            t = None
            for h in heads:
                t = T.section(self.book, a, b, h, stops=others, after=title, limit=limit)
                if t:
                    break
            if t and len(t) > 40:
                f["text"] = t
                self.found += 1
            else:
                self.missing.append((title + ": " if title else "") + f["name"])
        return feats

    def subclass(self, cls, name, feats, spells=None, nxt=None, span=6):
        e = {"id": slug(name), "name": name, "class": cls, "features": self.fill(feats, name, span=span, stops=[nxt] if nxt else [])}
        page = self.locate(name)
        if page:
            e["page"] = page
        if spells:
            e["spells"] = spells
        return e

    def report(self):
        print("feature text found for %d; missing %d: %s" % (self.found, len(self.missing), ", ".join(self.missing[:25])))
