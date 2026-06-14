"""Core autobrowse workflow: iterative agent exploration with trace analysis."""

import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

try:
    import anthropic
except ImportError:
    anthropic = None

from .trace_analyzer import TraceAnalyzer
from .skill_generator import SkillGenerator


@dataclass
class AutobrowseConfig:
    """Configuration for autobrowse workflow."""

    objective: str
    site_url: str
    max_iterations: int = 5
    timeout_per_run: int = 60
    api_key: Optional[str] = None

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")


@dataclass
class IterationResult:
    """Result from a single autobrowse iteration."""

    iteration: int
    success: bool
    trace: dict
    analysis: dict
    improvement_prompt: Optional[str] = None
    error: Optional[str] = None


class AutobrowseWorkflow:
    """Iterative agent exploration workflow."""

    def __init__(self, config: AutobrowseConfig):
        self.config = config
        if anthropic is None:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.analyzer = TraceAnalyzer()
        self.trace_history = []
        self.iterations = []

    def run(self) -> dict:
        """Execute autobrowse workflow."""
        print(f"🚀 Starting Autobrowse: {self.config.objective}")
        print(f"   Site: {self.config.site_url}")
        print(f"   Max iterations: {self.config.max_iterations}\n")

        for i in range(self.config.max_iterations):
            print(f"--- Iteration {i + 1}/{self.config.max_iterations} ---")
            result = self._iteration(i)
            self.iterations.append(result)

            if result.error:
                print(f"❌ Error: {result.error}\n")
                continue

            print(f"✓ Trace captured ({len(result.trace)} events)")
            print(f"  Analysis: {result.analysis['summary']}")

            if result.success:
                print(f"\n✅ Converged in {i + 1} iteration(s)!")
                return self._finalize_success(i)

            if result.improvement_prompt:
                print(f"  Next: {result.improvement_prompt[:100]}...\n")

        print(f"\n⚠️  Max iterations reached without full convergence")
        return self._finalize_partial()

    def _iteration(self, iteration_num: int) -> IterationResult:
        """Run one iteration: explore, analyze, improve."""
        try:
            trace = self._explore(iteration_num)
            self.trace_history.append(trace)

            analysis = self.analyzer.analyze(trace)
            success = analysis.get("success", False)

            improvement = None
            if not success and len(self.trace_history) < self.config.max_iterations:
                improvement = self._generate_improvement(trace, analysis)

            return IterationResult(
                iteration=iteration_num,
                success=success,
                trace=trace,
                analysis=analysis,
                improvement_prompt=improvement,
            )
        except Exception as e:
            return IterationResult(
                iteration=iteration_num,
                success=False,
                trace={},
                analysis={},
                error=str(e),
            )

    def _explore(self, iteration_num: int) -> dict:
        """Run agent to explore site and complete objective."""
        system_prompt = f"""You are a web automation agent. Your task is to:
1. Navigate to the given URL
2. Complete the objective: {self.config.objective}
3. Log every action: selectors used, decisions made, errors encountered
4. Return the final state and whether you succeeded

Be deterministic and document everything that worked or failed."""

        user_prompt = f"""Site: {self.config.site_url}
Iteration: {iteration_num + 1}/{self.config.max_iterations}

{f"Trace history: {json.dumps(self.trace_history[-1], indent=2)[:500]}" if self.trace_history else ""}

Please explore this site and attempt the objective. Document your process."""

        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return {
            "iteration": iteration_num,
            "timestamp": datetime.now().isoformat(),
            "response": response.content[0].text,
            "usage": asdict(response.usage),
        }

    def _generate_improvement(self, trace: dict, analysis: dict) -> str:
        """Generate next iteration's improvement prompt."""
        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=512,
            system="You are a strategic advisor for web automation. Given a failed attempt, suggest the next strategy to try.",
            messages=[
                {
                    "role": "user",
                    "content": f"""Failed attempt summary: {analysis['summary']}

Key failures:
{json.dumps(analysis.get('failures', []), indent=2)[:300]}

What should we try next to converge on this objective?""",
                }
            ],
        )

        return response.content[0].text

    def _finalize_success(self, final_iteration: int) -> dict:
        """Generate skill from successful convergence."""
        final_trace = self.trace_history[final_iteration]
        skill_gen = SkillGenerator()

        skill_markdown = skill_gen.generate(
            objective=self.config.objective,
            site_url=self.config.site_url,
            trace_history=self.trace_history,
            iterations=self.iterations,
        )

        return {
            "status": "converged",
            "iterations": final_iteration + 1,
            "skill_markdown": skill_markdown,
            "cost_estimate": self._estimate_cost(final_iteration),
            "trace_history": self.trace_history,
        }

    def _finalize_partial(self) -> dict:
        """Return partial result if max iterations reached."""
        skill_gen = SkillGenerator()

        skill_markdown = skill_gen.generate_partial(
            objective=self.config.objective,
            site_url=self.config.site_url,
            trace_history=self.trace_history,
            iterations=self.iterations,
            max_iterations=self.config.max_iterations,
        )

        return {
            "status": "partial",
            "iterations": len(self.trace_history),
            "skill_markdown": skill_markdown,
            "cost_estimate": self._estimate_cost(len(self.trace_history) - 1),
            "trace_history": self.trace_history,
            "notes": "Converged partially; not all edge cases covered",
        }

    def _estimate_cost(self, final_iteration: int) -> dict:
        """Estimate cost of exploration + amortization breakeven."""
        total_cost = sum(
            it["trace"]["usage"].get("input_tokens", 0) * 0.003 / 1000
            + it["trace"]["usage"].get("output_tokens", 0) * 0.015 / 1000
            for it in self.iterations[: final_iteration + 1]
        )

        skill_cost = 0.10  # Per-run cost of deterministic skill
        breakeven_runs = int(total_cost / skill_cost) if skill_cost > 0 else 0

        return {
            "exploration_cost": f"${total_cost:.2f}",
            "per_run_cost": f"${skill_cost:.2f}",
            "breakeven_runs": breakeven_runs,
        }


def run_autobrowse(
    objective: str, site_url: str, max_iterations: int = 5
) -> dict:
    """Convenience function to run autobrowse workflow."""
    config = AutobrowseConfig(
        objective=objective, site_url=site_url, max_iterations=max_iterations
    )
    workflow = AutobrowseWorkflow(config)
    return workflow.run()
