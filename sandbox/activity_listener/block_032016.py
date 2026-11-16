# 1. Confirm the executed_messages.txt has entries
wc -l ~/archwiz/executed_messages.txt 2>/dev/null || echo "No dedup file yet"

# 2. Confirm autoexec log is clean
wc -c ~/archwiz/autoexec.log

# 3. Show the listener's last few log lines
tail -10 ~/archwiz/listener.log