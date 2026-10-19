#!/usr/bin/env bash
# Injects learning-loop reminders into Claude's context. Called from hooks/hooks.json.
#   session: standing instruction on start, resume, clear and compact
#   prompt:  records an opt-out ("just do it", "skip the learning"); otherwise nudges when the
#            prompt asks why/how something works, reports an error or failure, or wraps up
# The opt-out is remembered per session in a flag file, so it survives context compaction.
# Opting out stops the teaching, not the end-of-task nudge: the short recap and one-line offer
# always remain, by design, so the door stays open for when the person has time.
# Set LEARNING_LOOP_NUDGES=off to turn both hooks off without uninstalling the plugin.

[ "${LEARNING_LOOP_NUDGES:-on}" = "off" ] && exit 0

input=$(cat)

# Read one top-level string field from the hook's JSON input. Uses jq or python3 when
# available, so keyword checks run on the user's prompt only, not on paths in the JSON.
field() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r --arg k "$1" '.[$k] // empty' 2>/dev/null
  elif command -v python3 >/dev/null 2>&1; then
    printf '%s' "$input" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get(sys.argv[1]) or "")
except Exception: pass' "$1" 2>/dev/null
  else
    printf '%s' "$input" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -n 1
  fi
}

emit() {
  # $1 = hook event name, $2 = context text (no double quotes or backslashes)
  printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' "$1" "$2"
}

session_id=$(field session_id | tr -cd 'A-Za-z0-9_-')
optout_flag="${TMPDIR:-/tmp}/learning-loop-optout-${session_id:-unknown}"

case "$1" in
  session)
    if [ -f "$optout_flag" ]; then
      emit SessionStart "learning-loop: the user opted out of teaching earlier in this session. Do the work without learning moments, predict-first questions or quizzes. Still end each substantive task with the short close: a one-line recap of what happened and a single one-line offer to go deeper or capture it as a doc. Resume teaching only if the user asks to turn learning back on."
    else
      emit SessionStart "The learning-loop plugin is installed, and its user wants it used by default. Load the learning-loop skill before answering when the user asks why something happened or broke, pastes an error, stack trace or failing log, asks how something works, asks to explain or walk through code, a diff or a PR (including changes Claude just made), or is building, debugging, reviewing, documenting or onboarding. For urgent triage, do the work first, then end with the skill's short close: what happened, the one thing worth knowing, and a single offer to go deeper. At wrap-up, when something non-obvious was figured out, load the knowledge-handoff skill and make one specific offer to capture it. If many people will need to learn it (onboarding, a pattern that recurs across services or teams, a team-wide tool), offer a self-paced lesson deck built with the frontend-slides skill instead of a doc. Before you report implementation work as done, run the skill's Completion check on the diff: if the change moved a business rule, data or a contract, run the loop on the downstream effect and offer a knowledge-handoff change explainer with a before/after diagram. A Stop hook checks this too. If the user says just do it or skip the learning, stop teaching for the rest of the session but keep the one-line recap."
    fi
    ;;
  prompt)
    prompt=$(field prompt)
    [ -z "$prompt" ] && prompt="$input"   # fallback: scan the raw JSON if it couldn't be parsed

    # Opting back in clears the flag; opting out sets it. Both take effect immediately.
    if printf '%s' "$prompt" | grep -Eiq '(turn|switch) (the )?(learning|teaching) back on|resume (the )?(learning|teaching)|teach me again'; then
      rm -f "$optout_flag"
      emit UserPromptSubmit "learning-loop: the user turned learning back on. Use the learning-loop skill again from here."
      exit 0
    fi
    if printf '%s' "$prompt" | grep -Eiq '(^|[^a-z])(just do it|skip the learning|skip the teaching|no teaching|no quizzes|stop teaching|stop the lessons)([^a-z]|$)'; then
      : > "$optout_flag"
      emit UserPromptSubmit "learning-loop: the user opted out of teaching for the rest of this session. Do the work without learning moments. Still end each substantive task with a one-line recap and a single one-line offer to go deeper; don't argue or repeat the offer."
      exit 0
    fi
    optedout=0; [ -f "$optout_flag" ] && optedout=1

    if [ "$optedout" = 0 ] && printf '%s' "$prompt" | grep -Eiq '(^|[^a-z])(why|how does|how do|how is|what does .{0,40} mean|explain|explanation|walk (me )?through|go over|break (it|this|that) down|help me understand|teach me|traceback|stack ?trace|exception|errors?|fail(s|ed|ing|ure)?|broke|broken|crash(es|ed|ing)?|panic|segfault|exit code|non-zero exit|timed? ?out)([^a-z]|$)'; then
      emit UserPromptSubmit "learning-loop: this prompt asks why or how something works, or reports an error or failure. Use the learning-loop skill, and end with its short close."
    elif printf '%s' "$prompt" | grep -Eiq '(^|[^a-z])(that fixed it|works now|thanks|thank you|we.re done|ship it|lgtm|merged|close the ticket|open (a |the )?prs?|push (it|the branch|both|the branches)|commit (it|this|the changes)|complete (this|the) (ticket|story|task)|finish (this|the) (ticket|story|task))([^a-z]|$)'; then
      # Wrap-up nudges still fire after an opt-out: the end-of-task offer is the one thing that always remains.
      if [ "$optedout" = 1 ]; then
        emit UserPromptSubmit "learning-loop: wrap-up, and the user opted out of teaching this session. Skip any lesson, but still close with a one-line recap and, if something non-obvious was figured out, a single one-line offer to capture it with the knowledge-handoff skill."
      else
        emit UserPromptSubmit "learning-loop: this looks like wrap-up or a request to finish work. Run the learning-loop Completion check on the change before you report it done. If something non-obvious was figured out, use the knowledge-handoff skill and make one specific offer to capture it. If many people will need it, offer a frontend-slides lesson deck instead (knowledge-handoff step 1a)."
      fi
    fi
    ;;
esac
exit 0
