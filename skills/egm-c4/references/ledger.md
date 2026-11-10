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

## Scope mapping

The orchestrator derives file names from the ledger `Scope` with this table and
writes the concrete paths into each brief.

| Ledger Scope | Decision-file stem | Review folder | Document |
| :----------- | :----------------- | :------------ | :------- |
| `C1` | `c1` | `docs/architecture/reviews/c1/` | `docs/architecture/c1-context.md` |
| `C2` | `c2` | `docs/architecture/reviews/c2/` | `docs/architecture/c2-containers.md` |
| `C3:<container>` | `c3-<container>` | `docs/architecture/reviews/c3-<container>/` | `docs/architecture/c3-<container>.md` |
| `C4` | `c4-plan` | `docs/architecture/reviews/c4-plan/` | `docs/architecture/c4-build-plan.md` |
| `C4:slice-NN` | none | none | `docs/architecture/slices/NN-<slice>.md` |

Decision files are `docs/architecture/decisions/<stem>.tree.md` and
`<stem>.answers.md`.

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
`done`. An `in-progress` task left by an interrupted session is resumed first.

**Slice batches.** Batches (`c4-code.md`) restrict only `C4:slice-NN` tasks
and the `C4` `drift` task. Tasks of every other scope, including a reopened
build plan's `C4` chain and C1 to C3 reopen tasks, are ready by the rule above
whether or not a batch is open. When a batch starts, the orchestrator adds
`batch Bn` to the Notes of each member slice's `implement` task (`B1` is slice
01 alone). When the user approves the batch gate, it adds `Bn approved` to the
same Notes. A batch is open from its start until it is approved, and at most
one is open. While a batch is open, the only ready `C4:slice-NN` tasks are
those of its member slices, including their `fix` chains. An `implement` with
no batch label is ready only when no batch is open; the next batch then takes
every such ready `implement`. `drift` is ready only when no batch is open.

If the build plan or an upper level is reopened while a batch is open,
in-progress slice rounds stop as "Contradictions while building" in
`c4-code.md` says, and the member slices' remaining tasks wait on the new
`approve` by the reopening rule. The batch stays open; its gate is asked once
the reopen chain's `approve` is `done` and every member slice's last
`code-review` is `done`.

## Status mapping

Document Status follows the scope's highest-ID `approve` task; `approve` in
the table means that task:

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
*   Build plan approved → per slice: implement, merge, verify, code-review;
    then one `C4` `drift` task that waits on every slice (see `c4-code.md`).
*   Section changes or review findings that need more than an approved
    replacement → `revise`, then a new `readiness`, `review` and `approve`. A
    change that needs a new decision → `grill` first.
*   Blocking code-review findings, failed verification, a path-check
    violation, or a change the user requests at a batch gate → `fix`, then
    `merge`, `verify` and `code-review` again.
*   User rejects at `approve` → `revise` (or `grill` if a new decision is
    needed), then `readiness`, `review` and a new `approve`.

**Superseding.** When a `revise` (or `grill`) chain is added for a scope, set
that scope's pending `readiness`, `review` and `approve` tasks (`todo`,
`stale`, or the `approve` the user just rejected) to `done` with Notes
`superseded by Txx`, naming the new task of the same type. When a `fix`
chain is added for a slice, supersede that slice's pending `merge`, `verify`
and `code-review` tasks the same way, and point every task that is not `done`
and depends on the slice's latest `verify` or `code-review` (done or not:
later slices' `implement`, the `drift` task) at the chain's new `code-review`.
Point any task that depended on a superseded task at its replacement. Because the Status mapping
reads the highest-ID `approve` task, a superseded `approve` never sets a
document to `Approved`.

Tasks a round proposes in `new_tasks` are added only after the user confirms.

## Reopening

When the user accepts a contradiction or forces an `Approved` level:

1.  Set the reopened document to `Draft` and add `grill`, `draft`, `readiness`,
    `review` and `approve` tasks for it. The `grill` round starts from the
    existing tree and answers, plus the contradiction.
2.  Mark every task that transitively depends on the old `approve` task
    `stale`, and point its dependency at the new `approve` task. Stale tasks
    therefore cannot run before the upper level is approved again. Done
    `C4:slice-NN` tasks follow the narrower rule in `c4-code.md`
    ("Contradictions while building").
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
