"""Exp 5 runner: one fresh, tool-free call per (model, game, rep); parse, save, score (sampled + greedy)."""
import argparse, json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime
import numpy as np
from dsl import apply_edits, net_stats, save_npz
from evaluate import evaluate

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGS = str(__import__("pathlib").Path(__file__).resolve().parents[1] / "ext/lm_understand-logs/exp5_write_from_scratch")
INSTR = os.path.join(ROOT, "harness", "instructions.md")
SYSTEM = "Answer the user's request."
LIMIT_WORDS = ("usage limit", "rate limit", "quota", "too many requests", "429", "usage_limit")


def codex_cmd(model, out_md, effort):
    cmd = ["codex", "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--skip-git-repo-check",
           "--json", "-m", model, "-c", f'model_reasoning_effort="{effort}"', "-c", 'model_reasoning_summary="detailed"',
           "-c", f'model_instructions_file="{INSTR}"', "-o", out_md]
    for line in open(os.path.join(ROOT, "harness", "codex_flags.txt")):
        if line.strip():
            cmd += ["-c", line.strip()]
    return cmd + ["-"]


def claude_cmd(model, effort):
    return ["claude", "-p", "--tools", "", "--strict-mcp-config", "--no-session-persistence",
            "--system-prompt", SYSTEM, "--model", model, "--effort", effort, "--output-format", "json"]


def audit_codex(events_path):
    ev_types, item_types, tool_items, errors, usage, done = {}, {}, {}, [], None, False
    for line in open(events_path):
        try:
            e = json.loads(line)
        except Exception:
            continue
        t = e.get("type"); ev_types[t] = ev_types.get(t, 0) + 1
        if t in ("item.started", "item.completed", "item.updated"):
            it = e["item"]["type"]
            if t == "item.completed":
                item_types[it] = item_types.get(it, 0) + 1
            if it not in ("reasoning", "agent_message", "error"):
                tool_items[it] = tool_items.get(it, 0) + 1
            if it == "error":
                errors.append(e["item"].get("message", ""))
        if t == "turn.completed":
            usage = e.get("usage"); done = True
        if t in ("turn.failed", "error"):
            errors.append(json.dumps(e)[:500])
    return {"event_types": ev_types, "item_types": item_types, "tool_items": tool_items,
            "tool_free": not tool_items, "usage": usage, "errors": errors, "turn_completed": done}


def call(backend, model, prompt, rdir, effort):
    work = tempfile.mkdtemp(prefix="exp5_empty_")  # fresh empty cwd
    t0 = time.time()
    if backend == "codex":
        answer = os.path.join(rdir, "answer.md")
        cmd = codex_cmd(model, answer, effort)
        with open(os.path.join(rdir, "events.jsonl"), "w") as fo, open(os.path.join(rdir, "stderr.log"), "w") as fe:
            p = subprocess.run(cmd, input=prompt, text=True, stdout=fo, stderr=fe, cwd=work, timeout=7200)
        wall = time.time() - t0
        audit = audit_codex(os.path.join(rdir, "events.jsonl"))
        reply = open(answer).read() if os.path.exists(answer) else ""
        usage = audit["usage"]
    else:
        cmd = claude_cmd(model, effort)
        p = subprocess.run(cmd, input=prompt, text=True, capture_output=True, cwd=work, timeout=7200)
        wall = time.time() - t0
        open(os.path.join(rdir, "result.json"), "w").write(p.stdout)
        open(os.path.join(rdir, "stderr.log"), "w").write(p.stderr)
        try:
            j = json.loads(p.stdout)
        except Exception:
            j = {}
        reply = j.get("result", "") if not j.get("is_error") else ""
        open(os.path.join(rdir, "answer.md"), "w").write(reply)
        audit = {"tool_free": j.get("num_turns") == 1 and not j.get("permission_denials"),
                 "num_turns": j.get("num_turns"), "is_error": j.get("is_error"), "stop_reason": j.get("stop_reason"),
                 "errors": [j.get("result")] if j.get("is_error") else [], "turn_completed": not j.get("is_error")}
        usage = j.get("usage")
    leftover = os.listdir(work)
    shutil.rmtree(work, ignore_errors=True)
    stderr = open(os.path.join(rdir, "stderr.log")).read()
    blob = (stderr + " " + " ".join(map(str, audit.get("errors", [])))).lower()
    limit = (not audit.get("turn_completed")) and any(w in blob for w in LIMIT_WORDS)
    run = {"backend": backend, "model": model, "effort": effort, "rc": p.returncode, "wall_s": round(wall, 1),
           "limit": limit, "audit": audit, "usage": usage, "cwd_leftover_files": leftover,
           "cmd": cmd, "end": datetime.now().isoformat(timespec="seconds"), "stderr_tail": stderr[-2000:]}
    json.dump(run, open(os.path.join(rdir, "run.json"), "w"), indent=1)
    return reply, run


