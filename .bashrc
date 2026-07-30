# Default Termux bashrc
if [ -f /data/data/com.termux/files/usr/etc/bash.bashrc ]; then
    source /data/data/com.termux/files/usr/etc/bash.bashrc
fi
alias recon='python3 ~/archwiz/recon.py'
alias recon-bridge='python3 ~/archwiz/recon_bridge.py'

# Auto-start Obsidian Bridge if not running
if ! pgrep -f "obsidian_server.py" > /dev/null; then
    mkdir -p ~/bin
    nohup python ~/bin/obsidian_server.py > ~/bin/obsidian_server.log 2>&1 &
fi
