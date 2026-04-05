# Techniques for Speculative Decoding in Large Language Models

## Definition
Speculative decoding is a family of methods designed to accelerate the inference speed of large language models (LLMs) by leveraging a smaller auxiliary (draft) model to propose candidate tokens, which are then verified by the larger target model. It targets the inefficiency where a single LLM forward pass typically yields only one token at a time, wasting compute capacity.

## Mechanism
Speculative decoding works by feeding the draft model a subset of the target model’s output candidates in parallel, allowing the draft to operate independently. The base model subsequently verifies each candidate in a subsequent pass. This approach reduces idle time and increases throughput by overlapping computation across models.

Mathematically, given an input sequence \(x\), the draft model \(M_d\) proposes a set of candidate tokens \(\{\hat{\omega}_i\}_{i=1}^k\), and the base model \(M_t\) verifies each \(\hat{\omega}_i\) in parallel. If all draft tokens are valid, the base model accepts the correct ones and skips the remaining untested tokens.

## Tradeoffs
- **Gains:** Up to 2–3× speedups in practice for LLMs on modern hardware, especially with large models and long sequences.
- **Costs:** Requires careful alignment of model architectures and attention mechanisms; misalignment can reduce effectiveness.
- **Failure modes:** Inefficient when draft models are too small or when the target model’s output distribution diverges significantly from the draft, causing rejections to increase.

## See Also
- [[apple-redrafter-mlx]]
- [[coding-confessions-survey]]
- [[eagle-llm]]
- [[practical-guide-speculative-decoding]]
