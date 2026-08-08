# Use Node.js as base
FROM node:20-slim

# Install python3 so our termux-stub script can run
RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy dependency configs
COPY package.json pnpm-lock.yaml* ./

# Install dependencies using pnpm
RUN npm install -g pnpm && pnpm install --frozen-lockfile || pnpm install

# Copy application files and stub
COPY . .

# Set up termux API stubs in PATH
RUN chmod +x termux-stub.py && \
    mkdir -p /opt/termux/bin && \
    for cmd in termux-battery-status termux-wifi-connectioninfo termux-wifi-scaninfo termux-telephony-deviceinfo termux-telephony-cellinfo termux-location termux-sms-list termux-sms-send termux-contact-list termux-clipboard-get termux-clipboard-set termux-notification termux-toast termux-volume termux-torch termux-vibrate termux-tts-speak termux-media-player termux-brightness termux-sensor termux-share termux-fingerprint termux-call-log termux-camera-photo termux-microphone-record; do \
        ln -s /app/termux-stub.py /opt/termux/bin/$cmd; \
    done

# Add stubs to PATH
ENV PATH="/opt/termux/bin:${PATH}"

# Expose server port
EXPOSE 3000

# Start command
CMD ["node", "server.js"]
