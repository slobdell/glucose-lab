# glucose-lab

A student research project on diabetes, run on a home GPU with Claude as a lab partner.

The student is the scientist: she picks the question, decides what counts as a result,
and writes every word of the paper. Claude writes and runs code, finds sources, and
explains the science.

## Start here

1. Read [`materials/00-start-here.md`](materials/00-start-here.md).
2. Open Claude Code in this folder and type `/orient`. Claude walks you through the two
   candidate projects and helps you choose. It won't choose for you.

## Candidate projects

| Project | Question |
| --- | --- |
| [A: MODY variant detective](materials/project-a-mody.md) | Can AI mutation predictors tell broken diabetes-gene variants from overactive ones? Which unexplained variants in patients are most likely to matter? |
| [B: Glucose forecast audit](materials/project-b-glucose.md) | Do AI models that warn of low blood sugar beat simple rules, and do they work on people they've never seen? |

Datasets and papers for both: [`materials/sources.md`](materials/sources.md).

## Layout

| Path | What goes there |
| --- | --- |
| `materials/` | Background reading: the projects, sources, ground rules, how the machine works |
| `notebook/` | The lab notebook: one entry per work session, written by the student |
| `data/` | Downloaded datasets (not committed; `scripts/` re-downloads them) |
| `scripts/` | Download, processing and GPU job scripts |
| `notebooks/` | Jupyter notebooks for exploring data and making figures |
| `src/glucose_lab/` | Reusable Python code, importable from notebooks and scripts |

## Setup

Runs on a Linux GPU machine prepared by
[machine_bootstrap](https://github.com/slobdell/machine_bootstrap), which provides
the shared `research` conda env (PyTorch + JupyterLab):

```bash
conda activate research
pip install -e .          # makes `import glucose_lab` work
research-gpu-check        # confirms the GPU works
research-jupyter          # starts JupyterLab in a screen session
```

Project-specific tools get added once a project is chosen.

Nothing in this repo is medical advice, and nothing here is used to diagnose anyone or
dose insulin.
