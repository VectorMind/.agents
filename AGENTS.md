# Agent Guidance

This repository stores reusable agent skills. Keep the portable skill contract as
the default:

- `skills/<name>/SKILL.md` contains the canonical workflow and trigger metadata.
- `skills/<name>/references/` contains optional deeper context loaded only when
  needed.
- `skills/<name>/scripts/` contains deterministic helpers that run in the
  consuming workspace.

Avoid product-specific metadata by default. Add files such as
`agents/openai.yaml`, `.github/prompts/*.prompt.md`, or
`.github/copilot-instructions.md` only when they provide a clear functional
advantage for a specific surface.

For Python dependencies used by skills, install packages in the consuming
workspace's uv project environment with `uv add`. Do not install skill runtime
dependencies globally or into this reusable skills repository.
