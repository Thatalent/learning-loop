#!/usr/bin/env python3
"""Learning judge: decides whether finished work needs a learning-loop debrief and a knowledge handoff.

The prompt nudges (learning-loop-nudge.sh) react to the words in a prompt ("why", "explain",
"error"). A request like "complete this ticket" has none of those words, so a change that moves a
business rule and the data behind it could ship with no debrief. This judge looks at the change.

It runs as the plugin's Stop hook (hooks/hooks.json) and as a CLI:

    python3 scripts/learning_judge.py hook                    # Stop hook: JSON on stdin
    python3 scripts/learning_judge.py report [--repo DIR] [--base REF] [--head REF] [--json]

The judge:
  1. Diffs the branch against its merge base with the default branch (committed, staged,
     unstaged and untracked work).
  2. Measures how much work was done (files, changed lines, test files).
  3. Matches the changed lines against rules. A repo can ship its own rule map at
     <repo>/.claude/learning-judge.json (rules that name its real downstream consumers). Without
     one, the generic rules in scripts/learning-judge.default.json apply. A rule names a kind of
     signal (business_rule, data_impact, contract, operational), why it matters, and the
     downstream chain that the change reaches.
  4. Picks a verdict: none, learn, or learn_and_handoff. A business rule change that also
     changes data or a contract gets learn_and_handoff: the engineer must understand the
     downstream effect, and the knowledge handoff gets a diagram of it.

As a Stop hook it blocks the stop once for each new set of signals, until the session has
used the learning-loop skill (and knowledge-handoff, when the verdict asks for it) after the
first edit. It never blocks twice for the same signals, never blocks when the transcript shows
no edits, and fails open: any error exits 0 so the session is never stuck. A repo needs nothing
for this to work; a rule map only sharpens the downstream chains.

Turn it off with LEARNING_JUDGE=off or LEARNING_LOOP_NUDGES=off. An opt-out in the session
("just do it", "skip the learning") turns the debrief into a one-line recap and offer.
Standard library only, Python 3.8+.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RULES_PATH = SCRIPT_DIR / "learning-judge.default.json"
REPO_CONFIG = Path(".claude") / "learning-judge.json"

VERDICT_NONE = "none"
VERDICT_LEARN = "learn"
VERDICT_LEARN_AND_HANDOFF = "learn_and_handoff"

LEARNING_KINDS = ("business_rule", "data_impact", "contract")
# Untracked files larger than this are build output or data, not hand-written changes.
MAX_UNTRACKED_BYTES = 512 * 1024

MODIFYING_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
# Bash commands that write files or history. Edits made through a shell (sed -i, a heredoc
# script, a redirect) count as work just like the Edit tool.
WRITE_BASH = re.compile(
    r"\bgit\s+(commit|merge|rebase|cherry-pick|apply|am|revert)\b"
    r"|\bsed\s+-i"
    r"|\btee\b"
    r"|(?<![0-9&>])>{1,2}\s*(?!/dev/null)[^\s&|>]"
    r"|\bpython3?\s+-\s*<<"
    r"|\bspotlessApply\b"
)
# Same phrases as the learning-loop plugin's nudge script, so both agree on an opt-out.
OPT_OUT = re.compile(
    r"(^|[^a-z])(just do it|skip the learning|skip the teaching|no teaching|no quizzes|"
    r"stop teaching|stop the lessons)([^a-z]|$)",
    re.IGNORECASE,
)
OPT_IN = re.compile(
    r"(turn|switch) (the )?(learning|teaching) back on|resume (the )?(learning|teaching)|teach me again",
    re.IGNORECASE,
)

DEFAULT_CONFIG = {
    "base_refs": ["origin/main", "origin/master", "main", "master"],
    "test_paths": ["**/tests/**", "**/test/**", "src/test/**", "**/test_*.py", "**/*_test.py", "**/*Test.java"],
    "ignore_paths": [".claude/**"],
    "size_thresholds": {"medium": 150, "large": 600},
    "max_evidence_per_rule": 3,
    "rules": [],
}


# ---- config -----------------------------------------------------------------------------------

def config_path_for(repo):
    """The repo's own rule map if it has one, else the plugin's generic rules."""
    repo_config = Path(repo) / REPO_CONFIG
    return repo_config if repo_config.is_file() else DEFAULT_RULES_PATH


def load_config(path=None):
    config = dict(DEFAULT_CONFIG)
    config_path = Path(path) if path else DEFAULT_RULES_PATH
    if config_path.is_file():
        with config_path.open() as handle:
            config.update(json.load(handle))
    if config.get("include_default_rules") and config_path != DEFAULT_RULES_PATH:
        # A repo map can keep the generic rules and add its own on top.
        with DEFAULT_RULES_PATH.open() as handle:
            config["rules"] = config["rules"] + json.load(handle)["rules"]
    for rule in config["rules"]:
        rule["_paths"] = [glob_to_regex(p) for p in rule.get("paths", ["**"])]
        rule["_exclude"] = [glob_to_regex(p) for p in rule.get("exclude_paths", [])]
        rule["_patterns"] = [re.compile(p) for p in rule.get("patterns", [])]
    config["_test"] = [glob_to_regex(p) for p in config["test_paths"]]
    config["_ignore"] = [glob_to_regex(p) for p in config["ignore_paths"]]
    config["_source"] = str(config_path)
    return config


def glob_to_regex(glob):
    """Converts a path glob to a regex. ** spans directories, * and ? stay inside one segment."""
    out = []
    i = 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif glob.startswith("**", i):
            out.append(".*")
            i += 2
        elif glob[i] == "*":
            out.append("[^/]*")
            i += 1
        elif glob[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(glob[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(path, regexes):
    return any(r.match(path) for r in regexes)


# ---- git --------------------------------------------------------------------------------------

def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo)] + list(args), capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), result.stderr.strip()))
    return result.stdout


def ref_exists(repo, ref):
    try:
        git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
        return True
    except RuntimeError:
        return False


def origin_default_branch(repo):
    """origin's default branch (refs/remotes/origin/HEAD), e.g. "origin/main", or None."""
    try:
        ref = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD").strip()
    except RuntimeError:
        return None
    return ref[len("refs/remotes/"):] if ref.startswith("refs/remotes/") else None


