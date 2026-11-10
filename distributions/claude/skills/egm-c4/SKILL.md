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

`/egm-c4 [c1|c2|c3 <container>|c4|<idea text>]`

*   **No argument:** resume from the ledger and run the next ready task.
*   **Any other text:** the idea. With no ledger, Start-up step 3 records it
    instead of asking for it. With a ledger, ask whether to append it as a
    note to the next ready task's scope.
*   **`c1`:** run C1. If C1 is `Approved`, confirm first that
    `docs/architecture/c1-context.md` returns to Draft and every task that
    depends on it becomes `stale`, then reopen it (see Reopening). The grill
    round keeps the existing decision log.
*   **`c2`, `c3 <container>`:** run that level. `/egm-c4 c3 <container>` names
    a container from the C2 container table; for a container that is not in
    the table or is marked `C3: skip`, refuse with that reason and list the
    containers marked `C3: required`. A `Draft` level resumes from its
    ledger tasks. An `Approved` level is reopened as for `c1`, keeping its
    decision log.
*   **`c4`:** run the C4 code step. A `Draft` build plan resumes from its
    ledger tasks; an `Approved` one resumes its slice tasks, and is reopened
    as for `c1` only when the user asks.

Forcing a level whose upper levels are not `Approved` is refused with the
reason: "upper levels are not Approved", naming them and their statuses. The
upper levels of `c4` are C1, C2 and every `C3: required` document.

## Role and write limits

You write only:

*   `docs/architecture/c4-tasks.md` (the ledger);
*   `docs/architecture/decisions/*.answers.md`, append-only;
*   the `**Status:**` line of a level document;
*   replacement text the user approved at a resolve gate, applied verbatim;
*   the user's gate decisions recorded verbatim in the round report, marked
    `Status: resolved`;
*   under direct dispatch, each reviewer's returned findings, saved verbatim to
    the scope's review folder (`docs/architecture/reviews/<stem>/`).

Every other file is written by a round subagent or by the review skills. You do
not draft documents, judge review findings, or write code. You may run
read-only commands such as `git status`, `git hash-object`, `git rev-parse`
and `git diff --name-only` for path checks;
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
    is not a git repository, ask the user to initialize one. Then take the
    idea from the input or ask the user to describe it, create the ledger with
    the C1 `grill`, `draft`, `readiness`, `review` and `approve` tasks, and
    record the idea verbatim as the first note entry (round 0, `R0-N1`) of
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

*   `C1`, `C2`, `C3:<container>`: the Grilling loop and Level loop below.
*   `C4` plan tasks: the Grilling loop and Level loop. `C4:slice-NN` tasks and
    the `C4` `drift` task: the C4 code step below.

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
    ask whether to keep or revert it before you use the result. In the C4
    step an implement or fix round's declared outputs are its ticket's
    Allowed Paths, and `references/c4-code.md` adds the branch checks.
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
    note entries and another round runs. On confirmation, mark the `grill` task
    `done`.

## Level loop

Each level has a document and a playbook, found through the ledger's scope
mapping:

| Level | Document | Playbook |
| :---- | :------- | :------- |
| C1 | `docs/architecture/c1-context.md` | `references/c1-context.md` |
| C2 | `docs/architecture/c2-containers.md` | `references/c2-container.md` |
| C3 | `docs/architecture/c3-<container>.md` | `references/c3-component.md` |
| Build plan | `docs/architecture/c4-build-plan.md` | `references/c4-code.md` |

The loop is the same at every level:

1.  **Grill** until the frontier is empty and confirmed.
2.  **Draft.** Dispatch a `draft` round. It writes the document only from the
    decision files and approved upper documents, with `**Status:** Draft`, and
    updates `GLOSSARY.md` and `docs/adr/`.
3.  **Section approval.** Show the draft one section at a time (for the
    build plan, its sections and then each ticket). Append each requested
    change to the answers file as a note entry, then add tasks by the
    ledger's adding and superseding rules (`references/ledger.md`).
4.  **Readiness.** Dispatch a `readiness` round. Gaps add tasks by the
    ledger's adding and superseding rules (`references/ledger.md`).
