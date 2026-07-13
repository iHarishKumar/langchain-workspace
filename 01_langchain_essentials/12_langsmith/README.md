# 12 · Tracing and Evaluation with LangSmith

> **Pattern:** You can't fix what you can't see, and you can't improve what you don't measure — tracing shows every step; evaluation scores the output.
> **You'll learn:** zero-code tracing via env vars, `@traceable`, building an eval dataset, LLM-as-judge evaluators, and the production feedback loop.

---

## 1. The two problems every LLM app hits in production

Everything in this series *works in a notebook*, where you can print and re-run. Production is
different:

1. **Debugging blind.** A user reports a bad answer. Which retrieval pulled the wrong chunk? Which
   agent step picked the wrong tool? With a multi-step chain there's no stack trace for "the answer
   was subtly wrong."
2. **Regressions you can't see.** You tweak a prompt and eyeball three examples — better! Meanwhile
   it silently broke five other cases. LLMs are nondeterministic; *vibes are not a test suite.*

**Tracing** solves the first; **evaluation** solves the second. [LangSmith](https://smith.langchain.com)
is LangChain's hosted platform for both (free tier available; LangChain-agnostic — it traces any
Python code).

---

## 2. Tracing: three env vars, zero code changes

```bash
# .env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...        # from smith.langchain.com → Settings → API Keys
LANGSMITH_PROJECT=langchain-workspace
```

That's the entire integration. Every chain, agent, retriever, and tool call from Lessons 01–11 now
records a **trace**: a tree of runs with inputs/outputs, latency, token counts, cost, and errors at
every node. The 40-message agent trace you streamed by hand in Lesson 06? It's now a clickable tree
in the UI — for *every* run, including the ones users hit while you were asleep.

Non-LangChain code joins the trace with a decorator:

```python
from langsmith import traceable

@traceable
def clean_input(text: str) -> str:      # shows up as a node in the same trace tree
    ...
```

---

## 3. Evaluation: regression tests for quality

The eval loop mirrors a test suite, with one twist — "passed" is a judgment call, so a model makes it:

```
dataset (question + reference answer)
   │  run each through your app  →  actual output
   ▼
evaluator: judge(question, reference, actual) → score
   ▼
aggregate → compare across versions
```

- **Dataset** — representative inputs + reference answers. Start with 10–20; grow it from real
  traces (especially the failures — every production bug becomes a test case).
- **Target** — the chain/agent under test.
- **Evaluator** — anything from `actual == expected` (rarely useful for prose) to **LLM-as-judge**:
  a model grades correctness against the reference. That's [Lesson 05](../05_evaluator_optimizer/)'s
  evaluator, promoted from a runtime loop to offline QA. Structured output keeps the verdict parseable.

The judge pattern, in miniature:

```python
class Grade(BaseModel):
    correct: bool
    reasoning: str

judge = judge_prompt | llm.with_structured_output(Grade)
```

With LangSmith, `evaluate()` runs the whole loop and hosts the results — every experiment linked to
its traces, diffable across prompt versions:

```python
from langsmith import evaluate
evaluate(target, data="my-dataset", evaluators=[correctness])
```

But note the pattern needs no platform: dataset + target + judge is ~30 lines of plain Python (the
notebook runs it locally first). The platform adds persistence, sharing, and history.

---

## 4. The production feedback loop

The two halves close a loop that's the actual point of this lesson:

```
   trace everything  ──►  bad runs surface  ──►  add them to the dataset
        ▲                                              │
        │                                              ▼
   ship the change  ◄──  evaluate the fix against the WHOLE dataset
```

Prompt changes stop being vibes. Model upgrades ("does gpt-5-mini break my agent?") become an
experiment you run, not a leap of faith. This is the difference between *having* an LLM app and
*operating* one.

---

## 5. Cheat sheet

| Concept | What it does |
|---|---|
| `LANGSMITH_TRACING=true` + API key | Every LangChain call traced — zero code changes |
| Trace | Tree of runs: inputs, outputs, latency, tokens, errors per node |
| `@traceable` | Pull plain Python functions into the trace tree |
| Dataset | Inputs + reference answers; grow it from real (failed) traces |
| LLM-as-judge | Model grades output vs. reference; structured output keeps it parseable |
| `evaluate(target, data, evaluators)` | Run the loop, host results, diff across versions |
| Trace → dataset → evaluate → ship | The production feedback loop |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — works **without** a LangSmith key (local eval runs anyway; tracing lights up if you add one).

---

🏁 **That's the series.** Twelve patterns, one arc: `invoke` → chains → parallel → routing → orchestration → evaluation loops → agents → memory → RAG → multi-agent → performance → observability. The [series README](../README.md) has the full map — and more series are in the works.
