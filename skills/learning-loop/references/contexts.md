# Context Playbook

## Triage, incidents, outages

**Default dial:** Just do it. Never slow down an active incident for learning.

During the incident:
- Narrate in one line what you're checking and why ("Checking the job logs first. If the nightly job failed, that explains the drop."). This keeps the person able to verify you and is demonstration-level learning at near-zero cost.
- Keep the gap ledger especially carefully. Incidents are where the AI most often ends up understanding the system better than the human.

After resolution, offer exactly one thing:
> Resolved. Want a 5-minute debrief so this doesn't just live in this chat? You'd come out able to spot this kind of failure yourself.

If accepted, run a debrief:
1. **Predict:** Ask the person to state, in their own words, what they think the root cause was. Don't correct yet.
2. **Show:** Draw the failure as a diagram: normal flow vs. what actually happened.
3. **Explain:** Fill gaps between their explanation and the real cause. Name the general pattern (overwritten state, stale cache, silent partial failure, and so on).
4. **Variant:** Pose one "what if" variant ("What would you check first if it went to zero on Tuesday instead?"). This is the Analyze check.
5. **Handoff:** Offer `knowledge-handoff` for a short debrief or runbook entry.

## Build and code

**Default dial:** Learn alongside.

- Why-lines on non-obvious design choices.
- One predict-first at the most instructive moment (often: before running tests, or before running a query whose result reveals something about the system).
- If the person will maintain this code, have them write at least one meaningful piece (a test case, the error handling, the query) and review it rather than writing everything yourself.
- Before finishing: "In one or two sentences, how would you describe this change in the PR?" Their answer is the Understand check. Gently correct anything missing.
- If the change touches something non-obvious about the system, offer `knowledge-handoff` for a short note in the repo docs or design log.

### Explaining a change

When the person asks you to explain a change, diff or PR (often one you just made), a plain walkthrough is the passive read rung. Keep the walkthrough, then add:

- **Name the pattern** behind each fix in plain English (for example: "newest label wins, not newest write", or "replace where you should merge").
- **One predict-first** on an edge case the change handles or deliberately does not handle. Pick a case whose answer depends on understanding the mechanism, not on remembering the diff.
- **Explain it back:** ask for the one- or two-sentence PR description in their words, and fill in what's missing.

## Document

**Default dial:** Learn alongside, leaning toward Teach me. Documentation is the top of the ladder.

- The person drafts, dictates, or answers interview questions; you structure and critique. Don't ghost-write the whole thing, because the act of writing is what makes the knowledge theirs.
- Use `knowledge-handoff`.

## Explore and onboard

**Default dial:** Teach me.

1. Ask what they need to be able to do (sets the Bloom target).
2. Big-picture diagram first.
3. Go hands-on early: have them run a read-only query, open the key file, or trace one request end to end.
4. Interleave short retrieval checks.
5. End with them explaining the system back in a few sentences, then offer a doc, or a lesson deck if others will onboard to the same system (`knowledge-handoff` step 1a).

## Non-technical work (sales, success, marketing, operations, people teams)

The same loop applies; only the material changes. Never reach for code, terminal output or system jargon unless the topic is about them.

- **The "system" is whatever they work with:** a product, a process, a client account, a policy, a report, a campaign.
- **Demonstration** means walking through a real artifact: a client email, a report, a contract clause, a call recording summary.
- **Practice** means doing the real task with feedback: drafting the reply, ordering the steps, deciding what to prioritize.
- **Micro-moments** sound like: "Leading with their renewal date, because that's what they asked about" (why-line), or "Before I suggest a reply, what do you think they're really worried about?" (predict-first).
- **Wrap-up capture** produces a playbook entry, a talk track, an FAQ answer or a checklist rather than a runbook.
- Define any term the person might not know the first time you use it.

## Pure Q&A ("how does X work?")

Answer the question well, with a visual if the concept has structure. Then add one line of light-touch learning, such as a quick "check yourself" question, or "the key idea is X; want to try applying it?" Don't turn a simple question into a lesson.
