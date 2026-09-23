import { StoryImagePlaceholder } from "@/components/story/StoryImagePlaceholder";
import type { StoryDetail } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";

interface StoryHeroProps {
  story: StoryDetail;
}

export function StoryHero({ story }: StoryHeroProps) {
  return (
    <div className="flex flex-col gap-2">
      <StoryImagePlaceholder category={formatCategoryLabel(story.category)} size="hero" />
      <p className="text-caption italic">Photography for this story is not yet available.</p>
    </div>
  );
}
