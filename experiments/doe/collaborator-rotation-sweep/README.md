# collaborator-rotation-sweep

Pre-registered replay campaign for collaborator filename rotation and reference mapping. It compares five independent classifier families over a 2^5 full factorial (31 non-empty arms): path, lexical, Markdown-link, workflow-context, and semantic-context. Identity/moniker collision checks remain a hard invariant.

The workflow emits an immutable EXPERIMENT record tied to the base and candidate SHAs, alongside a detailed report. The campaign does not edit collaborator identities, rewrite routes, or promote mappings automatically. Promotion remains a reviewed PR after classifier evidence and the repository/Termux gates pass on one head SHA.

Run locally:

```sh
python3 -B -m unittest discover -s tests -p 'test_rotation_sweep.py' -v
python3 scripts/identity/rotation_sweep.py --base-sha <40-hex> --candidate-sha <40-hex> --report rotation-sweep-report.json --record rotation-sweep-experiment.json
```

See DESIGN.json for factors, responses, stopping rules, and promotion criteria.
