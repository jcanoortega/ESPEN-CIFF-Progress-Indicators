"""
prepare_data.py
───────────────
Converts the ESPEN–CIFF Excel source files into JSON files consumed by
the dashboard.  Run this script whenever the source data are updated.

Usage
-----
    python prepare_data.py [--src-dir PATH] [--out-dir PATH]

    --src-dir   Directory containing the source Excel files.
                Default: current directory (looks for PCT_Indicators_CIFF*.xlsx
                and NTD_System_Integration.xlsx).
    --out-dir   Directory where JSON files will be written.
                Default: ./data/

Requirements
------------
    pip install pandas openpyxl
"""

import argparse
import json
import os
import glob
import shutil
import numpy as np
import pandas as pd


# ── helpers ──────────────────────────────────────────────────────────────────

def clean(v):
    """Convert numpy scalars and NaN to native Python types or None."""
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        f = float(v)
        return None if np.isnan(f) else round(f, 4)
    return v


def clean_record(row: dict) -> dict:
    return {k: clean(v) for k, v in row.items()}


# ── main ─────────────────────────────────────────────────────────────────────

def prepare(src_dir: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    # ── Locate source files ──────────────────────────────────────────────────
    pct_files = glob.glob(os.path.join(src_dir, "PCT_Indicators_CIFF*.xlsx"))
    si_files  = glob.glob(os.path.join(src_dir, "NTD_System_Integration*.xlsx"))

    if not pct_files:
        raise FileNotFoundError(f"No PCT_Indicators_CIFF*.xlsx found in {src_dir}")
    if not si_files:
        raise FileNotFoundError(f"No NTD_System_Integration*.xlsx found in {src_dir}")

    pct_path = sorted(pct_files)[-1]   # use latest if multiple
    si_path  = sorted(si_files)[-1]

    print(f"Reading PCT indicators  : {pct_path}")
    print(f"Reading system integration: {si_path}")

    xl  = pd.ExcelFile(pct_path)
    xl2 = pd.ExcelFile(si_path)

    # ── 1. Dictionaries ──────────────────────────────────────────────────────
    dc = xl.parse("Dictionary_Country")
    da = xl.parse("Dictionary_WHO_AFRO")
    dicts = {
        "country": {r["Indicator"]: r["Description"] for _, r in dc.iterrows()},
        "afro":    {r["Indicator"]: r["Description"] for _, r in da.iterrows()},
    }
    _write_json(dicts, out_dir, "dictionaries.json")

    # ── 2. AFRO regional indicators ──────────────────────────────────────────
    afro = xl.parse("WHO_AFRO_Region_Indicators")
    afro_records = []
    for _, row in afro.iterrows():
        rec = {"indicator": row["Indicator"]}
        for col in afro.columns[1:]:
            rec[str(int(col))] = clean(row[col])
        afro_records.append(rec)
    _write_json(afro_records, out_dir, "afro_indicators.json")

    # ── 3. Country indicators ────────────────────────────────────────────────
    df = xl.parse("Country_Indicators")
    # Distinguish Tanzania Zanzibar from mainland
    df.loc[df["ADMIN0ISO2"] == "ZZ", "ADMIN0ISO2"] = "TZ_Z"
    # Fill missing Namibia ISO2
    df.loc[df["ADMIN0"].str.contains("Namibia", na=False) & df["ADMIN0ISO2"].isna(),
           "ADMIN0ISO2"] = "NA"
    country_records = [clean_record(r) for r in df.to_dict(orient="records")]
    _write_json(country_records, out_dir, "country_indicators.json")

    # ── 4. System integration ────────────────────────────────────────────────
    sys_df = xl2.parse("NTD_System_Integration")
    qs_df  = xl2.parse("Questions")
    sys_df = sys_df.where(pd.notnull(sys_df), None)
    q_records = [
        {"q": str(int(r["Question"])), "text": r["System-level indicator"]}
        for _, r in qs_df.iterrows()
    ]
    si_payload = {
        "questions": q_records,
        "data": sys_df.to_dict(orient="records"),
    }
    _write_json(si_payload, out_dir, "system_integration.json")

    # ── 5. Copy logo assets (if source logos are present) ───────────────────
    assets_dir = os.path.join(os.path.dirname(out_dir), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    for logo in ["CIFF.png", "ESPEN-Bleu.png"]:
        src = os.path.join(src_dir, logo)
        dst = os.path.join(assets_dir, logo)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy(src, dst)
            print(f"Copied logo: {logo}")

    print("\n✓ Data preparation complete.")
    print(f"  Output directory: {os.path.abspath(out_dir)}")
    for fname in ["dictionaries.json", "afro_indicators.json",
                  "country_indicators.json", "system_integration.json"]:
        size = os.path.getsize(os.path.join(out_dir, fname))
        print(f"  {fname}: {size // 1024} KB")


def _write_json(obj, directory: str, filename: str) -> None:
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare dashboard data from Excel sources.")
    parser.add_argument("--src-dir", default=".", help="Directory with Excel source files.")
    parser.add_argument("--out-dir", default="data", help="Output directory for JSON files.")
    args = parser.parse_args()
    prepare(src_dir=args.src_dir, out_dir=args.out_dir)
