"""CLI for Ritual PR Infrastructure"""

from pathlib import Path

import click

from .generator import generate_infrastructure


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


def main():
    cli()
