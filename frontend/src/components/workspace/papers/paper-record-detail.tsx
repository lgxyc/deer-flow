"use client";

import { ExternalLinkIcon } from "lucide-react";
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
import { usePaper } from "@/core/papers/hooks";
import type { PaperPdfStatus } from "@/core/papers/types";
import { externalLinkClass } from "@/lib/utils";

function badgeVariantForPdfStatus(status: PaperPdfStatus) {
  // 详情页与列表页共用同一套视觉层级，避免状态颜色漂移。
  if (status === "stored") return "default";
  if (status === "missing") return "secondary";
  return "destructive";
}

function formatPdfStatus(
  status: PaperPdfStatus,
  t: ReturnType<typeof useI18n>["t"],
): string {
  // 保持详情页对 PDF 状态的翻译与列表页完全一致。
  if (status === "stored") return t.papers.pdfStatusStored;
  if (status === "missing") return t.papers.pdfStatusMissing;
  if (status === "download_failed") return t.papers.pdfStatusDownloadFailed;
  return t.papers.pdfStatusStorageFailed;
}

/** Paper Record 详情页：展示论文原始元数据与本地 PDF 状态。 */
export function PaperRecordDetail({ paperId }: { paperId: string }) {
  const { t } = useI18n();
  const { paper, isLoading, error } = usePaper(paperId);

  if (isLoading) {
    return (
      <div className="p-6">
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (error || !paper) {
    return (
      <div className="p-6">
        <Card>
          <CardHeader>
            <CardTitle>{t.papers.notFoundTitle}</CardTitle>
            <CardDescription>
              {error instanceof Error ? error.message : t.papers.notFound}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/workspace/papers">{t.papers.backToCorpus}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex size-full flex-col">
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h1 className="text-xl font-semibold">{t.papers.detailTitle}</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">
            {paper.paper_id}
          </p>
        </div>
        <Button asChild variant="outline">
          <Link href="/workspace/papers">{t.papers.backToCorpus}</Link>
        </Button>
      </div>

      <div className="grid gap-6 p-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{paper.title}</CardTitle>
            <CardDescription>
              {paper.source_name}:{paper.source_paper_id}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div>
              <p className="text-muted-foreground">{t.papers.abstract}</p>
              <p className="mt-1 whitespace-pre-wrap">{paper.abstract}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t.papers.authors}</p>
              <p className="mt-1 font-medium">
                {paper.authors.length > 0
                  ? paper.authors.join(", ")
                  : t.papers.none}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">{t.papers.categories}</p>
              <p className="mt-1 font-medium">
                {paper.categories.length > 0
                  ? paper.categories.join(", ")
                  : t.papers.none}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">{t.papers.discoveredFrom}</p>
              <p className="mt-1 font-medium">
                {paper.discovered_watch_ids.join(", ")}
              </p>
            </div>
            <a
              className={externalLinkClass}
              href={paper.source_abs_url}
              rel="noreferrer"
              target="_blank"
            >
              <span>{t.papers.openSource}</span>
              <ExternalLinkIcon className="ml-1 inline size-3" />
            </a>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t.papers.corpusStatusTitle}</CardTitle>
            <CardDescription>
              {t.papers.corpusStatusDescription}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div>
              <p className="text-muted-foreground">{t.papers.pdfStatus}</p>
              <div className="mt-1">
                <Badge variant={badgeVariantForPdfStatus(paper.pdf_status)}>
                  {formatPdfStatus(paper.pdf_status, t)}
                </Badge>
              </div>
            </div>
            <div>
              <p className="text-muted-foreground">{t.papers.pdfPath}</p>
              <p className="mt-1 font-medium break-all">
                {paper.pdf_relative_path ?? t.papers.none}
              </p>
            </div>
            {paper.pdf_error ? (
              <div>
                <p className="text-muted-foreground">{t.papers.pdfError}</p>
                <p className="text-destructive mt-1">{paper.pdf_error}</p>
              </div>
            ) : null}
            <div>
              <p className="text-muted-foreground">{t.papers.matchedQueries}</p>
              <p className="mt-1 font-medium">
                {paper.matched_query_terms.length > 0
                  ? paper.matched_query_terms.join(", ")
                  : t.papers.none}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">{t.papers.createdAt}</p>
              <p className="mt-1 font-medium">
                {new Date(paper.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">{t.papers.updatedAt}</p>
              <p className="mt-1 font-medium">
                {new Date(paper.updated_at).toLocaleString()}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
