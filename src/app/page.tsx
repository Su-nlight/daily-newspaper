import Link from "next/link";

import { Masthead } from "@/components/newspaper/Masthead";
import { PageContainer } from "@/components/layout/PageContainer";
import { getTodayEdition } from "@/lib/api/client";
import { siteConfig } from "@/lib/constants/site";
import { formatDisplayDate } from "@/lib/utils/date";

export default async function Home() {
  const edition = await getTodayEdition();

  return (
    <PageContainer>
      <Masthead date={edition.date} />

      <section className="space-y-2">
        <h2 className="text-subheadline">{edition.headline}</h2>
        <p className="text-body max-w-3xl text-muted">{edition.summary}</p>
      </section>

      <section className="grid gap-6 sm:grid-cols-2">
        {edition.stories.map((story) => (
          <article key={story.id} className="flex flex-col gap-2 border-t border-border pt-4">
            <p className="text-metadata text-accent">{story.category}</p>
            <h3 className="text-subheadline">
              <Link href={`/story/${story.id}`} className="hover:underline">
                {story.title}
              </Link>
            </h3>
            <p className="text-body text-muted">{story.summary}</p>
            <p className="text-caption">
              {story.source} · {formatDisplayDate(story.publishedAt)}
            </p>
          </article>
        ))}
      </section>

      <section className="space-y-3 border-t border-border pt-6">
        <p className="text-section-title">Route foundation</p>
        <ul className="grid gap-2 sm:grid-cols-2">
          {siteConfig.routes.map((route) => (
            <li key={route} className="text-caption rounded border border-border px-3 py-2">
              {route}
            </li>
          ))}
        </ul>
      </section>
    </PageContainer>
  );
}
