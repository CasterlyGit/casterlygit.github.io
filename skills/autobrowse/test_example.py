"""Example usage and basic test of autobrowse workflow."""

import json
from unittest.mock import Mock, patch
from .workflow import AutobrowseWorkflow, AutobrowseConfig
from .trace_analyzer import TraceAnalyzer
from .skill_generator import SkillGenerator


def test_trace_analyzer():
    """Test trace analysis logic."""
    analyzer = TraceAnalyzer()

    # Test success detection
    success_trace = {
        "response": "Successfully navigated to the site. Found the button. Clicked 'Book Now'. Confirmation received: Order #12345."
    }
    result = analyzer.analyze(success_trace)
    assert result["success"], "Should detect successful completion"
    assert result["confidence"] > 0.8, "Should have high confidence"

    # Test failure detection
    failure_trace = {
        "response": "Navigation failed. Could not find the target button. Timeout after 30 seconds waiting for element."
    }
    result = analyzer.analyze(failure_trace)
    assert not result["success"], "Should detect failure"
    assert len(result["failures"]) > 0, "Should extract failures"

    print("✓ Trace analyzer tests passed")


def test_skill_generator():
    """Test skill markdown generation."""
    gen = SkillGenerator()

    trace_history = [
        {
            "iteration": 0,
            "response": "Navigated to site. Found button selector: '.find-table'. Clicked. Form appeared. Filled date field. Selected time 19:00. Clicked submit. Booking confirmed.",
        }
    ]

    iterations = [
        Mock(
            analysis={
                "success": True,
                "selectors_used": [".find-table", "[data-test='time-picker']"],
                "failures": [],
                "confidence": 0.95,
            }
        )
    ]

    skill = gen.generate(
        objective="Book a 7pm reservation at Oliveto",
        site_url="https://opentable.com/oliveto",
        trace_history=trace_history,
        iterations=iterations,
    )

    assert "# Skill:" in skill, "Should generate markdown header"
    assert "Book a 7pm reservation" in skill, "Should include objective"
    assert ".find-table" in skill, "Should include selectors"
    assert "ROI breakeven" in skill, "Should include cost model"

    print("✓ Skill generator tests passed")


def test_workflow_config():
    """Test workflow configuration."""
    config = AutobrowseConfig(
        objective="Test objective",
        site_url="https://example.com",
        max_iterations=3,
    )

    assert config.objective == "Test objective"
    assert config.site_url == "https://example.com"
    assert config.max_iterations == 3

    print("✓ Workflow config tests passed")


def test_partial_skill_generation():
    """Test partial skill generation when max iterations reached."""
    gen = SkillGenerator()

    trace_history = [
        {"iteration": i, "response": f"Attempt {i+1}"} for i in range(3)
    ]

    iterations = [
        Mock(
            analysis={
                "selectors_used": [".selector-1", ".selector-2"],
                "failures": ["Element not found"],
            }
        )
        for _ in range(3)
    ]

    skill = gen.generate_partial(
        objective="Book reservation",
        site_url="https://opentable.com",
        trace_history=trace_history,
        iterations=iterations,
        max_iterations=3,
    )

    assert "(PARTIAL)" in skill, "Should mark as partial"
    assert "Max iterations" in skill, "Should explain max iterations reached"
    assert ".selector-1" in skill, "Should include discovered selectors"

    print("✓ Partial skill generation tests passed")


def example_workflow_structure():
    """Show the workflow structure without running real API calls."""
    print("\n" + "=" * 60)
    print("AUTOBROWSE WORKFLOW STRUCTURE")
    print("=" * 60)

    config = AutobrowseConfig(
        objective="Book a 7pm reservation at Oliveto",
        site_url="https://www.opentable.com/oliveto",
        max_iterations=3,
    )

    print(f"\nConfiguration:")
    print(f"  Objective: {config.objective}")
    print(f"  Site: {config.site_url}")
    print(f"  Max iterations: {config.max_iterations}")

    print(f"\nIteration structure:")
    print(f"  1. Explore: Agent navigates site")
    print(f"  2. Analyze: Parse trace for success/failures")
    print(f"  3. Improve: Generate next strategy")
    print(f"  4. Repeat: Until convergence or max iterations")

    print(f"\nOutput:")
    print(f"  ✓ Skill markdown (ready to publish)")
    print(f"  ✓ Cost estimate (exploration + breakeven)")
    print(f"  ✓ Trace history (full decision logs)")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    print("Running autobrowse tests...\n")

    try:
        test_workflow_config()
        test_trace_analyzer()
        test_skill_generator()
        test_partial_skill_generation()
        example_workflow_structure()

        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Set ANTHROPIC_API_KEY environment variable")
        print("2. Run: python -m skills.autobrowse.cli <objective> <site_url>")
        print("3. Example: python -m skills.autobrowse.cli \\")
        print('     "Book a 7pm reservation at Oliveto" \\')
        print('     "https://www.opentable.com/oliveto"')

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
