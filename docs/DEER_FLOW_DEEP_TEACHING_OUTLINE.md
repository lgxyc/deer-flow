# DeerFlow 深度教学文档大纲

## 文档目标

这份文档先作为讨论稿，只定义后续“深度阅读源码”的教学结构，不展开每个章节的细节实现。

成功标准：

- 用 10 个章节覆盖 DeerFlow 从启动、配置、运行时、Agent、工具、Sandbox、Skills、Memory、前端到扩展与调试的完整技术链路。
- 每章都明确读者应该理解的问题、需要阅读的核心源码入口、以及后续填充细节时应该验证的现象。
- 章节顺序遵循真实执行路径，避免先讲局部实现导致整体图景断裂。

## 第 1 章：项目全景与运行边界

本章回答：DeerFlow 到底是什么，哪些部分属于产品界面，哪些部分属于 agent harness，哪些部分是运行时基础设施。

核心主题：

- DeerFlow 2.0 的定位：super agent harness，而不是单一 deep research workflow。
- 顶层目录分工：`backend/`、`frontend/`、`skills/`、`scripts/`、`docker/`。
- 本地开发、Docker 开发、生产部署三种运行方式的边界。
- Nginx、Gateway、Frontend、Sandbox、配置文件之间的关系。

建议源码入口：

- [README_zh.md](/Users/mrl/lgx/project/deer-flow/README_zh.md)
- [Makefile](/Users/mrl/lgx/project/deer-flow/Makefile)
- [backend/README.md](/Users/mrl/lgx/project/deer-flow/backend/README.md)
- [frontend/README.md](/Users/mrl/lgx/project/deer-flow/frontend/README.md)

后续验证方式：

- 画出一次浏览器请求从 `localhost:2026` 到前端或后端的路由图。
- 区分 `make dev`、`make docker-start`、`make up` 分别启动哪些服务。

## 第 2 章：配置系统与启动流程

本章回答：DeerFlow 如何从 `config.yaml`、`.env`、运行目录和默认配置中构造可运行的应用。

核心主题：

- `config.yaml` 的模型、工具、sandbox、memory、summarization、skills、tracing 配置。
- `DEER_FLOW_PROJECT_ROOT`、`DEER_FLOW_CONFIG_PATH`、`DEER_FLOW_HOME`、`DEER_FLOW_SKILLS_PATH` 的作用。
- Gateway 启动时如何加载配置、设置日志、初始化 runtime。
- 配置热读取与启动快照之间的边界。

建议源码入口：

- [backend/packages/harness/deerflow/config/app_config.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/config/app_config.py)
- [backend/packages/harness/deerflow/config/paths.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/config/paths.py)
- [backend/packages/harness/deerflow/config/runtime_paths.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/config/runtime_paths.py)
- [backend/app/gateway/app.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/app.py)

后续验证方式：

- 修改一个非敏感配置项，观察哪些路径需要重启，哪些请求期会重新读取。
- 跟踪 `.deer-flow` 运行目录如何被创建和使用。

## 第 3 章：Gateway API 与 LangGraph-compatible Runtime

本章回答：前端和外部客户端如何通过 Gateway 创建 thread、启动 run、消费 SSE stream。

核心主题：

- FastAPI Gateway 的职责：REST API、LangGraph-compatible API、认证、中间件、runtime 生命周期。
- `/api/langgraph/*` 与 `/api/*` 的区别和兼容层含义。
- thread、run、assistant、stream mode、metadata、context/configurable 的数据流。
- SSE 事件如何被格式化、桥接、消费。

建议源码入口：

- [backend/app/gateway/app.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/app.py)
- [backend/app/gateway/services.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/services.py)
- [backend/app/gateway/routers/thread_runs.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/routers/thread_runs.py)
- [backend/app/gateway/routers/runs.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/routers/runs.py)
- [backend/packages/harness/deerflow/runtime/runs/manager.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/runtime/runs/manager.py)

后续验证方式：

- 构造一个最小 `POST /api/langgraph/threads/{id}/runs/stream` 请求，解释每个请求字段的归宿。
- 对照 SSE 输出说明 `values`、`messages-tuple`、`custom` 的用途。

## 第 4 章：Lead Agent 的创建与执行模型

本章回答：DeerFlow 的核心 agent 是如何被创建、如何选择模型、如何注入 prompt、tools 和 middlewares。

核心主题：

- `make_lead_agent` 的职责和执行顺序。
- 默认 lead agent 与自定义 agent 的关系。
- model selection、thinking、reasoning effort、vision、bootstrap agent 的配置路径。
- system prompt 如何组合 skills、memory、工作目录约束和 agent 配置。
- tracing callback 为什么挂在 graph invocation root。

建议源码入口：

