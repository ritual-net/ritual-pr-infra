# Engineering Standards Review

Review this pull request against core engineering principles and standards:

## Architecture & Design
- Does the design prioritize maintainability and safe failure modes with thoughtful autohealing?
- Are compute, memory, I/O, and networking resources used reasonably and efficiently?
- Is the right framework/tool being used for the job (polyglot when needed)?

## Code Quality & Correctness
- Are there sufficient unit, regression, fuzz, and integration tests?
- Is state localized as tightly as possible to prove code correctness?
- Are representational invariants, pre-conditions, and post-conditions annotated (especially in mission-critical code)?
- Is multithreading/multiprocessing used sparingly and only when needed?

## System Design
- Are failure modes safe and structured?
- Is the design easy to maintain by other team members?

## Code Hygiene (FLAG FOR JUSTIFICATION)

These patterns are not necessarily wrong, but require explicit justification from the author:

### Backward Compatibility
Flag any code that appears to maintain backward compatibility without explicit justification:
- Format fallbacks (`if new_field else old_field`)
- Version conditionals (`if version >= 2 else legacy`)
- Comments like `// For backward compatibility` or `# Legacy support`
- Try-except fallbacks to old methods

**Ask:** What consumer requires this? What is the migration timeline?

### "Make It Work" Patterns
Flag code that transforms data to accommodate library differences:
- Prefix stripping/adding (e.g., `key[1:]` to remove 0x04)
- Encoding conversions for library compatibility
- Comments like `// library X expects...` or `# Convert for compatibility`

**Ask:** Why can't we enforce a single canonical format? Which format is the source of truth?

### Over-Engineering
Flag excessive conditionals that may indicate unnecessary complexity:
- Feature detection (`hasattr` checks for method existence)
- Environment-based behavior switching
- Type sniffing to handle multiple input formats

**Ask:** Is this complexity necessary? Can we simplify to a single code path?

## Documentation
- Is the code well-documented with clear explanations?
- Are diagrams provided where they would aid understanding?

## Security & Integrity
- Are all commits and artifacts properly signed (for OSS components)?

Provide specific, actionable feedback on any violations or areas for improvement. For code hygiene flags, request explicit justification rather than blocking the PR.

