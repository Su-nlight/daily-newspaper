import { sendChatMessage } from "@/lib/api/client";

export default async function ChatPage() {
  const conversation = await sendChatMessage("What changed today in AI policy?");

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold tracking-tight">AI Assistant</h1>
      <p className="text-zinc-700 dark:text-zinc-300">
        Placeholder route for conversational assistant. Backend integration will be added in later modules.
      </p>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">
        Mock conversation messages: {conversation.messages.length}
      </p>
    </main>
  );
}
