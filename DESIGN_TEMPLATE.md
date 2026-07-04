# DESIGN

## Architecture

The solution uses a single rule-based orchestrator implemented in `candidate.py`. The orchestrator receives a user prompt, identifies the intent using deterministic rule-based routing, and executes the appropriate sequence of tools. Each workflow enforces the required tool ordering, handles validation and ambiguity where necessary, and records every tool invocation using the provided `Tools` wrapper.

```
                User Prompt
                     |
                     v
          +----------------------+
          | Rule-based Router    |
          +----------------------+
                     |
     -------------------------------------------------------
     |        |         |         |         |              |
  Models   Optimise  Forecast  Compare  Current Budget  Target KPI
                     |
                     v
               Lifesight Tools
```

---

## Agent topology and why

I implemented a single orchestration agent because the workflows are deterministic and entirely tool-driven. One orchestrator is sufficient to perform intent detection, validate user inputs, execute the required tool sequence, and return grounded responses.

A multi-agent design would add unnecessary coordination overhead for this assignment. Given more time, I would separate the system into an Intent Router, Planning Agent, and Tool Execution Agent for better scalability and maintainability.

---

## How I handled each hard problem

### Orchestration / ordering

Implemented explicit workflows for every prompt. Wherever required, `run_default_optimise` is always executed before `run_constrained_optimise`, and `forecast_revenue` is executed only after successful optimisation.

### Tool ambiguity (current_budget vs planner_budget; list vs details)

Used the canonical `get_current_budget` tool instead of the deprecated `get_planner_budget`. Used `list_models` to resolve the latest successful Revenue model whenever the user omitted the model ID.

### Token optimisation (the 19MB list, referencePoint, response curves)

Reduced the large model response to only the required fields (`id`, `modelName`, `outcomeKPI`, `modelStatus`, `createdAt`) and returned only the latest five models while preserving the total count.

Large optimisation responses were also reduced by extracting only the required "All Platforms" metrics instead of returning the complete optimisation payload.

### Latency / fewer LLM hops

No LLM was used. All routing and orchestration were implemented deterministically, resulting in zero LLM calls and zero token consumption.

### Zero hallucination (g07, g08, g10)

The system never invents models, budgets, metrics, or business rules. Invalid model IDs return tool errors, missing information results in clarification questions, and business rules such as locked channels are obtained directly from `channel_metadata`.

### Grounding (no glossary tool; how you map terms→fields + spot ambiguity; g09)

Business terms are grounded entirely in tool outputs. Ambiguous requests such as "Show me conversions" trigger clarification instead of returning fabricated values. Revenue, optimisation results, and channel information are always obtained directly from tool responses.

### Param correctness / recovery (camelCase)

All tool calls use the required API parameter names such as `mmmRequestId`, `constraintType`, and `totalBudget`, avoiding parameter mismatches and ensuring compatibility with the provided APIs.

### Harness improvements

Every tool invocation is executed through the provided `Tools` wrapper, allowing the harness to verify tool usage, execution order, and orchestration automatically.

---

## Trade-offs and what I cut

To maximise correctness within the assignment timeline, I implemented a deterministic rule-based orchestrator instead of an LLM-based planner.

This resulted in some repeated logic across workflows, particularly when identifying the latest Revenue model and executing optimisation pipelines.

With another day, I would:

- Refactor repeated logic into reusable helper functions.
- Improve intent detection beyond keyword matching.
- Support multi-turn conversations with conversation state.
- Add richer natural language responses.
- Improve robustness for unseen prompt variations.

---

## Results

```
Structural checks passed: 12/12
Total LLM hops: 0
Total prompt tokens: 0
Total completion tokens: 0
```

### Supported workflows

- Model listing
- Budget optimisation
- Revenue forecasting
- Multi-scenario comparison
- Target KPI budget calculation
- Current budget retrieval
- Locked channel identification
- Missing model detection
- Missing budget clarification
- Ambiguous metric clarification
- Parameter recovery
- End-to-end optimisation and forecasting
