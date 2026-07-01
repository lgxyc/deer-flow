import { fetch } from "@/core/api/fetcher";
import { getBackendBaseURL } from "@/core/config";

import type { CreateTopicWatchRequest, TopicWatch } from "./types";

/** 统一拼接 Topic Watch API 地址。 */
function topicWatchesUrl(path = ""): string {
  return `${getBackendBaseURL()}/api/topic-watches${path}`;
}

/** 把后端 detail 尽量原样透传给 UI，避免用户只看到笼统失败。 */
async function throwTopicWatchApiError(
  response: Response,
  fallback: string,
): Promise<never> {
  const body = (await response.json().catch(() => ({}))) as {
    detail?: unknown;
  };
  throw new Error(typeof body.detail === "string" ? body.detail : fallback);
}

/** 拉取当前用户可见的 Topic Watch 列表。 */
export async function listTopicWatches(): Promise<TopicWatch[]> {
  const response = await fetch(topicWatchesUrl());
  if (!response.ok) {
    await throwTopicWatchApiError(
      response,
      `Failed to load Topic Watches: ${response.statusText}`,
    );
  }
  const body = (await response.json()) as { watches: TopicWatch[] };
  return body.watches;
}

/** 创建 Topic Watch，watch_id 由调用方负责提供幂等 key。 */
export async function createTopicWatch(
  request: CreateTopicWatchRequest,
): Promise<TopicWatch> {
  const response = await fetch(topicWatchesUrl(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    await throwTopicWatchApiError(
      response,
      `Failed to create Topic Watch: ${response.statusText}`,
    );
  }
  return response.json() as Promise<TopicWatch>;
}

/** 读取单个 Topic Watch 详情。 */
export async function getTopicWatch(watchId: string): Promise<TopicWatch> {
  const response = await fetch(
    topicWatchesUrl(`/${encodeURIComponent(watchId)}`),
  );
  if (!response.ok) {
    await throwTopicWatchApiError(
      response,
      `Failed to load Topic Watch: ${response.statusText}`,
    );
  }
  return response.json() as Promise<TopicWatch>;
}
