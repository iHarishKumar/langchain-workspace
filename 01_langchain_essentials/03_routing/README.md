# 03 · Routing

> **Pattern:** Send each input to a *different* chain based on its content.
> **You'll learn:** custom function routers, `RunnableBranch`, LLM-based classification, and embedding-based **semantic routing**.

---

## 1. Why routing?

- [Lesson 01](../01_prompt_chaining/) ran steps **in sequence**.
- [Lesson 02](../02_parallelization/) ran steps **all at once**.
- Routing runs **one of several** — it picks the right chain for the input and skips the rest.

This is how you build a system that handles different *kinds* of input well. A support desk
shouldn't answer a refund question with the same prompt it uses for a crash report. Route the
billing query to a billing specialist, the bug to a technical one, everything else to a
generalist.

```
                 ┌─ billing_chain
query ─► router ─┼─ tech_chain
                 └─ general_chain
```

There are three common ways to build the router, from simplest to smartest.

---

## 2. Custom function router

The simplest router is a plain Python function that inspects the input and **returns the chain to
run**. Wrap it in `RunnableLambda` — when a runnable returns another runnable, LangChain invokes
the returned one with the same input:

```python
from langchain_core.runnables import RunnableLambda

def keyword_router(inputs: dict):
    q = inputs["query"].lower()
    if any(w in q for w in ("refund", "invoice", "charge")):
        return billing_chain
    if any(w in q for w in ("error", "crash", "bug")):
        return tech_chain
    return general_chain

rule_router = RunnableLambda(keyword_router)
```

✅ Free, instant, fully under your control.
❌ Brittle — "my card got hit twice" has no keyword, so it falls through to the wrong route.

Use this when inputs are structured or the keywords are reliable.

---

## 3. LLM classifier + `RunnableBranch`

For fuzzy natural language, let a model do the classifying. Two stages:

**Stage 1 — classify:**

```python
classifier = ChatPromptTemplate.from_template(
    "Classify into one word: 'billing', 'technical', or 'general'.\n\n"
    "Query: {query}\n\nCategory:"
) | llm | parser
```

**Stage 2 — branch on the label.** `RunnableBranch` is an `if/elif/else` over runnables: a list of
`(condition, runnable)` pairs plus a default:

```python
branch = RunnableBranch(
    (lambda x: "billing"   in x["category"].lower(), billing_chain),
    (lambda x: "technical" in x["category"].lower(), tech_chain),
    general_chain,   # default — required, runs if nothing matched
)

llm_router = RunnablePassthrough.assign(category=classifier) | branch
```

`RunnablePassthrough.assign(category=classifier)` adds the predicted `category` while keeping the
original `query`, so the destination chain still receives what it needs.

✅ Handles paraphrases and typos.
❌ Costs an extra LLM call per request, and adds latency.

---

## 4. Semantic routing (embeddings)

You can route by **meaning** without a classifier LLM call at all. The idea:

1. Write a few example utterances per route.
2. Embed them once and average into a **centroid** vector per route.
3. For each query, embed it and route to the **most similar** centroid (cosine similarity).

```python
import os
from langchain.embeddings import init_embeddings

# .env → MODEL_PROVIDER=openai, EMBEDDING_MODEL=text-embedding-3-small
embeddings = init_embeddings(
    os.environ["EMBEDDING_MODEL"],
    provider=os.environ["MODEL_PROVIDER"],
)

route_centroids = {
    name: np.mean(embeddings.embed_documents(examples), axis=0)
    for name, examples in route_examples.items()
}

def semantic_router(inputs):
    q_vec = embeddings.embed_query(inputs["query"])
    best = max(route_centroids, key=lambda r: cosine(q_vec, route_centroids[r]))
    return chains_by_route[best]
```

A query like *"can you reverse the duplicate payment"* has no billing keyword, but its embedding
sits closest to the billing examples — so it routes correctly.

✅ One **cheap** embedding call (not a full generation), scales to many routes, no keyword
maintenance.
❌ Quality depends on your example utterances; add a similarity threshold to catch
out-of-scope inputs.

---

## 5. Choosing an approach

| Approach | How it decides | Cost | Best when |
|---|---|---|---|
| Function router | your Python logic | free | clear keywords / structured input |
| LLM + `RunnableBranch` | a model classifies | 1 extra LLM call | fuzzy language, few routes |
| Semantic routing | embedding similarity | 1 cheap embed call | many routes, low latency, no keywords |

A common production setup: **function router first** (catch the obvious cases for free), fall back
to **semantic routing** for the rest, and reserve the **LLM classifier** for genuinely ambiguous
queries.

---

## 6. Cheat sheet

| Tool | Role |
|---|---|
| `RunnableLambda(fn)` | Wrap a function that returns the chain to run |
| `RunnableBranch((cond, chain), ..., default)` | if/elif/else over runnables |
| `RunnablePassthrough.assign(category=...)` | Add the classification, keep the original input |
| `init_embeddings(...)` + cosine similarity | Route by meaning, no extra generation |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — all three routers on the same support-desk example.

**Next:** 04 · Orchestrator–worker — a planner LLM splits work into subtasks and delegates to specialist workers.
