# 2DTM Postprocessing

A modular Python package for postprocessing 2D template matching results from cryo-EM workflows (e.g., cisTEM), including 2DTM p-value calculation, particle extraction and filtering.

---

## Installation

```bash
git clone https://github.com/kekexinz/2dtm_postprocess
cd 2dtm_postporcess
pip install -e . # editable mode
```

## 📦 Usage

### `extract-particles`
Extract initial particle peaks from 2DTM search.
```bash
extract-particles \ 
--db_file <cistem.db> \
--tm_job_id 1 \
--ctf_job_id 1 \
--pixel_size 1.0 \
--output <output.star>
[--d_xy_cutoff 10] \ # optional, min_peak_radius when locating local maxima
[--exclude_borders 30] \ # avoid finding partial particles near the edge of the image
[--metric pval] \ # "zscore" or "pval"
[--metric_cutoff 8.0] \
[--threads 12] \
```

### `filter-particles`

Filter particles based on image thickness and/or angular invariance.

```bash
filter-particles \
  --star_file <input.star> \
  --db_file <cistem.db> \
  --tm_job_id 1 \
  --ctf_job_id 1 \
  --pixel_size 1.0 \
  --output filtered_output.star \
  [--avg_cutoff_lb 0.0] \
  [--snr_cutoff_ub 9.0] \ 
  [--filter_by_image_thickness] \ # filter out thick images
  [--thickness_cutoff_lb] \
  [--thickness_cutoff_ub] \
  [--filter_by_angular_invariance] \
  [--geodesic_r] \
  [--geodesic_threads] \
  [--geodesic_method] \
  [--geodesic_threshold] \
```