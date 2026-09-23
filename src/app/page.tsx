import { EditionMeta } from "@/components/newspaper/EditionMeta";
import { EmptyEditionState } from "@/components/newspaper/EmptyEditionState";
import { HeroStory } from "@/components/newspaper/HeroStory";
import { Masthead } from "@/components/newspaper/Masthead";
import { NewspaperSection } from "@/components/newspaper/NewspaperSection";
import { SecondaryStories } from "@/components/newspaper/SecondaryStories";
import { SixtySecondBrief } from "@/components/newspaper/SixtySecondBrief";
import { PageContainer } from "@/components/layout/PageContainer";
import { RelevantToYou } from "@/components/personalization/RelevantToYou";
import { getHomepageFeed } from "@/lib/api/client";

const SECTION_LAYOUTS = {
  world: "list",
  technology: "grid",
  "ai-research": "grid",
  cybersecurity: "list",
} as const;

export default async function Home() {
  const feed = await getHomepageFeed();

  if (!feed.heroStory) {
    return (
      <PageContainer>
        <Masthead date={feed.edition.date} />
        <EmptyEditionState />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <Masthead date={feed.edition.date} />
      <EditionMeta edition={feed.edition} />
      <HeroStory story={feed.heroStory} />
      <SecondaryStories stories={feed.secondaryStories} />

      {feed.sections.map((section) => (
        <NewspaperSection
          key={section.slug}
          title={section.title}
          description={section.description}
          stories={section.stories}
          href={section.href}
          layout={SECTION_LAYOUTS[section.slug as keyof typeof SECTION_LAYOUTS] ?? "grid"}
        />
      ))}

      <RelevantToYou stories={feed.personalized} />
      <SixtySecondBrief items={feed.brief} />
    </PageContainer>
  );
}
