# 09 · RAG — Naive to Advanced

> **Pattern:** The model doesn't know your data — retrieve the relevant pieces and put them in the prompt.
> **You'll learn:** the split → embed → store → retrieve → generate pipeline, an LCEL RAG chain, and three upgrades: query rewriting, score thresholds, and citations.

---

## 1. Why RAG

Ask a model about *your* docs — internal wiki, product manual, last week's decisions — and it either
refuses or, worse, **makes something up**. Three ways to teach a model your data:

| Approach | How | Catch |
|---|---|---|
| Fine-tuning | Retrain on your data | Slow, costly, stale the day after, bad at facts |
| Long context | Stuff *everything* in the prompt | Cost per call explodes; recall degrades on huge inputs |
| **RAG** | Retrieve only the *relevant* pieces per question | You must build a retrieval pipeline — this lesson |

**Retrieval-Augmented Generation** wins for most "answer questions over my data" jobs: fresh (update
the index, not the model), cheap (send 3 chunks, not 300 pages), and auditable (you can *see* what
the answer was based on).

---

## 2. The naive pipeline

```
INGEST (once):    docs ──► split into chunks ──► embed ──► vector store
                                                              │
QUERY (per ask):  question ──► embed ──► similarity search ──► top-k chunks
                                                              │
                                       prompt(context + question) ──► LLM ──► answer
```

### Split

Embeddings capture *one idea* well; whole documents blur into mush, and you can't stuff 40 pages
into the prompt anyway. `RecursiveCharacterTextSplitter` cuts on paragraph/sentence boundaries
first, with an **overlap** so ideas straddling a cut survive in at least one chunk:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(docs)
```

Chunk size is the first knob to tune: too big → noisy, diluted embeddings; too small → fragments
with no context. A few hundred tokens is a sane default.

### Embed + store

Same embeddings idea as [Lesson 03's semantic router](../03_routing/) — meaning as vectors, but now
over your documents:

```python
vectorstore = InMemoryVectorStore.from_documents(chunks, init_embeddings(...))
```

`InMemoryVectorStore` (langchain-core, zero dependencies) is perfect for learning and tests. In
production you swap in Chroma, pgvector, Pinecone, Qdrant... — **the interface stays identical**,
which is the point of LangChain's vector-store abstraction.

### Retrieve + generate

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
rag.invoke("How do I install it?")
```

That's the whole naive RAG — a plain LCEL chain where one branch happens to hit a vector store.

---

## 3. Where naive RAG fails

1. **Wording mismatch.** The user says *"my flows die when a worker crashes"*; the doc says
   *"checkpoint recovery resumes interrupted runs."* Semantically related, but a single embedding of
   the user's phrasing may rank the right chunk poorly.
2. **No honesty.** Similarity search *always* returns k chunks — even for "what's the capital of
   France?" against your product docs. The model then answers from irrelevant context, or from its
   own guesses, with total confidence.
3. **No provenance.** An answer with no sources can't be verified or debugged.

Each failure has a targeted upgrade.

---

## 4. Upgrade 1 — Query rewriting (multi-query)

Don't search with one phrasing; have the LLM generate a few and merge the results:

```python
question ──► LLM ──► ["rephrase 1", "rephrase 2", "rephrase 3"]
                          │ retrieve for each, dedupe
                          ▼
                    union of chunks ──► generate
```

Structured output (Lesson 03's trick) makes the rewrite step reliable. Cost: one extra cheap LLM
call. Payoff: recall stops depending on the user guessing your docs' vocabulary.

---

## 5. Upgrade 2 — Score thresholds ("I don't know" beats a lie)

`similarity_search_with_score` exposes how similar the best match actually is. Gate on it:

```python
hits = vectorstore.similarity_search_with_score(question, k=3)
if hits[0][1] < THRESHOLD:            # best score too weak
    return "I can't answer that from the documentation."
```

Calibrate the threshold empirically: score a few on-topic and off-topic questions, pick a value
between the two clusters. This single `if` removes a whole class of hallucinations.

---

## 6. Upgrade 3 — Citations

You already have each chunk's `metadata` — put it in the context and ask for it back:

```python
context = "\n\n".join(f"[{d.metadata['source']}] {d.page_content}" for d in docs)
# prompt: "...cite the source file for each claim, like [pricing.md]"
```

Users can verify, and *you* can debug retrieval (a wrong answer citing `pricing.md` tells you
exactly which chunk misled it).

**Further up the ladder** (same ideas, bigger machinery): hybrid search (BM25 + vectors),
rerankers (a second model re-orders the top 20), parent-document retrieval (search small chunks,
return their bigger parents), and agentic RAG — Lesson 06's agent with retrieval as a *tool* it can
call repeatedly.

---

## 7. Cheat sheet

| Concept | What it does |
|---|---|
| `RecursiveCharacterTextSplitter(chunk_size, chunk_overlap)` | Split docs on natural boundaries, overlap protects cut ideas |
| `InMemoryVectorStore.from_documents(chunks, emb)` | Embed + index in one call (dev/tests) |
| `vectorstore.as_retriever(search_kwargs={"k": 3})` | Vector store → Runnable, pipes into LCEL |
| `{"context": retriever \| format_docs, ...}` | The naive RAG chain shape |
| Multi-query rewrite | LLM rephrases → retrieve each → dedupe → better recall |
| `similarity_search_with_score` + threshold | Refuse instead of hallucinating |
| Metadata in context | Citations: verifiable, debuggable answers |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — index a fictional product's docs (so the model *can't* cheat), watch naive RAG work and fail, then fix it three ways.

**Next:** [10 · Multi-agent and subgraph patterns](../10_multi_agent/) — when one agent isn't enough: specialists, supervisors, and subgraphs.
