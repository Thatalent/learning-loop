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

## Sanitization checklist for public sharing
- [ ] No customer, client, or partner names (including in ticket titles and screenshots)
- [ ] No credentials, tokens, account IDs, hostnames, bucket or table names, or internal URLs
- [ ] Internal product and system names replaced with generic plain-English descriptions
- [ ] Architecture simplified to the pattern being taught (for example, "a nightly job writes a file that a cache serves"), with gaps left deliberately so the real system can't be reconstructed
- [ ] Numbers changed or rounded so they don't reveal real business volume
- [ ] Ask yourself: could a competitor learn how the product works from this? If yes, generalize further, or move to a different domain entirely.
