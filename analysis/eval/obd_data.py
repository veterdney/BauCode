"""Shared loading of the Ökobaudat export for the eval scripts."""
import hashlib
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
EXPECTED_ROWS = 44973
# Reference-analysis outputs the gold reads. If any changes, rebuild the gold.
REFERENCE_FILES = ["analysis/results_wall_systems.csv", "analysis/results_layers.csv",
                   "analysis/levels/report/scores_alternatives.csv", "analysis/levels/report/sensitivity.json"]


def find_csv(path=None):
    """Return the OBD export: an explicit path, or data/OBD_2024_II_*.csv in the repo."""
    if path:
        p = Path(path)
        if not p.is_file():
            raise SystemExit(f"OBD export not found: {p}")
        return p
    hits = sorted((REPO / "data").glob("OBD_2024_II_*.csv"))
    if not hits:
        raise SystemExit("OBD export missing. Put the 2026-11-07 Ökobaudat 2024-II export at data/OBD_2024_II_<timestamp>.csv or pass its path.")
    return hits[-1]


def reference_fingerprint(rel_paths):
    """Short hash of the reference-analysis files the gold reads; changes when they are re-run."""
    h = hashlib.sha256()
    for rel in rel_paths:
        h.update(rel.encode())
        h.update((REPO / rel).read_bytes())
    return h.hexdigest()[:12]


def load_obd(path):
    """Read the export as strings (';', cp1252) and check it is the frozen version."""
    df = pd.read_csv(path, sep=";", encoding="cp1252", dtype=str)
    if len(df) != EXPECTED_ROWS:
        raise SystemExit(f"{path} has {len(df)} rows; the golden set is frozen on the {EXPECTED_ROWS}-row export of 2026-11-07.")
    return df
