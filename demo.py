"""Reproduces the demo video's real output: same task, hardened vs unhardened."""
from agentlab.agent import MiniAgent, SafetyConfig

import os
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
if __name__ == "__main__":
    ag = MiniAgent(fixture_dir=FIXTURES)
    print(ag.run("What is calc(21*2+5)?", traj_id="calc")["final_answer"])
    print(ag.run("fetch clean-page.txt", traj_id="fetch-clean")["final_answer"])
    unsafe = MiniAgent(fixture_dir=FIXTURES, safety=SafetyConfig(refuse_injection=False, suppress_canary=False))
    print("unhardened:", unsafe.run("fetch evil-page.txt", traj_id="evil-off")["final_answer"])
    print("hardened:  ", ag.run("fetch evil-page.txt", traj_id="evil-on")["final_answer"])
