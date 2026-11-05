#!/bin/zsh
# Time-boxed (~1 h) Qwen queue, 2026-11-05: thinking ON, 16k cap, first 50 problems of the fixed subset.
#   1. p50c (Astra's released edit): does it reproduce locally?
#   2. rdir0 (p50c's columns/norm, random written direction): is it the direction, or any edit of that size?
#   3. base (optional, if time remains): same-cap reference.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
run() { local out=$1; shift; for try in 1 2 3; do $PY wsp/qeval.py --out $out --n 50 --max-tokens 16384 "$@" && return 0; echo "CRASH: $out try $try $(date +%H:%M)" | tee -a runs/crashes.log; done; }
run runs/q08_p50c_16k_n50  --model models/qwen35-0.8b-p50c
run runs/q08_rdir0_16k_n50 --model models/qwen35-0.8b-rdir0
run runs/q08_base_16k_n50  --model models/qwen35-0.8b-base
