# Choose your draft setup

**Version 3.0.0:** replace your installed ZIP and regenerate your plan. The new default policy values roster coverage, so results intentionally differ from v2. Keep league files outside the installed skill. Local live advice requires Python on your computer; a downloaded static board or hosted chat artifact cannot run its local server.

First, [explore the saved v3 demo](https://nicodeguyo.github.io/fantasy-draft-analyst/). No account or installation is needed to inspect it. It switches between saved engine outputs; it does not run a personal draft. Your own plan requires an assistant that can read the instructions, research public data, and run the bundled Python scripts.

| Goal | Route | What you need |
|---|---|---|
| Prepare a downloadable board | [Claude browser preparation](#prepare-in-claude) | Skills and code execution in Claude; no local Python |
| Recalculate after actual picks | [Local live advice](#local-live-advice) | Python 3.10+, PyYAML, and a browser on the same computer |

Neither route syncs with your fantasy platform or makes picks for you. Assistant account and usage limits apply.

<a id="claude-in-your-browser-recommended"></a>

## Prepare in Claude

You do not need to install Python or use a terminal for this route. A *skill* is the downloadable package of instructions and scripts you give Claude.

**Prerequisites, checked September 5, 2026:** Anthropic lists custom skills for Free, Pro, Max, Team, and Enterprise. Code execution must be enabled; organization settings may restrict uploads. Your account's usage limits still apply. [Anthropic's setup requirements](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

1. [Download fantasy-draft-analyst.zip](https://github.com/nicodeguyo/fantasy-draft-analyst/raw/refs/heads/main/dist/fantasy-draft-analyst.zip). Keep it zipped.
2. In Claude, enable **Settings → Capabilities → Code execution and file creation**. For a work account, check your organization's Skills settings if this is unavailable.
3. Open **Customize → Skills → + → Create skill → Upload a skill**, choose the ZIP, and enable it. [Official upload instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
4. Start a new chat. Paste the [short starter prompt](../README.md#setup), or use the [full league template](#league-template) and ask Claude to use the fantasy draft analyst skill. Enable web search for fresh sources when available.
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

## Local live advice

This route recalculates recommendations after each recorded pick. It requires a Python process on your computer; a downloaded HTML file from a cloud chat cannot run the server. You can ask a local coding assistant to perform these steps.

1. Clone the repository and create an environment, using the [Claude Code commands](#claude-code) through the dependency installation step (copying the skill is optional for direct script use).
2. Save your confirmed settings as `league.yaml` outside the installed skill. Ask your assistant to prepare this from the [league template](#league-template). Validate every keeper's identity, owner, and round cost.
3. From the cloned repository root, enter the skill directory and prepare current public data (if you installed the skill elsewhere, enter that folder instead):

```bash
cd skills/fantasy-draft-analyst
python scripts/prepare_data.py --league /path/to/league.yaml --season 2026 --fetch-espn --fetch-cbs --fetch-fantasypros --out /path/to/players.csv
```

Replace the paths and season with your own. These feeds may be incomplete or unavailable. Inspect the output mode, source dates, warnings, and `players.evidence.json` before drafting. Provider fetch times do not prove that the forecasts themselves were recently updated. Keep the sidecar beside the CSV. Have the assistant research relevant news separately; this fetch does not supply automatic live news or betting data.

4. Start your session:

```bash
python scripts/live_draft.py --session /path/to/session.json init --league /path/to/league.yaml --players /path/to/players.csv
python scripts/live_draft.py --session /path/to/session.json serve --port 8768
```

5. Open `http://127.0.0.1:8768` on that same computer. Record a pick and confirm the draft history and shortlist update. Try Undo before draft night. Keep the Python process running while drafting.

**What success looks like:** the local board shows the correct turn, your roster, available players, and an updated shortlist after a recorded pick. It shows evidence limitations instead of treating missing projections as verified advice.

To resume, run `serve` with the same session file; do not initialize again. You can import actual picks, resolve unmatched names, refresh player inputs, and export decision records. Refreshing data is separate from recording picks. [Full live-session guide](../skills/fantasy-draft-analyst/references/live-draft.md).

### If local setup gets stuck

- **Python or PyYAML missing:** use the environment commands below. On Windows activate with `.venv\Scripts\Activate.ps1`; use `python` if that is your Python 3 command.
- **Page unavailable:** keep the server running, open the printed address on the host computer, and choose another port if 8768 is occupied. A phone cannot reach this loopback address.
- **No numerical recommendation:** inspect unresolved own picks and data coverage. Rank-only advice is a declared fallback, not a full projection comparison.
- **Need a preparation board too:** follow the skill's preparation workflow with the same validated inputs. The downloaded board remains a separate, frozen artifact.

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

Use the [local live setup above](#local-live-advice) for v3 data preparation and draft sessions. To inspect the frozen public example offline, follow [example reproduction](site/README.md). For the old simulation comparison, use the [v2 benchmark archive](archive/v2-benchmark.md).

## Updating

Re-download and upload the packaged ZIP, or pull the repository and re-copy the installed skill folder. Keep your league files outside the skill folder so replacing it does not replace your inputs. Regenerate your board when you want updated data; downloading a new skill does not refresh an existing board.


## League template

You can start with the short prompt and let the assistant ask questions. If you already have the settings, paste this complete template. “I don't know” is better than guessing; confirm the settings before the simulation.

```text
Use the fantasy draft analyst skill to make my draft plan.
Ask me about missing settings before you simulate.

Season and draft date: [2026, date and time zone]
Platform: [ESPN / Yahoo / Sleeper / other]
League size: [number of teams]
Draft order: [snake / linear], my pick: [number], rounds: [number]
Scoring: [standard / half-PPR / PPR]
Passing TDs: [4 or 6], interceptions: [penalty]
Other scoring: [bonuses, TE premium, or none]
Starting lineup: [QB, RB, WR, TE, FLEX, superflex, K, DEF counts]
Bench spots: [number]
Keepers: [none, or number allowed and cost rules]
My keeper options: [player and round cost, or none]
Known league keepers: [draft slot, player, round cost for each; or unknown]
Players I like or want to avoid: [names and why, or none]
Draft-room tendencies: [anything I know, or unknown]
Board colors: [favorite NFL team or colors]

Use current public data and show the date and source for each input.
Tell me if any data is unavailable or any result is only an approximation.
Give me keeper advice if relevant, a pick-by-pick plan, the cost of
waiting, and a downloadable HTML board. Explain the assumptions and
which changes would alter your recommendation. Do not use the sample
league's saved player data as current data for my league.
```

For live mode, also say: “Help me set up the local live session on my computer. Confirm actual keeper declarations and show me how to record, undo, and import picks.”
