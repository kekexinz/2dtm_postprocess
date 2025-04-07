import numpy as np 
import pandas as pd
from tm_post.geodesic import calculate_all_geodesic_means

def get_thickness_lookup(df_ctf, df_info):
    """
    Create a lookup function for image thickness based on ORIGINAL_IMAGE_FILENAME.
    Returns a function that takes a filename string and returns the sample thickness.
    """
    thickness_map = df_ctf.set_index('IMAGE_ASSET_ID')['SAMPLE_THICKNESS'].to_dict()
    filename_to_id = df_info.set_index('FILENAME')['IMAGE_ASSET_ID'].to_dict()
    def lookup(filename):
        clean_name = filename.strip("'")
        image_id = filename_to_id.get(clean_name, None)
        if image_id is not None:
            return thickness_map.get(image_id, np.nan)
        return np.nan
    
    return lookup

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
    df_out = df.copy()
    df_out["SCORE"] = 0 # Use Score column to flag filtered particles

    kept_mask = pd.Series([True] * len(df_out))

    # Basic snr/avg filtering
    if avg_cutoff_lb is not None:
        kept_mask &= df_out['AVG'] >= avg_cutoff_lb
    
    if snr_cutoff_ub is not None:
        kept_mask &= df_out["SNR"] <= snr_cutoff_ub

    print(f"[INFO] SNR/AVG filter applied: {kept_mask.sum()} particles retained.")

    # Apply thickness filtering
    get_thickness = get_thickness_lookup(df_ctf, df_info)    
    df_out["image_thickness"] = df_out["ORIGINAL_IMAGE_FILENAME"].apply(get_thickness)

    if filter_by_image_thickness and thickness_lb is not None and thickness_ub is not None:
        thick_mask = (
            (df_out["image_thickness"] > thickness_lb) &
            (df_out["image_thickness"] < thickness_ub)
        )
        kept_mask &= thick_mask
        print(f"[INFO] Thickness filter applied: {kept_mask.sum()} particles retained.")

    # Apply angular invariance filtering
    if filter_by_angular_invariance:
        print(f"[INFO] Calculating angular variance...")
        geodesic_means = calculate_all_geodesic_means(
            df_out, image_list, psi_list, theta_list, phi_list,
            pixel_size, r=geodesic_r, threads=geodesic_threads
        )
        df_out['mean_geodesic_distance'] = geodesic_means

        # Apply filter
        geodesic_keep_mask = (geodesic_means <=
                              np.nanquantile(geodesic_means, geodesic_threshold)
                              if geodesic_method == 'quantile'
                              else geodesic_means <= geodesic_threshold)
        kept_mask &= geodesic_keep_mask
        print(f"[INFO] Geodesic filter applied: {kept_mask.sum()} particles retained.")
        
    # Update SCORE column
    df_out.loc[kept_mask, 'SCORE'] = 1

    return df_out
