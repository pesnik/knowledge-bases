##############################################################
# Speculative Decoding KB — Pipeline Commands
# Requires: source ~/Tools/mlx/.venv/bin/activate
##############################################################
PYTHON = python3
PIPELINE = pipeline

.PHONY: compile plan validate open push help

## Run full pipeline: raw/ → wiki/
compile:
	$(PYTHON) $(PIPELINE)/compile.py

## Only show the concept plan (no writes)
plan:
	$(PYTHON) $(PIPELINE)/compile.py --stage plan

## Compile a single concept (usage: make concept SLUG=draft-verify-mechanism)
concept:
	$(PYTHON) $(PIPELINE)/compile.py --concept $(SLUG)

## Lint the wiki for broken links, orphans, missing sections
validate:
	$(PYTHON) $(PIPELINE)/validate.py

## Rebuild index.md only (after manual edits)
index:
	$(PYTHON) $(PIPELINE)/compile.py --stage index

## Fix broken links and orphans (post-process LLM output)
fix:
	$(PYTHON) $(PIPELINE)/fix.py

## Full pipeline + fix + validate
all: compile fix validate

## Git push to origin/master
push:
	git add -A && git commit -m "wiki: $$(date +%Y-%m-%d) compile" && git push

help:
	@grep -E '^##' Makefile | sed 's/## //'
