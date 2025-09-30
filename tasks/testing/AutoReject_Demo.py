"""Test task for autoreject processing block.

This task demonstrates the usage of the autoreject processing block
with epoched EEG data. It serves as both a test and a reference
implementation showing recommended parameters.

Processing Block: autoreject (signal_processing)
Version: 1.0.0
Registry: blocks/signal_processing/autoreject
"""

from __future__ import annotations

from autoclean.core.task import Task


config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "standard_1020"},
    "move_flagged_files": False,

    # Basic preprocessing
    "resample_step": {"enabled": True, "value": 250},
    "filtering": {
        "enabled": True,
        "value": {
            "l_freq": 0.1,
            "h_freq": 40.0,
            "notch_freqs": [60.0],
            "notch_widths": 4.0,
        },
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "trim_step": {"enabled": True, "value": 2.0},
    "crop_step": {"enabled": False, "value": {"start": 0.0, "end": 0.0}},
    "eog_step": {"enabled": False, "value": []},

    # Rereferencing before epoching
    "reference_step": {"enabled": True, "value": "average"},

    # ICA (optional - can be done before or after autoreject)
    "ICA": {
        "enabled": False,
        "value": {
            "method": "fastica",
            "n_components": None,
            "max_iter": "auto",
            "random_state": 97,
        },
    },
    "component_rejection": {
        "enabled": False,
        "method": "icvision",
        "value": {
            "ic_flags_to_reject": ["muscle", "heart", "eog", "ch_noise", "line_noise"],
            "ic_rejection_threshold": 0.3,
            "psd_fmax": 80.0,
        },
    },

    # Epoching (required for autoreject)
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -0.2, "tmax": 0.8},
        "event_id": None,  # Will use all events
        "remove_baseline": {"enabled": True, "window": [None, 0.0]},
        "threshold_rejection": {
            "enabled": False,  # Let autoreject handle rejection
            "volt_threshold": {"eeg": 0.000125},
        },
    },

    # === AUTOREJECT PROCESSING BLOCK ===
    # Block: signal_processing/autoreject v1.0.0
    # Purpose: Data-driven automated artifact rejection and channel interpolation
    # Reference: blocks/signal_processing/autoreject/README.md
    "apply_autoreject": {
        "enabled": True,
        "value": {
            # Core parameters - cross-validation grid
            "n_interpolate": [1, 4, 8],              # Channels to interpolate (search space)
            "consensus": [0.1, 0.25, 0.5, 0.75, 0.9], # Consensus thresholds (search space)

            # Performance parameters
            "n_jobs": 4,                              # Parallel jobs for CV
            "cv": 4,                                  # Number of CV folds

            # Reproducibility
            "random_state": 42,                       # Random seed for CV splits

            # Advanced parameters
            "picks": None,                            # Use all EEG channels
            "thresh_method": "bayesian_optimization", # Optimization method

            # Expected outputs:
            # - Cleaned epochs with interpolated channels
            # - Derivative: *_autoreject_epo.set
            # - Metadata: rejection stats, interpolated channels
        },
    },

    "ai_reporting": False,
}


class AutoReject_Demo(Task):
    """Demo task for autoreject processing block.

    Processing pipeline:
    1. Import and basic preprocessing
    2. Filter and rereference
    3. Create epochs
    4. Apply autoreject block (core step)
    5. Generate reports with before/after comparison

    This task demonstrates the autoreject block with standard parameters
    suitable for event-related potential (ERP) data.
    """

    def run(self) -> None:
        """Execute the autoreject test pipeline."""

        # Step 1: Import and basic preprocessing
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.trim_edges()

        # Step 2: Rereference
        self.rereference_data()

        # Step 3: Create epochs (required for autoreject)
        self.create_eventid_epochs()

        # Store original epochs for comparison
        if self.epochs is not None:
            self.original_epochs = self.epochs.copy()

        # Step 4: Apply autoreject processing block
        # This is the core step being tested
        self.apply_autoreject()

        # Step 5: Generate reports including comparison
        self.generate_reports()

    def generate_reports(self) -> None:
        """Generate comparison reports showing autoreject effect."""

        if self.epochs is None:
            return

        # Log quality metrics
        if hasattr(self, 'original_epochs') and self.original_epochs is not None:
            original_count = len(self.original_epochs)
            cleaned_count = len(self.epochs)
            rejected = original_count - cleaned_count
            rejection_percent = (rejected / original_count) * 100

            self.logger.info(f"AutoReject Results:")
            self.logger.info(f"  Original epochs: {original_count}")
            self.logger.info(f"  Cleaned epochs: {cleaned_count}")
            self.logger.info(f"  Rejected epochs: {rejected} ({rejection_percent:.1f}%)")

        # Note: AutoReject mixin automatically logs:
        # - Interpolated channels
        # - Rejection statistics
        # - Optimal parameters found by CV