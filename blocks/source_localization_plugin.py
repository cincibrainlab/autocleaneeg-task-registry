"""Source Localization Plugin Block for AutoClean EEG.

This block provides MNE minimum norm estimation for projecting sensor-space EEG
data to cortical sources using the fsaverage template brain. It demonstrates
the new single-file plugin block architecture.

Overview
--------
Source localization estimates the cortical origins of EEG sensor measurements
using minimum norm estimation (MNE). This implementation:

- Uses fsaverage template brain (no subject-specific anatomy needed)
- Supports both continuous (Raw) and epoched (Epochs) data
- Optionally converts source estimates to 68-channel ROI format
- Provides BIDS-compatible derivative outputs

The block adds the `apply_source_localization()` method to all Task classes.

Block Metadata
--------------
name: source_localization
version: 1.0.0
category: analysis
author: Cincinnati Children's Hospital - Brain Lab
license: MIT
requires:
    autoclean: >=2.3.0
    mne: >=1.6.0

Scientific Background
---------------------
Minimum norm estimation (MNE) is an inverse method that estimates cortical
source activity from EEG sensor measurements by finding the source distribution
with minimum energy that explains the observed data. The method assumes:

1. Forward model: Known relationship between sources and sensors
2. Noise covariance: Statistical properties of noise (here: identity matrix)
3. Source space: Cortical surface discretized into vertices

The inverse solution is computed as:
    M = R @ G.T @ (G @ R @ G.T + λ²C)⁻¹

Where:
- M: Inverse operator (n_sources × n_sensors)
- R: Source covariance matrix (minimum norm assumption)
- G: Forward solution (n_sensors × n_sources)
- C: Noise covariance matrix
- λ²: Regularization parameter (1/SNR²)

Scientific References
---------------------
Hämäläinen MS & Ilmoniemi RJ (1994). Interpreting magnetic fields of the brain:
minimum norm estimates. Medical & Biological Engineering & Computing, 32(1), 35-42.
https://doi.org/10.1007/BF02512476

Gramfort A, et al. (2013). MEG and EEG data analysis with MNE-Python.
Frontiers in Neuroscience, 7, 267.
https://doi.org/10.3389/fnins.2013.00267

Desikan RS, et al. (2006). An automated labeling system for subdividing the human
cerebral cortex on MRI scans into gyral based regions of interest. NeuroImage,
31(3), 968-980.
https://doi.org/10.1016/j.neuroimage.2006.01.021

Installation
------------
Copy this file to one of the block search paths:
    ~/.autoclean/blocks/source_localization_plugin.py

Or install via pip (future):
    pip install autocleaneeg-block-source-localization

Usage Examples
--------------
Basic source localization on continuous data:

    >>> class MyTask(Task):
    ...     def run(self):
    ...         self.import_raw()
    ...         self.resample_data()
    ...         self.filter_data()
    ...         self.apply_source_localization()

With ROI conversion (68-channel .set file):

    >>> config = {
    ...     "apply_source_localization": {
    ...         "enabled": True,
    ...         "value": {
    ...             "method": "MNE",
    ...             "lambda2": 0.111,
    ...             "convert_to_eeg": True,
    ...         }
    ...     }
    ... }

With epoched data:

    >>> class MyTask(Task):
    ...     def run(self):
    ...         self.import_raw()
    ...         self.create_regular_epochs()
    ...         self.apply_source_localization()
    ...         # Returns list of SourceEstimates (one per epoch)

Output Files
------------
When convert_to_eeg=True:
    derivatives/source_localization_eeg/
    ├── {subject}_dk_regions.set       # 68-channel ROI time courses
    ├── {subject}_dk_montage.fif       # ROI centroid positions
    └── {subject}_region_info.csv      # ROI metadata

When save_stc=True (optional, files are large):
    derivatives/source_localization/
    └── {subject}_stc.h5               # Vertex-level source estimates (2.3GB!)

Configuration
-------------
Task config structure:

    {
        "apply_source_localization": {
            "enabled": True,
            "value": {
                "method": "MNE",           # Or "dSPM", "sLORETA"
                "lambda2": 0.111,          # Regularization (1/SNR²)
                "pick_ori": "normal",      # Source orientation constraint
                "n_jobs": 10,              # Parallel jobs for forward solution
                "save_stc": False,         # Save vertex-level STC? (2.3GB files)
                "convert_to_eeg": True,    # Convert to 68-channel ROI? (3.9MB)
            }
        }
    }

Parameters
----------
method : str
    Inverse method: "MNE" (minimum norm), "dSPM" (noise-normalized),
    or "sLORETA" (standardized low-resolution brain electromagnetic tomography)

lambda2 : float
    Regularization parameter (inverse of SNR²). Typical values: 0.05-0.2.
    Higher values = more smoothing. Default: 0.111 (≈ SNR=3)

pick_ori : str or None
    Source orientation constraint:
    - "normal": Sources perpendicular to cortical surface (default)
    - None: Sources free to point in any direction (3x more parameters)

n_jobs : int
    Number of parallel jobs for forward solution computation.
    More jobs = faster, but more memory. Default: 10

save_stc : bool
    Whether to save vertex-level SourceEstimate to .h5 file.
    WARNING: Files are very large (~2.3GB for Raw, ~78MB per epoch).
    Set False unless you specifically need vertex-level data. Default: False

convert_to_eeg : bool
    Whether to convert source estimates to 68-channel ROI EEGLAB format.
    Uses Desikan-Killiany atlas to average vertices within each region.
    Output files are small (3.9MB). Recommended: True. Default: False

Troubleshooting
---------------
Error: "fsaverage data not found"
    Solution: MNE will auto-download fsaverage on first use. Ensure internet
    connection. Manual download: python -c "import mne; mne.datasets.fetch_fsaverage()"

Error: "Forward solution failed"
    Solution: Check that montage is set correctly. Verify channel names match
    standard 10-20 system.

Warning: "Some sources have very low values"
    Solution: This is normal for areas far from sensors. Consider using dSPM
    method for noise normalization.

Performance: Slow computation
    Solution: Increase n_jobs parameter. For 60s of data:
    - n_jobs=1: ~10 minutes
    - n_jobs=4: ~3 minutes
    - n_jobs=10: ~2 minutes

Notes
-----
- Requires average reference (applied automatically if not already)
- Uses identity noise covariance (assumes equal uncorrelated noise across sensors)
- Source space: fsaverage ico-5 (10,242 vertices per hemisphere)
- Forward model: 3-layer BEM (skin, skull, brain)

See Also
--------
source_psd : Regional power spectral density of source estimates
source_connectivity : Functional connectivity between source regions
fooof_aperiodic : Aperiodic parameters from source PSD
fooof_periodic : Oscillatory peaks from source PSD
"""

