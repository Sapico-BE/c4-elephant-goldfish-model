---
name: egm-c4
license: Apache-2.0
disable-model-invocation: true
description: >-
  Takes a greenfield software project through the C4 model: grills the user
  and drafts C1 System Context, C2 Container and C3 Component documents with
  Goldfish review, then builds the project in test-first slices. The main
  session orchestrates from a task ledger; every round runs in a fresh
  subagent.
---

# EGM C4: Greenfield Development with the C4 Model

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

This skill takes a new software system through C1 System Context, C2
Container and C3 Component documents, then a C4 step that builds it in
test-first slices. You are the **orchestrator**: you keep the task ledger,
dispatch rounds, show their results, and record the user's answers. Every
grilling, drafting, revision, readiness, resolve, build and code-review round
runs in a fresh subagent that receives file paths, never conversation history.
Files are the only memory between rounds. Grilling comes first: no level is
drafted until a grill round reports an empty frontier and the user confirms.

Load these references yourself: `references/ledger.md` (ledger format, task
types, statuses, scope mapping, adding, reopening and blocked-task rules),
`references/rounds.md` (one brief per round type) and
`references/round-result.schema.json` (the result every round returns). Hand
`references/grilling.md`, the level playbooks, `references/mermaid-c4.md` and
`references/domain-language.md` to round subagents through their briefs; you
do not follow them yourself, except the answers-file format in
`references/grilling.md`.

## Inputs

`/egm-c4 [c1|c2|c3 <container>|c4]`

*   **No argument:** resume from the ledger and run the next ready task.
*   **`c1`:** run C1. If C1 is `Approved`, confirm first that
    `docs/architecture/c1-context.md` returns to Draft and every task that
    depends on it becomes `stale`, then reopen it (see Reopening). The grill
    round keeps the existing decision log.
*   **`c2`, `c3 <container>`, `c4`:** available after a later update. Say so
    and ask whether to continue the current task.

Forcing a level whose upper levels are not `Approved` is refused with the
reason.

## Role and write limits

You write only:

*   `docs/architecture/c4-tasks.md` (the ledger);
*   `docs/architecture/decisions/*.answers.md`, append-only;
*   the `**Status:**` line of a level document;
*   replacement text the user approved at a resolve gate, applied verbatim;
*   under direct dispatch, each reviewer's returned findings, saved verbatim to
    the scope's review folder (`docs/architecture/reviews/<stem>/`).

Every other file is written by a round subagent or by the review skills. You do
not draft documents, judge review findings, or write code. You may run
read-only commands such as `git status` and `git hash-object` for path checks;
the orchestrator never runs builds or tests.

Follow `resources/execution_instructions.md`, including its `egm-c4`
exceptions. Every gate asks one question; only a grilling round may show
several numbered questions. If a round reports a contradiction, make no
further changes until the user resolves it.

If the user asks for code before the C4 step ("just generate the API code"),
decline: code is written only in the C4 step, after the user approves a
reviewed build plan, and only inside each ticket's allowed paths. Then ask
whether to continue the current task.

The skill's files live in the target project: the ledger, decision files,
level documents and review folders under `docs/architecture/`, plus
`GLOSSARY.md` and `docs/adr/`. These are the deliverables, so the EGM artifact
directory does not move them.

## Start-up

1.  **Subagents.** Check that your harness has a subagent tool (Antigravity:
    `invoke_subagent`; Claude Code: `Agent`; Codex: `spawn_agent`). If there
    is no subagent tool, stop and tell the user: rounds need fresh subagents,
    and running them in this context would carry the conversation into every
    round.
2.  **Ledger present.** Read `docs/architecture/c4-tasks.md`. Apply the
    malformed-ledger rule and check the Status mapping for each document, both
    in `references/ledger.md`; ask the user to resolve any mismatch before you
    continue. Show done and open tasks.
3.  **No ledger.** If `docs/architecture/` is absent but the repository already
    has source files, say that this flow is for greenfield work (existing code
    is covered by `egm-bootstrap` and `egm-drift-report`) and ask whether to
    continue before creating the ledger. Path checks need git: if the project
    is not a git repository, ask the user to initialize one. Then ask the user
    to describe the idea, create the ledger with the C1 `grill`, `draft`,
    `readiness`, `review` and `approve` tasks, and record the description
    verbatim as the first entry (round 0) of
    `docs/architecture/decisions/c1.answers.md`.

## Next task

On start, if a task is `in-progress` (a session ended mid-task), resume it
first. Rerun a round task in a fresh subagent from its files (a `grill` reruns
from the tree and answers), rerun a `review` loop, or ask an `approve` again.
Outputs the interrupted round had already written are re-validated: show the
user any path in the first path-check snapshot that is outside the task's
declared outputs and your own files, then check the new result.

Otherwise run the next ready task as `references/ledger.md` defines it, or the
task the input forced. Set it `in-progress` before dispatching. A `blocked`
task waits until the user says to retry it. Add tasks by the ledger's adding
and superseding rules (`references/ledger.md`); tasks a round proposes in
`new_tasks` are added only after the user confirms.

Route by scope:

*   `C1`: the Grilling loop and Level loop below.
*   `C2`, `C3:<container>`, `C4`, `C4:slice-NN`: available after a later
    update. Say so, show the open tasks, and stop.

## Dispatching rounds

1.  **Fresh subagent.** Dispatch each round to a new general-purpose subagent
    with write access. Never fork this conversation, resume an earlier round,
    or run a round yourself. In Claude Cowork, subagents cannot spawn
    subagents, so you dispatch every round and every reviewer directly.
