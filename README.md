# Learning Loop

**Skills that make you more competent every time you work with an AI, instead of more dependent on it.**

AI assistants are great at doing the work. The quiet cost is that the AI ends up understanding your system better than you do, and what it figured out disappears when the chat ends. Learning Loop flips that default. You still get real work done at real speed, with small, well-timed learning moments built in, a way to confirm what you learned, and a habit of turning it into docs your team can use.

## The framework

Two ideas, each answering a different question:

| Question | Framework | Role in the skills |
|---|---|---|
| *Where am I, and where do I need to be?* | **Bloom's taxonomy** (Remember → Understand → Apply → Analyze → Evaluate → Create) | Sets the competency goal and defines what counts as evidence |
| *How do I get there?* | **The learning ladder**, often called the learning pyramid (read → see → watch → discuss → practice → teach others) | Chooses activities, favoring the most active rung the situation allows |

A note on honesty: the learning pyramid is usually shown with retention percentages (5%, 10%, … 90%). Those numbers have no known source study. The *ordering*, active beats passive, is well supported, so these skills use it as a ladder and lean on techniques with strong evidence: retrieval practice, prediction, self-explanation, spacing, and visuals.

## The skills

| Skill | What it does | When it runs |
|---|---|---|
| `learning-loop` | The core engine: sets a Bloom goal, picks activities, adds micro-moments (why-lines, predict-first, diagrams), and tracks a "gap ledger" of things the AI knows that you don't yet | **Ambient** during building, documenting, and exploring. **Opt-in** during triage, with a debrief offer at the end |
| `check-understanding` | Quizzes, flashcards, scenario questions, and rubric reviews, matched to the Bloom level | "Quiz me", "check my understanding", or after a session |
| `knowledge-handoff` | Turns what you learned into an explainer, runbook, debrief, or decision record that **you** shape, then publishes it | "Document this", "write the postmortem", or end-of-task offers |

### The learning dial
- **Just do it:** the work, plus a 2-line "what happened and why" at the end. Default for urgent triage.
- **Learn alongside:** the work, plus lightweight learning moments. Default for everything else.
- **Teach me:** you drive, Claude coaches.

Say "just do it" or "skip the learning" at any time, and it stays off for the rest of the conversation.

## Install

**Claude (claude.ai / desktop):** download the `.skill` files from Releases and upload each one in Settings → Capabilities → Skills.

**Claude Code (plugin marketplace):**
```
/plugin marketplace add <your-github-user>/learning-loop
/plugin install learning-loop@learning-loop
```

**Other LLM tools:** each `skills/*/SKILL.md` is plain markdown with a short YAML header. Tools that support the Agent Skills format can load the folders directly. For others, paste the SKILL.md contents into custom instructions or a project prompt.

## Make it yours

Copy `skills/learning-loop/references/org-context.template.md` to `org-context.md` and fill in your tools, where docs should live, your internal glossary, and what must never appear in learning material. The skills read it automatically.

## Try it

See `examples/demo-smart-playlist.md` for a fictional 10-minute demo that teaches three classic bug patterns.

## License

MIT
