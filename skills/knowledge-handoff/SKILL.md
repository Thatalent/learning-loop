---
name: knowledge-handoff
description: 'Captures newly discovered system knowledge before it disappears into a chat or one person''s head. Use PROACTIVELY, without being asked, at the wrap-up of any investigation, bug fix, triage, or feature: when Claude has figured out something non-obvious about the codebase or system (a root cause, hidden coupling, undocumented behavior, gotcha, or design decision) and the user signals they''re done ("that fixed it", "thanks", "works now", "merged", "ship it", "LGTM", asking to commit, open a PR, or close a ticket). At that moment, offer once to turn it into a short doc the user shapes: explainer, runbook, incident debrief, decision record, or note in the repo''s docs. Also use when the user says "document this", "write this up", "make a runbook", "write the postmortem", "turn this into docs", "make a lesson", "train the team on this", or "onboarding deck". Skip trivial changes and anything already documented.'
---

# Knowledge Handoff

Teaching others sits at the top of the learning ladder, and writing a document is how most of us teach others at work. This skill does two jobs at once:

1. **It cements the person's own learning.** Writing exposes gaps that reading never does.
2. **It moves knowledge out of silos.** Out of one engineer's head, and out of the AI's context window, into a place the team can find.

The rule that makes both work: **the person shapes the content; you make it good.** If you ghost-write the whole thing, the doc may be fine but the person learns little, and nobody can answer follow-up questions about it.

## 0. Proactive capture at wrap-up (the most important trigger)

Most knowledge is lost not because nobody would write it down, but because nobody is asked at the right moment. That moment is **the end of the work**, right after you've reported what you found and the person signals they're wrapping up. Don't wait for "document this".

**When to offer.** All three are true:
1. **Something new was figured out.** During this session you discovered something non-obvious about the system: a root cause, a hidden dependency between components, behavior the code or docs don't make clear, an environment or config gotcha, a workaround, or a design decision and its reasons.
2. **It would help someone later.** A teammate (or this person in six months) hitting the same area would want it. Ask yourself: "If this person left tomorrow, would the team lose this?"
3. **It's wrap-up time.** The fix works, tests pass, the person says thanks or "done", or asks you to commit, open a PR, or close the ticket.

