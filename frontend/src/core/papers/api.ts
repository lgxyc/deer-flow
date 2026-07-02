import { fetch } from "@/core/api/fetcher";
import { getBackendBaseURL } from "@/core/config";

import type { PaperRecord } from "./types";

/** 统一拼接 Paper Record API 地址。 */
function papersUrl(path = ""): string {
  return `${getBackendBaseURL()}/api/papers${path}`;
}

/** 把后端 detail 尽量原样透传给 UI，避免用户只看到笼统失败。 */
async function throwPapersApiError(
  response: Response,
  fallback: string,
): Promise<never> {
  const body = (await response.json().catch(() => ({}))) as {
    detail?: unknown;
  };
  throw new Error(typeof body.detail === "string" ? body.detail : fallback);
}

/** 拉取当前用户可见的 Paper Record 列表。 */
export async function listPapers(): Promise<PaperRecord[]> {
  const response = await fetch(papersUrl());
  if (!response.ok) {
    await throwPapersApiError(
      response,
      `Failed to load Paper Records: ${response.statusText}`,
    );
  }
  const body = (await response.json()) as { papers: PaperRecord[] };
  return body.papers;
}

/** 读取单个 Paper Record 详情。 */
export async function getPaper(paperId: string): Promise<PaperRecord> {
  const response = await fetch(papersUrl(`/${encodeURIComponent(paperId)}`));
  if (!response.ok) {
    await throwPapersApiError(
      response,
      `Failed to load Paper Record: ${response.statusText}`,
    );
  }
  return response.json() as Promise<PaperRecord>;
}
