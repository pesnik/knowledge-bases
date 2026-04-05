#!/usr/bin/env python3
"""
compile.py — raw/ → wiki/ pipeline using mlx_lm directly (no server)

Loads LFM2 once, then runs: plan → compile → index → log

Usage:
  python pipeline/compile.py                          # full compile
  python pipeline/compile.py --stage plan             # just print concept plan
  python pipeline/compile.py --concept eagle          # compile one concept only
"""
import argparse
import json
import sys
import textwrap
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    COMPILE_MAX_TOKENS, CONCEPTS_DIR, INDEX_FILE, INDEX_MAX_TOKENS,
    LOG_FILE, PLAN_MAX_TOKENS, RAW_DIR, TEMPERATURE, VAULT_ROOT,
    MODEL_PATH, MAX_CHARS_PLAN, MAX_CHARS_COMPILE, MAX_CHARS_INDEX,
    KV_BITS, KV_GROUP_SIZE,
)


# ─────────────────────────────────────────────────────────────────────
# Model loader — lazy singleton
# ─────────────────────────────────────────────────────────────────────

_model = None
_tokenizer = None


def get_model():
    global _model, _tokenizer
    if _model is None:
        print(f"[load model] {MODEL_PATH} ...", flush=True)
        import mlx_lm
        _model, _tokenizer = mlx_lm.load(MODEL_PATH)
        print("[load model] ready\n")
    return _model, _tokenizer


def call_llm(system: str, user: str, max_tokens: int, label: str = "") -> str:
    if label:
        print(f"  [llm] {label} ...", end=" ", flush=True)

    import mlx_lm
    model, tokenizer = get_model()

    # Build chat prompt via tokenizer's chat template
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]
    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False,
    )

    from mlx_lm.sample_utils import make_sampler
    response = mlx_lm.generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        sampler=make_sampler(temp=TEMPERATURE),
        kv_bits=KV_BITS,
        kv_group_size=KV_GROUP_SIZE,
        verbose=False,
    )

    # mlx_lm.generate returns the full string (prompt + response) in some versions
    # Strip the prompt prefix if present
    if response.startswith(prompt):
        response = response[len(prompt):]

    if label:
        token_count = len(response.split())
        print(f"~{token_count} words", flush=True)

    return response.strip()


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def load_raw_files() -> dict[str, str]:
    files = {}
    for p in sorted(RAW_DIR.glob("*.md")):
        files[p.name] = p.read_text()
    if not files:
        print("[warn] No .md files found in", RAW_DIR)
    return files


def raw_corpus(files: dict[str, str], max_chars_per_file: int = 800) -> str:
    parts = []
    for name, content in files.items():
        truncated = content[:max_chars_per_file]
        if len(content) > max_chars_per_file:
            truncated += "\n...[truncated]"
        parts.append(f"==[{name}]==\n{truncated}")
    return "\n\n".join(parts)


# ─────────────────────────────────────────────────────────────────────
# Stage 1: Plan
# ─────────────────────────────────────────────────────────────────────

PLAN_SYSTEM = """\
You are a knowledge-base compiler. Identify 6-8 distinct technical concepts from the source material that each deserve their own wiki article.

Output ONLY a JSON array, no markdown fences, no explanation:
[
  {"slug": "kebab-case-name", "title": "Human Title", "summary": "one sentence"},
  ...
]"""


def stage_plan(raw_files: dict[str, str]) -> list[dict]:
    corpus = raw_corpus(raw_files, max_chars_per_file=MAX_CHARS_PLAN)
    raw_output = call_llm(
        system=PLAN_SYSTEM,
        user=f"Source material:\n\n{corpus}",
        max_tokens=PLAN_MAX_TOKENS,
        label="extracting concept list",
    )

    content = raw_output.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    start = content.find("[")
    if start == -1:
        print(f"\n[error] No JSON array found.\nRaw:\n{raw_output[:400]}")
        sys.exit(1)

    # Handle truncated JSON: walk backwards to find last complete object
    chunk = content[start:]
    try:
        concepts = json.loads(chunk)
    except json.JSONDecodeError:
        # Truncated — extract complete objects manually
        concepts = []
        for m in __import__("re").finditer(r'\{[^{}]+\}', chunk, __import__("re").DOTALL):
            try:
                obj = json.loads(m.group())
                if "slug" in obj:
                    concepts.append(obj)
            except json.JSONDecodeError:
                continue
        if not concepts:
            print(f"\n[error] Could not parse any concepts.\nRaw:\n{chunk[:400]}")
            sys.exit(1)

    print(f"\n  [plan] {len(concepts)} concepts:")
    for c in concepts:
        print(f"    - {c['slug']}: {c.get('title','')}")
    return concepts


# ─────────────────────────────────────────────────────────────────────
# Stage 2: Compile
# ─────────────────────────────────────────────────────────────────────

