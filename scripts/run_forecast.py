"""Run one forecasting experiment on MetaboNet and save scores to outputs/<name>/.

Every scientific choice is a flag; config.json records what was used. Example:
    python scripts/run_forecast.py --name trial --max-people 200 --history 24 --horizon 6 \\
        --low 70 --split person --test-frac 0.2
Run long ones with scripts/run-job.sh so they survive disconnects.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from glucose_lab import forecast as F
from glucose_lab.datasets import load_metabonet

ROOT = Path(__file__).resolve().parent.parent
MODELS = ["persistence", "trend", "ridge", "xgboost", "lstm"]

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("--name", required=True, help="output folder name under outputs/")
p.add_argument("--studies", nargs="*", help="MetaboNet studies to use (default: all)")
p.add_argument("--max-people", type=int, help="randomly sample this many people")
p.add_argument("--seed", type=int, default=0)
p.add_argument("--history", type=int, required=True, help="steps of past readings (5 min each)")
p.add_argument("--horizon", type=int, required=True, help="steps ahead to forecast")
p.add_argument("--low", type=float, required=True, help="mg/dL below which a reading counts as low")
p.add_argument("--max-gap", type=int, default=0, help="blank readings allowed in a history window")
p.add_argument("--stride", type=int, default=1, help="use every Nth window (thins overlapping windows)")
p.add_argument("--split", choices=["person", "study", "time"], required=True)
p.add_argument("--test-frac", type=float, help="for person/time splits")
p.add_argument("--test-studies", nargs="*", help="for study split")
p.add_argument("--models", nargs="*", default=MODELS, choices=MODELS)
p.add_argument("--trend-lookback", type=int, default=3)
p.add_argument("--epochs", type=int, default=5)
args = p.parse_args()

out = ROOT / "outputs" / args.name
out.mkdir(parents=True, exist_ok=True)
log_lines = []


def log(msg):
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    log_lines.append(line)


t0 = time.time()
log(f"loading MetaboNet ({'all studies' if not args.studies else ', '.join(args.studies)})")
df = load_metabonet(["date", "CGM"], studies=args.studies)
if args.max_people:
    people = df["person"].cat.remove_unused_categories().cat.categories
    keep = np.random.default_rng(args.seed).choice(people, min(args.max_people, len(people)), replace=False)
    df = df[df["person"].isin(keep)]
log(f"{df['person'].nunique()} people, {len(df):,} readings")

X, y, meta = F.make_windows(df, args.history, args.horizon, args.stride, args.max_gap)
del df
if args.split == "person":
    test = F.split_by_person(meta, args.test_frac, args.seed)
elif args.split == "study":
    test = F.split_by_study(meta, args.test_studies)
else:
    test = F.split_by_time(meta, args.test_frac)
Xtr, ytr, Xte, yte, mte = X[~test], y[~test], X[test], y[test], meta[test]
log(f"{len(X):,} windows: {len(Xtr):,} train ({meta[~test].person.nunique()} people), "
    f"{len(Xte):,} test ({mte.person.nunique()} people)")
if len(Xte) == 0 or len(Xtr) == 0:
    sys.exit("empty train or test set; check the split flags")

preds = {}
for m in args.models:
    log(f"model: {m}")
    if m == "persistence":
        preds[m] = F.predict_persistence(Xte)
    elif m == "trend":
        preds[m] = F.predict_trend(Xte, args.horizon, args.trend_lookback)
    elif m == "ridge":
        preds[m] = F.predict_ridge(Xtr, ytr, Xte, alpha=1.0)
    elif m == "xgboost":
        preds[m] = F.predict_xgboost(Xtr, ytr, Xte, n_estimators=300, max_depth=6, seed=args.seed)
    elif m == "lstm":
        preds[m] = F.predict_lstm(Xtr, ytr, Xte, hidden=64, epochs=args.epochs,
                                  batch_size=1024, seed=args.seed, log=log)

overall = pd.DataFrame({m: F.score(yte, p, args.low) for m, p in preds.items()}).T
by_hour = pd.concat({m: pd.DataFrame({h: F.score(yte[mte.hour == h], p[mte.hour == h], args.low)
                                      for h in range(24)}).T for m, p in preds.items()})
by_study = pd.concat({m: pd.DataFrame({s: F.score(yte[mte.study == s], p[mte.study == s], args.low)
                                       for s in sorted(mte.study.unique())}).T for m, p in preds.items()})
overall.to_csv(out / "scores.csv")
by_hour.to_csv(out / "scores_by_hour.csv")
by_study.to_csv(out / "scores_by_study.csv")
pd.DataFrame({"person": mte.person.to_numpy(), "time": mte.time.to_numpy(), "actual": yte,
              **{f"pred_{m}": p for m, p in preds.items()}}).to_parquet(out / "predictions.parquet")
(out / "config.json").write_text(json.dumps({**vars(args), "finished": datetime.now().isoformat(),
                                              "minutes": round((time.time() - t0) / 60, 1)}, indent=2))
pd.set_option("display.width", 200)
log("scores on test set:\n" + overall.round(3).to_string())
(out / "log.txt").write_text("\n".join(log_lines) + "\n")
log(f"saved to {out}")
