# Parallelization: stop making your LLM calls wait in line

*Article 2 of a LangChain series — the foundation patterns.*

---

In the last article we chained LLM calls, where each step fed the next. But here's a question worth asking every time you build a chain: **do these steps actually depend on each other?**

Often they don't. And when they don't, running them one after another is just wasted time.

## A concrete example

Say you're generating branding for a product idea. You want a name, a tagline, and a target audience. Notice that none of these needs the others — they all depend only on the original idea.

Sequentially, your latency is the *sum* of all three calls. In parallel, it's roughly the *slowest one*:

```
sequential:  [name]──[tagline]──[audience]   = call1 + call2 + call3
parallel:    [name] [tagline] [audience]     ≈ max(call1, call2, call3)
```

For three calls that's often a 2–3x speedup for free.

## RunnableParallel

LangChain makes this a one-liner. You name the branches; you get back a dict with the same keys:

```python
from langchain_core.runnables import RunnableParallel

branding = RunnableParallel(
    name=name_chain,
    tagline=tagline_chain,
    audience=audience_chain,
)

branding.invoke({"idea": "a gamified morning habit tracker"})
# → {"name": ..., "tagline": ..., "audience": ...}
```

Every branch gets the same input and runs concurrently. (Bonus: a plain `dict` of runnables auto-coerces into a `RunnableParallel` inside a pipe — so you've probably already used this without noticing.)

## Fan-out, then fan-in

The pattern gets powerful when you parallelize *and then* combine. Run the branches concurrently, then pipe the merged dict into a final synthesis call:

```python
launch_chain = branding | synthesis_prompt | llm | parser
```

The expensive part (three generations) happens all at once; only the final combine is sequential.

## It's also how you compare

Want to A/B two prompts? Or pit `gpt-4o` against `gpt-4o-mini`? Run them as parallel branches on the same input and compare the outputs side by side. Same mechanism, different use — this is the backbone of prompt testing and ensembling.

## Don't forget the other axis

- `RunnableParallel` = different chains, one input.
- `.batch([...])` = one chain, many inputs (also concurrent).

Use the first for "do several things to this input," the second for "do this thing to all these inputs."

## The fine print

Parallel isn't a magic "go faster" button:

- **Rate limits** — fanning out N calls can trip provider limits. Cap with `max_concurrency`.
- **Cost** — you still pay for every branch.
- **False independence** — if a branch secretly needs another's output, you must chain, not parallelize.

---

The notebook has a timing cell that measures parallel vs. sequential so you can see the speedup on your own machine. Link in the comments.

Next up: **Routing** — instead of running every chain, send each input to the *right* one.

#LangChain #LLM #AIEngineering #Python #GenAI
