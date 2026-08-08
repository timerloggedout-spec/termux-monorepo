# Use Python as base
FROM python:3.11-slim

# Set up working directory
WORKDIR /app

# Copy application files and stub
COPY . .

# Install python dependencies and mcp
RUN pip install --no-cache-dir -e .


# Set up termux API stubs in PATH
RUN chmod +x termux-stub.py && \
    mkdir -p /opt/termux/bin && \
    for cmd in termux-battery-status termux-wifi-connectioninfo termux-wifi-scaninfo termux-telephony-deviceinfo termux-telephony-cellinfo termux-location termux-sms-list termux-sms-send termux-contact-list termux-clipboard-get termux-clipboard-set termux-notification termux-toast termux-volume termux-torch termux-vibrate termux-tts-speak termux-media-player termux-brightness termux-sensor termux-share termux-fingerprint termux-call-log termux-camera-photo termux-microphone-record; do \
        ln -s /app/termux-stub.py /opt/termux/bin/$cmd; \
    done

# Add stubs to PATH
ENV PATH="/opt/termux/bin:${PATH}"

# Run MCP server
CMD ["python", "termux_mcp_server.py"]
