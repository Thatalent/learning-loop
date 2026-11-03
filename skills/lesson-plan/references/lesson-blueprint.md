# Lesson Blueprint

## 1. Intake interview (always, before writing anything)

Always interview the learner, even when you think you can infer the answers. Ask in one message (use a structured-question UI if there is one), and follow `teaching-sequence.md` §1:
1. **Topic and scope:** what exactly should they learn? ("How our nightly refresh works" beats "data pipelines.") If the conversation already makes it clear, state your reading and ask them to confirm.
2. **What their role needs:** use it day to day (Apply), troubleshoot it or handle problems with it (Analyze), own it, decide about it or review others' work on it (Evaluate), or teach it (Create).
3. **Where they are now:** a self-rating with **"No prior knowledge (default)"** pre-selected, plus a 2–3 question probe for anything higher. Never assume a level from job title alone.

Also note: time available (default 15 minutes), whether they're technical (for non-technical learners, use their documents, conversations and decisions, never code or system jargon), their language or stack if it is a code topic, and whether the lesson will be shared (if so, keep internal names, customer data and credentials out).

## 2. Objectives

Write one objective per level from the learner's **edge** (the first level they couldn't prove, or Remember for no prior knowledge) up to the **target**. Phrase each as something they'll be able to do, with a Bloom's verb:

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
| 4…n | **One teaching segment per objective, in level order** | Explain, diagram and give an example (`teaching-sequence.md` §3), then the activity from `activity-catalog.md` that practices exactly that. Skip the teaching only for content the interview showed they already know |
| n+1 | **Apply it to your world** | A prompt that connects the pattern to the learner's own system ("Find a job in your system that shares an output with another one") |
| n+2 | **Results** | `Kit.summary`: results by level, the next goal, and a next step per level |
| n+3 | **Make it stick** | When to revisit (in two days, then a week), what to try without notes, and a Create task (explain it to someone, or write it up with knowledge-handoff) |

**Teach before you test.** Apart from the predict-first slide, every activity must be answerable from what the lesson has already shown, or from what the interview proved the learner knows. The predict-first slide is the only deliberate exception: label it as a guess ("No wrong answers yet"), keep it off the results slide (give it an id containing a colon, such as `guess:predict`; `Kit.summary` skips those), and make sure later slides answer it.

For **group lessons a presenter runs** (lunch and learns, onboarding sessions), assume no prior knowledge, and keep the room's answer to a show of hands or a shout-out, with the presenter clicking.

Every activity slide shows its Bloom's level in the eyebrow ("Spot the bug · Analyze") and, the first time a type appears, one line on *why this activity*. Learners take the format more seriously when they know what it trains.

## 4. Build

1. **Read the frontend-slides skill** and follow it for everything visual: the fixed 1920×1080 stage, `viewport-base.css` included in full, a style preset that suits the topic, navigation and reduced motion. Choose a preset that fits the learner and topic; don't reuse one by default.
2. **Inline the kit:** paste `assets/lesson-kit.css` into the `<style>` block and `assets/lesson-kit.js` into a `<script>` block. Set the `--kit-*` variables to match the preset's colors and fonts.
3. **Write content only:** each activity is one `Kit.<type>(element, config)` call with plain data. Don't write new interaction code unless no kit type fits; if you must, follow the same rules (keyboard accessible, feedback with explanation, hint before answer, `record` the result).
4. **Keyboard safety:** the deck's arrow-key navigation must ignore key presses inside inputs, sliders and selects (see the example).
5. **Use the examples as references** for wiring. Both are known to work: `assets/example-lesson.html` (a technical topic, every activity type) and `assets/example-lesson-nontechnical.html` (a client renewal conversation, with spot-the-mistake in prose mode and a business simulation).

## 5. Check before handing over

- Open it (or render it headless) and complete every activity once: no console errors, every activity reaches a "correct" state, and the summary fills in.
- **Teach-before-test check:** for every activity except predict-first, name the earlier slide (or interview answer) that taught what it needs. If you can't, add teaching before it or cut the activity.
- Check that no slide overflows the stage and that text is readable at projector size.
- For non-technical learners: read every slide as they would. Any unexplained acronym, tool name or system term is a bug; define it or remove it.
- Search the file for anything that shouldn't be shared if the lesson will travel (internal hostnames, customer names, tokens).

## 6. Deliver

- **Claude Code:** save to `docs/lessons/<topic>.html` in the repo (create the folder if needed) and tell the learner how to open it. If it's for a team, suggest linking it from the README or onboarding doc.
- **Claude apps:** create the HTML file and present it. If the environment publishes artifacts, publishing gives a shareable link.
- Close with one line: when to revisit, and an offer to turn what they learned into a doc (knowledge-handoff) or to quiz them later (check-understanding).
