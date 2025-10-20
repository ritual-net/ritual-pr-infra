#!/usr/bin/env python3
"""
Test cost calculator against real Claude workflow data.

Usage:
    python scripts/test_cost_calculator.py <github_run_id>

Example:
    python scripts/test_cost_calculator.py 18667419031
"""

import json
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ritual_pr_infra.cost_analysis.claude_pricing import (
    calculate_pr_review_cost,
    format_cost_report,
)
from ritual_pr_infra.cost_analysis.log_parser import (
    extract_claude_usage_from_log,
    extract_model_usage_from_log,
)


def get_workflow_log(run_id: str, repo: str | None = None) -> str:
    """Fetch workflow log using gh CLI."""
    print(f"Fetching workflow log for run {run_id}...")

    cmd = ["gh", "run", "view", run_id, "--log"]
    if repo:
        cmd.extend(["--repo", repo])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print(f"Error fetching log: {result.stderr}")
        sys.exit(1)

    return result.stdout


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_cost_calculator.py <github_run_id> [repo]")
        print("\nExamples:")
        print("  python scripts/test_cost_calculator.py 18667419031")
        print("  python scripts/test_cost_calculator.py 18667419031 ritual-net/ritual-reth-nodebuilder-internal")
        sys.exit(1)

    run_id = sys.argv[1]
    repo = sys.argv[2] if len(sys.argv) > 2 else None

    # Fetch log
    log_text = get_workflow_log(run_id, repo)
    print(f"✓ Fetched log ({len(log_text):,} characters)\n")

    # Extract usage data
    print("Parsing log for usage data...")
    usage_data = extract_claude_usage_from_log(log_text)

    if not usage_data:
        print("❌ Could not find usage data in log")
        print("\nTrying alternative parser...")
        model_usage = extract_model_usage_from_log(log_text)

        if model_usage:
            print("✓ Found modelUsage data\n")
            usage_data = {"modelUsage": model_usage, "total_cost_usd": None}
        else:
            print("❌ Could not extract usage data from log")
            sys.exit(1)
    else:
        print("✓ Extracted complete usage data\n")

    # Save raw data for inspection
    with open("/tmp/claude_usage_data.json", "w") as f:
        json.dump(usage_data, f, indent=2)
    print("Raw data saved to /tmp/claude_usage_data.json\n")

    # Calculate costs
    print("Calculating costs...\n")
    model_usage = usage_data.get("modelUsage", {})

    if not model_usage:
        print("❌ No modelUsage data found")
        sys.exit(1)

    breakdowns = calculate_pr_review_cost(model_usage)

    # Get API-reported cost for verification
    api_reported = usage_data.get("total_cost_usd")

    # Generate report
    report = format_cost_report(breakdowns, api_reported)
    print(report)

    # Additional analysis
    print("\n" + "=" * 80)
    print("COST ANALYSIS")
    print("=" * 80)

    total_tokens = 0
    total_cost = 0.0

    for model_name, breakdown in breakdowns.items():
        model_total_tokens = (
            breakdown.token_usage.input_tokens
            + breakdown.token_usage.output_tokens
            + breakdown.token_usage.cache_read_tokens
            + breakdown.token_usage.cache_creation_tokens
        )
        total_tokens += model_total_tokens
        total_cost += breakdown.total_cost

        print(f"\n{model_name}:")
        print(f"  Total Tokens: {model_total_tokens:,}")
        print(f"  Cost per 1K tokens: ${(breakdown.total_cost / model_total_tokens * 1000):.4f}")

        # Cost breakdown percentages
        if breakdown.total_cost > 0:
            print("  Cost breakdown:")
            print(f"    Input:       {(breakdown.input_cost / breakdown.total_cost * 100):>5.1f}%")
            print(f"    Output:      {(breakdown.output_cost / breakdown.total_cost * 100):>5.1f}%")
            print(f"    Cache Read:  {(breakdown.cache_read_cost / breakdown.total_cost * 100):>5.1f}%")
            print(f"    Cache Write: {(breakdown.cache_write_cost / breakdown.total_cost * 100):>5.1f}%")

    print(f"\nTotal Tokens (all models): {total_tokens:,}")
    print(f"Total Cost: ${total_cost:.6f}")

    if api_reported:
        diff = abs(total_cost - api_reported)
        accuracy = (1 - diff / api_reported) * 100 if api_reported > 0 else 0
        print(f"Accuracy: {accuracy:.2f}%")

        if diff < 0.000001:
            print("✅ Calculator matches API-reported cost perfectly!")
        elif diff < 0.01:
            print("✅ Calculator matches API-reported cost (within 1¢)")
        else:
            print(f"⚠️ Calculator differs from API by ${diff:.6f}")

    print("=" * 80)


if __name__ == "__main__":
    main()

