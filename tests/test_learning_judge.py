"""Tests for scripts/learning_judge.py. Run from the repo root: python3 -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import learning_judge as lj  # noqa: E402

RULES = {
    "base_refs": ["main"],
    "test_paths": ["**/tests/**"],
    "ignore_paths": [".claude/**"],
    "size_thresholds": {"medium": 150, "large": 600},
    "rules": [
        {"id": "window", "kind": "business_rule", "title": "Export window", "paths": ["app/**"],
         "patterns": ["(?i)lookback"], "downstream": ["export file", "rollup", "dashboard total"]},
        {"id": "rows", "kind": "data_impact", "title": "Row shape", "paths": ["app/**"],
         "patterns": ["(?i)starttime"], "downstream": ["export file"]},
        {"id": "api", "kind": "contract", "title": "API field", "paths": ["app/dto/**"],
         "patterns": ["private "]},
        {"id": "cfg", "kind": "business_rule", "title": "Any config", "paths": ["config/**"]},
    ],
}


def config(rules=None):
    path = Path(tempfile.mkdtemp()) / "learning-judge.json"
    path.write_text(json.dumps(dict(RULES, rules=rules if rules is not None else RULES["rules"])))
    return lj.load_config(path)


def result_for(verdict, *ids):
    signals = [{"id": i, "kind": "business_rule", "title": i, "why": "", "downstream": ["x"], "learn": "",
                "files": ["f"], "evidence": [], "evidence_total": 1} for i in ids]
    return {"verdict": verdict, "base": "main", "signals": signals, "diagram": "",
            "effort": {"files": 1, "test_files": 0, "added": 1, "removed": 0, "code_lines": 1, "tier": "small"}}


def scan(first_edit=0, skills=(), opted_out=False, end=10):
    return {"first_edit": first_edit, "skills": list(skills), "opted_out": opted_out, "end": end}


class GlobTest(unittest.TestCase):
    def test_double_star_spans_directories_and_matches_root(self):
        regex = lj.glob_to_regex("**/tests/**")
        self.assertTrue(regex.match("tests/a.py"))
        self.assertTrue(regex.match("python_lambdas/x/tests/test_a.py"))
        self.assertFalse(regex.match("python_lambdas/x/a.py"))

    def test_single_star_stays_in_one_segment(self):
        regex = lj.glob_to_regex("pipelines/*/config/**")
        self.assertTrue(regex.match("pipelines/nightly-refresh/config/steps.json"))
        self.assertFalse(regex.match("pipelines/a/b/config/steps.json"))


class ParseDiffTest(unittest.TestCase):
    def test_reads_added_line_numbers_and_removed_lines(self):
        diff = "\n".join([
            "diff --git a/app/x.py b/app/x.py", "--- a/app/x.py", "+++ b/app/x.py",
            "@@ -3 +3,2 @@", "-old = 1", "+new = 2", "+other = 3",
        ])
        expected = {"app/x.py": {"added": [(3, "new = 2"), (4, "other = 3")], "removed": ["old = 1"]}}
        self.assertEqual(lj.parse_unified_diff(diff), expected)

    def test_removed_sql_comment_is_not_a_file_header(self):
        diff = "\n".join([
            "diff --git a/q.sql b/q.sql", "--- a/q.sql", "+++ b/q.sql",
            "@@ -1 +1 @@", "--- lookback is 7 days", "+-- lookback is N days",
        ])
        self.assertEqual(lj.parse_unified_diff(diff)["q.sql"]["removed"], ["-- lookback is 7 days"])

    def test_deleted_file_keeps_its_removed_lines(self):
        diff = "\n".join([
            "diff --git a/config/a.json b/config/a.json", "deleted file mode 100644",
            "--- a/config/a.json", "+++ /dev/null", "@@ -1 +0,0 @@", '-{"days": 7}',
        ])
        self.assertEqual(lj.parse_unified_diff(diff), {"config/a.json": {"added": [], "removed": ['{"days": 7}']}})


class SignalsAndVerdictTest(unittest.TestCase):
    def test_business_rule_plus_data_impact_needs_handoff(self):
        added = [(1, "lookback_days = job['LookbackDays']"), (2, "payload['starttime'] = refresh_time")]
        changes = {"app/export.py": {"added": added, "removed": []}}
        cfg = config()
        signals = lj.find_signals(changes, cfg)
        self.assertEqual({s["id"] for s in signals}, {"window", "rows"})
        self.assertEqual(lj.decide(signals, lj.measure_effort(changes, cfg)), lj.VERDICT_LEARN_AND_HANDOFF)

    def test_business_rule_alone_needs_learning_only(self):
        signals = [{"kind": "business_rule"}]
        self.assertEqual(lj.decide(signals, {"tier": "small"}), lj.VERDICT_LEARN)

    def test_data_impact_plus_contract_needs_handoff(self):
        self.assertEqual(lj.decide([{"kind": "data_impact"}, {"kind": "contract"}], {"tier": "small"}),
                         lj.VERDICT_LEARN_AND_HANDOFF)

    def test_small_change_without_signals_needs_nothing(self):
        self.assertEqual(lj.decide([], {"tier": "small"}), lj.VERDICT_NONE)

    def test_large_change_without_signals_still_needs_learning(self):
        self.assertEqual(lj.decide([], {"tier": "large"}), lj.VERDICT_LEARN)

    def test_operational_alone_needs_learning_only_when_not_small(self):
        self.assertEqual(lj.decide([{"kind": "operational"}], {"tier": "small"}), lj.VERDICT_NONE)
        self.assertEqual(lj.decide([{"kind": "operational"}], {"tier": "medium"}), lj.VERDICT_LEARN)

    def test_reformatted_line_is_not_evidence(self):
        changes = {"app/x.py": {"added": [(5, "  lookback: 1,")], "removed": ["lookback: 1"]}}
        self.assertEqual(lj.find_signals(changes, config()), [])

    def test_tests_do_not_count_as_signals_or_code_lines(self):
        changes = {"app/tests/test_x.py": {"added": [(1, "lookback = 3")] * 200, "removed": []}}
        cfg = config()
        self.assertEqual(lj.find_signals(changes, cfg), [])
        self.assertEqual(lj.measure_effort(changes, cfg)["code_lines"], 0)

    def test_evidence_lists_first_pattern_hits_before_later_ones_and_comments(self):
        rules = [{"id": "r", "kind": "data_impact", "title": "t", "paths": ["app/**"],
                  "patterns": ["starttime", "log"]}]
        changes = {"app/a.py": {"added": [(1, "log.info(x)"), (2, "# starttime note"), (3, "sql = 'starttime'")],
                                "removed": []}}
        evidence = lj.find_signals(changes, config(rules))[0]["evidence"]
        self.assertEqual([e.split(":")[1].split()[0] for e in evidence], ["3", "1", "2"])

    def test_rule_without_patterns_matches_any_changed_line(self):
        changes = {"config/prod.json": {"added": [], "removed": ['"window": 7']}}
        self.assertEqual([s["id"] for s in lj.find_signals(changes, config())], ["cfg"])

    def test_mermaid_marks_changed_nodes_and_escapes_angle_brackets(self):
        signals = [{"title": "Window", "kind": "business_rule", "downstream": ["storage <date>/file", "rollup"]}]
        diagram = lj.build_mermaid(signals)
        self.assertIn("flowchart LR", diagram)
        self.assertIn("#lt;date#gt;", diagram)
        self.assertIn("class n0 changed", diagram)


class TranscriptTest(unittest.TestCase):
    def entries(self, *items):
        return [{"type": t, "message": {"content": c}} for t, c in items]

    def test_finds_first_edit_and_skills(self):
        entries = self.entries(
            ("user", "complete this ticket"),
            ("assistant", [{"type": "tool_use", "name": "Read", "input": {}}]),
            ("assistant", [{"type": "tool_use", "name": "Edit", "input": {}}]),
            ("assistant", [{"type": "tool_use", "name": "Skill",
                            "input": {"skill": "anthropic-skills:learning-loop"}}]),
        )
        result = lj.scan_transcript(entries)
        self.assertEqual(result["first_edit"], 2)
        self.assertTrue(lj.skill_used_since(result["skills"], "learning-loop", 2))
        self.assertFalse(lj.skill_used_since(result["skills"], "knowledge-handoff", 0))

    def test_shell_edits_count_and_reads_do_not(self):
        read = self.entries(("assistant", [{"type": "tool_use", "name": "Bash",
                                            "input": {"command": "git diff 2>/dev/null | head"}}]))
        self.assertIsNone(lj.scan_transcript(read)["first_edit"])
        for command in ("python3 - <<'EOF'\nopen('x','w')\nEOF", "sed -i '' s/a/b/ f", "git commit -m x",
                        "echo hi > notes.txt"):
            entries = self.entries(("assistant", [{"type": "tool_use", "name": "Bash", "input": {"command": command}}]))
            self.assertEqual(lj.scan_transcript(entries)["first_edit"], 0, command)

    def test_latest_opt_out_or_opt_in_wins(self):
        out = self.entries(("user", "just do it"))
        self.assertTrue(lj.scan_transcript(out)["opted_out"])
        back = self.entries(("user", "skip the learning"), ("user", "turn learning back on"))
        self.assertFalse(lj.scan_transcript(back)["opted_out"])


class DecideHookTest(unittest.TestCase):
    def test_no_edit_in_session_never_blocks(self):
        reason, _ = lj.decide_hook(result_for(lj.VERDICT_LEARN, "a"), scan(first_edit=None), {})
        self.assertIsNone(reason)

    def test_blocks_once_then_lets_the_session_stop(self):
        result = result_for(lj.VERDICT_LEARN_AND_HANDOFF, "a")
        reason, state = lj.decide_hook(result, scan(), {})
        self.assertIn("learning-loop", reason)
        self.assertIn("knowledge-handoff", reason)
        reason, _ = lj.decide_hook(result, scan(), state)
        self.assertIsNone(reason)

    def test_skill_use_after_first_edit_acknowledges(self):
        result = result_for(lj.VERDICT_LEARN, "a")
        reason, state = lj.decide_hook(result, scan(first_edit=3, skills=[(5, "learning-loop:learning-loop")]), {})
        self.assertIsNone(reason)
        self.assertEqual(state["ack_signals"], ["a"])
        self.assertEqual(state["ack_index"], 10)

    def test_skill_use_before_first_edit_does_not_count(self):
        result = result_for(lj.VERDICT_LEARN, "a")
        reason, _ = lj.decide_hook(result, scan(first_edit=3, skills=[(1, "learning-loop")]), {})
        self.assertIsNotNone(reason)

    def test_handoff_verdict_needs_both_skills(self):
        result = result_for(lj.VERDICT_LEARN_AND_HANDOFF, "a")
        reason, _ = lj.decide_hook(result, scan(skills=[(1, "learning-loop")]), {})
        self.assertIsNotNone(reason)

    def test_new_signal_after_acknowledgment_blocks_again(self):
        _, state = lj.decide_hook(result_for(lj.VERDICT_LEARN, "a"), scan(skills=[(1, "learning-loop")]), {})
        later = scan(end=20, skills=[(1, "learning-loop")])
        reason, _ = lj.decide_hook(result_for(lj.VERDICT_LEARN, "a", "b"), later, state)
        self.assertIsNotNone(reason)

    def test_same_signals_after_acknowledgment_do_not_block(self):
        _, state = lj.decide_hook(result_for(lj.VERDICT_LEARN, "a"), scan(skills=[(1, "learning-loop")]), {})
        later = scan(end=20, skills=[(1, "learning-loop")])
        reason, _ = lj.decide_hook(result_for(lj.VERDICT_LEARN, "a"), later, state)
        self.assertIsNone(reason)

    def test_escalation_to_handoff_blocks_again(self):
        _, state = lj.decide_hook(result_for(lj.VERDICT_LEARN, "a"), scan(skills=[(1, "learning-loop")]), {})
        reason, _ = lj.decide_hook(result_for(lj.VERDICT_LEARN_AND_HANDOFF, "a"),
                                   scan(end=20, skills=[(1, "learning-loop")]), state)
        self.assertIn("knowledge-handoff", reason)

    def test_opt_out_asks_for_recap_only(self):
        reason, _ = lj.decide_hook(result_for(lj.VERDICT_LEARN_AND_HANDOFF, "a"), scan(opted_out=True), {})
        self.assertIn("Do not teach", reason)
        self.assertNotIn("predict-first", reason)


class RunHookTest(unittest.TestCase):
    """End to end against a throwaway git repo and transcript."""

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())

        def run(*args):
            subprocess.run(["git", "-C", str(self.repo)] + list(args), check=True, capture_output=True)

        run("init", "-q", "-b", "main")
        run("config", "user.email", "t@example.com")
        run("config", "user.name", "t")
        (self.repo / "app").mkdir()
        (self.repo / "app" / "export.py").write_text("LOOKBACK = 1\n")
        run("add", ".")
        run("commit", "-q", "-m", "base")
        run("checkout", "-q", "-b", "feature")
        (self.repo / "app" / "export.py").write_text("LOOKBACK = event_lookback\nstarttime = refresh_time\n")
        self.transcript = self.repo / "t.jsonl"
        self.transcript.write_text(json.dumps(
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit", "input": {}}]}}) + "\n")
        self.cfg = config()

    def hook(self, **extra):
        payload = dict({"session_id": "s1", "cwd": str(self.repo), "transcript_path": str(self.transcript)}, **extra)
        with mock.patch.object(lj, "load_config", return_value=self.cfg):
            return lj.run_hook(json.dumps(payload))

    def test_blocks_with_reason_then_allows_stop(self):
        first = self.hook()
        self.assertEqual(first["decision"], "block")
        self.assertIn("learn_and_handoff", first["reason"])
        self.assertIn("```mermaid", first["reason"])
        self.assertIsNone(self.hook())

    def test_stop_hook_active_never_blocks(self):
        self.assertIsNone(self.hook(stop_hook_active=True))

    def test_env_switch_turns_it_off(self):
        with mock.patch.dict(os.environ, {"LEARNING_JUDGE": "off"}):
            self.assertIsNone(self.hook())

    def test_cli_hook_fails_open(self):
        with mock.patch("sys.stdin") as stdin, mock.patch.object(lj, "run_hook", side_effect=RuntimeError("boom")):
            stdin.read.return_value = "{}"
            self.assertEqual(lj.main(["hook"]), 0)


class RulesLookupTest(unittest.TestCase):
    def repo(self, rules=None, include_defaults=False):
        root = Path(tempfile.mkdtemp())
        if rules is not None:
            (root / ".claude").mkdir()
            body = {"rules": rules}
            if include_defaults:
                body["include_default_rules"] = True
            (root / ".claude" / "learning-judge.json").write_text(json.dumps(body))
        return root

    def test_repo_without_a_rule_map_uses_the_plugin_defaults(self):
        self.assertEqual(lj.config_path_for(self.repo()), lj.DEFAULT_RULES_PATH)

    def test_repo_rule_map_replaces_the_defaults(self):
        repo = self.repo([{"id": "mine", "kind": "contract", "title": "t", "paths": ["**"]}])
        cfg = lj.load_config(lj.config_path_for(repo))
        self.assertEqual([r["id"] for r in cfg["rules"]], ["mine"])

    def test_repo_rule_map_can_keep_the_defaults(self):
        repo = self.repo([{"id": "mine", "kind": "contract", "title": "t", "paths": ["**"]}], include_defaults=True)
        ids = [r["id"] for r in lj.load_config(lj.config_path_for(repo))["rules"]]
        self.assertEqual(ids[0], "mine")
        self.assertIn("query-semantics", ids)

    def test_generic_signals_ask_for_the_real_consumers(self):
        result = result_for(lj.VERDICT_LEARN, "a")
        result["signals"][0]["generic"] = True
        self.assertIn("find the real consumers", lj.render_reason(result))

    def test_origin_default_branch_is_read_from_origin_head(self):
        with mock.patch.object(lj, "git", return_value="refs/remotes/origin/develop\n"):
            self.assertEqual(lj.origin_default_branch("."), "origin/develop")
        with mock.patch.object(lj, "git", side_effect=RuntimeError("no origin")):
            self.assertIsNone(lj.origin_default_branch("."))


class DefaultRulesTest(unittest.TestCase):
    def setUp(self):
        self.cfg = lj.load_config(lj.DEFAULT_RULES_PATH)

    def kinds(self, changes):
        return {s["kind"] for s in lj.find_signals(changes, self.cfg)}

    def test_every_default_rule_is_complete_and_generic(self):
        for rule in self.cfg["rules"]:
            for key in ("id", "kind", "title", "why", "downstream", "learn"):
                self.assertIn(key, rule, rule["id"])
            self.assertTrue(rule.get("generic"), rule["id"])
            self.assertIn(rule["kind"], ("business_rule", "data_impact", "contract", "operational"))

    def test_config_threshold_is_a_business_rule(self):
        changes = {"config/app.yml": {"added": [(4, "  lookback_days: 30")], "removed": ["  lookback_days: 7"]}}
        self.assertEqual(self.kinds(changes), {"business_rule"})

    def test_named_limit_constant_is_a_business_rule(self):
        changes = {"src/export.py": {"added": [(3, "MAX_LOOKBACK_DAYS = 90")], "removed": []}}
        self.assertEqual(self.kinds(changes), {"business_rule"})

    def test_sql_column_change_is_data_impact(self):
        changes = {"src/Repo.java": {"added": [(9, '+ " AS starttime,"')], "removed": []}}
        self.assertEqual(self.kinds(changes), {"data_impact"})

    def test_dto_field_is_a_contract(self):
        changes = {"src/main/java/x/web/dto/Request.java": {"added": [(5, "  private Instant refreshTime;")],
                                                            "removed": []}}
        self.assertEqual(self.kinds(changes), {"contract"})

    def test_business_rule_with_query_change_needs_handoff(self):
        changes = {"src/job.py": {"added": [(1, "DEFAULT_WINDOW_DAYS = 14"), (2, "sql = 'SELECT id FROM t'")],
                                  "removed": []}}
        signals = lj.find_signals(changes, self.cfg)
        self.assertEqual(lj.decide(signals, lj.measure_effort(changes, self.cfg)), lj.VERDICT_LEARN_AND_HANDOFF)

    def test_plain_refactor_and_s3_uri_in_a_message_are_not_signals(self):
        changes = {"src/gate.py": {"added": [(1, "def check(obj):"), (2, "    raise Bad('s3://%s/%s is late' % k)"),
                                             (3, "    return helper(obj)")], "removed": ["    return helper2(obj)"]}}
        self.assertEqual(lj.find_signals(changes, self.cfg), [])

    def test_lowercase_python_as_is_not_sql(self):
        changes = {"src/a.py": {"added": [(1, "import numpy as np"), (2, "with open(p) as handle:")], "removed": []}}
        self.assertEqual(lj.find_signals(changes, self.cfg), [])


if __name__ == "__main__":
    unittest.main()
