# 3. Clear the status bar safely (no hang)
python3 -c "from pathlib import Path; Path.home().joinpath('archwiz/autoexec.log').write_text(''); print('Log cleared.')"