# C3 Component playbook

Adapted from mattpocock/skills (skills/engineering/codebase-design/SKILL.md), MIT License. See THIRD_PARTY_NOTICES.md.

Level playbook for `docs/architecture/c3-<container>.md` (scope
`C3:<container>`). Audience: developers. The document opens one C2 container
into its components. Code and classes belong to the C4 step; other containers'
internals belong to their own C3 documents. C3 is written once per container
marked `C3: required` in C2.

Glossary and ADR rules are in `domain-language.md`. Round mechanics are in
`rounds.md`. Diagram notation is in `mermaid-c4.md`.

## Design vocabulary

A C3 component is a **deep module**: a lot of behavior behind a small
interface. Upstream codebase-design avoids the word "component"; here the C4
term wins, and the other terms carry over.

*   **Interface:** everything a caller must know to use the component: the
    signature, plus invariants, ordering constraints, error modes, required
    configuration and performance characteristics.
*   **Depth:** the behavior a caller or test can exercise per unit of interface
    they must learn. A deep component hides substantial behavior behind a small
    interface; a shallow one has an interface nearly as complex as its
    implementation.
*   **Seam:** a place where behavior can change without editing in that place;
    the location of the interface. In C3 the seam is the **test seam**: where
    the C4 step tests the component without reaching into its internals.
*   **Deletion test:** imagine deleting the component. If complexity vanishes,
    it was a pass-through; if it reappears across callers, it earns its keep.
*   **The interface is the test surface.** Callers and tests cross the same
    seam. A component that must be tested past its interface is probably the
    wrong shape.
*   **One adapter is a hypothetical seam; two adapters make a real one.**
    Introduce a seam only where something varies across it (a real database and
    an in-memory fake count as two).

Design for testability: accept dependencies instead of creating them, return
results instead of producing side effects, and keep the surface small.

## Seed questions

Seed the decision tree (`<scope>.tree.md`) with these branches, then grill
until the frontier is empty. Start from the approved C1 and C2 documents and the
container's row and relationships in C2.

*   Components and responsibilities: what are the deep modules, and what does
    each own?
*   Interfaces: for each component, the smallest interface a caller needs, with
    its invariants and error modes.
*   Dependencies: what does each component depend on, and in which direction?
*   Data ownership: which component owns which data in this container?
*   Error handling: which failures cross a seam, and how are they reported?
*   Test seams: where is each component tested, and what varies across the seam
    (a real and a fake adapter)?
*   Design it twice: for each non-obvious interface, which radically different
    alternative was considered, and why was it rejected?

## Document template

```markdown
# C3: Components of <container>

**Status:** Draft

## Overview

## Components

| Component | Responsibility | Interface summary | Depends on |
| :-------- | :------------- | :---------------- | :--------- |

## Component Diagram

(`C4Component` diagram, then the `**Legend**` line and `Shape | Meaning` table)

## Interfaces

### <Component>

(Prose and pseudo-signatures: operations, invariants, ordering, error modes)

## Test Seams

| Component | Seam | Adapters | What a test asserts |
| :-------- | :--- | :------- | :------------------ |

## CUJ Trace

### CUJ-1: <name>

1.  <Container or component> ... -> <component> ...

## Error Handling

## Open Questions
```

Notes:

*   `**Status:**` is `Draft`, `Approved` or `Implemented`.
*   Use the exact container and relationship names from C2 and the terms in
    `GLOSSARY.md`.
*   Write interfaces as prose and pseudo-signatures in no particular language,
    and describe behavior, not implementation. Never write real code.
*   The CUJ trace follows each C1 CUJ that crosses this container, naming the
    components involved. A CUJ that does not touch the container is left out.
*   Open Questions lists unresolved items with an owner, not hidden gaps.

## Diagram

Use `C4Component`: one `Container_Boundary` for this container, every component
as `Component`, and the C2 containers it talks to outside the boundary as
`Container` or `ContainerDb`. Every `Rel` states intent; add a protocol only on
a relationship that crosses the container boundary. Show no classes or code.
Follow the notation rules and the legend format in `mermaid-c4.md`.

## Ready for review

*   Every C2 relationship touching this container is realized by a component.
*   Every component has an interface and an agreed test seam.
*   Every component passes the deletion test.
*   Every CUJ that crosses this container is traceable through its components.
*   No open question blocks the C4 build plan.
