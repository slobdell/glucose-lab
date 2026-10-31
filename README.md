# glucose-lab

A student research project on diabetes, run on a home GPU with Claude as a lab partner.

The student is the scientist: she picks the question, decides what counts as a result,
and writes every word of the paper. Claude writes and runs code, finds sources, and
explains the science.

## Getting started on a Mac

You don't need the GPU to start. Reading, exploring, and choosing a project all work on
your laptop.

1. **Install the tools.** In the Terminal app, run this. It asks for your Mac password,
   and installs Claude, the GitHub CLI and ZeroTier (the family network the GPU is on):

   ```bash
   curl -fsSLO https://raw.githubusercontent.com/slobdell/machine_bootstrap/main/setup_mac.sh && bash setup_mac.sh
   ```

2. **Sign in to GitHub** in the browser window this opens:

   ```bash
   gh auth login --web --git-protocol https && gh auth setup-git
   ```

3. **Download the project.** If your Mac offers to install developer tools, say yes and
   run the command again.

   ```bash
   git clone https://github.com/slobdell/glucose-lab.git ~/glucose-lab
   ```

4. **Start Claude.** Open a new Terminal window and run:

   ```bash
   cd ~/glucose-lab && claude
   ```

   Sign in, then type `/orient`. Claude walks you through the two candidate projects and
   helps you choose. It won't choose for you.

When you want the GPU, type `/connect-gpu`. Claude checks your network approval and SSH
access, and asks Dad for anything still missing. Until then, keep working on everything else.

## Candidate projects

| Project | Question |
| --- | --- |
| [A: MODY variant detective](materials/project-a-mody.md) | Can AI mutation predictors tell broken diabetes-gene variants from overactive ones? Which unexplained variants in patients are most likely to matter? |
| [B: Glucose forecast audit](materials/project-b-glucose.md) | Do AI models that warn of low blood sugar beat simple rules, and do they work on people they've never seen? |

Datasets and papers for both: [`materials/sources.md`](materials/sources.md).

## Layout

| Path | What goes there |
| --- | --- |
| `DECISIONS.md` | Decision log: project choice, question, hypothesis, and why |
| `materials/` | Background reading: the projects, sources, ground rules, how the machine works |
| `notebook/` | The lab notebook: one entry per work session, written by the student |
| `data/` | Downloaded datasets (not committed; `scripts/` re-downloads them) |
| `scripts/` | Download, processing and GPU job scripts |
| `notebooks/` | Jupyter notebooks for exploring data and making figures |
| `src/glucose_lab/` | Reusable Python code, importable from notebooks and scripts |

## GPU server setup (for maintainers)

GPU work runs on a Linux machine prepared by
[machine_bootstrap](https://github.com/slobdell/machine_bootstrap), which provides
the shared `research` conda env (PyTorch + JupyterLab):

```bash
conda activate research
pip install -e .          # makes `import glucose_lab` work
research-gpu-check        # confirms the GPU works
mamba env update -n research -f environment.yml  # Project B packages
scripts/run-smoke-test.sh # end-to-end check: simulator + LSTM + XGBoost on GPU
research-jupyter          # starts JupyterLab in a screen session
```

Project-specific tools get added once a project is chosen. Requests from the student
arrive as GitHub issues: `tooling` for software, `access` for ZeroTier approval and SSH keys.

Nothing in this repo is medical advice, and nothing here is used to diagnose anyone or
dose insulin.
