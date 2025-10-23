# Automated PR Review Infrastructure

This repository uses automated AI reviewers to provide comprehensive code review feedback on all pull requests.

## 🤖 Active Reviewers

Three AI reviewers are configured to automatically review PRs:

1. **Manus AI** - Creates review tasks on manus.im with GitHub connector integration
2. **Claude** - Posts comprehensive inline comments directly on PRs  
3. **Devin** - Provides additional AI-powered code review with session tracking

All three reviewers run independently and in parallel, providing diverse perspectives on your code changes.

## 📋 Review Criteria

The reviewers evaluate PRs against these standards:

### Engineering Standards
- Architecture & design principles
- Code quality & correctness
- Testing & maintainability
- Documentation requirements
- Security & integrity
- System design (availability, failure modes)

### FSM Verification (where applicable)
- Finite state machine representation
- Static analysis & verification opportunities
- FSM completeness checking
- Verification loop recommendations
- Formal methods suggestions

See the full review prompts in `.ritual-pr/prompts/shared/`.

## 🔧 Configuration

### Customizing Reviews

1. **Edit Configuration**: Modify `.ritual-pr/config.yml` to:
   - Enable/disable specific reviewers
   - Change which prompts each reviewer uses
   - Modify trigger conditions (PR events, labels)

2. **Regenerate Workflows**: After editing config.yml, run:
   ```bash
   uvx ritual-pr-infra update-workflows
   ```
   This regenerates the GitHub Actions workflows with your changes.

3. **Customize Prompts**: Edit or add prompt files in `.ritual-pr/prompts/`:
   - `shared/` - Prompts used by all reviewers
   - `manus/` - Manus-specific prompts
   - `claude/` - Claude-specific prompts
   - `devin/` - Devin-specific prompts

### Required Secrets

The following GitHub secrets must be configured for the reviewers to work:

| Secret | Description | Get it from |
|--------|-------------|-------------|
| `MANUS_API_KEY` | Manus API key | https://manus.im |
| `MANUS_GITHUB_CONNECTOR_ID` | Manus GitHub connector UUID | https://manus.im → Connectors → GitHub |
| `ANTHROPIC_API_KEY` | Claude API key | https://www.anthropic.com |
| `DEVIN_API_KEY` | Devin API key | https://devin.ai |

To add secrets:
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with its corresponding value

## 🔄 How Reviews Work

### Workflow Lifecycle

1. **PR Event**: When a PR is opened or updated
2. **Validation**: Workflows validate that secrets and prompt files exist
3. **Prompt Loading**: Each reviewer loads its configured prompts
4. **API Call**: Reviewer creates a review session/task
5. **Review Posted**: Reviewer posts findings as PR comments

### Reviewer Coordination

The three reviewers **run independently** without coordination. This is intentional to provide:
- Diverse perspectives on code quality
- Redundancy (if one fails, others still review)
- Different types of feedback (inline comments, review tasks, session links)

You'll typically see:
- Manus: Posts a comment with task URL for tracking
- Claude: Posts inline comments on specific code lines
- Devin: Posts a session link where you can view detailed analysis

### Incremental Reviews

All reviewers are configured to:
1. Check if they've reviewed the PR before
2. Focus only on NEW changes since last review
3. Avoid repeating previous feedback
4. Update or supplement earlier comments

This prevents duplicate feedback when you update PRs.

## 🐛 Troubleshooting

### Workflow Not Running

**Problem**: Reviewers don't comment on new PRs

**Possible Causes**:
1. Workflows must be on the default branch (main/dev) to run
2. Secrets not configured
3. Workflow file syntax errors

**Solutions**:
1. Ensure workflow files are merged to default branch
2. Verify all secrets are set: Settings → Secrets and variables → Actions
3. Check Actions tab for workflow errors

### Secret Not Configured Error

**Problem**: Workflow fails with "Error: XXX_API_KEY secret not configured"

**Solution**:
1. Go to Settings → Secrets and variables → Actions
2. Add the missing secret
3. Re-run the failed workflow or create a new PR

### Prompt File Not Found Error

**Problem**: Workflow fails with "Error: Prompt file not found"

**Possible Causes**:
1. Prompt file was deleted
2. Config.yml references non-existent prompt
3. Workflow not regenerated after config change

**Solutions**:
1. Verify prompt files exist in `.ritual-pr/prompts/`
2. Check paths in config.yml match actual files
3. Run `uvx ritual-pr-infra update-workflows` if you changed config

### API Rate Limiting

**Problem**: Manus or Devin show "Unable to start review" errors

**Cause**: API rate limits or transient network issues

**Solution**: The workflows have built-in retry logic (3 attempts with exponential backoff). If all attempts fail:
1. Check API service status
2. Wait a few minutes and update the PR to trigger another review
3. Verify API keys are valid and have quota available

### Reviews Seem Repetitive

**Problem**: Reviewers repeat the same feedback multiple times

**Cause**: Reviewer may not have access to previous comments, or prompt instructs otherwise

**Solution**: 
1. Verify reviewers have `pull-requests: read` permission
2. Check that incremental review instructions are in prompts
3. This is rare; reviewers actively check for previous feedback

## 📊 Workflow Files

The GitHub Actions workflows are located in:
- `.github/workflows/manus-pr-review.yml`
- `.github/workflows/claude-pr-review.yml`
- `.github/workflows/devin-pr-review.yml`

These files are generated from `.ritual-pr/config.yml` and should not be edited directly. Instead:
1. Edit `config.yml`
2. Run `uvx ritual-pr-infra update-workflows`
3. Commit the regenerated workflow files

## 🎯 Best Practices

1. **Address feedback systematically**: Reviewers provide actionable suggestions
2. **Respond to comments**: Let reviewers know which issues you've fixed
3. **Ask for clarification**: If feedback is unclear, reply to the comment
4. **Don't merge with critical issues**: Address high-priority feedback before merging
5. **Update config as needed**: Adjust review criteria to match your team's standards

## 📚 Resources

- **ritual-pr-infra tool**: https://github.com/ritual-net/ritual-pr-infra
- **Manus AI**: https://manus.im
- **Claude**: https://www.anthropic.com
- **Devin**: https://devin.ai

## 🔐 Security

- All API keys are stored as encrypted GitHub secrets
- Reviewers have read-only access to your repository
- No reviewer can make commits or modify code
- All reviews are audit-logged in PR comment history

---

Generated by: [ritual-pr-infra](https://github.com/ritual-net/ritual-pr-infra)
