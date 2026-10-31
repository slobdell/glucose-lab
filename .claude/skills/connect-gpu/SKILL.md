---
name: connect-gpu
description: Connect the student's Mac laptop to the family GPU server (builder3) over ZeroTier and SSH, or check whether that connection works. Use when she types /connect-gpu, asks about getting on the GPU, or a GPU job is waiting and you're on her laptop.
---

Get her Mac talking to `builder3`. This is plumbing, so handle it quietly. Tell her only
what she has to do herself (type her Mac password, sign in somewhere, wait for her dad)
and where things stand. Run each check below, skip any step that's already done, and stop
at the first step that needs someone else.

Network facts: ZeroTier network `f3797ba7a8546f34`; `builder3` is `10.115.229.246` on it;
the SSH user is `devia`.

1. **ZeroTier installed?** Check for `/usr/local/bin/zerotier-cli`. If it's missing, she
   runs this herself in the Terminal app, because it asks for her Mac password, which you
   can't type for her:

   ```bash
   curl -fsSLO https://raw.githubusercontent.com/slobdell/machine_bootstrap/main/setup_mac.sh && bash setup_mac.sh
   ```

   It installs ZeroTier, the GitHub CLI and Claude (skipping what's already there), and
   joins the network.

2. **Approved on the network?** Run `zerotier-cli listnetworks`. If that fails with a
   permissions error, ask her to run `sudo zerotier-cli listnetworks` in Terminal and paste
   the output. Find the line for `f3797ba7a8546f34`:
   - **Not listed:** she runs `sudo zerotier-cli join f3797ba7a8546f34` in Terminal.
   - **`ACCESS_DENIED` or `REQUESTING_CONFIGURATION`:** her dad has to approve this laptop.
     Get the 10-character node ID from `zerotier-cli info` (third field). Unless an open
     issue already asks, run `gh issue create --label access --title "Approve laptop on
     ZeroTier" --body "Node ID: <id>"`. Tell her it's waiting on her dad, and that
     everything else in the project works in the meantime. Stop here.
   - **`OK`:** continue.

3. **Can it reach builder3?** `ping -c 3 10.115.229.246`. Right after approval it can take
   a minute or two to connect, so retry once before reporting a problem.

4. **SSH key and shortcut.** If `~/.ssh/id_ed25519` doesn't exist, create it with
   `ssh-keygen -t ed25519 -N "" -C "glucose-lab laptop" -f ~/.ssh/id_ed25519`. If
   `~/.ssh/config` has no `Host builder3` entry, append:

   ```
   Host builder3
       HostName 10.115.229.246
       User devia
       ServerAliveInterval 30
   ```

5. **Key accepted?** Run `ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new builder3 true`.
   If it's refused, her dad needs to add her key. A public key is safe to share, so unless
   an open issue already has it, run `gh issue create --label access --title "Add laptop SSH
   key for builder3" --body "<contents of ~/.ssh/id_ed25519.pub>"`. Tell her it's waiting on
   her dad. Stop here.

6. **GPU check.** Run `ssh builder3 'cd ~/projects/glucose-lab && git pull -q && scripts/run-smoke-test.sh'`.
   It prints a log path; wait about 30 seconds, then `ssh builder3 'tail -12 ~/projects/glucose-lab/<log>'`
   until it ends in `SMOKE TEST PASSED` or `FAILED`. It simulates a virtual patient and trains
   tiny models on the GPU, so a pass means the whole Project B stack works. Tell her the GPU
   is ready. Its error numbers are on synthetic data, not results; don't present them as
   findings. On a failure you can't fix quickly, open a `tooling` issue with the log.

## Running GPU work once connected

Keep her working on the laptop and drive the server over SSH:

- Push from the laptop, then `ssh builder3 'cd ~/projects/glucose-lab && git pull'`.
- Start jobs in a named `screen` session on the server, logging to `logs/`. Use
  `~/miniforge3/envs/research/bin/python` (or the project env once one exists), since
  non-interactive SSH doesn't load conda.
- Copy back only the small results she needs (tables, figures) with `scp`. Large data
  stays on the server.
- For JupyterLab: start it with `ssh builder3 '~/.local/bin/research-jupyter'`. Then she
  runs `ssh -N -L 8888:localhost:8888 builder3` in Terminal and opens the printed URL.
