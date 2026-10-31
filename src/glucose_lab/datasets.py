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


METABONET_DEFAULT_COLUMNS = ["source_file", "id", "date", "CGM", "insulin", "carbs", "is_test"]


def load_metabonet(columns=METABONET_DEFAULT_COLUMNS, studies=None):
    """MetaboNet public tier: one row per person per 5-minute step.

    The whole file is 155M rows by 37 columns, too big for memory, so pick `columns`
    (columns=None loads all) and optionally `studies` (values of `source_file`, e.g.
    ["Loop", "OhioT1DM"]). Blank CGM readings stay blank.

    `id` is only unique within a study, so a `person` column ("<study>:<id>") is added.
    """
    import pyarrow.parquet as pq

    path = DATA / "metabonet" / "metabonet_public.parquet"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing; run: python scripts/fetch_data.py metabonet")
    if columns is not None:
        columns = list(dict.fromkeys(["source_file", "id", *columns]))
    filters = [("source_file", "in", list(studies))] if studies else None
    df = pq.read_table(path, columns=columns, filters=filters,
                       read_dictionary=["source_file", "id"]).to_pandas()
    codes = df.groupby(["source_file", "id"], observed=True, sort=False).ngroup()
    keys = df[["source_file", "id"]].drop_duplicates()  # same first-seen order as ngroup
    names = (keys["source_file"].astype(str) + ":" + keys["id"].astype(str)).to_numpy()
    df.insert(0, "person", pd.Categorical.from_codes(codes.to_numpy(), names))
    return df


if __name__ == "__main__":
    df = load_metabonet(["date", "CGM"], studies=["OhioT1DM", "ShanghaiT1DM"])
    print(f"MetaboNet (2 small studies): {df['person'].nunique()} people, {len(df)} rows, "
          f"{df['CGM'].isna().mean():.0%} blank CGM")
    for kind in ("T1DM", "T2DM"):
        df = load_shanghai(kind)
        cgm = df.filter(like="CGM").iloc[:, 0]
        print(f"Shanghai {kind}: {df['patient'].nunique()} patients, "
              f"{df.groupby(['patient', 'period']).ngroups} recording periods, "
              f"{cgm.notna().sum()} CGM readings ({cgm.isna().sum()} blank)")
