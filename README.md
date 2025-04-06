# 2DTM Postprocessing

A modular Python package for postprocessing 2D template matching results from cryo-EM workflows (e.g., cisTEM), including 2DTM p-value calculation, particle extraction and filtering.

---

## Installation

```bash
git clone https://github.com/kekexinz/2dtm_postprocess
cd 2dtm_postporcess
pip install -e . # editable mode
```

### 📦 Full Example

## Usage

### `extract-particles`
Extract initial particle peaks from 2DTM search.
```bash
extract-particles \ 
--db_file <cistem.db> \
--tm_job_id 1 \
--ctf_job_id 1 \
--d_xy_cutoff 10 \ # min_peak_radius
--exclude_borders 30 \
--metric pval \
--metric_cutoff 8.0 \
--pixel_size 1.0 \
--threads 12 \
--output <output.star>
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
  [--filter_by_image_thickness] \
  [--thickness_cutoff_ub 500.0] \
  --output filtered_output.star
```