## Execution Instructions

*   **Design-Only Scope**: You are strictly forbidden from
    writing, modifying, or building any production implementation files (e.g.,
    `.h`, `.cc`, `.py`, `.go`) in the source tree. You may only write code
    inside a markdown draft block or in a temporary scratchpad file.
    *   **Scratchpad Location (CRITICAL)**: You MUST write any temporary
        scratchpad code files ONLY outside the project source tree, in your
        conversation's active scratch directory or, if your harness has none,
        a new private directory created with `mktemp -d`. If neither is
        available, keep the code in a markdown draft block. Do not use fixed,
        shared paths such as `/tmp/scratch.py`. You are STRICTLY FORBIDDEN
        from creating `.h`, `.cc`, `.py`, `.go`, or any other code files
        anywhere inside the project source tree.
    *   **HOW TO RESPOND**: If the user asks for production implementation while
        this design workflow is active, explain that it produces design documents
        and illustrative code only. Label any markdown or scratchpad example
        clearly. Do not imply that production files were changed. Ask whether to
        continue the design or leave the workflow for implementation.
*   **Explicit Consensus Gates**: You must confirm with the user and achieve
    explicit agreement at each step transition. Do not save the document or move
    to the next step without the user's explicit "go-ahead". Do not move on
    easily. Challenge the user at every step.
*   **ONE QUESTION AT A TIME (CRITICAL)**: You are strictly forbidden from
    asking more than one question in a single response. You must present exactly
    one question or request for clarification, wait for the user's response, and
    only then proceed. Do not bundle questions or present a list of questions
    for the user to answer at once.
*   **NO SUMMARIES (CRITICAL)**: You MUST NOT include a "Summary of work",
    "Status", "Adherence", or "Rule checklist" in your final response. Respond
    only with the technical content and next steps.
*   **Contradiction Auditing (MUST ENFORCE - CRITICAL)**: If you detect a
    contradiction between the user's new requests and earlier
    goals/architecture, **you MUST NOT modify any files**. You must only respond
    to the user in plain text, point out the contradiction, and ask for
    resolution. You are strictly forbidden from planning or executing any
    file-writing/editing tool in the same turn as you discover a contradiction.

**c4 exceptions**: These apply only while the `c4` skill runs and
override the rules above where they conflict.

*   **Code writing**: Allowed only for implement, fix and merge rounds in the C4
    step, after build-plan approval, inside the ticket's allowed paths.
*   **Round writes**: A round subagent may write its declared output files
    without a per-file go-ahead. Drafts keep `**Status:** Draft` until the user
    approves.
*   **Contradictions in rounds**: A round that finds a contradiction finishes
    its declared outputs and reports it. The orchestrator then makes no further
    changes until the user resolves it.
*   **Interview rounds**: A grilling round may present several numbered
    questions with recommended answers. Every other gate still asks one
    question.
*   **Orchestrator writes**: The main session writes only the files listed
    in the `c4` SKILL.md: the ledger `docs/architecture/c4-tasks.md`; the
    append-only answers files in `docs/architecture/decisions/`;
    `**Status:**` lines; replacement text the user approved at a resolve
    gate, applied verbatim; the user's gate decisions recorded verbatim in the
    round report, marked `Status: resolved`; and, under direct dispatch, each
    reviewer's returned findings, saved verbatim to the scope's review folder.