COMPILE_SYSTEM = """\
You are a technical wiki author. Write a precise, dense wiki article for the given concept.

Format (markdown only, no preamble):
# {Title}

## Definition
[2-4 sentence definition]

## Mechanism
[How it works — math notation or pseudocode if helpful]

## Tradeoffs
[Table or bullets: gains, costs, failure modes]

## See Also
- [[related-slug]]

Rules: assume ML engineer audience, use numbers not vague claims, use [[wikilinks]] for cross-refs."""


def stage_compile_one(concept: dict, corpus: str) -> str:
    user = (
        f"Concept: {concept['title']}\n"
        f"Slug: {concept['slug']}\n"
        f"Summary: {concept.get('summary','')}\n\n"
        f"Source material:\n\n{corpus}"
    )
    return call_llm(
        system=COMPILE_SYSTEM,
        user=user,
        max_tokens=COMPILE_MAX_TOKENS,
        label=f"[[{concept['slug']}]]",
    )


def stage_compile(concepts: list[dict], raw_files: dict[str, str], only: str | None = None):
    CONCEPTS_DIR.mkdir(parents=True, exist_ok=True)
    corpus = raw_corpus(raw_files, max_chars_per_file=MAX_CHARS_COMPILE)
    compiled = []
    for concept in concepts:
        if only and concept["slug"] != only:
            continue
        article = stage_compile_one(concept, corpus)
        out_path = CONCEPTS_DIR / f"{concept['slug']}.md"
        out_path.write_text(article)
        print(f"  [write] {out_path.relative_to(VAULT_ROOT)}")
        compiled.append(concept)
    return compiled


# ─────────────────────────────────────────────────────────────────────
# Stage 3: Index
# ─────────────────────────────────────────────────────────────────────

INDEX_SYSTEM = """\
Write a wiki/index.md catalog for a knowledge base on Speculative Decoding.

Format:
# Speculative Decoding — Index

> [one-line description]. LLM-maintained.

## [Category]
- [[slug]] — one sentence
...

## Open Questions
- [3-5 gaps not yet covered]

Output ONLY the markdown."""


def stage_index(concepts: list[dict]):
    WIKI_DIR = INDEX_FILE.parent
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    articles = "\n".join(
        f"- slug={c['slug']}, title={c['title']}, summary={c.get('summary','')}"
        for c in concepts
    )
    content = call_llm(
        system=INDEX_SYSTEM,
        user=f"Articles:\n{articles}",
        max_tokens=INDEX_MAX_TOKENS,
        label="index.md",
    )
    INDEX_FILE.write_text(content)
    print(f"  [write] {INDEX_FILE.relative_to(VAULT_ROOT)}")


# ─────────────────────────────────────────────────────────────────────
# Stage 4: Log
# ─────────────────────────────────────────────────────────────────────

def stage_log(raw_files: dict[str, str], concepts: list[dict]):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    raw_list = "\n".join(f"  - {name}" for name in raw_files)
    concept_list = "\n".join(f"  - [[{c['slug']}]] — {c['title']}" for c in concepts)
    entry = textwrap.dedent(f"""
    ## {date} — Compile

    **Ingested:**
    {raw_list}

    **Compiled:**
    {concept_list}

    ---
    """).lstrip()

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOG_FILE.exists():
        LOG_FILE.write_text(entry + LOG_FILE.read_text())
    else:
        LOG_FILE.write_text(f"# Speculative Decoding Wiki — Log\n\n{entry}")
    print(f"  [write] {LOG_FILE.relative_to(VAULT_ROOT)}")


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage",   choices=["plan", "compile", "index", "all"], default="all")
    parser.add_argument("--concept", help="Compile one concept slug only")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Speculative Decoding KB — compile.py")
    print(f"  Model : {MODEL_PATH}")
    print(f"{'='*60}\n")

    raw_files = load_raw_files()
    print(f"[raw] {len(raw_files)} files: {list(raw_files.keys())}\n")

    if args.concept:
        concept = {"slug": args.concept, "title": args.concept.replace("-", " ").title(), "summary": ""}
        stage_compile([concept], raw_files, only=args.concept)
        return

    if args.stage in ("plan", "all"):
        print("[stage 1/4] Plan")
        concepts = stage_plan(raw_files)
        print()
    else:
        concepts = [
            {"slug": p.stem, "title": p.stem.replace("-", " ").title(), "summary": ""}
            for p in sorted(CONCEPTS_DIR.glob("*.md"))
        ]

    if args.stage in ("compile", "all"):
        print("[stage 2/4] Compile")
        stage_compile(concepts, raw_files)
        print()

    if args.stage in ("index", "all"):
        print("[stage 3/4] Index")
        stage_index(concepts)
        print()

    if args.stage == "all":
        print("[stage 4/4] Log")
        stage_log(raw_files, concepts)
        print()

    print("Done. Open wiki/index.md in Obsidian.")


if __name__ == "__main__":
    main()
