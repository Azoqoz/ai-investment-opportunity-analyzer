import type { ReactNode } from "react";

import { ProductHeader } from "@/components/product-header";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <ProductHeader />
      <main className="workspace">{children}</main>
    </div>
  );
}
