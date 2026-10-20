#!/usr/bin/env python3
"""ocrdiff.py -- catch transcription errors by diffing our words against the scan's.

Adapted 2026-10-20 from ~/danish-texts/ocrdiff.py, whose docstring gives the
reasons at length. In short: a transcriber handed OCR does not copy it, it
reads it and writes it again, and the words lost between the two are invisible
to every structural check. This compares the transcription's words with an
independent machine reading of the same page (the scan's Internet Archive OCR
layer, or an external witness such as tesseract) and lists every place they
diverge with three matching words on both sides.

Differences from the danish-texts version:
  * self-contained: no paginate.py; the scan comes from SCANS.tsv via scans.py,
    and the offset from the note there ("Journal p. = PDF + N") or --offset;
  * MATHEMATICS IS REMOVED from the transcription before comparing ($...$,
    \\[...\\], equation/align/gather environments, \\tag{}), because the IA
    layer's formulas are garbage. The words are checked here; the formulas are
    checked symbol by symbol at the image, never by this tool;
  * German letters (ä ö ü ß) count as word characters.

  python3 ocrdiff.py extended-bodies/ehrenfest-1909             whole paper
  python3 ocrdiff.py --frag texts/extended-bodies/herglotz-1910/.parts/pp393-399.texfrag
  python3 ocrdiff.py --frag F --ocr witness.txt          external witness, pages split by form feed

The output is a candidate list, not a verdict. Settle each at the image.
Record the result as one line in the paper's RESUME-NOTES:
  OCRDIFF: <witness> | <n> candidates | <n> corrected | <n> witness's fault | <n> unresolved
"""
import argparse, collections, difflib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.abspath(__file__))
PAGE_MARK = re.compile(r"\\opage\{(\d+)\}")


def strip_math(s):
    s = re.sub(r"%.*", "", s)
    s = re.sub(r"\\begin\{(equation|align|gather|multline|eqnarray)\*?\}.*?\\end\{\1\*?\}", " ", s, flags=re.S)
    s = re.sub(r"\\\[.*?\\\]", " ", s, flags=re.S)
    s = re.sub(r"\$\$.*?\$\$", " ", s, flags=re.S)
    s = re.sub(r"\$.*?\$", " ", s, flags=re.S)
    s = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", s, flags=re.S)
    s = re.sub(r"\\(includegraphics|label|ref|tag|opage|footnote)(\[[^\]]*\])?", r" \\\1 ", s)
    s = re.sub(r"\\(includegraphics|label|ref|tag)\s*\{[^}]*\}", " ", s)
    s = re.sub(r"\\opage\{\d+\}", " ", s)
    s = re.sub(r"\\(begin|end)\{[^}]*\}", " ", s)
    return s


def words(s, latex=False):
    if latex:
        s = strip_math(s)
        s = s.replace("\\ss{}", "ß").replace('\\"a', "ä").replace('\\"o', "ö").replace('\\"u', "ü")
        s = re.sub(r"\\footnote\s*(\[[^\]]*\])?", " ", s)
        s = re.sub(r"\\[a-zA-Z]+\*?\s*", " ", s)
        s = s.replace("{", " ").replace("}", " ").replace("~", " ")
    s = s.replace("\u00ad", "").replace("\u0131", "i")       # IA layer: dotless i for i
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)          # rejoin OCR line-break splits
    s = re.sub(r"[^0-9A-Za-zÀ-ɏ]+", " ", s)
    return [w.lower() for w in s.split() if w]


SUPPRESSED = [0]

CONFUSIONS = [set(p) for p in ("rb", "li", "l1", "i1", "fe", "ec", "eo", "nu",
                               "vy", "cg", "hb", "sg", "tf", "ao", "äa", "öo", "üu", "ßs")]


def looks_like_ocr(s, t):
    if len(s) != len(t) or " " in s or " " in t:
        return False
    diff = [(a, b) for a, b in zip(s, t) if a != b]
    return len(diff) == 1 and set(diff[0]) in CONFUSIONS


def label(kind, s, t):
    if kind == "DITTO":
        return "scan repeats itself — probably OCR"
    if kind == "MISSING":
        return "dropped word" if len(s.split()) == 1 else "dropped words"
    if kind == "EXTRA":
        return "word not in scan"
    if looks_like_ocr(s, t):
        return "likely OCR"
    if len(s) > 3 and len(t) > 3 and s[:3] == t[:3]:
        return "form modernised?"          # Relativitätsprinzipes/-prinzips, giebt/gibt
    return ""


