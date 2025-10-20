# Ritual PR Infrastructure

[![CI](https://github.com/ritual-net/ritual-pr-infra/actions/workflows/ci.yml/badge.svg)](https://github.com/ritual-net/ritual-pr-infra/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Minimal one-time setup tool for **Manus AI** and **Claude** automated PR reviews with custom engineering prompts.

## Quick Start

```bash
cd /path/to/your/repo
uvx ritual-pr-infra init
```

That's it! The tool generates everything you need for automated PR reviews.

## Features

✨ **Two Independent AI Reviewers**
- **Manus AI**: Creates review tasks on manus.im with GitHub connector integration
- **Claude**: Posts comprehensive inline comments directly on your PRs

🎯 **Custom Engineering Prompts**
- Engineering standards (architecture, testing, maintainability, documentation)
- FSM verification (state machine analysis, static verification, formal methods)

🔄 **Incremental Reviews**
- Both agents check previous reviews to avoid duplicate work
- Focus on new changes when reviewing updated PRs

🛠️ **Two Simple Commands**
- `init` - One-time setup
- `update-workflows` - Update workflows without touching custom prompts

## Installation

```bash
uv tool install ritual-pr-infra
```

Or use directly with `uvx` (no installation needed):

```bash
uvx ritual-pr-infra init
```

## Setup Guide

### Step 1: Initialize Your Repository

```bash
cd /path/to/your/repo
uvx ritual-pr-infra init
```

This creates:
- `.ritual-pr/config.yml` - Configuration
- `.ritual-pr/prompts/shared/` - Engineering and FSM verification prompts
- `.github/workflows/manus-pr-review.yml` - Manus workflow
- `.github/workflows/claude-pr-review.yml` - Claude workflow

### Step 2: Configure Manus (One-Time Setup)

1. **Get your Manus API key** from https://manus.im
2. **Connect GitHub** in Manus web UI:
   - Go to https://manus.im → Connectors → GitHub
   - Click "Connect" and authorize the Manus app
   - Grant access to your repositories
   - **Copy the connector UUID** (shown after connecting)

### Step 3: Add GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions:

- `MANUS_API_KEY` - Your Manus API key
- `MANUS_GITHUB_CONNECTOR_ID` - The UUID from Manus Connectors page
- `ANTHROPIC_API_KEY` - Your Anthropic/Claude API key

### Step 4: Merge to Default Branch

**Important:** GitHub requires workflows to exist on the default branch before they can run.

```bash
git add .ritual-pr/ .github/workflows/
git commit -m "feat: add Manus and Claude PR review infrastructure"

# Create PR and merge to main/dev
git push -u origin add-pr-reviews
gh pr create --title "feat: add PR review infrastructure" --fill
gh pr merge --squash  # After approval
```

### Step 5: Test on a New PR

Once merged to your default branch, the workflows will automatically review all new PRs!

## How It Works

### Manus AI Review Workflow

1. Triggers on PR `opened` and `synchronize` events
2. Reads custom prompts from `.ritual-pr/prompts/`
3. Creates a review task on https://manus.im
4. **Posts a comment** with the task URL
5. Uses GitHub connector to access your repository
6. Manus posts its review as a PR comment when complete

### Claude Review Workflow

1. Triggers on PR `opened` and `synchronize` events  
2. Reads custom prompts from `.ritual-pr/prompts/`
3. Checks out PR with full history (`fetch-depth: 0`)
4. **Analyzes the PR diff** directly in the workflow
5. **Posts review comments** inline and as top-level observations
6. Shows progress tracking with checkboxes

## Commands

### `init` - Initial Setup

```bash
ritual-pr-infra init [--path /path/to/repo]
```

Generates:
- `.ritual-pr/` directory with config and prompts
- `.github/workflows/` with both review workflows

### `update-workflows` - Update Workflows Only

```bash
ritual-pr-infra update-workflows [--path /path/to/repo]
```

**Use this when:**
- Workflow templates have been updated in a new version
- You need to fix a workflow bug
- You want to regenerate workflows from your config

**Preserves:**
- All custom prompts in `.ritual-pr/prompts/`
- Your `.ritual-pr/config.yml` settings

**Regenerates:**
- `.github/workflows/manus-pr-review.yml`
- `.github/workflows/claude-pr-review.yml`

## Default Prompts

The tool includes two production-ready prompts:

### 1. **engineering.md** - Engineering Standards
- Architecture & design principles
- Code quality & correctness
- System design (availability, failure modes, maintainability)
- Documentation requirements
- Security & integrity (commit signing, OSS practices)

### 2. **fsm-verification.md** - FSM & Verification
- Finite state machine representation
- Static analysis & verification opportunities
- FSM completeness checking
- Verification loop recommendations
- Formal methods suggestions

These prompts were designed for **Rust blockchain projects** but work for any codebase.

## Customization

### Modify Existing Prompts

```bash
vim .ritual-pr/prompts/shared/engineering.md
vim .ritual-pr/prompts/shared/fsm-verification.md
```

### Add New Prompts

```bash
echo "# Security Review" > .ritual-pr/prompts/shared/security.md
```

Then update `.ritual-pr/config.yml`:

```yaml
manus:
  prompts:
    - shared/engineering.md
    - shared/security.md  # Your new prompt
```

### Agent-Specific Prompts

Create separate directories for agent-specific prompts:

```bash
mkdir -p .ritual-pr/prompts/manus
mkdir -p .ritual-pr/prompts/claude

echo "# Manus Custom Prompt" > .ritual-pr/prompts/manus/infrastructure.md
echo "# Claude Custom Prompt" > .ritual-pr/prompts/claude/documentation.md
```

Update config:

```yaml
manus:
  prompts:
    - shared/engineering.md
    - manus/infrastructure.md

claude:
  prompts:
    - shared/engineering.md
    - claude/documentation.md
```

### Disable an Agent

Set `enabled: false` in `.ritual-pr/config.yml`:

```yaml
manus:
  enabled: false  # Manus disabled

claude:
  enabled: true   # Only Claude reviews
```

Then regenerate workflows:

```bash
uvx ritual-pr-infra update-workflows
```

### Trigger Only on Specific Labels

```yaml
claude:
  trigger:
    "on": [opened, synchronize]
    labels: ["needs-review"]  # Only run if PR has this label
```

## Troubleshooting

### Workflows Not Running on PRs

**Problem:** New workflows don't run on PRs  
**Cause:** GitHub requires workflows to exist on the default branch first  
**Solution:** 
1. Merge the workflow files to your default branch (main/dev)
2. Set the correct default branch if needed: `gh repo edit --default-branch dev`
3. Subsequent PRs will trigger the workflows

### Manus Review Not Posting Comments

**Problem:** Manus creates tasks but doesn't comment on PR  
**Possible Causes:**
1. GitHub connector not set up in Manus web UI
2. Wrong `MANUS_GITHUB_CONNECTOR_ID` secret
3. Repository not authorized in Manus connector settings

**Solution:**
1. Go to https://manus.im → Connectors → GitHub
2. Verify your repositories are authorized
3. Copy the exact connector UUID to GitHub secrets
4. Trigger a new PR update to retry

### Manus API Rate Limiting

**Problem:** Manus workflow fails with "request too many"  
**Cause:** Manus API has a rate limit (200 requests/minute, 60s reset)  
**Solution:** 
- The workflow automatically retries with exponential backoff (2s, 4s, 8s)
- If all retries fail, it posts a warning comment
- Wait 60 seconds and push another commit to retry
- Normal usage (one PR update = one API call) won't hit limits

### Claude Review Not Appearing

**Problem:** Claude workflow runs but no comments appear  
**Possible Causes:**
1. Missing `id-token: write` or `actions: read` permissions
2. `ANTHROPIC_API_KEY` not set or invalid

**Solution:**
1. Verify secret is set: `gh secret list | grep ANTHROPIC`
2. Check workflow logs for permission errors
3. Ensure workflows were merged to default branch

### Workflow Validation Errors

**Problem:** "Workflow validation failed" error  
**Cause:** Workflow file on PR branch differs from default branch  
**Solution:** This is expected when first adding workflows. Merge the PR and it will work on subsequent PRs.

## Advanced Configuration

### Custom Workflow Triggers

```yaml
claude:
  trigger:
    "on": [opened, synchronize, ready_for_review, reopened]
    labels: []
```

### Multiple Prompts Per Agent

```yaml
manus:
  prompts:
    - shared/engineering.md
    - shared/fsm-verification.md
    - manus/blockchain-specific.md
    - manus/performance-critical.md
```

### Different Prompts for Different Agents

```yaml
manus:
  prompts:
    - shared/engineering.md  # Architecture focus

claude:
  prompts:
    - shared/fsm-verification.md  # Verification focus
```

## How Reviews Work

### Manus AI Reviews

1. Workflow creates a task on https://manus.im
2. Posts PR comment with task URL
3. Manus reviews using GitHub connector
4. **Manus posts review comment when complete**
5. You can track progress on manus.im

**Review Location:** Both on manus.im dashboard AND as PR comment

### Claude Reviews

1. Workflow triggers Claude Code Action
2. Claude reads PR diff and existing comments
3. **Checks if it has reviewed before** (incremental reviews)
4. Posts progress tracking comment
5. **Posts detailed review as PR comments**
6. Can create inline comments on specific code lines

**Review Location:** Directly on the PR as comments

## Directory Structure

```
ritual-pr-infra/
├── src/ritual_pr_infra/
│   ├── cli.py                  # Commands: init, update-workflows
│   ├── generator.py            # Workflow generation logic
│   └── templates/
│       ├── config.yml          # Default config
│       ├── prompts/
│       │   ├── engineering.md       # Engineering standards
│       │   └── fsm-verification.md  # FSM & verification
│       └── workflows/
│           ├── manus-pr-review.yml.j2   # Manus template
│           └── claude-pr-review.yml.j2  # Claude template
├── tests/
│   └── test_generator.py      # Unit tests
├── .github/workflows/
│   └── ci.yml                  # CI: lint, format, test
├── Makefile                    # Dev commands
├── pyproject.toml             # Package config
└── README.md                  # This file
```

## Development

### Running Tests

```bash
make test
```

### Linting and Formatting

```bash
make format  # Format code with ruff
make lint    # Lint code with ruff
make all     # Format, lint, and test
```

### Building the Package

```bash
uv build
```

## Production Usage

This tool is used in production by:
- **ritual-net/ritual-reth-internal** - Rust blockchain execution client

## Contributing

Contributions welcome! Please:
1. Run `make all` before committing
2. Add tests for new features
3. Update documentation

## License

Apache-2.0

## Links

- **Repository**: https://github.com/ritual-net/ritual-pr-infra
- **Issues**: https://github.com/ritual-net/ritual-pr-infra/issues
- **Manus AI**: https://manus.im
- **Claude Code Action**: https://github.com/anthropics/claude-code-action

## FAQ

**Q: Do both agents run on every PR?**  
A: Yes, by default. You can disable one by setting `enabled: false` in the config.

**Q: Can I use this with private repositories?**  
A: Yes! Both Manus (via GitHub connector) and Claude (via API) support private repos.

**Q: How much do the API calls cost?**  
A: 
- Manus: Check your manus.im pricing plan
- Claude: ~$0.30-0.50 per comprehensive PR review (depends on PR size)

**Q: Can the agents modify my code?**  
A: No. Both agents only read code and post comments. They don't create commits or modify files.

**Q: What if I update the tool and want to update my workflows?**  
A: Run `uvx ritual-pr-infra update-workflows` to regenerate workflows while preserving your custom prompts.

**Q: Can I test the workflows before merging?**  
A: Workflows must be on the default branch to run. Create a test repository or merge to a test branch first.

**Q: Do the agents duplicate each other's work?**  
A: No. Each uses different models and may find different issues. They also check previous reviews to avoid repeating feedback.
