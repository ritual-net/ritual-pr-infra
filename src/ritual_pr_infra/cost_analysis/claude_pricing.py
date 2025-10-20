"""
Claude API Cost Calculator

Modular implementation for calculating exact costs from Claude API usage data.
Accounts for context window pricing tiers and all token types.
"""

from dataclasses import dataclass


@dataclass
class ClaudePricing:
    """Pricing per million tokens for Claude models."""

    # Standard context window (200K tokens)
    input_standard: float
    output_standard: float
    cache_write_standard: float
    cache_read_standard: float

    # Extended context window (1M tokens) - if different
    input_extended: float | None = None
    output_extended: float | None = None
    cache_write_extended: float | None = None
    cache_read_extended: float | None = None

    context_threshold: int = 200_000  # tokens


# Claude Pricing (October 2025)
# Source: https://www.anthropic.com/pricing
CLAUDE_SONNET_4_5 = ClaudePricing(
    input_standard=3.00,
    output_standard=15.00,
    cache_write_standard=3.75,
    cache_read_standard=0.30,
    context_threshold=200_000,
)

CLAUDE_HAIKU_3_5 = ClaudePricing(
    input_standard=1.00,
    output_standard=5.00,
    cache_write_standard=1.25,
    cache_read_standard=0.30,
    context_threshold=200_000,
)

# Model name mapping
PRICING_MAP = {
    "claude-sonnet-4-5-20250929": CLAUDE_SONNET_4_5,
    "claude-3-5-haiku-20241022": CLAUDE_HAIKU_3_5,
}


