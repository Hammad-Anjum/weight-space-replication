"""1,000-episode MinAtar 1.0.15 evaluator for 600-32-32-6 tanh policies.
Sticky actions 0.1 (MinAtar's own Environment wrapper), difficulty ramping on (default), cap 10,000 steps.
Policy: 'sample' = softmax(logits) sampling, 'greedy' = argmax. Envs are stepped in lock-step batches per worker
so the MLP forward is batched."""
import argparse, json, os, sys, time
import numpy as np
from multiprocessing import Pool
from minatar import Environment
from dsl import load_npz

# 6 input channels <- MinAtar channel names (from each prompt's "THE INPUT" section)
CHANNEL_MAP = {
    "breakout": [["paddle"], [], ["brick"], ["ball"], ["trail"], []],
    "seaquest": [["sub_front", "sub_back"], ["enemy_fish", "enemy_sub", "enemy_bullet"],
                 ["enemy_fish", "enemy_sub", "diver"], ["friendly_bullet"], ["trail", "sub_back"],
                 ["oxygen_guage", "diver_guage"]],
    "asterix": [["player"], ["enemy"], ["gold"], [], ["trail"], []],
}
MAX_STEPS = 10_000


def make_obs_fn(env, game):
    ch = env.env.channels
    srcs = [[ch[n] for n in group] for group in CHANNEL_MAP[game]]
    def obs(env):
        s = env.state()
        o = np.zeros((10, 10, 6), np.float32)
        for k, idx in enumerate(srcs):
            if idx:
                o[:, :, k] = s[:, :, idx].any(axis=2)
        return o.reshape(600)  # index (row*10+col)*6+channel
    return obs


def forward(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    return h2 @ net["W3"] + net["b3"]


def run_chunk(args):
    npz, game, ep_ids, mode, seed = args
    net = {k: v.astype(np.float64) for k, v in load_npz(npz).items()}
    rng = np.random.RandomState(seed * 100003 + ep_ids[0])
    envs, obs_fn = [], None
    for e in ep_ids:
        env = Environment(game, sticky_action_prob=0.1)
        env.seed(seed * 1_000_003 + e)
        env.reset()
        envs.append(env)
    obs_fn = make_obs_fn(envs[0], game)
    n = len(envs)
    ret = np.zeros(n); length = np.zeros(n, int); alive = np.ones(n, bool)
    while alive.any():
        ids = np.flatnonzero(alive)
        X = np.stack([obs_fn(envs[i]) for i in ids]).astype(np.float64)
        L = forward(net, X)
        if mode == "greedy":
            acts = L.argmax(1)
        else:
            L = L - L.max(1, keepdims=True)
            P = np.exp(L); P /= P.sum(1, keepdims=True)
            u = rng.rand(len(ids), 1)
            acts = (P.cumsum(1) < u).sum(1).clip(0, 5)
        for i, a in zip(ids, acts):
            r, term = envs[i].act(int(a))
            ret[i] += r; length[i] += 1
            if term or length[i] >= MAX_STEPS:
                alive[i] = False
    return ret.tolist(), length.tolist()


def evaluate(npz, game, episodes=1000, mode="sample", procs=8, seed=0, chunk=25):
    ids = list(range(episodes))
    chunks = [(npz, game, ids[i:i + chunk], mode, seed) for i in range(0, episodes, chunk)]
    t = time.time()
    with Pool(procs) as p:
        res = p.map(run_chunk, chunks, chunksize=1)
    R = np.concatenate([r for r, _ in res]); Ln = np.concatenate([l for _, l in res])
    return {"mean": float(R.mean()), "se": float(R.std(ddof=1) / np.sqrt(len(R))), "episodes": len(R),
            "max": float(R.max()), "min": float(R.min()), "mean_length": float(Ln.mean()),
            "capped": int((Ln >= MAX_STEPS).sum()), "mode": mode, "seed": seed, "eval_s": round(time.time() - t, 1)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("npz"); ap.add_argument("game")
    ap.add_argument("--episodes", type=int, default=1000); ap.add_argument("--mode", default="sample")
    ap.add_argument("--procs", type=int, default=8); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    print(json.dumps(evaluate(a.npz, a.game, a.episodes, a.mode, a.procs, a.seed)))
