# Lesson Blueprint

## 1. Intake (keep it to three questions, or infer)

Ask only what you can't infer from the conversation, in one message:
1. **Topic and scope:** what exactly should they learn? ("How our nightly refresh works" beats "data pipelines.")
2. **What their role needs:** use it day to day (Apply), troubleshoot it or handle problems with it (Analyze), own it, decide about it or review others' work on it (Evaluate), or teach it (Create).
3. **Where they are now:** if the learning-loop skill already found their edge this session, use it. Otherwise run a quick probe: 2–3 questions climbing from Remember, stopping where it breaks. Never assume a level from job title alone.

Also note: time available (default 15 minutes), whether they're technical (for non-technical learners, use their documents, conversations and decisions, never code or system jargon), their language or stack if it is a code topic, and whether the lesson will be shared (if so, keep internal names, customer data and credentials out).

## 2. Objectives

Write one objective per level from the learner's **edge** (the first level they couldn't prove) up to the **target**. Phrase each as something they'll be able to do, with a Bloom's verb:

- Understand: "Explain why the playlist shrinks instead of grows."
- Apply: "Write the merge-and-trim fix for a nightly job."
- Analyze: "Diagnose a shrinking dataset from its symptoms."
- Evaluate: "Judge whether a proposed fix removes the cause."

If the edge is already at or above the target, there's no gap: say so, and offer a Create task instead of a lesson.

## 3. Structure (8–14 slides, 10–25 minutes)

| # | Slide | Purpose |
|---|---|---|
| 1 | **Title + "built for you" badge** | Topic, time, and the personalization: "solid through X, your role needs Y, this lesson climbs X+1 → Y" |
| 2 | **Predict first** | One `Kit.predict` question that surfaces the key misconception |
| 3 | **The big picture** | A diagram (static SVG, or `Kit.hotspots` if the edge is Remember) |
| 4…n | **One activity per objective, in level order** | Pick each from `activity-catalog.md`. Precede an activity with a short concept slide only when the learner has nothing to build on |
| n+1 | **Apply it to your world** | A prompt that connects the pattern to the learner's own system ("Find a job in your system that shares an output with another one") |
| n+2 | **Results** | `Kit.summary`: results by level, the next goal, and a next step per level |
| n+3 | **Make it stick** | When to revisit (in two days, then a week), what to try without notes, and a Create task (explain it to someone, or write it up with knowledge-handoff) |

Every activity slide shows its Bloom's level in the eyebrow ("Spot the bug · Analyze") and, the first time a type appears, one line on *why this activity*. Learners take the format more seriously when they know what it trains.

## 4. Build

1. **Read the frontend-slides skill** and follow it for everything visual: the fixed 1920×1080 stage, `viewport-base.css` included in full, a style preset that suits the topic, navigation and reduced motion. Choose a preset that fits the learner and topic; don't reuse one by default.
2. **Inline the kit:** paste `assets/lesson-kit.css` into the `<style>` block and `assets/lesson-kit.js` into a `<script>` block. Set the `--kit-*` variables to match the preset's colors and fonts.
3. **Write content only:** each activity is one `Kit.<type>(element, config)` call with plain data. Don't write new interaction code unless no kit type fits; if you must, follow the same rules (keyboard accessible, feedback with explanation, hint before answer, `record` the result).
4. **Keyboard safety:** the deck's arrow-key navigation must ignore key presses inside inputs, sliders and selects (see the example).
5. **Use the examples as references** for wiring. Both are known to work: `assets/example-lesson.html` (a technical topic, every activity type) and `assets/example-lesson-nontechnical.html` (a client renewal conversation, with spot-the-mistake in prose mode and a business simulation).

## 5. Check before handing over

- Open it (or render it headless) and complete every activity once: no console errors, every activity reaches a "correct" state, and the summary fills in.
- Check that no slide overflows the stage and that text is readable at projector size.
- For non-technical learners: read every slide as they would. Any unexplained acronym, tool name or system term is a bug; define it or remove it.
- Search the file for anything that shouldn't be shared if the lesson will travel (internal hostnames, customer names, tokens).

## 6. Deliver

- **Claude Code:** save to `docs/lessons/<topic>.html` in the repo (create the folder if needed) and tell the learner how to open it. If it's for a team, suggest linking it from the README or onboarding doc.
- **Claude apps:** create the HTML file and present it. If the environment publishes artifacts, publishing gives a shareable link.
- Close with one line: when to revisit, and an offer to turn what they learned into a doc (knowledge-handoff) or to quiz them later (check-understanding).
