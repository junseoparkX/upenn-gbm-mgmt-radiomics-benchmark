<<<<<<< HEAD
<<<<<<< HEAD
# upenn-gbm-mgmt-radiomics-benchmark
=======
=======
>>>>>>> 61b6581 (Update: feature selection + train/test export)
# UPENN-GBM MGMT Prediction (Segmentation-based Radiomics) — Reproduction & Comparison

## Goal
Our goal is to reproduce and compare the paper’s **Random Forest (RF) radiomics baseline** for **MGMT methylation classification** using **segmentation-based radiomic features** (CaPTk `segm_*` CSVs) from the UPENN-GBM cohort.

We will specifically compare our results against the paper’s reported **Mean AUC ± STD** for each **MRI/DTI sequence × tumor area** combination.

**Scope decision:** we will **exclude WT (whole tumor)** and focus on:
- **NET** (necrosis / non-enhancing tumor core depending on naming)
- **ED** (edema)
- **EN** (enhancing tumor)

## What we are comparing to (paper)
The paper reports RF performance summarized as:
- **Table 1:** MRI sequences (e.g., FLAIR, T1Gd, T1, T2, and all_modality) × areas (NET, ED, EN, WT)
- **Table 2:** DTI sequences (AD, FA, RD, TR, and all_modality) × areas (NET, ED, EN, WT)

We will compare our computed AUCs (and variability) to these tables, focusing on **NET/ED/EN only**.


### Key inputs
- `preprocessing_data/Radiomic_Features_CaPTk_segm_<SEQUENCE>_<AREA>.csv`
  - Radiomics features extracted from **segmentation-based** tumor regions.
  - Contains `SubjectID` and many feature columns.
- `preprocessing_data/UPENN-GBM_clinical_info_v2.1.csv`
  - Clinical labels including `MGMT` (Methylated / Unmethylated).
- `data/XY_mgmt.csv`
  - A merged “master” table containing `ID`, `y_mgmt`, and radiomic features (used to build a reliable small “core” set).

## Label definition
We build the binary label:
- `y_mgmt = 1` if `MGMT == "Methylated"`
- `y_mgmt = 0` if `MGMT == "Unmethylated"`
Any `MGMT` values outside these two classes (e.g., Not Available / Indeterminate) are dropped.

## Method overview (what we do)
### 1) Build a fixed test set (30 subjects, 15/15)
We create a fixed test set in two stages to avoid:
- tiny training sets if we only sample from the strict intersection across all parts
- zero-overlap test sets if we sample fully at random from the full cohort

**Stage A: Core-10 from `XY_mgmt.csv`**
- Drop XY rows with **≥ 50 NaNs** across feature columns.
- Sample **10 subjects**: **5 methylated + 5 unmethylated**.

**Stage B: Extra-20 from clinical cohort**
- From `UPENN-GBM_clinical_info_v2.1.csv`, keep only clean MGMT labels.
- Exclude the Core-10 IDs.
- Sample **20 subjects**: **10 methylated + 10 unmethylated**.

**Final test set:** 30 unique subjects with balanced classes (15/15),
saved as:
- `data/test_ids_core10_plus_extra20_seed340.csv`

### 2) Build X and y for a given (Sequence, Area)
For each segmentation-based radiomics file (example: `FLAIR_NC`):
- Load the features CSV
- Merge with clinical labels on `SubjectID` ↔ `ID`
- Drop non-binary MGMT labels
- Build:
  - `X`: numeric radiomic feature matrix
  - `y`: binary MGMT label vector

### 3) Verify test ID overlap and split train/test
Using the fixed test IDs:
- `test = subjects in current df whose ID is in test_ids`
- `train = remaining subjects`
Note: for a specific (Sequence, Area) file, test overlap may be < 30 if some test subjects do not exist in that file.

### 4) Feature filtering with XGBoost (importance > 0)
Before final training, we optionally reduce dimensionality:
- Train an `XGBClassifier` on `(X_train, y_train)`
- Keep only features with `feature_importances_ > 0`
- Filter both train and test matrices to these selected features
- Report how many features remain

### 5) Save model-ready matrices for this (Sequence, Area)
For downstream model training/evaluation (e.g., RF baseline):
- Save to `MRI/Net/`:
  - `X_train.csv`, `y_train.csv`, `X_test.csv`, `y_test.csv`

## Planned experiments (NET/ED/EN only)
We will iterate over segmentation-based radiomics CSVs for:
- MRI sequences: `FLAIR`, `T1Gd`, `T1`, `T2`, `all_modality`
- DTI sequences: `AD`, `FA`, `RD`, `TR`, `all_modality`
and tumor areas:
- `NET`, `ED`, `EN`
(we will **not run WT**)

For each (Sequence, Area):
1) Build `X, y` from the corresponding CaPTk segm CSV + clinical labels
2) Split using the fixed test set
3) (Optional) apply XGBoost importance filtering
4) Train and evaluate a Random Forest baseline
5) Record AUC (and variability if using CV/bootstrap)
6) Compare against the paper’s Table 1 / Table 2 values

## Reporting
For each (Sequence, Area), we will report:
- `n_train`, `n_test_used` (overlap size)
- AUC (and STD if applicable)
- Whether feature filtering was applied and how many features remained

## Notes on naming (NET / NC)
Some files may use names like `NC` for necrosis / non-enhancing core.
We treat this as the paper’s **NET** region for comparison, but we keep the raw filename tag in our logs for clarity.
<<<<<<< HEAD
>>>>>>> 61b6581 (Update: feature selection + train/test export)
=======
>>>>>>> 61b6581 (Update: feature selection + train/test export)
