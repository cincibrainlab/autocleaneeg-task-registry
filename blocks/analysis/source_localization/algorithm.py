"""Source localization algorithms for EEG data.

This module contains scientifically validated functions for estimating cortical
sources from sensor-space EEG data using minimum norm estimation (MNE).

These functions are EXACT copies from the AutoCleanEEG pipeline source.py module
and must NOT be modified to maintain reproducibility of scientific results.

References
----------
Hämäläinen MS & Il

moniemi RJ (1994). Interpreting magnetic fields of the brain:
minimum norm estimates. Medical & Biological Engineering & Computing, 32(1), 35-42.
"""

import matplotlib
import matplotlib.pyplot as plt
import mne
from mne.datasets import fetch_fsaverage

from autoclean.io.export import save_stc_to_file


def estimate_source_function_raw(raw: mne.io.Raw, config: dict = None):
    """
    Perform source localization on continuous resting-state EEG data using an identity matrix
    for noise covariance, keeping it as raw data.
    """
    # --------------------------------------------------------------------------
    # Preprocessing for Source Localization
    # --------------------------------------------------------------------------
    matplotlib.use("Qt5Agg")

    raw.set_eeg_reference("average", projection=True)
    print("Set EEG reference to average")

    noise_cov = mne.make_ad_hoc_cov(raw.info)
    print("Using an identity matrix for noise covariance")

    # --------------------------------------------------------------------------
    # Source Localization Setup
    # --------------------------------------------------------------------------
    fs_dir = fetch_fsaverage()
    trans = "fsaverage"
    src = mne.read_source_spaces(f"{fs_dir}/bem/fsaverage-ico-5-src.fif")
    bem = mne.read_bem_solution(f"{fs_dir}/bem/fsaverage-5120-5120-5120-bem-sol.fif")

    fwd = mne.make_forward_solution(
        raw.info, trans=trans, src=src, bem=bem, eeg=True, mindist=5.0, n_jobs=10
    )
    print("Created forward solution")

    inv = mne.minimum_norm.make_inverse_operator(raw.info, fwd, noise_cov)
    print("Created inverse operator with identity noise covariance")

    stc = mne.minimum_norm.apply_inverse_raw(
        raw, inv, lambda2=1.0 / 9.0, method="MNE", pick_ori="normal", verbose=True
    )

    # mne.viz.plot_alignment(
    #     raw.info,
    #     src=src,
    #     eeg=["original", "projected"],
    #     trans='fsaverage',
    #     show_axes=True,
    #     mri_fiducials=True,
    #     dig="fiducials",
    # )
    print(
        "Computed continuous source estimates using MNE with identity noise covariance"
    )

    if config is not None:
        save_stc_to_file(stc, config, stage="post_source_localization")

    matplotlib.use("Agg")
    return stc


def estimate_source_function_epochs(epochs: mne.Epochs, config: dict = None):
    """
    Perform source localization on epoched EEG data using an identity matrix
    for noise covariance.
    """
    # --------------------------------------------------------------------------
    # Preprocessing for Source Localization
    # --------------------------------------------------------------------------
    matplotlib.use("Qt5Agg")

    epochs.set_eeg_reference("average", projection=True)
    print("Set EEG reference to average")

    noise_cov = mne.make_ad_hoc_cov(epochs.info)
    print("Using an identity matrix for noise covariance")

    # --------------------------------------------------------------------------
    # Source Localization Setup
    # --------------------------------------------------------------------------
    fs_dir = fetch_fsaverage()
    trans = "fsaverage"
    src = mne.read_source_spaces(f"{fs_dir}/bem/fsaverage-ico-5-src.fif")
    bem = mne.read_bem_solution(f"{fs_dir}/bem/fsaverage-5120-5120-5120-bem-sol.fif")

    fwd = mne.make_forward_solution(
        epochs.info, trans=trans, src=src, bem=bem, eeg=True, mindist=5.0, n_jobs=10
    )
    print("Created forward solution")

    inv = mne.minimum_norm.make_inverse_operator(epochs.info, fwd, noise_cov)
    print("Created inverse operator with identity noise covariance")

    stc = mne.minimum_norm.apply_inverse_epochs(
        epochs, inv, lambda2=1.0 / 9.0, method="MNE", pick_ori="normal", verbose=True
    )

    print(
        "Computed source estimates for epochs using MNE with identity noise covariance"
    )

    if config is not None:
        # For epochs, we get a list of STCs, so we might need to handle this differently
        # or save each epoch separately
        if isinstance(stc, list):
            print(f"Generated {len(stc)} source estimates for epochs")
            # Optionally save the first few as examples
            for i, stc_epoch in enumerate(stc[: min(3, len(stc))]):
                save_stc_to_file(
                    stc_epoch, config, stage=f"post_source_localization_epoch_{i}"
                )
        else:
            save_stc_to_file(stc, config, stage="post_source_localization")

    return stc