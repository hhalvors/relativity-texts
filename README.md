# Relativity Texts

Transcriptions and English translations of early papers on the theory of
relativity, arranged by topic. The first topic, **no-go theorems for extended
bodies** (`texts/extended-bodies/`), is the debate of 1909–1911 over rigid
bodies in special relativity:

| Paper | Source |
|---|---|
| M. Born, „Die Theorie des starren Elektrons in der Kinematik des Relativitätsprinzips“ | *Ann. Phys.* 335 (1909): 1–56 |
| P. Ehrenfest, „Gleichförmige Rotation starrer Körper und Relativitätstheorie“ | *Phys. Z.* 10 (1909): 918 |
| G. Herglotz, „Über den vom Standpunkt des Relativitätsprinzips aus als ‚starr‘ zu bezeichnenden Körper“ | *Ann. Phys.* 336 (1910): 393–415 |
| F. Noether, „Zur Kinematik des starren Körpers in der Relativtheorie“ | *Ann. Phys.* 336 (1910): 919–944 |
| M. Laue, „Zur Diskussion über den starren Körper in der Relativitätstheorie“ | *Phys. Z.* 12 (1911): 85–87 |

Each transcription follows the printed text, with the journal's page numbers in
the margin, the printed equation numbers, and the printer's errors kept and
marked. The translations mirror the transcriptions page for page.

The second topic, **the Danish relativity debate, 1912–1917**
(`texts/danish-debate/`): H. M. Hansen's 1912 lecture, Kristian Kroman's attack of
1915, the replies of Helge Holst, C. E. Walsøe and Hansen, and Kroman's last word
(1917), all from *Fysisk Tidsskrift*. These editions are made in the
[danish-texts](https://github.com/hhalvors/danish-texts) repository and mirrored
here by `make mirror` (`MIRROR.tsv`); edit them there, not here.

## Structure

```
texts/<topic>/<paper>/
    transcription.tex / .pdf   the German, as printed
    translation.tex / .pdf     the English
    figures/                   redrawn or cropped figures, where a paper has them
catalog.yaml                   topics, each with its papers (status, citation, links, publish flag)
SCANS.tsv, scans.py            which scan each transcription was made from, by sha256
fetch-scans.sh                 how each scan was cut from the Internet Archive's issue scans
ocrdiff.py                     compares a transcription's words with the scan's text layer
MIRROR.tsv, mirror.sh          the papers mirrored from ~/danish-texts (`make mirror`)
templates/article.tex          the preamble every paper starts from
```

## Building

Requires TeX Live with `libertinus`, `libertinust1math` and `latexmk`.

```sh
make            # build every out-of-date PDF
make list       # which PDFs are missing or stale
make check      # validate catalog.yaml, verify the scans' hashes
make help
```

Each `.tex` is self-contained and also builds with `latexmk -pdf` in its own
directory.

## Sources and license

The scans are from the Internet Archive's copies of *Physikalische Zeitschrift*
and *Annalen der Physik*; they are not distributed here. The draft of
Ehrenfest's note was taken from German Wikisource (CC BY-SA) and checked
against the scan. The original papers are in the public domain in the United
States.

## License

Translations © Hans Halvorson. The transcriptions are reproductions of
public-domain texts. Feel free to use the translations with attribution.
The transcription of Ehrenfest's note derives from German Wikisource and is
therefore under CC BY-SA 4.0, with attribution to Wikisource's contributors.
