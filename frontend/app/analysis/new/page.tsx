import type { Metadata } from "next";

import { NewAnalysisClient } from "@/app/analysis/new/new-analysis-client";

export const metadata: Metadata = {
  title: "New Analysis",
  description: "Evaluate a simplified synthetic opportunity using the current prediction pipeline.",
};

export default function NewAnalysisPage() {
  return <NewAnalysisClient />;
}
