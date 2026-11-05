"""Local (MLX) MATH-500 eval mirroring the authors' `think35` protocol as closely as MLX allows.

Authors' protocol (ext/lm_understand-logs/exp8_math/code/evaluate.py): vLLM, chat template with enable_thinking,
user turn = problem + "\\nPlease reason step by step, and put your final answer within \\boxed{}.",
T=0.6 top_p=0.95 top_k=20 presence_penalty=1.5 (vLLM: applied over all generated tokens), max 32,768 new tokens,
last \\boxed{} after </think> graded with math-verify.

Deviations: MLX instead of vLLM (different kernels/RNG); a fixed random subset of problems; optionally a lower token cap.

    python wsp/qeval.py --model models/qwen35-0.8b-base --out runs/base --n 100 --samples 1 --max-tokens 32768
"""
import argparse
import json
import os
import random
import re
import sys
import time

import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUCTION = "Please reason step by step, and put your final answer within \\boxed{}."


# ---------------------------------------------------------------- grading (same reading as the authors' mathqa.py)
def answer_text(text):
    return text.split("</think>")[-1].strip() if "</think>" in text else text


def _box_at(text, idx):
    key = "\\boxed" if text.startswith("\\boxed", idx) else "\\fbox"
    rest = text[idx + len(key):]
    r = rest.lstrip()
    if r.startswith("{"):
        depth = 0
        for k, ch in enumerate(r):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return r[1:k].strip() or None
        return None
    if key == "\\boxed" and rest.startswith(" "):
        return rest.strip().split("$")[0].split("\n")[0].strip() or None
    return None


def last_boxed(text):
    idx = text.rfind("\\boxed")
    if idx < 0:
        idx = text.rfind("\\fbox")
        if idx < 0:
            return None
    return _box_at(text, idx)


def is_correct(pred, gold):
    if pred is None or gold is None:
        return False
    from math_verify import parse, verify
    try:
        g, p = parse("\\boxed{" + gold + "}"), parse("\\boxed{" + pred + "}")
        return bool(g and p and verify(g, p))
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------- sampling helpers
def make_presence(penalty, vocab):
    """vLLM-style presence penalty over the WHOLE generation (mlx-lm's default window is only 20 tokens).
    Stateless: `tokens` is the full generated history; duplicate indices in the scatter write the same value."""
    def proc(tokens, logits):
        if tokens.size:
            t = tokens.reshape(-1).astype(mx.int32)
            logits[:, t] = logits[:, t] - penalty
        return logits
    return proc


def make_repetition(penalty, vocab):
    """HF-style repetition penalty over the whole generation."""
    def proc(tokens, logits):
        if tokens.size:
            t = tokens.reshape(-1).astype(mx.int32)
            sel = logits[:, t]
            logits[:, t] = mx.where(sel < 0, sel * penalty, sel / penalty)
        return logits
    return proc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=100, help="problems (fixed random subset, seed 0); 500 = all")
    ap.add_argument("--offset", type=int, default=0, help="skip the first k problems of the subset order")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--max-tokens", type=int, default=32768)
    ap.add_argument("--thinking", type=int, default=1)
    ap.add_argument("--temp", type=float, default=0.6)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--presence", type=float, default=1.5)
    ap.add_argument("--repetition", type=float, default=0.0)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "data/math500/test.jsonl"))]
    order = list(range(len(rows)))
    random.Random(0).shuffle(order)
    sel = [rows[i] for i in order[a.offset:a.offset + a.n]]

    mx.random.seed(a.seed)
    model, tok = load(a.model)
    vocab = model.args.vocab_size if hasattr(model.args, "vocab_size") else 300000
    prompts, meta = [], []
    for r in sel:
        text = tok.apply_chat_template([{"role": "user", "content": r["problem"] + "\n" + INSTRUCTION}],
                                       tokenize=False, add_generation_prompt=True, enable_thinking=bool(a.thinking))
        ids = tok.encode(text, add_special_tokens=False)
        for s in range(a.samples):
            prompts.append(ids)
            meta.append((r, s))

    done_path = os.path.join(a.out, "generations.jsonl")
    done = set()
    if os.path.exists(done_path):
        for l in open(done_path):
            d = json.loads(l)
            done.add((d["id"], d["sample"]))
    todo = [i for i, (r, s) in enumerate(meta) if (r["unique_id"], s) not in done]
    print(f"{len(meta)} generations, {len(todo)} to do", flush=True)

    sampler = make_sampler(temp=a.temp, top_p=a.top_p, top_k=a.top_k)
    gen = BatchGenerator(model, max_tokens=a.max_tokens, stop_tokens=[[t] for t in tok.eos_token_ids],
                         sampler=sampler, completion_batch_size=a.batch, prefill_batch_size=8)

    def procs():
        p = []
        if a.presence:
            p.append(make_presence(a.presence, vocab))
        if a.repetition:
            p.append(make_repetition(a.repetition, vocab))
        return p

    uids = gen.insert([prompts[i] for i in todo], [a.max_tokens] * len(todo),
                      logits_processors=[procs() for _ in todo])
    uid2i = dict(zip(uids, todo))
    toks = {u: [] for u in uids}
    t0, ntok, fin = time.time(), 0, 0
    with open(done_path, "a") as f:
        while responses := gen.next_generated():
            for r in responses:
                if r.finish_reason != "stop":
                    toks[r.uid].append(r.token)
                ntok += 1
                if r.finish_reason is not None:
                    row, s = meta[uid2i[r.uid]]
                    text = tok.decode(toks.pop(r.uid))
                    pred = last_boxed(answer_text(text))
                    ok = is_correct(pred, row["answer"])
                    fin += 1
                    f.write(json.dumps({"id": row["unique_id"], "sample": s, "level": row["level"],
                                        "subject": row["subject"], "answer": row["answer"], "pred": pred,
                                        "correct": ok, "finish": r.finish_reason,
                                        "n_tokens": len(tokenize_len(tok, text)), "text": text}) + "\n")
                    f.flush()
                    el = time.time() - t0
                    print(f"[{fin}/{len(todo)}] {row['unique_id']} s{s} {r.finish_reason} ok={ok} "
                          f"| {ntok/el:.0f} tok/s, {el/60:.1f} min", flush=True)
    gen.close()
    summarize(a.out, vars(a))


def tokenize_len(tok, text):
    return tok.encode(text, add_special_tokens=False)


def summarize(out, args=None):
    g = [json.loads(l) for l in open(os.path.join(out, "generations.jsonl"))]
    n = len(g)
    s = {"n_generations": n, "n_problems": len({x["id"] for x in g}),
         "acc": sum(x["correct"] for x in g) / n, "cut_share": sum(x["finish"] == "length" for x in g) / n,
         "acc_when_finished": (sum(x["correct"] for x in g if x["finish"] != "length")
                               / max(1, sum(x["finish"] != "length" for x in g))),
         "mean_tokens": sum(x["n_tokens"] for x in g) / n}
    if args:
        s["args"] = args
    json.dump(s, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in s.items() if k != "args"}))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "summarize":
        summarize(sys.argv[2])
    else:
        main()
