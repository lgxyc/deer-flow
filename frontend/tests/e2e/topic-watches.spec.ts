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

function mockTopicWatchApi(page: Page) {
  const watches: MockTopicWatch[] = [];

  void page.route("**/api/topic-watches", async (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ watches }),
      });
    }

    const body = route.request().postDataJSON() as {
      watch_id: string;
      query_terms: string[];
      seed_papers: string[];
      template_family: MockTopicWatch["template_family"];
      schedule_preset: MockTopicWatch["schedule_preset"];
      enabled: boolean;
    };
    const watch: MockTopicWatch = {
      ...body,
      created_at: "2026-07-01T12:00:00Z",
      updated_at: "2026-07-01T12:00:00Z",
    };
    watches.unshift(watch);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(watch),
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
}

test.describe("Topic Watch board", () => {
  test("creates a watch and opens its detail page", async ({ page }) => {
    mockLangGraphAPI(page);
    mockTopicWatchApi(page);

    await page.goto("/workspace/topic-watches");

    await page.getByLabel("Query terms").fill("secure storage\nproofs");
    await page.getByLabel("Seed papers").fill("arXiv:2501.00001");
    await page.getByRole("button", { name: "Create watch" }).click();

    await expect(page.getByText("secure storage, proofs")).toBeVisible();
    await expect(page.getByText("Seed papers: arXiv:2501.00001")).toBeVisible();

    await page.getByRole("link", { name: "View details" }).click();

    await expect(
      page.getByRole("heading", { name: "Topic Watch Detail" }),
    ).toBeVisible();
    await expect(page.getByText("secure storage, proofs")).toBeVisible();
    await expect(page.getByText("arXiv:2501.00001")).toBeVisible();
  });
});
