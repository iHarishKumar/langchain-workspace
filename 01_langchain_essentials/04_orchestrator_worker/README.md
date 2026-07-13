# 04 · Orchestrator–Worker

> **Pattern:** A planner LLM decomposes a goal into subtasks at runtime, delegates each to a worker, then synthesizes the results.
> **You'll learn:** task decomposition with structured output, dynamic worker fan-out, and result aggregation.

---

## 1. The problem it solves

Prompt chaining ([Lesson 01](../01_prompt_chaining/)) has a **fixed** shape — you hard-code the
steps. But some goals can't be decomposed in advance. "Write a guide to caching strategies" might
need 3 sections; "compare 5 databases" needs 5. You don't know the shape until you look at the
input.

The orchestrator–worker pattern lets the **model decide the plan** at runtime:

```
goal ─► [orchestrator: plan] ─► [worker ×N in parallel] ─► [synthesizer] ─► final
```

- **Orchestrator** — reads the goal, emits a list of subtasks.
- **Workers** — one focused chain, run once per subtask (concurrently).
- **Synthesizer** — merges the pieces into one coherent output.

This is the LLM version of map-reduce: *plan → map over workers → reduce.*

---

## 2. The orchestrator: plan with structured output

The critical trick is making the planner return **typed objects**, not prose you have to parse.
LangChain's `with_structured_output` binds a Pydantic schema to the model and returns instances of
it:

```python
from pydantic import BaseModel, Field
from typing import List

class SubTask(BaseModel):
    title: str = Field(description="Short title of the subtask")
    instruction: str = Field(description="A specific, self-contained instruction for the worker")

class Plan(BaseModel):
    subtasks: List[SubTask] = Field(description="3-5 focused, non-overlapping subtasks")

planner = prompt | llm.with_structured_output(Plan)

plan = planner.invoke({"goal": GOAL})
plan.subtasks          # → List[SubTask], ready to iterate
```

Now the number of subtasks is decided by the model, but you get back safe, structured data you can
loop over — no brittle regex, no "parse the numbered list."

---

## 3. The workers: one chain, fanned out

You don't need a different chain per subtask. Define **one** general worker and run it once per
subtask. Because the subtasks are independent, fan them out concurrently with `.batch()`
([Lesson 02](../02_parallelization/)):

```python
worker = worker_prompt | llm | parser

inputs = [{"goal": GOAL, "title": s.title, "instruction": s.instruction} for s in plan.subtasks]
sections = worker.batch(inputs)      # all workers run at once
```

> **Dynamic worker selection.** Here every subtask uses the same worker. To route different
> subtask *types* to different specialists (e.g. a "code" worker vs a "prose" worker), have the
> orchestrator tag each subtask with a `worker_type`, then pick the chain per subtask — that's
> [Routing](../03_routing/) applied inside the loop.

---

## 4. The synthesizer: reduce

The workers produce isolated sections that may overlap or clash in tone. A final LLM call stitches
them together:

```python
draft = "\n\n".join(f"## {s.title}\n{sec}" for s, sec in zip(plan.subtasks, sections))
final = synthesizer.invoke({"goal": GOAL, "draft": draft})
```

The synthesizer's job: remove redundancy, add transitions, enforce a logical order.

---

## 5. Orchestrator–worker vs. neighbouring patterns

| Pattern | Who decides the steps | How many chains run |
|---|---|---|
| Prompt chaining (01) | you, at build time | fixed sequence |
| Routing (03) | a classifier | exactly one |
| **Orchestrator–worker (04)** | **the planner LLM, at runtime** | **many, in parallel** |
| Agents (06) | the LLM, step by step in a loop | as many as it takes |

Orchestrator–worker is a **single planning pass**: decide everything up front, then execute. If the
plan itself needs to adapt based on intermediate results, you want an **agent** (Lesson 06) or a
LangGraph loop.

---

## 6. Trade-offs

✅ Handles open-ended goals whose structure varies per input.
✅ Workers run in parallel → decomposition doesn't multiply latency linearly.
✅ Structured plans are debuggable and loggable.

⚠️ Cost scales with subtask count (N workers + 1 planner + 1 synthesizer).
⚠️ A bad plan poisons everything downstream — invest in the orchestrator prompt.
⚠️ Independent workers can't see each other's output; overlap is fixed only at synthesis.

---

## 7. Cheat sheet

| Tool | Role |
|---|---|
| `llm.with_structured_output(Plan)` | Planner returns typed `Plan` objects, not text |
| Pydantic `BaseModel` + `Field(description=...)` | Schema + guidance the model reads |
| `worker.batch(inputs)` | Run one worker over all subtasks concurrently |
| Synthesizer chain | Reduce the section drafts into one output |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — full plan → workers → synthesize pipeline.

**Next:** [05 · Evaluator–optimizer](../05_evaluator_optimizer/) — close the loop: generate, score, refine.
