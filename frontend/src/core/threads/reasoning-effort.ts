export type ThreadMode = "flash" | "thinking" | "pro" | "ultra";

export type ReasoningEffort = "minimal" | "low" | "medium" | "high" | "xhigh";

export const REASONING_EFFORT_OPTIONS: readonly ReasoningEffort[] = [
  "minimal",
  "low",
  "medium",
  "high",
  "xhigh",
];

/** 根据工作台模式推导默认推理强度，保持前端展示与提交行为一致。 */
export function getDefaultReasoningEffortForMode(
  mode: ThreadMode | undefined,
): ReasoningEffort | undefined {
  switch (mode) {
    case "flash":
      return "minimal";
    case "thinking":
      return "low";
    case "pro":
      return "medium";
    case "ultra":
      return "xhigh";
    default:
      return undefined;
  }
}
