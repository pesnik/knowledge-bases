#!/usr/bin/env python3
"""
compile.py — raw/ → wiki/ via local LLM

Usage:
  python pipeline/compile.py --kb speculative-decoding
  python pipeline/compile.py --kb speculative-decoding --stage plan
  python pipeline/compile.py --kb speculative-decoding --concept eagle
"""
import argparse
import json
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    MODEL_PATH, TEMPERATURE,
    COMPILE_MAX_TOKENS, INDEX_MAX_TOKENS, PLAN_MAX_TOKENS,
    MAX_CHARS_COMPILE, MAX_CHARS_INDEX, MAX_CHARS_PLAN,
    KV_BITS, KV_GROUP_SIZE,
    get_paths,
)

# ── Model singleton ───────────────────────────────────────────────────
_model = _tokenizer = None

def get_model():
    global _model, _tokenizer
    if _model is None:
        print(f"[load] {MODEL_PATH} ...", flush=True)
        import mlx_lm
        _model, _tokenizer = mlx_lm.load(MODEL_PATH)
        print("[load] ready\n")
    return _model, _tokenizer


def call_llm(system: str, user: str, max_tokens: int, label: str = "") -> str:
    if label:
        print(f"  [llm] {label} ...", end=" ", flush=True)
    import mlx_lm
    from mlx_lm.sample_utils import make_sampler
    model, tokenizer = get_model()
    prompt = tokenizer.apply_chat_template(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        add_generation_prompt=True, tokenize=False,
    )
    out = mlx_lm.generate(
        model, tokenizer, prompt=prompt, max_tokens=max_tokens,
        sampler=make_sampler(temp=TEMPERATURE),
        kv_bits=KV_BITS, kv_group_size=KV_GROUP_SIZE, verbose=False,
    )
    out = out[len(prompt):].strip() if out.startswith(prompt) else out.strip()
    if label:
        print(f"~{len(out.split())} words", flush=True)
    return out


# ── Helpers ───────────────────────────────────────────────────────────

def load_raw(raw_dir: Path) -> dict[str, str]:
    files = {p.name: p.read_text() for p in sorted(raw_dir.glob("*.md"))}
    if not files:
        print(f"[warn] No .md files in {raw_dir}")
    return files


def corpus(files: dict[str, str], max_chars: int) -> str:
    parts = []
    for name, content in files.items():
        chunk = content[:max_chars]
        if len(content) > max_chars:
            chunk += "\n...[truncated]"
        parts.append(f"==[{name}]==\n{chunk}")
    return "\n\n".join(parts)


# ── Stage 1: Plan ─────────────────────────────────────────────────────

PLAN_SYS = """\
You are a knowledge-base compiler. Identify 6-8 distinct technical concepts from \
the source material that each deserve their own wiki article.

Output ONLY a valid JSON array. No markdown fences, no explanation, no extra text.
Each element must have exactly these three fields:
  "slug"    — kebab-case identifier, e.g. "event-loop"
  "title"   — human-readable title, e.g. "Event Loop"
  "summary" — one sentence description

Example output:
[{"slug": "event-loop", "title": "Event Loop", "summary": "The core async execution model."}, \
{"slug": "memory-layer", "title": "Memory Layer", "summary": "Persistent context store."}]"""


def _normalize_concept(c: dict) -> dict | None:
    """Normalize variant formats the model may emit into {slug, title, summary}."""
    # Already correct
    if "slug" in c:
        return c
    # "name" + optional "arguments" sub-dict (function-call style)
    name = c.get("name") or c.get("title") or c.get("concept") or c.get("id") or ""
    if not name:
        return None
    args = c.get("arguments", {}) if isinstance(c.get("arguments"), dict) else {}
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    title = args.get("title") or name.replace("-", " ").title()
    summary = args.get("summary") or args.get("description") or c.get("summary") or c.get("description") or ""
    return {"slug": slug, "title": title, "summary": summary}


def stage_plan(raw_files: dict, kb: str) -> list[dict]:
    raw = call_llm(PLAN_SYS, f"Source:\n\n{corpus(raw_files, MAX_CHARS_PLAN)}",
                   PLAN_MAX_TOKENS, "planning concepts")
    chunk = raw.strip()
    # Strip markdown fences if present
    chunk = re.sub(r'^```[a-z]*\n?', '', chunk).rstrip('`').strip()
    start = chunk.find("[")
    if start == -1:
        print(f"\n[error] No JSON array.\nRaw:\n{raw[:300]}")
        sys.exit(1)
    chunk = chunk[start:]
    # Try to find the closing bracket (truncate at last valid ']')
    end = chunk.rfind("]")
    if end != -1:
        chunk = chunk[:end + 1]
    try:
        raw_concepts = json.loads(chunk)
    except json.JSONDecodeError:
        raw_concepts = [json.loads(m.group()) for m in re.finditer(r'\{[^{}]+\}', chunk, re.DOTALL)
                        if any(k in m.group() for k in ("slug", "name", "title", "concept"))]
        if not raw_concepts:
            print(f"\n[error] Could not parse concepts.\nRaw:\n{chunk[:300]}")
            sys.exit(1)
    concepts = [n for c in raw_concepts if (n := _normalize_concept(c)) is not None]
    if not concepts:
        print(f"\n[error] Normalization yielded no concepts.\nRaw:\n{chunk[:300]}")
        sys.exit(1)
    print(f"\n  [plan] {len(concepts)} concepts for [{kb}]:")
    for c in concepts:
        print(f"    - {c['slug']}")
    return concepts


