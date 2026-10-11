# Rubrics for Create-level Artifacts

Use these to review documents the person wrote. Give feedback per criterion with a specific suggestion, not a score. Point out the strongest part first.

## Explainer / concept doc
- **Accurate:** no factual errors about the system.
- **Causal:** explains why, not only what.
- **Right audience:** a newcomer could follow it; jargon is defined or linked.
- **Visual:** includes a diagram where the system has moving parts.
- **Checkable:** ends with a way for the reader to verify their understanding (a question, or a command to run).

## Runbook
- **Trigger is clear:** says when to use it (symptoms, alerts).
- **Steps are runnable:** exact commands or queries, with expected output.
- **Decision points:** says what to do when a check fails.
- **Safe:** read-only checks before any write action; destructive steps clearly flagged.
- **Owner and links:** who to escalate to; links to deeper docs.

## Incident debrief
- **Timeline:** what happened, when, and how it was noticed.
- **Root cause:** the mechanism, plus the general pattern it belongs to.
- **Why it wasn't caught:** the gap in tests, alerts, or design.
- **Fixes:** immediate remediation vs. lasting fix, with tickets.
- **Blameless:** about systems, not people.

## Decision record
- **Context:** the problem and constraints.
- **Options:** at least two, with tradeoffs.
- **Decision and why.**
- **Consequences:** what gets easier, what gets harder, and what would make us revisit.
