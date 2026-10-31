"""Loaders for downloaded datasets. Fetch them first with scripts/fetch_data.py.

Loaders only reshape files into tables; they don't drop, fill or filter readings,
since those are analysis decisions.
"""

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"


def load_shanghai(kind="T1DM"):
    """All recording periods for ShanghaiT1DM or ShanghaiT2DM, one row per timestamp.

    Adds `patient` and `period` from the file name (<patient>_<period>_<start date>);
    every original column is kept. CGM is every 15 minutes, in mg/dL.
    """
    folder = DATA / "shanghai" / f"Shanghai_{kind}"
    if not folder.exists():
        raise FileNotFoundError(f"{folder} missing; run: python scripts/fetch_data.py shanghai")
    frames = []
    for f in sorted(folder.glob("*.xls*")):
        patient, period, _ = f.stem.split("_")
        df = pd.read_excel(f)
        df.insert(0, "period", int(period))
        df.insert(0, "patient", patient)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_shanghai_summary(kind="T1DM"):
    """Clinical summary sheet: one row per recording period."""
    return pd.read_excel(DATA / "shanghai" / f"Shanghai_{kind}_Summary.xlsx")


if __name__ == "__main__":
    for kind in ("T1DM", "T2DM"):
        df = load_shanghai(kind)
        cgm = df.filter(like="CGM").iloc[:, 0]
        print(f"Shanghai {kind}: {df['patient'].nunique()} patients, "
              f"{df.groupby(['patient', 'period']).ngroups} recording periods, "
              f"{cgm.notna().sum()} CGM readings ({cgm.isna().sum()} blank)")
