# Replication log: Sparks of Weight-Space Programming

A running log for reproducibility. The newest results are at the top of each section. The paper analysis and the
original checklist are in `BREAKDOWN.md`.

## 0. Setup (2026-11-05)

| Item | Value |
|---|---|
| Machine | Apple M5 Pro, 48 GB, macOS (Darwin 25.5). No CUDA, so we use MLX instead of vLLM |
| Python | `.venv` (Python 3.12, uv): mlx-lm 0.32.2, math-verify, minatar 1.0.15, numpy |
| Authors' logs | `ext/lm_understand-logs` (git clone, depth 1, of github.com/RikiyaT/lm_understand-logs, as of 2026-11-05) |
| Base model | Qwen/Qwen3.5-0.8B @ `2fc06364715b967f1860aea9cf38778875588b17` (HF cache; symlink `models/qwen35-0.8b-base`) |
| Editors available | Codex CLI 0.163.0 on a ChatGPT subscription: `gpt-6-astra` and `gpt-6-luna` (mini models are refused). Claude: headless `claude -p` is logged out, so Claude subjects run as Claude Code subagents (see §2) |

**The authors' harness is not public.** The logs README lists it as "not included". Independent replications we
read but did not run (they are context for our results):
- **alan-turing-institute/weights_editing:** Exps 1, 2 and 5 with Astra, Opus 5.5 and older models, plus controls.
- **MatinKhajavi/Weight-Space-Programming:** all 8 experiments with Opus 5.5; Fable 5.1 on some.
- **openwsp/openwsp:** a live Exp 8 run with Astra scored 12.9% on MATH-500, versus 48.1% published.
- **tdotlab/weight-space-programming:** Exp 8 by hand on Qwen3.5-0.8B and 2B.

---

## 1. Exp 8: Qwen3.5-0.8B math (local MLX eval)

### 1a. The released edits rebuild exactly (done)
`ext/.../exp8_math/code/apply_edit.py` was applied to the pinned base weights for p10c, p25c and p50c. **All tensor
hashes match** the authors' evaluated checkpoints. The rebuilt models are `models/qwen35-0.8b-{p10c,p25c,p50c}`.

### 1b. Eval harness: `wsp/qeval.py`
- **Mirrors the authors' `think35` protocol:**
  - chat template with thinking on;
  - prompt = problem + "\nPlease reason step by step, and put your final answer within \boxed{}.";
  - T=0.6, top_p=0.95, top_k=20, presence penalty 1.5 over the whole generation (as vLLM does);
  - max 32,768 tokens;
  - the last `\boxed{}` after `</think>` is graded with math-verify.
- **Deviations:**
  - MLX instead of vLLM (different kernels and RNG).
  - **A fixed 100-problem subset** of MATH-500 (`random.Random(0).shuffle`), 1 sample per problem. The authors used
    500 problems × 4 samples.
  - The 16k-cap screens reuse the 32k runs: a generation that finished under 16,384 tokens is identical up to
    that point.
- **Throughput:** about 1,030 tokens/s at batch 32. One 100-problem run at 32k takes about 1 hour.
- **Bug fixed 2026-11-05:** the first version kept a lazy per-sequence presence mask, and its compute graph grew
  until Metal raised a "Resource limit exceeded" error two generations in. We replaced it with stateless
  gather/scatter penalties, retested at 8k, and restarted every run from scratch.

### 1c. Queue (running)
- **`runs/queue1.sh`:**
  - `q08_base_32k`: base model;
  - `q08_p50c_32k`: Astra's 50-pass edit;
  - `q08_base_nothink`: thinking off, Qwen's non-thinking sampling, 8k cap.
- **`runs/queue2.sh`:** random-edit controls at a 16k cap, built by `wsp/make_controls.py`. The p50c delta is exactly
  rank 1 (second singular value about 0.001 vs 1.75), which makes the controls clean:
  - `rdir0-2`: p50c's columns and per-column coefficients, but the written direction replaced by a random unit vector
    (same norm).
  - `rcol0-2`: p50c's direction moved to 64 random columns.
  - `rhead0-3`: one random attention head zeroed, like p25c. Heads 23.2, 15.4, 23.3 and 19.0.
  - `ropus0-1`: the shape of an Opus edit reported by MatinKhajavi (3 random heads zeroed + one random neuron ×2).
