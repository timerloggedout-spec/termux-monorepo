# 4. Restart the listener cleanly
python3 ~/archwiz/listener_control.py restart 2>/dev/null || echo "Listener control not available — starting manually"