def collect(spans, pages, off, vocab, pad=1, floor=None):
    """Compare each page's span with a window of scan pages (N-pad..N+pad)."""
    d_floor, r_floor = (2, 2) if floor is None else (floor, floor)
    raw = []
    for p, text in spans:
        idx = p - off - 1                     # PDF page index (0-based)
        if not (0 <= idx < len(pages)):
            continue
        lo, hi = max(0, idx - pad), min(len(pages), idx + pad + 1)
        T, S = words(text, latex=True), words(" ".join(pages[lo:hi]))
        if len(S) < 20 or len(T) < 6:
            continue
        sm = difflib.SequenceMatcher(None, S, T, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            if i1 < 3 or j1 < 3 or i2 > len(S) - 3 or j2 > len(T) - 3:
                continue
            if S[i1-3:i1] != T[j1-3:j1] or S[i2:i2+3] != T[j2:j2+3]:
                continue
            s, t = " ".join(S[i1:i2]), " ".join(T[j1:j2])
            before, after = " ".join(T[max(0, j1-6):j1]), " ".join(T[j2:j2+6])
            if tag == "delete" and 0 < i2 - i1 <= 4:
                # Single letters and bare numbers that the transcription lacks are,
                # in these papers, nearly always the symbols of inline formulas the
                # tex side has had removed ($O$, $n$, $V$): suppressed and counted.
                # NOT two-letter tokens: a dropped "in", "zu", "an" is exactly the
                # error this tool exists to catch.
                if all(len(w) == 1 or w.isdigit() for w in S[i1:i2]):
                    SUPPRESSED[0] += 1
                    continue
                if all(vocab[w] >= d_floor for w in S[i1:i2]):
                    n = i2 - i1
                    near = T[max(0, j1-10):j1] + T[j2:j2+10]
                    dit = any(near[x:x+n] == S[i1:i2] for x in range(len(near) - n + 1))
                    raw.append((p, "DITTO" if dit else "MISSING", s, t,
                                f"{before} \u27ea scan has: {s} \u27eb {after}"))
            elif tag == "insert" and 0 < j2 - j1 <= 2:
                raw.append((p, "EXTRA", s, t, f"{before} \u27ea tex only: {t} \u27eb {after}"))
            elif tag == "replace" and i2 - i1 <= 2 and j2 - j1 <= 2:
                if s.replace(" ", "") == t.replace(" ", ""):
                    continue
                if difflib.SequenceMatcher(None, s, t).ratio() < 0.5:
                    continue
                raw.append((p, "DIFFERS", s, t,
                            f"{before} \u27ea tex: {t}  |  scan: {s} \u27eb {after}"))
    return raw


def report(out, header):
    print(header + "\n")
    for p, kind, s, t, ctx in out:
        tag = label(kind, s, t)
        print(f"p.{p:>4} {kind:<8} {ctx}" + (f"  [{tag}]" if tag else ""))
    if SUPPRESSED[0]:
        print(f"\n  ({SUPPRESSED[0]} scan-only single letters/numbers suppressed: formula symbols)")
    print("\n  Settle every one of these at the image. Some are OCR error; the rest are"
          "\n  transcription error, the class no other check can see.")


def scan_for(paper):
    r = subprocess.run([sys.executable, os.path.join(REPO, "scans.py"), "path", paper],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip() or r.stdout.strip())
    return r.stdout.strip()


def offset_for(paper):
    for line in open(os.path.join(REPO, "SCANS.tsv"), encoding="utf-8"):
        if line.startswith(paper + "\t"):
            m = re.search(r"Journal p\. = PDF \+ (\d+)", line)
            if m:
                return int(m.group(1))
    sys.exit(f"no 'Journal p. = PDF + N' in SCANS.tsv for {paper}; pass --offset")


def pdf_pages(path):
    out = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"],
                         capture_output=True, text=True).stdout
    return out.split("\f")


def spans_of(text):
    marks = list(PAGE_MARK.finditer(text))
    out = []
    for m, nx in zip(marks, marks[1:] + [None]):
        out.append((int(m.group(1)), text[m.end(): nx.start() if nx else len(text)]))
    return out


def paper_of(path):
    d = os.path.dirname(os.path.abspath(path))
    if os.path.basename(d) == ".parts":
        d = os.path.dirname(d)
    rel = os.path.relpath(d, os.path.join(REPO, "texts"))
    return d, rel


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paper", nargs="?", help="topic/paper, e.g. extended-bodies/laue-1911")
    ap.add_argument("--frag", help="a .texfrag to check before splicing")
    ap.add_argument("--ocr", help="external witness: text file, one page per form feed, "
                                  "pages in the order of the fragment's \\opage markers")
    ap.add_argument("--offset", type=int, help="journal page = PDF page + OFFSET")
    a = ap.parse_args()

    if a.frag:
        text = open(a.frag, encoding="utf-8").read()
        d, paper = paper_of(a.frag)
    elif a.paper:
        paper = a.paper
        d = os.path.join(REPO, "texts", paper)
        text = open(os.path.join(d, "transcription.tex"), encoding="utf-8").read()
        text = text.partition("\\begin{document}")[2] or text
    else:
        ap.error("give a paper (topic/paper) or --frag")

    spans = spans_of(text)
    if not spans:
        sys.exit("no \\opage markers; nothing to bound.")
    if a.ocr:
        chunks = [c for c in open(a.ocr, encoding="utf-8").read().split("\f") if c.strip()]
        if len(chunks) != len(spans):
            sys.exit(f"witness has {len(chunks)} pages, text marks {len(spans)}")
        first = spans[0][0]
        pages, off = chunks, first - 1
        witness = f"external ({os.path.basename(a.ocr)})"
    else:
        pages = pdf_pages(scan_for(paper))
        off = a.offset if a.offset is not None else offset_for(paper)
        witness = "embedded layer"
    vocab = collections.Counter(words(" ".join(pages))) + collections.Counter(words(text, latex=True))
    out = sorted(collect(spans, pages, off, vocab, floor=1 if a.ocr else None))
    report(out, f"{paper}: pp. {spans[0][0]}\u2013{spans[-1][0]}, journal p. = PDF + {off} \u2014 "
                f"{len(out)} divergence(s) from the {witness}")
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
