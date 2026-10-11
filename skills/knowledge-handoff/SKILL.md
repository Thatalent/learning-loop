---
name: knowledge-handoff
description: Turns what a person learned or built with an AI into a durable document they own, such as an explainer, runbook, incident debrief, decision record, or onboarding note, so knowledge doesn't live only in one person's head or in a chat transcript. The person drafts, dictates, or answers interview questions; Claude structures, critiques, fact-checks, and publishes. Use whenever the user says "document this", "write this up", "make a runbook", "write the postmortem/debrief", "how do I share what we learned", "turn this into docs", or accepts an end-of-task offer to capture knowledge. Also use after triage debriefs, onboarding sessions, or any work where the AI figured out something about the system that the team should know.
---

# Knowledge Handoff

Teaching others sits at the top of the learning ladder, and writing a document is how most of us teach others at work. This skill does two jobs at once:

1. **It cements the person's own learning.** Writing exposes gaps that reading never does.
2. **It moves knowledge out of silos.** Out of one engineer's head, and out of the AI's context window, into a place the team can find.

The rule that makes both work: **the person shapes the content; you make it good.** If you ghost-write the whole thing, the doc may be fine but the person learns little, and nobody can answer follow-up questions about it.

## 1. Pick the doc type

Ask or infer which fits (templates in `references/templates.md`):
- **Explainer:** how something works and why. For concepts and systems.
- **Runbook:** what to do when a specific thing happens. For repeatable operations and triage.
- **Incident debrief:** what broke, why, and what changes. For post-incident learning.
- **Decision record:** what we chose, the alternatives, and why. For design choices.
- **Onboarding note:** what a newcomer needs to know first.

Keep it short. One page that gets read beats ten that don't.

## 2. Choose a drafting mode

Offer these; let the person pick:

- **They draft, you critique** (best learning). They write a rough version in any form; you review against `../check-understanding/references/rubrics.md` (if installed; otherwise check accuracy, causality, audience, and runnable steps), ask about gaps, and tighten the prose.
- **Interview mode** (best for people who hate writing). You ask 4–8 focused questions one or two at a time ("What was the first sign something was wrong?", "In your words, what actually caused it?"), then assemble the doc from *their answers*, keeping their phrasing where it's accurate. This still makes them generate the knowledge.
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

One line on where it lives, plus one optional suggestion: "Want to make this the first item in a quick quiz for the next person who's on call?" (which uses `check-understanding`).
