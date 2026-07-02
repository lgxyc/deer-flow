"""arXiv source adapter。"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass

import httpx

NS_MAP = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
ARXIV_ENDPOINT = "http://export.arxiv.org/api/query"
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_RESULTS = 5


class ArxivQueryError(RuntimeError):
    """arXiv 查询失败时抛出。"""


@dataclass(slots=True, frozen=True)
class ArxivPaperHit:
    """arXiv 返回的一篇论文命中。"""

    source_paper_id: str
    title: str
    abstract: str
    authors: list[str]
    categories: list[str]
    published_at: str | None
    updated_at: str | None
    abs_url: str
    pdf_url: str | None

    def to_dict(self) -> dict[str, object]:
        """把 dataclass 转成便于序列化与测试桩复用的字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ArxivPaperHit:
        """从字典恢复 ``ArxivPaperHit``，统一测试桩与真实 client 的返回面。"""
        return cls(
            source_paper_id=str(data["source_paper_id"]),
            title=str(data["title"]),
            abstract=str(data.get("abstract") or ""),
            authors=[str(item) for item in data.get("authors", [])],
            categories=[str(item) for item in data.get("categories", [])],
            published_at=str(data["published_at"]) if data.get("published_at") else None,
            updated_at=str(data["updated_at"]) if data.get("updated_at") else None,
            abs_url=str(data["abs_url"]),
            pdf_url=str(data["pdf_url"]) if data.get("pdf_url") else None,
        )


def _build_search_query(query: str) -> str:
    """构造 arXiv 的 ``search_query``，对多词查询保留短语语义。"""
    normalized = query.strip()
    if " " in normalized:
        return f'all:"{normalized}"'
    return f"all:{normalized}"


def _normalize_arxiv_id(raw_id: str) -> str:
    """把 arXiv `<id>` URL 归一成稳定的 source id。"""
    if "/abs/" in raw_id:
        tail = raw_id.split("/abs/", 1)[1]
    else:
        tail = raw_id.rsplit("/", 1)[-1]
    base, sep, suffix = tail.rpartition("v")
    if sep and suffix.isdigit():
        return base
    return tail


def _text(entry: ET.Element, path: str) -> str:
    """读取 Atom 节点文本并去掉边缘空白。"""
    node = entry.find(path, NS_MAP)
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def _parse_entry(entry: ET.Element) -> ArxivPaperHit:
    """把一条 Atom `<entry>` 解析成结构化论文对象。"""
    raw_id = _text(entry, "atom:id")
    pdf_url = None
    abs_url = raw_id
    for link in entry.findall("atom:link", NS_MAP):
        if link.get("title") == "pdf":
            pdf_url = link.get("href")
        elif link.get("rel") == "alternate":
            abs_url = link.get("href", abs_url)

    authors = [(author.findtext("atom:name", default="", namespaces=NS_MAP) or "").strip() for author in entry.findall("atom:author", NS_MAP)]
    categories = [item.get("term", "") for item in entry.findall("atom:category", NS_MAP) if item.get("term")]
    published_raw = _text(entry, "atom:published")
    updated_raw = _text(entry, "atom:updated")
    return ArxivPaperHit(
        source_paper_id=_normalize_arxiv_id(raw_id),
        title=" ".join(_text(entry, "atom:title").split()),
        abstract=" ".join(_text(entry, "atom:summary").split()),
        authors=[item for item in authors if item],
        categories=categories,
        published_at=published_raw.split("T", 1)[0] if published_raw else None,
        updated_at=updated_raw.split("T", 1)[0] if updated_raw else None,
        abs_url=abs_url,
        pdf_url=pdf_url,
    )


class ArxivClient:
    """通过 arXiv Atom API 拉取论文命中的异步 client。"""

    def __init__(
        self,
        *,
        endpoint: str = ARXIV_ENDPOINT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        user_agent: str = "deerflow-research-platform/0.1",
    ) -> None:
        self._endpoint = endpoint
        self._timeout = httpx.Timeout(timeout_seconds)
        self._headers = {"User-Agent": user_agent}

    async def search(self, *, query: str, max_results: int = DEFAULT_MAX_RESULTS) -> list[dict[str, object]]:
        """按单个 query term 查询 arXiv，并返回结构化论文列表。"""
        params = {
            "search_query": _build_search_query(query),
            "start": 0,
            "max_results": max(1, max_results),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout, headers=self._headers) as client:
                response = await client.get(self._endpoint, params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ArxivQueryError(f"arXiv query failed for '{query}': {exc}") from exc

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as exc:
            raise ArxivQueryError(f"arXiv returned invalid XML for '{query}'") from exc

        return [_parse_entry(entry).to_dict() for entry in root.findall("atom:entry", NS_MAP)]
