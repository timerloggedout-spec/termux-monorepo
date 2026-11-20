#!/data/data/com.termux/files/usr/bin/bash
# Start proxy, launch browser, capture Expert headers
node ~/cli-synthegration/http_sniffer.js 8888 &
PROXY_PID=$!
sleep 1
echo "Proxy running on :8888. Set Firefox proxy to localhost:8888, then use DeepSeek WebUI."
echo "Press Enter after you've sent an Expert message..."
read
kill $PROXY_PID