def resolve_base(repo, config, base=None, head="HEAD"):
    """Returns the merge base of head with the repo's default branch.

    Uses origin's own default branch when git knows it, then the configured candidates.
    """
    if base:
        candidates = [base]
    else:
        candidates = [origin_default_branch(repo)] + list(config["base_refs"])
        candidates = [c for i, c in enumerate(candidates) if c and c not in candidates[:i]]
    for ref in candidates:
        if ref and ref_exists(repo, ref):
            return git(repo, "merge-base", ref, head).strip(), ref
    raise RuntimeError("no base ref found among %s" % candidates)


def collect_changes(repo, config, base=None, head=None):
    """Returns {path: {"added": [(line_no, text)], "removed": [text]}} for the branch's work.

    Without head, the diff runs from the merge base to the working tree, so it includes commits,
    staged and unstaged edits, plus untracked files. With head, it covers only committed work.
    """
    merge_base, base_ref = resolve_base(repo, config, base, head or "HEAD")
    args = ["diff", "--unified=0", "--no-color", "--no-ext-diff", merge_base]
    if head:
        args.append(head)
    changes = parse_unified_diff(git(repo, *args))
    if not head:
        for path in git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
            full = Path(repo) / path
            try:
                if full.stat().st_size > MAX_UNTRACKED_BYTES:
                    continue
                lines = full.read_text(errors="replace").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            changes[path] = {"added": list(enumerate(lines, start=1)), "removed": []}
    changes = {p: c for p, c in changes.items() if not matches_any(p, config["_ignore"])}
    return changes, base_ref


