# 05 · Evaluator–Optimizer

> **Pattern:** One LLM generates, another scores it against criteria, and the loop repeats — feeding feedback back in — until a quality threshold is met.
> **You'll learn:** structured scoring, feedback loops, stopping conditions, and the token-cost trade-off.

---

## 1. The idea

A single generation is a one-shot gamble — sometimes great, sometimes not. The evaluator–optimizer
pattern turns generation into a **closed loop with quality control**:

```
brief ─► [generate] ─► [evaluate] ──pass?──► done
            ▲                        │ no
            └────── feedback ────────┘
```

Two roles, played by (usually) the same model with different prompts:

- **Generator** — produces the output; on later rounds it *revises* based on feedback.
- **Evaluator** — scores the output against explicit criteria and says pass/fail + why.

This mirrors how a writer and an editor work: draft, critique, revise, repeat.

---

## 2. The generator revises, not just generates

The key to the loop is that the generator prompt accepts the **previous attempt and the feedback**,
so each round is a targeted revision rather than a fresh random shot:

```python
generator = ChatPromptTemplate.from_messages([
    ("system", "Write ONE product tagline. If a previous attempt and feedback are given, "
               "revise to address the feedback."),
    ("human", "Brief: {brief}\n\nPrevious attempt: {previous}\nFeedback: {feedback}"),
]) | generator_llm | parser
```

On the first pass, `previous` and `feedback` are `"(none)"`.

---

## 3. The evaluator must be machine-readable

You can't branch on prose. Force the evaluator to return a **structured** verdict with
`with_structured_output`, so the score is a real number and `passed` is a real boolean:

```python
class Evaluation(BaseModel):
    score: int = Field(description="1 (poor) to 10 (excellent)", ge=1, le=10)
    passed: bool = Field(description="True only if it clearly meets the bar")
    feedback: str = Field(description="Specific, actionable feedback")

evaluator = eval_prompt | evaluator_llm.with_structured_output(Evaluation)
```

**Design the scoring prompt carefully:** name the criteria (punchiness, clarity, memorability),
give an explicit pass rule ("`passed=true` only if score ≥ 8"), and tell it to be demanding.
Vague criteria give you a vague, useless loop.

> **Tip — split the models.** Run the generator at a higher temperature (creative) and the
> evaluator at temperature 0 (consistent judging). You can even use a stronger model as the judge.

---

## 4. Stopping conditions (don't loop forever)

An unbounded loop is a runaway token bill. Always give it **two** exits:

```python
for i in range(1, max_iters + 1):          # 1) hard cap on iterations
    tagline = generator.invoke(...)
    ev = evaluator.invoke(...)
    if ev.passed or ev.score >= threshold: # 2) quality bar met
        return tagline
    previous, feedback = tagline, ev.feedback
return tagline                              # best-effort if cap hit
```

- **Quality met** — `passed` is true (or score ≥ threshold).
- **Max iterations** — bail out and return the best attempt so far.

A third condition worth adding in production: **no improvement** — if the score stops rising, stop
early rather than burning rounds.

---

## 5. The cost trade-off

Every iteration costs **two** LLM calls (generate + evaluate). A 4-round loop is up to 8 calls for
one output. That's the price of quality — so:

- Keep `max_iters` small (2–4 is usually plenty).
- Use the cheapest model that still judges reliably for the evaluator.
- Reserve the loop for outputs where quality genuinely matters (marketing copy, code, structured
  extraction) — not every request needs it.

---

## 6. Why a Python loop here (and not pure LCEL)?

LCEL pipes are a **DAG** — they flow forward, they don't cycle. A feedback loop is inherently
**cyclic**, so we drive it with a plain `while`/`for` loop around the runnables. When loops get more
complex (multiple exit branches, shared state, retries per node), that's exactly what **LangGraph**
is built for — you'll meet it in [Lesson 06](../06_agents_tool_calling/).

---

## 7. Cheat sheet

| Concept | What it does |
|---|---|
| Generator that reads `feedback` | Turns each round into a targeted revision |
| `with_structured_output(Evaluation)` | Machine-readable `score` / `passed` to branch on |
| Explicit criteria + pass rule | The difference between a useful and a useless judge |
| `max_iters` + threshold | Bounded loop — quality exit *and* safety exit |
| Two-temperature split | Creative generator, deterministic evaluator |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — a tagline generator that self-refines until it passes.

**Next:** [06 · Agents and tool calling](../06_agents_tool_calling/) — let the model choose its own actions and call real tools.
