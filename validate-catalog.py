#!/usr/bin/env python3
"""Validate catalog.yaml against what ~/hhalvors.github.io/RelativityTexts.hs reads.

That generator renders /relativity/ from this file (symlinked there as
data/relativity-texts.yaml). Aeson ignores unknown keys, so a misspelled key
reads as a missing one; a missing required key fails the site build. Checks:
  * Topic: id, title, papers; texts/<topic>/ exists once any paper is started.
  * Paper: id, author, title, year, status, links, publish (true/false), phase;
    status one of complete | in-progress | to-do; phase-1 papers also need
    title-en and source; a paper that is not to-do has transcription.tex in
    texts/<topic>/<id>/; a complete paper has links.
  * Ids are unique within a topic.
  * The papers with publish: false are exactly those in PRIVATE in the Makefile
    (as texts/<topic>/<id>), which keeps their PDFs out of `make public`.
"""
import os, re, sys, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOPIC  = ["id", "title", "papers"]
PAPER  = ["id", "author", "title", "year", "status", "links", "publish", "phase"]
STATUS = {"complete", "in-progress", "to-do"}
problems = []

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "catalog.yaml")
doc = yaml.safe_load(open(path, encoding="utf-8"))
private_cat = set()
for ti, t in enumerate(doc.get("topics") or []):
    tw = f"topics[{ti}] ({t.get('id')})"
    missing = [k for k in TOPIC if k not in t]
    if missing:
        problems.append(f"{tw}: missing {missing}"); continue
    seen = set()
    for pi, p in enumerate(t["papers"] or []):
        pw = f"{tw}.papers[{pi}] ({p.get('id')})"
        for k in PAPER:
            if k not in p: problems.append(f"{pw}: missing '{k}'")
        if p.get("id") in seen: problems.append(f"{pw}: duplicate id")
        seen.add(p.get("id"))
        if p.get("status") not in STATUS: problems.append(f"{pw}: unknown status {p.get('status')!r}")
        if not isinstance(p.get("links"), list): problems.append(f"{pw}: links must be a list (use [] when empty)")
        else:
            for j, l in enumerate(p["links"]):
                if not isinstance(l, dict) or "label" not in l or "url" not in l:
                    problems.append(f"{pw}.links[{j}]: needs label and url")
        if not isinstance(p.get("publish"), bool): problems.append(f"{pw}: publish must be true or false")
        elif p["publish"] is False: private_cat.add(f"{t['id']}/{p['id']}")
        if not isinstance(p.get("phase"), int): problems.append(f"{pw}: phase must be 1 or 2")
        if p.get("phase") == 1:
            for k in ("title-en", "source"):
                if k not in p: problems.append(f"{pw}: phase-1 paper lacks '{k}'")
        if p.get("status") in ("in-progress", "complete"):
            tex = os.path.join(HERE, "texts", t["id"], str(p.get("id")), "transcription.tex")
            if not os.path.isfile(tex): problems.append(f"{pw}: status {p['status']} but {os.path.relpath(tex, HERE)} is missing")
        if p.get("status") == "complete" and not p.get("links"):
            problems.append(f"{pw}: complete but has no links")

mk = open(os.path.join(HERE, "Makefile"), encoding="utf-8").read()
m = re.search(r"^PRIVATE\s*:=([^\n]*)", mk, re.M)
private_mk = set(m.group(1).split()) if m else set()
if private_mk != private_cat:
    problems.append(f"Makefile PRIVATE {sorted(private_mk)} != catalog publish:false {sorted(private_cat)}")

print(f"{len(problems)} problem(s)")
for p in problems: print("  " + p)
sys.exit(1 if problems else 0)
