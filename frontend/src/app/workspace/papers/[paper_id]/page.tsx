import { PaperRecordDetail } from "@/components/workspace/papers/paper-record-detail";

/** Paper Record 详情页路由入口。 */
export default async function PaperRecordDetailPage({
  params,
}: {
  params: Promise<{ paper_id: string }>;
}) {
  const { paper_id } = await params;
  return <PaperRecordDetail paperId={paper_id} />;
}
