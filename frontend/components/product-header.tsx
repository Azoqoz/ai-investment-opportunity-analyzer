"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/", label: "Overview" },
  { href: "/opportunities", label: "Universe" },
  { href: "/analysis/new", label: "New Analysis" },
  { href: "/methodology", label: "Methodology" },
];

function routeIsActive(pathname: string, href: string) {
  if (href === "/") return pathname === href;
  return pathname.startsWith(href);
}

export function ProductHeader() {
  const pathname = usePathname();

  return (
    <header className="product-header">
      <Link className="product-identity" href="/">
        <span className="terminal-mark" aria-hidden="true">IOA</span>
        <span>Investment Opportunity Analyzer</span>
      </Link>

      <nav className="terminal-nav" aria-label="Primary navigation">
        {navigation.map((item) => {
          const active = routeIsActive(pathname, item.href);
          return (
            <Link
              className={active ? "terminal-nav-active" : undefined}
              href={item.href}
              key={item.href}
              aria-current={active ? "page" : undefined}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="header-status">
        <span>Synthetic Universe <i aria-hidden="true" /> 5,000 records</span>
        <span className="api-state"><i aria-hidden="true" /> API offline</span>
      </div>
    </header>
  );
}
