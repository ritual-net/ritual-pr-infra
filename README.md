# Ritual PR Infrastructure

[![CI](https://github.com/ritual-net/ritual-pr-infra/actions/workflows/ci.yml/badge.svg)](https://github.com/ritual-net/ritual-pr-infra/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

One-time setup tool for Manus and Claude PR reviews.

## Installation

```bash
uv tool install ritual-pr-infra
```

Or use directly with `uvx`:

```bash
uvx ritual-pr-infra init
```

## Usage

```bash
cd /path/to/your/repo
uvx ritual-pr-infra init
```

This creates:
- `.ritual-pr/` with config and prompts
- `.github/workflows/` with Manus and Claude workflows

## Setup

### 1. Add GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `MANUS_API_KEY` - Your Manus API key
- `MANUS_GITHUB_CONNECTOR_ID` - Your Manus GitHub connector UUID (from https://manus.im → Connectors → GitHub)
- `ANTHROPIC_API_KEY` - Your Anthropic API key

**Note for Manus:** You must first connect GitHub in the Manus web UI (https://manus.im → Connectors → GitHub) and authorize access to your repositories. The connector UUID will be shown after setup.

### 2. Commit and Push

```bash
git add .ritual-pr/ .github/workflows/
git commit -m "Add Ritual PR review infrastructure"
git push
```

### 3. Open a PR

Open a PR and watch the automated reviews!

## Customization

### Change Which Prompts Are Used

Edit `.ritual-pr/config.yml` to modify which prompts each agent uses:

```yaml
manus:
  enabled: true
  prompts:
    - shared/security.md
    - shared/quality.md
    - manus/custom-prompt.md  # Agent-specific prompt
```

### Customize Review Instructions

Edit or add files in `.ritual-pr/prompts/`:

- `shared/` - Prompts used by both agents
- `manus/` - Manus-specific prompts (optional)
- `claude/` - Claude-specific prompts (optional)

### Re-generate Workflows

After changing the config, re-run:

```bash
uvx ritual-pr-infra init
```

This will regenerate the workflows based on your updated configuration.

## Directory Structure

After running `init`, your repository will have:

```
repository-root/
├── .ritual-pr/
│   ├── config.yml              # Configuration file
│   └── prompts/
│       ├── shared/
│       │   ├── security.md     # Security review prompts
│       │   ├── quality.md      # Quality review prompts
│       │   └── performance.md  # Performance review prompts
│       ├── manus/              # Optional: Manus-specific prompts
│       └── claude/             # Optional: Claude-specific prompts
└── .github/
    └── workflows/
        ├── manus-pr-review.yml   # Manus workflow
        └── claude-pr-review.yml  # Claude workflow
```

## Configuration Reference

### config.yml

```yaml
version: "1.0"

manus:
  enabled: true                    # Enable/disable Manus reviews
  prompts:                         # List of prompt files to use
    - shared/security.md
    - shared/quality.md
  trigger:
    on: [opened, synchronize]      # PR events to trigger on
    labels: []                     # Optional: only run if PR has these labels

claude:
  enabled: true                    # Enable/disable Claude reviews
  prompts:
    - shared/security.md
    - shared/quality.md
  trigger:
    on: [opened, synchronize]
    labels: []
```

### Trigger Events

Common PR trigger events:
- `opened` - When a PR is first opened
- `synchronize` - When new commits are pushed
- `reopened` - When a closed PR is reopened
- `ready_for_review` - When a draft PR is marked ready

### Label Filtering

To only run reviews on PRs with specific labels:

```yaml
manus:
  trigger:
    labels: ["needs-review", "security"]
```

## Default Prompts

The tool includes three default prompts:

1. **security.md** - Security vulnerability review
2. **quality.md** - Code quality and best practices
3. **performance.md** - Performance optimization opportunities

You can edit these or add your own in `.ritual-pr/prompts/`.

## Examples

### Example 1: Security-Only Reviews

```yaml
manus:
  enabled: true
  prompts:
    - shared/security.md

claude:
  enabled: false
```

### Example 2: Different Prompts for Each Agent

```yaml
manus:
  enabled: true
  prompts:
    - shared/security.md
    - manus/infrastructure.md

claude:
  enabled: true
  prompts:
    - shared/quality.md
    - claude/documentation.md
```

### Example 3: Label-Triggered Reviews

```yaml
manus:
  enabled: true
  prompts:
    - shared/security.md
  trigger:
    on: [opened, synchronize]
    labels: ["security-review"]
```

## License

Apache-2.0

## Support

For issues or questions, please open an issue on GitHub.

