# 10 · Multi-Agent and Subgraph Patterns

> **Pattern:** When one agent gets unreliable, split the job across specialists — and let a supervisor delegate.
> **You'll learn:** why big single agents degrade, the agents-as-tools supervisor pattern, subgraph mechanics, and when *not* to go multi-agent.

---

## 1. Why one agent stops being enough

[Lesson 06](../06_agents_tool_calling/)'s agent was great with 3 tools. Now imagine 25 tools across
research, finance, code, and email. Reliability drops in predictable ways:

- **Tool confusion** — the more (and more similar) tools, the more often the model picks the wrong one.
- **Prompt bloat** — every tool schema and instruction rides along on *every* call.
- **Context pollution** — a 40-message trace about invoices distracts the "send an email" step.
- **One prompt to rule them all** — a persona tuned for finance analysis is mediocre at copywriting.

The fix mirrors how humans organise: **specialists with narrow toolsets, and someone to coordinate**.

```
                          ┌──────────────┐
        user ───────────► │  SUPERVISOR  │ ─────────► final answer
                          └──────┬───────┘
                       delegates │ (as tool calls)
                 ┌───────────────┼────────────────┐
                 ▼               ▼                ▼
         ┌──────────────┐ ┌─────────────┐ ┌─────────────┐
         │ research     │ │ math        │ │ writer      │
         │ agent+tools  │ │ agent+tools │ │ agent+tools │
         └──────────────┘ └─────────────┘ └─────────────┘
```

This is [Lesson 04](../04_orchestrator_worker/)'s orchestrator–worker, escalated: workers are now
*agents*, and the orchestrator *decides at runtime* whom to call (vs. a fixed plan → batch).

---

## 2. The simplest supervisor: agents as tools

The trick that makes this almost free: **an agent is invocable, so an agent can be a tool.**

```python
research_agent = create_agent(llm, [search_docs], system_prompt="You are a research specialist...")

@tool
def research(question: str) -> str:
    """Look up facts about <domain>. Give it one specific question."""
    out = research_agent.invoke({"messages": [("human", question)]})
    return out["messages"][-1].content

supervisor = create_agent(llm, [research, calculate],
    system_prompt="You coordinate specialists. Delegate — don't answer domain questions yourself.")
```

The supervisor doesn't know (or care) that `research` runs a whole agent internally. Everything from
Lesson 06 still applies — the docstring is the delegation contract, streaming shows the delegation
decisions live.

**Why this works so well:**

- Each specialist has a **narrow toolset and its own system prompt** — tuned, testable, reusable.
- The supervisor sees **only distilled results**, not the specialists' internal tool traces — context
  stays clean by construction.
- It composes: specialists can have their own sub-specialists. Turtles all the way down.

---

## 3. What just happened, structurally: subgraphs

`create_agent` returns a **compiled LangGraph graph**. When the supervisor calls the `research`
tool, one graph runs *inside* another. That's a **subgraph** — graph as node of a parent graph —
and it's a first-class LangGraph concept, not a hack:

```python
child = child_builder.compile()
parent_builder.add_node("stage_two", child)     # a compiled graph IS a valid node
```

Two ways to embed, one rule of thumb:

| Embedding | Control flow decided by | Use when |
|---|---|---|
| Agent-as-tool | The supervisor **LLM**, at runtime | Which specialist to use depends on the request |
| Graph-as-node | **You**, with fixed edges | The pipeline between stages is known and must be deterministic |

Same escalation rule as Lesson 03 (router) vs. Lesson 06 (agent): known flow → wire it; unknown
flow → let the model decide.

---

## 4. Context engineering across agents

The single most important design decision: **what crosses the boundary between agents?**

- Supervisor → specialist: a *distilled task* ("What is NovaPlay's ARPU?"), not the whole
  conversation. Specialists start clean.
- Specialist → supervisor: a *distilled answer*, not the specialist's 15-message tool trace.

That isolation is exactly why multi-agent scales — and it has a price: a specialist can't see
context it wasn't given. If the specialist needs user preferences, pass them in the task string or
share a [store (Lesson 07)](../07_checkpointer_vs_store/).

---

## 5. When *not* to go multi-agent

Every hop adds an LLM call, latency, and a place to fail. The escalation ladder from this series
still applies — stop at the *first* rung that works:

```
chain (01) → parallel (02) → router (03) → single agent (06) → multi-agent (10)
```

Signals you actually need multi-agent: tool confusion you can measure, prompts fighting each other
(one persona can't do both jobs), or teams needing to own/test/deploy specialists independently.
"It sounds cooler" is not on the list. A single agent with 6 well-described tools beats a
five-agent system with vague ones, every time.

---

## 6. Cheat sheet

| Concept | What it does |
|---|---|
| Agents-as-tools | Wrap `specialist.invoke(...)` in `@tool` → supervisor delegates via tool calls |
| Supervisor | An ordinary `create_agent` whose tools happen to be agents |
| Specialist system prompts | Each sub-agent gets its own tuned persona + narrow toolset |
| Subgraph | A compiled graph used as a node (`add_node("x", child.compile())`) |
| Tool boundary = context boundary | Distilled task in, distilled answer out — traces stay private |
| Escalation ladder | chain → parallel → router → agent → multi-agent; stop early |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — two specialists, a supervisor that delegates (watch it live), and raw subgraph mechanics.

**Next:** [11 · Streaming and async](../11_streaming_async/) — make all of this *feel* fast (and *be* fast).
