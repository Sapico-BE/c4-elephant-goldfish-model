# C2 Container playbook

Level playbook for `docs/architecture/c2-containers.md` (scope `C2`). Audience:
technical staff. The document opens the C1 system box into its containers:
separately deployable or runnable units and data stores, with the technology
each uses and the protocols between them. Components inside a container belong
to C3, not here.

Glossary and ADR rules are in `domain-language.md`. Round mechanics are in
`rounds.md`. Diagram notation is in `mermaid-c4.md`.

## Seed questions

Seed the decision tree (`<scope>.tree.md`) with these branches, then grill
until the frontier is empty. Start from the approved C1 document: every C1
person, external system and CUJ must end up accounted for.

*   Deployable units and data stores: which containers does the system need,
    and what does each own?
*   Technology per container: language, framework, runtime, data store.
*   Protocols: how do containers talk to each other and to external systems
    (format, sync or async)?
*   Hosting: where does each container run?
*   Authentication and authorization: who may call what, and how is identity
    carried between containers?
*   Observability: logs, metrics, traces, alerts.
*   For each container: does it need a C3 document? Ask whether its internals
    are non-trivial, or whether it is a managed or off-the-shelf product.

## Document template

```markdown
# C2: Containers for <system>

**Status:** Draft

## Overview

## Containers

| Container | Type | Technology | Responsibility | Data owned | C3 |
| :-------- | :--- | :--------- | :------------- | :--------- | :- |

## Container Diagram

(`C4Container` diagram, then the `**Legend**` line and `Shape | Meaning` table)

## Relationships

| From | To | Intent | Protocol |
| :--- | :- | :----- | :------- |

## CUJ Walkthrough

### CUJ-1: <name>

1.  <Person or system> ... -> <container> ...

## Deployment

(Optional: `C4Deployment` diagram and legend)

## Cross-cutting Concerns

## Key Decisions

## Alternatives Considered

## Open Questions
```

Notes:

*   `**Status:**` is `Draft`, `Approved` or `Implemented`.
*   The `C3` column holds `C3: required` or `C3: skip (<reason>)` for every
    container. The orchestrator reads it to add C3 tasks, so a container with a
    missing or other value blocks readiness. Use `C3: skip` for managed
    services, off-the-shelf products and containers too small to have internal
    structure worth documenting; the reason names which.
*   Name every C1 person, external system and CUJ as C1 does; the Containers
    and Relationships tables account for each of them.
*   Key Decisions links the ADRs in `docs/adr/` that this level created, using
    relative Markdown links. Alternatives Considered names each rejected option
    and why.
*   The CUJ walkthrough follows each C1 CUJ through the containers, step by
    step, naming the relationship used.
*   Open Questions lists unresolved items with an owner, not hidden gaps.

## Diagram

Use `C4Container`: one `System_Boundary` for the system, every container as
`Container` or `ContainerDb`, and the C1 people and external systems outside the
boundary as `Person` and `System_Ext`. Every `Rel` states intent in its label
and the protocol and format in the technology argument. Show no components.

The deployment diagram is optional. Add a `C4Deployment` diagram when hosting
matters to a decision. It shows the C2 containers on infrastructure nodes and
adds no new containers. Give it its own `title` and legend. Follow the notation
rules and the legend format in `mermaid-c4.md`.

## Ready for review

*   Every C1 element (person, external system) is accounted for.
*   Every container has technology and responsibility, and a `C3: required` or
    `C3: skip (<reason>)` value.
*   Every relationship has intent and protocol.
*   Every CUJ is traceable through the containers.
*   No open question blocks C3.
