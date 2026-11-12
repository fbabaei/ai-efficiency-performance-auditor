"""Offline import and gate CLI. No network, telemetry collection or workloads."""

import argparse
import json
from pathlib import Path

from auditor_tools.budgets import evaluate_budgets
from auditor_tools.contracts import load_json
from auditor_tools.otlp import normalize_otlp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import-otlp", help="import one already-sanitized OTLP JSON export")
    importer.add_argument("input", type=Path)
    importer.add_argument("--confirm-sanitized", action="store_true", required=True)
    importer.add_argument("--source-id", default="input-1")
    importer.add_argument("--output", type=Path, help="new output file; existing files are never overwritten")
    gate = commands.add_parser("gate", help="evaluate approved budgets over supplied measurements")
    gate.add_argument("candidate", type=Path)
    gate.add_argument("--budgets", type=Path, required=True)
    gate.add_argument("--baseline", type=Path)
    gate.add_argument("--confirm-comparable", action="store_true")
    gate.add_argument("--output", type=Path, help="new output file; existing files are never overwritten")
    args = parser.parse_args()
    try:
        if args.command == "import-otlp":
            result = normalize_otlp(load_json(args.input), source_id=args.source_id)
            exit_code = 0
        else:
            if args.confirm_comparable and args.baseline is None:
                raise ValueError("--confirm-comparable requires --baseline")
            result = evaluate_budgets(
                load_json(args.candidate), load_json(args.budgets),
                load_json(args.baseline) if args.baseline is not None else None,
                comparable=args.confirm_comparable,
            )
            exit_code = {"pass": 0, "fail": 1, "inconclusive": 3}[result["status"]]
        content = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(content)
        else:
            print(content, end="")
    except (OSError, UnicodeError, ValueError, OverflowError, RecursionError) as error:
        parser.exit(2, f"Offline tool error: {error}\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
