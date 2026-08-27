import type { Metadata } from "next";

import { OpportunityDetailClient } from "@/app/opportunities/[id]/opportunity-detail-client";

type DetailPageProps = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: DetailPageProps): Promise<Metadata> {
  const { id } = await params;
  return {
    title: `Opportunity ${id}`,
    description: `Stored synthetic evaluation for opportunity ${id}.`,
  };
}

export default async function OpportunityDetailPage({ params }: DetailPageProps) {
  const { id } = await params;
  return <OpportunityDetailClient opportunityId={id} />;
}
