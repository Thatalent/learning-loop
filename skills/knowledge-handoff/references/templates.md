# Templates

Keep every doc skimmable: a summary on top, short sections, diagrams where they help.

## Explainer
```
# How <thing> works
**In one sentence:** ...
## The big picture
<diagram>
## Step by step
## Why it's built this way
## Common gotchas
## Check yourself
<one question or command a reader can use to verify understanding>
```

## Runbook
```
# Runbook: <symptom or alert>
**Use when:** <symptoms>
**Severity / who to page:** ...
## Quick checks (read-only)
1. <command/query> → expected: ...
## If check N fails
## Fix
⚠️ <flag any write/destructive step>
## Verify it worked
## Related: <links>
```

## Incident debrief
```
# Debrief: <short title> (<date>)
**Summary:** what happened, impact, status.
## Timeline
## Root cause
<mechanism in plain English> **Pattern:** <e.g. overwritten state, stale cache>
<before/after diagram>
## Why we didn't catch it sooner
## Fixes
| Type | Change | Ticket |
## What we learned
```

## Decision record
```
# Decision: <title>
**Status:** proposed / accepted / superseded
## Context
## Options considered
## Decision
## Consequences
```

## Onboarding note
```
# Start here: <system>
## What it does (one paragraph)
## The 3 things to understand first
## Where to look when something's wrong
## Who to ask
```

## Lesson deck outline
Hand this to `frontend-slides` as a reading deck. "Q/A" means a question slide followed by its answer slide.
```
1. Title: <topic>, for <audience>, ~10 min
2. Goal: "After this you can <Bloom verb + task>"
3. Big picture: one diagram of the parts involved (normal vs. failure for a bug)
4. Q/A Predict first: "What do you think happens when ...?"
5. The real case: what happened, shown with the actual error, log or query (sanitized)
6. Name the pattern: the general rule in one sentence, and where else it shows up
7. Q/A Practice: a new scenario with the same pattern, different details
8-10. Q/A Check yourself: 3 questions at the target level (from check-understanding)
11. Where next: runbook or explainer links, owner or channel to ask, date and author
```

## Sanitization checklist for public sharing
- [ ] No customer, client, or partner names (including in ticket titles and screenshots)
- [ ] No credentials, tokens, account IDs, hostnames, bucket or table names, or internal URLs
- [ ] Internal product and system names replaced with generic plain-English descriptions
- [ ] Architecture simplified to the pattern being taught (for example, "a nightly job writes a file that a cache serves"), with gaps left deliberately so the real system can't be reconstructed
- [ ] Numbers changed or rounded so they don't reveal real business volume
- [ ] Ask yourself: could a competitor learn how the product works from this? If yes, generalize further, or move to a different domain entirely.
