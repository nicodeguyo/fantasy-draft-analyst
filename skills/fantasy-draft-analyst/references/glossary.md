# Glossary — plain-language definitions for the appendix

Use only the terms that appear in the analysis. Definitions are written for a first-year player.

**ADP (average draft position)** — The average pick number at which a player is being taken across many drafts. It's the market price, not a ranking. Different platforms produce different ADPs because their users draft differently.

**Bell cow** — A running back who gets the clear majority of his team's carries plus the goal-line and passing-down work. The opposite is a committee, where two or more backs split the job unpredictably.

**Cliff** — A large drop in projected points between one tier and the next at a position. Cliffs are where you either pay up before the drop or deliberately wait until after it.

**Dead zone** — The stretch of a position's rankings (usually running backs from about pick 50 to 90) where nearly every player is in a committee or an unresolved camp battle. Reaches are earned here by role certainty, nowhere else.

**Flex** — A lineup slot that can be filled by more than one position (usually RB, WR, or TE). Each flex slot adds to how many players at those positions start league-wide, which lowers replacement level.

**Handcuff** — The backup to a starting running back. Owning your own starter's backup protects you if the starter gets hurt; in deep leagues with thin waiver wires this is defensive value.

**Keeper** — A player you carry over from last season instead of drafting. He costs you a pick, set by the league's keeper rule (often the round he was originally drafted, or one round earlier).

**Keeper inflation** — With keepers removed before the draft, the player available at any pick is worse than ADP implies, because the best players are already gone. Roughly, pick p delivers the ADP-(p + 0.7 × keepers) player early in the draft.

**Monte Carlo simulation** — Running the same draft many times with realistic randomness in how other teams pick. It is used twice here: 1,500 drafts to measure how often each player is still available at each of your picks, and 200 more per candidate per pick to measure pick value.

**Pick value** — Your projected final starting lineup if you take this player at this pick and draft sensibly for the rest of the draft. It is measured, not derived: the simulator plays the remaining picks out a couple of hundred times for each candidate and averages the lineup you end up with. It is what ranks every pick table, and unlike surplus it needs no assumption about where replacement level sits.

**Now** — On the board, how many points of final starting lineup you give up by taking that row instead of the best choice at that pick. "best" means take him; "−14" means fourteen points across a season, under one a week.

**Cost of waiting** — For one of your picks and one position, the value expected to be on the board now minus the value expected at your next pick. It answers "is this the round for a running back?" The same replacement level sits in both terms and cancels, so the answer doesn't move if that estimate does.

**Standard error (SE)** — How much a simulated average would wobble if you ran the simulation again. Two players within about two standard errors of each other are level, and the board says so rather than picking a winner on a decimal.

**Plan path** — The target at each of your picks, built pick by pick by taking the best pick value each time. A target has to be someone you can realistically expect to be there (at least half the time); a better player who falls to you less often is shown as "if he falls" upside instead.

**Pick geometry** — Your exact pick numbers in a snake draft and how far apart they are. Paired picks (at the turn) let you plan combinations; evenly spaced picks don't.

**Projection (Proj)** — Total fantasy points expected over the full regular season in your league's scoring. Not per game.

**Reach** — Taking a player earlier than his availability suggests you need to. Justified only by role certainty in a tier that's about to run out, and never by more than one round.

**Red-zone share** — The percentage of a team's plays inside the opponent's 20-yard line that go to a player. Touchdown totals bounce around; red-zone share moves less and predicts them better.

**Replacement level** — The projected points of the worst player at a position who still has to be in someone's starting lineup every week. With 14 teams and two flex spots, roughly the 38th running back and the 50th receiver. It explains which pools are deep; it no longer decides picks, because it is an estimate that can sit on a cliff and swing every back's value by twenty points.

**Route share** — The percentage of his team's pass plays a receiver actually runs a route on. The most predictive receiver stat there is, because efficiency on 40% of routes rarely survives a promotion to 85%.

**Snake draft** — A draft where the pick order reverses each round (1–12, then 12–1). The last pick of round 1 also gets the first pick of round 2.

**Superflex** — A flex slot that can also be filled by a quarterback. It roughly doubles the number of starting quarterbacks league-wide and makes QBs the scarcest position.

**Surplus ("vs. free")** — Projection minus replacement level: the points a player adds over the player you could have had for nothing. It is the clearest way to see which positions are deep this year, and it is the column on the tier boards. It does not rank the pick tables — see **Pick value**.

**Target share** — The percentage of a team's pass attempts thrown to one player. High target share on a low-volume passing offense produces good rate stats and mediocre totals; pair it with team attempts.

**Targets per route run (TPRR)** — Targets divided by routes run. Measures whether a player earns the ball when he's on the field. Above ~24% is elite; below ~17% is a decoy.

**There %** — How often a player was still undrafted at a given pick across the simulated drafts, measured with your own seat drafting off ADP so the number is about the rest of the room and not about your plan. Below 50% means plan for him being gone; above 80% means don't reach.

**Tier** — A group of players close enough in projection that which one you get barely matters. Draft across tiers, never within them.

**Win total** — The sportsbook line for how many games a team will win. A useful prior for game script: high win totals on run-first teams cap their receivers; low win totals on pass-heavy teams lift them.

**Yards per route run (YPRR)** — Receiving yards divided by routes run. A real efficiency measure, but unstable on small samples; use it to confirm a role story, not create one.
