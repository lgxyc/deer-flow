export const TOPIC_WATCH_TEMPLATE_FAMILIES = [
  "solution_platform",
  "survey",
] as const;

export const TOPIC_WATCH_SCHEDULE_PRESETS = [
  "daily",
  "every_3_days",
  "weekly",
] as const;

export type TopicWatchTemplateFamily =
  (typeof TOPIC_WATCH_TEMPLATE_FAMILIES)[number];
export type TopicWatchSchedulePreset =
  (typeof TOPIC_WATCH_SCHEDULE_PRESETS)[number];

export interface TopicWatch {
  watch_id: string;
  query_terms: string[];
  seed_papers: string[];
  template_family: TopicWatchTemplateFamily;
  schedule_preset: TopicWatchSchedulePreset;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTopicWatchRequest {
  watch_id?: string;
  query_terms: string[];
  seed_papers: string[];
  template_family: TopicWatchTemplateFamily;
  schedule_preset: TopicWatchSchedulePreset;
  enabled: boolean;
}
