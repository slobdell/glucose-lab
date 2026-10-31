"""Figures for forecasting runs, rendered to PNG on builder3 (no screen needed).

Reads what scripts/run_forecast.py saved in outputs/<run>/. Colors are a fixed
colorblind-checked order, so a model keeps its color across every figure.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from glucose_lab.forecast import clarke_zones

INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
LOW_BAND, RANGE_BAND = "#f6d5d4", "#eeeeea"
MODEL_COLORS = {"persistence": "#2a78d6", "trend": "#eb6834", "ridge": "#1baf7a",
                "xgboost": "#eda100", "lstm": "#e87ba4"}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": INK,
})


def _label_line_ends(ax, x, series):
    """Direct-label each line at its right end, nudged apart so labels don't overlap."""
    lo, hi = ax.get_ylim()
    gap = 0.05 * (hi - lo)
    ends = sorted(((s.iloc[-1], name) for name, s in series.items() if s.notna().any()))
    placed = []
    for y, name in ends:
        if placed and y - placed[-1] < gap:
            y = placed[-1] + gap
        placed.append(y)
        ax.annotate(name, (x, y), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK_2)


def plot_day(preds, person, day, low, models, path):
    """One person's day: actual glucose with each model's forecast for the same moments."""
    d = preds[(preds["person"] == person) & (preds["time"].dt.normalize() == pd.Timestamp(day))]
    d = d.sort_values("time").set_index("time")
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.axhspan(0, low, color=LOW_BAND, lw=0, zorder=0)
    ax.axhspan(low, 180, color=RANGE_BAND, lw=0, zorder=0)
    ax.text(0.005, low - 3, f"low (<{low:g})", transform=ax.get_yaxis_transform(),
            va="top", fontsize=9, color=INK_2)
    ax.text(0.005, 177, "target range 70-180", transform=ax.get_yaxis_transform(),
            va="top", fontsize=9, color=INK_2)
    series = {}
    for m in models:
        s = d[f"pred_{m}"].astype(float)
        ax.plot(s.index, s, color=MODEL_COLORS[m], lw=1.5, alpha=0.9)
        series[m] = s
    ax.plot(d.index, d["actual"], color=INK, lw=2.2)
    series["actual"] = d["actual"]
    ax.set_ylim(min(40, d[["actual"] + [f"pred_{m}" for m in models]].min().min() - 10),
                max(250, d["actual"].max() + 20))
    _label_line_ends(ax, d.index[-1], series)
    ax.set_ylabel("glucose (mg/dL)")
    ax.set_title(f"{person}, {pd.Timestamp(day):%Y-%m-%d}: actual vs. forecast for the same time")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    handles = [plt.Line2D([], [], color=INK, lw=2.2, label="actual")] + \
              [plt.Line2D([], [], color=MODEL_COLORS[m], lw=1.5, label=m) for m in models]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.1), ncol=len(handles),
              frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_clarke(preds, models, path, max_points=200_000, seed=0):
    """Clarke error grid per model: each dot is one forecast; zone shares in the title."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(preds), min(max_points, len(preds)), replace=False)
    ref = preds["actual"].to_numpy()[idx]
    fig, axes = plt.subplots(1, len(models), figsize=(4 * len(models), 4.4), squeeze=False)
    for ax, m in zip(axes[0], models):
        pred = preds[f"pred_{m}"].to_numpy()[idx]
        zones = clarke_zones(ref, pred)
        ax.hexbin(ref, pred, gridsize=70, extent=(0, 400, 0, 400), bins="log",
                  cmap="Blues", mincnt=1, linewidths=0)
        _clarke_lines(ax)
        a, b, d = ((zones == z).mean() * 100 for z in "ABD")
        ax.set_title(f"{m}\nA {a:.1f}%  B {b:.1f}%  D {d:.1f}%", fontsize=10)
        ax.set_xlabel("actual (mg/dL)")
        ax.set_xlim(0, 400)
        ax.set_ylim(0, 400)
        ax.set_aspect("equal")
    axes[0][0].set_ylabel("forecast (mg/dL)")
    fig.suptitle("Clarke error grid (darker = more forecasts). A accurate, B benign, "
                 "C/D/E clinically risky", fontsize=10, color=INK_2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _clarke_lines(ax):
    kw = dict(color=INK_2, lw=0.8)
    ax.plot([0, 400], [0, 400], color=GRID, lw=0.8)
    ax.plot([0, 175 / 3], [70, 70], **kw); ax.plot([175 / 3, 400 / 1.2], [70, 400], **kw)
    ax.plot([70, 70], [84, 400], **kw); ax.plot([0, 70], [180, 180], **kw)
    ax.plot([70, 290], [180, 400], **kw); ax.plot([70, 70], [0, 56], **kw)
    ax.plot([70, 400], [56, 320], **kw); ax.plot([180, 180], [0, 70], **kw)
    ax.plot([180, 400], [70, 70], **kw); ax.plot([240, 240], [70, 180], **kw)
    ax.plot([240, 400], [180, 180], **kw); ax.plot([130, 180], [0, 70], **kw)
    for label, (x, y) in {"A": (30, 15), "B": (370, 260), "B ": (280, 370), "C": (160, 370),
                          "C ": (160, 15), "D": (30, 140), "D ": (370, 120), "E": (30, 370),
                          "E ": (370, 15)}.items():
        ax.text(x, y, label.strip(), fontsize=10, color=INK_2, ha="center", va="center")


def plot_by_hour(by_hour, metric, models, path):
    """One score across the 24 hours of the day, one line per model."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    series = {}
    for m in models:
        s = by_hour.loc[m][metric]
        ax.plot(s.index, s.values, color=MODEL_COLORS[m], lw=2, marker="o", ms=4)
        series[m] = s
    _label_line_ends(ax, 23, series)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlim(-0.5, 25.5)
    ax.set_xlabel("hour of day (of the forecast target; check the date shift kept real clock time)")
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} by hour of day")
    ax.legend([plt.Line2D([], [], color=MODEL_COLORS[m], lw=2) for m in models], models,
              loc="upper left", bbox_to_anchor=(0, -0.15), ncol=len(models), frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
