# live_view.py never appeared because the session that creates it hasn’t been freshly exported.
# Force a fresh export, then rebuild the correlation.
python3 ~/cli-synthegration/synthegration_index.py export 417ddd6d-9711-465d-ab90-c92cc04aeabf 2>&1 | tail -5