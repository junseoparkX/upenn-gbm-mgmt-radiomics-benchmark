### Test set construction (fixed 30 subjects)

We build a fixed independent test set of 30 subjects (balanced 15/15) in two stages to avoid (i) having too small a training set when using only the full intersection across parts, and (ii) having zero overlap for some parts when sampling purely at random from the full cohort.

**Stage A: Core-10 from `XY_mgmt.csv`**
- Start from `MRI/data/XY_mgmt.csv` (contains `ID`, `y_mgmt`, and feature columns).
- Preprocess by dropping any subject whose feature row has **≥ 50 NaNs** (NaNs are counted across all feature columns; non-numeric values are coerced to NaN for counting).
- From the remaining subjects, randomly sample **10 subjects** with a fixed seed:
  - **5 MGMT methylated** (`y_mgmt = 1`)
  - **5 MGMT unmethylated** (`y_mgmt = 0`)
- These 10 subjects form the **core** test subset (`core10`).

**Stage B: Extra-20 from clinical cohort (excluding Core-10)**
- Load `MRI/preprocessing_data/UPENN-GBM_clinical_info_v2.1.csv` and keep only clean MGMT labels:
  - `MGMT ∈ {Methylated, Unmethylated}`
  - Map to `y_mgmt ∈ {1, 0}`
- Exclude all `core10` subject IDs from the clinical pool.
- Randomly sample **20 additional subjects** with the same fixed seed:
  - **10 MGMT methylated** (`y_mgmt = 1`)
  - **10 MGMT unmethylated** (`y_mgmt = 0`)
- These 20 subjects form the supplemental subset (`extra20`).

**Final test set**
- Concatenate `core10` and `extra20` → **30 unique subjects** total.
- Verify class balance: **15 methylated + 15 unmethylated**.
- Save as `MRI/data/test_ids_core10_plus_extra20_seed{seed}.csv` with columns:
  - `ID`, `y_mgmt`, `source` (either `XY_core` or `clinical_extra`)
