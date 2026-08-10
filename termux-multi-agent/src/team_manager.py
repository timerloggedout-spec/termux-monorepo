import os
import json
import random
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path

ROSTER_PATH = Path("termux-multi-agent/workspace/roster.json")

@dataclass
class AgentCandidate:
    id: str
    name: str
    role: str  # e.g., "CTO", "CFO", "Engineer", "Researcher", "l337 4@xπ$", "Script Kiddies"
    elo: float = 1200.0
    skills: List[str] = field(default_factory=list)
    wallet: float = 100.0  # internal points
    successes: int = 0
    failures: int = 0
    is_active: bool = True
    parent_id: Optional[str] = None
    mutation_count: int = 0
    tools: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "AgentCandidate":
        return cls(**d)

class TeamRoster:
    def __init__(self, filepath: Path = ROSTER_PATH):
        self.filepath = Path(filepath)
        self.candidates: Dict[str, AgentCandidate] = {}
        self.load()

    def load(self):
        """Loads candidates from JSON, or initializes with default populated roster."""
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.candidates = {
                        cid: AgentCandidate.from_dict(c)
                        for cid, c in data.items()
                    }
                return
            except Exception as e:
                # Fall back to initializing if there's any parsing issue
                pass
        self._initialize_default_roster()
        self.save()

    def save(self):
        """Saves current candidates to JSON."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        data = {cid: c.to_dict() for cid, c in self.candidates.items()}
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _initialize_default_roster(self):
        """Seeds the roster with a complete team hierarchy of potential candidates."""
        defaults = [
            # CTO / CFO (meh)
            AgentCandidate(
                id="cto-meh",
                name="CTO (meh)",
                role="CTO",
                elo=1050.0,
                skills=["delegation", "high-level-design", "meetings"],
                wallet=50.0,
                tools=["powerpoint", "email-connector"]
            ),
            AgentCandidate(
                id="cfo-meh",
                name="CFO (meh)",
                role="CFO",
                elo=1020.0,
                skills=["budgeting", "cost-cutting", "spreadsheets"],
                wallet=50.0,
                tools=["excel-sheet", "accounting-plugin"]
            ),
            # Engineers
            AgentCandidate(
                id="engine-bolt",
                name="Bolt (Perf Optimizer)",
                role="Engineer",
                elo=1280.0,
                skills=["profiling", "performance-optimization", "sqlite", "python"],
                wallet=150.0,
                tools=["pytest", "ast-grep", "cprofile"]
            ),
            AgentCandidate(
                id="engine-jules",
                name="Jules (Core Dev)",
                role="Engineer",
                elo=1260.0,
                skills=["system-architecture", "refactoring", "git-flow", "python"],
                wallet=120.0,
                tools=["git", "ast-grep", "bash-terminal"]
            ),
            AgentCandidate(
                id="engine-palette",
                name="Palette (UX Designer)",
                role="Engineer",
                elo=1180.0,
                skills=["accessibility", "frontend-reactivity", "ui-layout", "css"],
                wallet=100.0,
                tools=["playwright", "esbuild", "lit-html"]
            ),
            # Researchers
            AgentCandidate(
                id="research-curie",
                name="Curie (Tech Lead)",
                role="Researcher",
                elo=1240.0,
                skills=["feasibility-analysis", "emerging-tech", "whitepapers"],
                wallet=110.0,
                tools=["arxiv-search", "llm-probe"]
            ),
            AgentCandidate(
                id="research-scout",
                name="Scout (Trend Finder)",
                role="Researcher",
                elo=1150.0,
                skills=["competitor-analysis", "github-crawler", "benchmarking"],
                wallet=100.0,
                tools=["google-search-api", "github-api"]
            ),
            # l337 4@xπ$
            AgentCandidate(
                id="hax-zero",
                name="Zero (Sentinel Sec)",
                role="l337 4@xπ$",
                elo=1300.0,
                skills=["privilege-restriction", "exploit-mitigation", "security-audit"],
                wallet=200.0,
                tools=["static-analyzer", "permission-checker"]
            ),
            AgentCandidate(
                id="hax-neo",
                name="Neo (Symbolic King)",
                role="l337 4@xπ$",
                elo=1270.0,
                skills=["agentic-compression", "1337speak-compiler", "regex-master"],
                wallet=180.0,
                tools=["cedrlang-compiler", "symbolic-encoder"]
            ),
            # Script Kiddies
            AgentCandidate(
                id="kiddie-copy",
                name="CopyPaste Kiddie",
                role="Script Kiddies",
                elo=950.0,
                skills=["stackoverflow-scraping", "brute-force", "script-running"],
                wallet=30.0,
                tools=["curl", "sed-awk"]
            ),
            AgentCandidate(
                id="kiddie-paste",
                name="Github Scraper Kiddie",
                role="Script Kiddies",
                elo=980.0,
                skills=["forking-repos", "quick-fixes", "vibe-coding"],
                wallet=40.0,
                tools=["git-clone", "copilot-api"]
            )
        ]
        for candidate in defaults:
            self.candidates[candidate.id] = candidate

    def get_active_team(self) -> List[AgentCandidate]:
        return [c for c in self.candidates.values() if c.is_active]

    def get_all_candidates(self) -> List[AgentCandidate]:
        return list(self.candidates.values())

    def update_agent_performance(self, agent_id: str, success: bool, elo_delta: float):
        if agent_id in self.candidates:
            agent = self.candidates[agent_id]
            if success:
                agent.successes += 1
                agent.elo += elo_delta
                agent.wallet += 15.0  # success payout
            else:
                agent.failures += 1
                agent.elo = max(800.0, agent.elo + elo_delta)
                agent.wallet = max(0.0, agent.wallet - 10.0)  # failure penalty
            self.save()


class MoneyBallScout:
    """Evaluates agent roster and uses MoneyBall analytics to optimize the team."""

    def __init__(self, roster: TeamRoster):
        self.roster = roster

    def rotate_and_cull(self, bottom_pct: float = 0.20, top_pct: float = 0.20) -> Tuple[List[str], List[str]]:
        """
        MoneyBall draft:
        - Sort active team by performance (ELO & successes).
        - Deactivate/Cull the bottom % (removed from participation but kept for passive learning).
        - Clone the top % with random parameter mutations/modifications.
        """
        active_agents = self.roster.get_active_team()
        if len(active_agents) < 4:
            # Not enough agents to safely cull/clone without depleting workforce
            return [], []

        # Sort by ELO descending
        active_agents.sort(key=lambda a: a.elo, reverse=True)
        count = len(active_agents)

        cull_count = max(1, int(count * bottom_pct))
        clone_count = max(1, int(count * top_pct))

        # Bottom tier to cull (excluding critical managers if desired, but we follow raw stats here)
        bottom_tier = active_agents[-cull_count:]
        culled_ids = []
        for agent in bottom_tier:
            agent.is_active = False
            culled_ids.append(agent.id)

        # Top tier to clone
        top_tier = active_agents[:clone_count]
        cloned_ids = []
        for agent in top_tier:
            clone = self._clone_and_mutate(agent)
            self.roster.candidates[clone.id] = clone
            cloned_ids.append(clone.id)

        self.roster.save()
        return culled_ids, cloned_ids

    def _clone_and_mutate(self, parent: AgentCandidate) -> AgentCandidate:
        """Clones a top agent with mutated attributes (% rnd modifications)."""
        mutation_count = parent.mutation_count + 1
        new_id = f"{parent.id}-clone-v{mutation_count}"

        # Mutate ELO with a random drift around parent's level
        elo_drift = random.uniform(-40.0, 40.0)
        new_elo = max(900.0, parent.elo + elo_drift)

        # Mutate skills: copy and randomly swap/add one
        new_skills = list(parent.skills)
        mutation_pool = ["rust", "javascript", "ast-grep", "testing", "security", "performance", "cedrlang", "shell-scripting", "debugging"]
        potential_new_skills = [s for s in mutation_pool if s not in new_skills]
        if potential_new_skills and random.random() < 0.5:
            # Add a new skill
            new_skills.append(random.choice(potential_new_skills))
        elif len(new_skills) > 1 and random.random() < 0.3:
            # Replace one skill
            idx_to_replace = random.randint(0, len(new_skills) - 1)
            if potential_new_skills:
                new_skills[idx_to_replace] = random.choice(potential_new_skills)

        # Keep parent's tools but maybe add one randomly
        new_tools = list(parent.tools)
        tool_pool = ["playwright", "esbuild", "ast-grep", "cprofile", "pytest", "jq", "curl"]
        potential_tools = [t for t in tool_pool if t not in new_tools]
        if potential_tools and random.random() < 0.4:
            new_tools.append(random.choice(potential_tools))

        # Cloned agent starts fresh with active status and standard starting wallet
        return AgentCandidate(
            id=new_id,
            name=f"Modified Clone of {parent.name} (v{mutation_count})",
            role=parent.role,
            elo=new_elo,
            skills=new_skills,
            wallet=100.0,
            successes=0,
            failures=0,
            is_active=True,
            parent_id=parent.id,
            mutation_count=mutation_count,
            tools=new_tools
        )

    def evaluate_role_necessity(self, failed_tasks: List[Dict]) -> Optional[str]:
        """
        Dynamically detects if a specific capability/role is lacking based on failure history
        and hires/crafts a specialized agent.
        """
        if not failed_tasks:
            return None

        # Categorize failures by task/topic keyword
        failures_by_topic = {"security": 0, "performance": 0, "testing": 0, "compilation": 0}
        for task in failed_tasks:
            instruction = task.get("instructions", "").lower()
            errors = task.get("error", "").lower()
            combined = f"{instruction} {errors}"
            if "security" in combined or "privilege" in combined or "secure" in combined:
                failures_by_topic["security"] += 1
            if "perf" in combined or "optimize" in combined or "slow" in combined:
                failures_by_topic["performance"] += 1
            if "test" in combined or "assert" in combined:
                failures_by_topic["testing"] += 1
            if "compile" in combined or "syntax" in combined or "error" in combined:
                failures_by_topic["compilation"] += 1

        # Find most frequent failure topic
        most_frequent_failure = max(failures_by_topic, key=failures_by_topic.get)
        if failures_by_topic[most_frequent_failure] >= 2:
            # Create a new specialized agent to fill the gap
            specialist_id = f"specialist-{most_frequent_failure}-{int(time.time()) % 1000}"
            role_map = {
                "security": ("Security Specialist", "l337 4@xπ$", ["security-audit", "encryption", "privilege-restriction"]),
                "performance": ("Performance Alchemist", "Engineer", ["profiling", "performance-optimization", "concurrency"]),
                "testing": ("QA Automation Expert", "Engineer", ["pytest", "playwright", "test-coverage"]),
                "compilation": ("Syntax Fixer", "Script Kiddies", ["compilation-fixing", "auto-repair", "quick-fixes"])
            }
            name, role, skills = role_map.get(most_frequent_failure, ("General Specialist", "Engineer", ["general"]))

            new_specialist = AgentCandidate(
                id=specialist_id,
                name=name,
                role=role,
                elo=1220.0,
                skills=skills,
                wallet=120.0,
                tools=["ast-grep", "pytest"]
            )
            self.roster.candidates[specialist_id] = new_specialist
            self.roster.save()
            return specialist_id
        return None


class BettingArena:
    """Simulates job betting, bidding, and PolyMarket-style spectator betting on outcomes."""

    def __init__(self, roster: TeamRoster):
        self.roster = roster
        self.active_bids: Dict[str, Dict] = {}  # task_id -> { "agent_id": str, "amount": float }
        self.spectator_bets: Dict[str, List[Dict]] = {}  # task_id -> list of { "spectator_id": str, "outcome": str, "amount": float }

    def place_bid(self, agent_id: str, task_id: str, amount: float) -> bool:
        """An agent bids to take a job from the master tasks list."""
        if agent_id not in self.roster.candidates:
            return False
        agent = self.roster.candidates[agent_id]
        if not agent.is_active or agent.wallet < amount:
            return False

        agent.wallet -= amount
        self.active_bids[task_id] = {"agent_id": agent_id, "amount": amount}
        self.roster.save()
        return True

    def place_spectator_bet(self, spectator_id: str, task_id: str, outcome: str, amount: float) -> bool:
        """Spectator agents place bets on task outcome: 'success' or 'failure'."""
        if spectator_id not in self.roster.candidates:
            return False
        spectator = self.roster.candidates[spectator_id]
        if spectator.wallet < amount or outcome not in ["success", "failure"]:
            return False

        spectator.wallet -= amount
        if task_id not in self.spectator_bets:
            self.spectator_bets[task_id] = []
        self.spectator_bets[task_id].append({
            "spectator_id": spectator_id,
            "outcome": outcome,
            "amount": amount
        })
        self.roster.save()
        return True

    def resolve_bets(self, task_id: str, verdict: str) -> Dict:
        """
        Resolves bids and spectator bets based on task verdict.
        Returns a breakdown of payouts.
        """
        verdict = verdict.lower()
        if verdict in ["pass", "success"]:
            resolved_outcome = "success"
        else:
            resolved_outcome = "failure"

        payouts = {"agent_payouts": {}, "spectator_payouts": {}}

        # 1. Resolve bidding agent payout
        bid_info = self.active_bids.pop(task_id, None)
        if bid_info:
            agent_id = bid_info["agent_id"]
            amount = bid_info["amount"]
            agent = self.roster.candidates.get(agent_id)
            if agent:
                if resolved_outcome == "success":
                    # Successful job: retrieve bid + 1.5x bonus reward
                    payout_amount = amount + (amount * 1.5)
                    agent.wallet += payout_amount
                    payouts["agent_payouts"][agent_id] = payout_amount
                    agent.successes += 1
                else:
                    # Failed job: lose bid
                    payouts["agent_payouts"][agent_id] = 0.0
                    agent.failures += 1

        # 2. Resolve spectator bets (Polymarket style)
        bets = self.spectator_bets.pop(task_id, [])
        if bets:
            total_pool = sum(b["amount"] for b in bets)
            winning_bets = [b for b in bets if b["outcome"] == resolved_outcome]
            total_winning_amount = sum(b["amount"] for b in winning_bets)

            if total_winning_amount > 0:
                for bet in winning_bets:
                    spec_id = bet["spectator_id"]
                    spec_amount = bet["amount"]
                    # Proportional share of the total pool
                    share = spec_amount / total_winning_amount
                    payout = share * total_pool
                    spectator = self.roster.candidates.get(spec_id)
                    if spectator:
                        spectator.wallet += payout
                        payouts["spectator_payouts"][spec_id] = payout
            else:
                # No winning bets: the pool is burnt or returned to a general system treasury
                pass

        self.roster.save()
        return payouts
