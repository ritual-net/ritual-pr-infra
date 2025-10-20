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
