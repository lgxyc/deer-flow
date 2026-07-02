import { beforeEach, describe, expect, test, rs } from "@rstest/core";

rs.mock("@/core/api/fetcher", () => ({
  fetch: rs.fn(),
}));

rs.mock("@/core/config", () => ({
  getBackendBaseURL: () => "/backend",
}));

import { fetch as fetcher } from "@/core/api/fetcher";
import { getPaper, listPapers } from "@/core/papers/api";

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

describe("papers api", () => {
  test("loads paper list", async () => {
    mockedFetch.mockResolvedValueOnce(
      jsonResponse(200, {
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

    await expect(listPapers()).resolves.toHaveLength(1);
    expect(mockedFetch).toHaveBeenCalledWith("/backend/api/papers");
  });

  test("loads a single paper detail", async () => {
    mockedFetch.mockResolvedValueOnce(
      jsonResponse(200, {
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
      }),
    );

    await expect(getPaper("paper-1")).resolves.toMatchObject({
      paper_id: "paper-1",
      pdf_status: "stored",
    });
    expect(mockedFetch).toHaveBeenCalledWith("/backend/api/papers/paper-1");
  });
});
