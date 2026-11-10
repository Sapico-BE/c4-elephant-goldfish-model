# C4 code step playbook

Adapted from mattpocock/skills (skills/engineering/to-tickets/SKILL.md, skills/engineering/tdd/SKILL.md, skills/engineering/code-review/SKILL.md), MIT License. See THIRD_PARTY_NOTICES.md.

Playbook for the C4 step: the build plan `docs/architecture/c4-build-plan.md`
(scope `C4`, decision-file stem `c4-plan`) and its slice tickets
`docs/architecture/slices/NN-<slice>.md` (scope `C4:slice-NN`). The step
starts only when C1, C2 and every `C3: required` document are `Approved`. No
code is written until the user approves the reviewed build plan.

Round contracts (inputs, outputs, result summaries) are in `rounds.md`; ledger
rules are in `ledger.md`; glossary and ADR rules are in `domain-language.md`.
This file says what the build plan and tickets contain and how the slices run.

## Seed questions

The grill round for `c4-plan` seeds the decision tree with these branches,
starting from the approved C2 and C3 documents, and grills until the frontier
is empty:

*   Toolchain per container: language, framework, package manager, versions.
*   Build and test commands per container, and one command that builds and
    tests the whole project.
*   Code standards: formatter, linter and the conventions a reviewer checks.
*   Integration branch: the branch slices merge into (default: the branch that
    is checked out when the plan is approved).
*   Worktree root: where slice worktrees are created (suggest a sibling folder
    of the project, which lies outside it), or `none` to run slices on slice
    branches in the project checkout.
*   Slice order: which CUJ the walking skeleton carries, and which CUJs follow.
*   Slice granularity: too coarse or too fine; which tickets should be merged
    or split.

## Build plan template

```markdown
# C4: Build Plan

**Status:** Draft

## Overview

## File Tree

(Target tree: each C2 container is a top-level project; each C3 component is
a module in it, named with its interface.)

## Toolchain

| Container | Language and framework | Package manager | Versions |
| :-------- | :--------------------- | :-------------- | :------- |

## Build and Test Commands

| Container | Build | Test |
| :-------- | :---- | :--- |

Whole project: `<command>`

## Code Standards

## Branches and Worktrees

Integration branch: `<branch>`
Worktree root: `<path>` or `none`

## Slices

| Slice | Ticket | CUJ | Waits On |
| :---- | :----- | :-- | :------- |

## Target Scope & File Boundary

(The union of every ticket's Allowed Paths. No round writes outside it.)

## Open Questions
```

Notes:

*   `**Status:**` is `Draft`, `Approved` or `Implemented`. Tickets carry no
    Status line; the ledger tracks them.
*   Use the exact container and component names from C2, C3 and `GLOSSARY.md`.
*   The plan is a document only. The draft round writes no code, build files
    or configuration.

## Slice ticket template

```markdown
# NN: <slice title>

**What to build:** the end-to-end behavior this slice makes work, from the
user's point of view.

## Components

(C3 components this slice touches, with their containers.)

## Test Seams

(The agreed seams from the C3 Test Seams tables that this slice tests at.)

## Acceptance Criteria

- [ ] (Given/When/Then taken from a C1 CUJ)

## Allowed Paths

(Path globs relative to the project root, tests included.)

## Waits On

(Ticket numbers that must be done first; "None" for slice 01.)
```

## Slicing rules

*   **Vertical slices.** Each slice cuts a narrow but complete path through
    every layer it needs (data, interface, user-facing behavior and tests), is
    verifiable on its own, and fits one fresh subagent's context. Never slice
    by layer.
*   **Walking skeleton.** Slice 01 is the walking skeleton: one CUJ end to end
    through the real containers. Its Allowed Paths also include the
    scaffolding: build files, CI configuration, the root `README.md` and
    `AGENTS.md` (which records the code standards and the build and test
    commands).
*   **Waits On.** Every other ticket waits on 01, plus only the tickets that
    genuinely gate it. A ticket whose tickets are all done is ready.
