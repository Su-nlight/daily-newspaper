export const siteConfig = {
  name: "Daily Signal",
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
