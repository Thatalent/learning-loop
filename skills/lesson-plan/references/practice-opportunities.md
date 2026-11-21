# Practice Opportunities: plan for mastery, not for a pace

Based on Koedinger, Carvalho, Liu & McLaughlin, "An astonishing regularity in student learning rate," PNAS 120(13), 2023: 1.3 million observations, 27 datasets, 6,946 learners, math, science and language, late elementary to college.

## What the research found

- **Explanation alone isn't enough.** After lectures and readings, learners typically start practice at about **65% correct**, below mastery (80%).
- **Mastery takes repeated practice.** A typical learner needs about **7 practice opportunities per knowledge component** to reach 80%.
- **People differ mostly in where they start.** Starting accuracy ranged from about 55% (lower half) to 75% (upper half): about **13 opportunities** to mastery versus about **4**.
- **People are remarkably similar in how fast they learn.** Each opportunity adds about **0.09 log odds (~2.5 percentage points near 65%)**. A typical "slower" learner needs only about **one extra** opportunity (7.9 vs 6.9).
- **Practice counts, not time.** Opportunities predicted learning far better than calendar time.
- **Fine-grained knowledge components matter.** Learning is only visible when skills are split into the right small units; lumping them into one skill hides it.
- **More variation in rote, fact-heavy topics.** Learning-rate differences were larger in language datasets (arbitrary mappings) than in math or science, where learners can compensate by reasoning.

**Implication for every lesson:** the gap between learners is a gap in opportunities. Give people who start lower more practice, never a slower pace, lower expectations or a "slow learner" label.

## The conditions that make it true (build every practice item to these)

The finding holds under "favorable learning conditions." All the systems studied:
1. give **immediate feedback** on errors;
2. offer **explanatory, context-specific help on demand**, including a correct example if needed;
3. require the learner to **enter or see the correct response before moving on**;
4. use **tasks designed for one specific skill**, aligned with the goal;
5. give **repeated opportunities in varied tasks**, so knowledge generalizes but doesn't overgeneralize.

`Kit.practice` implements 1–5. A plain quiz question does not (no retry to the correct answer, no repetition).

## How to plan a lesson with this

1. **Break the goal into knowledge components (KCs).** A KC is the smallest piece someone can get right or wrong on its own: "pick Deque vs List for a need", not "Java collections". Tag each practice item with **one** KC (the paper found single-KC tagging predicts as well as multi-KC and is easier to interpret).
2. **Estimate the starting point per KC** from the interview or probe: roughly 75% (solid), 65% (typical), 55% (shaky), 40% (new to it).
3. **Budget opportunities** with `(logit(0.80) − logit(start)) / 0.09`, rounded up:

| Estimated starting accuracy | Opportunities to 80% |
|---|---|
| 75% | ~4 |
| 65% | ~7–9 |
| 55% | ~13–14 |
| 40% | ~20 |

4. **Write enough varied items** for each KC: at least the budget, with different surface details (numbers, names, contexts) and the same underlying skill. Varied items build generalization; repeating the same item builds memorization of that item.
5. **Let mastery, not slides, decide when to move on.** `Kit.practice` stops after 3 first-try successes in a row (adjust with `streak`) or at `max`, and records how many more opportunities are likely needed.
6. **Spread big budgets across sessions.** If a KC needs 13+ opportunities, do part now and queue the rest for spaced follow-ups (in two days, then a week). The follow-up practice set comes from the results slide or `check-understanding`.
7. **For rote, fact-heavy KCs** (vocabulary, arbitrary mappings, names), expect more variation between people: plan more spaced retrieval and adjust from the learner's actual first-try results rather than the averages.

## Scoring rules

- **Only the first attempt counts** as performance. A wrong first try or using a hint is recorded as an error; the learner still learns from the feedback and the retry.
- **Report progress as opportunities**, never as ability: "7 opportunities so far, about 4 more to mastery", not "you're behind".

## Limits to keep in mind

- The data come from well-designed practice systems (feedback, hints, varied tasks); the regularity may not hold without those conditions.
- How many opportunities each learner got wasn't experimentally controlled. A 2026 reanalysis (Lee et al., "The 'Astonishing Regularity' Revisited") found that estimates of learning-rate variation are sensitive to practice-sequence length. Treat equal learning rates as a strong default, not a law: let each learner's first-try results adjust their plan.
- Learners only benefit from opportunities they actually take. Make practice short, varied and clearly worth it, and say how close they are to mastery.
