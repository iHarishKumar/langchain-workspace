# 02 · Parallelization

> **Pattern:** Run independent chains concurrently and merge their outputs.
> **You'll learn:** `RunnableParallel`, fan-out/fan-in, comparing prompts/models, `.batch()`, and when *not* to parallelize.

---

## 1. The problem with sequential chains

In [Lesson 01](../01_prompt_chaining/) every step waited for the previous one — because each step
*needed* the previous output. But plenty of work is **independent**. If you want a product's
name, tagline, and target audience, none of those depends on the others. Running them one after
another just adds up the latency for no reason:

```
sequential:  [name]───[tagline]───[audience]      total = sum of all three
parallel:    [name]
             [tagline]      } all at once          total ≈ the slowest one
             [audience]
```

`RunnableParallel` runs the branches **concurrently** and collects them into one dict.

---

## 2. RunnableParallel

You give it named branches; it returns a dict with the same keys:

```python
from langchain_core.runnables import RunnableParallel

branding = RunnableParallel(
    name=name_chain,
    tagline=tagline_chain,
    audience=audience_chain,
)

branding.invoke({"idea": "a habit tracker that gamifies your mornings"})
# → {"name": "...", "tagline": "...", "audience": "..."}
```

Every branch receives the **same input** (`{"idea": ...}`) and runs at the same time. The result
is keyed by the branch names you chose.

### Shortcut: a plain dict

Inside a pipe, LangChain auto-coerces a plain `dict` of runnables into a `RunnableParallel`. So
these are equivalent:

```python
RunnableParallel(name=name_chain, tagline=tagline_chain)
{"name": name_chain, "tagline": tagline_chain}
```

You already saw this in Lesson 01 — `{"angle": angle_chain}` *was* a one-branch parallel block.

---

## 3. Fan-out, then fan-in

The real power is combining parallel branches with a synthesis step. Run the branches
concurrently (fan-out), then pipe the merged dict into a final call that uses all of them
(fan-in):

```python
synthesis_prompt = ChatPromptTemplate.from_template(
    "Write a launch blurb.\nName: {name}\nTagline: {tagline}\nAudience: {audience}"
)

launch_chain = branding | synthesis_prompt | llm | parser
```

`branding` emits `{name, tagline, audience}`; `synthesis_prompt` consumes exactly those keys. The
slow part (three generations) happens in parallel, and only the final combine is sequential.

---

## 4. Comparing prompts or models

Parallelization is also how you **compare** approaches. Same input, different personas — or
different models entirely (`gpt-4o` vs `gpt-4o-mini`) — side by side:

```python
compare = RunnableParallel(
    optimist=persona_chain("a relentless optimist"),
    skeptic=persona_chain("a hard-nosed skeptic"),
    pragmatist=persona_chain("a no-nonsense pragmatist"),
)
```

This is the backbone of A/B prompt testing and ensembling.

---

## 5. The other axis: `.batch()`

`RunnableParallel` runs **different chains on one input**. `.batch()` runs **one chain on many
inputs** — also concurrently:

```python
name_chain.batch([
    {"idea": "a habit tracker"},
    {"idea": "a budgeting app"},
    {"idea": "a meal planner"},
])
```

Use `RunnableParallel` for "do several different things to this input" and `.batch()` for "do the
same thing to all these inputs." Control fan-out width with
`config={"max_concurrency": N}`.

---

## 6. When to parallelize vs. chain

| Situation | Use |
|---|---|
| Step N needs step N-1's output | **Chain** ([Lesson 01](../01_prompt_chaining/)) |
| Steps are independent, same input | **`RunnableParallel`** |
| Same chain, many inputs | **`.batch()`** |
| Pick *one* path based on input | **Routing** ([Lesson 03](../03_routing/)) |

⚠️ **Watch out for:**
- **Rate limits** — fanning out N calls at once can trip provider limits; cap with `max_concurrency`.
- **Cost** — parallel doesn't mean free. You still pay for every branch.
- **False independence** — if a branch secretly needs another's output, you must chain, not parallelize.

---

## 7. Cheat sheet

| Concept | What it does |
|---|---|
| `RunnableParallel(a=..., b=...)` | Runs branches concurrently → dict keyed by name |
| `{"a": chain_a, "b": chain_b}` | Plain dict auto-coerces to `RunnableParallel` in a pipe |
| `parallel \| synthesis` | Fan-out then fan-in |
| `.batch([...])` | Same chain over many inputs, concurrently |
| `config={"max_concurrency": N}` | Cap simultaneous calls (rate-limit safety) |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — includes a timing cell proving the speedup.

**Next:** [03 · Routing](../03_routing/) — send each input to a *different* chain based on its content.
