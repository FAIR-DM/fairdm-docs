# ADR 0009 — `check` resolves external addresses, and reports a redirect separately from a failure

**Status:** accepted

## Decision

`fairdm-docs check` validates the external addresses a portal's documentation links to. It does
not validate internal cross-references — those are the builder's own concern, reported as
warnings during a build, and turning a warning into a failure is a publication decision this
command does not make.

An address that resolves by redirecting is not a failure. It is reported to the developer under
its own heading, separately from addresses that did not resolve, and it never by itself causes a
non-zero exit.

## Why

The command's own help text once claimed it detected "broken internal and external links", but
nothing in the package ever validated an internal cross-reference — the claim was never true. A
command that advertises a capability it does not have is worse than one that has a narrower scope
and says so, because a developer who trusts the claim finds out the hard way, in someone else's
review.

A redirect means the address still resolves. Failing a check because a site the documentation
links to moved its page makes the check fire on other people's housekeeping, and a check that
cries wolf gets switched off. It is still worth surfacing — a redirect today is sometimes a dead
link next year — which is why it is reported rather than simply ignored.

## Revisit if

Internal cross-reference validation, or turning a build warning into a check failure, is
specified as a deliberate publication gate — at that point it is a new requirement on this
command, not an extension of what "broken" already means here.
