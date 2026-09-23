import { StoryImagePlaceholder } from "@/components/story/StoryImagePlaceholder";
import { formatCategoryLabel } from "@/lib/utils/category";
import type { Article } from "@/types";

interface StoryHeroProps {
  story: Article;
}

export function StoryHero({ story }: StoryHeroProps) {
  return (
    <div className="space-y-2">
      <StoryImagePlaceholder category={formatCategoryLabel(story.category)} size="standard" />
      <p className="text-caption">Illustrative visual for {story.title}</p>
    </div>
  );
}
