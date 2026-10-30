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

## The computers

- **Your laptop** is where you work: reading, talking with Claude, your notebook and
  decisions. Everything saves to GitHub, so nothing is lost and Dad can see what you need.
- **The GPU computer (`builder3`)** is at home and does the heavy calculations. It has no
  screen. Your laptop reaches it through a private family network (ZeroTier) once Dad
  approves your laptop. `/connect-gpu` sets that up, and after that Claude runs GPU jobs
  there for you.
- **The software is Claude's job (and Dad's)**, not yours. If something needs building or
  fixing, Claude handles it or asks Dad through a GitHub issue.
- **3D proteins:** install [UCSF ChimeraX](https://www.cgl.ucsf.edu/chimerax/) on your
  laptop, then type `open 1v4s` to see glucokinase.
