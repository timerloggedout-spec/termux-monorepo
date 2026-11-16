#!/usr/bin/env bash
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "\e[91m[ERROR]\e[0m DEEPSEEK_API_KEY is required."
    echo "export DEEPSEEK_API_KEY='your_key'"
    exit 1
fi

# If CRITIC_API_KEY is not set, reuse DEEPSEEK_API_KEY
if [ -z "$CRITIC_API_KEY" ]; then
    export CRITIC_API_KEY="$DEEPSEEK_API_KEY"
    echo -e "\e[93m[WARN]\e[0m CRITIC_API_KEY not set, using same as DEEPSEEK_API_KEY"
fi

for cmd in ast-grep tmux python; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "\e[91m[ERROR]\e[0m Required tool missing: '$cmd'"
        exit 1
    fi
done

if [ "$1" == "--clean" ]; then
    rm -f agent_telemetry_stream.json local_repo.db temp_*_run.log
fi

if [ -z "$TMUX" ]; then
    SESSION_NAME="agent_master_hub_$(date +%s)"
    tmux new-session -d -s "$SESSION_NAME" "python run.py"
    tmux split-window -h -t "$SESSION_NAME" "python dashboard.py"
    tmux attach-session -t "$SESSION_NAME"
else
    tmux split-window -h "python dashboard.py"
    python run.py
fi
