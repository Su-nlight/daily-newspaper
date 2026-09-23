import { CompactStory } from "@/components/story/CompactStory";
import { HorizontalStory } from "@/components/story/HorizontalStory";
import { StandardStory } from "@/components/story/StandardStory";
import type { Article } from "@/types";

interface SecondaryStoriesProps {
  stories: Article[];
}

/**
 * Deliberately mixes StandardStory / CompactStory / HorizontalStory so the
 * stories immediately under the lead read as an editorial hierarchy rather
 * than a repeated card grid.
 */
export function SecondaryStories({ stories }: SecondaryStoriesProps) {
  if (stories.length === 0) return null;

  const [lead, ...rest] = stories;
  const compact = rest.slice(0, 2);
  const horizontal = rest.slice(2);

  return (
    <section className="grid gap-8 border-t border-border pt-8 lg:grid-cols-[1.3fr_1fr]">
      <StandardStory story={lead} emphasized />

      <div className="flex flex-col divide-y divide-border lg:border-l lg:border-border lg:pl-8">
        {compact.map((story) => (
          <CompactStory key={story.id} story={story} />
        ))}
      </div>

      {horizontal.length > 0 ? (
        <div className="flex flex-col divide-y divide-border lg:col-span-2">
          {horizontal.map((story) => (
            <HorizontalStory key={story.id} story={story} />
          ))}
        </div>
      ) : null}
    </section>
  );
}
