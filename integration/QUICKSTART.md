# Connected local-tool demo

This demo connects local MiniAgent execution, trajectory evaluation, a regression gate and synthetic-feedback dataset promotion. It needs Python 3.10 or newer and no model credentials or paid services.

## Source layout

Place these repositories side by side:

- agent-lab: this candidate branch;
- trajectory-eval: commit `63dd422bfbdeebff6fbc5fb5dbe73f235ee5919e`;
- data-flywheel: commit `265694496e5fdaa30197c463ed7448b2252a5269`;
- redteam-scanner: commit `865b9c1799e844d378280ade6b86996bbec03883`.

From the directory containing those repositories, apply the two included sibling patches to clean copies of their pinned sources:

```sh
git -C trajectory-eval apply ../agent-lab/integration/patches/trajectory-eval.patch
git -C data-flywheel apply ../agent-lab/integration/patches/data-flywheel.patch
export PYTHONPATH="$PWD/agent-lab:$PWD/trajectory-eval:$PWD/data-flywheel:$PWD/redteam-scanner"
python -m unittest discover -s trajectory-eval/tests -v
python -m unittest discover -s data-flywheel/tests -v
python -m unittest discover -s agent-lab/tests -v
python -m unittest discover -s agent-lab/integration -v
python agent-lab/connected_loop.py --output demo-output
```

The output directory must not already exist. Applying these patches changes only your local sibling copies. Review the patches before applying them. They are not changes already released by the sibling repositories.

The output includes actual local-tool traces, baseline scores, a synthetic-feedback pool, a golden dataset and `proof.json`. The proof checks the canary negative control, restored control, missing-case rejection, two accepted candidates, one rejected candidate and byte-identical golden output on promotion rerun.

Fresh local verification on Linux/Python 3.10.12 passed 83 test methods: 41 trajectory-eval, 19 data-flywheel, 15 agent-lab and 8 connected integration. This is author verification, not independent QA or a remote CI result.

This is a deterministic rule-engine demonstration, not an LLM benchmark, production adapter, security certification, human-feedback dataset or training result. Promotion is single-writer only, with no lock, automatic retraction, dataset history or containing-directory power-loss guarantee. Existing IDs skip rather than update. Keep using the explicit evaluation policy when consuming promoted data. The full redteam-scanner suite is excluded from the test total.
