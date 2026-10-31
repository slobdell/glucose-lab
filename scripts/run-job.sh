#!/bin/bash
# Run any command in a detached screen session named after the job, logging to logs/.
#   scripts/run-job.sh <job-name> <command...>
# Watch: tail -f <printed log>, or screen -r <job-name>. Python uses the research env.
set -e
[ $# -ge 2 ] || { echo "usage: $0 <job-name> <command...>"; exit 1; }
cd "$(dirname "$0")/.."
NAME=$1; shift
mkdir -p logs
LOG="logs/$NAME-$(date +%Y%m%d-%H%M%S).log"
export PATH="$HOME/miniforge3/envs/research/bin:$PATH"
screen -dmS "$NAME" bash -c "$(printf '%q ' "$@") > '$LOG' 2>&1; echo \"[exit \$?]\" >> '$LOG'"
echo "$LOG"
