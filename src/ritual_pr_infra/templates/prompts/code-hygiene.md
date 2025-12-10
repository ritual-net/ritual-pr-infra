# Code Hygiene Review

Review this pull request for code patterns that require explicit justification.

**Note:** These patterns are not necessarily wrong, but they add complexity and should be consciously chosen rather than reflexively added.

## Backward Compatibility Detection

Flag any code that appears to maintain backward compatibility:

### Patterns to Detect

1. **Format fallbacks:**
   ```python
   if "new_field" in data:
       return data["new_field"]
   elif "old_field" in data:  # ⚠️ FLAG THIS
       return data["old_field"]
   ```

2. **Version conditionals:**
   ```go
   if version >= 2 {
       // new behavior
   } else {  // ⚠️ FLAG THIS
       // old behavior
   }
   ```

3. **Backward compatibility comments:**
   - `// For backward compatibility`
   - `# Legacy support`
   - `// TODO: Remove after migration`
   - `/* Deprecated but still supported */`

4. **Try-except fallbacks:**
   ```python
   try:
       result = new_method()
   except:  # ⚠️ FLAG THIS
       result = old_method()  # fallback
   ```

### Required Justification
When flagged, ask the author to explain:
- What consumer requires the old format/behavior?
- What is the migration timeline?
- Is there a tracking issue for removal?

If no justification exists, suggest removing the backward compatibility code.

---

## "Make It Work" Pattern Detection

Flag code that transforms data to accommodate library differences:

### Patterns to Detect

1. **Prefix stripping/adding:**
   ```python
   # Strip 0x04 prefix because library X expects raw key
   key = public_key[1:] if public_key[0] == 0x04 else public_key  # ⚠️ FLAG
   ```

2. **Encoding conversions for library compatibility:**
   ```go
   // Convert because libraryA returns hex but libraryB expects bytes
   data = hex.DecodeString(result)  // ⚠️ FLAG if only done for library compat
   ```

3. **Silent format normalization:**
   ```python
   def process(data):
       if isinstance(data, str):
           data = data.encode()  # ⚠️ FLAG - why accept both?
       # ...
   ```

4. **Comments indicating library workarounds:**
   - `// eciespy expects...`
   - `# eth_keys returns... so we need to...`
   - `// Convert for compatibility with...`

### Required Justification
When flagged, ask the author to explain:
- Why can't we enforce a single canonical format?
- Which format is the "source of truth"?
- Can the transformation be pushed to the boundary/caller instead?

---

## Conditional Complexity

Flag excessive conditional logic that may indicate over-engineering:

### Patterns to Detect

1. **Feature detection:**
   ```python
   if hasattr(obj, 'new_method'):
       obj.new_method()
   else:
       obj.old_method()  # ⚠️ FLAG
   ```

2. **Environment-based behavior switching:**
   ```python
   if os.environ.get("USE_LEGACY_MODE"):  # ⚠️ FLAG
       # old path
   else:
       # new path
   ```

3. **Type sniffing:**
   ```python
   if isinstance(data, NewFormat):
       # handle new
   elif isinstance(data, OldFormat):  # ⚠️ FLAG
       # handle old
   ```

### Required Justification
When flagged, ask:
- Is this complexity necessary for the current requirements?
- Can we simplify to a single code path?
- Who/what specifically needs the alternative path?

---

## Review Output Format

For each flagged pattern, output:

```
⚠️ CODE HYGIENE FLAG: [Pattern Type]
Location: [file:line]
Pattern: [brief description]
Question for author: [specific question requiring justification]
```

If the author provides valid justification (migration plan, specific consumer, tracking issue), the flag can be resolved. If no justification exists, recommend simplifying the code.
