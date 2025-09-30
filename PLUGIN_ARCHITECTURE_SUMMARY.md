# Plugin Block Architecture - Quick Summary

**Status:** Prototype Complete ✅
**Date:** 2025-09-30
**Full Document:** [PLUGIN_BLOCK_ARCHITECTURE.md](./PLUGIN_BLOCK_ARCHITECTURE.md)

---

## TL;DR

We're transitioning blocks from **6-file duplicated code** → **1-file plugins that import from pipeline**.

**Before:**
```
blocks/analysis/source_localization/  (6 files, 48KB, duplicated code)
```

**After:**
```
blocks/source_localization_plugin.py  (1 file, 20KB, imports from pipeline)
```

---

## Key Changes

### 1. Single File Per Block
Everything in one file:
- Documentation (docstring)
- Metadata (`__block_metadata__` dict)
- Mixin class
- No duplication!

### 2. Imports from Pipeline
```python
# NO duplication - imports from pipeline!
from autoclean.calc.source import estimate_source_function_raw
```

### 3. Task-Aligned Pattern
Blocks work EXACTLY like task files:
- Drop file in `blocks/` directory
- Pipeline auto-discovers it
- Methods available to all tasks

---

## Files Created

1. **PLUGIN_BLOCK_ARCHITECTURE.md** (50+ pages)
   - Complete architecture specification
   - Design principles
   - Migration guide
   - Implementation roadmap

2. **source_localization_plugin.py** (prototype)
   - Working single-file block
   - Imports from pipeline (zero duplication)
   - Comprehensive documentation
   - Demonstrates new pattern

3. **PLUGIN_ARCHITECTURE_SUMMARY.md** (this file)
   - Quick reference
   - Key decisions
   - Next steps

---

## Prototype Usage

**Test the prototype:**
```bash
# Copy to test location
cp blocks/source_localization_plugin.py ~/.autoclean/blocks/

# Use in a task
class MyTask(Task):
    def run(self):
        self.import_raw()
        self.apply_source_localization()  # Method from plugin!
```

**Expected output:**
```
✓ Source localization plugin loaded (MNE v1.6.0)
✓ Algorithms available from autoclean.calc.source
```

---

## Why This Matters

### Problem We're Solving
- ❌ **Code duplication** between pipeline and task-registry
- ❌ **Manual synchronization** required for every change
- ❌ **Complex structure** (6 files per block)
- ❌ **Can't distribute** as standalone plugins

### Solution
- ✅ **Zero duplication** - blocks import from pipeline
- ✅ **Auto-sync** - pipeline is single source of truth
- ✅ **Simple** - one file per block
- ✅ **Distributable** - copy file or `pip install`

---

## Comparison

| Aspect | Current (Multi-File) | Proposed (Plugin) |
|--------|---------------------|-------------------|
| Files | 6 | 1 |
| Size | 48 KB | 20 KB |
| Duplication | YES | NO |
| Sync needed | Manual | Automatic |
| Distribution | Complex | Simple |
| User experience | Confusing | Clear |

---

## Next Steps

### Phase 1: Validation (Week 1)
- [x] Create architecture document
- [x] Build prototype single-file block
- [ ] Test prototype with pipeline
- [ ] Validate no duplication
- [ ] Document lessons learned

### Phase 2: Core Blocks (Weeks 2-4)
- [ ] Migrate 5 analysis blocks
- [ ] Migrate 2 signal processing blocks
- [ ] Update documentation
- [ ] Deprecate old structure

### Phase 3: Ecosystem (Weeks 5-8)
- [ ] PyPI distribution
- [ ] CLI commands (`blocks install`, `blocks list`)
- [ ] Community guidelines
- [ ] Block marketplace

---

## Design Principles

1. **Zero Duplication** - Always import from pipeline, never copy code
2. **Single File** - One block = one Python file
3. **Task Alignment** - Blocks work exactly like task files
4. **Discoverability** - Pipeline auto-finds blocks
5. **Backward Compatible** - Existing code continues to work

