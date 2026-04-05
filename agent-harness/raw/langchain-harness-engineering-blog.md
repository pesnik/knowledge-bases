# Improving Deep Agents with Harness Engineering
Source: blog.langchain.com/improving-deep-agents-with-harness-engineering
Clipped: 2026-04-05

## What is a Harness (LangChain's definition)
"The goal of a harness is to mold the inherently spiky intelligence of a model for tasks we care about."

Three primary optimization knobs:
1. **System Prompts** — instructional guidance shaping model behavior
2. **Tools** — available capabilities and integrations
3. **Middleware** — hooks that intercept and guide model and tool interactions

## Key Technical Patterns

### Build-Verify Loop
Models naturally stop after generating an initial solution. Implement explicit guidance for:
- Planning and discovery phases
- Implementation with testing in mind  
- Verification against task specifications
- Iterative fixing based on test feedback

Implementation: `PreCompletionChecklistMiddleware` forces verification before task completion.

### Context Injection Middleware
- `LocalContextMiddleware` maps directory structures and available tools at startup
- Time budget warnings nudge agents toward completion
- Environment constraints and evaluation criteria explicitly communicated

### Loop Detection
`LoopDetectionMiddleware` tracks repetitive file edits — helps agents escape "doom loops" where they repeatedly apply the same broken approach.

### Reasoning Budget Allocation
"Reasoning sandwich" approach for extended thinking models:
- Maximum reasoning at planning phase
- Standard reasoning for implementation
- Maximum reasoning at verification phase

## Observability is the Feedback Loop
Execution traces enable:
- Identifying failure patterns at scale
- Automated analysis of agent mistakes
- Data-driven harness improvements

## Key Result
Improved coding agent from **52.8% → 66.5% accuracy** on Terminal Bench 2.0 **without changing the underlying model**.

Implication: harness design is a first-class lever, not an afterthought.
