"""Commit Ranking Engine: Weighted evidence scoring and explainable attribution for CI build failures."""
import os
import re
from common import load_cfg
import log_parser

def rank(commits, log_text, failure_type=None, cfg=None):
    """
    Ranks candidate commits using a multi-factor evidence-based scoring model.
    commits: list of dicts (oldest first) with:
             'hash', 'author', 'message', 'files' (list of paths).
    """
    cfg = cfg or load_cfg()
    w = cfg.get("weights", {"file_match": 0.55, "pom_change": 0.25, "recency": 0.10, "change_size": 0.10})
    
    parsed = log_parser.parse_log(log_text)
    effective_ftype = failure_type or parsed["failure_type"]
    affected_file = parsed["affected_file"]
    tokens = [t.lower() for t in parsed.get("relevant_tokens", [])]

    n = max(len(commits), 1)
    raw = []
    evidence_list = []

    for i, c in enumerate(commits):
        c_files = c.get("files", [])
        stems = [os.path.splitext(os.path.basename(f))[0].lower() for f in c_files]
        basenames = [os.path.basename(f).lower() for f in c_files]

        # 1. File match factor
        f_match = 0.0
        match_details = []
        for f, base, stem in zip(c_files, basenames, stems):
            if affected_file and (base == affected_file.lower() or stem == os.path.splitext(affected_file)[0].lower()):
                f_match = 1.0
                match_details.append(f"Direct match with affected file '{os.path.basename(f)}'")
                break
            elif any(t in base or t == stem for t in tokens if len(t) > 2):
                f_match = 1.0
                match_details.append(f"Linked to error token/test '{os.path.basename(f)}'")
                break
            elif stem in log_text.lower():
                f_match = 0.8
                match_details.append(f"File stem '{stem}' referenced in console log")
                break

        # 2. Dependency factor
        pom = 0.0
        if any("pom.xml" in f.lower() for f in c_files) and effective_ftype == "dependency":
            pom = 1.0
            match_details.append("pom.xml modified during dependency resolution failure")

        # 3. Recency factor
        recency = (i + 1) / n

        # 4. Change size factor (smaller/focused changes or larger complex changes)
        size = min(len(c_files) / 5.0, 1.0)

        commit_raw_score = (
            w.get("file_match", 0.55) * f_match +
            w.get("pom_change", 0.25) * pom +
            w.get("recency", 0.10) * recency +
            w.get("change_size", 0.10) * size
        )
        raw.append(commit_raw_score)

        # Build evidence explanation string
        reasons = []
        if match_details:
            reasons.append("; ".join(match_details) + f" (+{w.get('file_match', 0.55) * f_match:.2f})")
        if pom > 0:
            reasons.append(f"Dependency configuration modified (+{w.get('pom_change', 0.25) * pom:.2f})")
        reasons.append(f"Commit recency index {i+1}/{n} (+{w.get('recency', 0.10) * recency:.2f})")
        reasons.append(f"Scope: {len(c_files)} file(s) changed (+{w.get('change_size', 0.10) * size:.2f})")

        evidence_list.append(" | ".join(reasons))

    total = sum(raw) or 1.0
    out = []
    threshold = cfg.get("rollback", {}).get("confidence_threshold", 0.60)

    for c, s, ev in zip(commits, raw, evidence_list):
        d = dict(c)
        normalized = round(s / total, 3)
        d["score"] = normalized
        d["evidence_details"] = ev
        if normalized >= threshold:
            d["attribution_status"] = "Probable Cause"
        elif normalized < 0.40:
            d["attribution_status"] = "Unlikely Cause"
        else:
            d["attribution_status"] = "Candidate under Review"
        out.append(d)

    ranked = sorted(out, key=lambda d: d["score"], reverse=True)
    return ranked

def decide(top, cfg=None):
    """Determines recommended SCM action and rollback advisability."""
    cfg = cfg or load_cfg()
    r = cfg.get("rollback", {})
    threshold = r.get("confidence_threshold", 0.60)
    max_files = r.get("max_files_for_isolation", 3)

    num_files = len(top.get("files", []))
    score = top.get("score", 0.0)
    isolated = num_files <= max_files

    if score >= threshold and isolated:
        return f"Rollback recommended: git revert {top['hash']} (isolated change of {num_files} files, confidence {score*100:.1f}%)"
    elif score >= threshold and not isolated:
        return f"Manual investigation required: High confidence ({score*100:.1f}%), but commit touches {num_files} files (exceeds isolation threshold of {max_files})"
    else:
        return f"Manual investigation required: Confidence ({score*100:.1f}%) is below decision threshold ({threshold*100:.1f}%)"

if __name__ == "__main__":
    sample = [
        {"hash": "a111111", "author": "PRU", "message": "CR-005: parser xml", "files": ["analyzer/parser.py"]},
        {"hash": "b222222", "author": "BKS", "message": "CR-002: update validator", "files": ["maven/src/main/java/com/commitsleuth/demo/Validator.java"]},
        {"hash": "c333333", "author": "PRU", "message": "CR-004: pom tweak", "files": ["maven/pom.xml", "README.md"]},
    ]
    log = "[ERROR] Validator.java:[12,30] ';' expected  COMPILATION ERROR"
    cfg = load_cfg()
    results = rank(sample, log, "compile", cfg)
    for r in results:
        print(f"{r['hash']} | {r['author']} | score={r['score']} | {r['attribution_status']}")
        print(f"   Evidence: {r['evidence_details']}")
    print("Action:", decide(results[0], cfg))
