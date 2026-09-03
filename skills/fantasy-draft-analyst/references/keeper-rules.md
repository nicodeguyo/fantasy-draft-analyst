# Keeper rules — a taxonomy, and how each one changes the math

Keeper leagues are all different, and the differences aren't cosmetic: two leagues with the same rosters and the same ADP can have opposite keeper answers. Get the rule exactly, then apply the adjustment below. When the user isn't sure, ask them to paste the rule text or a screenshot of the league's keeper sheet — the "keeper draft #" column on a commissioner's sheet is the rule in practice.

Contents

1. Cost basis
2. Eligibility
3. Number and duration
4. Timing and information
5. Auction keeper leagues
6. Dynasty and contract leagues (out of scope, with pointers)
7. Quick reference table

---

## 1. Cost basis

**Same round as drafted.** The keeper costs the pick in the round he was originally drafted. Surplus = (ADP as a pick) − (your pick in that round), then converted to points. A round-1 keeper is usually only worth it for a true top-5 player because inflation makes a late first-round pick a much better pick than it looks.

**One round earlier than drafted (round-minus-one).** The most common "escalating" rule. A player drafted in round 3 costs a round-2 pick. Round-1 picks become unkeepable (there is no round 0) — check whether the league treats them as ineligible or as costing round 1. This rule punishes early-round keepers and rewards mid-round hits; the best keepers are round 4–10 players who became top-40 assets.

**Two rounds earlier.** Same logic, steeper; mid-round hits are still keepable, early-round picks rarely are.

**Escalating year over year.** Costs rise each year the player is kept (round 8 → 7 → 6…). Adds a shelf life: value the keeper for this year *and* the discounted option to keep him again. A round-1 keeper has zero option value; a round-9 keeper on a 24-year-old has a lot. This rarely changes this season's decision but decides ties.

**Fixed round for all keepers** (e.g., every keeper costs a round-1 pick, or all keepers cost the last round). Compare each candidate's ADP against that single fixed pick. Under "all keepers cost round 1," keep the best player, full stop; under "all keepers cost the last round," keep the best player too — everyone is free — but note that other teams' keepers will all be elite, so inflation is at its maximum.

**Auction value carryover.** See §5.

## 2. Eligibility

**Waiver and free-agent pickups.** Three conventions: not keepable at all; keepable at the last round (or a fixed late round); or keepable at a round assigned by the commissioner. This is the highest-leverage unknown in most analyses — a free-agent RB1 at a last-round cost beats any drafted keeper. Ask first.

**Traded players.** Usually keep the original draft round, so the acquiring team inherits the cost basis. Some leagues re-price on trade. The commissioner's sheet will show it.

**Previously kept players.** Some leagues cap consecutive years (2 or 3); some escalate; some forbid keeping a player who was kept last year. Check both the cap and whether the cost basis resets.

**Rookies / undrafted players.** Occasionally priced at a fixed round. Ask.

**Round-1 picks.** Under round-minus-one rules, either ineligible or capped at round 1 — the difference is whether your best player is even an option.

## 3. Number and duration

**One keeper.** Pure surplus maximization: keep the biggest points-over-alternative, then draft.

**Two or three keepers.** The picks you forfeit interact. Keeping a round-2 and a round-3 player removes your two best draft picks; the alternative is one keeper plus a real pick at the other slot. Evaluate combinations, not candidates: for each combination, total surplus of the kept players minus the surplus you'd have drafted with the forfeited picks (after inflation). Often the right answer is one elite keeper plus one cheap late-round hit rather than two mid-round players.

**Unlimited keepers with escalating costs** shades toward dynasty; the same combination logic applies, but option value dominates for young players.

## 4. Timing and information

**Keepers declared before the draft, visible to all.** The most common case. You can model inflation because you know exactly which players are gone. Ask the user for the league's keeper list if it's been published — it replaces the simulator's keeper-draw model and makes the availability numbers much sharper.

**Keepers declared at the draft (as your pick in that round).** Inflation is unknown until it happens. Model it with the simulator's weighted draw and be more conservative on availability.

**Keeper deadline before the season's final roster moves** (injury designations, trades) means you may keep a player whose situation changes. Weight injury news heavily right before the deadline.

## 5. Auction keeper leagues

Keeper cost is last year's auction price (sometimes plus a fixed bump). Compute this year's fair price from surplus (see methodology § Auction) and keep any player whose fair price exceeds his keeper cost by the largest margin, in dollars. Inflation is explicit: total kept value minus total kept cost is the surplus that inflates every other player's price at the auction — estimate it and adjust your fair prices upward by that share.

## 6. Dynasty and contract leagues

Out of scope for this skill's full workflow. The single-season surplus math still holds for "who should start-quality players cost," but roster value there is dominated by age curves, contract years, and rookie-pick value; use a dynasty-specific process.

## 7. Quick reference

| Rule | What it does to the answer |
|---|---|
| Same round | Favors top-of-board keepers (inflation makes early picks worse than ADP) |
| Round-minus-one | Favors mid-round hits; round-1 picks unkeepable |
| Escalating yearly | Adds option value to cheap young keepers |
| Fixed round 1 for all | Keep the best player |
| Fixed last round for all | Keep the best player; expect maximal inflation |
| Waiver pickups not keepable | Eliminates the most common cheap-keeper source |
| Waiver pickups at last round | Often the best keeper on the roster — check first |
| Traded players inherit cost | Cost basis follows the player |
| Superflex | QB keepers roughly double in surplus |
| Multiple keepers | Evaluate combinations, not candidates |
| Keeper list published pre-draft | Feed it to the simulator instead of the draw model |
