import json, sys, numpy as np
from dsl import apply_edits, load_npz, net_stats
L = str(__import__("pathlib").Path(__file__).resolve().parents[1] / "ext/lm_understand-logs/exp5_write_from_scratch")
out = {}
for g in ["breakout", "seaquest", "asterix"]:
    net, rep = apply_edits(open(f"{L}/runs/{g}/reply/answer.md").read())
    ref = load_npz(f"{L}/networks/{g}/hand.npz")
    exact = all(np.array_equal(net[k], ref[k]) for k in net)
    st = net_stats(net)
    pub = json.load(open(f"{L}/runs/{g}/apply.json"))
    out[g] = {"exact_match": exact, "statements": rep["statements"], "applied": rep["applied"],
              "errors": rep["errors"], "nonzero_total": st["nonzero_total"],
              "published": [pub["edit_report"]["statements"], pub["edit_report"]["applied"], pub["nonzero_total"]],
              "entries_written": rep["entries_written"], "pub_entries": pub["edit_report"]["entries_written"]}
    print(g, out[g])
json.dump(out, open("validation_parser.json", "w"), indent=1)
