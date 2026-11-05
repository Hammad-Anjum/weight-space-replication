"""Score an already-saved reply (used for the Claude subjects, which are run as fresh Claude Code subagents instead of
`claude -p`, because headless `claude -p` auth was unavailable on 2026-11-05).

    python score_reply.py <run dir containing answer.md and run.json> <game>

Writes apply.json, net.npz, score.json in the same format as runner.py.
"""
import json
import os
import sys

from dsl import apply_edits, net_stats, save_npz
from evaluate import evaluate


def main(rdir, game, procs=4):
    reply = open(os.path.join(rdir, "answer.md")).read()
    run = json.load(open(os.path.join(rdir, "run.json")))
    net, rep_ = apply_edits(reply)
    st = net_stats(net)
    npz = os.path.join(rdir, "net.npz")
    save_npz(net, npz)
    apply = {"edit_report": rep_, **st, "parameters": 20486, "tool_free": run["audit"]["tool_free"],
             "usage": run.get("usage"), "wall_s": run.get("wall_s"), "reply_chars": len(reply)}
    json.dump(apply, open(os.path.join(rdir, "apply.json"), "w"), indent=1)
    s = evaluate(npz, game, mode="sample", procs=procs)
    g = evaluate(npz, game, mode="greedy", procs=procs)
    score = {"tag": run["tag"], "model": run["model"], "game": game, "rep": run["rep"], "sample": s, "greedy": g,
             "parsed_block": rep_["block"], "statements": rep_["statements"], "applied": rep_["applied"],
             "errors": len(rep_["errors"]), "cut_off": rep_["cut_off"], "nonzero_total": st["nonzero_total"],
             "tool_free": run["audit"]["tool_free"], "usage": run.get("usage"), "wall_s": run.get("wall_s"), "rc": 0}
    json.dump(score, open(os.path.join(rdir, "score.json"), "w"), indent=1)
    print(f"{run['tag']} {game} r{run['rep']}: sample {s['mean']:.1f} greedy {g['mean']:.1f} "
          f"stmts {rep_['applied']}/{rep_['statements']} nz {st['nonzero_total']} tool_free {run['audit']['tool_free']}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