def parse_unified_diff(text):
    """Parses `git diff --unified=0` output into added (with new line numbers) and removed lines.

    File headers (---/+++) are read only before the first hunk of each file. Inside a hunk, a
    removed line that itself starts with "--" (a SQL comment, for example) shows as "--- ..." and
    must stay a removed line.
    """
    changes = {}
    current = None
    in_header = False
    new_line = 0
    for line in text.splitlines():
        if line.startswith("diff --git"):
            current = None
            in_header = True
        elif in_header and line.startswith("--- "):
            old = line[4:]
            if old != "/dev/null":
                # A deleted file has "+++ /dev/null" next; its removed lines stay under this path.
                current = changes.setdefault(old[2:] if old.startswith("a/") else old,
                                             {"added": [], "removed": []})
        elif in_header and line.startswith("+++ "):
            path = line[4:]
            if path != "/dev/null":
                current = changes.setdefault(path[2:] if path.startswith("b/") else path,
                                             {"added": [], "removed": []})
        elif line.startswith("@@"):
            in_header = False
            match = re.search(r"\+(\d+)", line)
            new_line = int(match.group(1)) if match else 0
        elif in_header or current is None:
            continue
        elif line.startswith("+"):
            current["added"].append((new_line, line[1:]))
            new_line += 1
        elif line.startswith("-"):
            current["removed"].append(line[1:])
    return {p: c for p, c in changes.items() if c["added"] or c["removed"]}


# ---- judging ----------------------------------------------------------------------------------

def measure_effort(changes, config):
    test_files = [p for p in changes if matches_any(p, config["_test"])]
    lines = sum(len(c["added"]) + len(c["removed"]) for c in changes.values())
    test_lines = sum(len(changes[p]["added"]) + len(changes[p]["removed"]) for p in test_files)
    code_lines = lines - test_lines
    thresholds = config["size_thresholds"]
    if code_lines >= thresholds["large"]:
        tier = "large"
    elif code_lines >= thresholds["medium"]:
        tier = "medium"
    else:
        tier = "small"
    return {
        "files": len(changes),
        "test_files": len(test_files),
        "added": sum(len(c["added"]) for c in changes.values()),
        "removed": sum(len(c["removed"]) for c in changes.values()),
        "code_lines": code_lines,
        "tier": tier,
    }


def find_signals(changes, config):
    signals = []
    limit = config["max_evidence_per_rule"]
    for rule in config["rules"]:
        evidence = []
        files = []
        for path in sorted(changes):
            if not matches_any(path, rule["_paths"]) or matches_any(path, rule["_exclude"]):
                continue
            if matches_any(path, config["_test"]) and not rule.get("include_tests", False):
                continue
            change = changes[path]
            # A line that only moved or gained a trailing comma is not a change in behavior.
            added_keys = {normalize(text) for _, text in change["added"]}
            removed_keys = {normalize(text) for text in change["removed"]}
            hits = []
            for line_no, text in change["added"]:
                rank = match_rank(rule["_patterns"], text)
                if rank is not None and normalize(text) not in removed_keys and normalize(text):
                    hits.append(((is_comment(text), rank), "%s:%s  + %s" % (path, line_no, text.strip()[:140])))
            for text in change["removed"]:
                rank = match_rank(rule["_patterns"], text)
                if rank is not None and normalize(text) not in added_keys and normalize(text):
                    hits.append(((is_comment(text), rank), "%s  - %s" % (path, text.strip()[:140])))
            if hits:
                files.append(path)
                evidence.extend(hits)
        # Code before comments, then by the first pattern that matched: a rule lists its most
        # specific pattern first, so those lines show the behavior change best.
        evidence = [text for _, text in sorted(evidence, key=lambda hit: hit[0])]
        if files:
            signals.append({
                "id": rule["id"],
                "kind": rule["kind"],
                "title": rule["title"],
                "why": rule.get("why", ""),
                "downstream": rule.get("downstream", []),
                "learn": rule.get("learn", ""),
                "generic": bool(rule.get("generic", False)),
                "files": files,
                "evidence": evidence[:limit],
                "evidence_total": len(evidence),
            })
    return signals