5.  **Goldfish review.** Read `egm-review-loop` (`../egm-review-loop/SKILL.md`
    from this skill's folder) and follow it in this thread, not through a
    Skill tool, with:
    *   `TargetFile`: the level document; `SemanticTarget`: `full file`. For
        the build plan, `SemanticTarget` is `full file, plus every slice
        ticket listed in GoldfishContext`: reviewers review the tickets too,
        and approved replacement text may apply to a ticket;
    *   `ResolveMode: delegated`; `RunId`: the ledger `review` task ID (for
        example `T04`);
    *   reviewers and standards by level. Do not use `egm-codebase-details`:
        no code exists yet.

        | Level | Reviewer → standard |
        | :---- | :------------------ |
        | C1 | `egm-zoom-out` → `zoom-out-standard`; `egm-comprehension` → no standard; `egm-design`, `egm-structural`, `egm-style` → `c4-model-standard` |
        | C2 | as C1 without `egm-comprehension` |
        | C3 | as C2, plus `egm-implementation-readiness` → `c4-model-standard` |
        | Build plan | `egm-implementation-readiness` → `implementation-readiness-standard`; `egm-style` → `c4-model-standard` |

        `c4-model-standard` is
        `resources/document_standards/c4-model-standard.md`;
        `implementation-readiness-standard` is
        `resources/document_standards/implementation-readiness-standard.md`;
    *   `GoldfishContext`: the scope's decision files, the approved upper
        documents, `GLOSSARY.md`, the note "greenfield project: no existing
        code to leverage", and for the build plan every ticket in
        `docs/architecture/slices/`;
    *   `ReportDir`: the scope's review folder (for example
        `docs/architecture/reviews/c1/`), which keeps the loop's settled
        findings across runs. Name it as the report location to the loop, the
        synthesizer and every resolve round.

    Report names carry the run and round, so runs never overwrite each other:
    round reports are `goldfish_review_report.<RunId>.round-<n>.md`. Under
    direct dispatch (no synthesizer, as in Claude Cowork), save each
    reviewer's returned findings verbatim as
    `findings.<RunId>.round-<n>.<reviewer>.md` in the review folder; the
    resolve round reads them there. In delegated mode each loop round's
    resolution is a `resolve` round in a fresh subagent that follows
    `egm-resolve` through its report and stops before the gate. You show the
    gate, apply replacement text the user approves verbatim, record the
    user's decision for each finding verbatim in the round report, and mark it
    `Status: resolved` before the next round. Convergence counts only this
    run's reports; the settled list reads every run's reports in the folder.
    Findings that need more add tasks by the ledger's adding and superseding
    rules (`references/ledger.md`). The `review` task is `done` when the loop ends.
6.  **Approve.** Ask for explicit approval. On approval, set
    `**Status:** Approved`, mark `approve` `done`, and add the next tasks by the
    ledger's adding rules. On rejection, add tasks by the ledger's adding and
    superseding rules (`references/ledger.md`).

**Level order.** C2 is dispatched after C1 is `Approved`. After C2 is
`Approved`, add C3 tasks for each container the C2 table marks `C3: required`
(containers marked `C3: skip (<reason>)` get none), then the `C4` grill, draft,
readiness, review and approve tasks for the build plan. C3 for a container
runs only when C1 and C2 are `Approved`. The `C4` grill depends on every C3
`approve` task (on C2's when no container needs C3). Reconcile the C3 tasks each time C2 is approved again, as described in
`references/ledger.md`, and keep the `C4` grill's dependencies in step.

## C4 code step

Load `references/c4-code.md` yourself: it defines the slice tasks, batches,
path checks, batch gates and the finish.

1.  **Build plan.** Scope `C4` runs the Grilling loop and Level loop with the
    Build plan rows above. Its draft writes documents only:
    `docs/architecture/c4-build-plan.md` and tickets in
    `docs/architecture/slices/`. At its `approve` gate, name the plan's
    integration branch and worktree root. Approval of a root outside the
    project confirms that slice rounds write there; with `none`, slices run
    one at a time on slice branches in the project checkout. Before asking,
    check that the integration branch has a commit
    (`git rev-parse --verify <integration-branch>`); if not, ask the user to
    commit `docs/architecture/`, `GLOSSARY.md` and `docs/adr/` first. You never
    commit.
2.  **Slices.** No implement, fix or merge round runs before build-plan
    approval. On approval, add the slice and `drift` tasks. Slice 01, the
    walking skeleton, runs alone; later ready slices run in batches. Each
    slice is implemented, path-checked, merged, verified and code-reviewed by
    fresh subagents.
3.  **Path checks.** After each implement, fix and merge round, compare the
    changed paths with the ticket's Allowed Paths (the batch's for a merge).
    Show a violation; `references/c4-code.md` says whether it adds a `fix`
    chain or blocks the task for your keep-or-revert question.
4.  **Results.** A `FAIL` verify or `BLOCKING` code review proposes a `fix`;
    add the `fix` chain after the user confirms.
5.  **Batch gate.** After each batch, show its results and ask whether to
    start the next batch. Record batch membership and approval in the ledger
    by its batch rule (`references/ledger.md`), which next-ready follows.
6.  **Finish.** When every slice is done, dispatch the `drift` round (it reads
    `egm-drift-report`'s SKILL.md). After the user settles each finding and
    the `drift` task is `done`, set each fully implemented document to
    `Implemented`.

A contradiction while building stops slice work; see `references/c4-code.md`.

## Reopening

When the user accepts a contradiction or forces an `Approved` level, confirm
what returns to Draft and which tasks become `stale`. For a contradiction,
append it (document, statement, evidence) to the reopened scope's answers
file as a note entry. Then apply the reopening and Reconcile rules in
`references/ledger.md`; the new grill round starts from the existing tree and
answers plus the contradiction. When an `approve` task becomes `stale`, set
that document's `**Status:**` line to `Draft`.
