"use client";

import Link from "next/link";

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
import { useTopicWatch } from "@/core/topic-watches/hooks";
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
        <Button asChild variant="outline">
          <Link href="/workspace/topic-watches">
            {t.topicWatches.backToBoard}
          </Link>
        </Button>
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
      </div>
    </div>
  );
}
