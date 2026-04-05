# EAGLE (Extrapolation Algorithm for Greater Language-model Efficiency)

## Definition  
EAGLE is a method designed to improve the computational efficiency of large language model (LLM) inference by operating directly on **feature-level representations** (e.g., penultimate layer hidden states) rather than the full token sequence. This approach reduces redundant computation and memory traffic during decoding.

## Mechanism  
EAGLE works by:

1. **Feature extraction**: Computes intermediate feature vectors from the LLM’s intermediate layer(s.
2. **Draft generation**: Uses a small, efficient draft model to propose candidate next tokens.
3. **Verification**: The full large model verifies the draft tokens in parallel.
4. **Iteration**: Repeats the process until a terminating condition is met.

This method leverages the **implicit feature alignment** between draft and target models to accelerate generation without sacrificing output quality.

## Tradeoffs  
| Gain | Cost | Failure Mode |
|-----|------|--------------|
| Faster LLM inference (up to 3× speedup reported) | Requires careful draft model selection | Misalignment between draft and target models can cause quality degradation |
| Lower memory bandwidth pressure | Works best with models whose features are well aligned | Over-reliance on small drafts can lead to incorrect token proposals |
| Better utilization of hardware parallelism | Requires specialized implementations for different architectures | |

## See Also
- [[apple-redrafter-mlx]]
- [[coding-confessions-survey]]
- [[practical-guide-speculative-decoding]]
- [[speculative-decoding-approach]]
