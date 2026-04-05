# Practical Guide: 3x Faster LLM Inference with Speculative Decoding

## Definition
Speculative decoding is an inference acceleration technique that uses a small "draft" model to propose candidate tokens in parallel with a larger "target" model, which then verifies the correctness of the draft tokens, enabling up to 3× speedups in some scenarios by reducing compute waste from sequential token generation.

## Mechanism
Speculative decoding works by running a **draft model** in parallel with the **target model** to propose multiple token candidates (often k ≥ 1) per step, then the **target model** verifies each candidate in a single batch; correct candidates are kept and used to continue decoding, minimizing the number of sequential passes.

- **Mathematically**:  
  - Let \(D_d\) be the draft model, \(D_t\) the target model.  
  - For step \(t\): generate \(k\) candidates \(\{\hat{y}_{t,1}, ..., \hat{y}_{t,k}\}\) with \(D_d\); then run \(D_t\) on all candidates in parallel; keep those \(\hat{y}_{t,i}\) where \(|\hat{y}_{t,i} - y_{t,i}| < \tau\) (or log-probability threshold).
- **Pseudocode**:
  ```
  for each step t:
      draft = D_d(x, t)
      candidates = [draft(x, t, i) for i in 1..k]
      verified = [y for y in candidates if D_t.verifies(y)]
      if len(verified) == len(candidates):
          use all verified candidates
      else:
          use only correct ones
  ```

## Tradeoffs
| Gain / Cost | Gain | Cost | Failure Mode |
|-------------|------|------|--------------|
| **Speed** | Up to 3× faster LLM inference | Requires model parallelism; overhead of maintaining draft/target models | Model mismatch, incorrect verification |
| **Memory** | Leverages larger unified memory bandwidth | Needs extra memory for draft models | Out-of-memory on low-RAM devices |
| **Accuracy** | Near-lossless decoding for well-model alignment | Slightly lower per-token probability if draft is too small | Missed tokens if draft too conservative |
| **Generality** | Works with any LLM backend | Sensitive to token distribution shift | Failure on rare/unknown tokens |

## See Also
- [[apple-redrafter-mlx]]
- [[coding-confessions-survey]]
- [[eagle-llm]]
- [[speculative-decoding-approach]]
