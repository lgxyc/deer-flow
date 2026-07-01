import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createTopicWatch, getTopicWatch, listTopicWatches } from "./api";
import type { CreateTopicWatchRequest } from "./types";

export const topicWatchesQueryKey = ["topic-watches"] as const;

/** 查询 Topic Watch Board 列表数据。 */
export function useTopicWatches() {
  const { data, isLoading, error } = useQuery({
    queryKey: topicWatchesQueryKey,
    queryFn: () => listTopicWatches(),
  });
  return { watches: data ?? [], isLoading, error };
}

/** 查询单个 Topic Watch 详情。 */
export function useTopicWatch(watchId: string | null | undefined) {
  const { data, isLoading, error } = useQuery({
    queryKey: [...topicWatchesQueryKey, watchId],
    queryFn: () => getTopicWatch(watchId!),
    enabled: !!watchId,
  });
  return { watch: data ?? null, isLoading, error };
}

/** 创建 Topic Watch，并刷新列表与详情缓存。 */
export function useCreateTopicWatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: CreateTopicWatchRequest) => createTopicWatch(request),
    onSuccess: (watch) => {
      void queryClient.invalidateQueries({ queryKey: topicWatchesQueryKey });
      void queryClient.invalidateQueries({
        queryKey: [...topicWatchesQueryKey, watch.watch_id],
      });
    },
  });
}
