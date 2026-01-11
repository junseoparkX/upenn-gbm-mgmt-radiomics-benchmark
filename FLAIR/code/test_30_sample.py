# test_30_sample.py
# Create a 30-subject fixed test set in two stages:
#   (A) core10: sample 10 subjects (5 pos / 5 neg) from data/XY_mgmt.csv after NaN filtering
#   (B) extra20: sample 20 subjects (10 pos / 10 neg) from preprocessing_data/UPENN-GBM_clinical_info_v2.1.csv
#               excluding IDs already used in core10, and (optionally) excluding IDs present in XY_mgmt.csv
#
# Saves to: MRI/data/test_ids_core10_plus_extra20_seed{seed}.csv

from pathlib import Path
import argparse
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=340, help="Random seed.")
    parser.add_argument("--nan_threshold", type=int, default=50,
                        help="Drop a row from XY if (#NaNs in XY feature columns) >= this.")
    parser.add_argument("--exclude_all_xy_from_extra", action="store_true",
                        help="If set, extra20 will exclude ALL IDs that appear in XY_mgmt.csv (not just core10).")
    args = parser.parse_args()

    # Paths (robust, independent of cwd)
    code_dir = Path(__file__).resolve().parent
    mri_dir = code_dir.parent

    xy_path = mri_dir / "data" / "XY_mgmt.csv"
    clin_path = mri_dir / "preprocessing_data" / "UPENN-GBM_clinical_info_v2.1.csv"
    out_path = mri_dir / "data" / f"test_ids_core10_plus_extra20_seed{args.seed}.csv"

    try:
        # -------------------------
        # (A) core10 from XY_mgmt.csv
        # -------------------------
        if not xy_path.exists():
            raise FileNotFoundError(f"Missing file: {xy_path}")

        xy = pd.read_csv(xy_path)
        if "ID" not in xy.columns or "y_mgmt" not in xy.columns:
            raise ValueError("XY_mgmt.csv must contain columns: ID, y_mgmt")

        # Feature cols for NaN counting
        feat_cols = [c for c in xy.columns if c not in ["ID", "y_mgmt"]]
        feat = xy[feat_cols].apply(pd.to_numeric, errors="coerce")
        nan_counts = feat.isna().sum(axis=1)

        xy_clean = xy.loc[nan_counts < args.nan_threshold].copy()

        pos_xy = xy_clean[xy_clean["y_mgmt"] == 1]
        neg_xy = xy_clean[xy_clean["y_mgmt"] == 0]

        if len(pos_xy) < 5 or len(neg_xy) < 5:
            raise ValueError(f"Not enough XY samples after cleaning for 5/5. pos={len(pos_xy)}, neg={len(neg_xy)}")

        rng = np.random.default_rng(args.seed)
        core_pos_ids = rng.choice(pos_xy["ID"].astype(str).values, size=5, replace=False)
        core_neg_ids = rng.choice(neg_xy["ID"].astype(str).values, size=5, replace=False)

        core10 = pd.DataFrame({
            "ID": np.concatenate([core_pos_ids, core_neg_ids]),
            "y_mgmt": [1]*5 + [0]*5,
            "source": ["XY_core"]*10
        })

        core10_ids = set(core10["ID"].astype(str))
        all_xy_ids = set(xy["ID"].astype(str))

        # -------------------------
        # (B) extra20 from clinical info
        # -------------------------
        if not clin_path.exists():
            raise FileNotFoundError(f"Missing file: {clin_path}")

        clin = pd.read_csv(clin_path)
        if "ID" not in clin.columns or "MGMT" not in clin.columns:
            raise ValueError("Clinical CSV must contain columns: ID, MGMT")

        clin = clin[clin["MGMT"].isin(["Methylated", "Unmethylated"])].copy()
        clin["y_mgmt"] = clin["MGMT"].map({"Methylated": 1, "Unmethylated": 0}).astype(int)
        clin["ID"] = clin["ID"].astype(str)

        # Exclude core10, and optionally exclude all XY IDs
        exclude_ids = set(core10_ids)
        if args.exclude_all_xy_from_extra:
            exclude_ids |= set(all_xy_ids)

        clin_pool = clin[~clin["ID"].isin(exclude_ids)].copy()

        pos_c = clin_pool[clin_pool["y_mgmt"] == 1]
        neg_c = clin_pool[clin_pool["y_mgmt"] == 0]

        if len(pos_c) < 10 or len(neg_c) < 10:
            raise ValueError(
                "Not enough clinical samples to draw extra20 (10/10) after exclusions.\n"
                f"pos={len(pos_c)}, neg={len(neg_c)}\n"
                "Tip: run without --exclude_all_xy_from_extra if pool is too small."
            )

        extra_pos_ids = rng.choice(pos_c["ID"].values, size=10, replace=False)
        extra_neg_ids = rng.choice(neg_c["ID"].values, size=10, replace=False)

        extra20 = pd.DataFrame({
            "ID": np.concatenate([extra_pos_ids, extra_neg_ids]),
            "y_mgmt": [1]*10 + [0]*10,
            "source": ["clinical_extra"]*20
        })

        # -------------------------
        # Final 30 + checks + save
        # -------------------------
        test30 = pd.concat([core10, extra20], ignore_index=True)

        # Uniqueness check
        if test30["ID"].nunique() != 30:
            dup = test30[test30["ID"].duplicated(keep=False)].sort_values("ID")
            raise ValueError(f"Duplicate IDs found in test30:\n{dup}")

        # Balance check (must be 15/15)
        counts = test30["y_mgmt"].value_counts().to_dict()

        print("=== XY cleaning summary ===")
        print(f"XY rows before: {len(xy)}")
        print(f"XY rows dropped (NaNs >= {args.nan_threshold}): {(nan_counts >= args.nan_threshold).sum()}")
        print(f"XY rows kept: {len(xy_clean)}")
        print("XY class counts after cleaning:", xy_clean["y_mgmt"].value_counts().to_dict())

        print("\n=== Core10 (from XY) ===")
        print("Core10 counts:", core10["y_mgmt"].value_counts().to_dict())

        print("\n=== Extra20 (from clinical) ===")
        print("Extra20 counts:", extra20["y_mgmt"].value_counts().to_dict())

        print("\n=== Final test30 check (must be 15/15) ===")
        print(counts)

        # Shuffle for nice ordering
        test30 = test30.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        test30.to_csv(out_path, index=False)
        print("\nSaved CSV:", out_path)

    except Exception as e:
        print("ERROR:", str(e))


if __name__ == "__main__":
    main()
