# Domain Docs

How an agent should read this repo's domain documentation before working on the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — the vocabulary this repository uses, and the words it
  deliberately avoids.
- **`docs/adr/`** — read the decisions that touch the area you are about to work in.
  `docs/adr/index.md` lists them.

If any of these files don't exist, **proceed silently**. Don't flag their absence, and don't
suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and
`/improve-codebase-architecture`) creates them lazily when terms or decisions actually get
resolved.

## File structure

Single-context repo (this repo):

```
/
├── CONTEXT.md
├── memory/constitution.md
├── docs/adr/
│   ├── index.md
│   ├── 0001-....md
│   └── 0002-....md
└── fairdm_docs/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, say, or a test name), use the term as
defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

Two are worth repeating because the current code breaks both:

- **"Config" is banned unqualified.** It already means four different things in this codebase.
  Say *declarative configuration*, *build settings*, *registry entry*, or *Django settings*.
- **The directive is `autodoc-model`, singular.** The module is `autodoc_models` and the README
  has called it `autodoc-models`. Only the singular hyphenated form is real.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing
language the project doesn't use (reconsider) or there's a real gap (note it for
`/domain-modeling`).

## The gap between the README and the code

This package's README describes behaviour the code does not currently implement, in more than one
place. Treat the README as a statement of intent and the code as the statement of fact, and when
you find them disagreeing, say so in the issue rather than assuming either one is right.

## Flag conflicts with a recorded decision

If your output contradicts a decision in `docs/adr/`, surface it explicitly rather than silently
overriding:

> _Contradicts ADR 0002 (…) — but worth reopening because…_
