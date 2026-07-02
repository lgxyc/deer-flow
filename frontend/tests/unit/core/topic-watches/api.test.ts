import { beforeEach, describe, expect, test, rs } from "@rstest/core";

rs.mock("@/core/api/fetcher", () => ({
  fetch: rs.fn(),
}));

rs.mock("@/core/config", () => ({
  getBackendBaseURL: () => "/backend",
}));

import { fetch as fetcher } from "@/core/api/fetcher";
import {
  createTopicWatch,
  getTopicWatch,
  listTopicWatches,
  runTopicWatchIngest,
} from "@/core/topic-watches/api";

const mockedFetch = rs.mocked(fetcher);

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    statusText: status >= 400 ? "Bad Request" : "OK",
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  mockedFetch.mockReset();
});

describe("topic watches api", () => {
  test("loads topic watch list", async () => {
    mockedFetch.mockResolvedValueOnce(
      jsonResponse(200, {
        watches: [
          {
            watch_id: "watch-1",
            query_terms: ["secure storage"],
            seed_papers: [],
            template_family: "solution_platform",
            schedule_preset: "weekly",
            enabled: true,
            created_at: "2026-07-01T12:00:00Z",
            updated_at: "2026-07-01T12:00:00Z",
          },
        ],
      }),
    );

    await expect(listTopicWatches()).resolves.toHaveLength(1);
    expect(mockedFetch).toHaveBeenCalledWith("/backend/api/topic-watches");
  });

  test("creates a topic watch", async () => {
    mockedFetch.mockResolvedValueOnce(
      jsonResponse(200, {
        watch_id: "watch-1",
        query_terms: ["secure storage"],
        seed_papers: ["arXiv:2501.00001"],
        template_family: "solution_platform",
        schedule_preset: "weekly",
        enabled: true,
        created_at: "2026-07-01T12:00:00Z",
        updated_at: "2026-07-01T12:00:00Z",
      }),
    );

    await expect(
      createTopicWatch({
        watch_id: "watch-1",
        query_terms: ["secure storage"],
        seed_papers: ["arXiv:2501.00001"],
        template_family: "solution_platform",
        schedule_preset: "weekly",
        enabled: true,
      }),
    ).resolves.toMatchObject({
      watch_id: "watch-1",
      template_family: "solution_platform",
    });
  });

  test("loads a single topic watch", async () => {
    mockedFetch.mockResolvedValueOnce(
      jsonResponse(200, {
        watch_id: "watch-1",
        query_terms: ["secure storage"],
        seed_papers: [],
        template_family: "survey",
        schedule_preset: "daily",
        enabled: false,
        created_at: "2026-07-01T12:00:00Z",
        updated_at: "2026-07-01T12:00:00Z",
      }),
    );

    await expect(getTopicWatch("watch-1")).resolves.toMatchObject({
      watch_id: "watch-1",
      schedule_preset: "daily",
    });
    expect(mockedFetch).toHaveBeenCalledWith(
      "/backend/api/topic-watches/watch-1",
    );
  });

  test("runs manual topic watch ingest", async () => {
    mockedFetch.mockResolvedValueOnce(
      jsonResponse(200, {
        watch_id: "watch-1",
        searched_queries: ["secure storage"],
        total_hits: 1,
        screened_in_count: 1,
        created_count: 1,
        deduped_count: 0,
        failed_count: 0,
        papers: [
          {
            paper_id: "paper-1",
            source_name: "arxiv",
            source_paper_id: "2501.00001",
            title: "Secure Storage with Deduplication",
            abstract: "abstract",
            authors: ["Alice"],
            categories: ["cs.CR"],
            discovered_watch_ids: ["watch-1"],
            matched_query_terms: ["secure storage"],
            published_at: "2025-01-01",
            source_updated_at: "2025-01-02",
            source_abs_url: "https://arxiv.org/abs/2501.00001",
            source_pdf_url: "https://arxiv.org/pdf/2501.00001.pdf",
            pdf_status: "stored",
            pdf_relative_path: "research/corpus/pdfs/arxiv/2501.00001.pdf",
            pdf_error: null,
            created_at: "2026-07-01T12:00:00Z",
            updated_at: "2026-07-01T12:00:00Z",
          },
        ],
      }),
    );

    await expect(runTopicWatchIngest("watch-1")).resolves.toMatchObject({
      watch_id: "watch-1",
      created_count: 1,
      papers: [{ paper_id: "paper-1", pdf_status: "stored" }],
    });
    expect(mockedFetch).toHaveBeenCalledWith(
      "/backend/api/topic-watches/watch-1/ingest",
      {
        method: "POST",
      },
    );
  });
});
