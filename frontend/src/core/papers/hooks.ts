import { useQuery } from "@tanstack/react-query";

import { getPaper, listPapers } from "./api";

export const papersQueryKey = ["papers"] as const;

/** 查询 Paper Queue / Corpus 列表数据。 */
export function usePapers() {
  const { data, isLoading, error } = useQuery({
    queryKey: papersQueryKey,
    queryFn: () => listPapers(),
  });
  return { papers: data ?? [], isLoading, error };
}

/** 查询单个 Paper Record 详情。 */
export function usePaper(paperId: string | null | undefined) {
  const { data, isLoading, error } = useQuery({
    queryKey: [...papersQueryKey, paperId],
    queryFn: () => getPaper(paperId!),
    enabled: !!paperId,
  });
  return { paper: data ?? null, isLoading, error };
}
