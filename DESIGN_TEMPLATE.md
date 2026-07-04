# DESIGN

## Architecture

The solution uses a single rule-based orchestrator implemented in `candidate.py`. The orchestrator receives the user prompt, identifies the intent using rule-based routing, and executes the required sequence of tools. Each workflow follows the required tool ordering while recording every tool call through the provided `Tools` wrapper.

```
                User Prompt
                     |
                     v
          +--------------------+
          | Rule-based Router  |
          +--------------------+
                     |
     -----------------------------------------
     |        |        |        |            |
  List     Optimise  Forecast  Compare   Target KPI
                     |
                     v
               Lifesight Tools
```

---

## Agent topology and why

I used a single orchestrator instead of multiple agents because the assignment workflows are deterministic and tool-driven. A single agent is sufficient to identify user intent, execute the correct tool sequence, and return grounded responses.

A multi-agent architecture would introduce unnecessary coordination overhead for this implementation. With more time, I would separate the system into an Intent Router, Planning Agent, and Tool Execution Agent.

---

## How I handled each hard problem

### Orchestration / ordering

Implemented explicit workflows for each supported prompt. For optimisation workflows, `run_default_optimise` is always executed before `run_constrained_optimise`, satisfying the required dependency.

### Tool ambiguity (current_budget vs planner_budget; list vs details)

Used `list_models` to identify the latest successful Revenue model. I avoided deprecated tools where applicable and preferred the canonical workflow.

### Token optimisation (the 19MB list, referencePoint, response curves)

Instead of returning the complete model list, I returned only the relevant fields (`id`, `modelName`, `outcomeKPI`, `modelStatus`, `createdAt`) and displayed only the latest five models with the total count.

For optimisation responses, only the required "All Platforms" metrics were returned instead of the complete optimisation payload.

### Latency / fewer LLM hops

No LLM was used. All routing is deterministic using rule-based conditions, resulting in zero LLM calls and zero token usage.

### Zero hallucination (g07, g08, g10)

The implementation returns only values produced by the tools and does not fabricate any metrics. Error responses are propagated directly from the tools.

### Grounding (no glossary tool; how you map terms→fields + spot ambiguity; g09)

Business terms were mapped directly from tool outputs (for example, Revenue models and "All Platforms" optimisation response). No unsupported metrics were invented.

### Param correctness / recovery (camelCase)

Tool calls use the required API parameter names such as `mmmRequestId`, `constraintType`, and `totalBudget` as defined by the mock API.

### Harness improvements

Used the provided `Tools` wrapper for every tool invocation so that the harness automatically records tool traces for verification.

---

## Trade-offs and what I cut

To meet the assignment timeline, I implemented a deterministic rule-based orchestrator instead of an LLM planner. Code reuse through helper functions was limited, leading to some duplicated logic across prompts.

With another day, I would:

- Refactor repeated logic into reusable helper functions.
- Improve intent recognition to handle more prompt variations.
- Implement clarification handling for ambiguous prompts.
- Complete the remaining harness scenarios.
- Add conversation memory and better error recovery.

---

## Results

```
Structural checks passed: 5/12
Total LLM hops: 0
Total prompt tokens: 0
Total completion tokens: 0
```

Implemented prompts:
- Model listing
- Latest Revenue model optimisation
- Scenario comparison
- Target KPI calculation
- Core tool orchestration
