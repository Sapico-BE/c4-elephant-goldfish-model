# Round briefs

The orchestrator dispatches every round to a fresh subagent with a brief built
from this file. A round reads nothing else from the conversation and writes only
its declared output files. Every round returns one JSON result that matches
`round-result.schema.json`.

## Common brief header

Start every brief with these lines, filled in:

```
Round type: <type>
Task ID: <T-number from the ledger>
Load these references: <paths>
Input files: <paths>
Output files: <paths>
Read nothing else; write only your output files; return one JSON result
matching references/round-result.schema.json.
```

Every brief gives concrete paths for the decision files, review folder and
document. A round never derives them from the scope. `<scope>` below means the
decision-file stem from the scope mapping in `ledger.md`.

## Result fields

| Field | Content |
| :---- | :------ |
| `task_id` | Ledger task ID |
| `outcome` | `complete`, `needs_user`, or `blocked` |
| `files_written` | Paths |
| `questions` | Numbered questions, each with `recommendation` and the `decision` it settles |
| `frontier_empty` | `true` when no decision is open (grill rounds); `false` otherwise |
| `contradictions` | Upper-level statements this round contradicts: `document`, `statement`, `evidence` |
| `new_tasks` | Proposed ledger tasks: `scope`, `task`, `depends_on`, `reason` |
| `summary` | At most five lines for the orchestrator to show |

Fields that do not apply are empty arrays, `false`, or an empty string, never
omitted. The orchestrator validates each result, retries an invalid one once with
a fresh subagent, and then marks the task `blocked`.

Only grill rounds return `needs_user` with questions as their normal outcome.
Other rounds return `needs_user` only to report a contradiction or a choice the
brief cannot settle. A round that finds a contradiction finishes its declared
outputs and reports it.

The ledger has a `review` task type but no `review` round: the orchestrator runs
`egm-review-loop` itself with `ResolveMode: delegated`, and each loop round's
resolution step is the `resolve` round below. The `approve` task is a gate run by
the orchestrator and has no round either.

## `grill` round

**Inputs:** `references/grilling.md`, the level playbook (`references/c1-context.md`,
`c2-container.md`, `c3-component.md`, or the C4 grill topics in
`references/c4-code.md`), `references/domain-language.md`, the scope's
`<scope>.tree.md` and `<scope>.answers.md` in `docs/architecture/decisions/`
(absent in round one), approved upper-level documents, `GLOSSARY.md`.

**Instructions:** Rebuild the tree from the answers. Look up facts you can find
in files instead of asking. Mark nodes `open`, `decided` (citing an answer entry)
or `deferred`. When reopening, start from the existing tree and answers plus the
contradiction. Return the open frontier as numbered questions, each with a
recommended answer and the decision it settles.

**Output files:** `docs/architecture/decisions/<scope>.tree.md`. Never write the
answers file.

**When to return `needs_user`:** Whenever the frontier has open nodes: return the
questions. Return `complete` with `frontier_empty: true` and no questions when
none is open; the orchestrator then asks the user to confirm.

## `draft` round

**Inputs:** the level playbook, `references/mermaid-c4.md`,
`references/domain-language.md`, the scope's decision files, approved upper-level
documents, `GLOSSARY.md`, `docs/adr/`. For the C4 build plan: `references/c4-code.md`
and the approved C2 and C3 documents.

**Instructions:** Write the level document using only the decision files and
approved upper documents, with `**Status:** Draft`. A statement you cannot trace
to them becomes an Open Question. Deferred decisions are listed under Open
Questions. Update `GLOSSARY.md` and add ADRs by the domain-language rules. For
the build plan, write documents only: target file tree, toolchain and commands,
slice tickets, and a Target Scope & File Boundary that is the union of the
tickets' allowed paths.

**Output files:** `docs/architecture/c1-context.md`, `c2-containers.md`,
`c3-<container>.md`, or `c4-build-plan.md` with
`docs/architecture/slices/NN-<slice>.md`; `GLOSSARY.md`; `docs/adr/`.

**When to return `needs_user`:** When an upper-level document contradicts the
decision files, or a choice the brief cannot settle blocks the draft.

## `revise` round

**Inputs:** the level document, the scope's decision files including the answers
that request the change, approved upper-level documents, the level playbook,
`GLOSSARY.md`, and any readiness gaps or review findings to address.

**Instructions:** Change only what the new answers or listed gaps require. Keep
`**Status:** Draft`. Keep the document traceable to the decision files.

**Output files:** the level document, and `GLOSSARY.md` or `docs/adr/` when the
change touches them.

**When to return `needs_user`:** When the change needs a new decision (propose a
`grill` task in `new_tasks`), or contradicts an upper-level document.

## `readiness` round

**Inputs:** the level document, the level playbook's ready-for-review criteria,
approved upper-level documents.

**Instructions:** Check each criterion and return the gaps. Write nothing.

**Output files:** none. Gaps go in `summary` and `new_tasks` (a `revise` task).

**When to return `needs_user`:** When a gap needs a user decision or an
upper-level contradiction; otherwise return `complete`.

## `resolve` round

**Inputs:** `egm-resolve` with `StopBeforeGate` set, the review folder
`docs/architecture/reviews/<scope>/` and its per-round reports (under
direct dispatch, the reviewer findings the orchestrator saved verbatim in that
folder), the
target document.

**Instructions:** Follow `egm-resolve` through its report and stop before the
gate. Record dispositions and proposed replacement text. Do not edit the target.

