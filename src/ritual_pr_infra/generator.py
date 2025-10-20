"""Generator for Ritual PR infrastructure files"""

import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, PackageLoader, select_autoescape


def generate_infrastructure(repo_path: Path):
    """Generate all infrastructure files in the repository"""

    # Create directory structure
    ritual_pr_dir = repo_path / ".ritual-pr"
    prompts_dir = ritual_pr_dir / "prompts"
    shared_prompts_dir = prompts_dir / "shared"
    workflows_dir = repo_path / ".github" / "workflows"

    ritual_pr_dir.mkdir(exist_ok=True)
    prompts_dir.mkdir(exist_ok=True)
    shared_prompts_dir.mkdir(exist_ok=True)
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Copy default config
    templates_dir = Path(__file__).parent / "templates"
    shutil.copy(templates_dir / "config.yml", ritual_pr_dir / "config.yml")

    # Copy default prompts
    for prompt_file in (templates_dir / "prompts").glob("*.md"):
        shutil.copy(prompt_file, shared_prompts_dir / prompt_file.name)

    # Load config
    with open(ritual_pr_dir / "config.yml") as f:
        config = yaml.safe_load(f)

    # Generate workflows
    _generate_workflows(repo_path, config)


def update_workflows(repo_path: Path):
    """Update only workflow files, preserving all prompts

    This is useful when workflow templates have been updated but you want to
    keep your custom prompts unchanged.
    """
    ritual_pr_dir = repo_path / ".ritual-pr"
    config_file = ritual_pr_dir / "config.yml"

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}. Run 'init' first.")

    # Load existing config
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Regenerate only workflows
    _generate_workflows(repo_path, config)


def _generate_workflows(repo_path: Path, config: dict):
    """Internal function to generate workflow files from config"""
    workflows_dir = repo_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Setup Jinja2
    env = Environment(
        loader=PackageLoader("ritual_pr_infra", "templates/workflows"),
        autoescape=select_autoescape(),
    )

    # Generate Manus workflow
    if config.get("manus", {}).get("enabled", False):
        template = env.get_template("manus-pr-review.yml.j2")
        output = template.render(manus=config["manus"])
        (workflows_dir / "manus-pr-review.yml").write_text(output)

    # Generate Claude workflow
    if config.get("claude", {}).get("enabled", False):
        template = env.get_template("claude-pr-review.yml.j2")
        output = template.render(claude=config["claude"])
        (workflows_dir / "claude-pr-review.yml").write_text(output)

    # Generate Devin workflow
    if config.get("devin", {}).get("enabled", False):
        template = env.get_template("devin-pr-review.yml.j2")
        output = template.render(devin=config["devin"])
        (workflows_dir / "devin-pr-review.yml").write_text(output)
