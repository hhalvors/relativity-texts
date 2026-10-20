#!/bin/bash
# Run this ONCE from ~/relativity-texts/ to make the git repo and connect it to GitHub.
# Modeled on ~/danish-texts/setup.sh.
#
# Before running:
#   1. Create an empty repo at https://github.com/new
#        Name: relativity-texts     Visibility: Public
#        Do NOT add a README, .gitignore or license (they are here already).
#      (Or, with the GitHub CLI:  gh repo create hhalvors/relativity-texts --public)
#   2. Run:  bash setup.sh
#
# Authentication is HTTPS, as for danish-texts: when asked for a password, give a
# GitHub personal access token (Settings -> Developer settings -> Personal access
# tokens), not your account password. If danish-texts pushes without asking, the
# macOS keychain already holds the token and this will too.

set -e
cd "$(dirname "$0")"

if [ -d .git ]; then
  echo "This is already a git repository; nothing to do."; exit 1
fi

echo "== Building the PDFs (they are committed and served by GitHub Pages)"
make
make check

git init -b main
git add .
echo
echo "== Files to be committed (RESUME-NOTES, .parts/ and build files are ignored):"
git status --short
echo
read -p "Commit these and push to github.com/hhalvors/relativity-texts? [y/N] " ok
[ "$ok" = "y" ] || { echo "Stopped. Nothing committed; 'rm -rf .git' to start over."; exit 1; }

git commit -m "Initial commit: setup; Ehrenfest 1909 and Laue 1911 transcribed and translated"
git remote add origin https://github.com/hhalvors/relativity-texts.git
git push -u origin main

echo ""
echo "Done. Now enable GitHub Pages in the repo settings:"
echo "  Settings -> Pages -> Source: Deploy from branch -> main / (root)"
echo "  The PDFs will appear under https://hhalvors.github.io/relativity-texts/texts/<topic>/<paper>/"
