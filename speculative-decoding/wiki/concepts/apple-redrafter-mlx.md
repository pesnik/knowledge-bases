# Apple ReDrafter: Recurrent Drafter for Fast Speculative Decoding

## Definition
Apple ReDrafter is an LLM inference optimization technique that uses a smaller “draft” model to propose tokens in parallel with a larger “target” model, which then verifies them, enabling faster decoding on Apple Silicon.

## Mechanism
ReDrafter works by running a draft model in parallel with a larger model, where the draft model generates a batch of candidate tokens while the larger model verifies them in a single pass. This leverages the fact that the draft model can propose multiple tokens at once, while the larger model only processes one token at a time, reducing the number of passes and improving throughput.

- **Mathematical formulation**:  
  Let \( \mathcal{D} \) be the draft model, \( \mathcal{T} \) the target model, \( \mathcal{T}_{out} \) the ground truth tokens, and \( \mathcal{D}_{out} \) the draft predictions.  
  The draft phase produces:  
  \[
  \mathcal{D}_{out} = \text{draft}(\mathcal{D}_{\text{base}}, \mathcal{D}_{\text{context}}, \mathcal{D}_{\text{context}})
  \]  
  The verification phase produces:  
  \[
  \mathcal{T}_{out} = \text{verify}(\mathcal{D}_{out}, \mathcal{T})
  \]  
  The overall output is \( \mathcal{T}_{out} \) if all drafts are correct.

## Tradeoffs
| Gain / Cost | Description |
|-------------|-------------|
| **Speed** | Enables up to 3× faster LLM inference by parallelizing draft and verify steps. |
| **Accuracy** | Requires close alignment between draft and target model distributions; misalignment can reduce effectiveness. |
| **Memory** | Smaller draft reduces per-iteration memory pressure on unified memory. |
| **Latency** | Introduces additional compute overhead for the draft model, but this is offset by reduced token-by-token latency. |
| **Robustness** | Failure modes include incorrect draft predictions or insufficient verification capacity. |

## See Also
- [[coding-confessions-survey]]
- [[eagle-llm]]
- [[practical-guide-speculative-decoding]]
- [[speculative-decoding-approach]]
