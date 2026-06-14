"""CLI interface for autobrowse skill generation."""

import sys
import json
import argparse
from pathlib import Path

from .workflow import AutobrowseWorkflow, AutobrowseConfig


def main():
    """Command-line entry point for autobrowse."""
    parser = argparse.ArgumentParser(
        description="Teach agents to explore sites and generate reusable skills"
    )
    parser.add_argument(
        "objective", help="Task objective (e.g., 'Book a 7pm reservation at Oliveto')"
    )
    parser.add_argument("site_url", help="Target site URL (e.g., 'https://opentable.com')")
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Max iterations before convergence (default: 5)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Per-iteration timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save generated skill to file (default: stdout)",
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output (trace details)",
    )

    args = parser.parse_args()

    config = AutobrowseConfig(
        objective=args.objective,
        site_url=args.site_url,
        max_iterations=args.iterations,
        timeout_per_run=args.timeout,
        api_key=args.api_key,
    )

    workflow = AutobrowseWorkflow(config)
    result = workflow.run()

    if args.verbose:
        print(json.dumps(result, indent=2, default=str))
    else:
        # Print just the skill
        if "skill_markdown" in result:
            print("\n" + "=" * 60)
            print("GENERATED SKILL")
            print("=" * 60 + "\n")
            print(result["skill_markdown"])

            if args.output:
                args.output.write_text(result["skill_markdown"])
                print(f"\n✓ Skill saved to {args.output}")

            print("\n" + "=" * 60)
            print(f"Status: {result['status']}")
            print(f"Iterations: {result['iterations']}")
            if "cost_estimate" in result:
                print(f"Cost: {result['cost_estimate']['exploration_cost']}")
                print(f"Breakeven: {result['cost_estimate']['breakeven_runs']} runs")
            print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
