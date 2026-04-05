#!/usr/bin/env python3
"""
validate.py — lint a KB wiki

Usage:
  python pipeline/validate.py --kb speculative-decoding
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import get_paths

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--kb", required=True)
    args = p.parse_args()

    paths = get_paths(args.kb)

    print(f"\n{'='*60}")
    print(f"  validate — {args.kb}")
    print(f"{'='*60}\n")

    if not paths["concepts"].exists() or not list(paths["concepts"].glob("*.md")):
        print("[error] No compiled articles. Run compile.py first.")
        sys.exit(1)

    wiki = {p.stem: p.read_text() for p in sorted(paths["concepts"].glob("*.md"))}
    print(f"[load] {len(wiki)} articles\n")

    errors, warnings = [], []

    # 1. Broken wikilinks
    print("[1/6] Broken wikilinks")
    r = [f"  BROKEN  [[{l}]]  in  {s}.md"
         for s, c in wiki.items()
         for l in set(WIKILINK_RE.findall(c)) if l not in wiki]
    errors += r; print(f"  {'OK' if not r else f'{len(r)} issues'}")

    # 2. Orphan pages
    print("[2/6] Orphan pages")
    inbound = defaultdict(set)
    for src, content in {**wiki, **({"index": paths["index"].read_text()} if paths["index"].exists() else {})}.items():
        for l in WIKILINK_RE.findall(content):
            inbound[l].add(src)
    r = [f"  ORPHAN  {s}.md" for s in wiki if s not in inbound]
    warnings += r; print(f"  {'OK' if not r else f'{len(r)} warnings'}")

    # 3. Required sections
    print("[3/6] Required sections")
    r = [f"  MISSING  '{sec}'  in  {s}.md"
         for s, c in wiki.items() for sec in ("## Definition", "## See Also") if sec not in c]
    errors += r; print(f"  {'OK' if not r else f'{len(r)} issues'}")

    # 4. Article length
    print("[4/6] Article length")
    r = [f"  SHORT  {s}.md  ({len(c.split())} words)"
         for s, c in wiki.items() if len(c.split()) < 150]
    warnings += r; print(f"  {'OK' if not r else f'{len(r)} warnings'}")

    # 5. Meta files
    print("[5/6] Meta files")
    r = [f"  MISSING  {n}" for f, n in [(paths["index"], "wiki/index.md"), (paths["log"], "wiki/log.md")]
         if not f.exists() or f.stat().st_size < 50]
    errors += r; print(f"  {'OK' if not r else f'{len(r)} issues'}")

    # 6. Raw coverage
    print("[6/6] Raw coverage")
    all_text = "\n".join(wiki.values()) + (paths["index"].read_text() if paths["index"].exists() else "")
    r = [f"  UNCOVERED  raw/{f.name}" for f in sorted(paths["raw"].glob("*.md"))
         if f.stem not in all_text and f.name not in all_text]
    warnings += r; print(f"  {'OK' if not r else f'{len(r)} warnings'}")

    print()
    if errors:
        print(f"ERRORS ({len(errors)}):\n" + "\n".join(errors))
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):\n" + "\n".join(warnings))
    if not errors and not warnings:
        print("All checks passed.")
    print(f"\nSummary: {len(wiki)} articles | {len(errors)} errors | {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
