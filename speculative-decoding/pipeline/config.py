"""
Pipeline configuration — edit these to match your setup.
"""
from pathlib import Path

# ── Vault ────────────────────────────────────────────────────────────
VAULT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR    = VAULT_ROOT / "raw"
WIKI_DIR   = VAULT_ROOT / "wiki"
CONCEPTS_DIR = WIKI_DIR / "concepts"
LOG_FILE   = WIKI_DIR / "log.md"
INDEX_FILE = WIKI_DIR / "index.md"

# ── Local LLM (mlx_lm direct — no server needed) ────────────────────
MODEL_PATH = str(Path.home() / "Models/lmstudio-community")

# ── Generation params ────────────────────────────────────────────────
COMPILE_MAX_TOKENS  = 600       # per concept article
INDEX_MAX_TOKENS    = 350
PLAN_MAX_TOKENS     = 400
TEMPERATURE         = 0.2       # low for factual wiki content

# ── Context limits (M3 Pro 18GB — model uses 12.7GB, ~5GB left for KV) ──
MAX_CHARS_PLAN     = 400        # chars per raw file in plan stage (~400 tokens input)
MAX_CHARS_COMPILE  = 500        # chars per raw file in compile stage
MAX_CHARS_INDEX    = 80         # chars per concept summary in index stage

# ── KV cache quantization — halves KV memory footprint ──────────────
KV_BITS        = 8
KV_GROUP_SIZE  = 64
