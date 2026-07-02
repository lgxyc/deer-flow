"""研究平台的本地 PDF 存储。"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

import httpx

from deerflow.config.paths import get_paths
from deerflow.uploads.manager import write_upload_file_no_symlink

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]")


@dataclass(slots=True, frozen=True)
class StoredPdfResult:
    """描述一次 PDF 本地落盘尝试的结果。"""

    status: str
    relative_path: str | None
    error: str | None


def _filename_for_source(source_paper_id: str) -> str:
    """把 source id 归一成安全且稳定的 PDF 文件名。"""
    sanitized = _UNSAFE_FILENAME_CHARS.sub("-", source_paper_id).strip("-")
    if not sanitized:
        sanitized = "paper"
    return f"{sanitized}.pdf"


class ResearchPdfStore:
    """负责把论文 PDF 保存到 DeerFlow 的 per-user corpus 目录。"""

    def __init__(
        self,
        *,
        download_pdf: Callable[[str], Awaitable[bytes]] | None = None,
    ) -> None:
        self._download_pdf = download_pdf or self._default_download_pdf

    @staticmethod
    async def _default_download_pdf(url: str) -> bytes:
        """默认通过 ``httpx`` 下载 PDF 原始字节。"""
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(url)
            response.raise_for_status()
            return await response.aread()

    async def store_pdf(
        self,
        *,
        user_id: str,
        source_name: str,
        source_paper_id: str,
        pdf_url: str | None,
    ) -> StoredPdfResult:
        """按稳定路径保存一篇论文的 PDF，并在重复 run 时复用已有文件。"""
        filename = _filename_for_source(source_paper_id)
        relative_path = Path("research") / "corpus" / "pdfs" / source_name / filename
        destination_dir = await asyncio.to_thread(
            lambda: get_paths().user_corpus_pdfs_dir(user_id, source_name=source_name),
        )
        destination = destination_dir / filename

        if await asyncio.to_thread(destination.exists):
            return StoredPdfResult(status="stored", relative_path=relative_path.as_posix(), error=None)

        if not pdf_url:
            return StoredPdfResult(status="missing", relative_path=None, error="paper does not provide a pdf url")

        try:
            pdf_bytes = await self._download_pdf(pdf_url)
        except Exception as exc:  # noqa: BLE001 - 需要把上游失败转成可见状态
            return StoredPdfResult(status="download_failed", relative_path=None, error=str(exc))

        try:
            await asyncio.to_thread(destination_dir.mkdir, parents=True, exist_ok=True)
            await asyncio.to_thread(write_upload_file_no_symlink, destination_dir, filename, pdf_bytes)
        except Exception as exc:  # noqa: BLE001 - 需要把本地存储失败转成可见状态
            return StoredPdfResult(status="storage_failed", relative_path=None, error=str(exc))

        return StoredPdfResult(status="stored", relative_path=relative_path.as_posix(), error=None)
