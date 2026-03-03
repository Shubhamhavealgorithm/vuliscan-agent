import argparse
from pathlib import Path
from rich import print as rprint
from agent.scanner import scan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Path to a file to scan")
    ap.add_argument("--language", default="python")
    args = ap.parse_args()

    p = Path(args.path)
    content = p.read_text(encoding="utf-8", errors="ignore")
    result = scan(content, language=args.language, input_type="file", path_hint=str(p))
    rprint(result)

if __name__ == "__main__":
    main()