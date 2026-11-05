#!/bin/zsh
# Finish a Claude-subject run by its transcript id: audit + copy + score, then mark it scored in claude_runs.tsv.
cd "$(dirname "$0")"
row=$(grep "$1.output" claude_runs.tsv) || { echo "no row for $1"; exit 1; }
IFS=$'\t' read -r model game rep effort transcript stage st <<< "$row"
../.venv/bin/python claude_subject.py $model $game $rep $transcript $stage $effort && \
  sed -i '' "/$1.output/s/	running$/	scored/" claude_runs.tsv
