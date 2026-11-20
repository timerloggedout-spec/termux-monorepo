# Add a --boot flag to archwiz.sh
cat > ~/archwiz/archwiz.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
export LLM_PROFILE=archwiz
if [ "$1" = "--boot" ]; then
  echo "⚡ ArchWiz Boot Sequence"
  # Rebuild indices if stale
  GRID="$HOME/workspace/llm_map/llm_index_compact.jsonl"
  if [ ! -f "$GRID" ] || [ $(($(date +%s) - $(stat -c %Y "$GRID"))) -gt 172800 ]; then
    echo "🔄 Rebuilding Grid..."
    python3 "$HOME/workspace/llm_map/build_final_all_profile.py"
    python3 "$HOME/workspace/llm_map/func_indexer.py"
    python3 "$HOME/workspace/llm_map/foresight_collect.py"
  fi
  # Launch pipeline in tmux if available
  if command -v tmux &>/dev/null; then
    tmux new-session -d -s archwiz "~/archwiz/export_poller.sh 417ddd6d-9711-465d-ab90-c92cc04aeabf 10; bash"
    tmux split-window -t archwiz "python3 ~/archwiz/activity_listener.py --session 417ddd6d-9711-465d-ab90-c92cc04aeabf --auto --max-age 99999; bash"
    tmux new-window -t archwiz "python3 ~/archwiz/archwiz.py; bash"
    tmux attach -t archwiz
  else
    python3 ~/archwiz/archwiz.py
  fi
else
  exec python3 ~/archwiz/archwiz.py
fi
EOF
chmod +x ~/archwiz/archwiz.sh