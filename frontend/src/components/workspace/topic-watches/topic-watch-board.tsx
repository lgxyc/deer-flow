"use client";

import { SearchIcon } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { useI18n } from "@/core/i18n/hooks";
import {
  useCreateTopicWatch,
  useTopicWatches,
} from "@/core/topic-watches/hooks";
import {
  TOPIC_WATCH_SCHEDULE_PRESETS,
  TOPIC_WATCH_TEMPLATE_FAMILIES,
  type CreateTopicWatchRequest,
  type TopicWatchSchedulePreset,
  type TopicWatchTemplateFamily,
} from "@/core/topic-watches/types";
import { uuid } from "@/core/utils/uuid";

function parseMultilineInput(value: string): string[] {
  // 把多行/逗号输入统一拆成去重数组，避免表单把空白项传给后端。
  const normalized: string[] = [];
  const seen = new Set<string>();
  for (const piece of value.split(/[\n,]+/)) {
    const cleaned = piece.trim();
    if (!cleaned || seen.has(cleaned)) {
      continue;
    }
    normalized.push(cleaned);
    seen.add(cleaned);
  }
  return normalized;
}

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

/** Topic Watch Board：负责创建、列出并跳转到详情页。 */
export function TopicWatchBoard() {
  const { t } = useI18n();
  const { watches, isLoading, error } = useTopicWatches();
  const createMutation = useCreateTopicWatch();
  const [queryTermsInput, setQueryTermsInput] = useState("");
  const [seedPapersInput, setSeedPapersInput] = useState("");
  const [templateFamily, setTemplateFamily] =
    useState<TopicWatchTemplateFamily>("solution_platform");
  const [schedulePreset, setSchedulePreset] =
    useState<TopicWatchSchedulePreset>("weekly");
  const [enabled, setEnabled] = useState(true);

  const canSubmit = useMemo(
    () => queryTermsInput.trim().length > 0 && !createMutation.isPending,
    [createMutation.isPending, queryTermsInput],
  );

  /** 提交创建请求，并在成功后把表单恢复到默认状态。 */
  const handleCreate = async () => {
    // 在前端先做一次轻量归一化，让列表和详情马上看到稳定字段值。
    const request: CreateTopicWatchRequest = {
      watch_id: uuid(),
      query_terms: parseMultilineInput(queryTermsInput),
      seed_papers: parseMultilineInput(seedPapersInput),
      template_family: templateFamily,
      schedule_preset: schedulePreset,
      enabled,
    };
    if (request.query_terms.length === 0) {
      toast.error(t.topicWatches.queryTermsRequired);
      return;
    }

    try {
      await createMutation.mutateAsync(request);
      toast.success(t.topicWatches.createdSuccess);
      setQueryTermsInput("");
      setSeedPapersInput("");
      setTemplateFamily("solution_platform");
      setSchedulePreset("weekly");
      setEnabled(true);
    } catch (mutationError) {
      toast.error(
        mutationError instanceof Error
          ? mutationError.message
          : t.topicWatches.createError,
      );
    }
  };

  return (
    <div className="flex size-full flex-col">
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h1 className="text-xl font-semibold">{t.topicWatches.title}</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">
            {t.topicWatches.description}
          </p>
        </div>
      </div>

      <div className="grid flex-1 gap-6 overflow-y-auto p-6 lg:grid-cols-[minmax(22rem,28rem)_1fr]">
        <Card className="h-fit">
          <CardHeader>
            <CardTitle>{t.topicWatches.createTitle}</CardTitle>
            <CardDescription>
              {t.topicWatches.createDescription}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-2">
              <label
                className="text-sm font-medium"
                htmlFor="topic-watch-query-terms"
              >
                {t.topicWatches.queryTerms}
              </label>
              <Textarea
                id="topic-watch-query-terms"
                value={queryTermsInput}
                onChange={(event) => setQueryTermsInput(event.target.value)}
                placeholder={t.topicWatches.queryTermsPlaceholder}
              />
            </div>

            <div className="space-y-2">
              <label
                className="text-sm font-medium"
                htmlFor="topic-watch-seed-papers"
              >
                {t.topicWatches.seedPapers}
              </label>
              <Textarea
                id="topic-watch-seed-papers"
                value={seedPapersInput}
                onChange={(event) => setSeedPapersInput(event.target.value)}
                placeholder={t.topicWatches.seedPapersPlaceholder}
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  {t.topicWatches.templateFamily}
                </label>
                <Select
                  value={templateFamily}
                  onValueChange={(value: TopicWatchTemplateFamily) =>
                    setTemplateFamily(value)
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TOPIC_WATCH_TEMPLATE_FAMILIES.map((value) => (
                      <SelectItem key={value} value={value}>
                        {formatTemplateFamily(value, t)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  {t.topicWatches.schedulePreset}
                </label>
                <Select
                  value={schedulePreset}
                  onValueChange={(value: TopicWatchSchedulePreset) =>
                    setSchedulePreset(value)
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TOPIC_WATCH_SCHEDULE_PRESETS.map((value) => (
                      <SelectItem key={value} value={value}>
                        {formatSchedulePreset(value, t)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center justify-between rounded-lg border px-3 py-2">
              <div>
                <p className="text-sm font-medium">{t.topicWatches.enabled}</p>
                <p className="text-muted-foreground text-xs">
                  {enabled
                    ? t.topicWatches.enabledDescriptionOn
                    : t.topicWatches.enabledDescriptionOff}
                </p>
              </div>
              <Switch checked={enabled} onCheckedChange={setEnabled} />
            </div>
          </CardContent>
          <CardFooter>
            <Button
              className="w-full"
              disabled={!canSubmit}
              onClick={() => void handleCreate()}
            >
              {createMutation.isPending
                ? t.topicWatches.creating
                : t.topicWatches.createButton}
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t.topicWatches.boardTitle}</CardTitle>
            <CardDescription>{t.topicWatches.boardDescription}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
              </div>
            ) : error ? (
              <p className="text-destructive text-sm">
                {error instanceof Error
                  ? error.message
                  : t.topicWatches.loadError}
              </p>
            ) : watches.length === 0 ? (
              <div className="flex min-h-56 flex-col items-center justify-center gap-3 rounded-xl border border-dashed px-6 text-center">
                <div className="bg-muted flex h-14 w-14 items-center justify-center rounded-full">
                  <SearchIcon className="text-muted-foreground h-7 w-7" />
                </div>
                <div>
                  <p className="font-medium">{t.topicWatches.emptyTitle}</p>
                  <p className="text-muted-foreground mt-1 text-sm">
                    {t.topicWatches.emptyDescription}
                  </p>
                </div>
              </div>
            ) : (
              watches.map((watch) => (
                <div
                  key={watch.watch_id}
                  className="rounded-xl border p-4 shadow-xs"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-2">
                      <p className="font-medium">
                        {watch.query_terms.join(", ")}
                      </p>
                      <p className="text-muted-foreground text-sm">
                        {formatTemplateFamily(watch.template_family, t)}
                        {" · "}
                        {formatSchedulePreset(watch.schedule_preset, t)}
                        {" · "}
                        {watch.enabled
                          ? t.topicWatches.statusEnabled
                          : t.topicWatches.statusDisabled}
                      </p>
                      {watch.seed_papers.length > 0 ? (
                        <p className="text-muted-foreground text-sm">
                          {t.topicWatches.seedPapersLabel}
                          {": "}
                          {watch.seed_papers.join(", ")}
                        </p>
                      ) : null}
                    </div>
                    <Button asChild variant="outline" size="sm">
                      <Link href={`/workspace/topic-watches/${watch.watch_id}`}>
                        {t.topicWatches.viewDetails}
                      </Link>
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
