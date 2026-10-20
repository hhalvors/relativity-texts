# Translation playbook (relativity-texts)

The method is danish-texts' (`~/danish-texts/TRANSLATION-PLAYBOOK.md` §§0–4);
this file records the German→English conventions.

1. **Translate from `transcription.tex`, never from the scan.** A translation
   made before its transcription was checked must be re-checked at every
   reading that changed since (danish-texts §6a).
2. **Mirror the transcription 1:1**: the same `\opage` markers (placed at the
   corresponding word), the same `\tag` numbers, the same footnote numbers
   (`\footnote[n]{}`). Formulas are copied unchanged from the transcription,
   including any misprint, which gets a "[Tr.]" note.
3. **American spelling**; curly quotes written ``` ``…'' ```; the author's
   emphasis kept as `\emph{}`.
4. **Translator's notes** are factual only: a misprint, a reference resolved,
   a term explained. No commentary. They are set with `\trnote{…}`
   (defined in `templates/article.tex`), which makes a footnote marked with a
   letter (a, b, c …) and beginning "[Tr.]", so that the printed notes keep
   their printed numbers.
5. **Glossary first.** `GLOSSARY.md` fixes the terms; Hans approves it before
   Herglotz is translated. A term not in it is added, with its first page, when
   first met, and flagged to Hans.
6. **Titles** of works cited stay as the author cites them; journal and volume
   references verbatim ("Ann. d. Phys. 30, 1, 1909").
7. **Register**: scholarly, moderately literal, readable. Keep the author's
   long sentences where English allows; do not modernize the physics
   (no "Born-rigid" where the text says "relativ-starr": that is "relatively
   rigid").
8. Credit line under the title: "Translated from the German", no name.
9. **Translating is a second reading of the transcription**: keep a list of odd
   spots (a word that makes no sense, a formula that does not follow) and have
   the doubtful ones read at the image before the translation is called done.

Compile test: TRANSCRIPTION-PLAYBOOK.md §5, on translation.tex.
