#!/usr/bin/env python3
"""
validate.py — lint the wiki for quality issues

Checks:
  1. Broken wikilinks       — [[slug]] with no matching file
  2. Orphan pages           — articles with no inbound wikilinks
  3. Missing sections       — articles missing ## Definition or ## See Also
  4. Short articles         — under 150 words (likely incomplete)
  5. index.md / log.md      — exist and are non-empty
  6. Raw files uncompiled   — raw/ files not mentioned anywhere in wiki

Usage:
  python pipeline/validate.py
  python pipeline/validate.py --fix      # auto-fix what's fixable (orphan links in index)
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from config import CONCEPTS_DIR, INDEX_FILE, LOG_FILE, RAW_DIR, VAULT_ROOT

# ─────────────────────────────────────────────────────────────────────
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def load_wiki() -> dict[str, str]:
    """Returns {slug: content} for all concept files."""
    return {p.stem: p.read_text() for p in sorted(CONCEPTS_DIR.glob("*.md"))}


def extract_links(content: str) -> set[str]:
    return set(WIKILINK_RE.findall(content))


# ─────────────────────────────────────────────────────────────────────

def check_broken_links(wiki: dict[str, str]) -> list[str]:
    errors = []
    for slug, content in wiki.items():
        for link in extract_links(content):
            if link not in wiki:
                errors.append(f"  BROKEN LINK  [[{link}]]  in  {slug}.md")
    return errors


def check_orphans(wiki: dict[str, str]) -> list[str]:
    inbound = defaultdict(set)
    # Also check index.md for links
    extra_sources = {}
    if INDEX_FILE.exists():
        extra_sources["index"] = INDEX_FILE.read_text()

    for src, content in {**wiki, **extra_sources}.items():
        for link in extract_links(content):
            inbound[link].add(src)

    orphans = []
    for slug in wiki:
        if slug not in inbound:
            orphans.append(f"  ORPHAN       {slug}.md  (no inbound wikilinks)")
    return orphans


def check_sections(wiki: dict[str, str]) -> list[str]:
    errors = []
    required = ["## Definition", "## See Also"]
    for slug, content in wiki.items():
        for section in required:
            if section not in content:
                errors.append(f"  MISSING      '{section}'  in  {slug}.md")
    return errors


def check_length(wiki: dict[str, str]) -> list[str]:
    warnings = []
    for slug, content in wiki.items():
        words = len(content.split())
        if words < 150:
            warnings.append(f"  SHORT        {slug}.md  ({words} words — expected ≥ 150)")
    return warnings


def check_meta_files() -> list[str]:
    errors = []
    for f, name in [(INDEX_FILE, "wiki/index.md"), (LOG_FILE, "wiki/log.md")]:
        if not f.exists():
            errors.append(f"  MISSING FILE {name}")
        elif f.stat().st_size < 50:
            errors.append(f"  EMPTY FILE   {name}")
    return errors


def check_raw_coverage(wiki: dict[str, str]) -> list[str]:
    all_wiki_text = "\n".join(wiki.values())
    if INDEX_FILE.exists():
        all_wiki_text += INDEX_FILE.read_text()
    warnings = []
    for raw_file in sorted(RAW_DIR.glob("*.md")):
        if raw_file.stem not in all_wiki_text and raw_file.name not in all_wiki_text:
            warnings.append(f"  UNCOVERED    raw/{raw_file.name}  (not cited in wiki)")
    return warnings


# ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  Speculative Decoding KB — validate.py")
    print(f"  Vault : {VAULT_ROOT}")
    print(f"{'='*60}\n")

    if not CONCEPTS_DIR.exists() or not list(CONCEPTS_DIR.glob("*.md")):
        print("[error] No compiled articles found. Run compile.py first.\n")
        sys.exit(1)

    wiki = load_wiki()
    print(f"[load] {len(wiki)} concept articles\n")

    all_issues = []
    all_warnings = []

    print("[check 1/6] Broken wikilinks")
    r = check_broken_links(wiki)
    all_issues += r
    print(f"  {'OK' if not r else f'{len(r)} issues'}")

    print("[check 2/6] Orphan pages")
    r = check_orphans(wiki)
    all_warnings += r
    print(f"  {'OK' if not r else f'{len(r)} warnings'}")

    print("[check 3/6] Required sections")
    r = check_sections(wiki)
    all_issues += r
    print(f"  {'OK' if not r else f'{len(r)} issues'}")

    print("[check 4/6] Article length")
    r = check_length(wiki)
    all_warnings += r
    print(f"  {'OK' if not r else f'{len(r)} warnings'}")

    print("[check 5/6] Meta files (index.md, log.md)")
    r = check_meta_files()
    all_issues += r
    print(f"  {'OK' if not r else f'{len(r)} issues'}")

    print("[check 6/6] Raw coverage")
    r = check_raw_coverage(wiki)
    all_warnings += r
    print(f"  {'OK' if not r else f'{len(r)} warnings'}")

    print()
    if all_issues:
        print(f"ERRORS ({len(all_issues)}):")
        print("\n".join(all_issues))
    if all_warnings:
        print(f"\nWARNINGS ({len(all_warnings)}):")
        print("\n".join(all_warnings))
    if not all_issues and not all_warnings:
        print("All checks passed.")

    print()
    # Summary
    print(f"Summary: {len(wiki)} articles | {len(all_issues)} errors | {len(all_warnings)} warnings")
    sys.exit(1 if all_issues else 0)


if __name__ == "__main__":
    main()
