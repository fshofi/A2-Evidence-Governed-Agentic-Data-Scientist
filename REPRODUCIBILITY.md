# Reproducibility

## Controls

- Source archive SHA-256: `e0bf5f5de5b846e2f18e9d90606637267d46dfa260e0f17bb12e605db5efbeb4`
- Analytical CSV SHA-256: `74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8`
- Seed: `20260913`
- Split: first 80% train, final 20% test, no shuffle
- Python used for the V1.1 reference build: 3.12.14
- Exact tested dependency versions: `requirements-lock.txt`

## Clean environment

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m unittest discover -s tests -v
python scripts/run_v1.py --offline
python dashboard/build_dashboard.py
```

The exact dependency pins reproduce the tested Python environment. They do not promise byte-identical operating-system libraries or future wheel availability. The broader `requirements.txt` remains available for compatible development installs; the lock file is the reference verification path.
