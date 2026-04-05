# Practical Guide: 3x Faster LLM Inference with Speculative Decoding
Source: bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding
Clipped: 2026-04-05

## Setup Overview
Speculative decoding accelerates LLM inference by using a smaller draft model to propose tokens while the larger target model verifies in parallel. Works best when draft model predictions closely match target model distribution.

## Draft Model Selection Criteria

### Two Critical Misalignment Factors
1. **Task domain mismatch**: generic pretrained draft models don't capture specific workload patterns
2. **Context length limitations**: pretrained draft heads not optimized for long-context scenarios

**Recommendation**: Train custom draft model on your own data when possible.

## Acceptance Rate (α) — The Key Metric
α = how often the target model accepts draft predictions
- α 0.6-0.8 → 2-3x speedups
- α < 0.5 → wastes compute on rejected tokens, can be slower than baseline
- Linear relationship: acceptance rate ≈ throughput improvement

## Real Speedup Benchmarks

### Theoretical (Llama-3.1-8B)
- Baseline: 4,065 ms end-to-end latency
- With α=0.8, 5 speculative tokens: ~3x speedup

### EAGLE-3 Practical Results
- ~2x speedups on MT-Bench, HumanEval, CNN/DailyMail
- Real acceptance rates in 0.6-0.8 range

## Training a Custom EAGLE Draft Model

### Dataset
- Combined UltraChat-200k + ShareGPT

### Hardware
- 8 H200 GPUs
- Use gradient_accumulation_steps=8 for fewer GPUs
- ~10 training epochs

## When Speculative Decoding Doesn't Help
- Large batch sizes: memory bandwidth no longer the bottleneck — compute is
- Very short sequences: overhead of verification outweighs savings
- Draft model acceptance rate < 0.5: rejected tokens waste more than verified tokens save
- Highly diverse/creative tasks: hard to predict → low acceptance rate

## Implementation Checklist
1. Benchmark baseline latency first
2. Start with an existing draft model (EAGLE-3 has pretrained options for Llama/Mistral/Qwen)
3. Measure acceptance rate on your actual workload
4. If α < 0.6, consider training a custom draft model on your data
5. Test at your actual batch size — benefits diminish at batch > 1
6. Monitor for output distribution drift (should be lossless but validate)

## Key Takeaway
Don't treat speculative decoding as plug-and-play. The technique requires tuning to your specific hardware + model + workload combination. When tuned correctly, 2-3x latency reduction is achievable on single-stream inference.
