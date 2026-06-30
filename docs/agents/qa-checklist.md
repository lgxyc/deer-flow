# QA Checklist

Use this checklist before marking any issue done.

## 1. Scope check

- [ ] I read the parent PRD.
- [ ] I read the current issue in full.
- [ ] I read `AGENTS.md`, `backend/AGENTS.md`, `CONTEXT.md`, relevant ADRs, and this QA checklist.
- [ ] I stayed inside the issue's declared `Working Set` unless a real dependency forced expansion.

## 2. Standards check

- [ ] Raw truth and derived state are still separated correctly.
- [ ] New write paths are idempotent or versioned as required.
- [ ] Routers/pages remain thin; domain logic lives in deep modules.
- [ ] No forbidden `deerflow.* -> app.*` dependency was introduced.
- [ ] Comments explain invariants or trade-offs, not obvious syntax.
- [ ] Public or tricky Python interfaces have appropriate docstrings.
- [ ] Blocking I/O was not introduced onto async paths.

## 3. Verification check

- [ ] I ran the relevant backend lint command.
- [ ] I ran the relevant backend tests.
- [ ] I ran frontend checks/tests if the issue touched UI or API contracts.
- [ ] I updated docs when architecture, behavior, or workflow changed.

## 4. Mandatory review gate

- [ ] I ran the `$review` skill against `main`.
- [ ] Standards review returned no unresolved hard findings.
- [ ] Spec review returned no unresolved missing or wrong requirements.
- [ ] If review raised judgement calls only, I documented them explicitly in the completion summary.

## 5. Completion check

- [ ] Every acceptance criterion has concrete verification evidence.
- [ ] The branch contains only one issue's scope.
- [ ] Commit messages follow Conventional Commits.
- [ ] The final closing commit references the issue id.

If any item above is unchecked, the issue is not ready to mark done.
