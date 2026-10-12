import type { ChatPageContext, ChatSource } from "@/types";

/**
 * The only place the browser talks to the FastAPI chat backend (Module 07).
 * The Groq key never reaches the browser — it lives only in backend/.env.
 */
export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

export class ChatRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ChatRequestError";
  }
}

export interface ChatHistoryTurn {
  role: "user" | "assistant";
  content: string;
}

export interface StreamChatParams {
  message: string;
  conversationId: string;
  context: ChatPageContext | null;
  history: ChatHistoryTurn[];
  signal?: AbortSignal;
  onToken: (text: string) => void;
}

export interface StreamChatResult {
  sources: ChatSource[];
}

type ServerEvent =
  | { type: "token"; content: string }
  | { type: "done"; sources?: ChatSource[]; conversation_id?: string }
  | { type: "error"; message?: string };

/** Maps the page context the UI tracks onto the backend's `context` object. */
export function toRequestContext(context: ChatPageContext | null): Record<string, unknown> {
  if (!context) return {};
  switch (context.kind) {
    case "story":
      return { story_id: context.storyId };
    case "edition":
      return { edition_id: context.editionId };
    case "category":
      return { category: context.category };
    case "search":
      return { search_query: context.searchQuery, search_result_ids: context.resultIds ?? [] };
  }
}

/**
 * Splits a buffer of Server-Sent Events into complete events plus whatever
 * trailing partial event is still waiting for more bytes.
 */
export function parseSseBuffer(buffer: string): { events: ServerEvent[]; rest: string } {
  const normalized = buffer.replace(/\r\n/g, "\n");
  const blocks = normalized.split("\n\n");
  const rest = blocks.pop() ?? "";

  const events: ServerEvent[] = [];
  for (const block of blocks) {
    const data = block
      .split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trimStart())
      .join("\n");
    if (!data) continue;
    try {
      events.push(JSON.parse(data) as ServerEvent);
    } catch {
      // Ignore a malformed event rather than failing the whole answer.
    }
  }
  return { events, rest };
}

/**
 * Sends a chat message to POST /api/chat/stream and calls `onToken` for each
 * text chunk as it arrives. Resolves with the cited sources once the stream
 * finishes; rejects with ChatRequestError for any network, HTTP, or
 * server-reported failure.
 */
export async function streamChatMessage(params: StreamChatParams): Promise<StreamChatResult> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({
        message: params.message,
        conversation_id: params.conversationId,
        context: toRequestContext(params.context),
        history: params.history,
      }),
      signal: params.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ChatRequestError("Couldn't reach the Daily Signal server.");
  }

  if (!response.ok || !response.body) {
    throw new ChatRequestError(`The server responded with an error (${response.status}).`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value, { stream: !done });

    const { events, rest } = parseSseBuffer(done ? `${buffer}\n\n` : buffer);
    buffer = rest;

    for (const event of events) {
      if (event.type === "token") {
        params.onToken(event.content);
      } else if (event.type === "error") {
        throw new ChatRequestError(event.message || "The AI service reported an error.");
      } else if (event.type === "done") {
        return { sources: event.sources ?? [] };
      }
    }

    if (done) break;
  }

  throw new ChatRequestError("The response ended unexpectedly.");
}
