import Link from "next/link";

import { MobileNavigation } from "@/components/navigation/MobileNavigation";
import { ThemeToggle } from "@/components/navigation/ThemeToggle";
import { primaryNavLinks, siteConfig } from "@/lib/constants/site";

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-content items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="text-subheadline shrink-0 tracking-tight">
          {siteConfig.name}
        </Link>

        <nav aria-label="Primary" className="hidden items-center gap-6 md:flex">
          {primaryNavLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-metadata text-foreground/80 transition-colors hover:text-accent"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            href="/search"
            aria-label="Search"
            className="hidden size-9 items-center justify-center rounded-full border border-border text-foreground transition-colors hover:border-border-strong hover:bg-background-elevated md:flex"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              className="size-4"
            >
              <circle cx="10.5" cy="10.5" r="6.5" />
              <path strokeLinecap="round" d="m20 20-4.5-4.5" />
            </svg>
          </Link>

          <Link
            href="/saved"
            aria-label="Saved stories and settings"
            className="hidden size-9 items-center justify-center rounded-full border border-border text-foreground transition-colors hover:border-border-strong hover:bg-background-elevated md:flex"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              className="size-4"
            >
              <circle cx="12" cy="8" r="3.4" />
              <path strokeLinecap="round" d="M5 20c0-3.6 3.1-6 7-6s7 2.4 7 6" />
            </svg>
          </Link>

          <ThemeToggle />
          <MobileNavigation />
        </div>
      </div>
    </header>
  );
}