def one(backend, model, game, rep, effort, procs, tag):
    rdir = os.path.join(ROOT, "runs", tag, game, f"r{rep}")
    if os.path.exists(os.path.join(rdir, "score.json")):
        print(f"skip {rdir} (done)", flush=True); return json.load(open(os.path.join(rdir, "score.json")))
    os.makedirs(rdir, exist_ok=True)
    prompt = open(os.path.join(LOGS, "runs", game, "message.txt")).read()
    open(os.path.join(rdir, "prompt.txt"), "w").write(prompt)
    print(f"[{datetime.now():%H:%M:%S}] ask {tag} {game} r{rep}", flush=True)
    reply, run = call(backend, model, prompt, rdir, effort)
    if run["limit"]:
        print(f"LIMIT hit: {tag} {game} r{rep}: {run['audit'].get('errors')}", flush=True)
        return {"limit": True}
    net, rep_ = apply_edits(reply)
    st = net_stats(net)
    npz = os.path.join(rdir, "net.npz"); save_npz(net, npz)
    apply = {"edit_report": rep_, **st, "parameters": 20486, "tool_free": run["audit"]["tool_free"],
             "usage": run["usage"], "wall_s": run["wall_s"], "reply_chars": len(reply)}
    json.dump(apply, open(os.path.join(rdir, "apply.json"), "w"), indent=1)
    s = evaluate(npz, game, mode="sample", procs=procs)
    g = evaluate(npz, game, mode="greedy", procs=procs)
    score = {"tag": tag, "model": model, "game": game, "rep": rep, "sample": s, "greedy": g,
             "parsed_block": rep_["block"], "statements": rep_["statements"], "applied": rep_["applied"],
             "errors": len(rep_["errors"]), "cut_off": rep_["cut_off"], "nonzero_total": st["nonzero_total"],
             "tool_free": run["audit"]["tool_free"], "usage": run["usage"], "wall_s": run["wall_s"], "rc": run["rc"]}
    json.dump(score, open(os.path.join(rdir, "score.json"), "w"), indent=1)
    print(f"[{datetime.now():%H:%M:%S}] done {tag} {game} r{rep}: sample {s['mean']:.1f} greedy {g['mean']:.1f} "
          f"stmts {rep_['applied']}/{rep_['statements']} nz {st['nonzero_total']} tool_free {run['audit']['tool_free']} "
          f"wall {run['wall_s']}s usage {run['usage']}", flush=True)
    return score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="codex"); ap.add_argument("--model", required=True)
    ap.add_argument("--tag"); ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--games", default="breakout,seaquest,asterix"); ap.add_argument("--effort", default="xhigh")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    tag = a.tag or a.model
    for rep in range(1, a.n + 1):
        for game in a.games.split(","):
            r = one(a.backend, a.model, game, rep, a.effort, a.procs, tag)
            if r.get("limit"):
                print(f"STOP {tag}: usage limit", flush=True); return


if __name__ == "__main__":
    main()
