"""验证研究平台标准基线文档入口与关键内容可被后续流程稳定读取。"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_repo_file(relative_path: str) -> str:
    """读取仓库内文档，并在缺失时直接失败，避免后续流程静默跳过基线。"""
    content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    assert content.strip(), f"{relative_path} 不能为空"
    return content


def test_agent_entrypoints_point_to_the_documented_tracker_and_domain_docs():
    """验证仓库级 agent 入口、issue tracker 与领域文档入口保持单一事实来源。"""
    agents = _read_repo_file("AGENTS.md")
    issue_tracker = _read_repo_file("docs/agents/issue-tracker.md")
    triage_labels = _read_repo_file("docs/agents/triage-labels.md")
    domain_docs = _read_repo_file("docs/agents/domain.md")

    # 这里锁定 issue tracker 与标准文档入口，避免后续流程从错误 remote 推断任务来源。
    assert "source of truth" in agents
    assert "lgxyc/deer-flow" in agents
    assert "docs/agents/issue-tracker.md" in agents
    assert "docs/agents/triage-labels.md" in agents
    assert "docs/agents/domain.md" in agents

    # 这里证明 issue tracker 文档本身可读且明确指向 fork 仓库。
    assert "GitHub (`lgxyc/deer-flow`)" in issue_tracker
    assert "Do **not** infer the tracker repo from the local clone's `origin` remote" in issue_tracker

    # 这里锁定后续 triage 流程依赖的 canonical labels。
    for label in ("needs-triage", "needs-info", "ready-for-agent", "ready-for-human", "wontfix"):
        assert label in triage_labels

    # 这里锁定领域文档布局，避免后续 issue 重新解释入口位置。
    assert "single-context" in domain_docs
    assert "Root `CONTEXT.md`" in domain_docs
    assert "Global ADRs under `docs/adr/`" in domain_docs


def test_context_defines_the_research_platform_glossary():
    """验证根级术语表包含研究平台首批稳定术语。"""
    context = _read_repo_file("CONTEXT.md")

    for term in (
        "Topic Watch",
        "Paper Record",
        "Analysis View",
        "Proposal Draft",
        "Anchor-and-Bridge",
    ):
        assert f"**{term}**" in context


def test_initial_adrs_capture_the_required_research_platform_decisions():
    """验证首批 ADR 已覆盖 issue #2 要求的四类不可逆决策。"""
    adr_0001 = _read_repo_file("docs/adr/0001-three-layer-research-objects.md")
    adr_0002 = _read_repo_file("docs/adr/0002-db-and-markdown-kb-split.md")
    adr_0003 = _read_repo_file("docs/adr/0003-arxiv-first-and-built-in-research-scheduler.md")
    adr_0004 = _read_repo_file("docs/adr/0004-agents-md-as-single-source-of-truth.md")

    assert "Paper Record" in adr_0001
    assert "Analysis View" in adr_0001
    assert "Proposal Draft" in adr_0001

    assert "database" in adr_0002
    assert "Markdown knowledge base" in adr_0002

    assert "arXiv adapter" in adr_0003
    assert "built-in research-specific scheduler" in adr_0003

    assert "`AGENTS.md`" in adr_0004
    assert "`CLAUDE.md`" in adr_0004


def test_claude_redirects_keep_agents_md_as_the_only_authoritative_entry():
    """验证子目录 `CLAUDE.md` 只做重定向，避免 agent 规范分叉。"""
    backend_claude = _read_repo_file("backend/CLAUDE.md")
    frontend_claude = _read_repo_file("frontend/CLAUDE.md")

    # 这里锁定“只重定向不分叉”的入口约束，确保后续代理读取到同一份规范。
    assert "@AGENTS.md" in backend_claude
    assert "@AGENTS.md" in frontend_claude
    assert "guidance lives in [AGENTS.md]" in backend_claude
    assert "guidance lives in [AGENTS.md]" in frontend_claude
