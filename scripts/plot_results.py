"""Make PNG figures from a forecasting run into outputs/<run>/figures/.

    python scripts/plot_results.py --run exercise-400                  # all figures
    python scripts/plot_results.py --run exercise-400 --kind day --person Loop:123 --day 2026-03-02
    python scripts/plot_results.py --run exercise-400 --kind hour --metric lows_caught

Without --person/--day, the day plot picks a random test person-day that contains a low
(use --seed for a different one). Prints the paths of the figures it wrote.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from glucose_lab import plots

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("--run", required=True, help="folder name under outputs/")
p.add_argument("--kind", choices=["day", "clarke", "hour", "all"], default="all")
p.add_argument("--models", nargs="*", help="default: every model in the run")
p.add_argument("--person")
p.add_argument("--day", help="YYYY-MM-DD")
p.add_argument("--metric", default="lows_caught", help="score column for the hour plot")
p.add_argument("--seed", type=int, default=0)
args = p.parse_args()

run = ROOT / "outputs" / args.run
config = json.loads((run / "config.json").read_text())
models = args.models or config["models"]
figs = run / "figures"
figs.mkdir(exist_ok=True)
written = []

if args.kind in ("day", "clarke", "all"):
    preds = pd.read_parquet(run / "predictions.parquet")

if args.kind in ("day", "all"):
    person, day = args.person, args.day
    if not (person and day):
        days = preds.assign(day=preds["time"].dt.normalize())
        lows = days[days["actual"] < config["low"]][["person", "day"]].drop_duplicates()
        pick = lows.iloc[np.random.default_rng(args.seed).integers(len(lows))]
        person, day = person or pick["person"], day or pick["day"]
    path = figs / f"day_{str(person).replace(':', '-')}_{pd.Timestamp(day):%Y-%m-%d}.png"
    plots.plot_day(preds, person, day, config["low"], models, path)
    written.append(path)

if args.kind in ("clarke", "all"):
    path = figs / "clarke.png"
    plots.plot_clarke(preds, models, path, seed=args.seed)
    written.append(path)

if args.kind in ("hour", "all"):
    by_hour = pd.read_csv(run / "scores_by_hour.csv", index_col=[0, 1])
    path = figs / f"by_hour_{args.metric}.png"
    plots.plot_by_hour(by_hour, args.metric, models, path)
    written.append(path)

for w in written:
    print(w)
