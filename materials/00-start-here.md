# Start here

This is a real research project on diabetes. The goal is a result good enough to publish
in a student journal like the
[Journal of Emerging Investigators](https://emerginginvestigators.org/) or to enter at a
science fair (Regeneron ISEF, Computational Biology and Bioinformatics).

## You're the scientist; Claude is the lab tech

You might worry that using AI is cheating. If AI did your thinking or writing, it would be.
Here it's closer to a microscope: an instrument that lets you look at things too big or
too complex to check by hand, like 10,000 mutations at once or a year of glucose readings.

| You own | Claude helps with |
| --- | --- |
| The research question and hypothesis | Finding datasets, papers and tools, with links |
| Deciding what counts as a result *before* seeing the data | Writing, running and debugging code on the GPU |
| Understanding every analysis well enough to explain it aloud | Explaining code, biology and statistics |
| Every sentence of the paper and poster | Pointing out weak spots in your reasoning, without rewriting your words |
| Checking Claude's work | Saying when it's unsure and suggesting tests |

Claude can be wrong: it can misremember a number, invent a paper or write buggy code. So
open every citation, and check every important result with a simple test. Your lab
notebook (`notebook/`) is the record of what you did and concluded. It's also your proof
the work is yours, and it becomes the paper's Methods section. Journals and fairs ask how
AI was used, so at the end you'll write a short, honest disclosure.

## Two candidate projects

**[Project A: MODY variant detective](project-a-mody.md).** Some diabetes comes from a typo
in a single gene (MODY). Labs have measured what nearly every possible mutation does to two
of these genes. You grade AI mutation predictors against those answer keys, find where they
fail, and then use the best one on a gene with no answer key yet. It's heavy on biology:
proteins, enzymes and genetics.

**[Project B: Glucose forecast audit](project-b-glucose.md).** AI models claim to warn people
with type 1 diabetes before their blood sugar crashes. You test whether they beat simple
rules, and whether they work on people they never trained on. It's heavier on data and
physiology: insulin, food, exercise and sleep.

Both run on the home GPU, use real public data, and could produce a publishable result.
They're different kinds of work, and the right one is the one you'd want to think about
on a Saturday.

## How the machine works

- The GPU computer has no screen. You reach it over SSH from your laptop.
- `screen -S work` starts a session that keeps running if your connection drops.
  `screen -r work` reattaches to it.
- `research-jupyter` starts JupyterLab. To open it in your laptop's browser, run
  `ssh -L 8888:localhost:8888 <machine>` on your laptop, then open the URL it prints.
- 3D protein viewing happens on your laptop in [UCSF ChimeraX](https://www.cgl.ucsf.edu/chimerax/),
  or inside Jupyter.
- `nvidia-smi` shows what the GPU is doing.
