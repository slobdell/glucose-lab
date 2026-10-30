# Sources

Collected 2026-10-29 by web search. The full papers haven't been read yet, so check any
number against the paper itself before using it.

## Project A: MODY variant detective

### Answer keys (lab-measured mutation maps)

| Source | What it holds | Why it matters |
| --- | --- | --- |
| [A comprehensive map of human glucokinase variant activity](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10131484/) (Gersing et al., *Genome Biology* 2023) | Activity of about 97% of possible GCK missense and nonsense variants (yeast assay) | Scores track fasting glucose in carriers; finds hyperactive variants that conservation misses |
| [Characterizing glucokinase variant mechanisms using a multiplexed abundance assay](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11021015/) (Gersing et al., *Genome Biology* 2024) | Protein abundance (stability) of GCK variants | Separates "falls apart" from "stable but broken" |
| [Human gain-of-function variants in HNF1A confer protection from diabetes](https://www.cell.com/cell-genomics/fulltext/S2666-979X(23)00114-3) (DeForest et al., *Cell Genomics* 2023) | Transcriptional activity of 11,970 HNF1A variants in liver cells | About 1 in 5 rare population variants are gain-of-function |

### Background and rules

| Source | Use |
| --- | --- |
| [Unsupervised clustering of HNF1A missense variants using functional data](https://www.medrxiv.org/content/10.1101/19010900.full.pdf) (Althari et al., *AJHG* 2020) | 73 HNF1A variants, 4 assays; functional data reclassifying real MODY registry variants |
| [Systematic analysis of loss-of-function variants across MODY genes](https://link.springer.com/article/10.1007/s00125-026-06685-7) (*Diabetologia* 2026) | Loss-of-function variants in KCNJ11 and ABCC8 don't cause MODY, so those genes are out |
| [ClinGen Monogenic Diabetes Expert Panel: example HNF4A classification](https://erepo.clinicalgenome.org/evrepo/ui/classification/d54666ed-6c16-4627-866b-06dd61166fee) | Gene-specific clinical classification rules, e.g. REVEL ≥ 0.70 as computational evidence |
| [ProteinGym](https://oatml.cs.ox.ac.uk/publications/202312_Notin_ProteinGym.html) (Notin et al., NeurIPS 2023) | Standard benchmark: 70+ predictors on 250+ lab maps; a template for grading predictors |
| [MaveDB 2024](https://pubmed.ncbi.nlm.nih.gov/39838450/) (*Genome Biology* 2025) | Archive where lab mutation-map score files are downloaded |
| [Mapping the GCK–GKRP interaction landscape](https://www.biorxiv.org/content/10.64898/2026.01.15.699699.full.pdf) (bioRxiv 2026, not peer-reviewed) | 7,534 GCK substitutions scored for binding its regulator GKRP; a possible extra answer key |

**Standard databases and tools:** ClinVar, gnomAD, AlphaFold DB, AlphaMissense
precomputed scores, ESM-1v and ESM-2.

## Project B: Glucose forecast audit

| Source | Access | What it holds |
| --- | --- | --- |
| [Shanghai T1DM / T2DM datasets](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9849330/) | Open download | 12 type 1 patients for about 2 weeks; 100 type 2 patients |
| [MetaboNet](https://arxiv.org/html/2601.11505v1) (2026) | Public subset open; the rest needs data-use agreements | Many type 1 datasets in one format |
| [DiaTrend](https://ar5iv.labs.arxiv.org/html/2304.06506) | Data-use agreement | 54 type 1 patients, about 27,500 days of CGM |
| [Glucose-ML collection](https://arxiv.org/pdf/2507.14077) | Index of datasets | Access status of many diabetes datasets, including T1DEXI (about 495 type 1 patients) |
| [simglucose](https://pypi.org/project/simglucose) | Open source (MIT) | UVA/Padova type 1 simulator in Python |
| [GlucoBench](https://arxiv.org/html/2410.05780v1) (ICLR 2024) | Paper + code | Standard forecasting benchmark on public CGM datasets |
| [GlucoFM-Bench](https://arxiv.org/abs/2606.06881) (arXiv, June 2026) | Paper | 15 datasets, 1,117 people; a plain LSTM beats foundation models by 4–21% with enough data; all models struggle on type 1 and in low/high ranges |
