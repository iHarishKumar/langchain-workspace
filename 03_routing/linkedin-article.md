# Routing: stop answering every question with the same prompt

*Article 3 of a LangChain series — the foundation patterns.*

---

So far in this series we've chained LLM calls in sequence, and run them in parallel. Both run *every* step. But real apps often need to do the opposite: look at the input and run *just one* of several possible chains.

That's routing — and it's what turns a single prompt into a system.

## The intuition

Picture a support desk. A refund question and an app-crash report should not be handled by the same prompt. You want:

```
                 ┌─ billing specialist
query ─► router ─┼─ technical support
                 └─ generalist
```

The router's only job is to pick the right destination. There are three ways to build it, and they trade off cost against intelligence.

## 1. The function router (free, brittle)

The simplest router is a Python function that returns the chain to run:

```python
def keyword_router(inputs):
    q = inputs["query"].lower()
    if any(w in q for w in ("refund", "invoice", "charge")):
        return billing_chain
    if any(w in q for w in ("error", "crash", "bug")):
        return tech_chain
    return general_chain
```

Wrap it in `RunnableLambda` and you're done. Instant and free — but brittle. "My card got hit twice" has no keyword, so it falls through to the wrong place.

## 2. LLM classifier + RunnableBranch (smart, costs a call)

For messy natural language, let a model classify first, then branch on the label. `RunnableBranch` is just an if/elif/else over runnables:

```python
branch = RunnableBranch(
    (lambda x: "billing"   in x["category"].lower(), billing_chain),
    (lambda x: "technical" in x["category"].lower(), tech_chain),
    general_chain,  # default
)

router = RunnablePassthrough.assign(category=classifier) | branch
```

Now "my card got hit twice" routes to billing correctly. The cost: an extra LLM call per request.

## 3. Semantic routing (cheap, no keywords)

Here's the one most people haven't tried. You can route by *meaning* without an LLM classifier at all:

1. Write a handful of example phrases per route.
2. Embed them once, average into a "centroid" per route.
3. For each query, embed it and route to the nearest centroid by cosine similarity.

```python
def semantic_router(inputs):
    q_vec = embeddings.embed_query(inputs["query"])
    best = max(route_centroids, key=lambda r: cosine(q_vec, route_centroids[r]))
    return chains_by_route[best]
```

"Can you reverse the duplicate payment" has no billing keyword — but its embedding sits closest to the billing examples, so it routes correctly. One *cheap* embedding call instead of a full generation, and it scales to many routes without keyword maintenance.

## Which one?

| Approach | Decides by | Cost | Best for |
|---|---|---|---|
| Function | your logic | free | clear keywords |
| LLM + Branch | a model | 1 LLM call | fuzzy language, few routes |
| Semantic | embeddings | 1 embed call | many routes, low latency |

In production you often layer them: function router for the obvious cases, semantic routing for the rest, LLM classifier only for the genuinely ambiguous.

---

The notebook implements all three on the same support-desk example so you can compare them directly. Link in the comments.

That wraps the foundation trio — chaining, parallelization, routing. Next we move into orchestration: a planner LLM that breaks work into subtasks and delegates to specialist workers.

#LangChain #LLM #AIEngineering #Python #GenAI