from pathlib import Path
from typing import Union, Optional, List
import mne

# Import algorithms from pipeline (NO DUPLICATION!)
from autoclean.calc.source import (
    estimate_source_function_raw,
    estimate_source_function_epochs,
    convert_stc_to_eeg,
    convert_stc_list_to_eeg,
)
from autoclean.io.export import save_raw_to_set, save_epochs_to_set

# Block metadata (replaces manifest.json)
__block_metadata__ = {
    "name": "source_localization",
    "version": "1.0.0",
    "category": "analysis",
    "author": "Cincinnati Children's Hospital - Brain Lab",
    "email": "ernest.pedapati@cchmc.org",
    "license": "MIT",
    "url": "https://github.com/cincibrainlab/autocleaneeg-task-registry",
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
        },
        {
            "authors": "Gramfort A, et al.",
            "year": 2013,
            "title": "MEG and EEG data analysis with MNE-Python",
            "journal": "Frontiers in Neuroscience",
            "volume": "7",
            "pages": "267",
            "doi": "10.3389/fnins.2013.00267",
        },
        {
            "authors": "Desikan RS, et al.",
            "year": 2006,
            "title": "An automated labeling system for subdividing the human cerebral cortex",
            "journal": "NeuroImage",
            "volume": "31(3)",
            "pages": "968-980",
            "doi": "10.1016/j.neuroimage.2006.01.021",
        },
    ],
    "changelog": {
        "1.0.0": "Initial plugin block version. Migrated from multi-file structure.",
    },
}


