# Pane 1 (already working)
~/archwiz/export_poller.sh 417ddd6d-9711-465d-ab90-c92cc04aeabf 10

# Pane 2 (fresh listener)
python3 ~/archwiz/activity_listener.py --session 417ddd6d-9711-465d-ab90-c92cc04aeabf --clear-backlog --max-age 99999 --auto