# ADR 0010 — An interrupt exits 130, in every mode

**Status:** accepted

## Decision

When a developer interrupts `fairdm-docs` — an ordinary build, a check, or a live preview — the
command exits 130 and prints nothing that looks like a crash. Every command this package adds
follows the same convention.

## Why

130 is the shell convention for termination by `SIGINT`, and it is what a calling script tests
for. Before this decision, live preview alone exited 0 on interrupt, so a script watching for
success would call a session the developer killed a successful one, because the one command whose
whole purpose is running until interrupted was the one exception to the rule.

## Revisit if

A future command has a natural, successful completion that an interrupt could plausibly signal
rather than abort — nothing in this package currently does; every command runs until it finishes
or until the developer stops it.
