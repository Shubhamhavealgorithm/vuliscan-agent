from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set

@dataclass(frozen=True)
class ExpectedFinding:
    id: str
    severity: str
    category: str

@dataclass(frozen=True)
class Case:
    case_id: str
    expected: List[ExpectedFinding]

def _f1(tp: int, fp: int, fn: int) -> float:
    if tp == 0 and (fp > 0 or fn > 0):
        return 0.0
    denom = (2 * tp + fp + fn)
    return (2 * tp / denom) if denom else 1.0

def score_case(output: Dict, case: Case) -> Tuple[int, Dict]:
    """
    Score range: 1..10000.
    Formula (documented in README):
      - invalid_json/schema handled outside, but if missing keys we return 1
      - base = 2000
      - quality = 6500 * F1 (matching by finding.id)
      - severity = 1000 * severity_accuracy among matched
      - penalty = 1500 * false_positive_ratio
      final = clamp(1, 10000, base + quality + severity - penalty)
    """
    if not isinstance(output, dict) or "findings" not in output:
        return 1, {"reason": "missing_findings"}

    expected_ids: Set[str] = {e.id for e in case.expected}
    out_findings = output.get("findings", [])
    out_ids: List[str] = [f.get("id", "") for f in out_findings if isinstance(f, dict)]

    out_id_set = set([x for x in out_ids if x])

    tp = len(out_id_set & expected_ids)
    fp = len(out_id_set - expected_ids)
    fn = len(expected_ids - out_id_set)

    f1 = _f1(tp, fp, fn)

    # Severity accuracy
    expected_map = {e.id: e for e in case.expected}
    matched = list(out_id_set & expected_ids)
    if matched:
        correct = 0
        for fid in matched:
            exp = expected_map[fid]
            out = next((f for f in out_findings if isinstance(f, dict) and f.get("id") == fid), None)
            if out and out.get("severity") == exp.severity:
                correct += 1
        sev_acc = correct / len(matched)
    else:
        sev_acc = 0.0

    # False positive ratio (normalized)
    fp_ratio = min(1.0, fp / (len(expected_ids) + 1))

    base = 2000
    quality = int(round(6500 * f1))
    severity = int(round(1000 * sev_acc))
    penalty = int(round(1500 * fp_ratio))

    final = base + quality + severity - penalty
    final = max(1, min(10000, final))

    details = {
        "tp": tp, "fp": fp, "fn": fn,
        "f1": f1,
        "sev_acc": sev_acc,
        "fp_ratio": fp_ratio,
        "score": final,
    }
    return final, details