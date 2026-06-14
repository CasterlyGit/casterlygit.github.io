"""Generate reusable skills from converged traces."""

import json
from datetime import datetime
from typing import Optional


class SkillGenerator:
    """Generates markdown skills from agent traces."""

    def generate(
        self, objective: str, site_url: str, trace_history: list, iterations: list
    ) -> str:
        """Generate a complete, converged skill."""
        date = datetime.now().strftime("%Y-%m-%d")
        final_iteration = iterations[-1]
        analysis = final_iteration.analysis

        # Build steps from trace
        steps = self._extract_steps(trace_history[-1], analysis)
        selectors = analysis.get("selectors_used", [])
        constraints = self._extract_constraints(trace_history, iterations)

        # Estimate cost
        cost_estimate = self._estimate_cost(iterations)

        markdown = f"""# Skill: {self._format_title(objective)}

## Objective
{objective}
Generated: {date}

## How It Works

"""
        for i, step in enumerate(steps, 1):
            markdown += f"{i}. {step}\n"

        markdown += f"""
## Key Selectors

"""
        for selector in selectors:
            markdown += f"- `{selector}`\n"

        markdown += f"""
## Learned Constraints

"""
        for constraint in constraints:
            markdown += f"- {constraint}\n"

        markdown += f"""
## Deterministic Glue

```bash
#!/bin/bash
# To run this skill:
# 1. Ensure browserbase CLI is installed: pip install browserbase
# 2. Set BROWSERBASE_API_KEY environment variable
# 3. Run: bash run_skill.sh

SITE="{site_url}"
browserbase fetch "$SITE" | \\
  jq '.dom' | \\
  python3 <<'PYTHON'
import sys, json
# Load DOM and execute stored selectors
# ... (implementation in skill runtime)
PYTHON
```

## Cost Model

- First run: {cost_estimate['exploration_cost']} (full exploration, {len(iterations)} iterations)
- Subsequent runs: {cost_estimate['per_run_cost']} (deterministic path)
- ROI breakeven: Run {cost_estimate['breakeven_runs']} (amortizes exploration cost)

## References

- Site: {site_url}
- Converged in {len(iterations)} iteration(s)
- Confidence: {analysis.get('confidence', 'N/A'):.0%}
"""

        return markdown

    def generate_partial(
        self,
        objective: str,
        site_url: str,
        trace_history: list,
        iterations: list,
        max_iterations: int,
    ) -> str:
        """Generate a partial skill when max iterations reached without full convergence."""
        date = datetime.now().strftime("%Y-%m-%d")

        # Try to extract what worked from all attempts
        all_selectors = set()
        for iteration in iterations:
            selectors = iteration.analysis.get("selectors_used", [])
            all_selectors.update(selectors)

        markdown = f"""# Skill: {self._format_title(objective)} (PARTIAL)

## Objective
{objective}
Generated: {date}

## Status
⚠️ **Partial Convergence** — Max iterations ({max_iterations}) reached.
This skill works for most cases but may not handle all edge cases.

## How It Works

From {len(trace_history)} exploration attempts, the best path found:

1. Navigate to {site_url}
2. Execute the learned selectors (see below)
3. Handle errors gracefully (see constraints)

## Discovered Selectors

From exploration attempts:

"""
        for selector in sorted(list(all_selectors))[:15]:
            markdown += f"- `{selector}`\n"

        markdown += f"""
## Known Constraints & Fallbacks

- Site may have JS gates: try clicking interactive elements in order
- Selectors may change on redesign: use text matching as fallback
- Forms may vary: detect inputs by placeholder or label text
- Timeouts: increase wait times if network is slow

## Notes for Next Iteration

- Consider testing {max_iterations + 2} iterations next time for better convergence
- Document site-specific quirks (timezone handling, validation rules)
- Test on different dates/times to find temporal patterns

## Cost Model

- Exploration: ~${max_iterations * 0.5:.2f} (at ~$0.50/iteration)
- Per-run skill cost: ~$0.10
- Breakeven: ~{int(max_iterations * 0.5 / 0.10)} runs

## References

- Site: {site_url}
- Explored in {len(iterations)} iteration(s)
"""

        return markdown

    def _format_title(self, objective: str) -> str:
        """Format objective as a skill title."""
        # Capitalize and limit length
        title = objective.split(".")[0]  # First sentence
        if len(title) > 60:
            title = title[:57] + "..."
        return title.strip()

    def _extract_steps(self, trace: dict, analysis: dict) -> list:
        """Extract procedural steps from final trace."""
        response = trace.get("response", "")

        # Try to extract numbered steps
        lines = response.split("\n")
        steps = []

        for line in lines:
            line = line.strip()
            if line and any(line.startswith(f"{i}.") for i in range(1, 20)):
                steps.append(line)

        # If no numbered steps found, create generic ones
        if not steps:
            selectors = analysis.get("selectors_used", [])
            steps = [
                f"Navigate to the target URL",
                f"Use selectors: {', '.join(selectors[:3])}",
                f"Complete the objective step-by-step",
                f"Verify completion",
            ]

        return steps[:12]  # Top 12 steps

    def _extract_constraints(self, trace_history: list, iterations: list) -> list:
        """Extract learned constraints from failed attempts."""
        constraints = set()

        for iteration in iterations:
            analysis = iteration.analysis
            failures = analysis.get("failures", [])
            decisions = analysis.get("key_decisions", [])

            for failure in failures:
                if "timeout" in failure.lower():
                    constraints.add(
                        "Site may be slow to load — increase wait times if needed"
                    )
                if "stale" in failure.lower():
                    constraints.add(
                        "Elements may become stale — re-query selectors if element not found"
                    )
                if "not found" in failure.lower():
                    constraints.add("Some elements may be hidden or require scrolling")

            for decision in decisions:
                if "javascript" in decision.lower() or "js" in decision.lower():
                    constraints.add("Site requires JavaScript execution")
                if "form" in decision.lower():
                    constraints.add("Form submission may require additional validation")

        if not constraints:
            constraints.add("Handle dynamic content gracefully")

        return sorted(list(constraints))[:5]

    def _estimate_cost(self, iterations: list) -> dict:
        """Estimate cost of exploration vs. per-run skill cost."""
        # Average cost per iteration: ~$0.50 (Opus 4.1 @ ~1500 tokens in/out)
        exploration_cost = len(iterations) * 0.50
        per_run_cost = 0.10  # Deterministic browserbase + light validation
        breakeven = int(exploration_cost / per_run_cost) if per_run_cost > 0 else 0

        return {
            "exploration_cost": f"${exploration_cost:.2f}",
            "per_run_cost": f"${per_run_cost:.2f}",
            "breakeven_runs": breakeven,
        }
