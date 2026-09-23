import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { sendChatMessage } from "@/lib/api/client";

export default async function ChatPage() {
  const conversation = await sendChatMessage("What changed today in AI policy?");

  return (
    <PageContainer narrow>
      <SectionHeading
        eyebrow="Assistant"
        title="AI Assistant"
        description="Placeholder route for the conversational assistant. Backend integration will be added in later modules. The persistent chat bubble in the bottom-left corner is available on every page in the meantime."
      />
      <p className="text-caption">Mock conversation messages: {conversation.messages.length}</p>
    </PageContainer>
  );
}
