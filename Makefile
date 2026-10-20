# ============================================================
#  Makefile — relativity-texts
#
#  Builds a PDF from every .tex source under texts/.
#  Adapted from ~/danish-texts/Makefile (2026-10-20).
#
#  Usage:
#    make              rebuild all out-of-date PDFs
#    make clean        remove LaTeX auxiliary files (keep PDFs)
#    make cleanall     remove auxiliary files and compiled PDFs
#    make list         list every .tex source and its PDF status
#    make public       list the PDFs that may be published (see PRIVATE below)
#    make check        validate catalog.yaml and verify every scan's sha256
#    make help         show this message
#    make -j4          parallel build with 4 jobs
# ============================================================

# All .tex sources, except staged fragments in .parts/ (a fragment has no
# preamble; fragments also carry the extension .texfrag, belt and braces) and
# templates/ (a template is not a document).
TEXFILES := $(shell find texts -name '*.tex' -not -path '*/.parts/*' | sort)
PDFFILES := $(TEXFILES:.tex=.pdf)

# Works marked `publish: false` in catalog.yaml. Their PDFs are built but are
# not PUBLIC, and a publish script must use $(PUBLIC), never $(PDFFILES).
# Keep this list and the catalog in step (validate-catalog.py checks it).
# Empty since 2026-10-20: Hans decided to publish all five papers.
PRIVATE :=
PUBLIC  := $(filter-out $(addsuffix /%,$(addprefix texts/,$(PRIVATE))),$(PDFFILES))

LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all clean cleanall list public check help

all: $(PDFFILES)

# cd into the source directory so relative paths (figures/) resolve.
%.pdf: %.tex
	cd $(dir $<) && $(LATEXMK) $(notdir $<)

clean:
	@find texts \( -name '*.aux' -o -name '*.fdb_latexmk' -o -name '*.fls' \
	  -o -name '*.log' -o -name '*.out' -o -name '*.synctex.gz' -o -name '*.toc' \
	  -o -name '*.xdv' \) -delete
	@echo "Auxiliary files removed."

cleanall: clean
	@rm -f $(PDFFILES)
	@echo "Auxiliary files and compiled PDFs removed."

list:
	@for tex in $(TEXFILES); do pdf=$${tex%.tex}.pdf; \
	  if [ ! -f "$$pdf" ]; then echo "  MISSING  $$tex"; \
	  elif [ "$$tex" -nt "$$pdf" ]; then echo "  STALE    $$tex"; \
	  else echo "  ok       $$tex"; fi; done

public:
	@for p in $(PUBLIC); do echo $$p; done

check:
	python3 validate-catalog.py
	python3 scans.py verify

help:
	@sed -n '2,16p' Makefile
