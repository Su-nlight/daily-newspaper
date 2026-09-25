import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { PreferencesEditor } from "@/components/personalization/PreferencesEditor";
import {
  getContentTypes,
  getRegions,
  getSources,
  getTopics,
  getUserPreferences,
} from "@/lib/api/client";

export default async function TopicsPage() {
  const [topics, regions, sources, contentTypes, preferences] = await Promise.all([
    getTopics(),
    getRegions(),
    getSources(),
    getContentTypes(),
    getUserPreferences(),
  ]);

  return (
    <PageContainer narrow>
      <SectionHeading
        eyebrow="Personalization"
        title="Your Interests"
        description="Tell Daily Signal what to prioritize. These preferences drive Relevant to You on the homepage and other personalized sections across the site."
      />
      <PreferencesEditor
        topics={topics}
        regions={regions}
        sources={sources}
        contentTypes={contentTypes}
        initialPreferences={preferences}
      />
    </PageContainer>
  );
}
