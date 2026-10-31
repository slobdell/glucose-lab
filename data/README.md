# Data

**Where the data is:** only on the GPU server `builder3`, in
`~/projects/glucose-lab/data/`. A clone on the laptop has an empty `data/`; work with the
data by running code on builder3 over SSH, and copy back only small results (tables,
figures). Don't copy datasets to the laptop.

Downloaded datasets live here and are **not committed** (see `.gitignore`). Each one is
fetched by a script in `scripts/` so it can be re-downloaded on a fresh machine.

```bash
python scripts/fetch_data.py --list       # what's available and what's downloaded
python scripts/fetch_data.py shanghai     # download into data/shanghai/
python scripts/fetch_data.py metabonet    # manual download (website login); this verifies it
```

Each download writes `data/<name>/MANIFEST.json` with its source, version, license and date.

Record every dataset before using it:

| Dataset | Source URL | Version / date downloaded | License or access terms | Script |
| --- | --- | --- | --- | --- |
| ShanghaiT1DM / ShanghaiT2DM | [figshare](https://doi.org/10.6084/m9.figshare.21600933.v5); paper: [Zhao et al., *Sci Data* 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9849330/) | figshare v5 (2023-10-30); first downloaded 2026-10-30 | CC BY 4.0 (cite the paper) | `fetch_data.py shanghai` |
| MetaboNet public tier (`metabonet_public.parquet`, 1.5 GB) | [metabo-net.org](https://metabo-net.org/) (login required); paper: [Wolff et al., *J Diabetes Sci Technol* 2026](https://doi.org/10.1177/19322968261441637) | Full public file, downloaded 2026-10-30 (md5 in `fetch_data.py`) | Replica Health/JAEB public research terms: non-commercial research and education; anyone else using it must first agree to the same terms. Source licenses vary (mostly CC BY 4.0; HUPA-UCM is CC BY-NC-SA 2.5 AR); attribution is listed on the site | `fetch_data.py metabonet` (manual) |

Note: Shanghai CGM readings are every **15 minutes** (most CGM datasets are every 5).

### MetaboNet: what's in the file (checked 2026-10-30)

- **1,912 people, about 1,245 years of CGM** from 15 studies, on a 5-minute grid
  (155M rows). Most of it is the Loop study (845 people, about 805 years).
- **`id` repeats across studies.** A person is `source_file` + `id`; the loader adds a
  `person` column for this.
- **About 15% of CGM values are blank** (gaps stay blank; nothing is filled in).
- **Dates are shifted** for privacy (some are in 2027). Time of day is presumably real,
  but check before relying on it.
- **The built-in train/test split (`is_test`) is not purely "new people".** 182 people
  are entirely in test (unseen), but another 169 have earlier weeks in train and later
  weeks in test (`subject_split_across_traintest`). Results on `is_test` mix "new
  people" with "same people, later". Choosing a split is an analysis decision.
- Shanghai T1DM is included, resampled from 15 to 5 minutes.
- Loading everything takes more memory than builder3 has free; load selected columns
  or studies (`glucose_lab.datasets.load_metabonet`).

## Restricted datasets (data-use agreement)

These can't be fetched by script. After approval, download them by hand into
`data/<name>/` on builder3 only, and never commit or copy them elsewhere.

| Dataset | Where to request | Status |
| --- | --- | --- |
| DiaTrend (54 type 1 patients) | [Synapse syn38187184](https://doi.org/10.7303/syn38187184) | Not requested |
| T1DEXI (about 495 type 1 patients) | [Vivli](https://vivli.org/), study ID T1-DEXI | Not requested |
