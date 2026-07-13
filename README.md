# LangChain Workspace

Hands-on tutorial series on building with **LangChain** and **LangGraph** — organised as
*series → lessons*. Every lesson is a folder with a deep-dive `README.md` and a runnable
`notebook.ipynb` with minimal prose: read the concept, then run the code.

---

## Series

| # | Series | Lessons | Status |
|---|---|---|---|
| 01 | [LangChain Essentials](01_langchain_essentials/) — prompt chaining to multi-agent, memory, RAG, streaming, observability | 12 | ✅ complete |
| 02 | LangGraph Deep Dive — raw graphs, human-in-the-loop, persistence, durable execution | 10 planned | 🔜 next |
| 03 | Production RAG — hybrid search, rerankers, RAG evals, serving | outlined | 🗺 |
| 04 | Agent Evals — trajectory evals, LLM-judge calibration, regression gates | outlined | 🗺 |

**New here? Start with [Series 01, Lesson 01](01_langchain_essentials/01_prompt_chaining/).**

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .env.example .env             # then edit .env and paste your OpenAI key

# 4. Launch Jupyter
jupyter lab                      # or: jupyter notebook
```

All notebooks load credentials from the repo-root `.env` via `python-dotenv`. Models are created
with LangChain's provider-agnostic `init_chat_model` / `init_embeddings`, so you can swap providers
by editing `.env` — no notebook changes (the matching integration package must be installed).

Optional: add a [LangSmith](https://smith.langchain.com) key to `.env` (see `.env.example`) to get
tracing for every notebook — introduced in
[Series 01, Lesson 12](01_langchain_essentials/12_langsmith/).

---

## Repository layout

```
01_langchain_essentials/       ← series
   01_prompt_chaining/         ← lesson
      README.md                ← the concept, in depth
      notebook.ipynb           ← the demo, runnable top to bottom
   02_parallelization/
   ...
requirements.txt               ← one environment covers every series
```

---

## Follow along & support

- ⭐ **Star this repo** — it helps others find the series.
- 🔔 **Follow the series on LinkedIn** — a new lesson every Tuesday and Thursday. <!-- TODO: add profile URL -->
- 📬 **Newsletter** — coming soon: every lesson in your inbox. <!-- TODO: swap in the signup link when live -->
- 💼 **Team workshops** — hands-on LangChain/LangGraph training for engineering teams: harishkumargunjalli@gmail.com

---

## License

| What | License |
|---|---|
| **Code** — notebooks and code snippets | [MIT](LICENSE) — use it anywhere, including at work |
| **Written content** — lesson READMEs, explanations, diagrams | [CC BY-NC-SA 4.0](LICENSE-CONTENT.md) — share and adapt with attribution, **non-commercial** |

For commercial licensing of the written content (republishing, paid training material), email
harishkumargunjalli@gmail.com.
