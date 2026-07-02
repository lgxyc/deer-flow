"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

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
import type { TopicWatchIngestResult } from "@/core/papers/types";
import {
  useRunTopicWatchIngest,
  useTopicWatch,
} from "@/core/topic-watches/hooks";
import type {
  TopicWatchSchedulePreset,
  TopicWatchTemplateFamily,
} from "@/core/topic-watches/types";

function formatTemplateFamily(
  value: TopicWatchTemplateFamily,
  t: ReturnType<typeof useI18n>["t"],
): string {
  return value === "solution_platform"
    ? t.topicWatches.templateFamilySolutionPlatform
    : t.topicWatches.templateFamilySurvey;
}

function formatSchedulePreset(
  value: TopicWatchSchedulePreset,
  t: ReturnType<typeof useI18n>["t"],
): string {
  if (value === "daily") return t.topicWatches.scheduleDaily;
  if (value === "every_3_days") return t.topicWatches.scheduleEvery3Days;
  return t.topicWatches.scheduleWeekly;
}

/** Topic Watch 详情页：展示持久化配置与稳定元数据。 */
export function TopicWatchDetail({ watchId }: { watchId: string }) {
  const { t } = useI18n();
  const { watch, isLoading, error } = useTopicWatch(watchId);
  const runIngestMutation = useRunTopicWatchIngest();
  const [lastIngestResult, setLastIngestResult] =
    useState<TopicWatchIngestResult | null>(null);

  /** 触发手动 ingest，并把这次结果保留在详情页上下文里。 */
  const handleRunIngest = async () => {
    try {
      const result = await runIngestMutation.mutateAsync(watchId);
      setLastIngestResult(result);
      toast.success(
        t.topicWatches.ingestSuccess(
          result.created_count,
          result.deduped_count,
          result.failed_count,
        ),
      );
    } catch (mutationError) {
      toast.error(
        mutationError instanceof Error
          ? mutationError.message
          : t.topicWatches.ingestError,
      );
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (error || !watch) {
    return (
      <div className="p-6">
        <Card>
          <CardHeader>
            <CardTitle>{t.topicWatches.notFoundTitle}</CardTitle>
            <CardDescription>
              {error instanceof Error ? error.message : t.topicWatches.notFound}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/workspace/topic-watches">
                {t.topicWatches.backToBoard}
              </Link>
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
          <h1 className="text-xl font-semibold">
            {t.topicWatches.detailTitle}
          </h1>
          <p className="text-muted-foreground mt-0.5 text-sm">
            {watch.watch_id}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            disabled={runIngestMutation.isPending}
            onClick={() => void handleRunIngest()}
          >
            {runIngestMutation.isPending
              ? t.topicWatches.ingesting
              : t.topicWatches.runIngest}
          </Button>
          <Button asChild variant="outline">
            <Link href="/workspace/topic-watches">
              {t.topicWatches.backToBoard}
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-6 p-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t.topicWatches.configurationTitle}</CardTitle>
            <CardDescription>
              {t.topicWatches.configurationDescription}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div>
              <p className="text-muted-foreground">
                {t.topicWatches.queryTerms}
              </p>
              <p className="mt-1 font-medium">{watch.query_terms.join(", ")}</p>
            </div>
            <div>
              <p className="text-muted-foreground">
                {t.topicWatches.seedPapers}
              </p>
              <p className="mt-1 font-medium">
                {watch.seed_papers.length > 0
                  ? watch.seed_papers.join(", ")
                  : t.topicWatches.none}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">
                {t.topicWatches.templateFamily}
              </p>
              <p className="mt-1 font-medium">
                {formatTemplateFamily(watch.template_family, t)}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">
                {t.topicWatches.schedulePreset}
              </p>
              <p className="mt-1 font-medium">
                {formatSchedulePreset(watch.schedule_preset, t)}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">{t.topicWatches.enabled}</p>
              <p className="mt-1 font-medium">
                {watch.enabled
                  ? t.topicWatches.statusEnabled
                  : t.topicWatches.statusDisabled}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t.topicWatches.metadataTitle}</CardTitle>
            <CardDescription>
              {t.topicWatches.metadataDescription}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div>
              <p className="text-muted-foreground">{t.topicWatches.watchId}</p>
              <p className="mt-1 font-medium">{watch.watch_id}</p>
            </div>
            <div>
              <p className="text-muted-foreground">
                {t.topicWatches.createdAt}
              </p>
              <p className="mt-1 font-medium">
                {new Date(watch.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">
                {t.topicWatches.updatedAt}
              </p>
              <p className="mt-1 font-medium">
                {new Date(watch.updated_at).toLocaleString()}
              </p>
            </div>
          </CardContent>
        </Card>

        {lastIngestResult ? (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>{t.topicWatches.ingestResultTitle}</CardTitle>
              <CardDescription>
                {t.topicWatches.ingestResultDescription}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="flex flex-wrap gap-2">
                <Badge>
                  {t.topicWatches.ingestCreatedSummary(
                    lastIngestResult.created_count,
                  )}
                </Badge>
                <Badge variant="outline">
                  {t.topicWatches.ingestStats(
                    lastIngestResult.deduped_count,
                    lastIngestResult.failed_count,
                  )}
                </Badge>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button asChild variant="outline">
                  <Link href="/workspace/papers">
                    {t.topicWatches.openCorpus}
                  </Link>
                </Button>
              </div>

              <div className="grid gap-3">
                {lastIngestResult.papers.map((paper) => (
                  <Card key={paper.paper_id}>
                    <CardContent className="flex flex-col gap-3 pt-6 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="font-medium">{paper.title}</p>
                        <p className="text-muted-foreground text-xs">
                          {paper.source_name}:{paper.source_paper_id}
                        </p>
                      </div>
                      <Button asChild size="sm" variant="outline">
                        <Link href={`/workspace/papers/${paper.paper_id}`}>
                          {t.papers.viewDetail}
                        </Link>
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
