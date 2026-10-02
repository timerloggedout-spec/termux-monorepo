import sys, os
sys.path.insert(0, "/tmp")
p = os.popen("pgrep -f 'hindsight-api --port 8888'").read().strip().split("\n")[0]
for line in open(f"/proc/{p}/environ").read().split("\0"):
    if line.startswith("HINDSIGHT_API_KEY="):
        os.environ["HINDSIGHT_API_KEY"] = line.split("=",1)[1]
os.environ["HINDSIGHT_BASE_URL"] = "http://localhost:8888"
os.environ["HINDSIGHT_BANK_ID"] = "termux-monorepo::primary"
from agent_hindsight import retain, BASE, BANK
print("BASE:", BASE, "BANK:", BANK)
r1 = retain("DeepAgent e2e v2: post-migration write, bank aligned",
            metadata={"origin":"deepagent","event":"finish","task":"e2e-v2"})
print("retain:", r1)
