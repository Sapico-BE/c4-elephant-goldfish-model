# C1 System Context playbook

Level playbook for `docs/architecture/c1-context.md` (scope `C1`). Audience:
everyone, including non-technical readers. The document shows the system as one
box, the people who use it and the systems it talks to. Containers and
technology belong to C2, not here.

Glossary and ADR rules are in `domain-language.md`. Round mechanics are in
`rounds.md`. Diagram notation is in `mermaid-c4.md`.

## Seed questions

Seed the decision tree (`<scope>.tree.md`) with these branches, then grill
until the frontier is empty:

*   Problem and purpose: what problem does the system solve, and for whom?
*   People and personas: who uses it, and what does each persona want?
*   External systems: which systems does it depend on, or which depend on it?
*   Critical user journeys (CUJs): which journeys must work for the system to
    be worth building?
*   Goals and non-goals: what is in scope, and what is deliberately out?
*   Scale, compliance and budget: users, volumes, regulation, cost limits.

## Document template

```markdown
# C1: System Context for <system>

**Status:** Draft

## Overview

## Problem

## Goals

## Non-Goals

## People

| Person | Description | Goal |
| :----- | :---------- | :--- |

## External Systems

| System | Description | Interaction |
| :----- | :---------- | :---------- |

## Critical User Journeys

### CUJ-1: <name>

*   **Given** ...
*   **When** ...
*   **Then** ...

## System Context Diagram

(`C4Context` diagram, then the `**Legend**` line and `Shape | Meaning` table)

## Quality Attributes and Constraints

## Open Questions
```

Notes:

*   `**Status:**` is `Draft`, `Approved` or `Implemented`.
*   Each CUJ mentions only people and systems that appear in the diagram.
*   Open Questions lists unresolved items with an owner, not hidden gaps.

## Diagram

Use `C4Context`. Show the system as one `System`, every person as `Person` and
every external system as `System_Ext`. Include no containers and no
technology. Follow the notation rules and the legend format (a `**Legend**` line, then a
two-column `Shape | Meaning` table) in `mermaid-c4.md`.

## Ready for review

*   Every person and external system has a description.
*   Every CUJ uses only elements that appear in the diagram.
*   No open question blocks C2.