---

## Key Decisions

### Decision 1: Import from Pipeline (Not Duplicate)
**Rationale:** Pipeline is the source of truth. Blocks are lightweight wrappers.

**Before:**
```python
# blocks/.../algorithm.py (DUPLICATE of calc/source.py)
def estimate_source_function_raw(...):
    # 300 lines of duplicated code
```

**After:**
```python
# blocks/source_localization_plugin.py
from autoclean.calc.source import estimate_source_function_raw  # Import!
```

### Decision 2: Single File (Not Multi-File)
**Rationale:** Simplicity, portability, user-friendliness.

**Benefits:**
- Easier to understand (everything in one place)
- Easier to distribute (copy one file)
- Easier to version (git-friendly)
- Easier to contribute (one PR, one file)

### Decision 3: Align with Task Files
**Rationale:** Users already understand task files. Use same pattern.

**Task files:**
```python
from autoclean.core.task import Task
class MyTask(Task): pass
```

**Block files:**
```python
from autoclean.calc.source import estimate_source_function_raw
class SourceLocalizationMixin: pass
```

Same import-based pattern, just different base classes!

---

## FAQ

**Q: What happens to existing multi-file blocks?**
A: They'll be moved to `deprecated/` in v2.4.0, removed in v3.0.0. Migration guide provided.

**Q: Do I need to update my tasks?**
A: No! Tasks continue to work unchanged. New blocks add methods automatically.

**Q: How do I install a plugin block?**
A: Three ways:
1. Copy file to `~/.autoclean/blocks/`
2. `pip install autocleaneeg-block-*` (future)
3. Clone task-registry and add to path

**Q: Can I still use the pipeline's internal mixins?**
A: Yes! Internal mixins continue to work. Plugin blocks are additive, not breaking.

**Q: What if a plugin block has a bug?**
A: Fix the algorithm in the pipeline (`calc/source.py`). The block automatically uses the fixed version (no sync needed!).

**Q: Can I create my own plugin blocks?**
A: Yes! Follow the pattern in `source_localization_plugin.py`. Drop your file in `blocks/` and it works.

---

## Example: Creating a Custom Block

```python
# my_custom_block.py
"""My custom analysis block."""

from autoclean.calc.fooof_analysis import fit_fooof_models

__block_metadata__ = {
    "name": "my_custom_block",
    "version": "1.0.0",
    "category": "analysis",
}

class MyCustomMixin:
    def apply_my_analysis(self):
        """My custom analysis method."""
        # Use algorithms from pipeline
        results = fit_fooof_models(...)
        return results
```

**That's it!** Drop in `~/.autoclean/blocks/` and use:
```python
class MyTask(Task):
    def run(self):
        self.apply_my_analysis()  # Works!
```

---

## Resources

- **Full Architecture Doc:** [PLUGIN_BLOCK_ARCHITECTURE.md](./PLUGIN_BLOCK_ARCHITECTURE.md) (50+ pages)
- **Prototype Block:** [blocks/source_localization_plugin.py](./blocks/source_localization_plugin.py)
- **Migration Script:** Coming in Phase 2
- **Testing Guide:** Coming in Phase 2

---

## Feedback

Questions? Concerns? Suggestions?

- **GitHub Issues:** https://github.com/cincibrainlab/autocleaneeg-task-registry/issues
- **Email:** ernest.pedapati@cchmc.org
- **Discussions:** https://github.com/cincibrainlab/autocleaneeg-task-registry/discussions

---

## Status Summary

✅ **Architecture planned** - 50+ page specification document
✅ **Prototype built** - Working single-file block
⏳ **Testing needed** - Validate with pipeline discovery
⏳ **Migration planned** - Roadmap for all blocks
⏳ **Documentation needed** - User guide and contribution guide

**Ready for review and testing!**