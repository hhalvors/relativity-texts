#!/usr/bin/env python3
"""Resolve a paper to the scan it was transcribed from, and prove it is that scan.

Copied from ~/danish-texts/scans.py (2026-10-20); only this docstring differs.

~/bibliotek is a general philosophy library shared with other projects. This
repo uses five of its PDFs, each cut from a full journal-issue scan on the
Internet Archive (fetch-scans.sh records how). Do not rename the library to
suit this repo.

The failure that matters is a scan silently replaced by a different printing
or a different cut. Every \\opage{N} in a transcription encodes an offset into
one specific PDF; substitute another and every page marker is quietly wrong.
So identity here is the sha256 of the file, and the path is only an address.
A moved file keeps its byte size: stat every PDF (instant), hash only the size
matches.

  python3 scans.py path <paper>     absolute path, verified; non-zero exit if not
  python3 scans.py verify [paper…]  OK / MOVED / CHANGED / MISSING / UNRESOLVED
  python3 scans.py update           rewrite SCANS.tsv paths for MOVED files
  python3 scans.py rehash <paper> <path>   record a newly identified scan

A CHANGED result is never routine. A re-OCR of the same scan is benign and only
needs the hash updated; a different printing or cut invalidates the paper's
page map and every marker in it.
"""
import hashlib, os, subprocess, sys

REPO = os.path.dirname(os.path.abspath(__file__))
BIB  = os.path.join(os.path.dirname(REPO), "bibliotek")
TSV  = os.path.join(REPO, "SCANS.tsv")
COLS = ["book","scan","sha256","bytes","pages","page_size","witness","note"]


def load():
    head, rows = [], []
    for line in open(TSV, encoding="utf-8"):
        if line.startswith("#") or line.startswith("book\t"):
            head.append(line.rstrip("\n")); continue
        if line.strip():
            rows.append(dict(zip(COLS, line.rstrip("\n").split("\t"))))
    return head, rows


def save(head, rows):
    with open(TSV, "w", encoding="utf-8") as f:
        f.write("\n".join(head + ["\t".join(r.get(c, "") for c in COLS) for r in rows]) + "\n")


def abspath(rec):
    s = rec["scan"]
    if s == "UNRESOLVED": return None
    return os.path.join(REPO, s) if s.startswith("texts/") else os.path.join(BIB, s)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""): h.update(c)
    return h.hexdigest()


def refind(rec):
    """A moved file keeps its size. Stat is free; hash only the candidates."""
    want_b, want_h = int(rec["bytes"]), rec["sha256"]
    for root, _, files in os.walk(BIB):
        for fn in files:
            if not fn.lower().endswith(".pdf"): continue
            p = os.path.join(root, fn)
            try:
                if os.path.getsize(p) != want_b: continue
            except OSError: continue
            if sha(p) == want_h: return p
    return None


def pdfinfo(p):
    try:
        out = subprocess.run(["pdfinfo", p], capture_output=True, text=True, timeout=60).stdout
        pg = next((l.split(":",1)[1].strip() for l in out.splitlines() if l.startswith("Pages:")), "")
        sz = next((l.split(":",1)[1].strip() for l in out.splitlines() if l.startswith("Page size:")), "")
        return pg, sz
    except Exception:
        return "", ""


def check(rec):
    if rec["scan"] == "UNRESOLVED":
        return "UNRESOLVED", rec.get("note", ""), None
    p = abspath(rec)
    if not os.path.exists(p):
        found = refind(rec)
        return ("MOVED", os.path.relpath(found, BIB), found) if found else ("MISSING", rec["scan"], None)
    if sha(p) != rec["sha256"]:
        pg, szs = pdfinfo(p)
        same = (pg == rec["pages"] and szs == rec["page_size"])
        why = ("same page count and page size - probably re-OCR'd or re-compressed; "
               "verify a page reading, then accept" if same else
               "PAGE COUNT OR PAGE SIZE ALSO DIFFERS - this may be a different printing. "
               "The book's page map and every \\opage marker are suspect. Do not accept.")
        return "CHANGED", why, p
    return "OK", rec["scan"], p


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    head, rows = load()
    by = {r["book"]: r for r in rows}

    if cmd == "path":
        r = by.get(sys.argv[2]) or sys.exit(f"no such book: {sys.argv[2]}")
        st, info, p = check(r)
        if st in ("OK", "MOVED"): print(p); sys.exit(0)
        sys.exit(f"{st}: {sys.argv[2]} - {info}")

    if cmd == "rehash":
        book, path = sys.argv[2], os.path.abspath(sys.argv[3])
        r = by.get(book) or sys.exit(f"no such book: {book}")
        pg, szs = pdfinfo(path)
        r.update(scan=os.path.relpath(path, BIB) if path.startswith(BIB)
                      else os.path.relpath(path, REPO),
                 sha256=sha(path), bytes=str(os.path.getsize(path)),
                 pages=pg, page_size=szs, note="")
        save(head, rows); print(f"recorded {book} -> {r['scan']}  {r['sha256'][:16]}…")
        sys.exit(0)

    want = sys.argv[2:] if len(sys.argv) > 2 else None
    tally, moved = {}, []
    for r in rows:
        if want and r["book"] not in want: continue
        st, info, p = check(r)
        tally[st] = tally.get(st, 0) + 1
        if st == "MOVED": moved.append((r, p))
        if st != "OK" or want:
            print(f"{st:11s} {r['book']:44s} {info}")
    print("\n" + "  ".join(f"{k}: {v}" for k, v in sorted(tally.items())))
    if cmd == "update" and moved:
        for r, p in moved:
            r["scan"] = os.path.relpath(p, BIB)
        save(head, rows); print(f"updated {len(moved)} path(s)")
    elif moved:
        print("run `python3 scans.py update` to rewrite those paths")


if __name__ == "__main__":
    main()
