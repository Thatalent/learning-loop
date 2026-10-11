---
name: check-understanding
description: Verifies what a person actually learned, at the right Bloom's taxonomy level, using quizzes, flashcards, scenario questions, and rubric reviews of their own work. Use whenever the user says "quiz me", "test me", "check my understanding", "did I get this?", "make flashcards", "practice questions", "am I ready to own this?", or accepts an offer to check their learning after a task. Also use at the end of a learning-loop session, a triage debrief, or onboarding when confirming competency matters. Generates questions from what happened in the conversation (especially things the AI figured out that the person may not have followed), not generic trivia.
---

# Check Understanding

Learning isn't confirmed until the person produces evidence at the target level. This skill builds that evidence quickly and kindly. It's also a learning activity in itself: pulling an answer out of memory (retrieval practice) is one of the best-supported ways to make knowledge stick.

## 1. Set the target

Decide which Bloom's level you're checking. If the learning-loop skill set one, use it. Otherwise infer from the person's role and need, and say it in one line ("I'll check whether you could diagnose this yourself, which is the Analyze level."). See `../learning-loop/references/bloom.md` if the learning-loop skill is installed alongside; otherwise use the table in step 3.

## 2. Draw questions from the real work

The best questions come from the conversation itself:
- The root cause or key concept of the task.
- Items from the gap ledger: things the AI worked out that the person might not have followed.
- Decisions that were made and why.
- Commands, queries, or file locations they'll need again.

Avoid trivia that doesn't matter for doing the work. Never put secrets, credentials, or customer-identifying data in questions.

## 3. Match the format to the level

| Level | Format | Example shape |
|---|---|---|
| Remember | Multiple choice or flashcards | "Which job writes the nightly file?" |
| Understand | Explain-it-back, or multiple choice with plausible misconceptions as distractors | "In two sentences, why did the list shrink instead of grow?" |
| Apply | Do-it task | "Write the query that would show yesterday's row count." |
| Analyze | Variant scenario | "Same symptoms, but the nightly job succeeded. What do you check next?" |
| Evaluate | Critique | "Here's a proposed fix. What's risky about it?" |
| Create | Rubric review of their artifact | Review the runbook they wrote against `references/rubrics.md` |

See `references/question-design.md` for how to write good distractors, scenarios, and hints.

**Default mix:** 3–5 questions, starting one level below the target to build confidence and ending at the target. For a quick end-of-task check, 2–3 questions is plenty.

## 4. Deliver

- If an interactive quiz or flashcard tool is available, use it for Remember and Understand multiple-choice questions. Include a hint and a short explanation for each answer, since the explanation is where much of the learning happens.
- For open-ended questions (explain, apply, analyze, evaluate), ask **one at a time in chat** and wait for the answer. Don't reveal answers before they try.
- Offer a hint before giving the answer if they're stuck. Being stuck briefly is useful; being stuck for long is discouraging.

## 5. Give feedback

- Lead with what they got right, specifically.
- Correct misconceptions directly and explain why the right answer is right, tied back to the real system.
- For explain-it-back answers, judge the idea, not the wording. Paraphrase that captures the mechanism is a pass.
- Keep the tone of a good colleague, never a grader.

## 6. Close the loop

Summarize in two or three lines:
- **Solid:** what they clearly have.
- **Shaky:** what to revisit, and the best next activity for it (for example: "Try running the count query yourself next time", or "Draw the flow from memory").
- **Revisit:** suggest a spaced follow-up ("Try the variant question again in a couple of days. It'll stick much better than re-reading."). If a reminder or scheduling tool is available and they want it, offer to set one.

If they reached the target level, consider offering `knowledge-handoff`: someone who can pass the check can usually write the doc that teaches the next person.
