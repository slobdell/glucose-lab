"""End-to-end plumbing check for the Project B (glucose forecasting) stack on builder3.

Simulates one virtual type 1 patient with simglucose, then trains a tiny LSTM (PyTorch,
GPU) and a gradient-boosted tree (XGBoost, GPU) to forecast 30 minutes ahead. Uses
synthetic data only. The error numbers are printed to show the pipeline runs; they are
not results.

Usage: python scripts/gpu_smoke_test.py   (or scripts/run-smoke-test.sh for screen + log)
"""

import sys
import tempfile
import time
import traceback
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
HISTORY, HORIZON = 24, 6  # 5-minute steps: 2 h of history, forecast 30 min ahead
results = []


def check(name):
    def wrap(fn):
        def run(*args):
            start = time.time()
            try:
                out = fn(*args)
                results.append((name, True, f"{time.time() - start:.1f}s"))
                return out
            except Exception as e:
                traceback.print_exc()
                results.append((name, False, f"{type(e).__name__}: {e}"))
                return None
        return run
    return wrap


@check("GPU visible to PyTorch")
def gpu():
    import torch

    assert torch.cuda.is_available(), "PyTorch cannot see the GPU"
    free, total = torch.cuda.mem_get_info()
    print(f"torch {torch.__version__} (CUDA {torch.version.cuda}), "
          f"{torch.cuda.get_device_name(0)}: {free / 2**30:.1f} of {total / 2**30:.1f} GiB free")
    if free / total < 0.5:
        print("WARNING: someone else is using more than half the GPU memory (check nvidia-smi)")


@check("simglucose simulates a patient")
def simulate(days=2):
    from simglucose.actuator.pump import InsulinPump
    from simglucose.controller.basal_bolus_ctrller import BBController
    from simglucose.patient.t1dpatient import T1DPatient
    from simglucose.sensor.cgm import CGMSensor
    from simglucose.simulation.env import T1DSimEnv
    from simglucose.simulation.scenario import CustomScenario
    from simglucose.simulation.sim_engine import SimObj, sim

    start = datetime(2026, 1, 1)
    meals = [(h + 24 * d, g) for d in range(days) for h, g in [(7, 45), (12, 70), (18, 80)]]
    env = T1DSimEnv(
        T1DPatient.withName("adolescent#001"),
        CGMSensor.withName("GuardianRT", seed=1),  # 5-min readings; "Dexcom" here is 3-min
        InsulinPump.withName("Insulet"),
        CustomScenario(start_time=start, scenario=meals),
    )
    with tempfile.TemporaryDirectory() as d:
        df = sim(SimObj(env, BBController(), timedelta(days=days), animate=False, path=d))
    steps = df.index.to_series().diff().dropna().unique()
    assert len(steps) == 1 and steps[0] == np.timedelta64(5, "m"), f"CGM not every 5 min: {steps}"
    cgm = df["CGM"].dropna().to_numpy(dtype=np.float32)
    print(f"{len(cgm)} CGM readings, range {cgm.min():.0f}-{cgm.max():.0f} mg/dL")
    assert len(cgm) > 200 and 20 < cgm.mean() < 400
    return cgm


def windows(cgm):
    n = len(cgm) - HISTORY - HORIZON + 1
    X = np.stack([cgm[i:i + HISTORY] for i in range(n)])
    y = cgm[HISTORY + HORIZON - 1:]
    split = int(0.75 * n)  # earlier hours train, later hours test
    return X[:split], y[:split], X[split:], y[split:]


def rmse(pred, y):
    return float(np.sqrt(np.mean((pred - y) ** 2)))


@check("LSTM trains on GPU")
def lstm(data):
    import torch
    from torch import nn

    Xtr, ytr, Xte, yte = data
    dev = torch.device("cuda")
    mu, sd = Xtr.mean(), Xtr.std()
    t = lambda a: torch.tensor((a - mu) / sd, device=dev)

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(1, 32, batch_first=True)
            self.head = nn.Linear(32, 1)

        def forward(self, x):
            return self.head(self.lstm(x.unsqueeze(-1))[0][:, -1]).squeeze(-1)

    torch.manual_seed(0)
    net = Net().to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-2)
    losses = []
    for _ in range(200):
        opt.zero_grad()
        loss = nn.functional.mse_loss(net(t(Xtr)), t(ytr))
        loss.backward()
        opt.step()
        losses.append(loss.item())
    assert losses[-1] < 0.5 * losses[0], f"loss barely moved: {losses[0]:.3f} -> {losses[-1]:.3f}"

    ckpt = ROOT / "outputs" / "smoke_test_lstm.pt"
    ckpt.parent.mkdir(exist_ok=True)
    torch.save(net.state_dict(), ckpt)
    net.load_state_dict(torch.load(ckpt, map_location=dev))
    with torch.no_grad():
        pred = net(t(Xte)).cpu().numpy() * sd + mu
    print(f"training loss {losses[0]:.3f} -> {losses[-1]:.3f}; checkpoint saved and reloaded")
    return rmse(pred, yte)


@check("XGBoost trains on GPU")
def xgb(data):
    import xgboost

    Xtr, ytr, Xte, yte = data
    model = xgboost.XGBRegressor(n_estimators=200, max_depth=4, device="cuda", verbosity=0)
    model.fit(Xtr, ytr)
    assert model.get_booster().attributes() is not None
    print(f"xgboost {xgboost.__version__}")
    return rmse(model.predict(Xte), yte)


if __name__ == "__main__":
    print(f"=== glucose-lab GPU smoke test, {datetime.now():%Y-%m-%d %H:%M} ===\n")
    gpu()
    cgm = simulate()
    if cgm is not None:
        data = windows(cgm)
        scores = {"Persistence (no model)": rmse(data[2][:, -1], data[3]),
                  "LSTM": lstm(data), "XGBoost": xgb(data)}
        print("\n30-min-ahead RMSE on synthetic data (plumbing check, NOT a result):")
        for k, v in scores.items():
            print(f"  {k:24s} {'failed' if v is None else f'{v:.1f} mg/dL'}")

    print()
    for name, ok, info in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  ({info})")
    passed = all(ok for _, ok, _ in results) and len(results) == 4
    print("\nSMOKE TEST PASSED" if passed else "\nSMOKE TEST FAILED")
    sys.exit(0 if passed else 1)
