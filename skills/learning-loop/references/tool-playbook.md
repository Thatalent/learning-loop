# Tool Playbook

Use whatever tools are available in the current environment. These are the categories that reliably help, with fallbacks when the ideal tool is missing. Check `org-context.md` for organization-specific tools that fill each slot.

| Learning need | Best tool | Fallbacks |
|---|---|---|
| **See the system** (audio-visual) | An inline diagram or visualization tool (SVG/HTML widget, Mermaid renderer, diagramming connector) | Mermaid code block; ASCII diagram; a short numbered sequence |
| **See the data** | A native chart tool or plotting script | Small table with the 3–5 numbers that matter |
| **Demonstration in the real system** | Read-only connectors to the person's actual systems (databases, logs, repos, ticket tracker) | Show the exact command or query and the expected output; ask the person to run it |
| **Practice** | The person runs it themselves in their terminal or tool; you review | A realistic scenario they reason through in chat |
| **Retrieval practice** | An interactive quiz or flashcard tool | Ask one question at a time in chat; reveal the answer only after they respond |
| **Teaching others** | A collaborative docs tool or wiki connector (so the result is shared) | A markdown file in the repo's docs folder; a doc-ready block they can paste |
| **Teaching many people** (a repeatable lesson) | A self-paced HTML lesson deck from the `frontend-slides` skill, with question and reveal slides (see `knowledge-handoff` step 1a) | An explainer with a "Check yourself" section |
| **Spacing** | A reminder, scheduled message, or calendar tool if available and the person agrees | Suggest when to revisit ("try the variant question again in a couple of days") |

## Rules of thumb

- **Draw when there are more than three moving parts** or a sequence over time. Diagrams that show "normal" next to "what went wrong" are especially effective for debugging.
- **Prefer the real system over a description of it.** Watching a real query return real numbers beats any explanation. Use read-only operations for demonstrations, and never take write actions for the sake of a lesson.
- **Make the person the operator when the stakes are low.** If they can run the command themselves, let them.
- **Don't let tools become the lesson.** One good diagram beats three mediocre ones.
- **Keep sensitive data out of learning artifacts.** Quizzes, diagrams, and docs meant for wide sharing should not contain customer names, credentials, or internal identifiers unless the org context explicitly allows it.
