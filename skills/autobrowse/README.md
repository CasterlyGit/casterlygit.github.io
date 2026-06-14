# Autobrowse: Teach Agents to Explore Sites

Generate reusable web automation skills by letting Claude explore real sites and learn optimal paths.

## Problem

Browser agents have **amnesia**: they rediscover every site from scratch on every run. After 100 runs on the same site, the agent has done the same exploration 100 times—the reasoning evaporates with each session.

**Result:** Cost graph goes up linearly (no amortization). No durable artifact. Real sites are messy (JS gates, undocumented endpoints, redesigns).

## Solution

Autobrowse is a **workflow that uses AI to improve AI**:

1. **Agent explores** the real task on real site (one complete run)
2. **Studies the trace** it produced (what went wrong? what worked?)
3. **Iterates strategy** (try different selectors, endpoints, flows)
4. **Converges** on a reliable path (not lucky, deterministic)
5. **Graduates** winning approach → reusable skill (markdown + CLI)

Next agent/teammate runs the skill without re-learning.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python -m skills.autobrowse.cli \
  "Book a 7pm reservation at Oliveto" \
  "https://www.opentable.com/oliveto" \
  --iterations 5 \
  --output skill_oliveto.md
```

### Python API

```python
from skills.autobrowse import run_autobrowse

result = run_autobrowse(
    objective="Book a 7pm reservation at Oliveto",
    site_url="https://www.opentable.com/oliveto",
    max_iterations=5
)

print(result['skill_markdown'])
# Returns generated skill, ready to use
```

## How It Works

### Iteration Loop

Each iteration:

1. **Explore**: Agent navigates site, attempts objective, logs every decision
2. **Analyze**: Parse trace for success/failure, extract selectors, identify patterns
3. **Improve**: Ask agent what to try differently next time
4. **Repeat**: Until convergence or max iterations

### Convergence Criteria

- Objective completed successfully
- Path is deterministic (repeatable without luck)
- Selectors and constraints documented

### Output: Reusable Skill

Generated skill includes:

```markdown
# Skill: Book OpenTable Reservation

## How It Works
1. Navigate to ...
2. Click selector: ...
3. Fill form: ...

## Learned Constraints
- Site doesn't accept "7 PM" text → use datepicker
- Email validation strict → validate before submit

## Cost Model
- Exploration: $2.50 (5 iterations)
- Per-run: $0.10
- Breakeven: 25 runs
```

## Cost Model

**Exploration cost** is amortized across repeat runs:

- First run: ~$2.50 (5 iterations × $0.50 each)
- Subsequent runs: ~$0.10 (deterministic path)
- ROI breakeven: ~25 runs
- After 100 runs: savings of ~$240 vs. repeated exploration

**When to use autobrowse:**
- Recurring tasks (book restaurant weekly, fetch data daily)
- Team/customer handoff (skill is shareable documentation)
- Site is stable (redesigns break skills, but fallbacks documented)

## Example: OpenTable Reservation

Full example with real-world site:

```python
from skills.autobrowse import AutobrowseWorkflow, AutobrowseConfig

config = AutobrowseConfig(
    objective="Book a 7pm dinner reservation for 2 at Oliveto, Berkeley",
    site_url="https://www.opentable.com/oliveto-berkeley-ca",
    max_iterations=5,
)

workflow = AutobrowseWorkflow(config)
result = workflow.run()

# Result includes:
# - skill_markdown: Ready-to-use skill
# - iterations: Number of attempts needed
# - cost_estimate: Exploration cost + breakeven
# - trace_history: Full agent decision logs
```

## Success Criteria

✅ **Converged skill:** Deterministic path runs 100% (not probabilistic)  
✅ **Cost amortization:** Breakeven < 50 runs (reasonable for repeat task)  
✅ **Durability:** Skill survives redesign (graceful fallback documented)  
✅ **Portability:** Skill runs without context (just URL + form fields)

## Architecture

```
autobrowse/
├── workflow.py          # Core iteration loop
├── trace_analyzer.py    # Parse agent traces
├── skill_generator.py   # Convert traces → markdown skills
├── cli.py              # Command-line interface
└── README.md           # This file
```

## Known Limitations

1. **Requires Claude Opus 4.1** (strongest reasoning for complex sites)
2. **Site redesigns** break skills (but fallbacks documented)
3. **JS-heavy sites** may converge slowly (more iterations needed)
4. **Temporal patterns** (seasonal changes, rotating promotions) not captured
5. **Authentication** flows may need manual setup (OAuth, MFA)

## Future Work

- [ ] Multi-user skill learning (aggregate patterns from team)
- [ ] Skill versioning + auto-update on site redesign detection
- [ ] Browserbase + Playwright hybrid (real browser + headless speed)
- [ ] Skill marketplace (share skills across projects)
- [ ] Regression tests (alert when skill breaks)

## References

- GitHub Issue: [CasterlyGit/casterlygit.github.io#1](https://github.com/CasterlyGit/casterlygit.github.io/issues/1)
- Design Spec: [Design-Autobrowse-Skill-2026-06-14.md](../Design-Autobrowse-Skill-2026-06-14.md)
- Roadmap: [IMPLEMENTATION-ROADMAP-2026-06-14.md](../IMPLEMENTATION-ROADMAP-2026-06-14.md)
