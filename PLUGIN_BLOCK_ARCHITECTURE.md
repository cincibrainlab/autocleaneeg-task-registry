# Plugin Block Architecture Plan
## AutoClean EEG - Task-Registry Plugin System

**Document Version:** 1.0
**Date:** 2025-09-30
**Status:** Architecture Proposal
**Authors:** Architecture design session with autocleaneeg_pipeline team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Problem Statement](#problem-statement)
4. [Proposed Architecture](#proposed-architecture)
5. [Design Principles](#design-principles)
6. [Technical Specification](#technical-specification)
7. [Migration Path](#migration-path)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Code Examples](#code-examples)
10. [Testing Strategy](#testing-strategy)
11. [Distribution Model](#distribution-model)
12. [Backwards Compatibility](#backwards-compatibility)
13. [Future Extensions](#future-extensions)
14. [References](#references)

---

## Executive Summary

### Vision
Transform the autocleaneeg-task-registry from a documentation/reference repository into a **true plugin ecosystem** where processing blocks are self-contained, discoverable Python files that extend the pipeline without code duplication.

### Key Innovation
**Align blocks with the existing task file pattern** - blocks become single-file plugins that import from the pipeline rather than duplicating code, using the same discovery mechanism that already works for task files.

### Benefits
- ✅ **Zero duplication** - blocks import from pipeline, no copied code
- ✅ **Simple distribution** - one file = one block
- ✅ **Familiar pattern** - users already understand task files
- ✅ **Auto-discovery** - works like task discovery
- ✅ **Version control** - git-friendly single files
- ✅ **Easy contribution** - drop a file, submit PR
- ✅ **Minimal changes** - leverages existing infrastructure

### Impact
- **Developers**: No more manual synchronization between repos
- **Users**: Simple plugin installation (copy file or `pip install`)
- **Scientists**: Clear provenance and versioning
- **Maintainers**: Single source of truth in pipeline

---

## Current State Analysis

### Existing Architecture (As of v2.3.0)

#### Pipeline Repository Structure
```
autocleaneeg_pipeline/
├── src/autoclean/
│   ├── calc/
│   │   ├── source.py                    # ← Core algorithms
│   │   └── fooof_analysis.py
│   ├── mixins/
│   │   ├── __init__.py                  # ← Auto-discovery system
│   │   ├── signal_processing/
│   │   │   └── source_localization.py   # ← Imports from calc/
│   │   └── analysis/
│   │       ├── fooof_analysis.py
│   │       ├── source_psd.py
│   │       └── source_connectivity.py
│   └── core/
│       └── task.py                       # ← Task base class
```

**How it works:**
1. **Algorithms** in `calc/` contain scientific implementations
2. **Mixins** in `mixins/` provide user-facing interface
3. **Auto-discovery** scans `mixins/` for `*Mixin` classes
4. **Task class** inherits from ALL discovered mixins via `class Task(ABC, *DISCOVERED_MIXINS)`
5. **User tasks** inherit from `Task` and get all methods

#### Task-Registry Repository Structure
```
autocleaneeg-task-registry/
├── blocks/
│   └── analysis/
│       └── source_localization/
│           ├── algorithm.py      # ← DUPLICATE of calc/source.py
│           ├── mixin.py          # ← DUPLICATE of mixins/.../source_localization.py
│           ├── manifest.json     # ← Metadata
│           ├── schema.py         # ← Config validation
│           └── README.md         # ← Documentation
└── examples/
    └── analysis/
        └── source_localization/
            └── SourceLocalization_Raw.py   # ← Task file (imports from pipeline!)
```

**Key Observation:** Task files in `examples/` already work as plugins! They:
- Import from pipeline: `from autoclean.core.task import Task`
- Are self-contained single files
- Get discovered and loaded by the pipeline
- Work perfectly without duplication

**Problem:** Blocks in `blocks/` do NOT work like tasks - they duplicate code!

### How Task Files Work Today (The Model to Follow)

```python
# examples/analysis/source_localization/SourceLocalization_Raw.py
from autoclean.core.task import Task  # ← Import from pipeline

config = {  # ← Module-level config
    "apply_source_localization": {
        "enabled": True,
        "value": {"method": "MNE", "lambda2": 0.111}
    }
}

class SourceLocalization_Raw(Task):  # ← Inherits Task (has all mixins)
    def run(self):
        self.import_raw()
        self.apply_source_localization()  # ← Method from mixin
```

**Why this works:**
1. ✅ Single file - easy to understand, copy, share
2. ✅ Imports from pipeline - no duplication
3. ✅ Config co-located - clear what parameters do
4. ✅ Self-documenting - docstrings explain usage
5. ✅ Pipeline discovers it - via task file scanning

---

## Problem Statement

### The Duplication Problem

**Today we maintain DUPLICATE code in two places:**

| Component | Pipeline Location | Task-Registry Location | Problem |
|-----------|------------------|----------------------|---------|
| Algorithm | `src/autoclean/calc/source.py` | `blocks/.../algorithm.py` | Bug fixes must be applied to BOTH |
| Mixin | `src/autoclean/mixins/.../source_localization.py` | `blocks/.../mixin.py` | API changes must be synchronized |
| Subject ID pattern | Both locations | Both locations | We just fixed this in BOTH repos! |

**Real Example from This Session:**
- Fixed subject ID extraction bug
- Had to update 4 files in pipeline
- Had to update 6 files in task-registry
- Manual synchronization required
- Easy to miss locations

### The Synchronization Problem

**Current workflow for any change:**
1. Develop feature in pipeline
2. Test in pipeline
3. Commit to pipeline
4. Copy changed code to task-registry
5. Update task-registry
6. Commit to task-registry
7. Keep both repos in sync forever

**What goes wrong:**
- Forgetting to sync
- Partial syncs (some files updated, others missed)
- Version skew (registry lags behind pipeline)
- Testing complexity (which version is running?)

### The Documentation Problem

**Current state:**
- Task-registry README files document the block interface
- But the actual implementation is in the pipeline
- Documentation can drift from implementation
- Users confused about which is "source of truth"

### The Distribution Problem

**Blocks can't be distributed as plugins because:**
- They require specific directory structure (6 files)
- They import from themselves (local relative imports)
- They duplicate pipeline code (can't update independently)
- No versioning mechanism
- No dependency declaration

---

## Proposed Architecture

### Core Concept: Blocks = Task-Like Plugins

**Key Insight:** Task files ALREADY solve this problem. Blocks should work the SAME way.

```
Current:  Blocks duplicate pipeline code, complex multi-file structure
Proposed: Blocks are single files that import from pipeline, just like tasks
```

### Single-File Block Format

```python
# task-registry/blocks/source_localization.py  ← SINGLE FILE!
"""Source localization block for AutoClean EEG.

Provides MNE minimum norm estimation for projecting sensor-space EEG
to cortical sources using the fsaverage template brain.

Block Metadata
--------------
name: source_localization
version: 1.0.0
category: analysis
author: Cincinnati Children's Hospital - Brain Lab
license: MIT
requires: autoclean>=2.3.0, mne>=1.6.0

Scientific References
---------------------
Hämäläinen MS & Ilmoniemi RJ (1994). Interpreting magnetic fields
of the brain: minimum norm estimates. Medical & Biological Engineering
& Computing, 32(1), 35-42.

Examples
--------
>>> class MyTask(Task):
...     def run(self):
...         self.import_raw()
...         self.apply_source_localization()  # ← Method from this block
"""

from typing import Union, Optional
from pathlib import Path
import mne

# Import algorithms from pipeline (NO DUPLICATION!)
from autoclean.calc.source import (
    estimate_source_function_raw,
    estimate_source_function_epochs,
)
from autoclean.io.export import save_stc_to_file

# Block metadata (replaces manifest.json)
__block_metadata__ = {
    "name": "source_localization",
    "version": "1.0.0",
    "category": "analysis",
    "author": "Cincinnati Children's Hospital - Brain Lab",
    "license": "MIT",
    "requires": {
        "autoclean": ">=2.3.0",
        "mne": ">=1.6.0",
    },
    "provides_methods": ["apply_source_localization"],
    "config_keys": ["apply_source_localization"],
    "references": [
        {
            "authors": "Hämäläinen MS & Ilmoniemi RJ",
            "year": 1994,
            "title": "Interpreting magnetic fields of the brain: minimum norm estimates",
            "journal": "Medical & Biological Engineering & Computing",
            "volume": "32(1)",
            "pages": "35-42",
            "doi": "10.1007/BF02512476",
        }
    ],
}


class SourceLocalizationMixin:
    """Mixin providing source localization functionality to Task classes.

    This mixin is automatically discovered and added to the Task base class
    when the block is installed. It provides the apply_source_localization()
    method to all task instances.
    """

    def apply_source_localization(
        self,
        data: Union[mne.io.Raw, mne.Epochs, None] = None,
        method: str = "MNE",
        lambda2: float = 1.0 / 9.0,
        pick_ori: str = "normal",
        n_jobs: int = 10,
        save_stc: bool = False,
        stage_name: str = "apply_source_localization",
    ) -> Union[mne.SourceEstimate, list]:
        """Apply MNE source localization to estimate cortical sources.

        Parameters
        ----------
        data : Raw or Epochs, optional
            EEG data to process. If None, uses self.raw or self.epochs
        method : str
            Source estimation method: "MNE", "dSPM", or "sLORETA"
        lambda2 : float
            Regularization parameter (inverse of SNR^2)
        pick_ori : str
            Source orientation constraint: "normal" or None
        n_jobs : int
            Number of parallel jobs for forward solution
        save_stc : bool
            Whether to save vertex-level STC files (warning: 2.3GB)
        stage_name : str
            Name for tracking and exports

        Returns
        -------
        stc : SourceEstimate or list of SourceEstimate
            Source estimates with cortical activations

        Raises
        ------
        ValueError
            If no input data found or invalid parameters
        RuntimeError
            If source localization fails

        Examples
        --------
        >>> class MyTask(Task):
        ...     def run(self):
        ...         self.import_raw()
        ...         self.apply_source_localization(lambda2=0.111)
        """
        # Implementation uses algorithms imported from pipeline
        # (detailed implementation omitted for brevity - see prototype)

        # Determine data type and call appropriate algorithm
        if isinstance(data, mne.io.Raw):
            stc = estimate_source_function_raw(data, config=self.config, save_stc=save_stc)
        elif isinstance(data, mne.Epochs):
            stc = estimate_source_function_epochs(data, config=self.config, save_stc=save_stc)
        else:
            raise TypeError("Data must be Raw or Epochs")

        return stc
```

### Block Discovery System

**Extend existing mixin discovery to scan external block directories:**

```python
# In pipeline: src/autoclean/mixins/__init__.py

# Current: Discovers mixins in src/autoclean/mixins/
# Proposed: ALSO discover mixins in external block directories

# External block search paths (in priority order)
EXTERNAL_BLOCK_PATHS = [
    Path.home() / ".autoclean" / "blocks",  # User-installed blocks
    Path.cwd() / "blocks",                   # Project-local blocks
    Path("/path/to/task-registry/blocks"),   # Development blocks
]

# Discover external blocks (NEW)
def _discover_external_blocks():
    """Scan external directories for block files."""
    external_mixins = []

    for block_path in EXTERNAL_BLOCK_PATHS:
        if not block_path.exists():
            continue

        # Find all .py files (blocks)
        for block_file in block_path.rglob("*.py"):
            if block_file.name.startswith("_"):
                continue  # Skip private files

            # Import the block module
            spec = importlib.util.spec_from_file_location(
                f"external_block_{block_file.stem}",
                block_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Mixin classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith("Mixin") and obj.__module__ == module.__name__:
                    external_mixins.append(obj)

                    # Validate block metadata
                    if hasattr(module, "__block_metadata__"):
                        _validate_block(obj, module.__block_metadata__)

    return external_mixins

# Combine internal and external mixins
_internal_mixins = _discover_internal_mixins()  # Existing function
_external_mixins = _discover_external_blocks()   # NEW

DISCOVERED_MIXINS = tuple(_internal_mixins + _external_mixins)
```

### Block Lifecycle

```
1. User writes block file
   ├── Single .py file
   ├── Contains SourceLocalizationMixin class
   └── Imports from autoclean.calc

2. User installs block
   ├── Option A: Copy to ~/.autoclean/blocks/
   ├── Option B: pip install autocleaneeg-block-source-localization
   └── Option C: Add task-registry to search path

3. Pipeline discovers block
   ├── At import time, scans external block paths
   ├── Loads block module
   ├── Extracts Mixin classes
   └── Adds to DISCOVERED_MIXINS tuple

4. Task inherits block functionality
   ├── class Task(ABC, *DISCOVERED_MIXINS)
   ├── Task now has apply_source_localization() method
   └── User can call it in their task

5. User uses block in task
   ├── Write task file: class MyTask(Task)
   ├── Call method: self.apply_source_localization()
   └── Block functionality available transparently
```

---

## Design Principles

### 1. Zero Duplication Principle
**Never copy code from pipeline to task-registry. Always import.**

❌ **Bad:**
```python
# Duplicate algorithm in block
def estimate_source_function_raw(raw, config):
    # ... copied implementation ...
```

✅ **Good:**
```python
# Import from pipeline
from autoclean.calc.source import estimate_source_function_raw
```

### 2. Single File Principle
**One block = one Python file. Everything co-located.**

✅ Block file contains:
- Imports
- Metadata dict
- Mixin class
- Documentation

❌ Don't require:
- Separate manifest.json
- Separate schema.py
- Separate README.md
- Directory structure

### 3. Task Alignment Principle
**Blocks should work EXACTLY like task files.**

If users understand task files, they understand blocks:
```python
# Task file pattern
from autoclean.core.task import Task
class MyTask(Task): pass

# Block file pattern
from autoclean.calc.source import estimate_source_function_raw
class SourceLocalizationMixin: pass
```

### 4. Discoverability Principle
**Pipeline automatically finds and loads blocks. No registration required.**

Users just:
1. Drop file in blocks directory, OR
2. pip install block package
3. It works (no configuration needed)

### 5. Backward Compatibility Principle
**Existing pipeline code continues to work unchanged.**

Internal mixins in `src/autoclean/mixins/` still work.
External blocks are additive, not breaking.

### 6. Self-Documentation Principle
**Block file is the documentation.**

Rich docstrings + metadata dict = complete documentation.
No need to cross-reference separate files.

---

## Technical Specification

### Block File Structure

**Required elements:**
1. Module docstring with metadata
2. `__block_metadata__` dict
3. One or more `*Mixin` classes
4. Imports from pipeline (not duplicated code)

**Optional elements:**
- Helper functions (if needed)
- Config validation (Pydantic models)
- Tests (in docstring examples)

### Metadata Schema

```python
__block_metadata__ = {
    # Required fields
    "name": str,              # Block identifier (must match filename)
    "version": str,           # Semantic version (e.g., "1.0.0")
    "category": str,          # "signal_processing" | "analysis" | "visualization"

    # Optional fields
    "author": str,            # Author name/organization
    "email": str,             # Contact email
    "license": str,           # License identifier (e.g., "MIT")
    "url": str,               # Homepage/repository URL
    "requires": dict,         # {package: version_spec}
    "provides_methods": list, # Method names added to Task
    "config_keys": list,      # Config keys this block uses
    "references": list,       # Scientific references (see format below)
    "changelog": dict,        # {version: changes_description}
}
```

### Reference Format

```python
{
    "authors": "Last FM, Last FM, & Last FM",
    "year": 2020,
    "title": "Paper title",
    "journal": "Journal Name",
    "volume": "12(3)",
    "pages": "123-456",
    "doi": "10.1234/journal.5678",
    "pmid": "12345678",  # Optional
    "url": "https://...",  # Optional
}
```

### Import Conventions

**Algorithm imports (preferred):**
```python
from autoclean.calc.source import estimate_source_function_raw
from autoclean.calc.fooof_analysis import fit_fooof_models
```

**I/O imports:**
```python
from autoclean.io.export import save_stc_to_file, save_raw_to_set
from autoclean.io.import_ import import_eeg
```

**Utility imports:**
```python
from autoclean.utils.validation import validate_raw
from autoclean.utils.logging import get_logger
```

**DON'T import:**
- `from autoclean.mixins import ...` (creates circular dependency)
- `from autoclean.core.task import Task` (only for task files, not blocks)

### Mixin Class Convention

```python
class BlockNameMixin:  # Must end with "Mixin"
    """Brief description.

    Longer description explaining what the mixin provides.
    """

    def method_name(self, param1: type1, param2: type2, ...) -> return_type:
        """Method docstring following NumPy style.

        Parameters
        ----------
        param1 : type1
            Description

        Returns
        -------
        return_type
            Description

        Examples
        --------
        >>> # Usage example
        """
        # Implementation
```

### Config Integration

Blocks read config from `self.config`:
```python
def apply_source_localization(self, ...):
    # Get config for this block
    config_value = self.config.get("apply_source_localization", {})

    if isinstance(config_value, dict) and "value" in config_value:
        params = config_value["value"]
        method = params.get("method", "MNE")
        lambda2 = params.get("lambda2", 0.111)
```

Task config structure:
```python
config = {
    "apply_source_localization": {
        "enabled": True,
        "value": {
            "method": "MNE",
            "lambda2": 0.111,
            "save_stc": False,
        }
    }
}
```

---

## Migration Path

### Current Block Structure
```
blocks/analysis/source_localization/
├── algorithm.py       (300 lines)
├── mixin.py          (250 lines)
├── manifest.json     (100 lines)
├── schema.py         (50 lines)
├── README.md         (200 lines)
└── __init__.py       (5 lines)
Total: 6 files, ~900 lines
```

### Proposed Block Structure
```
blocks/source_localization.py  (400 lines total)
  ├── Module docstring (extracted from README.md)
  ├── __block_metadata__ dict (from manifest.json)
  ├── Imports (from algorithm.py, but referencing pipeline)
  └── SourceLocalizationMixin (from mixin.py, cleaned up)
```

**Reduction: 6 files → 1 file, ~900 lines → ~400 lines**

### Migration Steps for One Block

**Step 1: Create single-file version**
```bash
cd task-registry/blocks
python migrate_block.py source_localization
# Creates: source_localization_plugin.py
```

**Step 2: Convert components**
1. Copy README.md → module docstring
2. Convert manifest.json → `__block_metadata__` dict
3. Copy mixin.py → Mixin class
4. Change imports: `from .algorithm import X` → `from autoclean.calc.source import X`
5. Remove algorithm.py (not needed - imports from pipeline)
6. Inline schema.py validation (or omit if not critical)

**Step 3: Test plugin version**
```bash
# Copy to test location
cp source_localization_plugin.py ~/.autoclean/blocks/

# Run test task
autocleaneeg-pipeline process --task TestSourceLocalization --file test.set

# Verify it works
```

**Step 4: Deprecate old structure**
```bash
# Move old structure to deprecated/
mkdir -p deprecated/source_localization
mv analysis/source_localization/* deprecated/source_localization/

# Add deprecation notice
echo "DEPRECATED: Use source_localization.py instead" > deprecated/source_localization/README.md
```

**Step 5: Update documentation**
- Update task-registry README to explain new structure
- Add migration guide for existing users
- Update contribution guidelines

### Migration Script

```python
#!/usr/bin/env python3
"""Migrate a multi-file block to single-file plugin format.

Usage:
    python migrate_block.py source_localization
"""

import sys
import json
from pathlib import Path

def migrate_block(block_name: str):
    """Convert a multi-file block to single-file plugin."""

    # Paths
    old_dir = Path(f"analysis/{block_name}")
    new_file = Path(f"{block_name}_plugin.py")

    if not old_dir.exists():
        print(f"Error: Block directory not found: {old_dir}")
        return

    # Read components
    manifest = json.loads((old_dir / "manifest.json").read_text())
    readme = (old_dir / "README.md").read_text()
    mixin = (old_dir / "mixin.py").read_text()
    algorithm = (old_dir / "algorithm.py").read_text()

    # Extract imports from algorithm
    algorithm_imports = extract_imports(algorithm)

    # Build new file
    output = []
    output.append('"""' + readme + '"""')
    output.append("")
    output.append("# Imports")
    output.append(convert_imports(algorithm_imports))
    output.append("")
    output.append("# Metadata")
    output.append(f"__block_metadata__ = {json.dumps(manifest, indent=4)}")
    output.append("")
    output.append("# Mixin class")
    output.append(update_mixin_imports(mixin))

    # Write output
    new_file.write_text("\n".join(output))
    print(f"✓ Created: {new_file}")
    print(f"  Old: 6 files in {old_dir}")
    print(f"  New: 1 file: {new_file}")

def extract_imports(code: str) -> list:
    """Extract import statements from code."""
    imports = []
    for line in code.split("\n"):
        if line.startswith("import ") or line.startswith("from "):
            imports.append(line)
    return imports

def convert_imports(imports: list) -> str:
    """Convert algorithm imports to pipeline imports."""
    converted = []
    for imp in imports:
        # Change local imports to pipeline imports
        if "from .algorithm" in imp or "from autoclean.calc" in imp:
            # Keep autoclean imports as-is
            converted.append(imp)
        elif "from mne" in imp or "import mne" in imp:
            converted.append(imp)
        # Skip internal imports
    return "\n".join(converted)

def update_mixin_imports(mixin_code: str) -> str:
    """Update mixin to import from pipeline instead of local algorithm."""
    # Replace: from .algorithm import X
    # With: from autoclean.calc.source import X
    updated = mixin_code.replace(
        "from .algorithm import",
        "from autoclean.calc.source import"
    )
    return updated

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate_block.py <block_name>")
        sys.exit(1)

    migrate_block(sys.argv[1])
```

### Migration Timeline

**Phase 1: Prototype (Week 1)**
- Create single-file version of source_localization block
- Test with pipeline discovery system
- Validate approach

**Phase 2: Tooling (Week 2)**
- Build migration script
- Create testing framework
- Document new structure

**Phase 3: Core Blocks (Weeks 3-4)**
- Migrate 5 analysis blocks (source_localization, source_psd, source_connectivity, fooof_aperiodic, fooof_periodic)
- Migrate 2 signal processing blocks (wavelet_threshold, autoreject)
- Update documentation

**Phase 4: Deprecation (Week 5)**
- Move old structure to deprecated/
- Update all references
- Add deprecation warnings

**Phase 5: Distribution (Week 6)**
- Create PyPI packages for blocks
- Set up CI/CD for block releases
- Write user guide for block installation

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goals:**
- Prove the concept works
- Build minimal tooling
- Document the pattern

**Tasks:**
1. ✅ Create architecture document (this file)
2. Create prototype single-file block
3. Implement block discovery in pipeline
4. Write basic migration script
5. Test with one block end-to-end

**Deliverables:**
- `PLUGIN_BLOCK_ARCHITECTURE.md` (this file)
- `source_localization_plugin.py` (prototype)
- `blocks/migrate_block.py` (migration script)
- `test_plugin_discovery.py` (test suite)

**Success Criteria:**
- Prototype block discovered by pipeline
- Task can call block method
- Zero duplication with pipeline
- Single file, self-contained

### Phase 2: Core Blocks (Weeks 3-6)

**Goals:**
- Migrate all existing blocks
- Establish conventions
- Create comprehensive tests

**Tasks:**
1. Migrate analysis blocks (5 blocks)
   - source_localization
   - source_psd
   - source_connectivity
   - fooof_aperiodic
   - fooof_periodic

2. Migrate signal processing blocks (2 blocks)
   - wavelet_threshold
   - autoreject

3. Update documentation
   - Block catalog in README
   - Migration guide for users
   - Contribution guidelines

4. Deprecate old structure
   - Move to deprecated/
   - Add warning messages
   - Update references

**Deliverables:**
- 7 single-file plugin blocks
- Updated README.md
- MIGRATION_GUIDE.md
- CONTRIBUTING.md (updated)

**Success Criteria:**
- All blocks work as plugins
- All tests pass
- Documentation complete
- No errors or warnings

### Phase 3: Distribution (Weeks 7-10)

**Goals:**
- Enable pip installation of blocks
- Set up automated releases
- Provide multiple installation methods

**Tasks:**
1. Create PyPI package structure
   ```
   autocleaneeg-block-source-localization/
   ├── pyproject.toml
   ├── src/
   │   └── autocleaneeg_blocks/
   │       └── source_localization.py
   └── tests/
       └── test_source_localization.py
   ```

2. Set up CI/CD
   - GitHub Actions for testing
   - Automated PyPI releases
   - Version bumping

3. Write installation guide
   - pip install method
   - Manual file copy method
   - Git submodule method

4. Create block registry
   - Central catalog of available blocks
   - Version compatibility matrix
   - Installation instructions

**Deliverables:**
- 7 PyPI packages (one per block)
- CI/CD workflows
- Installation guide
- Block registry website/page

**Success Criteria:**
- Users can `pip install autocleaneeg-block-*`
- Automated testing on every PR
- Clear installation documentation
- Version compatibility enforced

### Phase 4: Ecosystem (Weeks 11-16)

**Goals:**
- Enable community contributions
- Provide developer tools
- Build block marketplace

**Tasks:**
1. Developer tools
   - Block template generator
   - Validation tools
   - Testing helpers

2. CLI commands
   ```bash
   autocleaneeg-pipeline blocks list
   autocleaneeg-pipeline blocks search connectivity
   autocleaneeg-pipeline blocks install source_localization
   autocleaneeg-pipeline blocks validate my_block.py
   ```

3. Community infrastructure
   - Block submission process
   - Review guidelines
   - Quality standards

4. Documentation
   - Block development tutorial
   - API reference
   - Best practices guide

**Deliverables:**
- `autocleaneeg-pipeline blocks` CLI
- Developer documentation
- Community guidelines
- Block marketplace

**Success Criteria:**
- External developers can create blocks
- Clear submission process
- Automated quality checks
- Growing ecosystem

---

## Code Examples

### Example 1: Simple Block (Source Localization)

See prototype file: `source_localization_plugin.py`

### Example 2: Block with Dependencies

```python
# blocks/advanced_ica.py
"""Advanced ICA with multiple algorithms.

Requires:
- mne-icalabel
- picard
- python-picard
"""

from typing import Optional, Union
import mne
from mne.preprocessing import ICA

# Check optional dependencies
try:
    from mne_icalabel import label_components
    ICLABEL_AVAILABLE = True
except ImportError:
    ICLABEL_AVAILABLE = False

try:
    import picard
    PICARD_AVAILABLE = True
except ImportError:
    PICARD_AVAILABLE = False

__block_metadata__ = {
    "name": "advanced_ica",
    "version": "1.0.0",
    "category": "signal_processing",
    "requires": {
        "autoclean": ">=2.3.0",
        "mne": ">=1.6.0",
        "mne-icalabel": ">=0.5.0",
        "picard": ">=0.7",
    },
    "provides_methods": ["apply_advanced_ica"],
}


class AdvancedICAMixin:
    """Provides advanced ICA with multiple algorithms."""

    def apply_advanced_ica(
        self,
        method: str = "picard",
        n_components: int = 25,
        reject_components: bool = True,
        **kwargs
    ):
        """Apply ICA with automatic component rejection."""

        # Check dependencies
        if method == "picard" and not PICARD_AVAILABLE:
            raise ImportError(
                "Picard algorithm requires: pip install python-picard"
            )

        if reject_components and not ICLABEL_AVAILABLE:
            raise ImportError(
                "Auto-rejection requires: pip install mne-icalabel"
            )

        # Implementation...
```

### Example 3: Block with Custom Config

```python
# blocks/custom_filter.py
"""Custom filtering with multiple methods."""

from typing import Optional
import mne
from scipy import signal

__block_metadata__ = {
    "name": "custom_filter",
    "version": "1.0.0",
    "category": "signal_processing",
    "config_keys": ["custom_filter"],
}


class CustomFilterMixin:
    """Provides custom filtering methods."""

    def apply_custom_filter(
        self,
        data: Optional[mne.io.Raw] = None,
        method: str = "butterworth",
        order: int = 4,
        **kwargs
    ):
        """Apply custom filter."""

        # Get config
        config_value = self.config.get("custom_filter", {})
        if isinstance(config_value, dict) and "value" in config_value:
            params = config_value["value"]
            method = params.get("method", method)
            order = params.get("order", order)

        # Use data or fall back to self.raw
        if data is None:
            if not hasattr(self, "raw"):
                raise ValueError("No data available")
            data = self.raw

        # Apply filter based on method
        if method == "butterworth":
            # Implementation...
            pass
        elif method == "chebyshev":
            # Implementation...
            pass
        else:
            raise ValueError(f"Unknown method: {method}")
```

### Example 4: Block Usage in Task

```python
# User's task file using plugin blocks
from autoclean.core.task import Task

config = {
    "apply_source_localization": {
        "enabled": True,
        "value": {"method": "MNE", "lambda2": 0.111}
    },
    "apply_source_psd": {
        "enabled": True,
        "value": {"freq_bands": {"alpha": (8, 13)}}
    },
}


class MyAnalysisTask(Task):
    """Custom analysis using plugin blocks."""

    def run(self):
        # Basic preprocessing
        self.import_raw()
        self.resample_data()
        self.filter_data()

        # Use plugin blocks (methods available because blocks are discovered)
        self.apply_source_localization()  # From source_localization plugin
        self.apply_source_psd()           # From source_psd plugin
        self.apply_source_connectivity()  # From source_connectivity plugin
```

---

## Testing Strategy

### Unit Tests for Blocks

```python
# tests/test_source_localization_plugin.py
import pytest
import mne
from pathlib import Path
import sys

# Add plugin to path
sys.path.insert(0, str(Path(__file__).parent.parent / "blocks"))

from source_localization_plugin import SourceLocalizationMixin, __block_metadata__


class TestSourceLocalizationPlugin:
    """Test source localization plugin."""

    def test_metadata(self):
        """Test block metadata is valid."""
        assert "name" in __block_metadata__
        assert "version" in __block_metadata__
        assert "category" in __block_metadata__
        assert __block_metadata__["name"] == "source_localization"

    def test_mixin_exists(self):
        """Test mixin class exists and has expected methods."""
        assert hasattr(SourceLocalizationMixin, "apply_source_localization")

    def test_method_signature(self):
        """Test method has correct signature."""
        import inspect
        sig = inspect.signature(SourceLocalizationMixin.apply_source_localization)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "data" in params
        assert "method" in params

    @pytest.mark.integration
    def test_with_real_data(self, sample_raw):
        """Test plugin with real EEG data."""
        # Create minimal task-like object
        class MockTask(SourceLocalizationMixin):
            def __init__(self, raw):
                self.raw = raw
                self.config = {}

        task = MockTask(sample_raw)
        stc = task.apply_source_localization()

        assert isinstance(stc, mne.SourceEstimate)
        assert stc.data.shape[0] > 1000  # Has vertices
```

### Integration Tests

```python
# tests/test_plugin_discovery.py
import pytest
from pathlib import Path
import importlib

def test_plugin_discovery():
    """Test that plugins are discovered by pipeline."""
    # Import mixins module (triggers discovery)
    from autoclean.mixins import DISCOVERED_MIXINS

    # Check for source localization mixin
    mixin_names = [m.__name__ for m in DISCOVERED_MIXINS]
    assert "SourceLocalizationMixin" in mixin_names


def test_task_has_plugin_methods():
    """Test that Task class has methods from plugins."""
    from autoclean.core.task import Task

    assert hasattr(Task, "apply_source_localization")


@pytest.mark.integration
def test_plugin_in_task(sample_config):
    """Test using plugin in a task."""
    from autoclean.core.task import Task

    class TestTask(Task):
        def run(self):
            self.import_raw()
            self.apply_source_localization()

    # Should not raise
    task = TestTask(sample_config)
```

### Continuous Integration

```yaml
# .github/workflows/test_plugins.yml
name: Test Plugin Blocks

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
        pip install autocleaneeg-pipeline>=2.3.0

    - name: Test plugin discovery
      run: pytest tests/test_plugin_discovery.py -v

    - name: Test individual plugins
      run: pytest tests/test_*_plugin.py -v

    - name: Test integration
      run: pytest tests/integration/ -v
```

---

## Distribution Model

### Method 1: Manual File Copy (Simplest)

```bash
# Download block
curl -O https://raw.githubusercontent.com/.../source_localization.py

# Install to user directory
mkdir -p ~/.autoclean/blocks
cp source_localization.py ~/.autoclean/blocks/

# Use in task
autocleaneeg-pipeline process --task MyTask --file data.set
```

### Method 2: Git Clone (Development)

```bash
# Clone task-registry
git clone https://github.com/.../autocleaneeg-task-registry.git

# Add to search path
export AUTOCLEAN_BLOCK_PATH=/path/to/task-registry/blocks

# Or add to config
echo "block_paths: ['/path/to/task-registry/blocks']" >> ~/.autoclean/config.yaml

# Use in task
autocleaneeg-pipeline process --task MyTask --file data.set
```

### Method 3: PyPI Install (Recommended)

```bash
# Install block as package
pip install autocleaneeg-block-source-localization

# Block is automatically discovered
# No configuration needed!

# Use in task
autocleaneeg-pipeline process --task MyTask --file data.set
```

**Package structure:**
```
autocleaneeg-block-source-localization/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── autocleaneeg_blocks/
│       ├── __init__.py
│       └── source_localization.py
└── tests/
    └── test_source_localization.py
```

**pyproject.toml:**
```toml
[project]
name = "autocleaneeg-block-source-localization"
version = "1.0.0"
description = "Source localization block for AutoClean EEG"
authors = [{name = "Cincinnati Children's Hospital - Brain Lab"}]
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = [
    "autocleaneeg-pipeline>=2.3.0",
    "mne>=1.6.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov"]

[project.entry-points."autocleaneeg.blocks"]
source_localization = "autocleaneeg_blocks.source_localization:SourceLocalizationMixin"
```

### Method 4: Block Manager CLI

```bash
# List available blocks
autocleaneeg-pipeline blocks list

# Search for blocks
autocleaneeg-pipeline blocks search connectivity

# Install block
autocleaneeg-pipeline blocks install source_localization

# Update block
autocleaneeg-pipeline blocks update source_localization

# Uninstall block
autocleaneeg-pipeline blocks uninstall source_localization

# Show block info
autocleaneeg-pipeline blocks info source_localization
```

---

## Backwards Compatibility

### For Existing Pipeline Users

**No breaking changes:**
- Internal mixins in `src/autoclean/mixins/` continue to work
- Existing tasks continue to work
- No API changes required

**Additive changes:**
- New blocks add methods to Task
- Users can opt-in to external blocks
- Default behavior unchanged

### For Existing Task-Registry Users

**Current blocks deprecated but functional:**
- Old multi-file blocks moved to `deprecated/`
- Will be removed in v3.0.0
- Migration guide provided

**New blocks work alongside old:**
- Can gradually migrate
- Test new format before full migration
- No rush to convert

### Deprecation Timeline

**v2.4.0 (Q4 2025):**
- Introduce plugin block system
- Mark old structure as deprecated
- Provide migration guide

**v2.5.0 - v2.9.0 (2026):**
- Support both old and new formats
- Encourage migration
- Provide tooling

**v3.0.0 (2027):**
- Remove support for old multi-file blocks
- Only plugin blocks supported
- Clean codebase

---

## Future Extensions

### Block Marketplace

**Vision:** Central repository of community-contributed blocks

Features:
- Web-based catalog
- Search and filtering
- Ratings and reviews
- Download statistics
- Version compatibility

**URL:** https://blocks.autocleaneeg.org

**Example:**
```
┌──────────────────────────────────────────┐
│ AutoClean EEG Block Marketplace          │
├──────────────────────────────────────────┤
│ Search: [connectivity_________] [Search] │
├──────────────────────────────────────────┤
│                                          │
│ ⭐⭐⭐⭐⭐ source_localization (v1.2.0)    │
│ Downloads: 5,234 | Author: Brain Lab    │
│ MNE source localization using fsaverage  │
│ [Install] [View Docs] [GitHub]          │
│                                          │
│ ⭐⭐⭐⭐☆ advanced_connectivity (v2.0.1)  │
│ Downloads: 3,891 | Author: J. Smith     │
│ Network analysis with BCT integration    │
│ [Install] [View Docs] [GitHub]          │
│                                          │
└──────────────────────────────────────────┘
```

### Block Collections

**Curated sets of related blocks:**

```bash
# Install a collection
autocleaneeg-pipeline blocks install-collection source-analysis

# Includes:
# - source_localization
# - source_psd
# - source_connectivity
# - fooof_aperiodic
# - fooof_periodic
```

**Collection manifest:**
```yaml
name: source-analysis
version: 1.0.0
description: Complete source-level analysis toolkit
blocks:
  - source_localization==1.0.0
  - source_psd==1.0.0
  - source_connectivity==1.0.0
  - fooof_aperiodic==1.0.0
  - fooof_periodic==1.0.0
```

### Block Templates

**Quick-start templates for common block types:**

```bash
# Create new block from template
autocleaneeg-pipeline blocks new my_block --template analysis

# Templates:
# - analysis: Template for analysis blocks
# - signal_processing: Template for signal processing
# - visualization: Template for plotting blocks
# - io: Template for import/export blocks
```

**Generated structure:**
```python
# my_block.py (generated from template)
"""[Description]

TODO: Fill in metadata and documentation
"""

__block_metadata__ = {
    "name": "my_block",
    "version": "0.1.0",
    "category": "analysis",
    # TODO: Add more metadata
}


class MyBlockMixin:
    """TODO: Add docstring"""

    def apply_my_block(self):
        """TODO: Implement method"""
        raise NotImplementedError("TODO: Implement apply_my_block()")
```

### Version Locking

**Ensure reproducible analyses:**

```python
# Lock file: blocks.lock
{
    "blocks": {
        "source_localization": {
            "version": "1.0.0",
            "source": "pypi",
            "hash": "sha256:abc123..."
        },
        "fooof_aperiodic": {
            "version": "1.2.1",
            "source": "git",
            "url": "https://github.com/.../fooof.git",
            "commit": "abc123"
        }
    }
}
```

```bash
# Create lock file
autocleaneeg-pipeline blocks lock

# Install from lock file
autocleaneeg-pipeline blocks install --locked

# Update lock file
autocleaneeg-pipeline blocks update --lock
```

### Block Dependencies

**Blocks can depend on other blocks:**

```python
__block_metadata__ = {
    "name": "source_connectivity",
    "version": "1.0.0",
    "requires_blocks": {
        "source_localization": ">=1.0.0",
    }
}


class SourceConnectivityMixin:
    def apply_source_connectivity(self):
        # Requires source localization first
        if not hasattr(self, "stc"):
            raise ValueError(
                "Source connectivity requires source localization. "
                "Call apply_source_localization() first."
            )
        # ...
```

### Performance Profiling

**Built-in profiling for blocks:**

```bash
# Profile a block
autocleaneeg-pipeline blocks profile source_localization --file test.set

# Output:
# Block: source_localization v1.0.0
# ├── apply_source_localization(): 45.2s
# │   ├── make_forward_solution: 30.1s (66%)
# │   ├── make_inverse_operator: 10.5s (23%)
# │   └── apply_inverse: 4.6s (11%)
# Total: 45.2s
```

---

## References

### Existing Systems with Similar Patterns

1. **Jupyter Notebooks** - Single-file literate programming
2. **Flask Blueprints** - Modular application components
3. **Django Apps** - Self-contained functionality
4. **pytest Plugins** - Entry point based discovery
5. **VS Code Extensions** - Single-file extension model

### Scientific Software Precedents

1. **EEGLAB Plugins** - .m files in plugins directory
2. **FieldTrip Toolboxes** - Modular analysis components
3. **SPM Extensions** - Single-directory toolboxes
4. **MNE-Python** - Modular processing with clear APIs

### Design Pattern References

1. **Mixin Pattern** - Multiple inheritance for behavior
2. **Plugin Architecture** - Hot-swappable components
3. **Convention over Configuration** - Sensible defaults
4. **Discovery Pattern** - Automatic registration

---

## Appendices

### Appendix A: File Size Comparison

**Current multi-file block:**
```
source_localization/
├── algorithm.py      14,807 bytes
├── mixin.py          15,986 bytes
├── manifest.json      4,304 bytes
├── schema.py          2,500 bytes (estimated)
├── README.md         10,555 bytes
└── __init__.py          100 bytes (estimated)
Total: 48,252 bytes (47 KB)
```

**Proposed single-file block:**
```
source_localization.py
Total: ~20,000 bytes (20 KB)

Reduction: 58% smaller
```

### Appendix B: Import Dependency Graph

```
Current (Duplicated):
┌─────────────────────────────────────────┐
│ Pipeline                                │
│ ├── calc/source.py                     │
│ │   └── estimate_source_function_raw() │
│ └── mixins/.../source_localization.py  │
│     └── imports calc/source.py         │
└─────────────────────────────────────────┘
           ↓ (manual copy)
┌─────────────────────────────────────────┐
│ Task-Registry                           │
│ └── blocks/.../                         │
│     ├── algorithm.py (DUPLICATE!)       │
│     └── mixin.py (imports ./algorithm)  │
└─────────────────────────────────────────┘

Proposed (Import-Based):
┌─────────────────────────────────────────┐
│ Pipeline (Source of Truth)              │
│ └── calc/source.py                      │
│     └── estimate_source_function_raw()  │
└─────────────────────────────────────────┘
           ↑ (imports)
┌─────────────────────────────────────────┐
│ Task-Registry (No Duplication!)         │
│ └── blocks/source_localization.py       │
│     └── imports calc/source.py          │
└─────────────────────────────────────────┘
```

### Appendix C: Metadata Format Comparison

**Current (manifest.json):**
```json
{
  "name": "source_localization",
  "version": "1.0.0",
  "category": "analysis",
  "description": "...",
  "references": [...]
}
```

**Proposed (Python dict):**
```python
__block_metadata__ = {
    "name": "source_localization",
    "version": "1.0.0",
    "category": "analysis",
    "description": "...",
    "references": [...]
}
```

**Advantages of Python dict:**
- No JSON parsing errors
- Can include computed values
- IDE validation
- Type hints possible
- Comments allowed

### Appendix D: Discovery Performance

**Benchmark (1000 blocks):**
- Current: N/A (not discoverable)
- Proposed: ~500ms (acceptable)

**Optimization strategies:**
- Cache discovered blocks
- Lazy loading
- Parallel scanning
- Index file

---

## Conclusion

This architecture plan proposes a fundamental shift in how AutoClean EEG blocks are structured and distributed. By aligning blocks with the existing task file pattern, we eliminate code duplication, simplify distribution, and create a true plugin ecosystem.

**Key Outcomes:**
1. **Single file per block** - easy to understand and share
2. **Zero duplication** - blocks import from pipeline
3. **Familiar pattern** - works like task files
4. **Auto-discovery** - no manual registration
5. **Future-proof** - enables PyPI distribution and ecosystem growth

**Next Steps:**
1. Review and approve this plan
2. Create prototype single-file block
3. Test discovery mechanism
4. Migrate existing blocks
5. Document and release

---

**Questions? Feedback? Suggestions?**

Open an issue or PR in the task-registry repository:
https://github.com/cincibrainlab/autocleaneeg-task-registry/issues

---

**Document History:**
- v1.0 (2025-09-30): Initial architecture proposal