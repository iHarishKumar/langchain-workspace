# Prompt Chaining: the LangChain pattern you'll use in almost every app

*Article 1 of a LangChain series — the foundation patterns.*

---

Most people's first instinct with an LLM is to write one giant prompt. "Research this topic, then outline it, then write me an intro." It works… until it doesn't. The output is mediocre, you can't tell which part failed, and when you want to tweak just the outline you're back to rewriting the whole thing.

There's a better default, and it's the most fundamental pattern in LangChain: **prompt chaining.**

## The idea in one line

Break the work into steps, and feed each step's output into the next.

```
topic → [research angle] → [outline] → [intro paragraph]
```

Each step is a small, focused prompt that does exactly one job. It's the Unix philosophy applied to LLMs: small tools, composed together.

## Why this beats one mega-prompt

- **Quality.** A model asked to do one thing does it better than a model juggling five goals.
- **Debuggability.** You can inspect the output of every step instead of guessing what went wrong inside a black box.
- **Tunability.** Different temperature, model, or parser per step — creative for the intro, deterministic for the extraction.
- **Resilience.** Retry or cache a single step instead of redoing everything.

The cost is latency: N steps means N sequential calls. So chain when the steps *genuinely depend* on each other. When they don't, you parallelize instead (that's the next article).

## How it looks in LangChain

LangChain expresses this with **LCEL** — the LangChain Expression Language — and the `|` pipe operator. If you've used a shell pipeline, this will feel familiar:

```python
angle_chain   = angle_prompt   | llm | parser   # topic   → angle
outline_chain = outline_prompt | llm | parser   # angle   → outline
intro_chain   = intro_prompt   | llm | parser   # outline → intro
```

Every component implements the same `Runnable` interface — `.invoke()`, `.stream()`, `.batch()` — so they snap together cleanly.

## The one trick worth knowing: accumulating state

If you naively write `angle_chain | outline_chain | intro_chain`, you throw away the intermediate results — you only get the final intro. To keep everything, use `RunnablePassthrough.assign()`:

```python
full_chain = (
    {"angle": angle_chain}
    | RunnablePassthrough.assign(outline=outline_chain)
    | RunnablePassthrough.assign(intro=intro_chain)
)
```

Now the result is a dict with the angle, the outline, AND the intro — perfect for showing your work or logging each stage.

## Production touches that take 30 seconds

Because every step is a Runnable, hardening the chain is trivial:

- `outline_chain.with_retry(stop_after_attempt=3)` — exponential backoff on flaky calls
- `intro_chain.with_fallbacks([backup_chain])` — swap to a backup model if the primary fails

Drop them straight back into the pipe; nothing else changes.

## When to reach for it

Use prompt chaining for any multi-stage task where step N needs step N-1: research → outline → draft → edit, or extract → transform → format. If your steps are independent, parallelize. If you need to pick one path out of many, that's routing.

---

Full concept doc + a runnable notebook (a 3-step blog pipeline, including token streaming) are in the repo. Link in the comments.

Next up: **Parallelization** — running independent chains at the same time with `RunnableParallel`.

#LangChain #LLM #AIEngineering #Python #GenAI
