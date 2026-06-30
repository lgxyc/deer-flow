# Workflow: DeerFlow 安全存储科研方案设计平台

<!-- 此文件会在每次继续执行时被后续会话读取。
     它把一个 PRD 与该 PRD 拆出的开发 issues 绑定在一起。 -->

## Parent PRD

- Reference: #1
- Title: PRD：基于 DeerFlow 的安全存储科研方案设计平台
- Source: GitHub issue on `lgxyc/deer-flow`

## Execution rule

- Complete exactly one ready issue per session.
- Work through the issue list below in order.
- Skip issues whose blockers are unfinished.
- Skip HITL issues until the required human decision is recorded.
- After completing one issue, summarize and stop.
- Do not work on issues outside this workflow unless the user explicitly updates this file.
- Before coding, read the parent PRD, current issue, `AGENTS.md`, `docs/agents/*.md`, `CONTEXT.md`, and the relevant ADRs.
- Start from the issue's `Working Set`. Do not begin with blind whole-repo search; widen search only when the working set no longer explains the dependency.
- After coding and basic verification, run the mandatory `$review` gate against `main`. If Standards or Spec review reports unresolved hard findings, fix them and rerun review before marking the issue done.

## Issue source

- Type: GitHub
- Location: `lgxyc/deer-flow`
- Lookup rule: `gh issue view <number> --repo lgxyc/deer-flow --comments`
- Done rule: all acceptance criteria are checked with real verification evidence, the issue work is committed, and the workflow status below is updated

## Issues

| Order | Issue | Title | Type | Blocked by | Status |
|---:|---|---|---|---|---|
| 1 | #2 | 初始化研究平台规范与领域文档基线 | AFK | None - can start immediately | open |
| 2 | #3 | 打通 Topic Watch 创建与查看路径 | AFK | #2 | blocked |
| 3 | #4 | 打通 arXiv 检索到 Paper Record/PDF Corpus 路径 | AFK | #3 | blocked |
| 4 | #5 | 打通 Analysis View 生成与知识库落地路径 | AFK | #4 | blocked |
| 5 | #6 | 打通 Proposal Draft 生成与 6 维评分路径 | AFK | #5 | blocked |
| 6 | #7 | 打通 Proposal Draft 审阅与版本化路径 | AFK | #6 | blocked |
| 7 | #8 | 打通调度中心与增量运行路径 | AFK | #6 | blocked |
| 8 | #9 | 打通 Dashboard 与 Source/Template Settings 路径 | AFK | #3, #4, #5, #6, #8 | blocked |
| 9 | #10 | 打通旧论文 Analysis View 手动重算路径 | AFK | #5 | blocked |

## Branch strategy

branch-per-issue

## Branch naming

`feature/{issue-number}-{slug}`

Example: `feature/6-proposal-draft-generator`

## Commit convention

conventional-commits

## Commit trailers

None

## Development standards

- `AGENTS.md`
- `CLAUDE.md`
- `docs/agents/issue-tracker.md`
- `docs/agents/triage-labels.md`
- `docs/agents/domain.md`
- `docs/agents/python-backend-standards.md`
- `docs/agents/qa-checklist.md`
- `CONTEXT.md`
- `docs/adr/*.md`
- `CONTRIBUTING.md`
- `backend/CLAUDE.md`
- `frontend/CLAUDE.md`

## Additional engineering rules

- Preserve the raw/derived split: `Paper Record` is raw truth; `Analysis View` and `Proposal Draft` are derived.
- All research jobs must be idempotent.
- Routers and UI compose workflows; they do not own core proposal logic, scoring, or version rules.
- `Analysis View` and `Proposal Draft` must keep explicit status/version semantics; never silently overwrite history.
- Test external behavior first: state transitions, deduplication, scheduler behavior, scoring outputs, review actions, KB emission.
- Preserve the `app.* -> deerflow.*` dependency direction.
- Record hard-to-reverse architecture choices in ADRs and new stable domain language in `CONTEXT.md`.
- One issue per branch, one issue per PR, no mixed slices.
- Rebase to the latest `main` before review.
- Prefer squash merge.
- Do not leave `WIP`, `tmp`, or other low-information commit messages in shared history.
- The final issue-closing commit should explicitly reference the issue id.
- Mandatory completion gate: run `$review` against `main`; unresolved hard findings on either Standards or Spec block completion.

## Commands

### Install

```bash
make install
```

### Lint

```bash
cd backend && make lint
cd frontend && pnpm lint
```

### Test

```bash
cd backend && make test
cd frontend && pnpm test
```

UI-affecting slices should also run:

```bash
cd frontend && pnpm test:e2e
```

### Type-check

```bash
cd frontend && pnpm typecheck
```

### Build

```bash
cd frontend && pnpm build
```

### Review

```text
$review against main
```

## Continue-session instructions

When the user says `继续` and references this workflow file, follow this loop:

1. Read this workflow file first.
2. Read the parent PRD.
3. Read the issue list in order.
4. Select the first ready issue.
5. Read the selected issue in full.
6. Read the development standards listed above.
7. Use `/implement` skill to implement that issue's scope.
8. Run the configured verification commands appropriate to the issue's scope.
9. Run `$review` against `main`.
10. If review reports unresolved hard findings, fix them and repeat steps 8-9.
11. Mark only verified acceptance criteria as checked.
12. Commit only files related to the issue and issue/workflow bookkeeping.
13. Update this workflow's issue table status for the completed issue.
14. Output completion summary with verification results and review status.
15. **Block and wait for user confirmation before proceeding.**
16. Stop. Do not begin another issue in the same session.

Ready issue checks:

- Status is open or unchecked.
- Type is AFK.
- Blocked by is `None - can start immediately` or all blockers are already done.
- The issue has concrete acceptance criteria with unchecked `- [ ]` items.
- Ignore issues not listed in this workflow.
- Reject planning-only, parent, epic, or PRD issues.
- Leave blocked issues untouched until their dependencies are complete.
- If no ready issue exists, report the blocker state and stop.

Commit message format:

```text
<type>(<scope>): <imperative summary>  refs #<issue-number>

- <what changed and why>
- <what changed and why>

Closes #<issue-number>
```

Completion summary format:

```text
## Issue Completion Summary

### Issue Details
- Issue: <issue id> - <title>
- PRD: #1
- Workflow: docs/workflows/deerflow-security-storage-research-platform-WORKFLOW.md

### Implementation
- Commit: <short hash> "<commit subject>"
- Files Changed: <list of modified files>
- Implementation Approach: <brief description of solution>

### Verification Results
- <command>: <PASS/FAIL> - <output summary>

### Acceptance Criteria
- [x] <criterion>: <verification evidence>

### Next Steps
- Next Issue: <next ready issue or blocker state>

---
**Awaiting user confirmation to proceed.**
```

## Continuation prompt

After `/clear`, say:

```text
继续，按照 docs/workflows/deerflow-security-storage-research-platform-WORKFLOW.md 执行下一个 ready issue
```

## Notes

- Keep this workflow scoped to the parent PRD above.
- Do not add unrelated issues to this file.
- If new scope is discovered, create or update issues through `to-issues` before continuing.
