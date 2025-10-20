"""Tests for generator module"""

import tempfile
from pathlib import Path

from ritual_pr_infra.generator import generate_infrastructure


def test_generate_infrastructure():
    """Test that generate_infrastructure creates all expected files"""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Generate infrastructure
        generate_infrastructure(repo_path)

        # Check that directories were created
        assert (repo_path / ".ritual-pr").exists()
        assert (repo_path / ".ritual-pr" / "prompts").exists()
        assert (repo_path / ".ritual-pr" / "prompts" / "shared").exists()
        assert (repo_path / ".github" / "workflows").exists()

        # Check that config was created
        assert (repo_path / ".ritual-pr" / "config.yml").exists()

        # Check that default prompts were created
        assert (repo_path / ".ritual-pr" / "prompts" / "shared" / "engineering.md").exists()
        assert (repo_path / ".ritual-pr" / "prompts" / "shared" / "fsm-verification.md").exists()

        # Check that workflows were created
        assert (repo_path / ".github" / "workflows" / "manus-pr-review.yml").exists()
        assert (repo_path / ".github" / "workflows" / "claude-pr-review.yml").exists()

        # Check workflow content
        manus_workflow = (repo_path / ".github" / "workflows" / "manus-pr-review.yml").read_text()
        assert "name: Manus PR Review" in manus_workflow
        assert "MANUS_API_KEY" in manus_workflow

        claude_workflow = (repo_path / ".github" / "workflows" / "claude-pr-review.yml").read_text()
        assert "name: Claude PR Review" in claude_workflow
        assert "ANTHROPIC_API_KEY" in claude_workflow


def test_generate_infrastructure_existing_files():
    """Test that generate_infrastructure handles existing files gracefully"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Create .github/workflows directory manually
        (repo_path / ".github" / "workflows").mkdir(parents=True)

        # Generate infrastructure
        generate_infrastructure(repo_path)

        # Should still succeed
        assert (repo_path / ".ritual-pr" / "config.yml").exists()
        assert (repo_path / ".github" / "workflows" / "manus-pr-review.yml").exists()
