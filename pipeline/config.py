"""
Shared pipeline configuration.
KB-specific paths are derived from the --kb argument at runtime.
"""
from pathlib import Path

KB_ROOT = Path(__file__).resolve().parents[1]   # ~/Pesnik/knowledge-bases/

# ── Local LLM ────────────────────────────────────────────────────────
MODEL_PATH = str(Path.home() / "Models/lmstudio-community")

# ── Generation params ────────────────────────────────────────────────
COMPILE_MAX_TOKENS = 600
INDEX_MAX_TOKENS   = 350
PLAN_MAX_TOKENS    = 400
TEMPERATURE        = 0.2

# ── Context limits (M3 Pro 18GB — 12.7GB weights, ~5GB for KV) ──────
MAX_CHARS_PLAN    = 400
MAX_CHARS_COMPILE = 500
MAX_CHARS_INDEX   = 80

# ── KV cache quantization ────────────────────────────────────────────
KV_BITS       = 8
KV_GROUP_SIZE = 64


def get_paths(kb: str) -> dict:
    """Return all relevant paths for a given KB name."""
    vault      = KB_ROOT / kb
    wiki       = vault / "wiki"
    concepts   = wiki / "concepts"
    return {
        "vault":    vault,
        "raw":      vault / "raw",
        "wiki":     wiki,
        "concepts": concepts,
        "index":    wiki / "index.md",
        "log":      wiki / "log.md",
    }
