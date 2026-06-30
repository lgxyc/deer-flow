import { expect, test } from "@rstest/core";

import {
  getDefaultReasoningEffortForMode,
  REASONING_EFFORT_OPTIONS,
} from "@/core/threads/reasoning-effort";

test("ultra 模式默认映射到 xhigh", () => {
  expect(getDefaultReasoningEffortForMode("ultra")).toBe("xhigh");
});

test("flash 与未选择模式保持既有默认行为", () => {
  expect(getDefaultReasoningEffortForMode("flash")).toBe("minimal");
  expect(getDefaultReasoningEffortForMode(undefined)).toBeUndefined();
});

test("工作台可枚举并显式选择 xhigh", () => {
  expect(REASONING_EFFORT_OPTIONS).toContain("xhigh");
});
