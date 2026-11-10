# C4 Model Standard

This standard defines the quality bar for C4 architecture documents (C1 System
Context, C2 Containers, C3 Components) and for the C4 build plan. Documents are
reviewed by a reviewer with no memory of the drafting conversation, so a
statement is credible only if the document or its inputs support it.

## Core Principle

A C4 document passes if a reader at its audience level can understand the
system from the document alone, its diagram follows the notation, every
statement traces to the scope's decision files or to an upper level document,
and its level's Ready for review criteria hold.

## 0. Context Sufficiency (Prerequisite Check)

*   **Inputs**: The reviewer must have the document under review, the upper
    level documents it builds on, and the decision files for the scope
    (`<scope>.tree.md` and `<scope>.answers.md`). If the level cannot be
    identified or the decision files are missing, fail immediately with a
    request for context.

## 1. Diagram Notation

*   **Title**: Each diagram has a `title` line that names the diagram type and
    scope.
*   **Legend**: Each diagram is followed by a Markdown legend table that
    explains its shapes and lines.
*   **Element completeness**: Each element has a type and a description.
    Containers and components also name their technology.
*   **Relationship labels**: Each relationship has an intent label. Between
    containers it also names the protocol. A bare "Uses" fails.
*   **Valid syntax**: The diagram is valid Mermaid C4 (`C4Context`,
    `C4Container`, `C4Component` or `C4Deployment`) that matches the level.

## 2. Level Discipline

*   **No level mixing**: C1 shows people and systems, not containers or
    technology. C2 shows containers, not components. C3 shows the components
    of one container, not code or the internals of other containers.
*   **Deployment diagrams**: Show C2 containers on infrastructure; add no new
    containers.
*   **Audience fit**: C1 is readable by non-technical staff. C2 serves
    technical staff. C3 serves developers.

## 3. Naming and Traceability

*   **Consistent names**: Names match the upper level document and the terms in
    `GLOSSARY.md`. Renamed or synonymous terms fail.
*   **Traceability**: Every substantive statement traces to an entry in the
    decision files or to an upper level document. Unsupported invention fails.
*   **Contradictions**: The document does not contradict a decided answer or an
    upper level document. A deferred question is listed in Open Questions, not
    silently decided.

## 4. Required Sections per Level

*   **C1**: Overview, Problem, Goals, Non-Goals, People, External Systems,
    CUJs (Given/When/Then), System Context diagram, Quality Attributes and
    Constraints, Open Questions.
*   **C2**: Overview, Container table (name, type, technology, responsibility,
    data owned, `C3: required` or `C3: skip (<reason>)`), Container diagram,
    Relationships table (from, to, intent, protocol), CUJ walkthrough,
    Cross-cutting Concerns, Key Decisions, Alternatives Considered, Open
    Questions. A Deployment diagram is optional.
*   **C3**: Overview, Component table (name, responsibility, interface
    summary, depends on), Component diagram, Interfaces, Test Seams, CUJ
    trace, Error Handling, Open Questions.

A missing section fails.

## 5. Ready for review

Check the Ready for review criteria of the reviewed level in its playbook. If
the playbook is not provided, apply these:

*   **C1**: Every person and external system has a description; every CUJ uses
    only diagram elements; no open question blocks C2.
*   **C2**: Every C1 element is accounted for; every container has technology
    and responsibility; every relationship has intent and protocol; every CUJ is
    traceable through the containers.
*   **C3**: Every C2 relationship touching this container is realized by a
    component; every component has an agreed test seam.
*   **Build plan**: Follow the implementation readiness standard; this standard
    applies to its notation, naming and traceability only.
