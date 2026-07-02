"use client";

import { ExternalLinkIcon, FileTextIcon } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18n } from "@/core/i18n/hooks";
import { usePapers } from "@/core/papers/hooks";
import type { PaperPdfStatus } from "@/core/papers/types";
import { externalLinkClass } from "@/lib/utils";

function badgeVariantForPdfStatus(status: PaperPdfStatus) {
  // 让 stored / missing / failed 三类状态在列表里一眼区分。
  if (status === "stored") return "default";
  if (status === "missing") return "secondary";
  return "destructive";
}

function formatPdfStatus(
  status: PaperPdfStatus,
  t: ReturnType<typeof useI18n>["t"],
): string {
  // 文案与后端状态值一一对应，避免 UI 自己发明第四套命名。
  if (status === "stored") return t.papers.pdfStatusStored;
  if (status === "missing") return t.papers.pdfStatusMissing;
  if (status === "download_failed") return t.papers.pdfStatusDownloadFailed;
  return t.papers.pdfStatusStorageFailed;
}

/** Paper Queue / Corpus 页面：负责列出当前用户可见的 Paper Record。 */
export function PaperCorpusBoard() {
  const { t } = useI18n();
  const { papers, isLoading, error } = usePapers();

  return (
    <div className="flex size-full flex-col">
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h1 className="text-xl font-semibold">{t.papers.title}</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">
            {t.papers.description}
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
          </div>
        ) : error ? (
          <p className="text-destructive text-sm">
            {error instanceof Error ? error.message : t.papers.loadError}
          </p>
        ) : papers.length === 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>{t.papers.emptyTitle}</CardTitle>
              <CardDescription>{t.papers.emptyDescription}</CardDescription>
            </CardHeader>
          </Card>
        ) : (
          <div className="grid gap-4">
            {papers.map((paper) => (
              <Card key={paper.paper_id}>
                <CardHeader className="gap-3">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{paper.title}</CardTitle>
                      <CardDescription>
                        {paper.source_name}:{paper.source_paper_id}
                      </CardDescription>
                    </div>
                    <Badge variant={badgeVariantForPdfStatus(paper.pdf_status)}>
                      {formatPdfStatus(paper.pdf_status, t)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <p className="text-muted-foreground line-clamp-3">
                    {paper.abstract}
                  </p>

                  <div className="flex flex-wrap gap-2">
                    {paper.matched_query_terms.map((term) => (
                      <Badge key={term} variant="outline">
                        {term}
                      </Badge>
                    ))}
                  </div>

                  <div className="text-muted-foreground flex flex-wrap items-center gap-4 text-xs">
                    <span>
                      {t.papers.discoveredFrom}:{" "}
                      {paper.discovered_watch_ids.join(", ")}
                    </span>
                    <span>
                      {t.papers.publishedAt}:{" "}
                      {paper.published_at ?? t.papers.none}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Button asChild size="sm" variant="outline">
                      <Link href={`/workspace/papers/${paper.paper_id}`}>
                        <FileTextIcon />
                        <span>{t.papers.viewDetail}</span>
                      </Link>
                    </Button>
                    <a
                      className={externalLinkClass}
                      href={paper.source_abs_url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      <span>{t.papers.openSource}</span>
                      <ExternalLinkIcon className="ml-1 inline size-3" />
                    </a>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
