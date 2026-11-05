import json
from evaluate import evaluate
L = str(__import__("pathlib").Path(__file__).resolve().parents[1] / "ext/lm_understand-logs/exp5_write_from_scratch")

def main():
    pub = json.load(open(f"{L}/eval/minatar_eval.json"))
    out = {}
    for g in ["breakout", "seaquest", "asterix"]:
        for mode in ["sample", "greedy"]:
            r = evaluate(f"{L}/networks/{g}/hand.npz", g, mode=mode)
            r["published_mean"] = pub[g]["hand"]["mean"]
            out[f"{g}.{mode}"] = r
            print(g, mode, round(r["mean"], 2), "+-", round(r["se"], 2), "len", r["mean_length"], r["eval_s"], "s; published", pub[g]["hand"]["mean"], flush=True)
            json.dump(out, open("validation_eval.json", "w"), indent=1)

if __name__ == "__main__":
    main()
