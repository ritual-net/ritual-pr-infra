"""CLI for Ritual PR Infrastructure"""

from pathlib import Path

import click

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
        click.echo("   - ANTHROPIC_API_KEY")
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


def main():
    cli()