# ── Stage 2: Compile ──────────────────────────────────────────────────

COMPILE_SYS = """\
You are a technical wiki author. Write a precise wiki article for the given concept.

Format (markdown only, no preamble):
# {Title}

## Definition
[2-4 sentence definition]

## Mechanism
[How it works — math/pseudocode if helpful]

## Tradeoffs
[Table or bullets: gains, costs, failure modes]

## See Also
- [[related-slug]]

Assume ML engineer audience. Use numbers not vague claims. Use [[wikilinks]] for cross-refs."""


def stage_compile(concepts: list[dict], raw_files: dict, paths: dict,
                  only: str | None = None) -> list[dict]:
    paths["concepts"].mkdir(parents=True, exist_ok=True)
    src = corpus(raw_files, MAX_CHARS_COMPILE)
    compiled = []
    for c in concepts:
        if only and c["slug"] != only:
            continue
        article = call_llm(
            COMPILE_SYS,
            f"Concept: {c['title']}\nSlug: {c['slug']}\nSummary: {c.get('summary','')}\n\nSource:\n\n{src}",
            COMPILE_MAX_TOKENS, f"[[{c['slug']}]]",
        )
        out = paths["concepts"] / f"{c['slug']}.md"
        out.write_text(article)
        print(f"  [write] {out.relative_to(paths['vault'])}")
        compiled.append(c)
    return compiled


# ── Stage 3: Index ────────────────────────────────────────────────────

INDEX_SYS = """\
Write a wiki/index.md catalog for a knowledge base.

Format:
# {Topic} — Index

> [one-line description]. LLM-maintained.

## [Category]
- [[slug]] — one sentence

## Open Questions
- [3-5 gaps not yet covered]

Output ONLY the markdown."""


def stage_index(concepts: list[dict], paths: dict, kb: str):
    paths["wiki"].mkdir(parents=True, exist_ok=True)
    articles = "\n".join(
        f"- slug={c['slug']}, title={c['title']}, summary={c.get('summary','')}"
        for c in concepts
    )
    content = call_llm(INDEX_SYS, f"Topic: {kb}\nArticles:\n{articles}",
                       INDEX_MAX_TOKENS, "index.md")
    paths["index"].write_text(content)
    print(f"  [write] {paths['index'].relative_to(paths['vault'])}")


# ── Stage 4: Log ──────────────────────────────────────────────────────

def stage_log(raw_files: dict, concepts: list[dict], paths: dict, kb: str):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = textwrap.dedent(f"""
    ## {date} — Compile

    **Ingested:**
    {chr(10).join(f"  - {n}" for n in raw_files)}

    **Compiled:**
    {chr(10).join(f"  - [[{c['slug']}]] — {c['title']}" for c in concepts)}

    ---
    """).lstrip()
    log = paths["log"]
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(entry + log.read_text() if log.exists()
                   else f"# {kb} Wiki — Log\n\n{entry}")
    print(f"  [write] {log.relative_to(paths['vault'])}")


# ── Main ──────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kb",      required=True, help="KB name, e.g. speculative-decoding")
    p.add_argument("--stage",   choices=["plan", "compile", "index", "all"], default="all")
    p.add_argument("--concept", help="Compile one concept slug only")
    args = p.parse_args()

    paths = get_paths(args.kb)
    if not paths["vault"].exists():
        print(f"[error] KB not found: {paths['vault']}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  KB      : {args.kb}")
    print(f"  Model   : {MODEL_PATH}")
    print(f"{'='*60}\n")

    raw_files = load_raw(paths["raw"])
    print(f"[raw] {len(raw_files)} files: {list(raw_files)}\n")

    if args.concept:
        c = {"slug": args.concept, "title": args.concept.replace("-", " ").title(), "summary": ""}
        stage_compile([c], raw_files, paths, only=args.concept)
        return

    if args.stage in ("plan", "all"):
        print("[stage 1/4] Plan")
        concepts = stage_plan(raw_files, args.kb)
        print()
    else:
        concepts = [{"slug": p.stem, "title": p.stem.replace("-", " ").title(), "summary": ""}
                    for p in sorted(paths["concepts"].glob("*.md"))]

    if args.stage in ("compile", "all"):
        print("[stage 2/4] Compile")
        stage_compile(concepts, raw_files, paths)
        print()

    if args.stage in ("index", "all"):
        print("[stage 3/4] Index")
        stage_index(concepts, paths, args.kb)
        print()

    if args.stage == "all":
        print("[stage 4/4] Log")
        stage_log(raw_files, concepts, paths, args.kb)
        print()

    print(f"Done. Open {args.kb}/wiki/index.md in Obsidian.")


if __name__ == "__main__":
    main()
