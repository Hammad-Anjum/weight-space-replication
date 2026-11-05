#!/bin/zsh
# Phase 0/1 queue: 100 MATH-500 problems (fixed subset, seed 0), 1 sample each.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
$PY wsp/qeval.py --model models/qwen35-0.8b-base --out runs/q08_base_32k --n 100 --max-tokens 32768
$PY wsp/qeval.py --model models/qwen35-0.8b-p50c --out runs/q08_p50c_32k --n 100 --max-tokens 32768
# thinking OFF, Qwen's non-thinking settings (authors' nothink35 protocol: T0.7 top_p0.8 top_k20 presence1.5, 8k)
$PY wsp/qeval.py --model models/qwen35-0.8b-base --out runs/q08_base_nothink --n 100 --max-tokens 8192 --thinking 0 --temp 0.7 --top-p 0.8
