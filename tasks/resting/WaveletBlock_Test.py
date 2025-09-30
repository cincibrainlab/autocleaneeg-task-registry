"""Test task for wavelet_threshold processing block.

This task demonstrates the usage of the wavelet_threshold processing block
with standard resting-state EEG data. It serves as both a test and a
reference implementation showing recommended parameters.

Processing Block: wavelet_threshold (signal_processing)
Version: 1.0.0
Registry: blocks/signal_processing/wavelet_threshold
"""

from __future__ import annotations

from autoclean.core.task import Task


config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "move_flagged_files": False,

    # Basic preprocessing
    "resample_step": {"enabled": True, "value": 250},
    "filtering": {
        "enabled": True,
        "value": {
            "l_freq": 1.0,
            "h_freq": 45.0,
            "notch_freqs": [60.0],
            "notch_widths": 4.0,
        },
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "trim_step": {"enabled": True, "value": 2.0},
    "crop_step": {"enabled": False, "value": {"start": 0.0, "end": 0.0}},
    "eog_step": {"enabled": False, "value": []},

    # === WAVELET_THRESHOLD PROCESSING BLOCK ===
    # Block: signal_processing/wavelet_threshold v1.0.0
    # Purpose: Remove transient artifacts using DWT + universal thresholding
    # Reference: blocks/signal_processing/wavelet_threshold/README.md
    "wavelet_threshold": {
        "enabled": True,
        "value": {
            # Core parameters
            "wavelet": "sym4",                  # Wavelet family (sym4 = symlet 4)
            "level": 5,                         # Decomposition level
            "threshold_mode": "soft",           # "soft" or "hard"
            "threshold_scale": 1.0,             # Multiplier for universal threshold

            # Advanced parameters
            "is_erp": False,                    # ERP-preserving mode (False for resting)
            "bandpass": (1.0, 30.0),           # Used only if is_erp=True
            "filter_kwargs": None,              # Additional MNE filter args
            "psd_fmax": 45.0,                  # PSD analysis ceiling (Hz)
            "picks": "eeg",                     # Channel selection

            # Expected outputs:
            # - Denoised raw data (transients removed)
            # - PDF report: *_wavelet_threshold.pdf
            # - Metadata: reduction metrics, effective level
        },
    },

    # Post-processing
    "reference_step": {"enabled": True, "value": "average"},

    # ICA (disabled - using wavelet instead)
    "ICA": {"enabled": False},
    "component_rejection": {"enabled": False},

    # Epoching (optional for resting)
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -1.0, "tmax": 1.0},
        "event_id": None,
        "remove_baseline": {"enabled": False, "window": [None, 0.0]},
        "threshold_rejection": {
            "enabled": False,
            "volt_threshold": {"eeg": 0.000125},
        },
    },

    "ai_reporting": False,
}


class WaveletBlock_Test(Task):
    """Test task for wavelet_threshold processing block.

    Processing pipeline:
    1. Import and basic preprocessing
    2. Apply wavelet_threshold block (core step)
    3. Rereference
    4. Create epochs (optional)
    5. Generate reports

    This task tests the wavelet_threshold block with standard parameters
    suitable for resting-state EEG data.
    """

    def run(self) -> None:
        """Execute the wavelet threshold test pipeline."""

        # Step 1: Import and basic preprocessing
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.trim_edges()

        # Store original for comparison
        if self.raw is not None:
            self.original_raw = self.raw.copy()

        # Step 2: Apply wavelet_threshold processing block
        # This is the core step being tested
        self.apply_wavelet_threshold()

        # Step 3: Post-processing
        self.rereference_data()

        # Step 4: Optional epoching
        self.create_regular_epochs(export=True)

        # Step 5: Generate reports including comparison plots
        self.generate_reports()

    def generate_reports(self) -> None:
        """Generate comparison reports showing wavelet effect."""

        if self.raw is None or self.original_raw is None:
            return

        # Plot overlay comparing before/after wavelet
        self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)

        # PSD topography comparison
        self.step_psd_topo_figure(self.original_raw, self.raw)

        # Note: Wavelet block automatically generates its own PDF report
        # at: reports/run_reports/*_wavelet_threshold.pdf