import Link from "next/link";

import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { getCategory } from "@/lib/api/client";
import { formatDisplayDate } from "@/lib/utils/date";

export default async function CategoryPage({ params }: PageProps<"/category/[slug]">) {
  const { slug } = await params;
  const { category, stories } = await getCategory(slug);

  return (
    <PageContainer>
      <SectionHeading
        eyebrow="Category"
        title={category?.name ?? "Category"}
        description={category?.description ?? "Category placeholder route for upcoming modules."}
      />

      <ul className="divide-y divide-border">
        {stories.map((story) => (
          <li key={story.id} className="flex flex-col gap-1 py-4">
            <h2 className="text-subheadline">
              <Link href={`/story/${story.id}`} className="hover:underline">
                {story.title}
              </Link>
            </h2>
            <p className="text-body text-muted">{story.summary}</p>
            <p className="text-caption">
              {story.source} · {formatDisplayDate(story.publishedAt)}
            </p>
          </li>
        ))}
      </ul>
    </PageContainer>
  );
}
