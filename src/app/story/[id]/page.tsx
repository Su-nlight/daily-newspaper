import { notFound } from "next/navigation";

import { PageContainer } from "@/components/layout/PageContainer";
import { AskAboutStory } from "@/components/story/AskAboutStory";
import { KeyFacts } from "@/components/story/KeyFacts";
import { RelatedStories } from "@/components/story/RelatedStories";
import { SourceList } from "@/components/story/SourceList";
import { StoryHeader } from "@/components/story/StoryHeader";
import { StoryHero } from "@/components/story/StoryHero";
import { StorySection } from "@/components/story/StorySection";
import { StorySummary } from "@/components/story/StorySummary";
import { getRelatedStories, getStory } from "@/lib/api/client";

export default async function StoryPage({ params }: PageProps<"/story/[id]">) {
  const { id } = await params;
  const story = await getStory(id);

  if (!story) {
    notFound();
  }

  const relatedStories = await getRelatedStories(story, 3);

  return (
    <PageContainer narrow>
      <StoryHeader story={story} />
      <StoryHero story={story} />
      <StorySummary text={story.summary} />
      <StorySection title="What Happened">
        <p>{story.whatHappened}</p>
      </StorySection>
      <StorySection title="Why It Matters">
        <p>{story.whyItMatters}</p>
      </StorySection>
      <KeyFacts facts={story.keyFacts} />
      <SourceList citations={story.citations} />
      <RelatedStories stories={relatedStories} />
      <AskAboutStory story={story} />
    </PageContainer>
  );
}
