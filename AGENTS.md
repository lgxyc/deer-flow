# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Codex, and others) when working with code in this repository. It is the source of truth; the sibling `CLAUDE.md` imports it via `@AGENTS.md`.

It is the **monorepo orientation layer**: it maps the whole repo and points to the
module guides that own the depth. For anything inside a module, read that module's
guide rather than expecting full detail here:

- **[backend/AGENTS.md](backend/AGENTS.md)** — backend depth: harness/app split, agent &
  middleware chain, sandbox, MCP, skills, memory, IM channels, persistence/migrations,
  config system, test layout.
- **[frontend/AGENTS.md](frontend/AGENTS.md)** — frontend depth: Next.js App Router layout,
  thread/streaming data flow, code style, commands.

## Agent skills

### Issue tracker

Issues and PRDs for this working copy are tracked in GitHub Issues on `lgxyc/deer-flow`, not the upstream `origin` remote. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the canonical triage labels mapped in `docs/agents/triage-labels.md`. See `docs/agents/triage-labels.md`.

### Domain docs

This repo currently uses a single-context layout with one root `CONTEXT.md` and global ADRs under `docs/adr/`. See `docs/agents/domain.md`.

### Python backend standards

Python backend implementation rules for the research-platform work live in `docs/agents/python-backend-standards.md`.

### QA checklist

The mandatory completion gate lives in `docs/agents/qa-checklist.md`.

## What is DeerFlow

DeerFlow is a LangGraph-based AI super-agent system with a full-stack architecture. The
backend runs a "super agent" with sandboxed execution, persistent memory, subagent
delegation, and extensible tools (built-in, MCP, community), all per-thread isolated. The
frontend is a Next.js chat UI. External IM platforms (Feishu, Slack, Telegram, Discord,
DingTalk) bridge into the same agent through the Gateway.

## Service Topology

A single `make dev` / Docker stack runs four cooperating services:

| Service         | Port   | Role                                                                 |
| --------------- | ------ | ------------------------------------------------------------------- |
| **Nginx**       | `2026` | Unified reverse-proxy entry point — open this in the browser        |
| **Gateway API** | `8001` | FastAPI REST API + embedded LangGraph-compatible agent runtime      |
| **Frontend**    | `3000` | Next.js web interface                                               |
| **Provisioner** | `8002` | Optional — only when sandbox is configured for provisioner/K8s mode |

Nginx is the single public entry: it serves the frontend and proxies `/api/langgraph/*`
to the Gateway's LangGraph runtime, rewriting it to Gateway's native `/api/*` routes; all
other `/api/*` go straight to the Gateway REST routers. See
[backend/AGENTS.md](backend/AGENTS.md) for the runtime and router detail.

## Repository Map

```text
deer-flow/
├── Makefile                        # Root orchestration: drives the full stack (dev/start/stop, docker, setup)
├── config.example.yaml             # Template -> copy to config.yaml (gitignored) at repo root
├── extensions_config.example.json  # Template -> copy to extensions_config.json (gitignored): MCP servers + skills
├── backend/                        # Python backend — see backend/AGENTS.md
│   ├── Makefile                    # Per-module backend commands (dev, gateway, test, lint, migrate-rev)
│   ├── packages/harness/           # deerflow-harness package (import: deerflow.*) — agent framework
│   └── app/                        # FastAPI Gateway + IM channels (import: app.*)
├── frontend/                       # Next.js frontend (pnpm) — see frontend/AGENTS.md
├── docker/                         # docker-compose files, nginx config, provisioner
├── skills/                         # Agent skills: public/ (committed), custom/ (gitignored)
├── contracts/                      # Cross-component JSON contracts (e.g. subagent status)
├── scripts/                        # Root orchestration scripts invoked by the Makefile (check, configure, doctor, serve, docker, deploy, setup_wizard)
├── tests/                          # Root-level tests (currently tests/skills/ — public skill tests)
└── docs/                           # Cross-cutting docs, plans, and design notes
```

Runtime config lives at the **repo root**: copy `config.example.yaml` -> `config.yaml`
(main app config) and `extensions_config.example.json` -> `extensions_config.json` (MCP
servers + skills). Both real files are gitignored and may be edited at runtime via the
Gateway API. Config schema and resolution order are documented in
[backend/AGENTS.md](backend/AGENTS.md).

## Commands: Root vs. Module

**Root `make` targets drive the whole stack** (run from the repo root):

