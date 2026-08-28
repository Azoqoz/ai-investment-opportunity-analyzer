"use client";

import type { ReactNode } from "react";

import { ApiStatusProvider } from "@/components/api-status-context";
import { ProductHeader } from "@/components/product-header";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <ApiStatusProvider>
      <div className="app-shell">
        <ProductHeader />
        <main className="workspace">{children}</main>
      </div>
    </ApiStatusProvider>
  );
}
