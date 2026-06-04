# Agent Guidance

This repository stores reusable agent skills. Keep the portable skill contract as
the default:

- `skills/<name>/SKILL.md` contains the canonical workflow and trigger metadata.
- `skills/<name>/references/` contains optional deeper context loaded only when
  needed.
- Reusable implementation code belongs in first-class CLI packages, not in
  skill-local scripts. A skill should call CLIs through arguments, stdin/stdout,
  files, and exit codes.
- `skills/<name>/scripts/` is not a default extension point. Use it only for
  tiny compatibility shims when there is a clear reason not to promote the code
  into a maintained CLI package.

The repository root `pyproject.toml` is the central `uv` project for skill
runtime tooling. Prefer dependency groups that install CLI packages used by
skills. Direct Python libraries in a group are acceptable only as a transitional
backing until the corresponding CLI exists.

Use the central `.agents` environment when a skill runs tooling as an external
CLI. Install packages into the consuming workspace only when that workspace's
own code must import or execute those packages.

Avoid product-specific metadata by default. Add files such as
`agents/openai.yaml`, `.github/prompts/*.prompt.md`, or
`.github/copilot-instructions.md` only when they provide a clear functional
advantage for a specific surface.
