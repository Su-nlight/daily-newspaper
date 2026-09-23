import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { searchStories } from "@/lib/api/client";

export default async function SearchPage() {
  const stories = await searchStories("AI");

  return (
    <PageContainer>
      <SectionHeading
        eyebrow="Search"
        title="Search Daily Signal"
        description="Placeholder route. Search UI and backend query integration will be added in later modules."
      />
      <p className="text-caption">Mock result count: {stories.length}</p>
    </PageContainer>
  );
}
