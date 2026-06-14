# CasterlyGit Skills Library

Reusable AI skills for web automation, research, and task execution.

## Skills

### 1. Autobrowse

Teach agents to explore websites and generate reusable skills through iterative learning.

**Problem:** Browser agents have amnesia—they rediscover every site from scratch on every run.

**Solution:** Agent explores once, learns optimal path, generates durable skill for teammates.

```bash
# Book a restaurant reservation
autobrowse \
  "Book a 7pm reservation at Oliveto" \
  "https://www.opentable.com/oliveto" \
  --iterations 5 \
  --output skill_oliveto.md
```

**Result:** Markdown skill that runs deterministically, saving 90% on repeat runs.

Learn more: [`skills/autobrowse/README.md`](skills/autobrowse/README.md)

## Installation

```bash
pip install -e .
```

## Development

```bash
# Run tests
python3 -m skills.autobrowse.test_example

# Use in Python
from skills.autobrowse import run_autobrowse

result = run_autobrowse(
    objective="Book reservation",
    site_url="https://opentable.com"
)
print(result['skill_markdown'])
```

## Next Skills (Roadmap)

- **Curvy**: Fast skill caching + learning (integrate with agent dispatch)
- **Fast-Path Routing**: <100ms skill execution via intelligent routing
- **CLI Workflows**: Native terminal skills without API gateway
- **IDE UX**: Better handling of readonly/temp files
- **Token Optimization**: TRIDENT-aware adaptive fan-out

See [`IMPLEMENTATION-ROADMAP-2026-06-14.md`](../../../approver/IMPLEMENTATION-ROADMAP-2026-06-14.md) for details.

## License

MIT (see LICENSE)

## References

- GitHub Issues: [#1-#5](https://github.com/CasterlyGit/casterlygit.github.io/issues)
- Implementation Roadmap: [14 hours across 3 segments](../../../approver/IMPLEMENTATION-ROADMAP-2026-06-14.md)
