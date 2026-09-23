import type { Metadata } from "next";
import Script from "next/script";

import { ChatBubble } from "@/components/chat/ChatBubble";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { ChatUiProvider } from "@/hooks/useChatUiState";
import { siteConfig } from "@/lib/constants/site";

import "./globals.css";

export const metadata: Metadata = {
  title: siteConfig.name,
  description: siteConfig.description,
};

// Runs before hydration to apply a stored theme preference (or the system
// preference) without a flash of the wrong theme. Kept minimal on purpose —
// see components/navigation/ThemeToggle.tsx for the interactive counterpart.
const themeInitScript = `
(function () {
  try {
    var stored = window.localStorage.getItem("theme");
    var theme = stored === "light" || stored === "dark" ? stored : null;
    if (theme) {
      document.documentElement.classList.toggle("dark", theme === "dark");
      document.documentElement.setAttribute("data-theme", theme);
    }
  } catch (e) {}
})();
`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased" suppressHydrationWarning>
      <head>
        <Script id="theme-init" strategy="beforeInteractive">
          {themeInitScript}
        </Script>
      </head>
      <body className="flex min-h-full flex-col bg-background text-foreground">
        <ChatUiProvider>
          <Header />
          <div className="flex-1">{children}</div>
          <Footer />
          <ChatBubble />
        </ChatUiProvider>
      </body>
    </html>
  );
}
