# DeerFlow 深度教学文档

这组文档把 DeerFlow 项目拆成 10 个独立章节，目标是按真实执行路径深读源码：从项目边界、配置启动、Gateway runtime、agent、middleware、tools、sandbox、skills、memory，一直到前端 workspace 和端到端调试。

本 README 是 Obsidian 入口页。章节列表使用双链，便于在图谱视图和反向链接中串起源码阅读笔记。

## 章节列表

1. [[01-system-overview|项目全景与运行边界]]
2. [[02-configuration-and-bootstrap|配置系统与启动流程]]
3. [[03-gateway-runtime|Gateway API 与 LangGraph-compatible Runtime]]
4. [[04-lead-agent-execution|Lead Agent 的创建与执行模型]]
5. [[05-middleware-chain|Middleware 链路与横切能力]]
6. [[06-tools-mcp-subagents|工具系统、MCP 与 Subagent 委派]]
7. [[07-sandbox-files-artifacts|Sandbox、文件系统与 Artifact 生命周期]]
8. [[08-skills-and-agent-config|Skills、Agent 配置与可扩展工作流]]
9. [[09-memory-persistence-runtime-history|Memory、Persistence、Checkpointer 与运行历史]]
10. [[10-frontend-workspace-debugging|Frontend Workspace、数据流与端到端调试]]

## 建议阅读路径

### 路径 A：从全局执行链路读

按章节 1 到 10 顺序阅读。这个路径适合第一次系统理解 DeerFlow：先建立运行边界，再看后端 runtime 如何创建 run，最后看前端如何消费 stream 并渲染 UI。

### 路径 B：从一次聊天请求读

推荐顺序：

1. [[03-gateway-runtime|Gateway API 与 LangGraph-compatible Runtime]]
2. [[04-lead-agent-execution|Lead Agent 的创建与执行模型]]
3. [[05-middleware-chain|Middleware 链路与横切能力]]
4. [[06-tools-mcp-subagents|工具系统、MCP 与 Subagent 委派]]
5. [[09-memory-persistence-runtime-history|Memory、Persistence、Checkpointer 与运行历史]]
6. [[10-frontend-workspace-debugging|Frontend Workspace、数据流与端到端调试]]

这个路径直接围绕 `POST /api/langgraph/.../runs/stream` 展开，适合调试一次用户消息从浏览器到 agent 再回到 UI 的链路。

### 路径 C：从扩展能力读

推荐顺序：

1. [[02-configuration-and-bootstrap|配置系统与启动流程]]
2. [[06-tools-mcp-subagents|工具系统、MCP 与 Subagent 委派]]
3. [[07-sandbox-files-artifacts|Sandbox、文件系统与 Artifact 生命周期]]
4. [[08-skills-and-agent-config|Skills、Agent 配置与可扩展工作流]]
5. [[10-frontend-workspace-debugging|Frontend Workspace、数据流与端到端调试]]

这个路径适合新增工具、skill、artifact 展示或前端入口时使用。

## 图表约定

- `flowchart` 用于表达模块依赖、状态归属和数据归宿。
- `sequenceDiagram` 用于表达请求顺序、stream 时序和回调触发顺序。
- 图中的节点名优先使用真实文件、函数、hook、API path 或 state key。
- 图表只描述本章已经通过源码确认的链路；不把推测性设计画成事实。
- 如果图表和源码不一致，以源码为准，并更新图表。

## 验证约定

每章展开源码时，建议固定包含这些小节：

- 核心概念
- 关键源码逐段讲解
- 调用链追踪
- Mermaid 架构图和时序图
- 可运行验证实验
- 常见改造点
- 风险和调试入口

验证实验需要写清：

- 验证目的：要证明哪个源码结论。
- 运行前提：需要后端、前端、数据库、Docker、mock，还是静态 demo。
- 推荐命令：例如 `pnpm test`、`pnpm test:e2e`、`make dev`、`curl`。
- 观察点：网络请求、SSE event、数据库记录、文件路径、UI 状态或日志。
- 未执行时必须明确标注“未执行”，不要把建议命令写成已验证结论。

## 阅读时的源码记录方式

- 先读章节列出的入口文件，再用 `rg` 追调用链。
- 记录真实函数名、hook 名、API path 和配置 key。
- 对跨章节概念使用双链，例如 [[03-gateway-runtime|Gateway runtime]]、[[07-sandbox-files-artifacts|Artifact 生命周期]]、[[10-frontend-workspace-debugging|前端 workspace]]。
- 如果发现章节内容与源码不一致，优先修正文档，不保留过期解释。
