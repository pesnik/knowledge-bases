##############################################################
# Knowledge Bases — Pipeline
# Usage: make <target> kb=<topic>
# Example: make all kb=speculative-decoding
##############################################################
PYTHON   = python3
PIPELINE = pipeline

ifndef kb
  $(error kb is required. Usage: make <target> kb=<topic-name>)
endif

.PHONY: compile fix validate all push

compile:
	$(PYTHON) $(PIPELINE)/compile.py --kb $(kb)

fix:
	$(PYTHON) $(PIPELINE)/fix.py --kb $(kb)

validate:
	$(PYTHON) $(PIPELINE)/validate.py --kb $(kb)

## compile + fix + validate in one shot
all: compile fix validate

## compile a single concept (usage: make concept kb=speculative-decoding slug=eagle)
concept:
	$(PYTHON) $(PIPELINE)/compile.py --kb $(kb) --concept $(slug)

## just show the concept plan, no writes
plan:
	$(PYTHON) $(PIPELINE)/compile.py --kb $(kb) --stage plan

## rebuild index.md only
index:
	$(PYTHON) $(PIPELINE)/compile.py --kb $(kb) --stage index

push:
	git add -A && git commit -m "wiki: $(kb) $$(date +%Y-%m-%d)" && git push
