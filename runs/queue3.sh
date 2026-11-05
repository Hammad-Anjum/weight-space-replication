#!/bin/zsh
# Resumable queue (replaces queue1/queue2 after the Metal buffer-limit crashes, 2026-11-05).
# Each eval is retried (resuming from generations.jsonl) until it has all generations; crashes are logged.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
run() {  # out_dir n args...
  local out=$1 n=$2; shift 2
  for try in 1 2 3 4 5 6; do
    $PY wsp/qeval.py --out $out --n $n "$@" && return 0
    echo "CRASH: $out try $try ($(wc -l < $out/generations.jsonl 2>/dev/null) done) $(date +%H:%M)" | tee -a runs/crashes.log
  done
}
while pgrep -f "q08_base_nothink" >/dev/null; do sleep 30; done   # let the running thinking-off eval finish
run runs/q08_base_32k 100 --model models/qwen35-0.8b-base --max-tokens 32768
run runs/q08_p50c_32k 100 --model models/qwen35-0.8b-p50c --max-tokens 32768
for c in rdir0 rcol0 rhead0 rhead1 ropus0 rdir1 rcol1 rhead2 rhead3 ropus1 rdir2 rcol2; do
  run runs/q08_${c}_16k 100 --model models/qwen35-0.8b-$c --max-tokens 16384
done
