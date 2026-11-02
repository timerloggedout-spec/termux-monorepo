#!/bin/bash
# Unit 063 verification: structure stories, then full games driven by a
# binary-search player (new user, non-integer handling, returning-user stats).
set -e
cd "$(dirname "$0")"

psql -d number_guess -v ON_ERROR_STOP=1 -f verify.sql

python3 - <<'PYEOF'
import re, subprocess, sys

def play(username, junk_first=False):
    p = subprocess.Popen(["./number_guess.sh"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, text=True, bufsize=1)
    def send(s):
        p.stdin.write(str(s) + "\n"); p.stdin.flush()
    def readline():
        line = p.stdout.readline()
        if not line:
            raise RuntimeError("script ended unexpectedly")
        return line.rstrip("\n")
    out = []
    line = readline(); out.append(line)
    assert line == "Enter your username:", repr(line)
    send(username)
    welcome = readline(); out.append(welcome)
    prompt = readline(); out.append(prompt)
    assert prompt == "Guess the secret number between 1 and 1000:", repr(prompt)
    lo, hi, tries, sent_junk = 1, 1000, 0, False
    while True:
        if junk_first and not sent_junk:
            send("abc"); sent_junk = True
            line = readline(); out.append(line)
            assert line == "That is not an integer, guess again:", repr(line)
        guess = (lo + hi) // 2
        send(guess); tries += 1
        line = readline(); out.append(line)
        if line.startswith("You guessed it in"):
            m = re.fullmatch(r"You guessed it in (\d+) tries\. The secret number was (\d+)\. Nice job!", line)
            assert m, repr(line)
            assert int(m.group(1)) == tries, (m.group(1), tries)
            assert lo <= int(m.group(2)) <= hi
            break
        elif line == "It's higher than that, guess again:":
            lo = guess + 1
        elif line == "It's lower than that, guess again:":
            hi = guess - 1
        else:
            raise RuntimeError("unexpected line: " + repr(line))
    p.wait(timeout=10)
    return welcome, tries

# Game 1: brand-new user, with a non-integer guess first
w1, t1 = play("fleet_tester", junk_first=True)
assert w1 == "Welcome, fleet_tester! It looks like this is your first time here.", repr(w1)
print(f"game 1 OK ({t1} tries)")

# Game 2: same user plays again
w2, t2 = play("fleet_tester")
assert w2 == f"Welcome back, fleet_tester! You have played 1 games, and your best game took {t1} guesses.", repr(w2)
print(f"game 2 OK ({t2} tries)")

# Third entry: welcome-back stats must reflect both finished games
w3proc = subprocess.Popen(["./number_guess.sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
w3proc.stdin.write("fleet_tester\n"); w3proc.stdin.flush()
w3proc.stdout.readline()
w3 = w3proc.stdout.readline().rstrip("\n")
best = min(t1, t2)
assert w3 == f"Welcome back, fleet_tester! You have played 2 games, and your best game took {best} guesses.", repr(w3)
w3proc.kill()
print("welcome-back stats OK")
PYEOF

n=$(psql -d number_guess -t --no-align -c "SELECT count(*) FROM games g JOIN users u ON u.user_id=g.user_id WHERE u.username='fleet_tester'")
echo "games recorded for fleet_tester: $n"
[ "$n" = "2" ] || { echo "GAME ROWS FAIL"; exit 1; }

[ -x files/number_guess.sh ] || { echo "deliverable number_guess.sh not executable"; exit 1; }
grep -q "RANDOM" files/number_guess.sh || { echo "RANDOM missing from script"; exit 1; }
echo "VERIFY DONE"
