#!/usr/bin/env python3
"""
fix.py — post-process LLM output

Usage:
  python pipeline/fix.py --kb speculative-decoding
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import get_paths

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def fix_broken_links(content: str, known: set[str]) -> tuple[str, int]:
    fixed = 0
    def replace(m):
        nonlocal fixed
        link = m.group(1)
        if link in known:
            return m.group(0)
        normalized = link.lower().replace(" ", "-")
        if normalized in known:
            return f"[[{normalized}]]"
        fixed += 1
        return link
    return WIKILINK_RE.sub(replace, content), fixed


def fix_orphan(slug: str, content: str, all_slugs: list[str]) -> tuple[str, bool]:
    siblings = [s for s in all_slugs if s != slug][:4]
    links = "\n".join(f"- [[{s}]]" for s in siblings)
    if "## See Also" in content:
        existing = [l for l in WIKILINK_RE.findall(content.split("## See Also")[-1])
                    if l in set(all_slugs)]
        if existing:
            return content, False
        parts = content.split("## See Also")
        return parts[0].rstrip() + f"\n\n## See Also\n{links}\n", True
    return content.rstrip() + f"\n\n## See Also\n{links}\n", True


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--kb", required=True)
    args = p.parse_args()

    paths = get_paths(args.kb)
    wiki = {p.stem: p.read_text() for p in sorted(paths["concepts"].glob("*.md"))}
    known = set(wiki)
    all_slugs = sorted(wiki)

    print(f"[fix] {args.kb} — {len(wiki)} articles\n")
    link_fixes = orphan_fixes = 0

    for slug, content in wiki.items():
        new = content
        new, n = fix_broken_links(new, known)
        if n:
            link_fixes += n
            print(f"  [links] {slug}.md — removed {n} broken link(s)")
        new, injected = fix_orphan(slug, new, all_slugs)
        if injected:
            orphan_fixes += 1
            print(f"  [see-also] {slug}.md — injected")
        if new != content:
            (paths["concepts"] / f"{slug}.md").write_text(new)

    print(f"\nDone: {link_fixes} broken links removed, {orphan_fixes} See Also sections fixed.")


if __name__ == "__main__":
    main()
