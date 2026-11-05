"""Build random-edit control models for Exp 8 (Qwen3.5-0.8B). Each control is a model dir under models/ with one
safetensors file in which a few tensors differ from the base.

Controls (seeded, deterministic):
  rdir<k>   p50c's edit with the WRITTEN DIRECTION replaced by a random unit vector: per tensor, p50c's delta D on
            its 64 columns is ~rank 1 (D = s a b^T); the control writes s r b^T with r random. Same columns, same
            per-column magnitudes, same norm. Tests: does the specific "loop direction" matter?
  rcol<k>   p50c's direction a and per-column coefficients, moved to 64 RANDOM columns of the same tensors.
            Tests: do the specific columns matter?
  rhead<k>  zero one random attention head's output (o_proj input columns) in a random full-attention layer,
            the same kind of edit as p25c (head 15.7). Tests: does knocking out an arbitrary head break loops?
  ropus<k>  the shape of an Opus 5.5 edit reported by an independent replication (zero 3 random heads, x2 one
            random MLP neuron's down_proj column). Tests: are such small arbitrary edits enough?
"""
import json
import os
import shutil
import sys

import mlx.core as mx
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "models/qwen35-0.8b-base")
P50C = os.path.join(ROOT, "models/qwen35-0.8b-p50c")
ST = "model.safetensors-00001-of-00001.safetensors"
PFX = "model.language_model.layers."
FULL_ATTN = [3, 7, 11, 15, 19, 23]
HEADS, HEAD_DIM, HIDDEN, FFN = 8, 256, 1024, 3584


def f32(x):
    return np.array(x.astype(mx.float32))


def write(name, base, changes, info):
    d = os.path.join(ROOT, "models", f"qwen35-0.8b-{name}")
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(BASE):
        if f != ST and not f.startswith("model.safetensors"):
            shutil.copy(os.path.join(BASE, f), d)
    shutil.copy(os.path.join(BASE, "model.safetensors.index.json"), d)
    out = dict(base)
    for k, v in changes.items():
        out[k] = mx.array(v.astype(np.float32)).astype(mx.bfloat16)
    mx.save_safetensors(os.path.join(d, ST), out, metadata={"format": "pt"})
    rel = {k: float(np.linalg.norm(v - f32(base[k])) / np.linalg.norm(f32(base[k]))) for k, v in changes.items()}
    json.dump({"name": name, "info": info, "relative_change": rel}, open(os.path.join(d, "control.json"), "w"), indent=1)
    print(name, info, {k.replace(PFX, ""): round(r, 4) for k, r in rel.items()}, flush=True)


def main(n=3):
    base = mx.load(os.path.join(BASE, ST))
    p50 = mx.load(os.path.join(P50C, ST))
    dkeys = [PFX + f"{L}.mlp.down_proj.weight" for L in (15, 19)]
    # p50c delta per tensor -> (columns, rank-1 factors)
    fac = {}
    for k in dkeys:
        W, We = f32(base[k]), f32(p50[k])
        D = We - W
        cols = np.where(np.abs(D).sum(0) > 0)[0]
        U, S, Vt = np.linalg.svd(D[:, cols], full_matrices=False)
        fac[k] = (cols, U[:, 0], S[0] * Vt[0], S[:3].tolist())
        print(k.replace(PFX, ""), "cols", len(cols), "top singular values of delta", [round(s, 3) for s in S[:3]])

    for i in range(n):
        rng = np.random.default_rng(1000 + i)
        ch = {}
        for k in dkeys:
            cols, a, sb, _ = fac[k]
            r = rng.standard_normal(HIDDEN)
            r /= np.linalg.norm(r)
            W = f32(base[k]).copy()
            W[:, cols] += np.outer(r, sb)
            ch[k] = W
        write(f"rdir{i}", base, ch, "random written direction, p50c columns and coefficients")

        ch = {}
        for k in dkeys:
            cols, a, sb, _ = fac[k]
            rc = rng.choice(np.setdiff1d(np.arange(FFN), cols), size=len(cols), replace=False)
            W = f32(base[k]).copy()
            W[:, rc] += np.outer(a, sb)
            ch[k] = W
        write(f"rcol{i}", base, ch, "p50c direction and coefficients on random columns")

    heads = [(L, h) for L in FULL_ATTN for h in range(HEADS) if (L, h) != (15, 7)]
    rng = np.random.default_rng(7)
    picks = [heads[j] for j in rng.choice(len(heads), size=n + 1, replace=False)]
    for i, (L, h) in enumerate(picks):
        k = PFX + f"{L}.self_attn.o_proj.weight"
        W = f32(base[k]).copy()
        W[:, h * HEAD_DIM:(h + 1) * HEAD_DIM] = 0
        write(f"rhead{i}", base, {k: W}, f"zero head {L}.{h}")

    for i in range(2):
        rng = np.random.default_rng(2000 + i)
        ch = {}
        for j in rng.choice(len(heads), size=3, replace=False):
            L, h = heads[j]
            k = PFX + f"{L}.self_attn.o_proj.weight"
            W = ch.get(k, f32(base[k]).copy())
            W[:, h * HEAD_DIM:(h + 1) * HEAD_DIM] = 0
            ch[k] = W
        L, c = int(rng.integers(24)), int(rng.integers(FFN))
        k = PFX + f"{L}.mlp.down_proj.weight"
        W = ch.get(k, f32(base[k]).copy())
        W[:, c] *= 2
        ch[k] = W
        write(f"ropus{i}", base, ch, f"zero 3 random heads + x2 neuron {L}:{c}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
