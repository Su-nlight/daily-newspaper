import { FullChat } from "@/components/chat/FullChat";
import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";

export default function ChatPage() {
  return (
    <PageContainer>
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        <SectionHeading
          eyebrow="Assistant"
          title="AI Assistant"
          description="Ask about stories, topics, and research. Answers are grounded in Daily Signal coverage and cite their sources. Your conversation continues from the chat bubble and back."
        />
        <FullChat />
      </div>
    </PageContainer>
  );
}
