import { expect, test, type Page } from "@playwright/test";

import { mockLangGraphAPI } from "./utils/mock-api";

type MockTopicWatch = {
  watch_id: string;
  query_terms: string[];
  seed_papers: string[];
  template_family: "solution_platform" | "survey";
  schedule_preset: "daily" | "every_3_days" | "weekly";
  enabled: boolean;
  created_at: string;
  updated_at: string;
};

type MockPaper = {
  paper_id: string;
  source_name: "arxiv";
  source_paper_id: string;
  title: string;
  abstract: string;
  authors: string[];
  categories: string[];
  discovered_watch_ids: string[];
  matched_query_terms: string[];
  published_at: string;
  source_updated_at: string;
  source_abs_url: string;
  source_pdf_url: string;
  pdf_status: "stored" | "download_failed";
  pdf_relative_path: string | null;
  pdf_error: string | null;
  created_at: string;
  updated_at: string;
};

function mockResearchPlatformApi(page: Page) {
  const watches: MockTopicWatch[] = [
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
  ];
  const papers: MockPaper[] = [];

  void page.route("**/api/topic-watches", async (route) => {
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ watches }),
    });
  });

  void page.route("**/api/topic-watches/*/ingest", async (route) => {
    const paper: MockPaper = {
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
    };
    papers.splice(0, papers.length, paper);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        watch_id: "watch-1",
        searched_queries: ["secure storage"],
        total_hits: 1,
        screened_in_count: 1,
        created_count: 1,
        deduped_count: 0,
        failed_count: 0,
        papers,
      }),
    });
  });

  void page.route("**/api/topic-watches/*", async (route) => {
    const watchId = route.request().url().split("/").pop() ?? "";
    const watch = watches.find((item) => item.watch_id === watchId);
    if (!watch) {
      return route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Not found" }),
      });
    }
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(watch),
    });
  });

  void page.route("**/api/papers", async (route) => {
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ papers }),
    });
  });

  void page.route("**/api/papers/*", async (route) => {
    const paperId = route.request().url().split("/").pop() ?? "";
    const paper = papers.find((item) => item.paper_id === paperId);
    if (!paper) {
      return route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Not found" }),
      });
    }
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(paper),
    });
  });
}

test.describe("Topic Watch ingest flow", () => {
  test("runs ingest from watch detail and opens corpus detail", async ({
    page,
  }) => {
    mockLangGraphAPI(page);
    mockResearchPlatformApi(page);

    await page.goto("/workspace/topic-watches/watch-1");

    await page.getByRole("button", { name: "Run ingest" }).click();

    await expect(page.getByText("Created 1 paper record")).toBeVisible();
    await expect(page.getByRole("link", { name: "Open corpus" })).toBeVisible();

    await page.getByRole("link", { name: "Open corpus" }).click();
    await expect(
      page.getByRole("heading", { name: "Paper Queue / Corpus" }),
    ).toBeVisible();
    await expect(
      page.getByText("Secure Storage with Deduplication"),
    ).toBeVisible();

    await page.getByRole("link", { name: "View paper detail" }).click();
    await expect(
      page.getByRole("heading", { name: "Paper Record Detail" }),
    ).toBeVisible();
    await expect(
      page.getByText("research/corpus/pdfs/arxiv/2501.00001.pdf"),
    ).toBeVisible();
  });
});
