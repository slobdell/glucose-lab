# Data

Downloaded datasets live here and are **not committed** (see `.gitignore`). Each one is
fetched by a script in `scripts/` so it can be re-downloaded on a fresh machine.

```bash
python scripts/fetch_data.py --list       # what's available and what's downloaded
python scripts/fetch_data.py shanghai     # download into data/shanghai/
```

Each download writes `data/<name>/MANIFEST.json` with its source, version, license and date.

Record every dataset before using it:

| Dataset | Source URL | Version / date downloaded | License or access terms | Script |
| --- | --- | --- | --- | --- |
| ShanghaiT1DM / ShanghaiT2DM | [figshare](https://doi.org/10.6084/m9.figshare.21600933.v5); paper: [Zhao et al., *Sci Data* 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9849330/) | figshare v5 (2023-10-30); first downloaded 2026-10-30 | CC BY 4.0 (cite the paper) | `fetch_data.py shanghai` |

Note: Shanghai CGM readings are every **15 minutes** (most CGM datasets are every 5).

## Restricted datasets (data-use agreement)

These can't be fetched by script. After approval, download them by hand into
`data/<name>/` on builder3 only, and never commit or copy them elsewhere.

| Dataset | Where to request | Status |
| --- | --- | --- |
| DiaTrend (54 type 1 patients) | [Synapse syn38187184](https://doi.org/10.7303/syn38187184) | Not requested |
| T1DEXI (about 495 type 1 patients) | [Vivli](https://vivli.org/), study ID T1-DEXI | Not requested |
