#!/usr/bin/env python3
"""Validate catalog.yaml.

Two sets of checks:
 1. The danish-texts schema (copied from ~/danish-texts/validate-catalog.py,
    2026-10-20): the keys DanishTexts.hs requires, so that a trimmed copy of that
    generator can read this file. Aeson ignores unknown keys; a MISSING required
    key is what breaks a site build.
 2. This repo's own keys: every work has `publish` (true/false) and `phase`;
    every phase-1 work has `title_en` and `source`; status values are known; and
    the works with `publish: false` are exactly those listed in PRIVATE in the
    Makefile, which is what keeps their PDFs out of `make public`.
"""
import os, re, sys, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LINK    = [("label",1),("url",1)]
SECTION = [("title",1),("status",1),("links",1)]
WORK    = [("id",1),("title",1),("year",1),("venue",0),("note",0),("sections",1),
           ("publish",1),("phase",1)]
AUTHOR  = [("id",1),("name",1),("dates",1),("bio",1),("works",1)]
STATUS  = {"complete", "in-progress", "to-do"}

problems = []

def check(obj, spec, where, typename):
    if not isinstance(obj, dict):
        problems.append(f"{where}: expected a mapping for {typename}"); return False
    for key, req in spec:
        if req and key not in obj:
            problems.append(f"{where}: {typename} is missing required key '{key}'")
    return True

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "catalog.yaml")
doc = yaml.safe_load(open(path, encoding="utf-8"))
private_cat = set()
for ai, a in enumerate(doc.get("authors") or []):
    aw = f"authors[{ai}] ({a.get('id')})"
    if not check(a, AUTHOR, aw, "Author"): continue
    for wi, w in enumerate(a.get("works") or []):
        ww = f"{aw}.works[{wi}] ({w.get('id')})"
        if not check(w, WORK, ww, "Work"): continue
        if not isinstance(w.get("publish"), bool):
            problems.append(f"{ww}: publish must be true or false")
        elif w["publish"] is False:
            private_cat.add(f"{a['id']}/{w['id']}")
        if w.get("phase") == 1:
            for k in ("title_en", "source"):
                if k not in w: problems.append(f"{ww}: phase-1 work lacks '{k}'")
            started = any(s.get("status") != "to-do" for s in w.get("sections") or [])
            d = os.path.join(HERE, "texts", a["id"], w["id"], "transcription.tex")
            if started and not os.path.isfile(d):
                problems.append(f"{ww}: status is not to-do but texts/{a['id']}/{w['id']}/transcription.tex is missing")
        for si, s in enumerate(w.get("sections") or []):
            sw = f"{ww}.sections[{si}]"
            if check(s, SECTION, sw, "Section"):
                if s.get("status") not in STATUS:
                    problems.append(f"{sw}: unknown status {s.get('status')!r}")
                if not isinstance(s.get("links"), list):
                    problems.append(f"{sw}: links must be a list (use [] when empty)")
                else:
                    for j, l in enumerate(s["links"]): check(l, LINK, f"{sw}.links[{j}]", "Link")

mk = open(os.path.join(HERE, "Makefile"), encoding="utf-8").read()
m = re.search(r"^PRIVATE\s*:=([^\n]*)", mk, re.M)
private_mk = set(m.group(1).split()) if m else set()
if private_mk != private_cat:
    problems.append(f"Makefile PRIVATE {sorted(private_mk)} != catalog publish:false {sorted(private_cat)}")

print(f"{len(problems)} problem(s)")
for p in problems: print("  " + p)
sys.exit(1 if problems else 0)
