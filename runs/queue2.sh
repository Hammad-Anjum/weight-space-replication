#!/bin/zsh
# Random-edit controls, 16k cap, same 100 problems. Waits for queue1 to finish.
cd "$(dirname "$0")/.."
while [ ! -f runs/q08_base_nothink/summary.json ]; do sleep 60; done
for c in rdir0 rcol0 rhead0 rhead1 ropus0 rdir1 rcol1 rhead2 rhead3 ropus1 rdir2 rcol2; do
  .venv/bin/python wsp/qeval.py --model models/qwen35-0.8b-$c --out runs/q08_${c}_16k --n 100 --max-tokens 16384
done
