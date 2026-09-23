import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { getTopics } from "@/lib/api/client";

export default async function TopicsPage() {
  const topics = await getTopics();

  return (
    <PageContainer>
      <SectionHeading eyebrow="Discover" title="Topics" description="Placeholder topic discovery route." />
      <ul className="grid gap-3 sm:grid-cols-2">
        {topics.map((topic) => (
          <li key={topic.id} className="border-t border-border pt-3">
            <p className="text-subheadline">{topic.name}</p>
            <p className="text-caption">{topic.description}</p>
          </li>
        ))}
      </ul>
    </PageContainer>
  );
}
