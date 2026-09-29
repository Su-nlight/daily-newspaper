import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { ArchiveTimeline } from "@/components/newspaper/ArchiveTimeline";
import { getArchive } from "@/lib/api/client";

export default async function ArchivePage() {
  const months = await getArchive();

  return (
    <PageContainer narrow>
      <SectionHeading
        eyebrow="History"
        title="Archive"
        description="Browse past editions of Daily Signal by date."
      />
      <ArchiveTimeline months={months} />
    </PageContainer>
  );
}
