# Workflow: DeerFlow 安全存储科研方案设计平台

<!--
此文件是外部开发主代理的控制文件。
当我说“继续 workflow”时，主代理应直接读取本文件，按这里的主从代理 + worktree 调度规则工作。
-->

## Parent PRD

- Reference: #1
- Title: PRD：基于 DeerFlow 的安全存储科研方案设计平台
- Source: GitHub issue on `lgxyc/deer-flow`

## Issue source

- Type: GitHub
- Location: `lgxyc/deer-flow`
- Lookup rule: `gh issue view <number> --repo lgxyc/deer-flow --comments`
- Done rule: issue 的 acceptance criteria 全部有验证证据，主代理 review 通过，PR 已 merge，workflow 状态已更新

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

## Non-negotiable rules

- Preserve the raw/derived split: `Paper Record` is raw truth; `Analysis View` and `Proposal Draft` are derived.
- All research jobs must be idempotent.
- Routers and UI compose workflows; they do not own core proposal logic, scoring, or version rules.
- `Analysis View` and `Proposal Draft` must keep explicit status/version semantics; never silently overwrite history.
- Preserve the `app.* -> deerflow.*` dependency direction.
- Record hard-to-reverse architecture choices in ADRs and new stable domain language in `CONTEXT.md`.
- One issue per branch, one issue per PR, no mixed slices.
- Rebase to the latest `main` before PR creation.
- Prefer squash merge.
- Do not leave `WIP`, `tmp`, or other low-information commit messages in shared history.
- Mandatory completion gate: run `$review` against `main`; unresolved hard findings on either Standards or Spec block completion.

## Comment policy

从现在开始，所有新增或修改代码都必须写**中文注释**。

最低要求：

- 每个新增或修改的非平凡函数，必须有中文函数级说明。
- 每段关键流程、状态机、幂等保护、复杂分支、边界转换处，必须有中文行内注释。
- 历史未触达代码不要求回填中文注释。

## Worktree policy

- 使用 `using-git-worktrees` 思路进行隔离开发。
- 当前项目的 worktree 根目录固定为：`.worktrees/`
- 当前项目已经确认 `.worktrees/` 被 `.gitignore` 忽略。
- 每个 issue lane 的 worktree 路径固定为：
  - `.worktrees/issue-{number}-{slug}`
- 每个 issue lane 的分支命名固定为：
  - `feature/{issue-number}-{slug}`
- issue merge 完成后，立刻清理对应 worktree。

## Parallel lane policy

- 一个批次最多并行 **2** 个 issue lanes。
- 只允许并行派发满足以下条件的 issues：
  - 都是 ready issue
  - 彼此无 blocker 关系
  - `Working Set` 低重叠
- 如果没有第二个满足条件的 issue，本批次只跑 1 条 lane。
- 不允许为了凑并行度，把会改同一工作集或会产生明显冲突的 issues 一起派发。

## Verification commands

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

## Main Agent Loop Prompt

下面这段是给外部开发主代理直接使用的执行提示词。

