"""Finish one Claude-subject run (Claude Code subagent used as the subject, see LOG.md "Claude subjects").

    python claude_subject.py <model> <game> <rep> <subagent transcript .output (JSONL)> <staging dir> [effort, default xhigh]

1. Audits the subagent transcript: every tool_use (name + target path). Allowed: exactly one Read of the staged
   task.txt and one Write of answer.md in the staging dir. Anything else -> tool_free = False (run still scored, flagged).
2. Copies task.txt (= the verbatim authors' message.txt), answer.md and the transcript into
   runs/claude-<model>/<game>/r<rep>/, writes run.json, then scores via score_reply.py.
"""
import json
import os
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def audit(transcript, stage):
    tools, usage, models = [], {}, set()
    seen = set()
    for line in open(transcript):
        try:
            e = json.loads(line)
        except Exception:
            continue
        for o in walk(e):
            if o.get("type") == "tool_use" and o.get("id") not in seen:
                seen.add(o.get("id"))
                inp = o.get("input", {})
                tools.append({"name": o.get("name"),
                              "target": inp.get("file_path") or inp.get("command") or inp.get("pattern") or ""})
            if isinstance(o.get("model"), str) and o["model"].startswith("claude"):
                models.add(o["model"])
        m = e.get("message") if isinstance(e, dict) else None
        if isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("id") not in usage.setdefault("_ids", []):
            usage["_ids"].append(m.get("id"))   # one count per API message (the transcript repeats usage per block)
            usage["output_tokens"] = usage.get("output_tokens", 0) + int(m["usage"].get("output_tokens") or 0)
    usage.pop("_ids", None)
    allowed = [("Read", os.path.join(stage, "task.txt")), ("Write", os.path.join(stage, "answer.md"))]
    got = [(t["name"], t["target"]) for t in tools if t["name"] != "SubagentHandback"]  # harness return step
    ok = sorted(got) == sorted(allowed)
    return {"tool_calls": tools, "tool_free": ok, "allowed": allowed, "models_seen": sorted(models)}, usage


def main(model, game, rep, transcript, stage, effort="xhigh"):
    tag = f"claude-{model}" if effort == "xhigh" else f"claude-{model}-{effort}"
    rdir = os.path.join(ROOT, "runs", tag, game, f"r{rep}")
    os.makedirs(rdir, exist_ok=True)
    shutil.copy(os.path.join(stage, "task.txt"), os.path.join(rdir, "prompt.txt"))
    ans = os.path.join(stage, "answer.md")
    if os.path.exists(ans):
        shutil.copy(ans, os.path.join(rdir, "answer.md"))
    else:
        open(os.path.join(rdir, "answer.md"), "w").write("")
    shutil.copy(transcript, os.path.join(rdir, "subagent_transcript.jsonl"))
    au, usage = audit(transcript, stage)
    run = {"backend": "claude-code-subagent", "tag": tag, "model": model, "rep": int(rep), "game": game,
           "effort": effort, "audit": au, "usage": usage, "wall_s": None,
           "end": datetime.now().isoformat(timespec="seconds"),
           "deviations": ["Claude Code subagent system prompt instead of 'Answer the user's request.'",
                          "task delivered via one Read of a staged copy of message.txt; reply saved via one Write",
                          f"reasoning effort via Agent tool effort={effort}"]}
    json.dump(run, open(os.path.join(rdir, "run.json"), "w"), indent=1)
    print("audit:", json.dumps({k: au[k] for k in ("tool_free", "models_seen")}), [t["name"] for t in au["tool_calls"]])
    sys.argv = ["score_reply.py", rdir, game]
    from score_reply import main as score
    score(rdir, game)


if __name__ == "__main__":
    main(*sys.argv[1:7])
