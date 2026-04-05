# EAGLE: Extrapolation Algorithm for Greater Language-model Efficiency
Source: sites.google.com/view/eagle-llm + research papers
Clipped: 2026-04-05

## Core Innovation
EAGLE operates at the **feature level** (penultimate layer hidden states) rather than the token level. This makes the regression task considerably simpler because features are more abstract and have clearer structure than raw token sequences.

## Architecture

### Auto-regression Head
- Lightweight model (0.24B–0.99B parameters depending on base model)
- Single-layer transformer decoder
- Input: current feature vectors + sampled token embeddings from previous step
- Output: predicted next feature vector
- The frozen base LLM's classification head converts predicted features → token distributions

### Why Feature-Level Works
- Token prediction: model must handle sampling randomness + semantic prediction
- Feature prediction: only semantic prediction (sampling already resolved)
- Including token embeddings in input "ensures consistent mapping between input and output"

### Tree-Based Guessing
- Multiple predictions from auto-regression head form a sparse context-aware token tree
- Avoids nonsensical combinations (unlike token-level approaches which can propose "I am begin")
- Tree structure passed to base LLM for parallel verification

## Training
- Dataset: ShareGPT (<70,000 conversational turns)
- Only auto-regression head is trained; base LLM frozen
- Vicuna 33B trainable in 24 hours on RTX 3090

## EAGLE vs EAGLE-2 vs EAGLE-3
| Version | Key Improvement |
|---------|-----------------|
| EAGLE-1 | Feature-level autoregression, static tree |
| EAGLE-2 | Dynamic tree construction — adapts tree shape based on confidence scores |
| EAGLE-3 | Scales with "training-time test" technique; 2-6x speedup range |

## Benchmarks
- EAGLE vs vanilla decoding: **3x faster** (13B models)
- EAGLE vs Lookahead: **2x faster**
- EAGLE vs Medusa: **1.6x faster**
- EAGLE-3: **2-6x speedup** depending on model size and batch

## Verification: Multi-Round Speculative Sampling
EAGLE extends traditional speculative sampling into recursive form:
- Maintains distributional consistency with original LLM
- Supports tree-based generation structures
- Mathematically equivalent outputs to vanilla decoding (lossless)

## Key Property: Losslessness
EAGLE produces mathematically identical output distribution to vanilla autoregressive decoding. The speedup is entirely latency — not an approximation.
