#!/usr/bin/env python3
"""Score CodeAnt's PR 1 review against the seeded-defect answer key.
Usage:
  Step 1 — extract:   python3 score_pr1.py /path/to/codeant_pr1/
  Step 2 — fill in:   open codeant_pr1/score_template.md, mark VERDICT per defect
  Step 3 — compute:   python3 score_pr1.py --compute /path/to/codeant_pr1/score_template.md
"""
import json, sys, re
from pathlib import Path

DEFECTS = [
    {"id":"D1","file":"src/services/helper_services/cleanup_service.rs",
     "dimension":"Security","weight":5,
     "description":"Hardcoded bearer token (TELEMETRY_TOKEN constant)",
     "keywords":["TELEMETRY_TOKEN","TELEMETRY_URL","Bearer","secret",
                 "credential","hardcoded","token","Authorization"]},
    {"id":"D2","file":"src/services/websocket/websocket_server.rs",
     "dimension":"Observability","weight":3,
     "description":"Logging unredacted client payload in [AUDIT ts=...] line",
     "keywords":["AUDIT","full_payload","input_text","PII","sensitive",
                 "redact","mask","leak"]},
    {"id":"D3","file":"src/proto/executor.proto",
     "dimension":"Compatibility","weight":5,
     "description":"Field tag changed from 2 to 5 (wire-breaking)",
     "keywords":["tag","field number","wire","compat","breaking",
                 "backward","schema","proto"]},
    {"id":"D4","file":"src/services/all_session_services/session_management_service.rs",
     "dimension":"Resource","weight":3,
     "description":"Removed dup-key check; HashMap.insert silently overwrites",
     "keywords":["overwrite","duplicate","leak","orphan","container",
                 "previous","contains_key"]},
    {"id":"D5","file":"src/services/execution_services/executor_service.rs",
     "dimension":"Correctness","weight":2,
     "description":"Returns Ok(empty) instead of Err on container error",
     "keywords":["Ok(String","swallow","silent","graceful",
                 "degradation","Err","empty"]},
    {"id":"D6","file":"src/services/helper_services/cleanup_service.rs",
     "dimension":"Failure-handling","weight":2,
     "description":"force: true -> false in RemoveContainerOptions",
     "keywords":["force","RemoveContainerOptions","running","cleanup"]},
]
TOTAL = sum(d["weight"] for d in DEFECTS)

def is_codeant(c):
    return "codeant" in (c.get("user") or {}).get("login","").lower()

def load_comments(d):
    out = []
    for fname, ctype in [("pr1_inline_comments.json","inline"),
                          ("pr1_reviews.json","review"),
                          ("pr1_issue_comments.json","general")]:
        p = d / fname
        if not p.exists(): continue
        for c in json.loads(p.read_text()):
            if not is_codeant(c): continue
            if not c.get("body"): continue
            out.append({
                "type": ctype,
                "path": c.get("path",""),
                "line": c.get("line") or c.get("original_line"),
                "body": c["body"],
                "url":  c.get("html_url","")})
    return out

def candidates(d, all_c):
    res = []
    for c in all_c:
        kw = [k for k in d["keywords"] if k.lower() in c["body"].lower()]
        if c["path"] == d["file"] or kw:
            res.append({**c, "kw_hits": kw,
                        "path_match": c["path"] == d["file"]})
    return res

def render(d_in):
    all_c = load_comments(d_in)
    L = [f"# CodeAnt PR 1 — Scoring Template",
         f"\nCodeAnt comments captured: {len(all_c)}",
         f"Total defect weight available: {TOTAL}\n",
         "Mark each defect: replace `VERDICT: ?` with CAUGHT, PARTIAL, or MISSED.\n",
         "  CAUGHT  = full weight  (names file AND identifies the issue)",
         "  PARTIAL = half weight  (touches file/region, misses the issue)",
         "  MISSED  = 0            (no relevant comment)\n", "---\n"]
    for d in DEFECTS:
        L += [f"## {d['id']} — {d['dimension']} (weight {d['weight']})",
              f"File: `{d['file']}`",
              f"Defect: {d['description']}\n"]
        cs = candidates(d, all_c)
        if not cs:
            L.append("**No matching comments found.**\n")
        for i, c in enumerate(cs, 1):
            L += [f"### Candidate {i} ({c['type']})"]
            if c["path"]: L.append(f"Path: `{c['path']}`  Line: {c['line']}")
            if c["kw_hits"]: L.append(f"Keyword hits: {c['kw_hits']}")
            if c["url"]: L.append(f"URL: {c['url']}")
            body = c["body"].strip()
            if len(body) > 1500: body = body[:1500] + "\n... [truncated]"
            L += ["", "```", body, "```", ""]
        L += [f"**VERDICT: ?**", "", "---", ""]
    out = d_in / "score_template.md"
    out.write_text("\n".join(L))
    print(f"Wrote {out}\nNext: open it, set each VERDICT, then run --compute on it.")

def compute(template_path):
    text = Path(template_path).read_text()
    pat = re.compile(r"##\s+(D\d)\s+—.*?\(weight\s+(\d+)\).*?\*\*VERDICT:\s+(\w+)\*\*",
                     re.DOTALL)
    rows, total = [], 0.0
    for m in pat.finditer(text):
        did, w, v = m.group(1), int(m.group(2)), m.group(3).upper()
        credit = w if v=="CAUGHT" else (w/2 if v=="PARTIAL" else 0)
        rows.append((did, w, v, credit)); total += credit
    print(f"\n{'ID':4} {'Weight':>6} {'Verdict':>8} {'Credit':>7}")
    print("-"*30)
    for r in rows: print(f"{r[0]:4} {r[1]:>6} {r[2]:>8} {r[3]:>7}")
    print("-"*30)
    print(f"{'TOTAL':4} {TOTAL:>6} {'':>8} {total:>7}")
    print(f"\nRecall: {total} / {TOTAL} = {total/TOTAL*100:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--compute":
        compute(sys.argv[2])
    elif len(sys.argv) == 2:
        render(Path(sys.argv[1]))
    else:
        print(__doc__); sys.exit(1)