# Quick Start Guide

## Installation & Usage

```bash
# One-line setup for any repository
cd /path/to/your/repo
uvx ritual-pr-infra init
```

That's it! 🎉

## What It Does

Creates:
- `.ritual-pr/config.yml` - Configuration file
- `.ritual-pr/prompts/shared/*.md` - Three default prompts (security, quality, performance)
- `.github/workflows/manus-pr-review.yml` - Manus workflow
- `.github/workflows/claude-pr-review.yml` - Claude workflow

## Required GitHub Secrets

Add these in your repository settings (Settings → Secrets and variables → Actions):

- `MANUS_API_KEY` - Your Manus API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key

## Next Steps

```bash
# 1. Commit the generated files
git add .ritual-pr/ .github/workflows/
git commit -m "Add Ritual PR review infrastructure"

# 2. Push to GitHub
git push

# 3. Open a PR and watch the automated reviews!
```

## Customization

### Change Which Prompts Are Used

Edit `.ritual-pr/config.yml`:

```yaml
manus:
  enabled: true
  prompts:
    - shared/security.md     # Include this prompt
    - shared/quality.md      # Include this prompt
    # - shared/performance.md  # Comment out to exclude

claude:
  enabled: true
  prompts:
    - shared/quality.md      # Claude only checks quality
```

### Modify Review Instructions

Edit files in `.ritual-pr/prompts/shared/`:

```bash
# Edit existing prompts
vim .ritual-pr/prompts/shared/security.md

# Add new prompts
echo "# My Custom Review" > .ritual-pr/prompts/shared/custom.md
```

Then update `config.yml` to use the new prompt:

```yaml
manus:
  prompts:
    - shared/security.md
    - shared/custom.md
```

### Agent-Specific Prompts

Create agent-specific directories:

```bash
# Manus-only prompts
mkdir -p .ritual-pr/prompts/manus
echo "# Manus Custom Review" > .ritual-pr/prompts/manus/infra.md

# Claude-only prompts
mkdir -p .ritual-pr/prompts/claude
echo "# Claude Custom Review" > .ritual-pr/prompts/claude/docs.md
```

Update config:

```yaml
manus:
  prompts:
    - shared/security.md
    - manus/infra.md

claude:
  prompts:
    - shared/quality.md
    - claude/docs.md
```

### Trigger Only on Specific Labels

Edit `.ritual-pr/config.yml`:

```yaml
manus:
  trigger:
    "on": [opened, synchronize]
    labels: ["needs-security-review"]  # Only run if PR has this label
```

### Regenerate Workflows

After changing the config:

```bash
uvx ritual-pr-infra init
```

This regenerates the workflows based on your updated configuration.

## Disabling an Agent

Set `enabled: false` in `.ritual-pr/config.yml`:

```yaml
manus:
  enabled: false  # Manus reviews disabled

claude:
  enabled: true   # Only Claude reviews will run
```

Then regenerate:

```bash
uvx ritual-pr-infra init
```

## Troubleshooting

### Workflows Not Running

1. Check that secrets are added (MANUS_API_KEY, ANTHROPIC_API_KEY)
2. Verify workflows are in `.github/workflows/`
3. Check PR triggers match your config (opened, synchronize, etc.)

### Prompts Not Loading

1. Verify prompt files exist in `.ritual-pr/prompts/`
2. Check paths in `config.yml` match actual file locations
3. Ensure prompt files are committed and pushed

### Want to Start Over

```bash
# Remove generated files
rm -rf .ritual-pr/ .github/workflows/*pr-review.yml

# Re-run init
uvx ritual-pr-infra init
```

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

### Example 2: Different Prompts Per Agent

```yaml
manus:
  enabled: true
  prompts:
    - shared/security.md
    - shared/performance.md

claude:
  enabled: true
  prompts:
    - shared/quality.md
```

### Example 3: Label-Triggered Reviews

```yaml
manus:
  trigger:
    "on": [opened, synchronize]
    labels: ["ready-for-review"]
```

## Help & Support

- **Repository**: https://github.com/ritual/ritual-pr-infra
- **Issues**: Open an issue on GitHub
- **Documentation**: See README.md for full documentation

## Philosophy

This tool does one thing: generates PR review infrastructure. After running `init`, the tool is no longer needed. Your repository has standard GitHub Actions workflows that work independently.

**Simple. Minimal. Done.** ✨

