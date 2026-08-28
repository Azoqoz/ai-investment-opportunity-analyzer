import type { ReactNode } from "react";

type StatusTone = "neutral" | "invest" | "review" | "reject";

export function StatusLabel({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: StatusTone;
}) {
  return <span className={`status-label status-${tone}`}>{children}</span>;
}
