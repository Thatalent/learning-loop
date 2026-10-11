# Bloom's Taxonomy for Competency Goals

Use these levels to set the target ("what should they be able to do?") and to decide what counts as evidence. Levels build on each other, but people don't have to climb in strict order. A quick Apply exercise often builds Understanding faster than more explanation.

| Level | The person can... | Useful verbs | Evidence that they've got it |
|---|---|---|---|
| **Remember** | Recall facts, names, terms | define, list, name, recognize | Answers recall questions correctly; uses terms correctly in conversation |
| **Understand** | Explain ideas in their own words | explain, summarize, describe, compare | Explains the concept or root cause to you in plain English without copying your phrasing |
| **Apply** | Use it in a real situation | run, implement, use, execute | Runs the query, writes the config, or performs the fix themselves |
| **Analyze** | Break a situation into parts and find causes | diagnose, trace, differentiate, debug | Diagnoses a new or variant problem with little or no help |
| **Evaluate** | Judge quality and make tradeoffs | review, critique, justify, choose | Reviews someone else's solution and spots real issues; defends a design choice |
| **Create** | Produce something new that others can use | design, write, build, teach | Writes the runbook, design, or explainer that someone else successfully learns from |

## Choosing a target

- **Triage debrief:** usually Analyze ("could you diagnose the next one?").
- **Building a feature in an unfamiliar area:** Apply for the parts they'll maintain, Understand for the rest.
- **Onboarding to a system:** Understand for the big picture, Apply for the daily tasks.
- **Owning a system or being on call for it:** Analyze minimum; Evaluate for design decisions.
- **Writing team documentation:** Create, which requires the levels below it. Gaps show up quickly when someone tries to write it.

Don't aim everything at Create. Pick the level the person actually needs for their role, and say it out loud so they can push back ("I'm aiming for you to be able to diagnose this kind of thing yourself. Is that the right goal, or do you just need the gist?").

## Gauging the current level cheaply

- Listen to vocabulary. Correct use of terms suggests Remember+; describing mechanisms suggests Understand+.
- Ask for a prediction. Accurate predictions suggest Understand or Analyze.
- Ask what they've already tried. Good hypotheses suggest Analyze.
- When unsure, assume one level lower than it looks and adjust quickly. Over-explaining slightly is cheaper than losing them.
