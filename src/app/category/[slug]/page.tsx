import { notFound } from "next/navigation";

import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { HeroStory } from "@/components/newspaper/HeroStory";
import { NewspaperSection } from "@/components/newspaper/NewspaperSection";
import { TrendingTopics } from "@/components/newspaper/TrendingTopics";
import { getCategoryFeed } from "@/lib/api/client";

export default async function CategoryPage({ params }: PageProps<"/category/[slug]">) {
  const { slug } = await params;
  const feed = await getCategoryFeed(slug);

  if (!feed.category) {
    notFound();
  }

  return (
    <PageContainer>
      <SectionHeading eyebrow="Category" title={feed.category.name} description={feed.category.description} />

      {feed.featuredStory ? (
        <HeroStory story={feed.featuredStory} />
      ) : (
        <p className="text-body border-t border-border pt-8 text-muted">
          No stories in this category yet.
        </p>
      )}

      <NewspaperSection
        title="More in this category"
        stories={feed.secondaryStories}
        layout="grid"
        columns={2}
      />

      <NewspaperSection title="Latest" stories={feed.latestStories} layout="list" />

      <TrendingTopics topics={feed.trendingTopics} />
    </PageContainer>
  );
}
