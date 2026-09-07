# Research — 002

Four questions had to be answered before the plan could be written. Each was settled by running
the command against a real, temporary project, not by reading the source.

## Q1 — Can `fairdm-docs build` be proven end to end, or only by inspecting arguments?

A1 found that 23 of `tests/test_cli.py`'s 31 tests replace `sphinx.cmd.build.main` or
`subprocess.run` with a stand-in, and that no test anywhere runs a real build through the command.
Whether a real build is feasible inside the suite, and fast enough to run on every change, was
unverified.

**Probe.** A temporary project declaring `name` and `version` only, with `docs/index.rst` as its
sole page, built by calling `fairdm_docs.cli.main()` directly with `sys.argv` set to
`["fairdm-docs", "build"]`.

**Result.** `build succeeded, 1 warning.` The warning is `autodoc2_packages must not be empty`,
which is R6's, not this specification's. `docs/_build/html/index.html` exists and contains
`Probe`. Elapsed: well under a second.

**Settled:** feasible, fast, and the index must be `.rst` — the same constraint 001's research
recorded, for the same reason (R3 owns the Markdown path). US1's acceptance scenarios are proven
by reading rendered HTML off disk, not by asserting on argv.

## Q2 — Does a malformed `pyproject.toml` actually reach the developer as a traceback?

A1 traced this from the exception-handling code without running it. ADR 0008 requires a single
error type; confirming the violation needed the failure to happen.

**Probe.** A `pyproject.toml` containing `[project\nname = probe` — an unterminated table header —
in a project otherwise identical to Q1's, with `fairdm-docs build` run against it.

**Result.** An uncaught `tomllib.TOMLDecodeError` propagates out of `utils.py:98`, through
`config.py:83` (which catches only `FileNotFoundError`) and `cli.py:195` (which catches only
`ConfigError`), to the interpreter — 15 frames of Python traceback, ending in `Expected ']' at the
end of a table declaration (at line 1, column 9)`.

**Settled:** confirmed rather than inferred. This is a defect against ADR 0008 and is fixed in
this run, per D7.

## Q3 — What actually happens when the preview port is occupied?

The spec requires the command to stop before starting anything, naming the port and the setting
that changes it.

**Probe.** A socket bound to port 5000, then `fairdm-docs build --live` run against a project
otherwise identical to Q1's.

**Result.**

```
❌ Error: Port 5000 is already in use.
   Configure a different port in pyproject.toml:
   [tool.fairdm.docs]
   port = 5001
EXIT CODE 1
```

No server process is started; the message names the port and the fix.

**Settled:** already correct. FR-010 is satisfied by existing code; it needs a test, not a
change.

## Q4 — Does a redirect actually fail the check today?

A1 read `cli.py:271-274` and concluded a redirect is treated as broken, because the code matches
the substring `": [redirected]"` against each line of the builder's report. That conclusion was
wrong, and only running it against a real redirect showed why.

**Probe.** `fairdm-docs check` against a page linking only `https://httpbin.org/redirect-to?url=…`,
which redirects with a 302.

**Result.** The builder's actual output line is:

```
index.rst:4: [redirected with Found] https://httpbin.org/redirect-to?url=https://example.com to https://example.com
```

`"with Found"` sits where the matching code expects a closing bracket, so
`": [redirected]" in line.lower()` never matches. The command exits 0 and prints "All links are
valid!" — the redirect is recorded in `output.txt` and never reaches the developer.

**Settled:** the code does not fail on a redirect, by accident rather than by design — the match
was written to catch it and does not. What the specification requires and the code lacks is the
other half: telling the developer a redirect happened. `decisions.md` D5 was corrected after this
probe; the earlier assessment (a workspace record, not part of this repository) is corrected
alongside it.

## Structure

Two findings shape the plan. First, the module under test is exercisable directly — `cli.py`'s
commands can be invoked as ordinary functions with `sys.argv` set, with no need for a subprocess
or a `CliRunner` layer between the test and the code, which keeps the real-build tests as fast as
the mocked ones they replace. Second, the linkcheck output parser in `check()` needs to change
regardless of D5's exit-code finding, because FR-013 requires a redirect to be reported and it
currently is not — the parsing loop is rewritten to classify each line into broken, redirected, or
neither, rather than collapsing broken and (attempted) redirected detection into one list.