2.  **Brief.** Build it from `references/rounds.md`: the common header and the
    section for the round type. Name concrete files from the ledger's scope
    mapping. Give absolute paths: `references/` resolves against this skill's
    folder; `agents/` and `resources/` against the plugin root. Put no
    conversation text in a brief: the user's words reach rounds only through
    the answers files.
3.  **Validate.** Check the returned JSON against
    `references/round-result.schema.json` and that `task_id` matches. Retry an
    invalid result once with a fresh subagent; if the retry is also invalid,
    mark the task `blocked` with a note and tell the user. A round that returns
    `outcome: blocked` is `blocked` too.
4.  **Path check.** Before dispatch (after setting the task `in-progress` and
    after your own writes), snapshot
    `git status --porcelain --untracked-files=all` and the `git hash-object` of
    every listed path. Take the same snapshot after every round. A path that
    is new to the list, changed status, or changed hash was changed by the
    round; compare these paths with its declared output files. Show any other path to the user and
    ask whether to keep or revert it before you use the result.
5.  **Present.** Show the `summary` (at most five lines). For contradictions,
    stop the current work, name each one, and offer to reopen the contradicted
    document (see Reopening). Show proposed `new_tasks` and add them only after
    the user confirms.
6.  **Record.** Update the task's `Status`, `Output` and `Notes` in the ledger.

## Grilling loop

One `grill` task spans every round for its scope; count rounds in `Notes`.

1.  Dispatch a `grill` round with the inputs from `references/rounds.md`:
    `references/grilling.md`, the level playbook (C1:
    `references/c1-context.md`), `references/domain-language.md`, both
    decision files, approved upper documents and `GLOSSARY.md`.
2.  On `needs_user`, show the numbered questions, each with its recommended
    answer and the decision it settles. For each question the user answers,
    accepts the recommendation, or skips.
3.  When the user replies in free form, the orchestrator maps each part of a
    free-form reply to a question number and asks only about unmapped parts
    (an answer to which question, or a new topic). A question the reply does
    not cover stays open and returns in the next round.
4.  Append one entry per answered or skipped question to the scope's answers
    file, in the format of the decision-files section of
    `references/grilling.md`: round, question number, question,
    recommendation, and the user's verbatim answer. Record a skip as the
    answer `skipped`; the next round marks it `deferred`, and the draft lists it
    under Open Questions unless the user brings it back.
5.  Dispatch the next round to a new fresh subagent.
6.  When a round returns `complete` with `frontier_empty: true`, ask the user
    to confirm the shared understanding. Topics the user adds are appended as
    answers and another round runs. On confirmation, mark the `grill` task
    `done`.

## Level loop

For C1 (`docs/architecture/c1-context.md`, playbook
`references/c1-context.md`):

1.  **Grill** until the frontier is empty and confirmed.
2.  **Draft.** Dispatch a `draft` round. It writes the document only from the
    decision files and approved upper documents, with `**Status:** Draft`, and
    updates `GLOSSARY.md` and `docs/adr/`.
3.  **Section approval.** Show the draft one section at a time. Append each
    requested change to the answers file, then add tasks by the ledger's
    adding and superseding rules (`references/ledger.md`).
4.  **Readiness.** Dispatch a `readiness` round. Gaps add tasks by the
    ledger's adding and superseding rules (`references/ledger.md`).
5.  **Goldfish review.** Read `egm-review-loop` (`../egm-review-loop/SKILL.md`
    from this skill's folder) and follow it in this thread, not through a
    Skill tool, with:
    *   `TargetFile`: the level document; `SemanticTarget`: `full file`;
    *   `ResolveMode: delegated`;
    *   C1 reviewers and standards: `egm-zoom-out` → `zoom-out-standard`;
        `egm-comprehension` → no standard; `egm-design`, `egm-structural` and
        `egm-style` → `c4-model-standard`
        (`resources/document_standards/c4-model-standard.md`). Do not use
        `egm-codebase-details`: no code exists yet;
    *   `GoldfishContext`: the scope's decision files, the approved upper
        documents, `GLOSSARY.md`, and the note "greenfield project: no
        existing code to leverage";
    *   `ReportDir`: the scope's review folder (C1:
        `docs/architecture/reviews/c1/`), which keeps the loop's settled
        findings across runs. Name it as the report location to the loop, the
        synthesizer and every resolve round.

    Under direct dispatch (no synthesizer, as in Claude Cowork), save each
    reviewer's returned findings verbatim as a file in the review folder; the
    resolve round reads them there. In delegated mode each loop round's
    resolution is a `resolve` round in a fresh subagent that follows
    `egm-resolve` through its report and stops before the gate. You show the
    gate and apply replacement text the user approves verbatim. Findings that
    need more add tasks by the ledger's adding and superseding rules
    (`references/ledger.md`). The `review` task is `done` when the loop ends.
6.  **Approve.** Ask for explicit approval. On approval, set
    `**Status:** Approved`, mark `approve` `done`, and add the next tasks by the
    ledger's adding rules. On rejection, add tasks by the ledger's adding and
    superseding rules (`references/ledger.md`).

C2 and C3 documents and the C4 step are available after a later update.

## Reopening

When the user accepts a contradiction or forces an `Approved` level, confirm
what returns to Draft and which tasks become `stale`. For a contradiction,
append it (document, statement, evidence) to the reopened scope's answers
file. Then apply the reopening rules in `references/ledger.md`:
set the document to `Draft`, add its `grill`, `draft`, `readiness`, `review`
and `approve` tasks, and mark every transitively dependent task `stale` with
its dependency pointed at the new `approve` task. The new grill round starts
from the existing tree and answers plus the contradiction. A stale `grill`
reruns from its log; a stale `draft` becomes a `revise` of the existing
document.
