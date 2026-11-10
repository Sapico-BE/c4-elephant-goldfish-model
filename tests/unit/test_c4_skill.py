# SPDX-License-Identifier: Apache-2.0
"""Contracts for the egm-c4 orchestrator skill and its references."""

import json
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/egm-c4"
REFS = SKILL / "references"
ADAPTED = ("grilling.md", "domain-language.md")


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
