import glob, json, os
import numpy as np
ROOT = os.path.dirname(os.path.abspath(__file__))
L = str(__import__("pathlib").Path(__file__).resolve().parents[1] / "ext/lm_understand-logs/exp5_write_from_scratch")
pub = json.load(open(f"{L}/eval/minatar_eval.json"))
GAMES = ["breakout", "seaquest", "asterix"]
PPO = {"breakout": ("ppo100_s2", "ppo500_s0"), "seaquest": ("ppo100_s2", "ppo500_s2"), "asterix": ("ppo100_s6", "ppo500_s1")}
rows, out = [], {}
for tag in sorted(os.listdir(os.path.join(ROOT, "runs"))):
    for g in GAMES:
        S = [json.load(open(f)) for f in sorted(glob.glob(f"{ROOT}/runs/{tag}/{g}/r*/score.json"))]
        if not S: continue
        sm = [s["sample"]["mean"] for s in S]; gr = [s["greedy"]["mean"] for s in S]
        fail = sum(1 for s in S if not s["parsed_block"] or s["applied"] == 0)
        out[f"{tag}.{g}"] = {"sample": sm, "greedy": gr, "sample_mean": float(np.mean(sm)), "greedy_mean": float(np.mean(gr)),
            "failed": fail, "out_tokens": [(s["usage"] or {}).get("output_tokens") for s in S],
            "wall_s": [s["wall_s"] for s in S], "tool_free": [s["tool_free"] for s in S],
            "stmts": [f'{s["applied"]}/{s["statements"]}' for s in S], "nonzero": [s["nonzero_total"] for s in S],
            "cut_off": [s["cut_off"] for s in S]}
        p1, p5 = (pub[g][k]["mean"] for k in PPO[g])
        o = out[f"{tag}.{g}"]
        print(f"{tag:12s} {g:9s} sample {' '.join(f'{x:7.1f}' for x in sm)} | mean {o['sample_mean']:7.1f} || greedy {' '.join(f'{x:7.1f}' for x in gr)} | mean {o['greedy_mean']:7.1f} || PPO100 {p1:.1f} PPO500 {p5:.1f} | fail {fail} | tok {o['out_tokens']} | wall {o['wall_s']} | stmts {o['stmts']} nz {o['nonzero']} toolfree {o['tool_free']}")
json.dump(out, open(os.path.join(ROOT, "summary.json"), "w"), indent=1)
