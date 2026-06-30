# Domain Docs

How engineering skills should consume this repo's domain documentation for the research-platform work.

## Layout

This repo currently uses a **single-context** layout:

- Root `CONTEXT.md`
- Global ADRs under `docs/adr/`

Read those before proposing architecture, naming modules, or splitting work into issues.

## Before exploring, read these

- `CONTEXT.md`
- Relevant ADRs under `docs/adr/`
- `AGENTS.md`

If a topic is clearly frontend-only or backend-only, also read the more specific guide:

- `frontend/CLAUDE.md`
- `backend/CLAUDE.md`

## Vocabulary rules

- Use the glossary terms from `CONTEXT.md` in issue titles, PRDs, tests, and architecture notes.
- Do not replace glossary terms with loose synonyms once the project has chosen a name.
- If a new stable concept appears during design or implementation, add it to `CONTEXT.md` instead of inventing parallel vocabulary in tickets.

## ADR rules

- If a change would contradict an existing ADR, say so explicitly.
- If a decision is hard to reverse, surprising, and the result of a real trade-off, record a new ADR before or alongside implementation.
