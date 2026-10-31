"""Download a dataset into data/<name>/ (gitignored), verify its checksum, and unpack it.

Usage:
    python scripts/fetch_data.py --list
    python scripts/fetch_data.py shanghai          # skips if already downloaded
    python scripts/fetch_data.py shanghai --force  # re-download

Only open-access datasets belong in DATASETS. Restricted ones (DiaTrend, T1DEXI) are
downloaded by hand after the data-use agreement is approved; see data/README.md.
"""

import argparse
import hashlib
import json
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

DATASETS = {
    "shanghai": {
        "description": "ShanghaiT1DM (12 patients) and ShanghaiT2DM (100 patients), CGM every 15 min",
        "url": "https://ndownloader.figshare.com/files/42966622",
        "filename": "diabetes_datasets.zip",
        "md5": "4bfb61cfa506b48155fd9e841ee48e21",
        "source": "https://doi.org/10.6084/m9.figshare.21600933.v5",
        "version": "figshare v5 (2023-10-30)",
        "license": "CC BY 4.0",
        "cite": "Zhao Q et al., Scientific Data 2023, https://pmc.ncbi.nlm.nih.gov/articles/PMC9849330/",
    },
}


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(name, force=False):
    spec = DATASETS[name]
    dest = DATA / name
    manifest = dest / "MANIFEST.json"
    if manifest.exists() and not force:
        print(f"{name}: already in {dest} (use --force to re-download)")
        return dest

    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / spec["filename"]
    print(f"{name}: downloading {spec['url']}")
    urllib.request.urlretrieve(spec["url"], archive)
    got = md5(archive)
    if got != spec["md5"]:
        archive.unlink()
        sys.exit(f"{name}: checksum mismatch (got {got}, expected {spec['md5']}); the source may have changed")

    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            members = [m for m in z.namelist() if "__MACOSX" not in m and not m.endswith(".DS_Store")]
            for member in members:  # refuse paths that would escape dest
                if not (dest / member).resolve().is_relative_to(dest.resolve()):
                    sys.exit(f"{name}: unsafe path in archive: {member}")
            z.extractall(dest, members)

    manifest.write_text(json.dumps({**spec, "downloaded": date.today().isoformat()}, indent=2))
    print(f"{name}: ready in {dest}")
    return dest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("names", nargs="*", help="datasets to fetch")
    p.add_argument("--list", action="store_true", help="list available datasets")
    p.add_argument("--force", action="store_true", help="re-download even if present")
    args = p.parse_args()

    if args.list or not args.names:
        for k, v in DATASETS.items():
            status = "downloaded" if (DATA / k / "MANIFEST.json").exists() else "not downloaded"
            print(f"{k:12s} {status:15s} {v['license']:10s} {v['description']}")
        sys.exit(0)
    unknown = set(args.names) - DATASETS.keys()
    if unknown:
        sys.exit(f"unknown dataset(s): {', '.join(sorted(unknown))}; try --list")
    for n in args.names:
        fetch(n, args.force)
