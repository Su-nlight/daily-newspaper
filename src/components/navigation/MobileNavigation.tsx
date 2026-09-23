"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { primaryNavLinks } from "@/lib/constants/site";

export function MobileNavigation() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  return (
    <div className="md:hidden">
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        aria-label="Open navigation menu"
        aria-expanded={isOpen}
        className="flex size-9 items-center justify-center rounded-full border border-border text-foreground"
      >
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="size-4">
          <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {isOpen ? (
        <div className="fixed inset-0 z-50 flex">
          <button
            type="button"
            aria-label="Close navigation menu"
            onClick={() => setIsOpen(false)}
            className="absolute inset-0 bg-foreground/30 backdrop-blur-[1px]"
          />
          <nav className="relative ml-auto flex h-full w-full max-w-xs flex-col gap-1 border-l border-border bg-background px-6 py-6">
            <div className="mb-6 flex items-center justify-between">
              <span className="text-headline text-lg">Daily Signal</span>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                aria-label="Close navigation menu"
                className="flex size-9 items-center justify-center rounded-full border border-border"
              >
                <svg
                  aria-hidden="true"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  className="size-4"
                >
                  <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </div>
            {primaryNavLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className="text-body border-b border-border py-3 text-foreground"
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/search"
              onClick={() => setIsOpen(false)}
              className="text-body border-b border-border py-3 text-foreground"
            >
              Search
            </Link>
            <Link
              href="/saved"
              onClick={() => setIsOpen(false)}
              className="text-body py-3 text-foreground"
            >
              Saved Stories
            </Link>
          </nav>
        </div>
      ) : null}
    </div>
  );
}
