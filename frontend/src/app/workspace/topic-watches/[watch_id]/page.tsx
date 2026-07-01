import { TopicWatchDetail } from "@/components/workspace/topic-watches/topic-watch-detail";

export default async function TopicWatchDetailPage({
  params,
}: {
  params: Promise<{ watch_id: string }>;
}) {
  const { watch_id } = await params;
  return <TopicWatchDetail watchId={watch_id} />;
}
