# Speculative Decoding: Balancing Speed and Accuracy in Large Language Models

## Definition
Speculative decoding is a technique that accelerates large language model (LLM) inference by employing a smaller “draft” model to propose candidate tokens while the larger target model verifies them in parallel, leveraging the fact that the draft model can propose multiple candidates per step. It is most effective when draft predictions closely match target model probabilities.

## Mechanism
The core idea is to decouple token generation into two parallel steps:
1. **Draft phase**: A smaller model (the draft) predicts a set of candidate tokens for a sequence step.
2. **Verify phase**: The larger model (the target) verifies each candidate in a single parallel pass, accepting or rejecting them based on its own logits.

Typical pseudocode:
```
for each sequence step:
    generate k draft tokens in parallel
    verify all k tokens in one batch
    keep only tokens accepted by target model
```

This approach reduces the number of full model passes required, thus speeding up generation without retraining the main model.

## Tradeoffs
| Gain / Cost | Description |
|-------------|-------------|
| **Speed** | Drastically reduces latency by avoiding sequential token-by-token generation |
   - Up to **3× faster** inference reported in practice |
 | **Accuracy** | Potential for small accuracy drop if draft model is misaligned with target model |
| **Memory** | Enables larger context windows by reducing compute per step |
| **Applications** | Ideal for interactive apps, real-time search, and edge devices with limited compute |
| **Failure modes** | Mismatch between draft and target distributions can cause errors or reduced perplexity gains |

## See Also
- [[apple-redrafter-mlx]]
- [[coding-confessions-survey]]
- [[eagle-llm]]
- [[practical-guide-speculative-decoding]]
