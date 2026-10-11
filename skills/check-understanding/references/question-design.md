# Question Design

## Multiple choice that teaches
- Make distractors **real misconceptions**, not obviously wrong filler. Good sources: the person's own wrong guesses earlier in the conversation, the first hypothesis that got ruled out during debugging, and common general mistakes (such as "the job must have failed" when it actually succeeded but did the wrong thing).
- Keep options parallel in length and form so the longest option isn't always right.
- Every explanation should say why the right answer is right *and* why the most tempting wrong one is wrong.

## Explain-it-back prompts
- Ask for a constrained length ("in two sentences") so the person has to pick the core idea.
- Ask for mechanism, not definition: "why did X happen" beats "what is X".
- Accept their words. Check for the key causal link.

## Variant scenarios (Analyze)
- Change one variable from the real incident and ask what changes in the diagnosis.
- Good variant types: different symptom with the same cause; same symptom with a different cause; the fix applied, but a new edge case.
- Ask "what would you check first, and why?" The *why* reveals whether they have a model of the system or a memorized checklist.

## Critique prompts (Evaluate)
- Present a plausible but flawed fix, query, or design. Include one real issue, not five.
- Ask them to name the risk and propose an improvement.

## Hints
- Hint 1 points to where to look ("Think about what the nightly job writes and where.").
- Hint 2 narrows the mechanism ("What happens if two writers use the same file name?").
- Then give the answer with an explanation.
