#!/usr/bin/env python3
import sys
import json
import os

cmd = os.path.basename(sys.argv[0])

mocks = {
    "termux-battery-status": {
        "health": "GOOD",
        "percentage": 85,
        "plugged": "PLUGGED_AC",
        "status": "CHARGING",
        "temperature": 29.5
    },
    "termux-wifi-connectioninfo": {
        "bssid": "00:11:22:33:44:55",
        "frequency_mhz": 5240,
        "ip": "192.168.1.105",
        "link_speed_mbps": 866,
        "mac_address": "66:77:88:99:aa:bb",
        "network_id": 1,
        "rssi": -45,
        "ssid": "Home_WiFi"
    },
    "termux-wifi-scaninfo": [
        {
            "bssid": "00:11:22:33:44:55",
            "frequency_mhz": 5240,
            "rssi": -45,
            "ssid": "Home_WiFi"
        }
    ],
    "termux-telephony-deviceinfo": {
        "device_id": "123456789012345",
        "device_software_version": "01",
        "network_operator": "Mock Telecom",
        "network_operator_name": "MockTelecom",
        "phone_type": "GSM",
        "sim_operator": "46001",
        "sim_operator_name": "MockTelecom",
        "sim_serial_number": "898601234567890",
        "sim_state": "READY"
    },
    "termux-telephony-cellinfo": [
        {
            "type": "lte",
            "registered": True,
            "mcc": 310,
            "mnc": 260,
            "ci": 12345,
            "pci": 300,
            "tac": 54321,
            "earfcn": 600,
            "dbm": -90
        }
    ],
    "termux-location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "altitude": 10.0,
        "accuracy": 5.0,
        "vertical_accuracy": 5.0,
        "bearing": 0.0,
        "speed": 0.0,
        "elapsedMs": 0,
        "provider": "gps"
    },
    "termux-sms-list": [
        {
            "id": "1",
            "sender": "+15551234567",
            "body": "Hello from mock Termux SMS!",
            "received": "2026-08-08 12:00:00"
        }
    ],
    "termux-sms-send": "SMS sent successfully.",
    "termux-contact-list": [
        {
            "name": "John Doe",
            "number": "+15551234567"
        }
    ],
    "termux-clipboard-get": "Mock Clipboard Content",
    "termux-clipboard-set": "Clipboard set successfully.",
    "termux-notification": "Notification sent successfully.",
    "termux-toast": "Toast shown.",
    "termux-volume": {
        "stream": "music",
        "volume": 8,
        "max_volume": 15
    },
    "termux-torch": "Torch toggled.",
    "termux-vibrate": "Vibration triggered.",
    "termux-tts-speak": "Spoken: Hello",
    "termux-media-player": "Media playback updated.",
    "termux-brightness": "Brightness set.",
    "termux-sensor": {
        "sensor": "accelerometer",
        "values": [0.1, 0.2, 9.8]
    },
    "termux-share": "Shared file successfully.",
    "termux-fingerprint": {
        "auth_result": "AUTH_RESULT_SUCCESS"
    },
    "termux-call-log": [
        {
            "name": "Jane Smith",
            "phone_number": "+15559876543",
            "type": "INCOMING",
            "date": "2026-08-08 11:30:00",
            "duration": "120"
        }
    ],
    "termux-camera-photo": "Photo taken.",
    "termux-microphone-record": "Audio recorded."
}

val = mocks.get(cmd, f"Mock output for {cmd}")
if isinstance(val, (dict, list)):
    print(json.dumps(val))
else:
    print(val)
