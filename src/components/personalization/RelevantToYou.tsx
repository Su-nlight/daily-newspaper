import Link from "next/link";

import { SectionHeading } from "@/components/layout/SectionHeading";
import { WhyRelevant } from "@/components/personalization/WhyRelevant";
import type { PersonalizedStory } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";

interface RelevantToYouProps {
  stories: PersonalizedStory[];
}

export function RelevantToYou({ stories }: RelevantToYouProps) {
  if (stories.length === 0) return null;

  return (
    <section className="flex flex-col gap-6 border-t border-border pt-8">
      <SectionHeading
        eyebrow="For you"
        title="Relevant to You"
        description="Stories prioritized from the interests and sources you've set on the Topics page — not AI-generated yet."
      />

      <div className="grid gap-6 sm:grid-cols-2">
        {stories.map(({ article, reasons }) => (
          <article key={article.id} className="flex flex-col gap-2 border-l-2 border-accent/40 pl-4">
            <p className="text-metadata text-accent">{formatCategoryLabel(article.category)}</p>
            <h3 className="text-subheadline">
              <Link href={`/story/${article.id}`} className="hover:underline">
                {article.title}
              </Link>
            </h3>
            <p className="text-body text-muted">{article.summary}</p>
            <WhyRelevant reasons={reasons} />
          </article>
        ))}
      </div>
    </section>
  );
}