*   **Allowed Paths.** Unlike upstream tickets, these tickets name paths: the
    path check needs them. Keep them as narrow as the slice allows; two tickets
    that may run in one batch should overlap as little as possible.
*   **Wide refactors** that no vertical slice can land green run as
    expand, migrate in batches, then contract, each its own ticket.

## Ready for review

*   Every C2 container appears in the File Tree, Toolchain and Build and Test
    Commands.
*   Every C3 component maps to a module and is touched by at least one ticket.
*   Every C1 CUJ is carried by at least one ticket's Acceptance Criteria.
*   Every ticket names Components, Test Seams from C3, Acceptance Criteria,
    Allowed Paths and Waits On; Waits On has no cycles.
*   Slice 01 is the walking skeleton and its Allowed Paths include the
    scaffolding.
*   The Target Scope & File Boundary equals the union of all Allowed Paths.
*   Branches and Worktrees names the integration branch and a worktree root
    (or `none`).
*   No open question blocks slice 01.

## Slice loop

The orchestrator runs this loop after build-plan approval.

**Tasks.** When the plan is approved, add per ticket, in ticket order, the
`C4:slice-NN` tasks `implement`, `merge`, `verify` and `code-review`, each
depending on the one before. Each `implement` depends on the build plan's
`approve` and on the last `code-review` of every ticket in Waits On. Then add
one `C4` `drift` task that depends on every slice's last `code-review`.

**Worktree root.** A worktree root outside the project needs the user's
consent: at the build plan's `approve` gate, name the worktree root and say
that slice rounds will write there; approval confirms it. No worktree exists before that approval. With worktree root
`none`, or if the user declines worktrees, each round works on its slice branch
in the project checkout and returns the checkout to the integration branch
before it finishes; slices then run strictly one after another.

**Batches.** Slice 01 runs alone as batch `B1`. Each later batch is every
slice whose `implement` is ready, and in no batch, when the batch starts. The
orchestrator records batch membership and gate approvals in the ledger, and
next-ready follows them, by the batch rule in `ledger.md`, so batches survive a
resumed session. Within a batch, run the tasks in ledger order, one round at a
time. Each slice goes through:

1.  **Implement.** A fresh implementer subagent works red-green at the
    ticket's Test Seams on branch `c4/NN-<slice>`, created from the integration
    branch, in a worktree under the worktree root (or in the project checkout
    when it is `none`). It commits its work on that branch.
2.  **Path check.** The implement round's declared outputs are the ticket's
    Allowed Paths (see Path checks).
3.  **Merge.** A fresh merge subagent merges the slice branch into the
    integration branch with `--no-commit`, checks the staged paths against the
    batch's Allowed Paths, and commits only when every path is inside them
    (otherwise it aborts the merge and returns `needs_user`). It resolves
    conflicts only within those paths and removes the slice worktree; the
    branch stays.
4.  **Verify.** A fresh verify subagent runs the plan's Build and Test Commands
    on the integration branch and returns `PASS` or `FAIL: <summary>`.
5.  **Code review.** A fresh read-only subagent reviews the slice diff and
    returns `APPROVED` or `BLOCKING: <findings>`.

A `FAIL`, a `BLOCKING` result or a path-check violation on the slice branch
adds a `fix` chain by the ledger's adding and superseding rules; tasks that
waited on the slice's old `code-review` (later slices' `implement`, the
`drift` task) then wait on the chain's new one. A `fix` round works on the
slice branch the way the implement round did; the chain's `merge`, `verify`
and `code-review` then run again.

**Batch gate.** When every slice in the open batch has its last `code-review`
done, show each slice's verify and code-review summaries and ask whether to
start the next batch. On approval, record `Bn approved` as the ledger's batch
rule says. Otherwise append the requested change to
`docs/architecture/decisions/c4-plan.answers.md`, then add a `fix` chain for
the slice that names the entry, or a build-plan `revise` when a ticket itself
must change; the batch stays open and the gate is asked again.

## Path checks

