# X thread

Post each numbered block as one tweet. Images are in `figures/`. Character counts are under 280 for each.

---

**1/**
I replicated "Sparks of Weight-Space Programming" (the MIT post where GPT-6 Astra edits neural net weights by hand) on my MacBook with MLX.

Short version: the core idea holds up. The headline numbers look bigger than they are.

Results + caveats below 🧵

---

**2/**
First I checked my setup against their released files.

Their 3 Qwen weight edits rebuild bit-for-bit from the public model. Astra's game networks score within 3% of their published numbers on my machine.

So the numbers below come from the same setup they used.

📎 figures/4_checks.png

---

**3/**
The math claim: Astra edits 0.016% of Qwen3.5-0.8B and MATH-500 goes from 7.9% to 48.1%.

The edit is real. A random edit of the same size, in the same place, does nothing (8% → 8%). Astra's edit took it to 22% at a 16k token cap (they used 32k).

---

**4/**
But here's the catch.

That 7.9% is the model with thinking ON, where it loops until it runs out of tokens. With thinking OFF (the model card's default), the unedited model scores 43% on my run.

No edit needed.

📎 figures/1_qwen_math.png

---

**5/**
The authors knew. A comment in their own released code says the model loops with thinking on and that thinking off is the default.

The post only reports thinking on.

---

**6/**
Their own results file lists about 7 Qwen runs. One of them found the big fix (48.1%). The others landed between 7.9% and 14.1%.

An independent group (openwsp) re-ran it with Astra and got 12.9%.

So the big result is possible. It just isn't reliable.

📎 figures/2_authors_runs.png

---

**7/**
The second claim: an LLM writes a game-playing network from zero, in one reply, no tools, no training.

This one held up for Astra. Breakout: 430 and 590 on my runs vs 15.8 for PPO trained 100M steps.

Seaquest didn't: 10 and 3 vs their published 53.

---

**8/**
Then I tried smaller models, since nobody runs Astra on a laptop.

Claude Opus 5.5 came close on Asterix (49 vs Astra's 53–69).
Sonnet, Haiku and GPT-6 Luna mostly failed, near zero on most games.

Sonnet used ~8x more tokens than Astra and still scored far lower.

📎 figures/3_minatar_ladder.png

---

**9/**
Caveats (there are plenty):
• 1–3 runs per setting, 50–100 math problems each
• MLX on Apple Silicon, they used vLLM on NVIDIA
• 16k token cap vs their 32k (ran out of time)
• Claude ran as Claude Code subagents, different system prompt
• A safety filter stopped 2 Claude runs

---

**10/**
My takeaway: a top LLM can read a network, find what's broken, and patch it by hand. That's genuinely new.

But "7.9% → 48.1%" fixes a broken mode, from one lucky run out of ~7. And only the biggest models can do it today.

---

**11/**
Everything is open: code, every run, every score, and a plain-English write-up.

Repo: https://github.com/Hammad-Anjum/weight-space-replication

Credit to the original authors for releasing full logs, which made this possible, and to ATI, openwsp, MatinKhajavi and tdotlab for their replications.
