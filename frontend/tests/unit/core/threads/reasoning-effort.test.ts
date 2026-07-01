import { expect, test } from "@rstest/core";

import {
  getDefaultReasoningEffortForMode,
  getReasoningEffortForRequest,
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

test("提交上下文在 ultra 模式下默认发送 xhigh", () => {
  expect(getReasoningEffortForRequest("ultra", undefined)).toBe("xhigh");
});

test("提交上下文保留显式选择的 xhigh 与 flash 空值语义", () => {
  expect(getReasoningEffortForRequest("pro", "xhigh")).toBe("xhigh");
  expect(getReasoningEffortForRequest("flash", undefined)).toBeUndefined();
});
