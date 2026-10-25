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
| `learning-loop` | The core engine: finds your competency gap (the Bloom's level your role needs minus the level you can prove), picks activities, adds micro-moments (why-lines, predict-first, diagrams), and tracks a "gap ledger" of things the AI knows that you don't yet | **Ambient** during building, documenting, and exploring. **Opt-in** during triage, with a debrief offer at the end |
| `check-understanding` | Quizzes, flashcards, scenario questions, and rubric reviews, matched to the Bloom level | "Quiz me", "check my understanding", or after a session |
| `knowledge-handoff` | Turns what you learned into an explainer, runbook, debrief, or decision record that **you** shape, then publishes it. When many people need to learn the same thing, it builds a self-paced lesson deck instead (with the optional [`frontend-slides`](https://github.com/zarazhangrui/frontend-slides) skill) so the lesson repeats without a teacher | "Document this", "write the postmortem", or end-of-task offers |
| `lesson-plan` | Builds a **personalized, interactive HTML lesson** for one learner on any topic, technical or not (a system, but also a product, process, client conversation or policy), aimed at their gap: one hands-on activity per Bloom's level, picked to fit the topic (label a diagram, order a process, sort, explore a simulation, estimate, spot the mistake, finish a task, branching scenario), plus a results slide and a revisit plan. Built with [`frontend-slides`](https://github.com/zarazhangrui/frontend-slides) | "Make me a lesson on…", "teach me X properly", or when a team needs a lesson deck |

### The learning dial
- **Just do it:** the work, plus a 2-line "what happened and why" at the end. Default for urgent triage.
- **Learn alongside:** the work, plus lightweight learning moments. Default for everything else.
- **Teach me:** you drive, Claude coaches.

Say "just do it" or "skip the learning" at any time, and the teaching stays off for the rest of the session, including after context compaction. Say "turn the learning back on" to resume. Opting out stops the teaching, not the nudge: Claude still ends each substantive task with a one-line recap and a single one-line offer to go deeper.

### Why it triggers so often (Claude Code plugin only)

Claude picks a skill by matching your message against its description, which isn't enough for a skill meant to run ambiently. A request like "complete this ticket" has no learning words in it, yet the change it produces can move a business rule and the data other teams read. So the plugin ships three hooks (`hooks/hooks.json`), and nothing has to be added to your repos:

- **SessionStart** adds a standing instruction to use `learning-loop` by default, including the skill's Completion check before work is reported as done. It works like a line in `~/.claude/CLAUDE.md`, but nobody has to edit that file, and it goes away when you disable the plugin.
- **UserPromptSubmit** adds a one-line nudge when a prompt asks why or how something works, asks to explain or walk through code, a diff or a PR, or reports an error, failure, crash or stack trace, plus a wrap-up nudge on "that fixed it", "LGTM", "merged", "open PRs", "push the branch", "complete this ticket" and similar. Keyword checks run on the prompt text only; the script uses `jq` or `python3` when installed and falls back to a plain-text check otherwise.
- **Stop** runs the **learning judge** (`scripts/learning_judge.py`) on the change itself. It diffs the branch against the repo's default branch, measures the work, and looks for three kinds of signal: a **business rule** (a window, threshold, limit, default or schedule), a **data impact** (what a query selects or a job writes, a schema change) and a **contract** (a field one side sends and another reads). A business rule plus a data or contract change means the engineer must understand the downstream effect: the hook asks Claude to run the loop at Bloom *Analyze* and to offer a `knowledge-handoff` change explainer, and it hands over a mermaid skeleton of the data flow. It blocks once per new set of signals, only in sessions that edited files, honors the opt-out, and lets the session finish if it hits any error. The same rubric lives in the skill (Completion check), so clients without hooks apply it too.

#### Optional: teach the judge your repo's real consumers

Out of the box the judge uses generic rules (`scripts/learning-judge.default.json`) that find the *kind* of change but not who consumes it, so it asks Claude to look up the real readers before teaching or drawing. A repo can add `.claude/learning-judge.json` to name them, for example "this config key feeds the nightly rollup job, which feeds the weekly revenue dashboard". Copy the default file as a starting point, replace the `downstream` chains with real ones, and set `"include_default_rules": true` to keep the generic rules as well. No script or hook goes in the repo.

```bash
# What would the judge say about a branch? (run from inside the repo)
python3 <plugin>/scripts/learning_judge.py report
python3 <plugin>/scripts/learning_judge.py report --head feature/my-branch --json
```

To turn all three hooks off and keep the skills, set `LEARNING_LOOP_NUDGES=off` (for example in the `env` block of `~/.claude/settings.json`). `LEARNING_JUDGE=off` turns off only the Stop-hook judge. The hooks need `bash`, and the judge needs `python3` (3.8+, standard library only) and `git`, so they don't run on Windows without WSL or Git Bash. Skills uploaded to claude.ai don't get the hooks, but they still carry the Completion check.

## Install

**Claude (claude.ai / desktop):** download the `.skill` files from the [latest release](https://github.com/Thatalent/learning-loop/releases/latest) and upload each one in Settings → Capabilities → Skills.

**Claude Code (plugin marketplace):**
```
/plugin marketplace add Thatalent/learning-loop
/plugin install learning-loop@learning-loop
```

**Other LLM tools:** each `skills/*/SKILL.md` is plain markdown with a short YAML header. Tools that support the Agent Skills format can load the folders directly. For others, paste the SKILL.md contents into custom instructions or a project prompt.

## Make it yours

Copy `skills/learning-loop/references/org-context.template.md` to `org-context.md` and fill in your tools, where docs should live, your internal glossary, and what must never appear in learning material. The skills read it automatically.

## Try it

See `examples/demo-smart-playlist.md` for a fictional 10-minute demo that teaches three classic bug patterns.

## License

MIT
