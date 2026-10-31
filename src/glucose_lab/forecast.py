"""Glucose forecasting toolkit: windows, splits, baselines, models and scores.

Every scientific choice (history length, horizon, what counts as low, how to split,
what to do with gaps) is a parameter with no hidden default in the analysis itself.
Times are in 5-minute steps unless a name says otherwise.
"""

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view


# ---------- windows ----------

def make_windows(df, history, horizon, stride=1, max_gap_steps=0):
    """Turn per-person CGM series into (past readings -> reading `horizon` steps later).

    df needs columns person, date, CGM on a regular 5-minute grid. A window is kept only
    if its history has at most `max_gap_steps` blank readings and the target isn't blank
    (blanks in kept windows are filled by carrying the last reading forward).
    Returns X (n, history), y (n,), and a table with person, target time and hour.
    """
    Xs, ys, metas = [], [], []
    for person, g in df.sort_values(["person", "date"]).groupby("person", sort=False, observed=True):
        cgm = g["CGM"].to_numpy(dtype=np.float32)
        if len(cgm) < history + horizon:
            continue
        hist = sliding_window_view(cgm[: len(cgm) - horizon], history)[::stride]
        target_idx = np.arange(history - 1 + horizon, len(cgm))[::stride]
        target = cgm[target_idx]
        ok = (np.isnan(hist).sum(1) <= max_gap_steps) & ~np.isnan(target) & ~np.isnan(hist[:, -1])
        if not ok.any():
            continue
        hist = pd.DataFrame(hist[ok]).ffill(axis=1).bfill(axis=1).to_numpy(np.float32)
        Xs.append(hist)
        ys.append(target[ok])
        dates = g["date"].to_numpy()[target_idx[ok]]
        metas.append(pd.DataFrame({"person": person, "time": dates}))
    meta = pd.concat(metas, ignore_index=True)
    meta["hour"] = pd.DatetimeIndex(meta["time"]).hour
    meta["study"] = meta["person"].str.split(":").str[0]
    return np.concatenate(Xs), np.concatenate(ys), meta


# ---------- splits (each returns a boolean "is test" mask over windows) ----------

def split_by_person(meta, test_frac, seed):
    """Hold out a random fraction of people entirely."""
    people = meta["person"].unique()
    rng = np.random.default_rng(seed)
    test = rng.choice(people, size=max(1, int(round(test_frac * len(people)))), replace=False)
    return meta["person"].isin(test).to_numpy()


def split_by_study(meta, test_studies):
    """Hold out whole studies (train on some, test on others)."""
    return meta["study"].isin(test_studies).to_numpy()


def split_by_time(meta, test_frac):
    """Same people in train and test: each person's last fraction of time is test."""
    rank = meta.groupby("person")["time"].rank(pct=True)
    return (rank > 1 - test_frac).to_numpy()


# ---------- baselines and models (each returns predictions for X_test) ----------

def predict_persistence(X_test):
    """'It stays where it is now.'"""
    return X_test[:, -1]


def predict_trend(X_test, horizon, lookback):
    """Extend the straight line through the last `lookback` steps."""
    slope = (X_test[:, -1] - X_test[:, -1 - lookback]) / lookback
    return X_test[:, -1] + slope * horizon


def predict_ridge(X_train, y_train, X_test, alpha):
    from sklearn.linear_model import Ridge

    return Ridge(alpha=alpha).fit(X_train, y_train).predict(X_test)


def predict_xgboost(X_train, y_train, X_test, n_estimators, max_depth, seed):
    import xgboost

    model = xgboost.XGBRegressor(n_estimators=n_estimators, max_depth=max_depth,
                                 learning_rate=0.05, device="cuda", random_state=seed)
    return model.fit(X_train, y_train).predict(X_test)


def predict_lstm(X_train, y_train, X_test, hidden, epochs, batch_size, seed, log=print):
    """Small LSTM on the GPU. Predicts the change from the last reading."""
    import torch
    from torch import nn

    torch.manual_seed(seed)
    dev = torch.device("cuda")
    mu, sd = float(X_train.mean()), float(X_train.std())
    norm = lambda a: torch.tensor((a - mu) / sd, dtype=torch.float32)
    Xtr, Xte = norm(X_train).to(dev), norm(X_test)  # training set lives on the GPU
    ytr = norm(y_train).to(dev) - Xtr[:, -1]

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(1, hidden, num_layers=2, batch_first=True)
            self.head = nn.Linear(hidden, 1)

        def forward(self, x):
            return self.head(self.lstm(x.unsqueeze(-1))[0][:, -1]).squeeze(-1)

    net = Net().to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    n = len(Xtr)
    for epoch in range(epochs):
        perm = torch.randperm(n, device=dev)
        total = 0.0
        for i in range(0, n, batch_size):
            idx = perm[i:i + batch_size]
            xb, yb = Xtr[idx], ytr[idx]
            opt.zero_grad()
            loss = nn.functional.mse_loss(net(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item() * len(idx)
        log(f"  LSTM epoch {epoch + 1}/{epochs}: train loss {total / n:.4f}")
    net.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(Xte), 65536):
            xb = Xte[i:i + 65536].to(dev)
            out.append((net(xb) + xb[:, -1]).cpu())
    return torch.cat(out).numpy() * sd + mu


# ---------- scores ----------

def clarke_zones(ref, pred):
    """Clarke error grid zone (A-E) for each (reference, predicted) pair in mg/dL.

    A: clinically accurate; B: benign error; C: would cause unnecessary treatment;
    D: fails to detect a high or low; E: would treat the opposite way.
    Boundaries follow Clarke et al., Diabetes Care 1987.
    """
    ref, pred = np.asarray(ref, float), np.asarray(pred, float)
    z = np.full(ref.shape, "B", dtype="<U1")
    a = (np.abs(pred - ref) <= 0.2 * ref) | ((ref < 70) & (pred < 70))
    e = ((ref <= 70) & (pred >= 180)) | ((ref >= 180) & (pred <= 70))
    c = ((ref >= 70) & (ref <= 290) & (pred >= ref + 110)) | \
        ((ref >= 130) & (ref <= 180) & (pred <= (7 / 5) * ref - 182))
    d = ((ref >= 240) & (pred >= 70) & (pred <= 180)) | \
        ((ref <= 175 / 3) & (pred <= 180) & (pred >= 70)) | \
        ((ref >= 175 / 3) & (ref <= 70) & (pred >= (6 / 5) * ref))
    z[d] = "D"
    z[c] = "C"
    z[e] = "E"
    z[a] = "A"
    return z


def score(y, pred, low_threshold):
    """Error overall and in the low range, low-alarm detection, and Clarke zones."""
    err = pred - y
    low, alarm = y < low_threshold, pred < low_threshold
    zones = clarke_zones(y, pred)
    out = {
        "n": len(y),
        "RMSE": float(np.sqrt(np.mean(err ** 2))),
        "MAE": float(np.mean(np.abs(err))),
        "RMSE_when_low": float(np.sqrt(np.mean(err[low] ** 2))) if low.any() else np.nan,
        "lows_caught": float((alarm & low).sum() / low.sum()) if low.any() else np.nan,
        "alarms_true": float((alarm & low).sum() / alarm.sum()) if alarm.any() else np.nan,
    }
    for zone in "ABCDE":
        out[f"zone_{zone}"] = float((zones == zone).mean())
    return out
