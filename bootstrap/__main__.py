"""Run with python3 -m bootstrap from the repository root."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .core import (ROOT, Invalid, candidates, check_review, issue_body, load, read_json,
                   review_packet, review_template, task_for)
from .github import apply, preview


def main(argv=None):
    parser = argparse.ArgumentParser(description="Remora development bootstrap; no autonomous worker authority")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="Validate task graph and copied plan integrity")
    ready = commands.add_parser("candidates", help="Offline dependency simulation, not a claim")
    ready.add_argument("--completed", nargs="*", default=[])
    task = commands.add_parser("task", help="Print the issue-ready definition")
    task.add_argument("task_id")
    packet = commands.add_parser("review-packet", help="Freeze clean HEAD for independent review; print JSON")
    packet.add_argument("task_id")
    packet.add_argument("--base", required=True)
    packet.add_argument("--developer", required=True)
    template = commands.add_parser("review-template", help="Print an UNVERIFIED review skeleton")
    template.add_argument("packet", type=Path)
    review = commands.add_parser("review-check", help="Check format and bindings; does not authorize completion")
    review.add_argument("packet", type=Path)
    review.add_argument("review", type=Path)
    github = commands.add_parser("github", help="Preview or explicitly apply GitHub backlog setup")
    github.add_argument("--repo", required=True)
    github.add_argument("--owner", required=True, help="Project owner login")
    github.add_argument("--human", required=True, help="Human accountable for imported tasks")
    github.add_argument("--project", type=int, help="Existing project number; otherwise reuse/create a named Project")
    github.add_argument("--apply", action="store_true", help="Create remote GitHub resources as one human operator")
    args = parser.parse_args(argv)
    try:
        manifest = load()
        if args.command == "check":
            result = {"result": "valid", "tasks": len(manifest["tasks"]), "milestones": len(manifest["milestones"]),
                      "scenarios": 28, "mode": "human-operated bootstrap"}
        elif args.command == "candidates":
            result = {"dependency_candidates": candidates(manifest, args.completed),
                      "warning": "Human-declared simulation only. Confirm assignment, scope, resources and completion evidence on GitHub."}
        elif args.command == "task":
            print(issue_body(task_for(manifest, args.task_id), manifest["source_sha256"]))
            return 0
        elif args.command == "review-packet":
            result = review_packet(ROOT, args.task_id, args.base, args.developer)
        elif args.command == "review-template":
            result = review_template(read_json(args.packet))
        elif args.command == "review-check":
            check_review(read_json(args.packet), read_json(args.review))
            result = {"format_and_bindings": "valid", "authorization": "NONE",
                      "warning": "Human must authenticate reviewer, verify evidence, budget and current candidate, and authorize integration."}
        else:
            operation = apply if args.apply else preview
            result = operation(manifest, args.repo, args.owner, args.human, args.project)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (Invalid, OSError, KeyError, TypeError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"Remora bootstrap: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
