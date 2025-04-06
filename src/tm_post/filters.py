import numpy as np 
import pandas as pd
from tm_post.geodesic import calculate_all_geodesic_means

def apply_image_thickness_filter(peaks, df_ctf, df_info, cutoff_lb, cutoff_ub):
    df_ctf = df_ctf[(df_ctf['SAMPLE_THICKNESS']>cutoff_lb) & (df_ctf['SAMPLE_THICKNESS']<cutoff_ub)]
    filenames = df_info[df_info['IMAGE_ASSET_ID'].isin(df_ctf['IMAGE_ASSET_ID'].values)]['FILENAME']
    filenames = [f"'{filename}'" for filename in filenames]
    peaks_filtered = peaks[peaks['ORIGINAL_IMAGE_FILENAME'].isin(filenames)]
    return peaks_filtered

def apply_angular_invariance_filter(df, mean_geodesic_array, method='quantile', threshold=0.95):
    """
    Filter rows in df based on geodesic distance.
    - method='quantile': keep rows <= quantile threshold
    - method='cutoff': keep rows <= fixed distance threshold
    """
    if method == 'quantile':
        cutoff = np.nanquantile(mean_geodesic_array, threshold)
    elif method == 'cutoff':
        cutoff = threshold
    else:
        raise ValueError("method must be 'quantile' or 'cutoff'")

    keep_mask = mean_geodesic_array <= cutoff
    df_filtered = df[keep_mask].reset_index(drop=True)
    return df_filtered, keep_mask, cutoff


def apply_filter(
    df,
    image_list,
    psi_list,
    theta_list,
    phi_list,
    pixel_size,
    df_ctf,
    df_info,
    avg_cutoff_lb=None,
    snr_cutoff_ub=None,
    filter_by_image_thickness=True,
    thickness_lb=None,
    thickness_ub=None,
    filter_by_angular_invariance=False,
    geodesic_r=4,
    geodesic_threads=8,
    geodesic_method='quantile',  # or 'cutoff'
    geodesic_threshold=0.8       # quantile (0.8) or distance cutoff (e.g., 0.3)
):
    """
    Apply thickness and geodesic filtering on a DataFrame of peaks.

    Parameters:
    - df: Input DataFrame.
    - filter_by_image_thickness: Whether to perform geodesic distance filtering.
    - thickness_col: Name of the column storing thickness values.
    - thickness_cutoff: Minimum thickness to keep (if filtering by thickness).
    - filter_by_angular_invariance: Whether to perform geodesic distance filtering.
    - geodesic_r: Radius in pixels for local patch.
    - geodesic_threads: Number of threads for parallel geodesic computation.
    - geodesic_method: 'quantile' or 'cutoff'.
    - geodesic_threshold: Threshold value for filtering.

    Returns:
    - Filtered DataFrame.
    - Optionally added columns: 'mean_geodesic_distance'
    """
    df_filtered = df.copy()

    # Basic snr/avg filtering
    if avg_cutoff_lb is not None:
        df_filtered = df_filtered[df_filtered['AVG'] >= avg_cutoff_lb]
    
    if snr_cutoff_ub is not None:
        df_filtered = df_filtered[df_filtered['SNR'] <= snr_cutoff_ub]

    print(f"[INFO] SNR/AVG filter applied: {len(df_filtered)} particles retained.")

    # Apply thickness filtering
    if filter_by_image_thickness and thickness_lb is not None and thickness_ub is not None:
        df_filtered = apply_image_thickness_filter(df_filtered, df_ctf, df_info, thickness_lb, thickness_ub)
        print(f"[INFO] Thickness filter applied: {len(df_filtered)} particles retained.")

    # Apply geodesic distance filtering
    if filter_by_angular_invariance:
        print(f"[INFO] Calculating geodesic distances...")
        geodesic_means = calculate_all_geodesic_means(
            df_filtered, image_list, psi_list, theta_list, phi_list,
            pixel_size, r=geodesic_r, threads=geodesic_threads
        )
        df_filtered['mean_geodesic_distance'] = geodesic_means

        df_filtered, mask, cutoff = apply_angular_invariance_filter(
            df_filtered, geodesic_means, method=geodesic_method, threshold=geodesic_threshold
        )
        print(f"[INFO] Geodesic filter applied: {len(df_filtered)} particles retained.")

    return df_filtered
