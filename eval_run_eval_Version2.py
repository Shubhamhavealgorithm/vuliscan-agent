import json
from pathlib import Path
from agent.scanner import scan
from agent.scoring import Case, ExpectedFinding, score_case

def load_cases(path: str):
    p = Path(path)
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        expected = [ExpectedFinding(**e) for e in obj["expected"]]
        yield obj, Case(case_id=obj["case_id"], expected=expected)

def main():
    cases_path = "eval/datasets/cases.jsonl"
    total = 0
    per_case = []

    for raw, case in load_cases(cases_path):
        out = scan(
            raw["content"],
            language=raw.get("language", "python"),
            input_type=raw.get("input_type", "snippet"),
            path_hint=raw.get("path_hint", "unknown"),
        )
        sc, details = score_case(out, case)
        total += sc
        per_case.append((case.case_id, sc, details))

    avg = total / len(per_case)
    # Convert avg to 1..10000 scale already; avg is already in that range.
    print(f"Cases: {len(per_case)}")
    print(f"Average score (1-10000): {avg:.2f}")
    print("Per-case:")
    for cid, sc, details in per_case:
        print(f"- {cid}: {sc} details={details}")

if __name__ == "__main__":
    main()