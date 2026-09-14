#!/usr/bin/env python3
"""
Utility to help extract cookies for Headless Web Backends.
"""

import sys
import json

def main():
    print("=== Cookie Extraction Helper ===")
    print("1. Open your browser and go to the chat site (e.g., grok.com or chat.mistral.ai).")
    print("2. Log in and open Developer Tools (F12).")
    print("3. Go to the Network tab and send a message.")
    print("4. Find the chat/completion request, right-click -> Copy -> Copy as cURL.")
    print("5. Paste the curl command below (or just the 'cookie:' header value):")
    
    try:
        raw_input = sys.stdin.read()
    except EOFError:
        return

    # Simple parser for curl cookie header
    cookies = {}
    if "cookie:" in raw_input.lower():
        parts = raw_input.split("'")
        for p in parts:
            if p.lower().startswith("cookie:"):
                cookie_str = p[7:].strip()
                for pair in cookie_str.split(";"):
                    if "=" in pair:
                        k, v = pair.strip().split("=", 1)
                        cookies[k] = v
                break
    
    if not cookies:
        # Try raw semicolon-separated string
        for pair in raw_input.split(";"):
            if "=" in pair:
                k, v = pair.strip().split("=", 1)
                cookies[k] = v

    if cookies:
        print("\n=== Extracted Cookies (JSON) ===")
        print(json.dumps(cookies, indent=2))
        print("\nTo use these in your Hub, save them to your session manager or set the relevant environment variables.")
    else:
        print("\n[!] Could not extract cookies. Please ensure you pasted the full curl command or the cookie header.")

if __name__ == "__main__":
    main()
