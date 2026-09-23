import { StandardStory } from "@/components/story/StandardStory";
import type { Article } from "@/types";

interface RelatedStoriesProps {
  stories: Article[];
}

export function RelatedStories({ stories }: RelatedStoriesProps) {
  if (stories.length === 0) return null;

  return (
    <section className="border-t border-border pt-6">
      <h2 className="text-section-title mb-4 text-accent">Related Stories</h2>
      <div className="grid gap-8 sm:grid-cols-2">
        {stories.map((story) => (
          <StandardStory key={story.id} story={story} />
        ))}
      </div>
    </section>
  );
}
