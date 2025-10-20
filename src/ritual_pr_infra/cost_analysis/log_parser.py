"""
Parse Claude workflow logs to extract usage and cost data.
"""

import json
import re


def extract_claude_usage_from_log(log_text: str) -> dict | None:
    """
    Extract usage and cost data from Claude workflow log.

    Args:
        log_text: Full text of workflow log from `gh run view --log`

    Returns:
        Dict with usage data, or None if not found

    Example output:
        {
            "total_cost_usd": 0.23035,
            "usage": {...},
            "modelUsage": {...}
        }
    """
    # Look for the JSON object containing total_cost_usd
    # It appears in logs as a complete JSON object

    # More robust: find the complete JSON structure
    # Search for pattern: {...total_cost_usd...modelUsage...}
    lines = log_text.split("\n")

    for i, line in enumerate(lines):
        if '"total_cost_usd"' in line:
            # Found the line with total_cost_usd
            # Now collect the full JSON object
            json_start = None
            json_end = None
            brace_count = 0

            # Search backwards to find opening brace
            for j in range(i, max(0, i - 50), -1):
                if "{" in lines[j]:
                    json_start = j
                    break

            if json_start is None:
                continue

            # Search forwards to find matching closing brace
            for j in range(json_start, min(len(lines), json_start + 200)):
                brace_count += lines[j].count("{") - lines[j].count("}")
                if brace_count == 0 and "{" in lines[json_start]:
                    json_end = j
                    break

            if json_end is None:
                continue

            # Extract and parse JSON
            json_text = "\n".join(lines[json_start : json_end + 1])

            # Clean up log prefixes
            json_text = re.sub(r"^[^{]*", "", json_text, flags=re.MULTILINE)

            try:
                data = json.loads(json_text)
                if "total_cost_usd" in data and "modelUsage" in data:
                    return data
            except json.JSONDecodeError:
                continue

    return None


def extract_model_usage_from_log(log_text: str) -> dict | None:
    """
    Extract just modelUsage from log (more reliable).

    Returns dict like:
        {
            "claude-sonnet-4-5-20250929": {
                "inputTokens": 27,
                "outputTokens": 4248,
                ...
            }
        }
    """
    pattern = r'"modelUsage":\s*\{[^}]*(?:\{[^}]*\}[^}]*)+\}'

    # Find the modelUsage JSON block
    match = re.search(pattern, log_text, re.DOTALL)
    if match:
        # Extract the matched text
        model_usage_text = "{" + match.group(0).split("{", 1)[1]
        try:
            # Parse just the modelUsage object
            full_obj = json.loads("{" + model_usage_text + "}")
            return full_obj.get("modelUsage")
        except json.JSONDecodeError:
            pass

    # Alternative: line-by-line parsing
    lines = log_text.split("\n")
    for i, line in enumerate(lines):
        if '"modelUsage"' in line:
            # Collect JSON starting from this line
            json_lines = []
            brace_count = 0
            started = False

            for j in range(i, min(len(lines), i + 100)):
                clean_line = re.sub(r'^[^{}"]*', "", lines[j])
                if "{" in clean_line or started:
                    started = True
                    json_lines.append(clean_line)
                    brace_count += clean_line.count("{") - clean_line.count("}")

                    if brace_count == 0 and started:
                        break

            json_text = "\n".join(json_lines)
            try:
                data = json.loads("{" + json_text)
                if "modelUsage" in data:
                    return data["modelUsage"]
            except json.JSONDecodeError:
                pass

    return None