- [backend/packages/harness/deerflow/agents/lead_agent/agent.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/agent.py)
- [backend/packages/harness/deerflow/agents/lead_agent/prompt.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/prompt.py)
- [backend/packages/harness/deerflow/agents/factory.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/factory.py)
- [backend/packages/harness/deerflow/models/factory.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/models/factory.py)

后续验证方式：

- 从一次 run 的 `config.context` 或 `config.configurable` 追踪到最终 model、agent_name 和 prompt。
- 解释新增一个模型配置后，前端模型列表和后端 agent 执行如何看到它。

## 第 5 章：Middleware 链路与横切能力

本章回答：DeerFlow 如何在 agent 前后插入线程目录、上传文件、上下文压缩、标题、memory、图像、错误处理和安全终止等能力。

核心主题：

- middleware 的顺序为什么重要。
- ThreadData、Uploads、Summarization、Todo、Title、Memory、ViewImage、Clarification 的职责。
- tool error、LLM error、loop detection、token usage、tool output budget 等稳定性中间件。
- middleware 与 LangChain/LangGraph agent 状态之间的交互方式。

建议源码入口：

- [backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py)
- [backend/packages/harness/deerflow/agents/middlewares/uploads_middleware.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/middlewares/uploads_middleware.py)
- [backend/packages/harness/deerflow/agents/middlewares/summarization_middleware.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/middlewares/summarization_middleware.py)
- [backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py)
- [backend/packages/harness/deerflow/agents/thread_state.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/thread_state.py)

后续验证方式：

- 画出一条用户消息进入 agent 前后，哪些 middleware 会修改 state 或 prompt。
- 找出一个必须放在链路末尾的 middleware，并解释原因。

## 第 6 章：工具系统、MCP 与 Subagent 委派

本章回答：DeerFlow 如何组织内置工具、配置工具、MCP 工具、skill 管理工具，以及如何把任务委派给 subagent。

核心主题：

- `get_available_tools()` 如何聚合工具来源。
- sandbox tools、built-in tools、community tools、MCP tools 的职责差异。
- tool search、skill manage、present files、clarification、view image、task tool 的使用场景。
- subagent registry、executor、并发限制、超时、事件回传。
- ACP agent 集成与普通 subagent 的差异。

建议源码入口：

- [backend/packages/harness/deerflow/tools/tools.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/tools/tools.py)
- [backend/packages/harness/deerflow/tools/builtins/task_tool.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/tools/builtins/task_tool.py)
- [backend/packages/harness/deerflow/subagents/executor.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/subagents/executor.py)
- [backend/packages/harness/deerflow/subagents/registry.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/subagents/registry.py)
- [backend/packages/harness/deerflow/mcp/tools.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/mcp/tools.py)

后续验证方式：

- 列出一个 run 中实际可用工具，并说明它们来自配置、MCP、builtin 还是 sandbox。
- 跟踪 lead agent 调用 `task()` 后 subagent 如何启动、轮询和返回结果。

## 第 7 章：Sandbox、文件系统与 Artifact 生命周期

本章回答：DeerFlow 如何让 agent 安全地读写文件、执行命令、处理上传文件并把结果呈现给用户。

核心主题：

- `SandboxProvider` 与 `Sandbox` 抽象。
- LocalSandbox 与 AioSandbox 的差异。
- 虚拟路径 `/mnt/user-data/workspace`、`/mnt/user-data/uploads`、`/mnt/user-data/outputs`、`/mnt/skills` 的映射。
- 文件上传、格式转换、artifact 发现与服务。
- `str_replace` 的文件操作锁与并发安全。
- shell 权限、安全边界与部署风险。

建议源码入口：

- [backend/packages/harness/deerflow/sandbox/sandbox.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/sandbox/sandbox.py)
- [backend/packages/harness/deerflow/sandbox/sandbox_provider.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/sandbox/sandbox_provider.py)
- [backend/packages/harness/deerflow/sandbox/local/local_sandbox.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/sandbox/local/local_sandbox.py)
- [backend/packages/harness/deerflow/sandbox/tools.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/sandbox/tools.py)
- [backend/app/gateway/routers/uploads.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/routers/uploads.py)
- [backend/app/gateway/routers/artifacts.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/routers/artifacts.py)

后续验证方式：

- 上传一个文件后，追踪它在 thread 目录中的物理路径和 prompt 中的呈现方式。
- 生成一个 artifact 后，解释前端如何通过 Gateway 读取它。

## 第 8 章：Skills、Agent 配置与可扩展工作流

本章回答：DeerFlow 如何用 `SKILL.md` 和 agent 配置扩展能力，而不是把所有逻辑写死在代码里。

核心主题：

