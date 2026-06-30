# Python Backend Standards

This document defines the Python development rules for repo-local work on the DeerFlow research platform. It is intentionally compatible with the current backend style, toolchain, and architecture.

## Source priority

Project-specific rules override generic Python style references.

Read in this order:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `CONTRIBUTING.md`
4. `backend/ruff.toml`
5. External references

## Code style

- Use Python 3.12-compatible syntax only.
- Format with `ruff format`; lint with `ruff check`.
- Respect the repo formatter settings:
  - double quotes
  - spaces for indentation
  - import sorting handled by Ruff/isort
  - line length follows the repo config, not default PEP 8 width
- Do not hand-format against the formatter. If `ruff format` rewrites it and readability remains acceptable, keep the formatted result.

## Naming

- Modules and packages: short, lowercase names; underscores only when they clearly improve readability.
- Classes, TypedDicts, dataclasses, exceptions: `CapWords`.
- Functions, methods, local variables, helpers: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- First parameters: `self` / `cls`.
- Use a single leading underscore for non-public names.
- Avoid vague abbreviations unless they are already dominant in the project domain, such as `PDP`, `MCP`, `SSE`, or `ADR`.

## Comments and docstrings

- Comments explain why, invariants, safety constraints, or non-obvious trade-offs. They should not narrate obvious syntax.
- Keep comments true; stale comments are worse than no comments.
- From this point forward, all newly added or modified code must use **Chinese comments**.
- Every newly added or modified non-trivial function must have a Chinese function-level explanation.
- Every key flow, state machine step, idempotence guard, complex branch, and boundary translation must have Chinese inline comments where the intent would otherwise be easy to miss.
- Historical untouched code does not need to be rewritten just to change comment language.
- Public modules, public functions, public classes, reducers, lifecycle hooks, and boundary helpers should have docstrings.
- Use triple double quotes for docstrings.
- Prefer short one-line docstrings when the summary fits.
- Multi-line docstrings should start with a summary line and only include details when they add real value.
- For tricky non-public helpers, add either a short docstring or a targeted inline comment directly under the `def`.

## Module structure

- Preserve the backend split:
  - `deerflow.*` owns reusable harness/runtime/framework logic
  - `app.*` owns Gateway and app-specific orchestration
- Do not import `app.*` from `deerflow.*`.
- Keep routers thin:
  - parse and validate request
  - call service/domain/deep module
  - translate boundary errors to HTTP
- Keep domain rules and state transitions in deep modules with narrow interfaces.
- Prefer a focused new module over growing a router or service into a multi-concern file.

## Function design

- Prefer small, single-purpose functions, but do not fragment simple logic pointlessly.
- Make side effects explicit at function boundaries.
- Keep transformation functions pure where possible, especially for:
  - normalization
  - scoring
  - deduplication
  - version derivation
  - state transition calculation
- Validate at boundaries, not redundantly in every inner helper.
- Fail closed on conflicting state rather than silently choosing one path.

## Idempotence and state safety

- Assume retries, repeated UI actions, and repeated scheduler executions will happen.
- Every write path that can be retried must be idempotent by key, version, or status transition.
- Never create duplicate `Paper Record`, PDF ingest, `Analysis View`, or `Proposal Draft` versions from the same logical event.
- Separate raw truth from derived state:
  - raw objects are guarded against accidental overwrite
  - derived objects are versioned and recomputable
- If a reducer or merge path detects a conflict that indicates an invariant violation, raise instead of merging heuristically.

## Async and I/O rules

- Do not perform blocking disk or network I/O on the event loop.
- Reuse the repo's existing async/offload patterns such as `asyncio.to_thread(...)` where appropriate.
- If adding file or DB behavior inside async paths, either:
  - use a native async API, or
  - offload blocking work explicitly
- Add or update regression coverage in the existing blocking-I/O guard tests when you introduce new async file or network paths.

## Logging and errors

- Use module-level loggers: `logger = logging.getLogger(__name__)`.
- Log at the boundary where the failure becomes actionable.
- Use `logger.exception(...)` when preserving traceback matters.
- Do not swallow exceptions silently.
- Domain/deep modules should raise meaningful exceptions or explicit guard errors.
- HTTP translation belongs at the Gateway boundary, not deep inside reusable logic.

## Testing expectations

- Test external behavior, not private implementation details.
- Follow the existing backend pattern: `backend/tests/test_*.py`.
- Reuse fixtures/helpers before inventing new scaffolding.
- Add narrow regression tests for:
  - state transitions
  - idempotence
  - deduplication
  - versioning
  - boundary validation
  - blocking-I/O regressions where relevant
- For new deep modules, prefer direct unit tests plus one integration path that proves wiring.

## Mandatory review gate

- All Python backend changes must pass:
  - lint
  - relevant tests
  - mandatory `$review` against `main`
- A change is not done if review reports unresolved hard findings on either:
  - Standards
  - Spec

## External references

- PEP 8: https://peps.python.org/pep-0008/
- PEP 257: https://peps.python.org/pep-0257/
- Python Logging HOWTO: https://docs.python.org/3/howto/logging.html
- pytest good practices: https://docs.pytest.org/en/stable/explanation/goodpractices.html
