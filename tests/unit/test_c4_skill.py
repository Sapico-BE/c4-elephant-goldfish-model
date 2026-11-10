# SPDX-License-Identifier: Apache-2.0
"""Contracts for the egm-c4 orchestrator skill and its references."""

import json
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/egm-c4"
REFS = SKILL / "references"
ADAPTED = ("grilling.md", "domain-language.md", "c3-component.md")


def read(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def flat(path: Path) -> str:
  return " ".join(read(path).split())


def test_grilling_defines_rounds_and_decision_files() -> None:
  text = flat(REFS / "grilling.md")
  for phrase in ("<scope>.tree.md", "<scope>.answers.md", "append-only",
                 "`open`", "`decided`", "`deferred`", "frontier_empty",
                 "recommended answer", "look up", "Open Questions"):
    assert phrase in text, phrase


def test_domain_language_rules() -> None:
  text = flat(REFS / "domain-language.md")
  for phrase in ("GLOSSARY.md", "docs/adr/", "hard to reverse",
                 "surprising", "real trade-off"):
    assert phrase in text, phrase


@pytest.mark.parametrize("name", ADAPTED)
def test_adapted_reference_credits_mit_source(name: str) -> None:
  text = flat(REFS / name)
  assert "Adapted from mattpocock/skills" in text
  assert "MIT License" in text
  notices = flat(ROOT / "THIRD_PARTY_NOTICES.md")
  assert f"skills/egm-c4/references/{name}" in notices


def test_third_party_notice_carries_mit_text() -> None:
  notices = flat(ROOT / "THIRD_PARTY_NOTICES.md")
  assert "https://github.com/mattpocock/skills" in notices
  assert "Permission is hereby granted, free of charge" in notices


RESULT_FIELDS = {"task_id", "outcome", "files_written", "questions",
                 "frontier_empty", "contradictions", "new_tasks", "summary"}
OUTCOMES = {"complete", "needs_user", "blocked"}
QUESTION_FIELDS = {"number", "question", "recommendation", "decision"}
CONTRADICTION_FIELDS = {"document", "statement", "evidence"}
NEW_TASK_FIELDS = {"scope", "task", "depends_on", "reason"}
TASK_TYPES = ("grill", "draft", "revise", "readiness", "review", "approve",
              "implement", "merge", "verify", "code-review", "fix", "drift")
STATUSES = ("todo", "in-progress", "done", "blocked", "stale")
ROUND_TYPES = ("grill", "draft", "revise", "readiness", "resolve",
               "implement", "fix", "merge", "verify", "code-review", "drift")


def schema() -> dict:
  return json.loads(read(REFS / "round-result.schema.json"))


def test_round_result_schema_shape() -> None:
  s = schema()
  assert s["type"] == "object"
  assert s["additionalProperties"] is False
  assert set(s["required"]) == RESULT_FIELDS == set(s["properties"])
  props = s["properties"]
  assert set(props["outcome"]["enum"]) == OUTCOMES
  assert props["frontier_empty"]["type"] == "boolean"
  assert set(props["questions"]["items"]["required"]) == QUESTION_FIELDS
  assert set(props["contradictions"]["items"]["required"]) == CONTRADICTION_FIELDS
  assert set(props["new_tasks"]["items"]["required"]) == NEW_TASK_FIELDS


def test_round_examples_match_schema() -> None:
  blocks = re.findall(r"```json\s*\n(.*?)```", read(REFS / "rounds.md"), re.S)
  outcomes = set()
  for block in blocks:
    result = json.loads(block)
    assert set(result) == RESULT_FIELDS
    assert result["outcome"] in OUTCOMES
    assert isinstance(result["frontier_empty"], bool)
    assert all(set(q) == QUESTION_FIELDS for q in result["questions"])
    assert all(set(c) == CONTRADICTION_FIELDS for c in result["contradictions"])
    assert all(set(t) == NEW_TASK_FIELDS for t in result["new_tasks"])
    assert len(result["summary"].splitlines()) <= 5
    outcomes.add(result["outcome"])
  assert outcomes == OUTCOMES


def test_ledger_vocabulary_and_rules() -> None:
  text = flat(REFS / "ledger.md")
  for word in TASK_TYPES + STATUSES + ("Draft", "Approved", "Implemented"):
    assert f"`{word}`" in text, word
  for phrase in ("docs/architecture/c4-tasks.md", "new `approve` task",
                 "only after the user confirms", "Reconcile",
                 "malformed", "does not rewrite"):
    assert phrase in text, phrase


def test_rounds_cover_every_round_type() -> None:
  text = read(REFS / "rounds.md")
  for kind in ROUND_TYPES:
    assert re.search(rf"^## `{kind}` round", text, re.M), kind


PLAYBOOKS = {
    "c1-context.md": ("People", "External Systems", "Critical User Journeys",
                      "Quality Attributes and Constraints", "C4Context"),
    "c2-container.md": ("Containers", "C3: required", "C3: skip",
                        "Relationships", "C4Container", "C4Deployment",
                        "Key Decisions"),
    "c3-component.md": ("Components", "Interfaces", "Test Seams",
                        "Error Handling", "C4Component", "deep module"),
}


def test_mermaid_reference_has_one_example_per_diagram() -> None:
  text = read(REFS / "mermaid-c4.md")
  for kind in ("C4Context", "C4Container", "C4Component", "C4Deployment"):
    assert re.search(rf"```mermaid\s*\n\s*{kind}\b", text), kind
  flat_text = " ".join(text.split())
  for phrase in ("title", "Legend", "technology", "deep module", "test seam"):
    assert phrase in flat_text, phrase


@pytest.mark.parametrize("name", sorted(PLAYBOOKS))
def test_level_playbook_structure(name: str) -> None:
  text = read(REFS / name)
  for heading in ("## Seed questions", "## Document template", "## Diagram",
                  "## Ready for review"):
    assert heading in text, heading
  for term in PLAYBOOKS[name]:
    assert term in text, term


def test_c4_model_standard() -> None:
  text = flat(ROOT / "resources/document_standards/c4-model-standard.md")
  for phrase in ("title", "legend", "technology", '"Uses"', "GLOSSARY.md",
                 "decision files", "level", "Ready for review"):
    assert phrase in text, phrase
  assert "c4-model-standard.md" in read(ROOT / "resources/README.md")


def test_orchestrator_contract() -> None:
  text = flat(SKILL / "SKILL.md")
  for phrase in ("docs/architecture/c4-tasks.md", "fresh subagent",
                 "`references/ledger.md`", "`references/rounds.md`",
                 "`references/grilling.md`", "round-result.schema.json",
                 "`resources/document_standards/c4-model-standard.md`",
                 "ResolveMode: delegated", "never runs builds or tests"):
    assert phrase in text, phrase


def test_orchestrator_review_focus() -> None:
  text = flat(SKILL / "SKILL.md")
  for phrase in (
      "maps each part of a free-form reply to a question number",
      "greenfield",
      "after every round",
      "no subagent tool",
  ):
    assert phrase in text, phrase


def test_execution_rules_scope_egm_c4_exceptions() -> None:
  text = flat(ROOT / "resources/execution_instructions.md")
  for phrase in ("egm-c4", "Code writing", "Round writes",
                 "Contradictions in rounds", "Interview rounds",
                 "Orchestrator writes"):
    assert phrase in text, phrase
  assert "keep the code in a markdown draft block" in text


def test_review_loop_delegated_resolution() -> None:
  text = flat(ROOT / "skills/egm-review-loop/SKILL.md")
  for phrase in ("ResolveMode", "`inline`", "`delegated`",
                 "Execute the resolution workflow in the primary Elephant context",
                 "StopBeforeGate: true", "ReportDir"):
    assert phrase in text, phrase


def test_resolve_can_stop_before_gate() -> None:
  text = flat(ROOT / "skills/egm-resolve/SKILL.md")
  assert "StopBeforeGate" in text
  assert "without editing `TargetFile`" in text


def test_c4_passes_report_dir() -> None:
  assert "ReportDir" in flat(SKILL / "SKILL.md")


def test_delegated_round_reports_and_report_dir() -> None:
  loop = flat(ROOT / "skills/egm-review-loop/SKILL.md")
  assert "goldfish_review_report.round-" in loop
  assert "Status: resolved" in loop
  assert "goldfish_review_report.round-" in flat(
      SKILL / "references/rounds.md")
  assert "ReportDir" in flat(ROOT / "skills/egm-resolve/SKILL.md")
  assert "ReportDir" in flat(ROOT / "docs/designs/review.md")


def test_orchestrator_routes_all_design_levels() -> None:
  text = flat(SKILL / "SKILL.md")
  for phrase in ("`references/c2-container.md`", "`references/c3-component.md`",
                 "/egm-c4 c3 <container>", "upper levels are not Approved",
                 "Reconcile", "`stale`"):
    assert phrase in text, phrase
