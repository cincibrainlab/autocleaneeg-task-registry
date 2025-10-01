"""Zapline DSS-based line noise removal mixin for AutoClean tasks."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional

import mne

from autoclean.utils.logging import message


# Dynamically load algorithm module to support block portability
# (blocks are loaded with synthetic module names, so relative imports fail)
def _load_algorithm_module():
    """Load algorithm.py from the same directory as this mixin file."""
    mixin_path = Path(__file__).parent
    algorithm_path = mixin_path / "algorithm.py"

    spec = importlib.util.spec_from_file_location(
        "zapline_algorithm", algorithm_path
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    raise ImportError(f"Could not load algorithm module from {algorithm_path}")


# Load algorithm functions at module import time
_algorithm = _load_algorithm_module()
apply_zapline_dss = _algorithm.apply_zapline_dss
compute_line_noise_power = _algorithm.compute_line_noise_power


class ZaplineMixin:
    """Mixin providing Zapline DSS-based line noise removal."""

    def apply_zapline(
        self,
        data: Optional[mne.io.BaseRaw] = None,
        stage_name: str = "post_zapline",
    ) -> Optional[mne.io.BaseRaw]:
        """Apply Zapline DSS-based line noise removal if enabled in configuration.

        Uses Denoising Source Separation (DSS) to remove power line artifacts
        (50 or 60 Hz) and their harmonics from EEG/MEG data.

        Parameters
        ----------
        data : mne.io.BaseRaw, optional
            Raw object to clean. If not provided, uses ``self.raw``.
        stage_name : str, default="post_zapline"
            Stage identifier used when exporting the cleaned data.

        Returns
        -------
        mne.io.BaseRaw or None
            The cleaned raw instance when Zapline ran, otherwise the original object.

        Notes
        -----
        Configuration parameters (in task config):
        - fline : float
            Line noise frequency in Hz (60 for US/Americas, 50 for Europe/Asia)
        - nkeep : int
            Number of noise components to remove (typically 1)
        - use_iter : bool
            Use iterative removal for thorough noise reduction
        - max_iter : int
            Maximum iterations for iterative mode

        **When to use Zapline vs Notch Filtering**:

        Zapline is preferred over traditional notch filters because it removes line
        noise while preserving signal at nearby frequencies. Notch filters create
        spectral holes that can distort oscillatory activity (e.g., alpha band near
        line noise harmonics). Zapline uses spatial information to specifically
        target the noise component, making it ideal for high-density EEG arrays.

        For datasets with <32 channels, consider traditional notch filtering as
        Zapline's spatial decomposition may be less effective.

        Examples
        --------
        In task config:
        >>> config = {
        ...     "apply_zapline": {
        ...         "enabled": True,
        ...         "value": {"fline": 60, "nkeep": 1, "use_iter": False}
        ...     }
        ... }

        References
        ----------
        .. [1] de Cheveigné, A. (2020). ZapLine: A simple and effective method to
           remove power line artifacts. NeuroImage, 207, 116356.
        """
        inst = data if data is not None else getattr(self, "raw", None)
        if inst is None:
            message("warning", "Zapline skipped: no raw data available")
            return inst

        # Check if step is enabled in configuration
        is_enabled, settings = self._check_step_enabled("apply_zapline")
        if not is_enabled:
            message("info", "Zapline disabled in configuration")
            return inst

        # Extract parameters from config
        # Handle case where settings["value"] might be None
        params = (settings or {}).get("value") or {}
        fline = float(params.get("fline") or 60.0)
        nkeep = int(params.get("nkeep") or 1)
        use_iter = bool(params.get("use_iter") or False)
        max_iter = int(params.get("max_iter") or 10)

        # Validate parameters
        if fline not in [50.0, 60.0]:
            message(
                "warning",
                f"Unusual line frequency {fline} Hz (typically 50 or 60 Hz)",
            )

        nyquist = inst.info["sfreq"] / 2
        if fline >= nyquist:
            message(
                "error",
                f"Line frequency ({fline} Hz) must be below Nyquist ({nyquist} Hz)",
            )
            return inst

        if nkeep < 1 or nkeep > 5:
            message("warning", f"nkeep={nkeep} is unusual (typically 1-2)")

        n_channels = inst.info["nchan"]
        if n_channels < 2:
            message(
                "error",
                f"Zapline requires at least 2 channels, found {n_channels}",
            )
            return inst

        if n_channels < 32:
            message(
                "warning",
                f"Zapline works best with >32 channels (found {n_channels})",
            )

        # Measure line noise before removal
        try:
            power_before, snr_before = compute_line_noise_power(inst, fline=fline)
            message(
                "info",
                f"Pre-Zapline: {power_before:.1f} dB at {fline} Hz (SNR: {snr_before:.2f})",
            )
        except Exception as exc:
            message("warning", f"Could not compute pre-Zapline power: {exc}")
            power_before = None
            snr_before = None

        # Apply Zapline
        message(
            "header",
            f"Applying Zapline (fline={fline} Hz, nkeep={nkeep}, "
            f"iter={use_iter})...",
        )

        try:
            cleaned, info = apply_zapline_dss(
                inst,
                fline=fline,
                nkeep=nkeep,
                use_iter=use_iter,
                max_iter=max_iter,
            )
        except (ImportError, Exception) as exc:
            # Check if it's a BlockDependencyError (which is a subclass of Exception)
            # These need to propagate to pipeline level for user-friendly handling
            from autoclean.utils.block_errors import BlockDependencyError

            if isinstance(exc, BlockDependencyError):
                raise

            # For other exceptions, log and return original data
            message("error", f"Zapline failed: {exc}")
            return inst

        # Measure line noise after removal
        try:
            power_after, snr_after = compute_line_noise_power(cleaned, fline=fline)
            reduction_db = power_before - power_after if power_before else None

            if reduction_db is not None:
                message(
                    "info",
                    f"Post-Zapline: {power_after:.1f} dB at {fline} Hz "
                    f"(reduction: {reduction_db:.1f} dB, SNR: {snr_after:.2f})",
                )

                if reduction_db < 10:
                    message(
                        "warning",
                        f"Line noise reduction is modest ({reduction_db:.1f} dB). "
                        "Consider increasing nkeep or using iterative mode.",
                    )
            else:
                message(
                    "info",
                    f"Post-Zapline: {power_after:.1f} dB at {fline} Hz (SNR: {snr_after:.2f})",
                )
        except Exception as exc:
            message("warning", f"Could not compute post-Zapline power: {exc}")
            power_after = None
            snr_after = None
            reduction_db = None

        # Update instance data and save result
        self._update_instance_data(inst, cleaned)
        self._save_raw_result(cleaned, stage_name)

        # Get block info for reproducibility
        block_info = self._get_block_info("zapline")

        # Store metadata
        metadata = {
            "block_name": "zapline",
            "fline": fline,
            "nkeep": nkeep,
            "use_iter": use_iter,
            "max_iter": max_iter,
            "method": info.get("method"),
            "iterations": info.get("iterations"),
            "n_channels": n_channels,
        }

        # Add block version/commit info for reproducibility
        if block_info:
            metadata.update(block_info)

        if power_before is not None:
            metadata["power_before_db"] = float(power_before)
        if power_after is not None:
            metadata["power_after_db"] = float(power_after)
        if reduction_db is not None:
            metadata["reduction_db"] = float(reduction_db)
        if snr_before is not None:
            metadata["snr_before"] = float(snr_before)
        if snr_after is not None:
            metadata["snr_after"] = float(snr_after)

        self._update_metadata("step_zapline", metadata)

        message("success", f"Zapline complete ({info.get('iterations')} iterations)")
        return cleaned
