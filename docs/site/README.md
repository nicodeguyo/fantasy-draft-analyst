# The sample demo

The homepage is a static, account-free explanation of the existing draft planner. It does not generate personalized boards or run simulations in your browser. Making a personal board follows the [skill setup guide](../install.md).

## One pick, two possible teams

`pick-comparison.json` contains two branches of one saved sample draft, using seed `20260905` and the [sample league](../../examples/sample-league/). Before either branch, the code selects the highest projected available running back and wide receiver at pick 5. It does not search for a favorable result. Both branches copy the same draft state and random-generator state, then use the simulator's adaptive policy to finish the draft. Opponent decisions can diverge as the remaining player pool changes.

The Achane branch projects 1,828 starting-lineup points; the Nacua branch projects 1,858. That 30-point difference is **one illustrative outcome**, not an averaged advantage or a recommendation. The published board averages many rollouts and may rank candidates differently. The homepage highlights players absent from the other branch, rather than treating a player moving between RB1 and RB2 as a different player.

From the repository root, with PyYAML installed:

```bash
python3 scripts/reproduce_demo.py --repo . --output docs/site/pick-comparison.json
python3 scripts/build_demo.py
```

The first command records the input hashes and validates legal lineups. The second refreshes only the marked comparison section in `index.html`. It is deterministic and uses no fresh network data. The homepage also contains both saved lineups as ordinary HTML, so this explanation remains readable without JavaScript.

## Animation and privacy

Changing the selected candidate animates the saved lineup for about a quarter second. Scroll progress draws a small underline beneath the example heading. No essential text depends on either effect; reduced motion disables positional animation. The walkthrough video is user-controlled with captions. Copying an example link includes only the saved branch (`rb` or `wr`), never a visitor's editable league prompt. The page has no analytics, account login, or form submission.

The 10-second recording is trimmed from the original real sample-board recording. It demonstrates manual pick tracking; it does not imply recalculated advice.

## Local preview and deployment

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. GitHub Pages should deploy `main`, root; `.nojekyll` keeps the static files intact. Relative assets also work under the `/fantasy-draft-analyst/` project base path. The package download points to the committed skill zip.

Scroll Craft's unchanged engine is vendored from commit `0b816225945e45380397d6a0487efa3c98916858` of [nateherkai/scroll-craft](https://github.com/nateherkai/scroll-craft), under its [MIT license](vendor/SCROLLCRAFT-LICENSE). The site needs no Node build, external fonts, generated imagery, or additional Python runtime dependency.
