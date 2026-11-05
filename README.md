# Replicating "Sparks of Weight-Space Programming"

An independent replication, still in progress, of Takehi, Teoh, Zhang and Khattab (MIT CSAIL, November 2026),
*Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights*
([blog post](https://rikiyat.github.io/blog/weight-space-programming/),
[authors' logs](https://github.com/RikiyaT/lm_understand-logs)). We have no affiliation with the authors.

The question we focus on: **does it actually work, and does it hold beyond one flagship model and one run?**

**[`LOG.md`](LOG.md) is the running log.** It holds every setting, deviation from the authors' setup, result and
caveat. This README only explains how to rebuild the setup.

## What's here

| Path | What it is |
|---|---|
| `wsp/qeval.py` | Exp 8. A local MLX MATH-500 eval that mirrors the authors' `think35` protocol (thinking on, T=0.6, top_p=0.95, top_k=20, presence penalty 1.5 over the whole generation, 32k cap, math-verify on the last `\boxed{}`) |
| `wsp/make_controls.py` | Exp 8. Random-edit controls for Qwen3.5-0.8B: a random direction, random columns, random heads zeroed, and Opus-style random edits, matched to Astra's released edit |
| `runs/` | Exp 8 eval queues (`queue*.sh`) and results: per-run `summary.json` and `generations_slim.jsonl` |
| `exp5/` | Exp 5 (write MinAtar policy networks from scratch), across editors of different sizes: an edits-DSL parser, a 1,000-episode evaluator, runners for Codex and Claude subjects, and every run's reply, network (`net.npz`), tool audit and score |
| `scripts/` | Repo upkeep: a commit-time path sanitizer and a generation slimmer |

## Reproduce

Hardware used: an Apple M5 Pro with 48 GB, running MLX. There's no CUDA, so Exp 8 uses MLX in place of the
authors' vLLM (a listed deviation).

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt

# Upstream logs: prompts, released networks and edits, eval code
git clone --depth 1 https://github.com/RikiyaT/lm_understand-logs ext/lm_understand-logs

# Exp 8: base model (pinned revision) and MATH-500
hf download Qwen/Qwen3.5-0.8B --revision 2fc06364715b967f1860aea9cf38778875588b17
.venv/bin/python -c "from huggingface_hub import hf_hub_download as d; d('HuggingFaceH4/MATH-500','test.jsonl',repo_type='dataset',local_dir='data/math500')"
B=~/.cache/huggingface/hub/models--Qwen--Qwen3.5-0.8B/snapshots/2fc06364715b967f1860aea9cf38778875588b17
mkdir -p models && ln -sfn $B models/qwen35-0.8b-base
# Rebuild Astra's released edits (hash-checked). Copy the config/tokenizer files from $B into each models/qwen35-0.8b-<run>/ first.
.venv/bin/python -I ext/lm_understand-logs/exp8_math/code/apply_edit.py \
  $B/model.safetensors-00001-of-00001.safetensors ext/lm_understand-logs/exp8_math/runs/p50c/edit \
  models/qwen35-0.8b-p50c/model.safetensors-00001-of-00001.safetensors
.venv/bin/python wsp/make_controls.py 3                    # random-edit control models
.venv/bin/python wsp/qeval.py --model models/qwen35-0.8b-p50c --out runs/q08_p50c_32k --n 100 --max-tokens 32768

# Exp 5: validate the pipeline on Astra's released networks, then run subjects and summarize
cd exp5
../.venv/bin/python validate_parser.py && ../.venv/bin/python validate_eval.py
../.venv/bin/python runner.py --backend codex --model gpt-6-luna --n 3    # Codex CLI subject, tools off
../.venv/bin/python summarize.py
```

Claude subjects were run as fresh Claude Code subagents because headless `claude -p` wasn't available. They receive
the verbatim prompt through one file read and save their reply with one write. Each transcript is audited
(`exp5/claude_subject.py`); `LOG.md` lists the differences this introduces. The prompts are not committed: each
run's prompt is byte-identical to upstream `exp5_write_from_scratch/runs/<game>/message.txt`.

## Related independent replications

- [alan-turing-institute/weights_editing](https://github.com/alan-turing-institute/weights_editing)
- [MatinKhajavi/Weight-Space-Programming](https://github.com/MatinKhajavi/Weight-Space-Programming)
- [openwsp/openwsp](https://github.com/openwsp/openwsp)
- [tdotlab/weight-space-programming](https://github.com/tdotlab/weight-space-programming)

## Licenses

- **Our code:** MIT (see [`LICENSE`](LICENSE)).
- **Upstream logs:** CC BY 4.0 (scripts MIT). They are not redistributed here; clone them as shown above.
- **MinAtar:** GPL-3.0. It is installed from PyPI, and its source (embedded in the upstream Exp 5 prompts) is not
  redistributed here.
- **Benchmarks:** MATH-500 and the others keep their own licenses.

## Maintainer note

`.gitattributes` passes text files through `scripts/sanitize_paths.py` at commit time. It strips local paths and
session ids without touching the working tree. Enable it in each clone you commit from:

```bash
git config filter.sanitize.clean "python3 scripts/sanitize_paths.py %f"
git config filter.sanitize.smudge cat
```
