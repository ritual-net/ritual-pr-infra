"""CLI for Ritual PR Infrastructure"""

import json
import os
import re
import subprocess
from pathlib import Path

import click
import yaml

from .generator import generate_infrastructure
from .generator import update_workflows as regenerate_workflows


@click.group()
def cli():
    """Ritual PR Infrastructure - Setup tool for multi-agent PR reviews"""
    pass


@cli.command()
@click.option("--path", default=".", help="Repository path (default: current directory)")
def init(path: str):
    """Initialize Ritual PR review infrastructure in a repository"""
    repo_path = Path(path).resolve()

    if not repo_path.exists():
        click.echo(f"Error: Path {repo_path} does not exist", err=True)
        return

    click.echo(f"Initializing Ritual PR infrastructure in {repo_path}...")

    try:
        generate_infrastructure(repo_path)
        click.echo("✓ Created .ritual-pr/ directory")
        click.echo("✓ Generated prompt templates")
        click.echo("✓ Generated GitHub Actions workflows")
        click.echo("\nNext steps:")
        click.echo("1. Add these secrets to your GitHub repository:")
        click.echo("   - MANUS_API_KEY")
        click.echo("   - MANUS_GITHUB_CONNECTOR_ID")
        click.echo("   - ANTHROPIC_API_KEY")
        click.echo("   - DEVIN_API_KEY")
        click.echo("2. Commit the generated files:")
        click.echo("   git add .ritual-pr/ .github/workflows/")
        click.echo("   git commit -m 'Add Ritual PR review infrastructure'")
        click.echo("3. Push and open a PR to test!")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise


@cli.command()
@click.option("--path", default=".", help="Repository path (default: current directory)")
def update_workflows(path: str):
    """Update GitHub Actions workflows without touching prompts

    Use this when workflow templates have been updated but you want to
    preserve your custom prompts. Only regenerates workflow files from
    your existing .ritual-pr/config.yml.
    """
    repo_path = Path(path).resolve()

    ritual_pr_dir = repo_path / ".ritual-pr"
    if not ritual_pr_dir.exists():
        click.echo("Error: .ritual-pr/ directory not found. Run 'init' first.", err=True)
        return

    config_file = ritual_pr_dir / "config.yml"
    if not config_file.exists():
        click.echo("Error: .ritual-pr/config.yml not found. Run 'init' first.", err=True)
        return

    click.echo(f"Updating workflows in {repo_path}...")
    click.echo("→ Preserving all prompts in .ritual-pr/prompts/")

    try:
        regenerate_workflows(repo_path)
        click.echo("✓ Regenerated GitHub Actions workflows")
        click.echo("✓ Preserved all custom prompts")
        click.echo("\nCommit the updated workflows:")
        click.echo("   git add .github/workflows/")
        click.echo("   git commit -m 'Update PR review workflows'")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise


@cli.command()
@click.argument("pr_url")
@click.option("--path", default=".", help="Repository path (default: current directory)")
def trigger_manus(pr_url: str, path: str):
    """Manually trigger Manus review for a PR (bypasses GitHub Actions)

    PR_URL: GitHub pull request URL (e.g., https://github.com/owner/repo/pull/123)

    This command:
    1. Reads prompts from .ritual-pr/prompts/ in your repository
    2. Sends a review request to Manus API
    3. Returns the task URL where you can track the review

    Useful when GitHub Actions IP addresses are rate-limited by Manus.
    """
    repo_path = Path(path).resolve()

    # Check for .ritual-pr directory
    ritual_pr_dir = repo_path / ".ritual-pr"
    if not ritual_pr_dir.exists():
        click.echo("Error: .ritual-pr/ directory not found. Run 'init' first.", err=True)
        return

    # Parse PR URL
    pr_match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not pr_match:
        click.echo(f"Error: Invalid PR URL: {pr_url}", err=True)
        click.echo("Expected format: https://github.com/owner/repo/pull/123", err=True)
        return

    owner, repo, pr_number = pr_match.groups()
    full_repo = f"{owner}/{repo}"

    click.echo(f"Triggering Manus review for {full_repo}#{pr_number}...")

    # Load config
    config_file = ritual_pr_dir / "config.yml"
    if not config_file.exists():
        click.echo("Error: .ritual-pr/config.yml not found.", err=True)
        return

    with open(config_file) as f:
        config = yaml.safe_load(f)

    if not config.get("manus", {}).get("enabled", False):
        click.echo("Error: Manus is disabled in config.yml", err=True)
        return

    # Load prompts
    prompts_dir = ritual_pr_dir / "prompts"
    prompt_files = config["manus"]["prompts"]
    combined_prompt = ""

    for prompt_file in prompt_files:
        prompt_path = prompts_dir / prompt_file
        if not prompt_path.exists():
            click.echo(f"Warning: Prompt file not found: {prompt_file}", err=True)
            continue
        with open(prompt_path) as f:
            combined_prompt += f.read() + "\n\n"

    # Get secrets from environment
    api_key = os.getenv("MANUS_API_KEY")
    connector_id = os.getenv("MANUS_GITHUB_CONNECTOR_ID")

    if not api_key:
        click.echo("Error: MANUS_API_KEY environment variable not set", err=True)
        click.echo("Set it with: export MANUS_API_KEY=your-key", err=True)
        return

    if not connector_id:
        click.echo("Error: MANUS_GITHUB_CONNECTOR_ID environment variable not set", err=True)
        click.echo("Get it from https://manus.im → Connectors → GitHub", err=True)
        return

    # Build instructions
    instructions = f"""

IMPORTANT INSTRUCTIONS FOR MANUS AI:
1. Read existing PR comments to check if you have already reviewed this PR
2. If you have reviewed before, focus only on NEW changes since your last review
3. After completing your review, USE THE GITHUB CONNECTOR to post a comment on this PR
4. Start your comment with: MANUS AI REVIEW
5. Include your findings, recommendations, and action items
6. Repository: {full_repo}, PR Number: {pr_number}"""

    # Build JSON payload
    payload = {
        "prompt": f"{combined_prompt}\nPull Request: {pr_url}{instructions}",
        "taskMode": "agent",
        "connectors": [connector_id],
        "agentProfile": "quality",
        "createShareableLink": True,
    }

    click.echo("→ Sending request to Manus API...")
    click.echo(f"  Payload size: {len(json.dumps(payload))} bytes")

    # Send request
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-w",
            "\n__HTTP__%{http_code}",
            "--request",
            "POST",
            "--url",
            "https://api.manus.ai/v1/tasks",
            "--header",
            f"API_KEY: {api_key}",
            "--header",
            "Content-Type: application/json",
            "--data",
            json.dumps(payload),
        ],
        capture_output=True,
        text=True,
    )

    # Parse response
    lines = result.stdout.strip().split("\n")
    http_code = lines[-1].replace("__HTTP__", "") if lines else "unknown"
    response_body = "\n".join(lines[:-1]) if len(lines) > 1 else ""

    if http_code == "200":
        try:
            response_json = json.loads(response_body)
            task_url = response_json.get("task_url", "")
            share_url = response_json.get("share_url", "")

            click.echo("✅ Success! Manus review task created")
            click.echo(f"📊 Task URL: {task_url}")
            click.echo(f"🔗 Share URL: {share_url}")
            click.echo("\nManus will review the PR and post comments when complete.")
        except json.JSONDecodeError:
            click.echo(f"✅ HTTP 200 but couldn't parse response: {response_body}")
    else:
        click.echo(f"❌ Failed with HTTP {http_code}", err=True)
        click.echo(f"Response: {response_body}", err=True)


def main():
    cli()
