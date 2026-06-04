# .agents

Central registry for reusable agent skills and the CLI tooling they depend on.

## Contract

Skills should stay portable and mostly declarative:

- `skills/<name>/SKILL.md` defines when to use the skill and the canonical
  workflow.
- `skills/<name>/references/` contains optional deeper context that is loaded
  only when needed.
- Reusable implementation code should live in first-class CLI packages, not in
  skill-local scripts.

The preferred boundary is that a skill invokes a CLI command, and the CLI works
with the target repository through files, arguments, stdin, stdout, and exit
codes. That keeps the tool independently testable and prevents reusable code
from being hidden inside agent-only folders.

## Python Runtime Model

This repository owns a central `uv` project for skill runtime tooling. The
central `.venv` is for CLIs and libraries used by skills as external tools.

Use dependency groups to install only the tooling needed on a given machine:

```bash
uv sync --group document-ingest-light
uv sync --group tables-reports
uv sync --all-groups
```

Because `default-groups` is empty, run commands from this environment with
`uv run --group <group> ...`.

Install dependencies into a target repository only when that repository's own
code must import or execute them. Skill runtime dependencies belong here when
the skill uses them through a CLI boundary.

## Dependency Groups

The long-term default is for dependency groups to install CLI packages, for
example:

```toml
[dependency-groups]
document-ingest = [
  "agent-document-ingest @ git+https://github.com/example/agent-document-ingest.git",
]
```

Direct library dependencies are acceptable as a transitional backing for skills
that do not have a packaged CLI yet. Once a CLI package exists, prefer replacing
the raw libraries with that package so the command interface becomes the tested
contract.
