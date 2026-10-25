---
name: lesson-plan
description: Builds a personalized, interactive HTML lesson for one learner with the frontend-slides skill. It targets the gap between the Bloom's level their role needs and the level they can prove today, with one hands-on activity per level instead of only questions. Activities are chosen to fit what's being taught, for example labeling a diagram, ordering a process, sorting, exploring a simulation, estimating, spotting a mistake, finishing a task, or a branching scenario. Works for any topic, technical or not, from systems and code to products, processes, client conversations, policies and business decisions. Use when someone asks for a lesson, lesson plan, learning plan, tutorial, training module, self-paced lesson, interactive explainer, or "teach me X properly", or when learning-loop or knowledge-handoff decide a person or team needs a lesson rather than a doc.
---

# Lesson Plan

Turn "I need to understand X" into a short, personalized, self-paced HTML lesson where the learner **does** something on almost every slide. It sits at the top of the learning ladder: practice, with feedback, aimed exactly at the learner's gap.

This skill depends on **frontend-slides** for the deck itself (stage, style, navigation). Read that skill first. If it isn't installed, say so and offer either to build a plain single-page lesson with the same activities, or to install it.

## Workflow

1. **Find the gap.** The goal is the distance between the Bloom's level the learner's role needs and the level they can prove today. **If learning-loop already established their level this session, skip the questions** and reuse it. Otherwise **interview them first** (what they need to do, what they already know in their own words, a short probe climbing from the basics, and what confuses them), as described in `references/teaching-sequence.md`. Starting from zero is normal: the lesson then begins at the foundations. If there's no gap, say so and suggest a Create task instead of a lesson.
2. **Map the knowledge.** List the 3–7 ideas the goal depends on, in prerequisite order, and mark which ones they already have. The lesson teaches the missing ones, in order.
3. **Write objectives.** One per level, from the edge up to the target, each phrased as something they'll be able to do.
4. **Teach each objective before testing it.** Every objective is a segment: a plain-language explanation of what, why and how; a labeled diagram with the key part highlighted; a worked example; then the activity; then feedback that explains. Scale the teaching to the learner: novices get every step, people near the goal start at the activity. See `references/teaching-sequence.md`.
5. **Pick one activity per objective** with `references/activity-catalog.md`. Choose by the kind of knowledge first (structure, process, distinctions, cause and effect, judgment, critical reading), then by level and experience. Use at least three different activity types in a lesson of six or more activities.
6. **Build the deck** with frontend-slides, following the structure in `references/lesson-blueprint.md`: title with a "built for you" badge, predict-first, big picture, activities in level order, apply it to your world, results, and make it stick. Inline `assets/lesson-kit.css` and `assets/lesson-kit.js`; each activity is a single `Kit.<type>(el, config)` call with plain data. `assets/example-lesson.html` (technical) and `assets/example-lesson-nontechnical.html` (a client conversation) show every activity type wired up.
7. **Test it.** Complete each activity once (or render it headless): no errors, every activity can be solved, the results slide fills in, nothing overflows the stage.
8. **Deliver and close the loop.** Save it (`docs/lessons/<topic>.html` in a repo, or a presented file or artifact in the apps), tell the learner when to revisit (in two days, then a week), and offer a Create step: write it up with knowledge-handoff, or quiz them later with check-understanding.

## Principles

- **Teach, then test.** A lesson must work for someone who knows nothing about the topic. Explain and diagram each idea before any activity uses it, add one new idea at a time, and don't climb a level until the one below is solid.
- **Interaction is the point.** Questions alone are a quiz. Each objective gets an activity that makes the learner manipulate the idea: arrange it, sort it, break it, fix it, decide.
- **Fit beats variety.** The activity must match what's being taught. A simulation for cause and effect, sequencing for a process, spot-the-mistake for reading code, an email or a policy critically. Never pick a format to tick a box.
- **Speak the learner's language.** Lessons are for engineers and non-engineers alike. For non-technical learners, build from the documents, conversations and decisions they deal with, never code or system jargon, and define any term the topic needs.
- **Personal beats generic.** Build activities from the learner's own work: their systems and incidents, or their clients, processes and reports. When the lesson will be shared or the content is sensitive, use a sanitized or fictional example that teaches the same pattern.
- **Feedback teaches.** Every check explains why, wrong answers get a hint before the answer, and revealing an answer counts as practice rather than success.
- **Accessible by default.** No drag-only interactions (every kit activity works by click and keyboard), readable at projector size, and reduced motion respected.
- **Honest results.** The results slide reports what the learner actually solved and names their next goal: the first level they didn't solve.

## Related skills

- `learning-loop`: finds the competency gap this lesson targets.
- `check-understanding`: question-writing rules for any retrieval slides, and a later follow-up quiz.
- `knowledge-handoff`: for teams, it offers a lesson deck when many people need the same knowledge; use this skill to build it, personalized to the most common gap.
- `frontend-slides` (separate plugin): the deck framework this skill builds on.
