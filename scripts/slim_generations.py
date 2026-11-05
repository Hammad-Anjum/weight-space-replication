"""Write generations_slim.jsonl (every field except the full text) next to a finished Qwen eval's generations.jsonl.
The full-text files are several MB per run, so they are gitignored. Run this only on finished runs (summary.json
present).

    python scripts/slim_generations.py runs/q08_*
"""
import json
import os
import sys

for d in sys.argv[1:]:
    src, dst = os.path.join(d, "generations.jsonl"), os.path.join(d, "generations_slim.jsonl")
    if not os.path.exists(os.path.join(d, "summary.json")):
        print(f"skip {d}: not finished (no summary.json)")
        continue
    with open(src) as f, open(dst, "w") as g:
        for line in f:
            r = json.loads(line)
            r["text_chars"] = len(r.pop("text", ""))
            g.write(json.dumps(r) + "\n")
    print(f"wrote {dst}")
