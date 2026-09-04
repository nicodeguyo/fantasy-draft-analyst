# Installing the skill

The skill is a folder: `skills/fantasy-draft-analyst/` containing `SKILL.md`, reference files, and scripts. Where you put it depends on where you use Claude.

## Claude.ai (web) and the Claude desktop app, including Cowork

Cowork and claude.ai load the skills enabled on your account, not files on your computer.

1. Download the packaged skill: [`dist/fantasy-draft-analyst.zip`](../dist/fantasy-draft-analyst.zip). (The zip's root is the `fantasy-draft-analyst/` folder — that's what the uploader expects. If you zip it yourself, zip the folder, not its contents.)
2. Turn on **Settings → Capabilities → Code execution and file creation**. The simulator and the board renderer are Python scripts; they run in Claude's code sandbox when this is on. Without it the skill still works — it does the math analytically and skips the HTML board.
3. Open **Customize → Skills** (left sidebar on claude.ai; the Customize entry in the desktop app's sidebar) → **+** → **Create skill** → **Upload a skill** → choose the zip. Toggle it on.
4. Start a chat and describe your draft. The skill triggers on its own when you mention a draft, keepers, a pick number, ADP, tiers, or targets; you can also say "use the fantasy draft analyst skill".

Plan notes as of September 2026: Anthropic's support docs say skills are available on Free, Pro, Max, Team and Enterprise with code execution enabled; the developer docs list custom skills as Pro and up. If the upload option isn't there on a free plan, use the [paste-anywhere prompt](../prompt/fantasy-draft-analyst-prompt.md) instead.

## Claude Code

Personal (every project):

```bash
git clone https://github.com/nicodeguyo/fantasy-draft-analyst.git
mkdir -p ~/.claude/skills
cp -r fantasy-draft-analyst/skills/fantasy-draft-analyst ~/.claude/skills/
pip install pyyaml
```

Project-only: copy the folder to `.claude/skills/fantasy-draft-analyst/` inside the project instead.

Invoke with `/fantasy-draft-analyst`, or just describe your league — Claude reads the skill's description and picks it up. Scripts run with `python3 ${CLAUDE_SKILL_DIR}/scripts/draft_sim.py ...`; Claude handles that.

As a plugin (so updates come through `/plugin update`):

```
/plugin marketplace add nicodeguyo/fantasy-draft-analyst
/plugin install fantasy-draft-analyst@fantasy-draft-analyst
```

## Any other assistant (ChatGPT, Gemini, a plain chat)

Open [`prompt/fantasy-draft-analyst-prompt.md`](../prompt/fantasy-draft-analyst-prompt.md), fill in the league block at the top, and paste the whole thing. Turn on web browsing if the assistant has it; if not, paste your platform's top-150 ADP and the last few days of injury news for your targets into the chat. You get the same method with pencil-and-paper math instead of a 1,500-draft simulation.

## Running the scripts yourself

Everything is standard-library Python plus PyYAML.

```bash
cd examples/sample-league
python3 ../../skills/fantasy-draft-analyst/scripts/draft_sim.py --league league.yaml --players players.csv --sims 1500 --pick-values --keeper-scenarios --out sim.json
python3 ../../skills/fantasy-draft-analyst/scripts/build_board.py --league league.yaml --sim sim.json --notes notes.json --players players.csv --out draft-board.html
```

`draft_sim.py` prints a markdown summary (the plan path with its projected lineups, keeper scenarios, cost of waiting, the pick-value table at each of your picks, replacement levels, sample drafts) and writes `sim.json` plus `sim_availability.csv`, a full name × pick availability matrix. Budget five to six minutes for a 12-team league; `--rollouts 60` gives a rough answer in under two, and `--no-pick-values` skips the rollouts entirely. `fetch_adp.py` pulls current ADP from FantasyFootballCalculator, ESPN, the Footballguys cross-platform table, or Sleeper trending; `scoring.py` turns stat-line projections into points in your scoring; `merge_adp.py` reprices a player pool with your platform's ADP.

## Updating

The skill is versioned in `SKILL.md` (`metadata.version`). Re-download the zip or `git pull` and re-copy. Your `league.yaml` lives outside the skill folder, so updates don't touch it.
