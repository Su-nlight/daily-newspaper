import { notFound } from "next/navigation";

import { PageContainer } from "@/components/layout/PageContainer";
import { ArticleCompletionTracker } from "@/components/story/ArticleCompletionTracker";
import { ArticleViewTracker } from "@/components/story/ArticleViewTracker";
import { AskAboutStory } from "@/components/story/AskAboutStory";
import { KeyFacts } from "@/components/story/KeyFacts";
import { RelatedStories } from "@/components/story/RelatedStories";
import { SaveStoryButton } from "@/components/story/SaveStoryButton";
import { ShareStoryButton } from "@/components/story/ShareStoryButton";
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
      <ArticleViewTracker storyId={story.id} title={story.title} category={story.category} />

      <StoryHeader story={story} />

      <div className="flex gap-3">
        <SaveStoryButton storyId={story.id} title={story.title} />
        <ShareStoryButton storyId={story.id} title={story.title} />
      </div>

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

      <ArticleCompletionTracker storyId={story.id} title={story.title} />

      <RelatedStories stories={relatedStories} />
      <AskAboutStory story={story} />
    </PageContainer>
  );
}
