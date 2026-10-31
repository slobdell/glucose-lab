#!/bin/bash
# Run the GPU smoke test in a detached screen session, logging to logs/.
# Prints the log path; `tail` it, or `screen -r smoke-test` to watch.
set -e
cd "$(dirname "$0")/.."
mkdir -p logs
LOG="logs/smoke-test-$(date +%Y%m%d-%H%M%S).log"
PY="$HOME/miniforge3/envs/research/bin/python"
screen -dmS smoke-test bash -c "'$PY' scripts/gpu_smoke_test.py > '$LOG' 2>&1"
echo "$LOG"
