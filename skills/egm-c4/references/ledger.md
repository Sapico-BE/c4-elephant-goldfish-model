# Task ledger

`docs/architecture/c4-tasks.md` in the target project holds one table. The
orchestrator is its only writer.

| Column | Content |
| :----- | :------ |
| `ID` | `T01`, `T02`, … in creation order |
| `Scope` | `C1`, `C2`, `C3:<container>`, `C4`, `C4:slice-NN` |
| `Task` | `grill`, `draft`, `revise`, `readiness`, `review`, `approve`, `implement`, `merge`, `verify`, `code-review`, `fix`, `drift` |
| `Status` | `todo`, `in-progress`, `done`, `blocked`, `stale` |
| `Depends on` | Task IDs |
| `Output` | File the task produced |
| `Notes` | Round count, contradictions, user overrides |

One `grill` task spans all rounds for its scope; `Notes` counts them. A
`review` task spans one `egm-review-loop` run.

## Example after C1 approval

| ID | Scope | Task | Status | Depends on | Output | Notes |
| :- | :---- | :--- | :----- | :--------- | :----- | :---- |
| T01 | C1 | grill | done | | docs/architecture/decisions/c1.tree.md | 3 rounds |
| T02 | C1 | draft | done | T01 | docs/architecture/c1-context.md | |
| T03 | C1 | readiness | done | T02 | | |
| T04 | C1 | review | done | T03 | docs/architecture/reviews/c1/ | 2 loop rounds |
| T05 | C1 | approve | done | T04 | docs/architecture/c1-context.md | |
| T06 | C2 | grill | todo | T05 | | |
| T07 | C2 | draft | todo | T06 | | |
| T08 | C2 | readiness | todo | T07 | | |
| T09 | C2 | review | todo | T08 | | |
| T10 | C2 | approve | todo | T09 | | |

## Next ready task

The first `todo` or `stale` task, in ID order, whose dependencies are all
`done`.

## Status mapping

Document Status follows the scope's `approve` task:

| Document `**Status:**` | Ledger state |
| :--------------------- | :----------- |
| `Draft` (or file missing) | `approve` task is not `done` |
| `Approved` | `approve` task is `done`; C4 slices for the scope are not all `done` |
| `Implemented` | `approve` is `done` and every slice touching the scope is `done` |

On start, the orchestrator checks this mapping for each document and asks the
user to resolve any mismatch.

## Malformed ledger

On start, if a row has an unknown status or task type, a missing column, or a
dependency on a missing ID, the orchestrator shows those rows and does not
rewrite the file until the user fixes it or confirms a correction. The
orchestrator does not rewrite a malformed ledger on its own.

## Adding tasks

The orchestrator adds tasks only by these rules:

*   C1 approved → C2 grill, draft, readiness, review, approve.
*   C2 approved → the same five tasks per container marked `C3: required`, then
    the C4 grill, draft, readiness, review and approve tasks for the build plan.
*   Build plan approved → per slice: implement, merge, verify, code-review.
*   Section changes or review findings that need more than an approved
    replacement → `revise`, then a new `readiness` and `review`. A change that
    needs a new decision → `grill` first.
*   Blocking code-review findings or failed verification → `fix`, then `merge`,
    `verify` and `code-review` again.
*   User rejects at `approve` → `revise` (or `grill` if a new decision is
    needed), then `readiness`, `review` and a new `approve`.

Tasks a round proposes in `new_tasks` are added only after the user confirms.

## Reopening

When the user accepts a contradiction or forces an `Approved` level:

1.  Set the reopened document to `Draft` and add `grill`, `draft`, `readiness`,
    `review` and `approve` tasks for it. The `grill` round starts from the
    existing tree and answers, plus the contradiction.
2.  Mark every task that transitively depends on the old `approve` task
    `stale`, and point its dependency at the new `approve` task. Stale tasks
    therefore cannot run before the upper level is approved again.
3.  A stale `grill` reruns from its existing log and the upper level's changes;
    a stale `draft` becomes a `revise` of the existing document.

## Reconcile after C2 changes

When C2 is approved again, the orchestrator compares the container table with
the C3 tasks. Reconcile as follows: add tasks for new `C3: required`
containers, mark tasks for removed or `C3: skip` containers `done` with a note,
and keep renamed containers' tasks after asking the user.

## Blocked tasks

A task becomes `blocked` after an invalid round result is retried once, or when
a round returns `outcome: blocked`. It returns to `todo` when the user says to
retry it.
