# How it works

An iPhone cannot be a Termux host. This project does not pretend otherwise.
Termux is Android-only: there is no Termux for iOS, an iPhone cannot install
a Termux APK / .deb, and no jailbreak is offered or required.

It splits the job the way it actually works:

- **Cockpit (the iPhone):** iSH / a-Shell for local shell work with
  translated commands, Blink Shell / Termius as ssh clients, Safari/Chrome
  for cloud consoles, and Files for moving projects.
- **Real Termux (the Android device):** Termux itself, with sshd on port
  8022. The iPhone ssh-es in over the same LAN or Tailscale and gets the
  genuine Termux: real `pkg`, real `$PREFIX`, real paths.
- **Cloud-Termux (no Android at hand):** a cloud Linux box (GitHub
  Codespaces from the phone browser) with a pkg-like wrapper over apt, so
  the workflow feels Termux-style even though it is plain Linux underneath.
- **Translate route:** Termux commands and paths map to iSH (Alpine)
  equivalents — `pkg install` -> `apk add`, clipboard/tts/open helpers —
  and Termux-only tools honestly map to *no equivalent*, never a fake one.
- **Transfer route:** iOS Files -> the shared Download folder -> Termux
  `~/storage/downloads` (after `termux-setup-storage` + Allow). Not
  `~/downloads`: that is Termux's private folder, invisible to iOS Files.
  Archives must be extracted before Python can use the files.
- **Brain (this repo):** Gemini Carbon 4 Extended Thinking runs
  MAP -> MODEL -> STRESS -> DECIDE over every action. The HOLD gates in
  `brains.py` are authoritative — Carbon 4 and every freeai advisor can
  only tighten a verdict, never override a HOLD.

## The recommended route, end to end

1. Android device: open Termux, run `pkg install openssh`, `sshd`
   (or just run the generated `setup-termux.sh`)
2. In Termux: `whoami` and `ip addr` — note the username and IP
3. iPhone: open iSH / Blink / Termius
4. `ssh -p 8022 <user>@<host>` — you are inside real Termux
5. Across networks: put both devices on Tailscale and ssh to the
   Tailscale address instead
