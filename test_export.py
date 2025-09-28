# tasks/TestTask.py
"""Testtask task implementation for AutoCleanEEG pipeline."""

from typing import Any, Dict
from autoclean.core.task import Task

# =============================================================================
#                        AUTOCLEANEEG TASK CONFIGURATION
# =============================================================================
# This configuration controls how your EEG data will be automatically cleaned
# and processed. Each section handles a different aspect of the pipeline.
#
# 🟢 enabled: True  = Apply this processing step
# 🔴 enabled: False = Skip this processing step
#
# 💡 TIP: Generated from Task Registry - modify as needed for your specific data
# =============================================================================

config = {
    'schema_version': '2025.09',
    'dataset_name': 'Test',
    'resample_step': {
        'enabled': True,
        'value': 256
    }
}


class Testtask(Task):
    """Testtask task implementation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Testtask task.

        Parameters
        ----------
        config : Dict[str, Any]
            Configuration dictionary from the pipeline
        """
        # Initialize data containers
        self.raw = None
        self.original_raw = None
        self.epochs = None

        # Call parent initialization - IMPORTANT!
        super().__init__(config)

    def run(self) -> None:
        """Run the Testtask processing pipeline."""
        # Import raw EEG data
        self.import_raw()

        # Basic preprocessing steps
        self.resample_data()
        self.assign_eog_channels()
        self.trim_edges()
        self.crop_duration()
        self.filter_data()

        # Store original for comparison
        self.original_raw = self.raw.copy()

        # Create BIDS-compliant paths and filenames
        self.create_bids_path()

        # Channel cleaning
        self.clean_bad_channels()

        # Re-referencing
        self.rereference_data()

        # Artifact detection
        self.annotate_noisy_epochs()
        self.annotate_uncorrelated_epochs()
        self.detect_dense_oscillatory_artifacts()

        # ICA processing
        self.run_ica()

        # ICA component classification
        psd_fmax = self.settings.get('component_rejection', {}).get('value', {}).get('psd_fmax')

        self.classify_ica_components(
            method='iclabel',
            reject=True,
            psd_fmax=psd_fmax
        )

        # Drop EOG channels after ICA processing
        self.drop_eog_channels()

        # Epoching with export
        self.create_regular_epochs(export=True)

        # Detect outlier epochs
        self.detect_outlier_epochs()

        # Clean epochs using GFP
        self.gfp_clean_epochs()

        # Generate visualization reports
        self.generate_reports()

    def generate_reports(self) -> None:
        """Generate quality control visualizations and reports."""
        if self.raw is None or self.original_raw is None:
            return

        # Plot raw vs cleaned overlay using mixin method
        self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)

        # Plot PSD topography using mixin method
        self.step_psd_topo_figure(self.original_raw, self.raw)

        # Additional report generation can be added here