- public skills、custom skills、nested skills 的发现和解析。
- skill 权限、allowed tools、启用状态、安装和安全扫描。
- `SOUL.md`、custom agent、bootstrap/setup/update agent 工具的关系。
- skills 如何注入 system prompt，以及 summarization 如何保留近期 skill 上下文。
- skill evolution 相关配置和后续扩展方向。

建议源码入口：

- [backend/packages/harness/deerflow/skills/parser.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/skills/parser.py)
- [backend/packages/harness/deerflow/skills/installer.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/skills/installer.py)
- [backend/packages/harness/deerflow/skills/tool_policy.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/skills/tool_policy.py)
- [backend/app/gateway/routers/skills.py](/Users/mrl/lgx/project/deer-flow/backend/app/gateway/routers/skills.py)
- [skills/public](/Users/mrl/lgx/project/deer-flow/skills/public)

后续验证方式：

- 选一个 `skills/public/*/SKILL.md`，追踪它如何被发现、展示、启用并注入 agent。
- 解释 `allowed_tools` 如何影响最终可用工具集合。

## 第 9 章：Memory、Persistence、Checkpointer 与运行历史

本章回答：DeerFlow 如何保存会话状态、run 事件、用户记忆、反馈数据，并在多轮对话中恢复上下文。

核心主题：

- LangGraph checkpointer 与 DeerFlow persistence 的边界。
- thread metadata、run record、run event、feedback、user 的存储模型。
- memory extraction queue、storage、updater、prompt injection。
- SQLite/Postgres 后端选择和迁移。
- token usage、run journal、stream bridge 与调试可观测性。

建议源码入口：

- [backend/packages/harness/deerflow/agents/memory/storage.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/memory/storage.py)
- [backend/packages/harness/deerflow/agents/memory/queue.py](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/agents/memory/queue.py)
- [backend/packages/harness/deerflow/persistence](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/persistence)
- [backend/packages/harness/deerflow/runtime/checkpointer](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/runtime/checkpointer)
- [backend/packages/harness/deerflow/runtime/stream_bridge](/Users/mrl/lgx/project/deer-flow/backend/packages/harness/deerflow/runtime/stream_bridge)

后续验证方式：

- 结束一次对话后，找到 thread state、run event 和 memory 数据分别存在哪里。
- 解释删除一个 thread 时，LangGraph 状态和 DeerFlow 本地文件数据如何清理。

## 第 10 章：Frontend Workspace、数据流与端到端调试

本章回答：Next.js 前端如何组织 workspace UI、调用后端 API、处理流式消息、展示工具结果、todos、artifacts 和设置面板。

核心主题：

- Next.js App Router 页面结构和 workspace layout。
- React Query、LangGraph SDK、API client 的分工。
- thread 列表、message rendering、prompt input、uploads、model selector、settings 的状态来源。
- ai-elements 组件如何展示 reasoning、task、artifact、code block、plan、sources。
- 前后端端到端调试：网络请求、SSE、静态 demo、单元测试和 E2E 测试。

建议源码入口：

- [frontend/src/app/workspace/workspace-content.tsx](/Users/mrl/lgx/project/deer-flow/frontend/src/app/workspace/workspace-content.tsx)
- [frontend/src/core/threads/hooks.ts](/Users/mrl/lgx/project/deer-flow/frontend/src/core/threads/hooks.ts)
- [frontend/src/core/api/api-client.ts](/Users/mrl/lgx/project/deer-flow/frontend/src/core/api/api-client.ts)
- [frontend/src/core/models/hooks.ts](/Users/mrl/lgx/project/deer-flow/frontend/src/core/models/hooks.ts)
- [frontend/src/components/workspace/input-box.tsx](/Users/mrl/lgx/project/deer-flow/frontend/src/components/workspace/input-box.tsx)
- [frontend/src/components/ai-elements](/Users/mrl/lgx/project/deer-flow/frontend/src/components/ai-elements)

后续验证方式：

- 从用户点击发送按钮开始，追踪到后端 run stream，再回到消息组件渲染。
- 找一个 artifact 或 todo 的 UI，解释它的数据来自哪个 stream event 或 API。

## 建议讨论点

1. 是否把第 3 章和第 4 章拆得更细：一章讲 Gateway runtime，一章专讲 LangGraph agent graph。
2. 是否优先加一章“认证与多用户隔离”，或者把它并入第 3 章和第 9 章。
3. 是否把 IM Channels 作为独立章节，还是作为 Gateway 的外部入口案例放在第 3 章。
4. 后续填充细节时，是否每章都要求包含“关键类图、调用链、源码逐段讲解、调试实验、常见改造点”五个固定小节。
5. 阅读顺序是否按运行链路推进，还是按你最关心的主题优先，例如先读 Agent/Tools/Sandbox。
