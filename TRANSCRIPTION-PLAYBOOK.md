# Transcription playbook (relativity-texts)

The method is danish-texts' (`~/danish-texts/TRANSCRIPTION-PLAYBOOK.md`: read
§00 and §3 first). This file records only what differs for journal articles in
German Antiqua with mathematics, and what the pilots taught.

## 1. Per paper, before anything else

1. `python3 scans.py path <topic>/<paper>` — the verified scan.
2. Read the paper's `RESUME-NOTES.md` (page map, edition check, resume point).
3. **Edition check.** Look for an existing transcription of the same printing
   (German Wikisource first: `Seite:<title>.djvu/<n>` pages, fetched with
   `?action=raw`). If one exists, it is the draft; diff it against the layer
   (`ocrdiff.py`) and read the page images against it. Checked 2026-10-20:
   only Ehrenfest 1909 is on Wikisource; Laue, Herglotz, Noether and Born are on
   neither German nor English Wikisource.
4. Otherwise the draft comes from the scan's text layer by script
   (`pdftotext -f N -l N`), prose only. **The layer's formulas are garbage**:
   every formula is set from the page image.

## 2. Accuracy (danish-texts §00 points 1–4, unchanged)

- No agent re-types prose that a machine text already supplies; readers report
  corrections as a list.
- Every page is read at the image by an agent that did not produce the text,
  with **two planted control errors** per reader (one one-letter change in the
  prose, one change to a formula — a dropped prime, a changed index or sign).
  A reader whose controls are not both reported reads again.
- **Formulas are read twice**, symbol by symbol, by two agents; one of them may
  be the agent that set them, the other must not be.
- `python3 ocrdiff.py <topic>/<paper>` (or `--frag` per batch) before
  splicing; record `OCRDIFF: <witness> | <n> candidates | <n> corrected | <n>
  witness's fault | <n> unresolved` in RESUME-NOTES. ocrdiff strips the
  mathematics before comparing, so it witnesses prose only.
- Agents stage images in ≤2 calls, render to `mktemp -d` (never into the repo),
  save results to a file as they go, and stop after two failed device calls.
- Crop sheets for agents ≤ ~1560 px on the long side (Read downscales larger
  images).

## 3. Batches (Herglotz, Noether, Born)

Formula-dense papers: batches of 4–6 journal pages per agent, fragments written
to `.parts/pp<FIRST>-<LAST>.texfrag` (never `.tex`), spliced by the caller.
Pilot one batch and measure its cost before dispatching more; ≤5 agents at a
time. See danish-texts TRANSLATION-PLAYBOOK §6e for the formula-heavy model.

## 4. Conventions (differences from danish-texts)

1. **Class.** Journal articles: `\documentclass[12pt,a4paper]{article}` from
   `templates/article.tex`. Each file is self-contained. (The danish-texts rule
   "a book is never `article`" concerns books.)
2. **Spelling and typography as printed.** 1909–11 orthography (*daß*,
   *Relativitäts-Prinzipes*, *giebt* if printed); the printer's hyphenated
   compounds as printed. babel `[german]` (1901 patterns), not `ngerman`.
3. **Emphasis.** The print's letterspacing (and italic, where the journal sets
   it) is `\emph{}`. Names spaced in the original ("M. Born") are emphasis.
4. **Page markers.** `\opage{918}` at the exact word where journal page 918
   begins. Journal pages, not PDF pages. Before a `[`: `\opage{N}\relax[`.
5. **Equations.** Reproduce the printed notation exactly ($ict$, $R_4$, primes,
   indices). Keep printed equation numbers with `\tag{12}`, `\tag{4b}`. Do not
   renumber or modernize. A displayed formula without a number is `\[ … \]`.
   Misprints: `% sic:` comment at the end of the physical line, and a bracketed
   "[Tr.]" note in the translation only.
6. **Footnotes.** Numbered as printed. The journals restart footnote numbers on
   each page, so set `\footnote[n]{…}` with the printed number.
7. **Figures.** Redraw in TikZ if simple; otherwise a cleaned crop of the scan,
   `figures/fig1.png` at 300 dpi, noted in the header and RESUME-NOTES.
8. **Columns and other articles.** *Phys. Z.* is set in two columns and its
   pages carry other articles: transcribe only the paper's own text, and put
   `\opage` where the paper's text on that page begins. The journal's running
   heads, column numbers and signatures are not transcribed.
9. **Header.** The comment block at the top of `transcription.tex` states the
   source, the scan's sha256, the page map, how accuracy was established
   (with the OCRDIFF totals), and every misprint kept. It is the record of the
   edition; RESUME-NOTES is untracked.
10. **Dashes and quotes.** The print's dash (Gedankenstrich) as `--` or `---`
   matching its length; German quotes as the Unicode „…“ the print shows.

## 5. Compile test (the Cowork VM has no libertinus and no babel-german)

```sh
d=$(mktemp -d); cp transcription.tex $d/t.tex; cd $d
sed -i -e 's/\\usepackage{libertinus}/\\usepackage{lmodern}/' -e '/libertinust1math/d' \
       -e 's/\\usepackage\[german\]{babel}.*//' t.tex     # the VM has no babel-german either
pdflatex -interaction=nonstopmode -halt-on-error t.tex >/dev/null; pdflatex -interaction=nonstopmode -halt-on-error t.tex | grep -E '^!|Output written'
grep -c 'Missing character' t.log
```

Expect `Output written` and 0 missing characters. Real builds (`make`) happen on
Hans's machine.

## 6. Lessons

(Add lessons that apply beyond one paper here, the same day.)

- **Wikisource quality 4 is not diplomatic** (Ehrenfest, 2026-10-20). The
  proofread page had two word errors in one page — „sonder“ for the print's
  „sondern“, and „dimensionslose“ for the print's „dimensionierte“, a change of
  sense — plus an emphasis span cut short and the footnote's bold volume numbers
  lost. The layer diff caught the second; only the image reading caught the
  others. Treat a Wikisource text as a draft, never as the text of record.
- **A comparison reader misses one-letter case endings** (Laue, 2026-10-20). A
  Sonnet reader checking a draft against the image found the planted formula
  control at once but missed the planted prose control („einer“ for „eines“)
  until told one had been missed. danish-texts measured the same (comparison
  spot-reads catch ~1 of 2 controls). For the long papers prefer **blind**
  reading (the reader transcribes the page; a script compares it with the draft
  and the layer), keep the controls for any comparison reading, and never accept
  a reading whose controls were not both found on the first pass.
- **ocrdiff noise from formulas**: with the mathematics stripped from the
  transcription, the layer's formula letters show as "dropped words". ocrdiff now
  suppresses (and counts) scan-only single letters and bare numbers, never
  two-letter words (a dropped „in“, „zu“ is the error it exists for). The IA
  layer writes a dotless ı for i; ocrdiff folds it.
- **Cost, measured** (agent tokens): Ehrenfest image check 108k (1 p.); Laue
  draft with formulas 147k + second reading 146k + re-read (3 pp.) — about
  100k a page for a short paper including fixed overhead.