Before each `implement`, `fix` and `merge` round, take the SKILL.md snapshot of
the project checkout and record the integration branch head
(`git rev-parse <integration-branch>`). After the round, collect the changed
paths:

*   in the project checkout, by the snapshot comparison in SKILL.md;
*   commits on the integration branch: `git diff --name-only <recorded-head>
    <integration-branch>`;
*   for `implement` and `fix`, the slice-branch diff:
    `git diff --name-only <integration-branch>...c4/NN-<slice>`, plus
    `git status --porcelain --untracked-files=all` in the slice worktree.

Compare them with the allowed set: the ticket's Allowed Paths for `implement`
and `fix`, the union of the batch's Allowed Paths for `merge`. A path outside
it is a violation; show it to the user. What happens next depends on where the
violation is:

*   **On the slice branch or in the slice worktree:** add a `fix` chain whose
    round reverts the out-of-bounds changes. The slice does not merge until a
    path check passes. To keep such a change instead, the ticket's Allowed
    Paths must first change through a build-plan `revise`.
*   **Elsewhere** (changes left in the project checkout outside the slice
    branch, or commits an `implement` or `fix` round made on the integration
    branch): a `fix` round cannot reach them. Ask the SKILL.md keep-or-revert question and mark the task `blocked`
    until the user has resolved every such path.

A merge round checks its staged paths before committing, so an out-of-bounds
merge is never committed; a merge commit that still shows one is handled as
"elsewhere".

## Implement rounds: red-green

*   Read `GLOSSARY.md` so test names use the project's terms, and respect the
    ADRs in `docs/adr/`.
*   Test only at the ticket's Test Seams, which the C3 document already agreed.
    Test behavior through the public interface, never internals.
*   **Red before green.** Write one failing test, run it to see it fail, then
    write only enough code to pass it. One seam, one test, one minimal change
    per cycle. Do not write all tests first.
*   Take expected values from an independent source (a worked example, the
    ticket's Acceptance Criteria), never by recomputing them the way the code
    does.
*   Refactoring belongs to the code review, not the red-green loop.
*   A `fix` round fixes only the listed findings, failure or out-of-bounds
    paths, with a failing test first where the fix changes behavior.

## Code review: two axes

The code-review round reports two axes separately and never merges or reranks
their findings:

*   **Standards:** does the diff follow the plan's Code Standards and
    `AGENTS.md`? Cite the rule. Possible code smells (mysterious name,
    duplicated code, feature envy, speculative generality and the like) are
    judgement calls, never hard violations; a documented standard overrides
    them, and anything tooling already enforces is skipped.
*   **Spec:** does the diff implement the C3 interfaces it touches and the
    ticket? Report missing or partial Acceptance Criteria, behavior the ticket
    did not ask for, and interface mismatches, quoting the ticket or C3 line.

Only a hard Standards violation or a Spec finding is `BLOCKING`. A Spec finding
that shows the C3 interface itself is wrong is a contradiction.

## Finish

When every slice is done, the `drift` round reads `egm-drift-report`'s
SKILL.md (not through a Skill tool), follows it on `docs/architecture/`
against the built code, and writes its report. After the user settles each finding (update the document through a
reopen, or the code through a `fix` chain), the orchestrator sets each fully
implemented document to `Implemented`: C1, C2 and the build plan when every
slice is done, and a C3 document when every slice touching its container is
done.

## Contradictions while building

When a round reports that the code needs something an approved document does
not allow:

1.  Stop: dispatch no further slice rounds; in-progress slice tasks stay
    unmerged.
2.  Apply the reopen rule in `ledger.md` to the contradicted level. The build
    plan returns to `Draft` too and is grilled again before any slice resumes.
3.  For slice tasks the reopen rule is narrowed: done slices whose Components
    include an affected component become `stale` with the note
    "rework against revised C3"; their code stays. Done slices that touch no
    affected component stay `done`.
4.  When the build plan is approved again, reconcile the slice tasks with the
    new tickets: add tasks for new tickets, mark tasks for removed tickets
    `done` with a note, and run each stale `implement` as a rework of the
    existing code against the revised C3 document and ticket.
