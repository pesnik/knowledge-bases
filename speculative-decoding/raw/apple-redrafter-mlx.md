# Apple ReDrafter: Recurrent Drafter for Fast Speculative Decoding
Source: machinelearning.apple.com/research/recurrent-drafter + arxiv.org/abs/2403.09919
Clipped: 2026-04-05

## Why Apple Built This
Apple needed speculative decoding for on-device inference on Apple Silicon (Metal GPUs via MLX). Existing methods (EAGLE, Medusa) were designed for NVIDIA datacenter GPUs. ReDrafter optimizes specifically for the memory-bandwidth characteristics of unified memory Apple Silicon.

## Three Core Innovations

### 1. RNN-Based Draft Model
- Uses recurrent neural network (not transformer) conditioned on the LLM's hidden states
- RNNs are more efficient than transformer decoders for the draft model task
- Conditioned on LLM hidden states → tight coupling, better acceptance rates
- Competing approaches: Medusa uses feed-forward heads; EAGLE uses a small transformer decoder

### 2. Dynamic Tree Attention
- Applies tree attention over beam search results
- Eliminates duplicated prefixes in candidate sequences
- Reduces computational waste in verification step
- Adapts tree shape dynamically rather than using static tree templates

### 3. Knowledge Distillation Training
- Draft model learns directly from target LLM's output distribution
- Addresses distribution mismatch problem inherent in independently-trained drafters
- More aligned acceptance rates than naive small-model drafting

## Performance
| Hardware | Speedup |
|----------|---------|
| NVIDIA H100 | up to 2.8x (Vicuna, MT-Bench) |
| Apple M1 Max | up to 1.37x |
| Apple M2 Ultra | up to 2.3x |

## MLX Implementation
- Full implementation available in MLX for Apple Silicon
- Benchmarked on Metal GPUs
- Demonstrates viability for on-device inference, not just datacenter

## LM Studio Integration (Feb 2025)
- LM Studio beta added speculative decoding support for MLX models
- 20-50% speed gains reported for typical use cases
- Works with standard MLX-format models including community models

## Why Smaller Gains on Apple Silicon vs H100?
- Apple Silicon is unified memory architecture — no separate VRAM
- Memory bandwidth is still a bottleneck but different characteristics than discrete GPU
- Speculative decoding benefits are smaller on M1 Max than M2 Ultra because M2 Ultra has higher memory bandwidth
- Correlation: higher memory bandwidth → greater speculative decoding benefit
