import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";

export default function AboutPage() {
  return (
    <PageContainer narrow>
      <SectionHeading eyebrow="Daily Signal" title="About Daily Signal" />
      <p className="text-body text-muted">
        Daily Signal is a personalized digital newspaper focused on actionable intelligence across
        technology, research, careers, and global developments.
      </p>
    </PageContainer>
  );
}