**Output files:** `docs/architecture/reviews/<scope>/goldfish_review_report.round-<n>.md`
(`n` is the loop round; the orchestrator names the file).

**When to return `needs_user`:** When a finding needs a user choice before a
disposition can be written. The orchestrator runs the gate and applies approved
replacement text verbatim.

## `implement` round

**Inputs:** `references/c4-code.md`, the slice ticket
`docs/architecture/slices/NN-<slice>.md`, `docs/architecture/c4-build-plan.md`,
the C3 documents the ticket touches, the code standards the build plan names.

**Instructions:** Work red-green at the ticket's test seams on its own branch or
worktree. Write only inside the ticket's allowed paths. Slice 01 is the walking
skeleton and may write the scaffolding its ticket lists.

**Output files:** files inside the ticket's allowed paths.

**When to return `needs_user`:** When the C3 interfaces or the ticket
contradict what the code needs. Finish what is possible and report the
contradiction.

## `fix` round

**Inputs:** the slice ticket, the blocking code-review findings, the failed
verification summary, or the path-check violation, plus the files they name.

**Instructions:** Fix only the listed findings, or revert the out-of-bounds
changes. Stay inside the ticket's allowed paths.

**Output files:** files inside the ticket's allowed paths.

**When to return `needs_user`:** When fixing needs a change outside the allowed
paths or reveals a contradiction with a C3 interface.

## `merge` round

**Inputs:** the batch's slice branches or worktrees, the integration branch, the
tickets' allowed paths.

**Instructions:** Merge each slice into the integration branch. Resolve
conflicts only within the batch's allowed paths.

**Output files:** files inside the batch's allowed paths.

**When to return `needs_user`:** When a conflict lies outside the allowed paths
or cannot be resolved without changing a slice's intent.

## `verify` round

**Inputs:** `docs/architecture/c4-build-plan.md` (build and test commands), the
integration branch.

**Instructions:** Run the build plan's build and test commands. Do not fix
anything. Return `outcome: complete` with a `summary` that begins `PASS` or
`FAIL: <short failure summary>`. On `FAIL`, propose a `fix` task for the slice
in `new_tasks`; after the user confirms it, the orchestrator adds `fix`,
`merge`, `verify` and `code-review` as `ledger.md` describes.

**Output files:** build outputs only.

**When to return `needs_user`:** When a build or test command is missing or
cannot run in this environment; use `blocked` if nothing can run.

## `code-review` round

**Inputs:** the slice diff, the slice ticket, the C3 interfaces it touches, the
code standards the build plan names.

**Instructions:** Read-only. Check the diff against the code standards, the C3
interfaces and the ticket. Return `outcome: complete` with a `summary` that
begins `APPROVED` or `BLOCKING: <findings>`. Blocking findings propose a `fix`
task for the slice in `new_tasks`; the orchestrator then adds `fix`, `merge`,
`verify` and `code-review` as `ledger.md` describes.

**Output files:** none.

**When to return `needs_user`:** When a finding shows the C3 interface itself is
wrong (report it as a contradiction).

## `drift` round

**Inputs:** `egm-drift-report`, `docs/architecture/`, the implemented code.

**Instructions:** Run `egm-drift-report` on `docs/architecture/`. Report where
documents and code disagree.

**Output files:** the drift report in the location `egm-drift-report` names.

**When to return `needs_user`:** When drift shows a document that no longer
matches the built system and the user must choose between updating the document
and the code.

## Example results

A grill round with questions:

```json
{
  "task_id": "T01",
  "outcome": "needs_user",
  "files_written": ["docs/architecture/decisions/c1.tree.md"],
  "questions": [
    {
      "number": 1,
      "question": "Who are the primary users, and is there an admin role?",
      "recommendation": "Customers and support staff; no separate admin role in v1.",
      "decision": "People: user roles"
    }
  ],
  "frontier_empty": false,
  "contradictions": [],
  "new_tasks": [],
  "summary": "Round 1 wrote the C1 tree with 6 nodes.\n1 question is open."
}
```

A draft round that reports a contradiction:

```json
{
  "task_id": "T07",
  "outcome": "needs_user",
  "files_written": ["docs/architecture/c2-containers.md"],
  "questions": [],
  "frontier_empty": false,
  "contradictions": [
    {
      "document": "docs/architecture/c1-context.md",
      "statement": "The system has no external payment provider.",
      "evidence": "c2.answers.md round 2 settles checkout through a hosted payment page."
    }
  ],
  "new_tasks": [],
  "summary": "Draft written with Status Draft.\n1 contradiction with C1."
}
```

A completed grill round:

```json
{
  "task_id": "T06",
  "outcome": "complete",
  "files_written": ["docs/architecture/decisions/c2.tree.md"],
  "questions": [],
  "frontier_empty": true,
  "contradictions": [],
  "new_tasks": [],
  "summary": "No open nodes remain in the C2 tree."
}
```

A blocked round:

```json
{
  "task_id": "T12",
  "outcome": "blocked",
  "files_written": [],
  "questions": [],
  "frontier_empty": false,
  "contradictions": [],
  "new_tasks": [
    {
      "scope": "C4",
      "task": "revise",
      "depends_on": [],
      "reason": "The build plan's slice 02 ticket lacks allowed paths."
    }
  ],
  "summary": "Cannot start: the slice 02 ticket in the build plan has no allowed paths."
}
```
