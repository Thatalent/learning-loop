# Bloom's Taxonomy for Competency Goals

Use these levels to find a person's competency gap and to decide what counts as evidence. Treat them as a pyramid: each level rests on the ones below, so secure the foundation before building on it. In practice levels overlap (a quick Apply exercise can build Understanding), but when setting goals, close the lowest gap first.

| Level | The person can... | Useful verbs | Evidence that they've got it |
|---|---|---|---|
| **Remember** | Recall facts, names, terms | define, list, name, recognize | Answers recall questions correctly; uses terms correctly in conversation |
| **Understand** | Explain ideas in their own words | explain, summarize, describe, compare | Explains the concept or root cause to you in plain English without copying your phrasing |
| **Apply** | Use it in a real situation | run, implement, use, execute | Runs the query, writes the config, or performs the fix themselves |
| **Analyze** | Break a situation into parts and find causes | diagnose, trace, differentiate, debug | Diagnoses a new or variant problem with little or no help |
| **Evaluate** | Judge quality and make tradeoffs | review, critique, justify, choose | Reviews someone else's solution and spots real issues; defends a design choice |
| **Create** | Produce something new that others can use | design, write, build, teach | Writes the runbook, design, or explainer that someone else successfully learns from |

## Finding the gap

A goal is a gap: **the level the role needs minus the level the person can prove.**

**What the role needs**
- Uses the system day to day: Apply.
- On call for it, or debugging it: Analyze.
- Owns its design or reviews changes to it: Evaluate.
- Teaches it, documents it, or onboards others: Create.

**What they can prove: probe upward until it breaks.** Ask one problem per level, starting at the base, adapted to the actual system. Stop at the first level they can't do without help or looking things up; that is their edge.

| Level | Probe (adapt to the system) |
|---|---|
| Remember | "Without looking: what does it take in, what does it produce, who owns it?" |
| Understand | "In two or three sentences, what happens from input to output, and why is it built that way?" |
| Apply | "What exact check shows whether it's healthy right now? Run it." |
| Analyze | "Its main number dropped by half overnight. Three possible causes, and what do you check first?" |
| Evaluate | "Here's a proposed fix. What would you need to know before approving it, and what could it break?" |
| Create | "Outline the first steps of a runbook a new teammate could follow without asking you." |

**For non-technical topics** (a product, process, client account, policy or report), use the same climb with their material:

| Level | Probe |
|---|---|
| Remember | "Without looking: what are the main steps, and who's involved in each?" |
| Understand | "In two or three sentences, why does it work this way?" |
| Apply | "Walk me through exactly what you'd do for this real case." |
| Analyze | "This went wrong last month. What are three possible reasons, and which would you check first?" |
| Evaluate | "Here's a proposed approach. What would you need to know before agreeing, and what could go wrong?" |
| Create | "Outline a short guide or checklist a new colleague could follow without asking you." |

Judge answers on whether they demonstrate the level (specific, causal where needed, actionable), not on polish. "Shaky" (partly, or needed to look) counts as the edge.

**The first goal is the first level they couldn't prove**, never a level above it, even if the role needs more. If they're solid through everything the role needs, there's no gap for this system: say so, and offer Create (writing it up for the next person) rather than teaching below their level.

**Then say it out loud:** "You're solid through Understand, and on call this needs Analyze. So the first goal is Apply: you run the health check yourself." Let the person push back on the goal.

## Gauging cheaply during normal work

You won't run the full climb on every task. Lightweight signals:
- Listen to vocabulary. Correct use of terms suggests Remember+; describing mechanisms suggests Understand+.
- Ask for a prediction. Accurate predictions suggest Understand or Analyze.
- Ask what they've already tried. Good hypotheses suggest Analyze.
- When unsure, probe one level up with a single question rather than assuming.
