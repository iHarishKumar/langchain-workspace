Your first instinct with an LLM is one giant prompt.

"Research this, outline it, then write the intro."

It works… until the output is mediocre and you can't tell which part failed.

There's a better default — the most fundamental pattern in LangChain:

𝗣𝗿𝗼𝗺𝗽𝘁 𝗰𝗵𝗮𝗶𝗻𝗶𝗻𝗴.

Break the work into steps. Feed each output into the next:

topic → research angle → outline → intro

Why it beats one mega-prompt:

→ Quality: each call has ONE job, so it does it better
→ Debuggable: inspect every step, not a black box
→ Tunable: different model/temperature per step
→ Resilient: retry or cache a single step

In LangChain it's just the pipe operator:

angle | outline | intro

And one trick to keep every intermediate result instead of only the last one:

RunnablePassthrough.assign()

I wrote up the full pattern + a runnable notebook (3-step blog pipeline with live token streaming). Link in the comments. 👇

This is article 1 of a LangChain series. Next: parallelization.

#LangChain #LLM #AIEngineering #Python #GenAI
