export type PaperPdfStatus =
  | "stored"
  | "missing"
  | "download_failed"
  | "storage_failed";

export interface PaperRecord {
  paper_id: string;
  source_name: string;
  source_paper_id: string;
  title: string;
  abstract: string;
  authors: string[];
  categories: string[];
  discovered_watch_ids: string[];
  matched_query_terms: string[];
  published_at: string | null;
  source_updated_at: string | null;
  source_abs_url: string;
  source_pdf_url: string | null;
  pdf_status: PaperPdfStatus;
  pdf_relative_path: string | null;
  pdf_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface TopicWatchIngestResult {
  watch_id: string;
  searched_queries: string[];
  total_hits: number;
  screened_in_count: number;
  created_count: number;
  deduped_count: number;
  failed_count: number;
  papers: PaperRecord[];
}
