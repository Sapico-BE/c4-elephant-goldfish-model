# Domain language

Adapted from mattpocock/skills (skills/engineering/domain-modeling/SKILL.md), MIT License. See THIRD_PARTY_NOTICES.md.

Follow these rules when drafting or revising a level document. They keep the
project's vocabulary consistent and record decisions worth remembering.

## Glossary

`GLOSSARY.md` sits at the project root. Create it when the first term is
resolved. Every name that appears in a diagram has an entry. A glossary is a
glossary and nothing else: no implementation details, no specs, no scratch
notes.

- Be opinionated. Pick one word per concept and list the rest under `_Avoid_`.
- Keep definitions to one or two sentences: what it is, not what it does.
- Include only terms specific to this project, not general programming
  concepts.
- Group terms under subheadings when clusters appear.

```md
# {Context name}

{One or two sentences on what this context is and why it exists.}

## Language

**Order**:
A request to buy goods, placed by a customer.
_Avoid_: Purchase, transaction
```

When a user's wording conflicts with a glossary entry, or a term is vague or
overloaded, do not silently pick one. Record the conflict as an Open Question
or return `needs_user` with the specific choice.

## Decisions (ADRs)

Write an ADR in `docs/adr/NNNN-<slug>.md` only when all three hold:

1. The decision is hard to reverse: changing your mind later is costly.
2. It is surprising without context: a reader will wonder why it was done this
   way.
3. It is the result of a real trade-off: genuine alternatives existed and one
   was chosen for specific reasons.

If any is missing, skip the ADR. Create `docs/adr/` when the first ADR is
needed. Number sequentially: scan for the highest existing number and add one.

```md
# {Short title of the decision}

{One to three sentences: the context, what was decided, and why.}
```

An ADR can be a single paragraph. Add a `Status` line, Considered Options, or
Consequences only when they add real value. Typical ADR subjects: system
shape, integration patterns between containers, technology choices with
lock-in, boundary and scope decisions, deliberate deviations from the obvious
path, constraints not visible in the design, and non-obvious rejected
alternatives.

Link ADRs from the level document's Key Decisions section.
