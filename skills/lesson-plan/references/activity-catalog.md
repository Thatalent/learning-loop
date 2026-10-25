# Activity Catalog

Ten interactive activity types, grouped by **what kind of knowledge they teach**. Pick by the knowledge type first, then check the Bloom's level and the learner's experience. Every type is implemented in `assets/lesson-kit.js`, so a lesson only supplies content.

Sources behind these choices: the H5P content-type catalog (the most widely used open set of interactive learning formats), research on Parsons problems, explorable explanations, faded worked examples, and erroneous examples. Summaries are under "Why these work" at the end.

## Quick picker

| What you're teaching | Best-fit activity | Bloom's levels | Kit function |
|---|---|---|---|
| The parts of a system, vocabulary, "what is where" | **Label the diagram** (explore hotspots, then find-it quiz) | Remember | `Kit.hotspots` |
| A procedure, pipeline, lifecycle or timeline | **Put it in order** (Parsons-style sequencing) | Understand, Apply | `Kit.sequence` |
| Distinctions: symptom vs cause vs fix, which category, which owner | **Sort it** (buckets) | Understand, Analyze | `Kit.sort` |
| Cause and effect in something that changes (caches, queues, retries, rate limits, timing, scaling) | **Explore the system** (simulation with a goal) | Understand, Analyze | `Kit.simulate` |
| A misconception you want to surface before teaching | **Predict first** | Understand | `Kit.predict` |
| Scale and intuition: sizes, rates, costs, latency | **Estimate** (calibration slider) | Understand, Evaluate | `Kit.estimate` |
| Reading code, configs, queries or logs critically | **Spot the bug** (erroneous example) | Analyze, Evaluate | `Kit.spot` |
| A skill the learner will perform: a fix, a query, a runbook step | **Finish the fix** (faded worked example) | Apply | `Kit.fade` |
| Judgment under uncertainty: triage, trade-offs, policy | **Choose your response** (branching scenario) | Apply, Analyze, Evaluate | `Kit.branch` |
| Recall to lock it in | **Retrieval check** (quiz or flashcards; use the check-understanding skill's question rules) | Remember, Understand | `Kit.predict` with several items, or a quiz slide |

**Create** is not an in-deck activity: end every lesson by asking the learner to produce something (an explainer, a runbook note, teaching a teammate), and point to the knowledge-handoff skill.

## Choosing well

**Match the learner's experience (the expertise reversal effect).** Worked and faded examples help novices most and can slow down experienced learners. For someone solid through Understand, lead with Predict, Sequence and Finish the fix. For someone solid through Apply, lead with Spot the bug, Explore the system and Choose your response.

**One activity per objective, climbing.** A personalized lesson has one objective per Bloom's level from the learner's edge up to what their role needs, and one activity per objective, in level order. Don't put a Remember activity in front of someone who's already solid at Understand.

**Variety matters, but fit matters more.** Never use an activity just to fill a type quota. Use at least three different types in a lesson of six or more activities, so it doesn't feel like a quiz in disguise.

**Use the learner's real context.** Activities built from the learner's own systems, code and incidents transfer far better than generic ones. When the content is sensitive or the deck will be shared, use a sanitized or fictional equivalent that teaches the same pattern.

## Design rules per activity

### Label the diagram (`Kit.hotspots`)
- Draw the system as an inline SVG: 4–7 parts, labeled, with arrows for data flow.
- Place each hotspot at a box's corner (percent coordinates), never over its label.
- Explore first (each spot reveals one sentence about that part), then a 2–4 question find-it quiz ("Which part can show an out-of-date number?").

### Put it in order (`Kit.sequence`)
- 4–7 steps, each a short complete sentence. Order must be unambiguous.
- Don't add distractor steps for novices: research found distractors lowered success and increased time on task for novice learners. Add one for experienced learners only.
- The explanation should say *why* the order matters, not repeat the order.

### Sort it (`Kit.sort`)
- 2–4 buckets, 4–9 cards, at least two cards per bucket.
- Best buckets are distinctions experts make instinctively and novices blur: symptom/cause/fix, safe/risky, read-only/writes data, team A/team B owns it.

### Explore the system (`Kit.simulate`)
- 1–3 controls (sliders or toggles) and a `render(state)` that returns a small result: a number, a status, or a tiny SVG.
- Always give a goal ("Change the settings until the playlist keeps its songs") with a `check(state)`. A simulation without a goal is a toy; with a goal it's a guided discovery.
- The success message should name the insight ("Timing never fixes it; only separating the writers does").

### Predict first (`Kit.predict`)
- Use it at the start of a section, before the explanation. 3–4 options, built from real misconceptions.
- Wrong guesses are fine and expected; the reveal does the teaching.

### Estimate (`Kit.estimate`)
- Pick a quantity whose true value surprises (a cache hit rate, a queue's backlog after an hour, rows after a bad join).
- Set a tolerance that rewards the right order of magnitude, not exactness.

### Spot the bug (`Kit.spot`)
- 4–12 lines of the learner's language or config format; exactly one bug (or two related lines).
- Frame it as someone else's code. Attributing errors to a fictional author keeps it low-stakes.
- Hint points to *where to look*, explanation says *why it breaks* and *how to fix it*.

### Finish the fix (`Kit.fade`)
- 3–6 steps, with 1–3 blanks. Fade later steps first for novices, earlier steps for those further along.
- `accept` lists every reasonable answer (synonyms, short forms). Matching is case-insensitive substring.

### Choose your response (`Kit.branch`)
- 2–3 decision points, 2–3 choices each, at least one good ending and one realistic bad ending.
- Feedback on each choice explains the consequence. Bad choices should be tempting, not silly.

## Why these work (research summary)

- **Interactive formats generally:** the H5P catalog's core types (drag and drop, fill in the blanks, image hotspots, branching scenarios, interactive books) are the formats most widely used for self-paced interactive learning, and they map onto the activities above.
- **Parsons problems (sequencing):** studies found learners complete Parsons problems faster than fixing or writing code, with the same learning gains; distractor steps reduced novice success and increased time on task.
- **Explorable explanations (simulations):** what distinguishes them from plain widgets is that they deliberately guide attention to particular phenomena in the simulation, which is why every simulation here has a goal.
- **Faded worked examples:** reduce cognitive load for novices; in a workplace training study, gradual fading outperformed both example–problem pairs and pure problem-solving, especially on delayed and transfer tests.
- **Erroneous examples (spot the bug):** students who found, explained and fixed errors did significantly better on delayed tests than students who solved the same problems, even though they liked the materials less. Expect it to feel harder; that's part of why it works.
- **Retrieval practice and prediction** (see the learning-loop skill's `learning-ladder.md`): pulling an answer from memory, and guessing before being told, both strengthen retention.