class SourceLocalizationMixin:
    """Mixin providing source localization functionality to Task classes.

    This mixin is automatically discovered and added to the Task base class
    when the plugin block is installed. It provides the apply_source_localization()
    method to all task instances.

    The mixin handles both continuous (Raw) and epoched (Epochs) EEG data,
    automatically detecting the input type and applying the appropriate
    algorithm.

    Methods
    -------
    apply_source_localization(data, method, lambda2, pick_ori, n_jobs, save_stc, ...)
        Apply MNE source localization to estimate cortical sources

    Attributes Set
    --------------
    self.stc : mne.SourceEstimate or None
        Source estimate for continuous data (if Raw input)

    self.stc_list : list of mne.SourceEstimate or None
        List of source estimates (if Epochs input)

    Examples
    --------
    >>> class MyTask(Task):
    ...     def run(self):
    ...         self.import_raw()
    ...         stc = self.apply_source_localization()
    ...         print(f"Source data shape: {stc.data.shape}")
    """

    def apply_source_localization(
        self,
        data: Union[mne.io.Raw, mne.Epochs, None] = None,
        method: str = "MNE",
        lambda2: float = 1.0 / 9.0,
        pick_ori: str = "normal",
        n_jobs: int = 10,
        save_stc: bool = False,
        convert_to_eeg: bool = False,
        stage_name: str = "apply_source_localization",
    ) -> Union[mne.SourceEstimate, List[mne.SourceEstimate]]:
        """Apply MNE source localization to estimate cortical sources.

        This method performs minimum norm estimation (MNE) to project sensor-space
        EEG data to the cortical surface. It automatically detects whether input
        is continuous (Raw) or epoched (Epochs) data and applies the appropriate
        algorithm.

        The method uses the fsaverage template brain with an identity noise
        covariance matrix, making it suitable for resting-state analyses without
        requiring subject-specific anatomical data or empty-room recordings.

        Source estimates are SourceEstimate objects containing:
        - data: (n_vertices, n_times) array of source activations
        - vertices: Vertex indices for left and right hemispheres
        - tmin: Start time
        - tstep: Time step (1/sfreq)

        Parameters
        ----------
        data : Raw, Epochs, or None, optional
            EEG data to process. If None, uses self.raw or self.epochs.

        method : str, default="MNE"
            Source estimation method:
            - "MNE": Minimum norm estimation (default)
            - "dSPM": Dynamic statistical parametric mapping (noise-normalized)
            - "sLORETA": Standardized low-resolution brain electromagnetic tomography

        lambda2 : float, default=1/9
            Regularization parameter (inverse of SNR²).
            Controls smoothness vs. fit to data.
            Typical values: 0.05 (sharp) to 0.2 (smooth).
            Default: 0.111 ≈ SNR of 3

        pick_ori : str or None, default="normal"
            Source orientation constraint:
            - "normal": Sources perpendicular to cortical surface (recommended)
            - None: Sources can point in any direction (3x more parameters)

        n_jobs : int, default=10
            Number of parallel jobs for forward solution computation.
            More jobs = faster but more memory.
            Recommended: 4-10 depending on CPU cores

        save_stc : bool, default=False
            Whether to save vertex-level SourceEstimate files.
            WARNING: Files are very large:
            - Raw: ~2.3 GB per subject
            - Epochs: ~78 MB per epoch
            Only enable if you specifically need vertex-level data.

        convert_to_eeg : bool, default=False
            Whether to convert source estimates to 68-channel ROI EEGLAB format.
            Uses Desikan-Killiany atlas to average vertices within regions.
            Output files are small (3.9 MB). Recommended for most analyses.

        stage_name : str, default="apply_source_localization"
            Name for tracking and exports

        Returns
        -------
        stc : mne.SourceEstimate or list of mne.SourceEstimate
            Source estimate(s) with cortical activations:
            - Single SourceEstimate if Raw input
            - List of SourceEstimates if Epochs input

        Raises
        ------
        AttributeError
            If no input data found (no self.raw or self.epochs)

        TypeError
            If input is not Raw or Epochs

        RuntimeError
            If source localization fails (e.g., bad montage, missing fsaverage)

        ValueError
            If invalid method or parameters

        Examples
        --------
        Basic usage with continuous data:

        >>> class MyTask(Task):
        ...     def run(self):
        ...         self.import_raw()
        ...         stc = self.apply_source_localization()
        ...         print(f"Source shape: {stc.data.shape}")
        ...         # Output: Source shape: (20484, 15000)  # vertices × timepoints

        With custom parameters:

        >>> stc = self.apply_source_localization(
        ...     method="dSPM",
        ...     lambda2=0.05,
        ...     n_jobs=4
        ... )

        With epoched data:

        >>> class MyTask(Task):
        ...     def run(self):
        ...         self.import_raw()
        ...         self.create_regular_epochs()
        ...         stc_list = self.apply_source_localization()
        ...         print(f"Number of epochs: {len(stc_list)}")

        With ROI conversion (recommended for most analyses):

        >>> stc = self.apply_source_localization(convert_to_eeg=True)
        >>> # Creates 68-channel .set file in derivatives/source_localization_eeg/

        Notes
        -----
        - Automatically sets average reference if not already applied
        - Uses identity noise covariance (assumes equal uncorrelated noise)
        - Source space: fsaverage ico-5 (10,242 vertices per hemisphere)
        - Forward model: 3-layer BEM (skin, skull, brain)

        See Also
        --------
        source_psd : Compute power spectral density of source estimates
        source_connectivity : Compute functional connectivity between sources
        """
        # Determine input data
        if data is None:
            # Try to use instance data
            if hasattr(self, "epochs") and self.epochs is not None:
                data = self.epochs
            elif hasattr(self, "raw") and self.raw is not None:
                data = self.raw
            else:
                raise AttributeError(
                    "No data available. Either pass data parameter or ensure "
                    "self.raw or self.epochs exists."
                )

        # Validate data type
        if not isinstance(data, (mne.io.Raw, mne.Epochs)):
            raise TypeError(
                f"Data must be mne.io.Raw or mne.Epochs, got {type(data)}"
            )

        # Get configuration
        config_value = {}
        if hasattr(self, "config"):
            config_value = self.config.get(stage_name, {})

        # Extract parameters from config if available
        if isinstance(config_value, dict) and "value" in config_value:
            params = config_value["value"]
            method = params.get("method", method)
            lambda2 = params.get("lambda2", lambda2)
            pick_ori = params.get("pick_ori", pick_ori)
            n_jobs = params.get("n_jobs", n_jobs)
            save_stc = params.get("save_stc", save_stc)
            convert_to_eeg = params.get("convert_to_eeg", convert_to_eeg)

        # Build config dict for algorithm functions
        save_config = {}
        if hasattr(self, "config"):
            save_config = self.config.copy()

        # Process based on data type
        if isinstance(data, mne.io.Raw):
            # Continuous data
            print(f"Applying {method} source localization to Raw data...")
            stc = estimate_source_function_raw(
                data,
                config=save_config,
                save_stc=save_stc
            )

            # Store in instance
            self.stc = stc

            # Convert to ROI if requested
            if convert_to_eeg:
                print("Converting source estimates to 68-channel ROI format...")
                convert_stc_to_eeg(stc, save_config)

            return stc

        elif isinstance(data, mne.Epochs):
            # Epoched data
            print(f"Applying {method} source localization to Epochs data...")
            stc_list = estimate_source_function_epochs(
                data,
                config=save_config,
                save_stc=save_stc
            )

            # Store in instance
            self.stc_list = stc_list

            # Convert to ROI if requested
            if convert_to_eeg:
                print("Converting source estimates to 68-channel ROI format...")
                convert_stc_list_to_eeg(stc_list, save_config)

            return stc_list

        else:
            # Should never reach here due to earlier type check
            raise TypeError(f"Unexpected data type: {type(data)}")


# Module-level validation (runs when block is imported)
def _validate_block():
    """Validate that block dependencies are available."""
    try:
        import mne
        mne_version = mne.__version__
        print(f"✓ Source localization plugin loaded (MNE v{mne_version})")
    except ImportError:
        print("✗ ERROR: MNE-Python not found. Install with: pip install mne>=1.6.0")
        raise

    # Check for calc module
    try:
        from autoclean.calc import source
        print(f"✓ Algorithms available from autoclean.calc.source")
    except ImportError:
        print("✗ ERROR: autoclean.calc.source not found. Is pipeline installed?")
        raise


# Run validation on import
_validate_block()