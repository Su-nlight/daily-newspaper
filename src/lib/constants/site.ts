export const siteConfig = {
  name: "Daily Signal",
  tagline: "Personal Daily Intelligence",
  description: "Personalized digital newspaper for technology and world intelligence.",
  routes: [
    "/",
    "/story/[id]",
    "/category/[slug]",
    "/search",
    "/saved",
    "/topics",
    "/archive",
    "/research",
    "/career",
    "/chat",
    "/about",
  ] as const,
};

export interface NavLink {
  label: string;
  href: string;
}

export const primaryNavLinks: NavLink[] = [
  { label: "Today's Edition", href: "/" },
  { label: "Topics", href: "/topics" },
  { label: "Research", href: "/research" },
  { label: "Career", href: "/career" },
  { label: "Archive", href: "/archive" },
];

export const footerLinks: NavLink[] = [
  { label: "About", href: "/about" },
  { label: "Methodology", href: "/about" },
  { label: "Sources", href: "/about" },
  { label: "Privacy", href: "/about" },
  { label: "Terms", href: "/about" },
];