```bash
make setup       # Interactive setup wizard (recommended for new users)
make doctor      # Check configuration and system requirements
make config      # Generate local config files from the examples
make check       # Check that required tools are installed
make install     # Install all dependencies (frontend + backend + pre-commit hooks)
make dev         # Start all services with hot-reload (Gateway + Frontend + Nginx)
make start       # Start all services in production mode (local, optimized)
make stop        # Stop all running services
make up / down   # Build/stop the production Docker stack (browser at localhost:2026)
make docker-start / docker-stop / docker-logs   # Docker development environment
```

Run `make help` for the full list.

**Per-module commands drive a single module** (run inside that module):

```bash
# Backend (see backend/AGENTS.md for the full set)
cd backend && make dev        # Gateway API with reload (port 8001)
cd backend && make test       # Backend test suite
cd backend && make lint       # ruff check
cd backend && make format     # ruff format

# Frontend (see frontend/AGENTS.md for the full set)
cd frontend && pnpm dev       # Dev server with Turbopack (port 3000)
cd frontend && pnpm check     # Lint + type check (run before committing)
cd frontend && pnpm test      # Unit tests
```

Rule of thumb: **root `make` = the full application**; **`backend/Makefile` and `frontend/`
(`pnpm`) = per-module work.**

## Where to Go Next

- Backend work -> **[backend/AGENTS.md](backend/AGENTS.md)**
- Frontend work -> **[frontend/AGENTS.md](frontend/AGENTS.md)**
- Setup & install -> **[Install.md](Install.md)**, **[CONTRIBUTING.md](CONTRIBUTING.md)**
- Project overview & usage -> **[README.md](README.md)** (translations: `README_zh.md`,
  `README_ja.md`, `README_fr.md`, `README_ru.md`)
- Security policy -> **[SECURITY.md](SECURITY.md)**
- Changes -> **[CHANGELOG.md](CHANGELOG.md)**

## Cross-Cutting Conventions

These apply repo-wide; module guides own the module-specific detail.

- **Documentation update policy** — keep docs in sync with code: update `README.md` for
  user-facing changes and the relevant `AGENTS.md` for development/architecture changes in
  the same change set.
- **Test-driven development** — features and bug fixes ship with tests. Backend tests live
  in `backend/tests/` (TDD is mandatory there; see [backend/AGENTS.md](backend/AGENTS.md));
  frontend tests live in `frontend/tests/`.
- **Format before pushing** — run `make format` (backend) / `pnpm check` (frontend). Backend
  CI enforces `ruff format --check`, so formatting must be clean before a push.

## Research Platform Standards

- Preserve the raw/derived split. `Paper Record` is the raw truth layer; `Analysis View` and `Proposal Draft` are derived and must remain recomputable.
- Keep all research jobs idempotent. Re-running a `Topic Watch` or reanalysis flow must not duplicate papers, PDFs, views, or proposal versions.
- Push business logic into deep modules. Routers, pages, and UI state should orchestrate, not own research-domain rules or state machines.
- Model lifecycle explicitly. `Analysis View` and `Proposal Draft` need visible status and version semantics; do not hide mutation behind silent overwrite.
- Test observable behavior. Favor tests for state transitions, deduplication, scheduling behavior, scoring output, review actions, and knowledge-base emission over internal implementation details.
- Preserve the existing backend boundary. `app.*` may depend on `deerflow.*`; `deerflow.*` must not depend on `app.*`.
- Record stable language and hard-to-reverse decisions. Add domain terms to `CONTEXT.md`; add surprising or costly decisions to `docs/adr/`.

## Working Rules

- For issue-driven implementation, read the parent PRD, the current issue, `AGENTS.md`, `docs/agents/*.md`, `CONTEXT.md`, and relevant ADRs before coding.
- Start from the issue's declared working set. Do not begin with blind whole-repo search; expand only when the local working set no longer explains the dependency.
- Keep one implementation branch per issue, one issue focus per PR, and do not mix unrelated slices in the same change.
- Use Chinese for repo-local planning artifacts created for this project unless a specific upstream contribution requires English.
- When repo-level and subproject docs conflict, prefer the more specific source and call out the conflict in the completion summary.
- Any Python backend change must follow `docs/agents/python-backend-standards.md`.
- Any issue completion must satisfy `docs/agents/qa-checklist.md`.
- Coding is not complete until `$review` has been run against `main` and unresolved hard findings are fixed.

## Git Rules

- Branch from `main`.
- Use one branch per issue.
- Name branches with both type and issue id, for example `feature/123-topic-watch-ingestion`.
- Use Conventional Commits for every commit.
- Do not merge multiple issues into one branch or one PR.
- Rebase onto the latest `main` before review.
- Prefer squash merge for implementation branches.
- Do not leave `WIP`, `tmp`, `fix later`, or similarly low-information commit messages in shared history.
- The final issue-closing commit should explicitly reference the issue id.
