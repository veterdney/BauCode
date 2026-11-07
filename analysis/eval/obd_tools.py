"""Read-only data tools for the agent under test.

The agent gets the same sources a human analyst would: the frozen Ökobaudat export and the
files of this repository's analysis. The tools only look things up; they do no arithmetic,
no filtering by plausibility and no unit conversion, because those are what the eval tests.
"""
import json
from pathlib import Path

import pandas as pd

from obd_data import REPO, find_csv, load_obd

META = ["UUID", "Version", "Name (en)", "Name (de)", "Kategorie (en)", "Konformitaet", "Laenderkennung", "Typ",
        "Referenzjahr", "Gueltig bis", "Declaration owner", "Registrierungsnummer", "Registrierungsstelle",
        "Bezugsgroesse", "Bezugseinheit", "Referenzfluss-Name", "Schuettdichte (kg/m3)", "Flaechengewicht (kg/m2)",
        "Rohdichte (kg/m3)", "Schichtdicke (m)", "Laengengewicht (kg/m)", "Stueckgewicht (kg)",
        "Umrechungsfaktor auf 1kg", "biogener Kohlenstoffgehalt in kg"]
ROW = ["Modul", "Szenario", "Szenariobeschreibung"]
READABLE = ("analysis/", "data/Building material property dataset")
MAX_CHARS = 60000

TOOLS = [
    {"name": "search_datasets", "strict": True,
     "description": "Search the Ökobaudat export by words in the dataset name (English or German) or category. Returns one line per dataset with its UUID, category, dataset type, declared quantity and unit, densities and validity. Up to `limit` results.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["query", "limit"],
                      "properties": {"query": {"type": "string", "description": "Words to find in name or category, e.g. 'straw bale' or 'Mineral wool'"},
                                     "limit": {"type": "integer", "description": "Maximum results, 1-50"}}}},
    {"name": "get_dataset", "strict": True,
     "description": "All metadata and every module row (A1-A3 ... D, with scenario labels) of one dataset, with every indicator the export holds for that row. Values are as declared, per the dataset's declared quantity and unit.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["uuid"],
                      "properties": {"uuid": {"type": "string"}}}},
    {"name": "category_values", "strict": True,
     "description": "One indicator for one module across every dataset whose category contains the given text. Returns UUID, name, declared quantity and unit, densities and the value, as declared. Use it to compare or take medians yourself.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["category", "module", "indicator"],
                      "properties": {"category": {"type": "string", "description": "Text the English category must contain, e.g. 'Aluminium profiles'"},
                                     "module": {"type": "string", "description": "Module as written in the export, e.g. 'A1-A3', 'C3', 'D'"},
                                     "indicator": {"type": "string", "description": "Column name, e.g. 'GWPtotal (A2)', 'PENRT', 'GWP'"}}}},
    {"name": "read_repo_file", "strict": True,
     "description": "Read a file of the reference analysis: any path under analysis/ (reports, result CSVs, sensitivity.json) or the material property dataset under data/.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["path"],
                      "properties": {"path": {"type": "string", "description": "Path relative to the repository root, e.g. analysis/levels/report/README.md"}}}},
]


class ObdTools:
    def __init__(self, csv_path=None):
        self.df = load_obd(find_csv(csv_path))
        self.ind = [c for c in self.df.columns if c not in META + ROW and not c.startswith(("URL", "UUID des", "Version des", "Referenzfluss-UUID", "Hintergrund", "Veroeffentlicht", "Kategorie (orig"))]
        self.uni = self.df.drop_duplicates("UUID")

    @staticmethod
    def _clean(rec):
        return {k: v for k, v in rec.items() if isinstance(v, str) and v != ""}

    def search_datasets(self, query, limit=20):
        words = [w.lower() for w in query.split() if w]
        hay = (self.uni["Name (en)"].fillna("") + " | " + self.uni["Name (de)"].fillna("") + " | " + self.uni["Kategorie (en)"].fillna("")).str.lower()
        mask = pd.Series(True, index=self.uni.index)
        for w in words:
            mask &= hay.str.contains(w, regex=False)
        hits = self.uni[mask]
        cols = ["UUID", "Name (en)", "Kategorie (en)", "Typ", "Bezugsgroesse", "Bezugseinheit", "Rohdichte (kg/m3)",
                "Schuettdichte (kg/m3)", "Flaechengewicht (kg/m2)", "Gueltig bis", "Konformitaet"]
        limit = max(1, min(int(limit), 50))
        return {"total_matches": int(len(hits)), "shown": min(limit, len(hits)),
                "results": [self._clean(r) for r in hits[cols].head(limit).to_dict("records")]}

    def get_dataset(self, uuid):
        rows = self.df[self.df.UUID == uuid.strip()]
        if rows.empty:
            return {"error": f"No dataset with UUID {uuid} in the export."}
        meta = self._clean(rows.iloc[0][META].to_dict())
        modules = [self._clean(r) for r in rows[ROW + self.ind].to_dict("records")]
        return {"metadata": meta, "modules": modules}

    def category_values(self, category, module, indicator):
        if indicator not in self.df.columns:
            return {"error": f"Unknown indicator '{indicator}'. Known: {', '.join(self.ind)}"}
        rows = self.df[self.df["Kategorie (en)"].fillna("").str.contains(category, case=False, regex=False) & (self.df.Modul == module)]
        cols = ["UUID", "Name (en)", "Kategorie (en)", "Szenario", "Bezugsgroesse", "Bezugseinheit", "Rohdichte (kg/m3)", indicator]
        recs = [self._clean(r) for r in rows[cols].head(300).to_dict("records")]
        return {"rows": int(len(rows)), "shown": len(recs), "values": recs}

    def read_repo_file(self, path):
        root = REPO.resolve()
        full = (root / path.strip().lstrip("/")).resolve()
        try:
            rel = full.relative_to(root)
        except ValueError:
            rel = None
        if rel is None or not rel.as_posix().startswith(READABLE) or rel.as_posix().startswith("analysis/eval"):
            return {"error": "Only files under analysis/ (excluding analysis/eval/) and the material property dataset can be read."}
        if not full.is_file():
            return {"error": f"No such file: {rel}"}
        text = full.read_text(encoding="utf-8", errors="replace")
        return {"path": str(rel), "truncated": len(text) > MAX_CHARS, "content": text[:MAX_CHARS]}

    def call(self, name, args):
        fn = {"search_datasets": self.search_datasets, "get_dataset": self.get_dataset,
              "category_values": self.category_values, "read_repo_file": self.read_repo_file}.get(name)
        if fn is None:
            return json.dumps({"error": f"Unknown tool {name}"}), True
        try:
            out = fn(**args)
        except (TypeError, ValueError) as exc:
            return json.dumps({"error": f"Bad arguments for {name}: {exc}"}), True
        return json.dumps(out, ensure_ascii=False), "error" in out
