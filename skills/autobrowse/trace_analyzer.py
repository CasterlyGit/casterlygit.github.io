"""Analyze agent traces to extract decisions, failures, and success patterns."""

import re
import json
from typing import Any


class TraceAnalyzer:
    """Analyzes agent exploration traces."""

    def analyze(self, trace: dict) -> dict:
        """Analyze a single trace for success, failures, and patterns."""
        response_text = trace.get("response", "")

        success = self._detect_success(response_text)
        failures = self._extract_failures(response_text)
        selectors = self._extract_selectors(response_text)
        decisions = self._extract_decisions(response_text)

        return {
            "success": success,
            "summary": self._summarize(
                response_text[:500]
            ),  # First 500 chars as summary
            "failures": failures,
            "selectors_used": selectors,
            "key_decisions": decisions,
            "confidence": self._estimate_confidence(success, failures),
        }

    def _detect_success(self, text: str) -> bool:
        """Detect if objective was completed."""
        success_indicators = [
            "successfully",
            "completed",
            "booking confirmed",
            "confirmation",
            "success",
            "✓",
            "✅",
        ]
        failure_indicators = [
            "failed",
            "unable",
            "error",
            "timeout",
            "stale",
            "not found",
            "couldn't",
        ]

        text_lower = text.lower()
        success_count = sum(text_lower.count(ind) for ind in success_indicators)
        failure_count = sum(text_lower.count(ind) for ind in failure_indicators)

        # Success if more success indicators AND objective completion mentioned
        return success_count > failure_count and (
            "complete" in text_lower or "success" in text_lower
        )

    def _extract_failures(self, text: str) -> list:
        """Extract failure/error patterns from trace."""
        failures = []

        error_patterns = [
            r"(?:error|failed|timeout|stale|not found):?\s*([^\n]+)",
            r"(?:encountered|hit|ran into):?\s*([^\n]+)",
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            failures.extend(matches[:3])  # Limit to top 3

        return failures[:5]  # Return top 5 failures

    def _extract_selectors(self, text: str) -> list:
        """Extract CSS/XPath selectors from trace."""
        selectors = []

        css_pattern = r'(?:selector|button|click|element):\s*(?:`([^`]+)`|"([^"]+)")'
        xpath_pattern = r'(?:xpath|path):\s*(?:`([^`]+)`|"([^"]+)")'

        for pattern in [css_pattern, xpath_pattern]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                selector = match[0] or match[1]
                if selector and selector not in selectors:
                    selectors.append(selector)

        return selectors[:10]  # Top 10 selectors

    def _extract_decisions(self, text: str) -> list:
        """Extract key decisions/strategies from trace."""
        decisions = []

        # Look for decision patterns
        decision_pattern = r"(?:decided|chose|used|tried):\s*([^\n]+)"
        matches = re.findall(decision_pattern, text, re.IGNORECASE)

        # Also extract lines with "because" or "reason"
        reason_pattern = r"([^\n]*(?:because|reason|found that)[^\n]*)"
        reason_matches = re.findall(reason_pattern, text, re.IGNORECASE)

        decisions = (matches + reason_matches)[:5]
        return [d.strip() for d in decisions if d.strip()]

    def _summarize(self, text: str) -> str:
        """Create brief summary of trace."""
        # Return first sentence or first 100 chars
        sentences = text.split(". ")
        if sentences:
            return (sentences[0] + ".").strip()[:150]
        return text[:150]

    def _estimate_confidence(self, success: bool, failures: list) -> float:
        """Estimate confidence in this trace's findings."""
        if success:
            return 0.9 + (0.1 * (1 - min(len(failures) / 5, 1)))
        else:
            return 0.5 + (0.4 * (1 - min(len(failures) / 5, 1)))