def match_rank(patterns, text):
    """Index of the first pattern that matches text, 0 when the rule has no patterns, else None."""
    if not patterns:
        return 0
    for index, pattern in enumerate(patterns):
        if pattern.search(text):
            return index
    return None


def normalize(text):
    return re.sub(r"\s+", " ", text.strip().rstrip(",;"))


def is_comment(text):
    return text.strip().startswith(("#", "//", "*", "/*", "--", "<!--"))


def decide(signals, effort):
    kinds = {s["kind"] for s in signals}
    if "business_rule" in kinds and kinds & {"data_impact", "contract"}:
        return VERDICT_LEARN_AND_HANDOFF
    if {"data_impact", "contract"} <= kinds:
        return VERDICT_LEARN_AND_HANDOFF
    if kinds & set(LEARNING_KINDS):
        return VERDICT_LEARN
    if effort["tier"] == "large" or ("operational" in kinds and effort["tier"] != "small"):
        return VERDICT_LEARN
    return VERDICT_NONE


def judge(repo, config, base=None, head=None):
    changes, base_ref = collect_changes(repo, config, base, head)
    effort = measure_effort(changes, config)
    signals = find_signals(changes, config)
    return {
        "verdict": decide(signals, effort),
        "base": base_ref,
        "effort": effort,
        "signals": signals,
        "diagram": build_mermaid(signals),
        "rules": config.get("_source", ""),
    }


def build_mermaid(signals):
    """A flowchart skeleton from each signal's changed area to its downstream consumers."""
    if not any(s["downstream"] for s in signals):
        return ""
    lines = ["flowchart LR"]
    ids = {}

    def node(label):
        if label not in ids:
            ids[label] = "n%d" % len(ids)
            safe = label.replace('"', "'").replace("<", "#lt;").replace(">", "#gt;")
            lines.append('  %s["%s"]' % (ids[label], safe))
        return ids[label]

    edges = set()
    changed = []
    for signal in signals:
        if not signal["downstream"]:
            continue
        source = node("CHANGED: %s (%s)" % (signal["title"], signal["kind"]))
        changed.append(source)
        previous = source
        for step in signal["downstream"]:
            current = node(step)
            if (previous, current) not in edges:
                edges.add((previous, current))
                lines.append("  %s --> %s" % (previous, current))
            previous = current
    lines.append("  classDef changed fill:#fde68a,stroke:#b45309,color:#111")
    lines.append("  class %s changed" % ",".join(changed))
    return "\n".join(lines)


# ---- transcript -------------------------------------------------------------------------------

def read_transcript(path):
    entries = []
    if not path or not os.path.isfile(path):
        return entries
    with open(path, errors="replace") as handle:
        for raw in handle:
            try:
                entries.append(json.loads(raw))
            except ValueError:
                continue
    return entries


def content_items(entry):
    message = entry.get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


def scan_transcript(entries):
    """Returns where the session first edited, which skills it loaded and when, and opt-out state."""
    first_edit = None
    skills = []
    opted_out = False
    for index, entry in enumerate(entries):
        kind = entry.get("type")
        for item in content_items(entry):
            if not isinstance(item, dict):
                continue
            if kind == "assistant" and item.get("type") == "tool_use":
                name = item.get("name", "")
                tool_input = item.get("input") or {}
                if name in MODIFYING_TOOLS or (
                        name == "Bash" and WRITE_BASH.search(tool_input.get("command", ""))):
                    if first_edit is None:
                        first_edit = index
                elif name == "Skill":
                    skills.append((index, str(tool_input.get("skill", ""))))
            elif kind == "user" and item.get("type") == "text":
                text = item.get("text", "")
                if OPT_IN.search(text):
                    opted_out = False
                elif OPT_OUT.search(text):
                    opted_out = True
    return {"first_edit": first_edit, "skills": skills, "opted_out": opted_out, "end": len(entries)}


def skill_used_since(skills, name, since):
    return any(index >= since and (s == name or s.endswith(":" + name)) for index, s in skills)


