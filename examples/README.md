# Example Tasks

This directory contains example task files demonstrating how to use processing blocks from the task-registry.

## Directory Structure

```
examples/
├── analysis/
│   ├── source_localization/     # Source localization examples
│   ├── fooof/                   # FOOOF spectral parameterization
│   └── complete_pipeline/       # Full source analysis pipeline
└── signal_processing/
    ├── autoreject/              # AutoReject examples
    └── wavelet/                 # Wavelet denoising examples
```

## Using These Examples

### From Pipeline Repository

If you've cloned the main `autocleaneeg_pipeline` repository:

```bash
# Run an example task
autocleaneeg-pipeline process --task SourceLocalization_Raw --file /path/to/data.set

# List all available tasks (including examples)
autocleaneeg-pipeline list-tasks
```

### Standalone Usage

Copy any example task file to your workspace:

```bash
# Copy to your workspace tasks directory
cp examples/analysis/source_localization/SourceLocalization_Raw.py ~/.autoclean/tasks/

# Or create a custom location
mkdir -p ~/my_eeg_tasks
cp examples/analysis/source_localization/SourceLocalization_Raw.py ~/my_eeg_tasks/

# Run from custom location
autocleaneeg-pipeline process --task ~/my_eeg_tasks/SourceLocalization_Raw.py --file /path/to/data.set
```

## Modifying Examples

These examples are starting points. Common modifications:

1. **Adjust preprocessing**: Enable/disable ICA, change filtering parameters
2. **Change analysis parameters**: Modify block-specific settings (e.g., FOOOF frequency range)
3. **Add/remove blocks**: Comment out steps you don't need
4. **Combine blocks**: Create custom analysis pipelines

## Example Categories

### Analysis Blocks

- **Source Localization**: Project EEG to cortical sources using MNE
- **FOOOF**: Separate periodic (oscillations) from aperiodic (1/f) activity
- **Complete Pipeline**: End-to-end source analysis workflow

### Signal Processing Blocks

- **AutoReject**: ML-based artifact rejection for epochs
- **Wavelet**: Transient artifact removal using wavelet thresholding

## Documentation

For detailed information about each block:
- See individual block directories in `blocks/`
- Check block manifest.json files for parameters
- Read mixin.py docstrings for method documentation

## Contributing Examples

Have a useful task example? Contributions welcome!

1. Create a well-documented task file
2. Test it on sample data
3. Add README explaining what it demonstrates
4. Submit a pull request

## Support

- **Issues**: https://github.com/cincibrainlab/autocleaneeg-task-registry/issues
- **Discussions**: https://github.com/cincibrainlab/autocleaneeg-task-registry/discussions
- **Documentation**: https://docs.autocleaneeg.org