**When not to offer.** Trivial or self-explanatory changes; knowledge already in a doc you can point to (link it instead); the person declined a handoff earlier in this session; or an incident is still in progress (wait until it's resolved).

**How to offer.** One short, specific line at the end of your wrap-up, naming the knowledge, the doc type, and where it would live. Never block the wrap-up on it:

> One thing worth keeping: the nightly refresh and the build both write the same S3 key, which isn't obvious from either job. Want me to capture it as a short runbook note in your team wiki, linked from the ticket? About 2 minutes; I'll ask you two questions.

**If they say yes, keep it fast.** Default to a short interview (two or three questions, see step 2), so the person still puts it in their own words. Then write the doc, mark anything unconfirmed as unverified, and save it where the org context says docs live (the ticket or the team wiki), or the repo's `docs/` folder for code-level knowledge. In a coding session, prefer adding it to the same branch or PR as the change, so the knowledge ships with the code.

**If many people will need this,** pass the many-learners test in step 1a, and offer a lesson deck instead of a doc. That is still one offer, not two:

> This scheme/port mismatch will bite anyone who configures a client for this database. Want to turn it into a 10-minute self-paced lesson deck in `docs/lessons/`, so the next engineer can click through it with a quiz at the end?

**If they say no or ignore it,** drop it for the rest of the session. One offer, no reminders.

**In Claude Code especially:** you often know more about what changed and why than anyone else will after the session ends. Before your final summary of an investigation, fix, or feature, check the three conditions above. If they hold, end the summary with the offer.

## 1. Pick the doc type

Ask or infer which fits (templates in `references/templates.md`):
- **Explainer:** how something works and why. For concepts and systems.
- **Runbook:** what to do when a specific thing happens. For repeatable operations and triage.
- **Incident debrief:** what broke, why, and what changes. For post-incident learning.
- **Decision record:** what we chose, the alternatives, and why. For design choices.
- **Onboarding note:** what a newcomer needs to know first.
- **Lesson deck:** a self-paced, click-through lesson with questions and reveals, built with the `frontend-slides` skill. For things many people will need to learn. See step 1a.

Keep it short. One page that gets read beats ten that don't.

## 1a. Lesson decks: when many people need to learn it

A doc tells people what's true. A lesson deck makes each new reader predict, practice and check themselves, the same loop the original person went through, so the lesson repeats without anyone there to teach it.

**The many-learners test.** Make a lesson deck instead of a doc when at least one of these holds:
- Many people will need it: onboarding to a shared system, a tool or process the whole team uses, or a concept everyone on call must understand.
- The knowledge is a **pattern** that will recur in other services or teams (a class of bug, a config trap, a design tradeoff), not a one-off fix.
- It has been asked or explained more than once already.
- The person says "the team should know this", "train others", or "make this a lesson".

For a single system quirk only its owners will hit, a runbook or explainer is still better. Don't make a deck when a page would do.

**Build it.**
1. **Keep the person shaping it.** Use interview mode (step 2) to settle the learning goal as a Bloom's level ("after this, an engineer can diagnose X alone" is Analyze) and the 3–5 key points, in their words.
2. **Outline it so it teaches, not tells.** Use the lesson deck outline in `references/templates.md`: goal, big picture, a predict-first question, the real case, the named pattern, a practice scenario, a check-yourself quiz, and where to go next. Put every question on one slide and its answer on the next, so self-paced readers commit to a guess before they see it. Take the quiz questions from `check-understanding` at the target level when it's installed.
3. **Hand the outline to `frontend-slides`.** Tell it this is a **reading deck** (self-paced, higher density), so it doesn't need to ask, and let it run its style choice with the person. Keep it to about 10–15 slides, roughly 10 minutes.
4. **Sanitize** (step 4). A lesson meant for many readers spreads further than a ticket comment.
5. **Publish it as one HTML file** where learners will look (step 5). Default to `docs/lessons/<topic>.html` in the relevant repo, unless `org-context.md` says otherwise. Link it from the README, the runbook or wiki page, and the ticket. If the folder has an index (`docs/lessons/README.md`), add one line: the topic, who it's for, and the target level.

**If `frontend-slides` isn't installed,** write the same outline as an explainer with a "Check yourself" section, and mention that the skill would turn it into a click-through deck.

## 2. Choose a drafting mode

Offer these; let the person pick:

- **They draft, you critique** (best learning). They write a rough version in any form; you review against `../check-understanding/references/rubrics.md` (if installed; otherwise check accuracy, causality, audience, and runnable steps), ask about gaps, and tighten the prose.
- **Interview mode** (best for people who hate writing). Ask one or two questions at a time: **two or three in total** for a quick wrap-up capture (step 0), or **four to six** for a full doc or a lesson deck ("What was the first sign something was wrong?", "In your words, what actually caused it?"), then assemble the doc from *their answers*, keeping their phrasing where it's accurate. This still makes them generate the knowledge.
- **You draft, they own** (fastest; use when time is short). You draft from the conversation, then ask them to read it and change at least the summary and root cause into their own words. Mark anything they haven't verified.

## 3. Fact-check and mark provenance

- Check every claim against what actually happened in the conversation or in the real system. Don't fill gaps with plausible guesses.
- Anything the AI inferred but nobody verified gets marked: `> ⚠️ Unverified: ...`. The person can confirm and remove the marker.
- Include the diagram from the session if there was one. Visuals make docs far more useful to the next reader.

## 4. Protect sensitive information

Before publishing, scan for things that shouldn't be in a shared doc: credentials, tokens, personal data, customer names or identifiers, and anything listed under "Never include" in `../learning-loop/references/org-context.md` (if present). If the doc is meant for **public** sharing (a blog post, an open-source repo, a conference talk), also generalize internal system names, product vocabulary, and architecture details so the doc teaches the *pattern* without exposing how the business works. Use the sanitization checklist in `references/templates.md`.

## 5. Publish where people will find it

- Use `org-context.md` to pick the destination (wiki space, repo docs folder, ticket link).
- If a docs or wiki connector is available, offer to publish there directly (ask before publishing; it's visible to others).
- Otherwise produce a doc-ready file or block the person can paste.
- Link it from where people will look: the ticket, the PR, the alert, the README.

## 6. Close

One line on where it lives, plus one optional suggestion: "Want to make this the first item in a quick quiz for the next person who's on call?" (which uses `check-understanding`). For a lesson deck, suggest instead that the next person to onboard runs through it and says where they got stuck, so the deck improves.