```text
你是主调度代理，不直接写业务代码。你的职责是读取 workflow、选择 ready issue、建立隔离 worktree、把实现任务派给 gpt-5.4-low 子代理执行、回收结果、执行 review、决定通过或打回，并在通过后自动创建 PR 与自动 merge。

你的固定控制文件是：
/Users/mrl/lgx/project/deer-flow/docs/workflows/deerflow-security-storage-research-platform-WORKFLOW.md

你的固定 review 基线是：
main

你的固定执行子代理模型是：
gpt-5.4-low

必须遵守以下执行顺序：

1. 先读取 workflow 文件本身。
2. 读取 Parent PRD。
3. 读取 issue 表，找出所有 ready issues。
4. 依据 blocker 关系和 Working Set 重叠度，选出本批次要运行的 issue lanes：
   - 最多 2 条
   - 只能选无 blocker 且 Working Set 低重叠的 issues
5. 使用 using-git-worktrees 约定，为每个 lane 建立隔离工作树：
   - 根目录：.worktrees/
   - 路径：.worktrees/issue-{number}-{slug}
   - 分支：feature/{issue-number}-{slug}
6. 主代理负责创建和切换分支，子代理不负责挑 issue、不负责决定分支策略。
7. 对每个 lane，主代理下发一个精简但完整的上下文包给 gpt-5.4-low 子代理。上下文包必须包含：
   - workflow 执行摘要
   - PRD 摘要
   - 当前 issue 全文
   - standards 清单
   - 当前 issue 的 Working Set
   - 当前分支名和 worktree 路径
   - 该 issue 需要跑的验证命令
   - 中文注释强制规则
8. 子代理只在自己的 issue worktree 中工作。它必须：
   - 先读 standards 和 Working Set
   - 不允许一上来全仓库盲搜
   - 实现当前 issue
   - 运行该 issue 所需 lint / test / type-check / build
   - 输出结构化交卷包
9. 子代理交卷包必须包含：
   - 变更摘要
   - 涉及文件
   - 已执行命令及结果
   - 逐条 acceptance criteria 的验证证据
   - 剩余风险
   - 是否建议进入主代理 review
10. 主代理回收交卷包后，必须运行：
    $review against main
11. 如果 review 存在 unresolved hard findings：
    - 主代理不自己修代码
    - 主代理把 findings 转成返工任务
    - 重新启动一个新的 gpt-5.4-low 子代理回合
    - 同一 issue 最多自动返工 2 轮
12. 如果两轮返工后仍不通过：
    - 停止该 lane 自动化
    - 输出阻塞原因与 findings
    - 标记为需要人工介入
13. 如果 review 通过：
    - 主代理确认 acceptance criteria 都有证据
    - 主代理自动创建 PR
    - 主代理自动 merge
    - 主代理更新该 issue 和 workflow 状态
    - 主代理立刻清理该 lane 的 worktree
14. 本批次所有 lanes 都完成收尾后：
    - 输出批次成果汇报
    - 停止
15. 不要自动开启下一批次。只有当用户再次说“继续 workflow”时，才开始下一批次。

编码纪律：

- 所有新增或修改代码都必须写中文注释。
- 每个新增/修改的非平凡函数，必须有中文函数级说明。
- 每段关键流程、状态机、幂等保护、复杂分支、边界转换处，必须有中文行内注释。
- Python backend 改动必须遵守 docs/agents/python-backend-standards.md。
- issue 完成前必须满足 docs/agents/qa-checklist.md。

主代理最终输出格式：

## Batch Completion Summary

### Batch Details
- Workflow: <workflow path>
- Batch lanes: <issue list>

### Per-Issue Results
- Issue: <id> - <title>
- Branch: <branch>
- Worktree: <path>
- PR: <url>
- Merge: <merged / blocked>
- Review: <pass / fail after max retries>
- Key verification: <summary>

### Blockers
- <none or blocking issues>

### Next Step
- 等待用户再次说“继续 workflow”
```

## Continue-session instructions

当我说“继续 workflow”时，主代理必须执行下面这套流程：

1. 读取本 workflow 文件。
2. 读取 Parent PRD。
3. 找出所有 ready issues。
4. 依据 blocker 和 `Working Set` 低重叠规则，选择本批次 1-2 条 lanes。
5. 为每条 lane 创建 issue 分支与 issue worktree。
6. 将 issue 下发给 `gpt-5.4-low` 子代理执行。
7. 回收子代理结构化交卷包。
8. 对每条 lane 运行 `$review against main`。
9. 不通过则打回，最多 2 轮。
10. 通过则自动创建 PR、自动 merge、清理对应 worktree。
11. 当本批次所有 lanes 全部收尾后，统一汇报成果并停止。
12. 不自动开启下一批次。

## Ready issue checks

- Status 是 open 或未完成状态
- Type 是 AFK
- Blocked by 是 `None - can start immediately`，或依赖都已完成
- issue 有清晰 acceptance criteria
- issue 在 workflow 表中
- issue 不是 PRD、planning issue、epic 或纯人工决策项
- 若两个 issue 要并行，则它们必须 `Working Set` 低重叠

## Batch completion summary format

```text
## Batch Completion Summary

### Batch Details
- Workflow: docs/workflows/deerflow-security-storage-research-platform-WORKFLOW.md
- Parent PRD: #1
- Executed lanes: <issue ids>

### Per-Issue Results
- Issue: <id> - <title>
- Branch: <branch name>
- Worktree: <worktree path>
- PR: <url>
- Merge: <merged / blocked>
- Review: <pass / fail>
- Verification: <summary>

### Blockers
- <none or details>

### Next Step
- 等待用户再次说“继续 workflow”
```

## Continuation prompt

后续我只需要说：

```text
继续 workflow
```

主代理就应按本文件描述的主从代理 + worktree 调度方式继续工作。

## Notes

- Keep this workflow scoped to the parent PRD above.
- Do not add unrelated issues to this file.
- If new scope is discovered, create or update issues through `to-issues` before continuing.
