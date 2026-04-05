#!/usr/bin/env python3
"""
fix.py — post-process LLM output to repair common issues

Fixes:
  1. Broken wikilinks → plain text (LLM used prose titles not slugs)
  2. Orphan pages → inject See Also links to sibling concepts
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import CONCEPTS_DIR, VAULT_ROOT

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def load_wiki() -> dict[str, str]:
    return {p.stem: p.read_text() for p in sorted(CONCEPTS_DIR.glob("*.md"))}


def fix_broken_links(slug: str, content: str, known_slugs: set[str]) -> tuple[str, int]:
    """Replace [[Unknown Title]] with plain text if slug not in known set."""
    fixed = 0
    def replace(m):
        nonlocal fixed
        link = m.group(1)
        if link in known_slugs:
            return m.group(0)  # keep
        # Try normalizing: lower + hyphens
        normalized = link.lower().replace(" ", "-")
        if normalized in known_slugs:
            return f"[[{normalized}]]"
        # Not found — strip to plain text
        fixed += 1
        return link
    return WIKILINK_RE.sub(replace, content), fixed


def fix_orphan(slug: str, content: str, all_slugs: list[str]) -> tuple[str, bool]:
    """Ensure the article has a See Also section with links to sibling articles."""
    siblings = [s for s in all_slugs if s != slug][:4]  # up to 4 links
    see_also_links = "\n".join(f"- [[{s}]]" for s in siblings)

    if "## See Also" in content:
        # Replace empty or broken See Also
        existing_links = WIKILINK_RE.findall(content.split("## See Also")[-1])
        valid = [l for l in existing_links if l in set(all_slugs)]
        if valid:
            return content, False  # already has valid links

        # Replace the See Also block
        parts = content.split("## See Also")
        new_content = parts[0].rstrip() + f"\n\n## See Also\n{see_also_links}\n"
        return new_content, True
    else:
        # Append See Also at end
        return content.rstrip() + f"\n\n## See Also\n{see_also_links}\n", True


def main():
    wiki = load_wiki()
    known = set(wiki.keys())
    all_slugs = sorted(wiki.keys())

    print(f"[fix] {len(wiki)} articles in {CONCEPTS_DIR.relative_to(VAULT_ROOT)}\n")

    total_link_fixes = 0
    total_orphan_fixes = 0

    for slug, content in wiki.items():
        new_content = content

        # Fix 1: broken wikilinks
        new_content, n_fixed = fix_broken_links(slug, new_content, known)
        if n_fixed:
            total_link_fixes += n_fixed
            print(f"  [links] {slug}.md — removed {n_fixed} broken link(s)")

        # Fix 2: orphan — no valid inbound links doesn't help here, but ensure outbound
        new_content, injected = fix_orphan(slug, new_content, all_slugs)
        if injected:
            total_orphan_fixes += 1
            print(f"  [links] {slug}.md — injected See Also section")

        if new_content != content:
            (CONCEPTS_DIR / f"{slug}.md").write_text(new_content)

    print(f"\nDone: {total_link_fixes} broken links removed, {total_orphan_fixes} See Also sections fixed.")


if __name__ == "__main__":
    main()
