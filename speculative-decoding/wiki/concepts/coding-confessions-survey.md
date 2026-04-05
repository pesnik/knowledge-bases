# A Survey of Speculative Decoding Techniques

## Definition
Speculative decoding techniques are methods designed to accelerate the inference of large language models (LLMs) by leveraging auxiliary smaller models to propose token candidates in parallel with the primary model’s verification step, thereby reducing latency while maintaining accuracy.

## Mechanism
Speculative decoding works by running a **draft model** in parallel to the larger **target model**, where the draft model predicts a small set of candidate tokens (often \(k\–1\); e.g., \(k=3\) or \(5\)), and the target model verifies each token in a single batch. This approach reduces the number of expensive target-model passes, improving throughput.

- **Mathematical view**:  
  - Let \( \hat{y}_1, \ldots, \hat{y_k} \) be candidates from the draft model.  
  - The target model computes logits \( \log \pi(y_i \mid \text{context}, \hat{y}_1, \ldots, \hat{y_{k}}) \) for each candidate.  
  - Candidates with logits above a threshold or within a confidence interval are accepted.

- **Pseudocode**:
```python
for each token batch:
    draft_preds = draft_model(query, context)
    all_logits = target_model(query, context, draft_preds)
    accepted = (all_logits >= threshold) & (all_logits <= threshold + delta)
    final_preds = draft_preds[accepted]
```

## Tradeoffs
| Gain / Cost | Description |
|-------------|-------------|
| **Speed** | Up to 2–5× faster inference for LLMs on modern hardware when supported by memory bandwidth and compute parallelism. |
| **Accuracy** | Acceptable if draft model’s distribution is close to target model’s; otherwise, error rates may rise. |
| **Memory** | Requires additional memory for draft model outputs; mitigated by smaller model size. |
| **Robustness** | Failure modes include mis-specification of token space, over/under-shooting acceptance thresholds. |

## See Also
- [[apple-redrafter-mlx]]
- [[eagle-llm]]
- [[practical-guide-speculative-decoding]]
- [[speculative-decoding-approach]]
