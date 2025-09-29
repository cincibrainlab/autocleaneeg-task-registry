# Testing Guide

Guide for testing task registry functionality and validation.

## Registry Validation

The registry uses automated validation to ensure task files match registry entries.

### CI Validation

On every pull request and push to main:
```bash
python scripts/validate_registry.py
```

**Checks performed:**
- `registry.json` exists and is valid JSON
- Registry version field equals 1
- All task entries have unique names
- All task paths are unique
- All registry paths point to existing files in `tasks/`
- All `.py` files in `tasks/` are registered (except `__init__.py`)

### Local Testing

```bash
# From repository root
python scripts/validate_registry.py
```

**Expected output:**
```
registry.json matches tasks directory
```

**Exit codes:**
- `0` - All validation passed
- `1` - Validation errors found (details in stderr)

## Task File Validation

### Manual Testing with test_export.py

The repository includes a test script for validating task exports:

```bash
# Location: root directory (deprecated, will be removed)
python test_export.py
```

**Purpose:** Tests task file import and basic validation

**Usage:**
1. Add your task file to `tasks/<category>/`
2. Update `registry.json` with task entry
3. Run validation script
4. Check for import errors or schema issues

**Note:** This script will be deprecated in favor of pytest-based tests.

## Integration Testing

### Task Wizard Backend

The repository includes a Cloudflare Worker backend (`src/`) for Task Wizard integration.

**Local development:**
```bash
npm install
npm run dev
```

**Type checking:**
```bash
npm run check
```

**Deploy to preview:**
```bash
npm run deploy
```

### API Endpoints

**GET /api/registry**
- Returns current registry.json contents
- Includes commit hash for versioning

**POST /api/tasks/pr**
- Creates pull request with new/updated task
- Requires GitHub App authentication
- Validates task format before submission

## CI/CD Pipeline

### GitHub Actions Workflows

**registry-ci.yml**
- Triggers: Pull requests, pushes to main
- Steps:
  1. Checkout repository
  2. Set up Python 3.11
  3. Validate registry entries
  4. Stamp commit hash (main branch only)
  5. Auto-commit updated registry.json

**claude-code-review.yml**
- Automated code review using Claude
- Checks task quality and best practices

### Commit Hash Stamping

After push to main, CI runs:
```bash
python scripts/stamp_registry_commit.py
```

Updates `registry.json`:
```json
{
  "version": 1,
  "commit": "abc123def456...",
  "tasks": [...]
}
```

## Testing Checklist

Before submitting a new task:

- [ ] Task file follows v2025.09 schema pattern
- [ ] Task added to `registry.json` with category and description
- [ ] Run `python scripts/validate_registry.py` locally
- [ ] Import task in Python (check for syntax errors)
- [ ] Verify EOG configuration uses full dict format
- [ ] Check all steps present in config (even if disabled)
- [ ] Test with sample data (if available)

## Common Issues

### "registry path does not exist"
**Cause:** Task file path in registry.json doesn't match actual file location
**Fix:** Update path in registry.json or move file to match path

### "task files missing from registry"
**Cause:** `.py` file exists in tasks/ but not registered
**Fix:** Add entry to registry.json

### "duplicate task name/path"
**Cause:** Same name or path used twice in registry
**Fix:** Ensure unique names and paths for all tasks

## Future Improvements

Planned testing enhancements:
- Migrate to pytest framework
- Add task schema validation tests
- Add config parameter validation
- Integration tests for Cloudflare Worker
- End-to-end Task Wizard workflow tests