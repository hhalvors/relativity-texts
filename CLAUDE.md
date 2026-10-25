# Working in relativity-texts

Transcriptions and English translations of early papers on relativity theory,
beginning with the rigid-body papers of 1909–1911 (Born, Ehrenfest, Herglotz,
F. Noether, Laue). Each paper gets a diplomatic transcription of the published
text with its original pagination, an English translation, and PDFs.

This repo inherits the method of `~/danish-texts`. **Before a transcription or
translation job, read `~/danish-texts/CLAUDE.md`,
`~/danish-texts/TRANSCRIPTION-PLAYBOOK.md` §00 and §3, and
`~/danish-texts/TRANSLATION-PLAYBOOK.md` §§0–4.** The playbooks here record
only what differs. (Set up 2026-10-20 from
`~/research/qft-metaphysics/RELATIVITY-TEXTS-START.md`.)

## Standing rules (Hans)

1. **Hans commits and pushes. You never do.** Read-only git only, and always as
   `git --no-optional-locks status`: a plain `git status` from the sandbox leaves
   a `.git/index.lock` it cannot delete.
2. **No deletions.** Move unwanted files to `~/research/_to_delete/`.
3. **Ask before downloading anything** not listed in SCANS.tsv or the paper's
   RESUME-NOTES (the Wikisource draft of Ehrenfest is listed).
4. **Ask Hans before any job that has agents read every page image**: say which
   cheaper options you checked and give the token estimate.
5. Printed documents in 12 pt. Translations in American spelling.
6. **Tooling runs through `make` without Claude.** No step may depend on a
   Claude session to regenerate any output.
7. Translations carry the credit line "Translated from the German" and no
   translator's name (Hans, 2026-10-20, as in danish-texts).

## Which job is this?

| The user wants | Read first |
|---|---|
| A scan turned into `transcription.tex` | **TRANSCRIPTION-PLAYBOOK.md**, then danish-texts' §00 and §3 |
| A finished transcription turned into English | **TRANSLATION-PLAYBOOK.md** and **GLOSSARY.md** |
| To continue a paper already under way | `texts/<topic>/<paper>/RESUME-NOTES.md` |
| The scan a paper was made from | `python3 scans.py path <topic>/<paper>`; SCANS.tsv |
| A lost scan regenerated | `fetch-scans.sh` (not run by default) |
| The catalog edited | `catalog.yaml`, then `python3 validate-catalog.py` |

The repo is organized by **topic**, not by author (Hans, 2026-10-20):
`texts/<topic>/<author>-<year>/`. The first topic is `extended-bodies`
("No-go theorems for extended bodies"). Papers, in order of work: `extended-bodies/ehrenfest-1909` (1 p.),
`extended-bodies/laue-1911` (3 pp.), `extended-bodies/herglotz-1910` (23 pp.),
`extended-bodies/noether-1910` (26 pp.), `extended-bodies/born-1909` (56 pp.).
One paper per session after the two pilots. Papers still in copyright (Møller 1949)
are listed in the catalog with `status: in-copyright` and a link to an online
copy, and are never transcribed or translated here.
The archive's tentative cutoff is 1970: papers published before then (Hans,
2026-10-22).

The second topic, `danish-debate` ("The Danish relativity debate, 1912–1917":
Hansen, Kroman, Holst, Walsøe), is **mirrored from ~/danish-texts**, where those
editions are made and corrected (`texts/kroman/`). `MIRROR.tsv` lists them and
`make mirror` (mirror.sh) copies the .tex and .pdf in; publish-relativity.sh runs
it. **Never edit `texts/danish-debate/` here**: fix the source in danish-texts and
re-mirror. To add a mirrored paper, add a row to MIRROR.tsv and a catalog entry.
Hansen's 1916 reply is published here although danish-texts holds it back until
2027-01-01 (Hans, 2026-10-21: US public domain, as for Laue and Born). Hansen
1912 is not yet transcribed (danish-texts has only a skeleton; no scan online). Second-phase papers are listed in
`catalog.yaml` with `phase: 2`; do not start one without Hans.

## The rules that save money

- **Never read a page image in the main conversation, and never let bulk OCR
  output land there.** Page reading goes to subagents, which return a short
  report and write their results to files. (danish-texts measured a hundredfold
  difference.)
- Estimate before dispatching, pilot one agent, run batches of ≤5, save after
  each batch. Agents stop after two failed device calls.
- No agent re-types text: a script or an existing transcription supplies the
  draft; agents report corrections as a list.

## Accuracy

Transcribing a paper means transcribing it *and* establishing that it is
accurate. Every page is read at the image by an agent that did not produce the
text, with two planted control errors per reader; the prose is diffed against
the scan's text layer (`python3 ocrdiff.py <topic>/<paper>`) and the result
recorded as an `OCRDIFF:` line; every formula is checked symbol by symbol at
the image (the layer cannot witness formulas). The `transcription.tex` header
states how accuracy was established. A clean compile is not evidence of accuracy.

## Repo facts

- **Scans** are in `~/bibliotek`, identified by sha256 in SCANS.tsv
  (`scans.py verify`). Journal p. = PDF p. + offset (SCANS.tsv note column).
  The IA layer is usable for prose (Antiqua) and garbage for formulas.
- **A paper directory tracks the edition only**: `transcription.tex/.pdf`,
  `translation.tex/.pdf`, `figures/`. RESUME-NOTES.md, BATCH-AGENT.md, scripts
  and `.parts/` are untracked (.gitignore). Never write scratch files in the
  repo; render to `mktemp -d`.
- **`make`** builds every `.tex` under `texts/`. Never leave a preamble-less
  fragment with a `.tex` extension there; use `.texfrag`.
- **`make` cannot run in the Cowork VM**: `libertinus` is not installed there.
  Compile-test with the substitution recipe in TRANSCRIPTION-PLAYBOOK.md §5;
  real builds happen on Hans's machine.
- **`publish: false`** in catalog.yaml must be mirrored in `PRIVATE` in the
  Makefile; a publish script uses `make public`. (All five first-phase papers
  are `publish: true`, Hans 2026-10-20.)
- **Web publication** (wired 2026-10-20): `catalog.yaml` is symlinked as
  `~/hhalvors.github.io/data/relativity-texts.yaml` and rendered at
  https://hanshalvorson.com/relativity/ by `RelativityTexts.hs` there. The PDFs
  are served by this repo's GitHub Pages (hhalvors.github.io/relativity-texts/,
  which redirects to hanshalvorson.com/relativity-texts/). Hans publishes with
  `~/hhalvors.github.io/publish-relativity.sh "message"` (make, make check,
  site build, commit and push both repos). When a paper is finished, set its
  `status: complete` in the catalog and give it Transcription/Translation links.

## Editorial stance

Diplomatic transcriptions: 1909–11 orthography and the printer's errors kept as
printed, each misprint marked `% sic:` at the site and listed in the header;
the translation notes it in a bracketed "[Tr.]" footnote. The German umlaut
rule of danish-texts applies: a word that has lost its umlaut in the scan and is
no German word (`hore`, `abhangig`) gets it back; that is not a correction.