# ---- hook -------------------------------------------------------------------------------------

def required_skills(verdict):
    if verdict == VERDICT_LEARN_AND_HANDOFF:
        return ["learning-loop", "knowledge-handoff"]
    if verdict == VERDICT_LEARN:
        return ["learning-loop"]
    return []


def state_path(repo, session_id):
    git_dir = Path(git(repo, "rev-parse", "--absolute-git-dir").strip())
    safe = re.sub(r"[^A-Za-z0-9_-]", "", session_id or "unknown") or "unknown"
    return git_dir / "learning-judge" / (safe + ".json")


def load_state(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


VERDICT_RANK = {VERDICT_NONE: 0, VERDICT_LEARN: 1, VERDICT_LEARN_AND_HANDOFF: 2}


def fingerprint(verdict, signals):
    key = verdict + "|" + ",".join(sorted(s["id"] for s in signals))
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def decide_hook(result, scan, state, optout_flag=False):
    """Returns (block_reason_or_None, new_state). Pure, so it can be unit tested.

    state keeps what this session already covered:
      ack_signals / ack_verdict / ack_index: the signals and verdict the session's skill use
        covered, and the transcript position after which a new skill use counts again.
      blocked_fingerprint: the last verdict+signals this hook blocked on, so it blocks once.
    """
    verdict = result["verdict"]
    if verdict == VERDICT_NONE or scan["first_edit"] is None:
        return None, state
    since = state.get("ack_index", scan["first_edit"])
    if all(skill_used_since(scan["skills"], name, since) for name in required_skills(verdict)):
        acknowledged = set(state.get("ack_signals", [])) | {s["id"] for s in result["signals"]}
        top = max(verdict, state.get("ack_verdict", VERDICT_NONE), key=VERDICT_RANK.get)
        return None, dict(state, ack_signals=sorted(acknowledged), ack_verdict=top,
                          ack_index=scan["end"])
    if "ack_verdict" in state:
        new_signals = [s for s in result["signals"] if s["id"] not in set(state["ack_signals"])]
        escalated = VERDICT_RANK[verdict] > VERDICT_RANK[state["ack_verdict"]]
        if not new_signals and not escalated:
            return None, state
    current = fingerprint(verdict, result["signals"])
    if state.get("blocked_fingerprint") == current:
        return None, state
    reason = render_reason(result, opted_out=scan["opted_out"] or optout_flag)
    return reason, dict(state, blocked_fingerprint=current)


def run_hook(stdin_text):
    if os.environ.get("LEARNING_JUDGE", "on") == "off" or os.environ.get("LEARNING_LOOP_NUDGES", "on") == "off":
        return None
    payload = json.loads(stdin_text or "{}")
    if payload.get("stop_hook_active"):
        return None
    repo = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    repo = git(repo, "rev-parse", "--show-toplevel").strip()
    config = load_config(config_path_for(repo))
    result = judge(repo, config)
    scan = scan_transcript(read_transcript(payload.get("transcript_path")))
    session_id = payload.get("session_id", "")
    optout_flag = os.path.exists(os.path.join(
        os.environ.get("TMPDIR", "/tmp"), "learning-loop-optout-" + re.sub(r"[^A-Za-z0-9_-]", "", session_id)))
    path = state_path(repo, session_id)
    reason, new_state = decide_hook(result, scan, load_state(path), optout_flag)
    if new_state:
        save_state(path, new_state)
    if reason:
        return {"decision": "block", "reason": reason}
    return None


# ---- output -----------------------------------------------------------------------------------

def render_summary(result):
    effort = result["effort"]
    lines = [
        "Verdict: %s" % result["verdict"],
        "Work: %d files (%d test), +%d/-%d lines, %d non-test lines changed (%s) vs %s." % (
            effort["files"], effort["test_files"], effort["added"], effort["removed"],
            effort["code_lines"], effort["tier"], result["base"]),
    ]
    if result.get("rules"):
        lines.append("Rules: %s" % result["rules"])
    if result["signals"]:
        lines.append("Signals:")
    for signal in result["signals"]:
        lines.append("- [%s] %s (%d changed line(s) in %d file(s))" % (
            signal["kind"], signal["title"], signal["evidence_total"], len(signal["files"])))
        if signal["why"]:
            lines.append("  Why it matters: %s" % signal["why"])
        for item in signal["evidence"]:
            lines.append("    %s" % item)
        if signal["downstream"]:
            lines.append("  Downstream: %s" % " -> ".join(signal["downstream"]))
        if signal["learn"]:
            lines.append("  Engineer should be able to: %s" % signal["learn"])
    return "\n".join(lines)


def render_reason(result, opted_out=False):
    summary = render_summary(result)
    header = ("Learning judge (learning-loop plugin): this change moves things other "
              "people and systems depend on, so the engineer should understand it before you finish.")
    if opted_out:
        return "\n\n".join([
            header, summary,
            "The user opted out of teaching this session. Do not teach. Close with one line on what "
            "changed downstream (use the Downstream chain above) and one line offering a "
            "knowledge-handoff doc with a diagram of it. Then stop.",
        ])
    steps = [
        "Do this now, before you finish:",
        "1. Load the learning-loop skill. Set the Bloom goal to %s. Ask the engineer ONE "
        "predict-first question about the downstream effect of this change (for example: what "
        "changes for the last consumer in the Downstream chain, and when will it show?). Then end "
        "your turn and wait for the answer; confirm or correct it with a why-line next turn." % (
            "Analyze (trace the downstream effect and predict what consumers will see)"
            if result["verdict"] == VERDICT_LEARN_AND_HANDOFF
            else "Understand (explain what changed and why)"),
    ]
    if result["verdict"] == VERDICT_LEARN_AND_HANDOFF:
        steps.append(
            "2. Load the knowledge-handoff skill and make ONE specific offer: an explainer of this "
            "change built around a before/after diagram of the data flow. Start from the mermaid "
            "skeleton below, mark what changed (rule, window, row shape, contract) on the edges, "
            "and add the deploy order and what to watch after release.")
    if any(s.get("generic") for s in result["signals"]):
        steps.append("The downstream chain above is generic: this repo has no .claude/learning-judge.json "
                     "yet. Before you teach or draw, find the real consumers of what changed (search for "
                     "readers of the changed config key, column, path or field) and use their names. "
                     "Offer to save them as rules in .claude/learning-judge.json so the next change is "
                     "judged with them.")
    steps.append("Size the debrief to the work: skip anything the engineer already showed they know. "
                 "If they say \"just do it\" or \"skip the learning\", stop teaching and give a "
                 "one-line recap instead.")
    parts = [header, summary, "\n".join(steps)]
    if result["diagram"] and result["verdict"] == VERDICT_LEARN_AND_HANDOFF:
        parts.append("Diagram skeleton:\n```mermaid\n%s\n```" % result["diagram"])
    return "\n\n".join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hook", help="run as a Claude Code Stop hook (JSON on stdin)")
    report = sub.add_parser("report", help="print the verdict for the current branch")
    report.add_argument("--repo", default=os.getcwd())
    report.add_argument("--base", help="base ref (default: first of config base_refs)")
    report.add_argument("--head", help="head ref; omit to include uncommitted work")
    report.add_argument("--config", help="rules path (default: <repo>/.claude/learning-judge.json, "
                                         "else the plugin's generic rules)")
    report.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "hook":
        try:
            output = run_hook(sys.stdin.read())
        except Exception as error:  # fail open: a judge bug must never trap the session
            print("learning_judge: skipped (%s)" % error, file=sys.stderr)
            return 0
        if output:
            print(json.dumps(output))
        return 0

    repo = git(args.repo, "rev-parse", "--show-toplevel").strip()
    result = judge(repo, load_config(args.config or config_path_for(repo)), args.base, args.head)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_summary(result))
        if result["diagram"]:
            print("\n```mermaid\n%s\n```" % result["diagram"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
