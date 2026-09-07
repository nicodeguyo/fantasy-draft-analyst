# Make your draft plan

**Version 3.0.0:** replace your installed ZIP and regenerate your plan. The new default policy values roster coverage, so results intentionally differ from v2. Keep league files outside the installed skill. Local live advice requires Python on your computer; a downloaded static board or hosted chat artifact cannot run its local server.

First, [explore the sample demo](https://nicodeguyo.github.io/fantasy-draft-analyst/). No account or installation is needed to try it. Your own plan requires an assistant that can read the instructions, research public data, and run the bundled Python scripts.

## Claude in your browser (recommended)

You do not need to install Python or use a terminal for this route. A *skill* is the downloadable package of instructions and scripts you give Claude.

**Prerequisites, checked September 5, 2026:** Anthropic lists custom skills for Free, Pro, Max, Team, and Enterprise. Code execution must be enabled; organization settings may restrict uploads. Your account's usage limits still apply. [Anthropic's setup requirements](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

1. [Download fantasy-draft-analyst.zip](https://github.com/nicodeguyo/fantasy-draft-analyst/raw/refs/heads/main/dist/fantasy-draft-analyst.zip). Keep it zipped.
2. In Claude, enable **Settings → Capabilities → Code execution and file creation**. For a work account, check your organization's Skills settings if this is unavailable.
3. Open **Customize → Skills → + → Create skill → Upload a skill**, choose the ZIP, and enable it. [Official upload instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
4. Start a new chat. Paste the [league-description prompt](../README.md#setup) with your settings and ask Claude to use the fantasy draft analyst skill. Enable web search for fresh sources when available.
5. Check the settings Claude gathers. Then have it run the simulator, explain the recommendations, and create a downloadable HTML board.
6. Download and open the HTML file in your browser. Try crossing off a player and marking your pick before draft night. Open that same file in the same browser to continue tracking.

**What success looks like:** a written analysis, dated sources, and an HTML board tailored to your rules. A chat answer alone is not the completed board. If Claude cannot run code or access a necessary source, ask it to explain the missing step instead of treating an approximation as a simulation.

The board stores your marks locally when your browser allows storage. It does not sync across devices, connect to your fantasy platform, or recalculate advice as you mark picks. Check that persistence works in your browser before relying on it.

### If you get stuck

- **Upload missing or disabled:** check code execution and your organization's skill permissions. Use Anthropic's linked troubleshooting guide for account-specific restrictions.
- **ZIP rejected:** use the packaged download without unzipping it. It contains one `fantasy-draft-analyst/` folder, including `SKILL.md` and the scripts. [Required package structure](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).
- **Claude replies without running the simulation:** ask, “Use the installed skill, run its simulator, and create the downloadable HTML board. Tell me what is blocking you if you cannot.”
- **Current data is unavailable:** provide a public source or a sanitized export of player data. Do not reuse the sample league's old data as if it were current.
- **No code execution available:** use the [paste-anywhere prompt](../prompt/fantasy-draft-analyst-prompt.md). It offers an analytical approximation; it does not run the full simulator.

## Claude Code

Requires Claude Code, Git, Python 3.10+, and PyYAML in the Python environment used to run the scripts.

```bash
git clone https://github.com/nicodeguyo/fantasy-draft-analyst.git
cd fantasy-draft-analyst
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyyaml
mkdir -p ~/.claude/skills
cp -r skills/fantasy-draft-analyst ~/.claude/skills/
```

Start Claude Code with that environment active. Invoke `/fantasy-draft-analyst` and paste the [league description](../README.md#setup). For a project-only install, copy the skill folder into `.claude/skills/` inside that project instead.

Alternatively, install this repository's plugin from Claude Code:

```text
/plugin marketplace add nicodeguyo/fantasy-draft-analyst
/plugin install fantasy-draft-analyst@fantasy-draft-analyst
```

The plugin still needs a Python environment with PyYAML to run its scripts.

## Codex or another coding assistant

Clone the repository and create the Python environment using the commands above, stopping before the `mkdir` and `cp` commands. Then ask your assistant:

```text
Read skills/fantasy-draft-analyst/SKILL.md and follow it for my league.
Use the repository's .venv Python environment to run the scripts.
Ask about missing rules before simulating. Here are my settings:
[paste the league description from the README]
```

The assistant needs permission to read the repository, execute Python, and research current public sources. No connection to your private fantasy account is required.

## Any assistant without code execution

Open the [paste-anywhere prompt](../prompt/fantasy-draft-analyst-prompt.md), fill in its league block, and paste the whole thing. Enable browsing if available; otherwise supply current public player data and news yourself.

This route uses a one-pick-ahead analytical approximation. It is useful for discussing a decision, but its results are not the full rollout simulation used in the sample benchmark. Do not expect the generated HTML board from this route.

## Running the scripts yourself

Requires Python 3.10+ and PyYAML. From a cloned repository, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyyaml
```

On Windows, use `.venv\Scripts\Activate.ps1` in PowerShell for activation. Use `python` in place of `python3` to create the environment if that is your Python 3 command.

Regenerate the example into a separate output folder:

```bash
mkdir -p output
python skills/fantasy-draft-analyst/scripts/draft_sim.py \
  --league examples/sample-league/league.yaml \
  --players examples/sample-league/players.csv \
  --sims 1500 --pick-values --keeper-scenarios \
  --out output/sim.json
python skills/fantasy-draft-analyst/scripts/build_board.py \
  --league examples/sample-league/league.yaml \
  --sim output/sim.json \
  --notes examples/sample-league/notes.json \
  --players examples/sample-league/players.csv \
  --out output/draft-board.html
```

These multi-line commands use macOS/Linux shell syntax. In PowerShell, put each command on one line without the trailing backslashes. Open `output/draft-board.html` in a browser to inspect the result.

Keeper scenarios run before the board and choose among up to four surplus-shortlisted candidates plus nobody. Use `--keeper "Player Name"` or `--no-keeper` for an explicit decision. The simulator supports zero or one keeper per team. A published keeper list needs each player’s original draft slot and round cost; omitted opponents keep nobody. An empty list means unknown keepers and uses modeled draws.

The simulator prints a summary and writes the JSON results plus an availability CSV. Budget several minutes depending on your hardware; `--rollouts 60` is quicker but less precise, and `--no-pick-values` skips the full candidate comparisons. The sample uses saved inputs so you can reproduce it. For a real league, update the settings and fetch fresh data first.

To reproduce the README's policy comparison using the committed sample output:

```bash
python scripts/compare_policies.py \
  --league examples/sample-league/league.yaml \
  --players examples/sample-league/players.csv \
  --sim examples/sample-league/sim.json \
  --drafts 800
```

The scripts in `skills/fantasy-draft-analyst/scripts/` include ADP fetching, projection scoring, and ADP merging. Read the [method explanation](how-it-works.md) and [sample run log](../examples/sample-league/RUNLOG.md) before interpreting the output.

## Updating

Re-download and upload the packaged ZIP, or pull the repository and re-copy the installed skill folder. Keep your league files outside the skill folder so replacing it does not replace your inputs. Regenerate your board when you want updated data; downloading a new skill does not refresh an existing board.

## New v3 data and live workflow

Inside the installed `fantasy-draft-analyst` directory:

```bash
python scripts/prepare_data.py --league league.yaml --snapshot evidence.json --out players.csv
python scripts/draft_sim.py --league league.yaml --players players.csv --sims 100 --rollouts 20 --pick-values --out sim.json
python scripts/build_board.py --league league.yaml --players players.csv --sim sim.json --notes notes.json --out draft-board.html
python scripts/live_draft.py --session session.json init --league league.yaml --players players.csv
python scripts/live_draft.py --session session.json serve --port 8768
```

Create `notes.json` from the output reference (an empty `{}` is valid for a minimal board). These are initial exploration settings, not a precision guarantee. Increase simulations after checking the data and runtime. Read [evidence](../skills/fantasy-draft-analyst/references/evidence.md) for current provider options and [live sessions](../skills/fantasy-draft-analyst/references/live-draft.md) for pick imports, undo, refresh and receipts. `--help` documents every executable option. Carry `players.evidence.json` with the CSV so live advice retains provenance.