@dataclass
class TokenUsage:
    """Token usage for a single model."""

    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    context_window: int = 200_000


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a model."""

    model_name: str
    input_cost: float
    output_cost: float
    cache_read_cost: float
    cache_write_cost: float
    total_cost: float
    token_usage: TokenUsage
    pricing_tier: str  # 'standard' or 'extended'


def calculate_token_cost(tokens: int, price_per_mtok: float, description: str = "") -> float:
    """
    Calculate cost for a number of tokens.

    Args:
        tokens: Number of tokens
        price_per_mtok: Price per million tokens (USD)
        description: Optional description for debugging

    Returns:
        Cost in USD
    """
    cost = (tokens / 1_000_000) * price_per_mtok
    return cost


def calculate_model_cost(
    model_name: str,
    usage: TokenUsage,
) -> CostBreakdown:
    """
    Calculate cost for a single model's usage.

    Args:
        model_name: Claude model name
        usage: Token usage data

    Returns:
        Detailed cost breakdown

    Raises:
        ValueError: If model_name not recognized
    """
    if model_name not in PRICING_MAP:
        raise ValueError(f"Unknown model: {model_name}. Known models: {list(PRICING_MAP.keys())}")

    pricing = PRICING_MAP[model_name]

    # Determine pricing tier based on context window
    is_extended = usage.context_window > pricing.context_threshold
    tier = "extended" if is_extended else "standard"

    # Select appropriate pricing
    if is_extended and pricing.input_extended is not None:
        input_price = pricing.input_extended
        output_price = pricing.output_extended
        cache_write_price = pricing.cache_write_extended
        cache_read_price = pricing.cache_read_extended
    else:
        input_price = pricing.input_standard
        output_price = pricing.output_standard
        cache_write_price = pricing.cache_write_standard
        cache_read_price = pricing.cache_read_standard

    # Calculate costs
    input_cost = calculate_token_cost(usage.input_tokens, input_price, "input")
    output_cost = calculate_token_cost(usage.output_tokens, output_price, "output")
    cache_read_cost = calculate_token_cost(usage.cache_read_tokens, cache_read_price, "cache_read")
    cache_write_cost = calculate_token_cost(usage.cache_creation_tokens, cache_write_price, "cache_write")

    total_cost = input_cost + output_cost + cache_read_cost + cache_write_cost

    return CostBreakdown(
        model_name=model_name,
        input_cost=input_cost,
        output_cost=output_cost,
        cache_read_cost=cache_read_cost,
        cache_write_cost=cache_write_cost,
        total_cost=total_cost,
        token_usage=usage,
        pricing_tier=tier,
    )


def calculate_pr_review_cost(model_usage_data: dict) -> dict[str, CostBreakdown]:
    """
    Calculate total cost for a PR review from Claude API response.

    Args:
        model_usage_data: The 'modelUsage' dict from Claude Code Action output

    Returns:
        Dict mapping model names to their cost breakdowns

    Example input:
        {
            "claude-sonnet-4-5-20250929": {
                "inputTokens": 27,
                "outputTokens": 4248,
                "cacheReadInputTokens": 225020,
                "cacheCreationInputTokens": 25612,
                "contextWindow": 200000,
                "costUSD": 0.227352
            },
            "claude-3-5-haiku-20241022": {
                "inputTokens": 2689,
                "outputTokens": 212,
                "cacheReadInputTokens": 0,
                "cacheCreationInputTokens": 0,
                "contextWindow": 200000,
                "costUSD": 0.0029992
            }
        }
    """
    breakdowns = {}

    for model_name, usage_data in model_usage_data.items():
        usage = TokenUsage(
            input_tokens=usage_data.get("inputTokens", 0),
            output_tokens=usage_data.get("outputTokens", 0),
            cache_read_tokens=usage_data.get("cacheReadInputTokens", 0),
            cache_creation_tokens=usage_data.get("cacheCreationInputTokens", 0),
            context_window=usage_data.get("contextWindow", 200_000),
        )

        breakdown = calculate_model_cost(model_name, usage)
        breakdowns[model_name] = breakdown

    return breakdowns


def format_cost_report(breakdowns: dict[str, CostBreakdown], api_reported_total: float | None = None) -> str:
    """
    Format cost breakdown as human-readable report.

    Args:
        breakdowns: Cost breakdowns by model
        api_reported_total: Total cost reported by API (for verification)

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("CLAUDE PR REVIEW - COST BREAKDOWN")
    report.append("=" * 80)
    report.append("")

    total_calculated = 0.0

    for model_name, breakdown in breakdowns.items():
        report.append(f"Model: {model_name}")
        report.append(
            f"Pricing Tier: {breakdown.pricing_tier} (context: {breakdown.token_usage.context_window:,} tokens)"
        )
        report.append("-" * 80)

        # Token counts
        report.append("Token Usage:")
        report.append(
            f"  Input (fresh):       {breakdown.token_usage.input_tokens:>10,} tokens → ${breakdown.input_cost:>10.6f}"
        )
        report.append(
            f"  Output:              {breakdown.token_usage.output_tokens:>10,} tokens → ${breakdown.output_cost:>10.6f}"
        )
        report.append(
            f"  Cache Read:          {breakdown.token_usage.cache_read_tokens:>10,} tokens → ${breakdown.cache_read_cost:>10.6f}"
        )
        report.append(
            f"  Cache Write:         {breakdown.token_usage.cache_creation_tokens:>10,} tokens → ${breakdown.cache_write_cost:>10.6f}"
        )
        report.append("-" * 80)
        report.append(f"Model Total:                                      ${breakdown.total_cost:>10.6f}")
        report.append("")

        total_calculated += breakdown.total_cost

    report.append("=" * 80)
    report.append(f"TOTAL CALCULATED COST:                            ${total_calculated:>10.6f}")

    if api_reported_total is not None:
        diff = abs(total_calculated - api_reported_total)
        match = "✅ MATCH" if diff < 0.000001 else "❌ MISMATCH"
        report.append(f"API REPORTED COST:                                ${api_reported_total:>10.6f}")
        report.append(f"Difference:                                       ${diff:>10.6f} {match}")

    report.append("=" * 80)

    return "\n".join(report)
