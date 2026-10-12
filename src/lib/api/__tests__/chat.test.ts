import { afterEach, describe, expect, it, vi } from "vitest";

import { ChatRequestError, parseSseBuffer, streamChatMessage, toRequestContext } from "../chat";

function sseResponse(chunks: string[], status = 200): Response {
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
  return new Response(body, { status, headers: { "Content-Type": "text/event-stream" } });
}

afterEach(() => vi.restoreAllMocks());

describe("parseSseBuffer", () => {
  it("parses complete events and keeps the partial remainder", () => {
    const { events, rest } = parseSseBuffer(
      'data: {"type":"token","content":"Hi"}\n\ndata: {"type":"token","content":" th',
    );
    expect(events).toEqual([{ type: "token", content: "Hi" }]);
    expect(rest).toBe('data: {"type":"token","content":" th');
  });

  it("handles CRLF line endings and skips malformed events", () => {
    const { events } = parseSseBuffer('data: not json\r\n\r\ndata: {"type":"done"}\r\n\r\n');
    expect(events).toEqual([{ type: "done" }]);
  });
});

describe("toRequestContext", () => {
  it("maps each page context kind onto the backend's context object", () => {
    expect(toRequestContext(null)).toEqual({});
    expect(toRequestContext({ kind: "story", label: "x", storyId: "s1" })).toEqual({
      story_id: "s1",
    });
    expect(toRequestContext({ kind: "edition", label: "x", editionId: "e1" })).toEqual({
      edition_id: "e1",
    });
    expect(toRequestContext({ kind: "category", label: "x", category: "ai" })).toEqual({
      category: "ai",
    });
    expect(
      toRequestContext({ kind: "search", label: "x", searchQuery: "rag", resultIds: ["a", "b"] }),
    ).toEqual({ search_query: "rag", search_result_ids: ["a", "b"] });
  });
});

describe("streamChatMessage", () => {
  const base = {
    message: "hello",
    conversationId: "c1",
    context: null,
    history: [],
  };

  it("streams tokens split across chunk boundaries, then resolves with sources", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      sseResponse([
        'data: {"type":"token","content":"Hel',
        'lo"}\n\ndata: {"type":"token","content":" world"}\n\n',
        'data: {"type":"done","sources":[{"publisher":"P","url":"https://p.example/a","index":1}]}\n\n',
      ]),
    );

    const tokens: string[] = [];
    const result = await streamChatMessage({ ...base, onToken: (t) => tokens.push(t) });

    expect(tokens.join("")).toBe("Hello world");
    expect(result.sources).toEqual([{ publisher: "P", url: "https://p.example/a", index: 1 }]);
  });

  it("sends the message, conversation id, context and history to the backend", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(sseResponse(['data: {"type":"done","sources":[]}\n\n']));

    await streamChatMessage({
      message: "why?",
      conversationId: "conv-1",
      context: { kind: "story", label: "T", storyId: "story-1" },
      history: [{ role: "user", content: "hi" }],
      onToken: () => {},
    });

    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toMatch(/\/api\/chat\/stream$/);
    expect(JSON.parse(String((init as RequestInit).body))).toEqual({
      message: "why?",
      conversation_id: "conv-1",
      context: { story_id: "story-1" },
      history: [{ role: "user", content: "hi" }],
    });
  });

  it("rejects with ChatRequestError when the server reports a stream error", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      sseResponse(['data: {"type":"error","message":"Groq rate limit exceeded."}\n\n']),
    );
    await expect(streamChatMessage({ ...base, onToken: () => {} })).rejects.toThrow(
      "Groq rate limit exceeded.",
    );
  });

  it("rejects when the server can't be reached or returns an HTTP error", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new TypeError("Failed to fetch"));
    await expect(streamChatMessage({ ...base, onToken: () => {} })).rejects.toBeInstanceOf(
      ChatRequestError,
    );

    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response("nope", { status: 500 }));
    await expect(streamChatMessage({ ...base, onToken: () => {} })).rejects.toThrow("(500)");
  });

  it("rejects when the stream ends without a done event", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      sseResponse(['data: {"type":"token","content":"partial"}\n\n']),
    );
    await expect(streamChatMessage({ ...base, onToken: () => {} })).rejects.toThrow(
      "ended unexpectedly",
    );
  });
});
