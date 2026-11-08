# agent-lab (MiniAgent)

A small but genuinely working tool-using agent, built so trajectory-eval and
redteam-scanner have a real owned target instead of fixtures.

## What it is

- `agentlab/tools.py` - real local tools: `calc` (arithmetic via ast, no
  eval), `notes` (key-value store), `clock`, and `fetch` (reads fixture pages
  from a local directory - the offline stand-in for the web).
- `agentlab/agent.py` - MiniAgent: plans with a rule engine (deterministic,
  no LLM, no API spend), calls the tools, and emits trajectories in teval's
  JSONL schema. Its safety controls are real code paths in `SafetyConfig`:
  tool-allowlist enforcement, injection refusal on tool output, canary
  suppression, system-prompt protection, PII redaction, step budget.

## The regression loop (the point of the project)

Every safety control can be flipped off, and the test suite does exactly that:

- teval grades the trajectories MiniAgent actually produces: a hardened run
  passes all six graders; flipping `suppress_canary` off makes the injection
  canary leak into the answer and the run fails.
- artscan probes MiniAgent's real behavior: the hardened agent scans clean;
  flipping each control off surfaces exactly the paired finding.

MiniAgent is deliberately a deterministic rule-based agent, not an LLM
agent: runs are reproducible and free, and the safety controls under test
are ordinary code, which is what makes the regression loop exact. An
LLM-backed brain can be plugged in later behind the same interface (that
needs API approval and spend).

`tests/test_gate_loop.py` closes the CI loop end to end: record a baseline
from the hardened agent's real runs, verify identical runs pass the gate,
verify a flipped safety control fails it naming the regressed grader
(`evil-fetch/injection_canary`), verify the revert passes.

15 tests cover the tools, the runs, each regression, and the gate loop. Stdlib only.

```bash
python3 -m unittest discover -s tests
```

## Why this exists

"Agent Red-Team Scanner" and "Trajectory Eval Harness" are only credible if
they run against a real agent. MiniAgent is that owned target today; the same
interfaces wrap any future agent we build (a Qualifier or Leash build) without
changing the graders or probes.

## Demo

`demo.py` reproduces the recorded demo run end to end, offline (standard
library only, no model calls):

    python demo.py

It executes the library's real code path and prints the same output shown in
the recorded demo video.
