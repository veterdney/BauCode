"""Write docs/eval.html, the browsable view of the golden set, for GitHub Pages.

  python3 -I analysis/eval/build_page.py

Re-run it whenever golden_v1.jsonl changes, so the published page matches the cases.
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "docs" / "eval.html"
HEAD = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}'
        'body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>\n')

cases = [json.loads(l) for l in open(HERE / "golden_v1.jsonl", encoding="utf-8") if l.strip()]
data = json.dumps(cases, ensure_ascii=False).replace("</", "<\\/")
page = (HERE / "page_template.html").read_text(encoding="utf-8").replace("__DATA__", data)
title = re.search(r"<title>.*?</title>\n?", page).group(0)
page = page.replace(title, "", 1)
OUT.write_text(HEAD.replace("</head>", title.strip() + "</head>") + page + "\n</body></html>\n", encoding="utf-8")
print(f"{len(cases)} cases -> {OUT.relative_to(HERE.parents[1])}")