- **The question:** if random edits also lift MATH-500, the claim that the LLM found the loop circuit is weak, and the
  real story is that the base model is fragile.

### 1d. Results
_(pending)_

---

## 2. Exp 5: write MinAtar networks from scratch (editor-size ladder)

Code is in `exp5/`, written by a subagent and checked by me:
- `dsl.py`: the edits-DSL parser;
- `evaluate.py`: 1,000 episodes, MinAtar 1.0.15, sticky actions 0.1, 10k-step cap, sampled or greedy actions;
- `runner.py`: Codex subjects;
- `claude_subject.py` + `score_reply.py`: Claude subjects;
- `summarize.py`: the results table.

**Validation (passed):**
- Parsing Astra's three replies reproduces `hand.npz` exactly.
- Astra's networks score 502.9 / 52.2 / 54.2 against 517.4 / 53.1 / 53.2 published (all within 3%).

**Codex subjects:**
- The prompt is the verbatim `message.txt`, with the instructions file "Answer the user's request.", effort `xhigh`.
- Every tool and hook is switched off.
- Each call runs from a fresh empty temp directory.
- Every event stream is audited for tool calls.

**Claude subjects (deviation):**
- Headless `claude -p` is logged out and the account owner isn't available. So each Claude subject is a **fresh
  Claude Code subagent** (model `sonnet`, `haiku` or `opus`), which carries none of this conversation.
- It gets the staged verbatim `message.txt` through one Read, and saves its reply with one Write.
- `claude_subject.py` audits the transcript; any other tool call marks the run not tool-free.
- **Differences from the authors' setup:**
  - Claude Code's subagent system prompt instead of the one-line instruction;
  - effort not set;
  - task and reply go through Read/Write.
- **The orchestrating session (me) is never the subject,** because it has read the authors' answers.

### Results (sampled score, mean over 1,000 episodes; greedy in brackets)
| Editor (effort) | Breakout | Seaquest | Asterix | Output tokens per call |
|---|---|---|---|---|
| PPO 100M / 500M (published) | 15.8 / 25.3 | 5.6 / 88.9 | 25.8 / 55.2 | – |
| GPT-6 Astra, published (xhigh, n=1) | 517.4 | 53.1 | 53.2 | 20–29k |
| GPT-6 Astra, ours (xhigh) | r1 430.4 [322.7] | r1 **10.1** [9.5] | r1 52.9 [54.3] | 20–29k |
| GPT-6 Luna (xhigh, n=3) | 0.0, 1.7, 2.3 | 1.0, 0.0, 0.5 | 0.9, 1.5, 3.1 | 14–33k |
| Claude Sonnet 5.5 (xhigh) | r1 **blocked by API safeguards** | r1 5.4 [5.3] | r1 29.0 [31.1] | 190–207k |
| Claude Sonnet 5.5 (default effort) | r1 4.4 [8.4] | r1 0.8 [1.0] | r1 10.9 [12.9] | 4–50k |
| Claude Haiku 5.5 (xhigh) | running | running | running | |
| Claude Opus 5.5 (xhigh) | r1 **blocked by safety classifier** | running | running | |

**Notes:**
- **Safeguards block.** Sonnet xhigh Breakout r1 was stopped by the API: "safeguards flagged this message …
  `[reasoning_extraction]`", request `req_011Cgj2fQmvNrh475HDej3tv`. The prompt was the verbatim task, which ran fine
  at default effort. It is not retried and not scored.
- **Astra Seaquest.** Our 10.1 against the published 53.1 agrees with ATI (n=3 mean 25.5): the published Seaquest
  run looks like a lucky draw.
- **Luna's failures are real.** Every reply parsed; its networks just don't play (for example, Breakout misses the
  first ball). In 2 of 75 statements Luna gave a value list of the wrong shape, and the parser skipped those, as the
  prompt's rules say.
- **Sonnet's token use.** At xhigh, Sonnet spent about 7–10× the output tokens Astra did, for far lower scores.
- **Token counts for Claude** are summed once per API message from the subagent transcript; wall time isn't
  recorded for Claude runs.
- **Run mapping:** each Claude run's transcript ↔ run is in `exp5/claude_runs.tsv`. Finish a run with
  `exp5/finish.sh <transcript id>`.

To reproduce the table: `cd exp5 && ../.venv/bin/python summarize.py`.
