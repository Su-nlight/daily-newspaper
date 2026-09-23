import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { getSavedStories } from "@/lib/api/client";

export default async function SavedPage() {
  const savedStories = await getSavedStories();

  return (
    <PageContainer>
      <SectionHeading
        eyebrow="Library"
        title="Saved Stories"
        description="Placeholder route for saved stories management."
      />
      <p className="text-caption">Mock saved stories: {savedStories.length}</p>
    </PageContainer>
  );
}
