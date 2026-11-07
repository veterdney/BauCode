"""Shared loading of the Oekobaudat export for the eval scripts.

pandas is imported only when the export is actually loaded, so the reference fingerprint and
the offline contract tests run on the standard library alone.

Encoding note: this loader reads the export as cp1252. The older analysis script
analysis/extract.py reads it as latin-1; the two differ for bytes 0x80-0x9F (for example the
euro sign and typographic quotes). The eval does not change extract.py; strings in that byte
range may therefore differ between the two pipelines.
"""
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXPECTED_ROWS = 44973
# Reference-analysis outputs the gold reads. If any changes, rebuild the gold.
REFERENCE_FILES = ["analysis/results_wall_systems.csv", "analysis/results_layers.csv",
                   "analysis/levels/report/scores_alternatives.csv", "analysis/levels/report/sensitivity.json"]


def find_csv(path=None):
    """Return the OBD export: an explicit path, or the single data/OBD_2024_II_*.csv in the repo.

    Several matching exports are ambiguous and refused (the old behaviour silently took the last one).
    """
    if path:
        p = Path(path)
        if not p.is_file():
            raise SystemExit(f"OBD export not found: {p}")
        return p
    hits = sorted((REPO / "data").glob("OBD_2024_II_*.csv"))
    if not hits:
        raise SystemExit("OBD export missing. Put the 2026-11-07 Oekobaudat 2024-II export at data/OBD_2024_II_<timestamp>.csv or pass its path.")
    if len(hits) > 1:
        raise SystemExit("Several OBD exports match data/OBD_2024_II_*.csv; pass the one to use explicitly (--csv): "
                         + ", ".join(h.name for h in hits))
    return hits[0]


def file_provenance(path, rows=None):
    """What can be said about the export bytes actually used. Integrity, not authenticity:
    no canonical expected hash is published, so none is asserted here."""
    p = Path(path)
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return {"filename": p.name, "size_bytes": p.stat().st_size, "sha256": h.hexdigest(), "rows": rows,
            "expected_rows": EXPECTED_ROWS, "encoding_assumed": "cp1252", "origin": "unknown (not recorded in repo)",
            "export_date": "2026-11-07 (stated in README; not verified)", "licence": "unknown (not recorded in repo)"}


def reference_fingerprint(rel_paths):
    """Short hash of the reference-analysis files the gold reads; changes when they are re-run.
    A missing file raises (FileNotFoundError) instead of being skipped."""
    h = hashlib.sha256()
    for rel in rel_paths:
        h.update(rel.encode())
        h.update((REPO / rel).read_bytes())
    return h.hexdigest()[:12]


def load_obd(path):
    """Read the export as strings (';', cp1252) and check it is the frozen version (row count)."""
    import pandas as pd
    df = pd.read_csv(path, sep=";", encoding="cp1252", dtype=str)
    if len(df) != EXPECTED_ROWS:
        raise SystemExit(f"{path} has {len(df)} rows; the golden set is frozen on the {EXPECTED_ROWS}-row export of 2026-11-07.")
    return df