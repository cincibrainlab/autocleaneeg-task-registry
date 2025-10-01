"""Test task for zapline processing block.

This task demonstrates the usage of the zapline processing block
for DSS-based line noise removal. It serves as both a test and a reference
implementation showing recommended parameters.

Processing Block: zapline (signal_processing)
Version: 1.0.0
Registry: blocks/signal_processing/zapline
"""

from __future__ import annotations

from autoclean.core.task import Task
from autoclean.utils.logging import message
from autoclean.utils.database import get_run_record


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
            "h_freq": 100.0,
            # NOTE: No notch filter - Zapline will handle line noise
            "notch_freqs": None,
            "notch_widths": None,  # Not used when notch_freqs is None
        },
    },
    "drop_outerlayer": {"enabled": True, "value": []},
    "trim_step": {"enabled": True, "value": 2.0},
    "crop_step": {"enabled": False, "value": {"start": 0.0, "end": 0.0}},
    "eog_step": {"enabled": True, "value": ["E8", "E25"]},

    # === ZAPLINE PROCESSING BLOCK ===
    # Block: signal_processing/zapline v1.0.0
    # Purpose: DSS-based line noise removal (alternative to notch filtering)
    # Reference: blocks/signal_processing/zapline/README.md
    "apply_zapline": {
        "enabled": True,
        "value": {
            # Line frequency (Hz) - depends on region
            # 60 Hz for US/Americas, 50 Hz for Europe/Asia
            "fline": 60,

            # Number of noise components to remove
            # Typically 1 is sufficient, increase if noise persists
            "nkeep": 1,

            # Iterative mode for thorough removal
            # False: Single pass (faster)
            # True: Iterative removal (more thorough)
            "use_iter": False,

            # Maximum iterations (only used if use_iter=True)
            "max_iter": 10,

            # Expected outputs:
            # - Cleaned continuous data with line noise removed
            # - Derivative: *_post_zapline_raw.fif
            # - Metadata: power reduction, SNR, iterations
        },
    },

    # Channel cleaning (after zapline)
    "clean_bad_channels": {"enabled": True, "value": {}},

    # Rereferencing
    "reference_step": {"enabled": True, "value": "average"},

    # ICA (optional)
    "ICA": {
        "enabled": True,
        "value": {
            "method": "picard",
            "n_components": 0.99,
            "max_iter": "auto",
            "random_state": 97,
        },
    },
    "component_rejection": {
        "enabled": True,
        "method": "icvision",
        "value": {
            "ic_flags_to_reject": ["muscle", "heart", "eog", "ch_noise"],
            "ic_rejection_threshold": 0.3,
            "psd_fmax": 80.0,
        },
    },

    # Epoching (optional for testing)
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -0.5, "tmax": 1.5},
        "event_id": None,
        "remove_baseline": {"enabled": True, "window": [None, 0.0]},
        "threshold_rejection": {
            "enabled": True,
            "volt_threshold": {"eeg": 0.000150},
        },
    },

    "ai_reporting": False,
}


class Zapline_Demo(Task):
    """Demo task for zapline processing block.

    Processing pipeline:
    1. Import and basic preprocessing
    2. Apply zapline block (core step) - removes line noise
    3. Clean bad channels
    4. Rereference
    5. ICA (optional)
    6. Create epochs
    7. Generate reports with spectral comparison

    This task demonstrates the zapline block as a superior alternative
    to traditional notch filtering. Zapline preserves signal content at
    frequencies near line noise harmonics, making it ideal for high-density
    EEG arrays (>32 channels).
    """

    def run(self) -> None:
        """Execute the zapline test pipeline."""

        # Step 1: Import and basic preprocessing
        self.import_raw()
        self.resample_data()
        self.filter_data()  # Note: No notch filter, Zapline handles it
        self.drop_outer_layer()
        self.assign_eog_channels()
        self.trim_edges()

        # Save pre-zapline data for before/after comparison plots
        self.pre_zapline_raw = self.raw.copy()

        # Step 2: Apply zapline processing block
        # This is the core step being tested
        # Zapline metadata will automatically log:
        # - source_commit (git hash of block version)
        # - power_before_db, power_after_db
        # - reduction_db (noise reduction)
        # - snr_before, snr_after
        self.apply_zapline()

        # Step 3: Clean bad channels (after line noise removal)
        self.clean_bad_channels()

        # Step 4: Rereference
        self.rereference_data()

        # Step 5: ICA (optional)
        self.run_ica()

        # Step 6: Create epochs (optional, for visualization)
        self.create_eventid_epochs()

        # Step 7: Generate quality reports
        self.generate_reports()

    def generate_reports(self) -> None:
        """Generate reports showing zapline effectiveness."""

        # Generate before/after PSD comparison plots
        if hasattr(self, 'pre_zapline_raw') and self.raw is not None:
            self.step_psd_topo_figure(self.pre_zapline_raw, self.raw, report_subdir="zapline")

        # The zapline block automatically logs quality metrics
        # including power reduction and SNR improvement

        # Check metadata for zapline results
        run_record = get_run_record(self.config['run_id'])
        zapline_meta = run_record.get('metadata', {}).get('step_zapline', {})

        if zapline_meta:
            message("info", "Zapline Quality Metrics:")
            message("info", f"  Block version: {zapline_meta.get('source_commit', 'unknown')[:8]}")
            message("info", f"  Line frequency: {zapline_meta.get('fline')} Hz")
            message("info", f"  Components removed: {zapline_meta.get('nkeep')}")

            if 'reduction_db' in zapline_meta:
                reduction = zapline_meta['reduction_db']
                message("info", f"  Noise reduction: {reduction:.1f} dB")

                if reduction >= 20:
                    message("info", "  Quality: Excellent (>20 dB reduction)")
                elif reduction >= 10:
                    message("info", "  Quality: Good (10-20 dB reduction)")
                else:
                    message("info", "  Quality: Modest (<10 dB reduction)")
                    message("info", "  Suggestion: Try use_iter=True or increase nkeep")

            if 'snr_after' in zapline_meta:
                snr = zapline_meta['snr_after']
                message("info", f"  Post-Zapline SNR: {snr:.2f}")
        else:
            message("warning", "No zapline metadata found")
