import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi, type MockInstance } from "vitest";

import { ChatBubble } from "@/components/chat/ChatBubble";
import { ChatPageContextSetter } from "@/components/chat/ChatPageContextSetter";
import { ChatProvider, useChat } from "@/components/chat/ChatProvider";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { FullChat } from "@/components/chat/FullChat";

const nav = vi.hoisted(() => ({ pathname: "/" }));

vi.mock("next/navigation", () => ({ usePathname: () => nav.pathname }));
vi.mock("next/link", () => ({
  default: ({ href, children, onClick }: { href: string; children: ReactNode; onClick?: () => void }) => (
    <a
      href={href}
      onClick={(event) => {
        event.preventDefault(); // jsdom can't navigate; the test changes nav.pathname itself
        onClick?.();
      }}
    >
      {children}
    </a>
  ),
}));

type ServerEvent = Record<string, unknown>;

function sseResponse(events: ServerEvent[]): Response {
  const body = events.map((e) => `data: ${JSON.stringify(e)}\n\n`).join("");
  return new Response(body, { status: 200, headers: { "Content-Type": "text/event-stream" } });
}

function answer(text: string, sources: ServerEvent[] = []): ServerEvent[] {
  return [
    { type: "token", content: text },
    { type: "done", sources, conversation_id: "c" },
  ];
}

function requestBody(fetchMock: MockInstance<typeof fetch>, call: number) {
  const init = fetchMock.mock.calls[call][1] as RequestInit;
  return JSON.parse(String(init.body));
}

const INPUT = "Message Daily Signal AI";

let fetchMock: MockInstance<typeof fetch>;

beforeEach(() => {
  nav.pathname = "/";
  fetchMock = vi.spyOn(globalThis, "fetch");
});

afterEach(() => vi.restoreAllMocks());

describe("sending and rendering answers", () => {
  it("streams an answer with markdown, citations and sources", async () => {
    fetchMock.mockImplementation(async () =>
      sseResponse(
        answer("India proposes **quarterly audits** [1].\n\n- lending\n- healthcare\n\n`code`", [
          { publisher: "Tech Ledger", url: "https://t.example/a", title: "AI audits", index: 1 },
        ]),
      ),
    );
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatWindow variant="full" />
      </ChatProvider>,
    );

    await user.type(screen.getByLabelText(INPUT), "What changed?{Enter}");

    expect((await screen.findByText("quarterly audits")).tagName).toBe("STRONG");
    expect(screen.getAllByRole("listitem").map((li) => li.textContent)).toContain("lending");

    const source = screen.getByRole("link", { name: /Tech Ledger — AI audits/ });
    expect(source.getAttribute("href")).toBe("https://t.example/a");
    expect(source.getAttribute("target")).toBe("_blank");

    const citation = screen.getByRole("link", { name: "Source 1" });
    const anchorId = citation.getAttribute("href")!.slice(1);
    expect(document.getElementById(anchorId)).toBeTruthy();
  });

  it("renders links safely and never raw HTML", async () => {
    fetchMock.mockImplementation(async () =>
      sseResponse(
        answer("See [the docs](https://docs.example/x) <b>bold</b><script>alert(1)</script>"),
      ),
    );
    const user = userEvent.setup();
    const { container } = render(
      <ChatProvider>
        <ChatWindow variant="full" />
      </ChatProvider>,
    );

    await user.type(screen.getByLabelText(INPUT), "hi{Enter}");

    const link = await screen.findByRole("link", { name: "the docs" });
    expect(link.getAttribute("rel")).toBe("noopener noreferrer");
    expect(link.getAttribute("target")).toBe("_blank");
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("b")).toBeNull();
  });

  it("renders fenced code blocks", async () => {
    fetchMock.mockImplementation(async () =>
      sseResponse(answer("Try:\n\n```python\nprint('hi')\n```")),
    );
    const user = userEvent.setup();
    const { container } = render(
      <ChatProvider>
        <ChatWindow variant="full" />
      </ChatProvider>,
    );

    await user.type(screen.getByLabelText(INPUT), "code{Enter}");

    await waitFor(() => expect(container.querySelector("pre code")).toBeTruthy());
    expect(container.querySelector("pre code")!.textContent).toContain("print('hi')");
  });

  it("sends on Enter, inserts a newline on Shift+Enter, and ignores empty input", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("ok")));
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatWindow variant="full" />
      </ChatProvider>,
    );
    const input = screen.getByLabelText(INPUT) as HTMLTextAreaElement;

    await user.type(input, "{Enter}");
    expect(fetchMock).not.toHaveBeenCalled();

    await user.type(input, "line one{Shift>}{Enter}{/Shift}line two");
    expect(input.value).toBe("line one\nline two");
    expect(fetchMock).not.toHaveBeenCalled();

    await user.keyboard("{Enter}");
    await screen.findByText("ok");
    expect(requestBody(fetchMock, 0).message).toBe("line one\nline two");
    expect(input.value).toBe("");
  });

  it("aligns user messages right and AI messages left", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("hello back")));
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatWindow variant="full" />
      </ChatProvider>,
    );
    await user.type(screen.getByLabelText(INPUT), "hello{Enter}");
    await screen.findByText("hello back");

    expect(screen.getByText("hello").closest("div")!.className).toContain("justify-end");
    expect(screen.getByText("hello back").closest("div.flex")!.className).toContain("justify-start");
  });

  it("shows a thinking state while streaming, then announces completion", async () => {
    let release!: (events: ServerEvent[]) => void;
    fetchMock.mockImplementation(
      () => new Promise<Response>((resolve) => (release = (e) => resolve(sseResponse(e)))),
    );
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatWindow variant="full" />
      </ChatProvider>,
    );

    await user.type(screen.getByLabelText(INPUT), "slow{Enter}");

    const log = screen.getByRole("log", { name: "Conversation" });
    await waitFor(() => expect(log.getAttribute("aria-busy")).toBe("true"));
    expect(screen.getByRole("status").textContent).toBe("Daily Signal AI is thinking.");

    release(answer("done now"));
    await screen.findByText("done now");
    await waitFor(() => expect(log.getAttribute("aria-busy")).toBe("false"));
    expect(screen.getByRole("status").textContent).toBe("Response complete.");
  });
});

describe("context awareness", () => {
  it("uses the current story as context and keeps conversation history", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("Because retrieval fails.")));
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatPageContextSetter
          context={{ kind: "story", label: "New RAG benchmark", storyId: "story-rag-benchmark" }}
        />
        <ChatWindow variant="compact" />
      </ChatProvider>,
    );

    expect(await screen.findByText("New RAG benchmark")).toBeTruthy();
    // Story pages offer story-shaped suggestions.
    await user.click(screen.getByRole("button", { name: "Why does this matter?" }));
    await screen.findByText("Because retrieval fails.");

    expect(requestBody(fetchMock, 0)).toMatchObject({
      message: "Why does this matter?",
      context: { story_id: "story-rag-benchmark" },
      history: [],
    });

    await user.type(screen.getByLabelText(INPUT), "How could this affect my research?{Enter}");
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));

    const second = requestBody(fetchMock, 1);
    expect(second.context).toEqual({ story_id: "story-rag-benchmark" });
    expect(second.history).toEqual([
      { role: "user", content: "Why does this matter?" },
      { role: "assistant", content: "Because retrieval fails." },
    ]);
    expect(second.conversation_id).toBe(requestBody(fetchMock, 0).conversation_id);
  });

  it("sends edition, category and search-result context for those pages", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("ok")));
    const user = userEvent.setup();

    const cases: { context: Parameters<typeof ChatPageContextSetter>[0]["context"]; expected: object }[] = [
      {
        context: { kind: "edition", label: "Today's edition", editionId: "edition-2026-09-22" },
        expected: { edition_id: "edition-2026-09-22" },
      },
      {
        context: { kind: "category", label: "AI category", category: "ai" },
        expected: { category: "ai" },
      },
      {
        context: {
          kind: "search",
          label: "Search results for “rag”",
          searchQuery: "rag",
          resultIds: ["a", "b"],
        },
        expected: { search_query: "rag", search_result_ids: ["a", "b"] },
      },
    ];

    for (const [index, { context, expected }] of cases.entries()) {
      const { unmount } = render(
        <ChatProvider>
          <ChatPageContextSetter context={context} />
          <ChatWindow variant="compact" />
        </ChatProvider>,
      );
      await user.type(screen.getByLabelText(INPUT), "hello{Enter}");
      await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(index + 1));
      expect(requestBody(fetchMock, index).context).toEqual(expected);
      unmount();
    }
  });

  it("pins a story from 'Ask AI' and lets the user clear it", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("ok")));
    const user = userEvent.setup();

    function Opener() {
      const { openChat } = useChat();
      return (
        <button
          onClick={() => openChat({ storyId: "story-ransomware-shift", title: "Ransomware shift", context: "x" })}
        >
          pin
        </button>
      );
    }

    render(
      <ChatProvider>
        <Opener />
        <ChatWindow variant="compact" />
      </ChatProvider>,
    );

    await user.click(screen.getByRole("button", { name: "pin" }));
    expect(await screen.findByText("Ransomware shift")).toBeTruthy();

    await user.type(screen.getByLabelText(INPUT), "tell me more{Enter}");
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(requestBody(fetchMock, 0).context).toEqual({ story_id: "story-ransomware-shift" });

    await user.click(screen.getByRole("button", { name: "Clear" }));
    // The context bar is gone (the earlier "Now discussing: …" divider stays).
    expect(screen.queryByText(/^Discussing:/)).toBeNull();
  });

  it("marks where the conversation's context changed", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("ok")));
    const user = userEvent.setup();

    function Switcher() {
      const { openChat } = useChat();
      return (
        <button onClick={() => openChat({ storyId: "s2", title: "Second story", context: "x" })}>
          switch
        </button>
      );
    }

    render(
      <ChatProvider>
        <ChatPageContextSetter context={{ kind: "story", label: "First story", storyId: "s1" }} />
        <Switcher />
        <ChatWindow variant="compact" />
      </ChatProvider>,
    );

    await user.type(screen.getByLabelText(INPUT), "one{Enter}");
    await waitFor(() => expect(screen.getAllByText("ok")).toHaveLength(1));
    await user.click(screen.getByRole("button", { name: "switch" }));
    await user.type(screen.getByLabelText(INPUT), "two{Enter}");
    await waitFor(() => expect(screen.getAllByText("ok")).toHaveLength(2));

    expect(screen.getByText("Now discussing: First story")).toBeTruthy();
    expect(screen.getByText("Now discussing: Second story")).toBeTruthy();
  });
});

describe("errors", () => {
  it("shows 'Something went wrong. Try again.' with a working retry", async () => {
    fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch"));
    fetchMock.mockImplementation(async () => sseResponse(answer("Recovered answer")));
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatPageContextSetter context={{ kind: "story", label: "S", storyId: "s1" }} />
        <ChatWindow variant="compact" />
      </ChatProvider>,
    );

    await user.type(screen.getByLabelText(INPUT), "will fail{Enter}");

    // (The message is also announced via the sr-only live region, so scope to the log.)
    const log = screen.getByRole("log", { name: "Conversation" });
    expect(await within(log).findByText("Something went wrong. Try again.")).toBeTruthy();
    expect(within(log).getByText("Couldn't reach the Daily Signal server.")).toBeTruthy();
    expect(screen.getByRole("status").textContent).toBe("Something went wrong. Try again.");

    await user.click(screen.getByRole("button", { name: "Retry" }));

    expect(await screen.findByText("Recovered answer")).toBeTruthy();
    expect(screen.queryByText("Something went wrong. Try again.")).toBeNull();
    // The question wasn't duplicated, and was retried with the same context.
    expect(screen.getAllByText("will fail")).toHaveLength(1);
    expect(requestBody(fetchMock, 1)).toMatchObject({
      message: "will fail",
      context: { story_id: "s1" },
      history: [],
    });
  });

  it("surfaces server-reported stream errors the same way", async () => {
    fetchMock.mockImplementation(async () =>
      sseResponse([{ type: "error", message: "Groq rate limit exceeded. Please try again shortly." }]),
    );
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatWindow variant="full" />
      </ChatProvider>,
    );

    await user.type(screen.getByLabelText(INPUT), "hi{Enter}");

    const log = screen.getByRole("log", { name: "Conversation" });
    expect(await within(log).findByText("Something went wrong. Try again.")).toBeTruthy();
    expect(within(log).getByText(/rate limit/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Retry" })).toBeTruthy();
  });
});

describe("bubble, full chat and focus", () => {
  it("opens the compact panel with focus in the input, and Escape returns focus to the bubble", async () => {
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatBubble />
      </ChatProvider>,
    );

    const bubble = screen.getByRole("button", { name: "Ask Daily Signal AI" });
    expect(bubble.getAttribute("aria-expanded")).toBe("false");
    await user.click(bubble);

    const dialog = screen.getByRole("dialog", { name: "Daily Signal AI assistant" });
    expect(dialog).toBeTruthy();
    await waitFor(() => expect(document.activeElement).toBe(screen.getByLabelText(INPUT)));

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(
      screen.getByRole("button", { name: "Ask Daily Signal AI" }),
    );
  });

  it("keeps the conversation when moving between compact chat, full chat and back", async () => {
    fetchMock.mockImplementation(async () =>
      sseResponse(
        answer("Persisted answer [1]", [
          { publisher: "Tech Ledger", url: "https://t.example/a", index: 1 },
        ]),
      ),
    );
    const user = userEvent.setup();

    function App() {
      return (
        <ChatProvider>
          <ChatBubble />
          {nav.pathname === "/chat" ? <FullChat /> : null}
        </ChatProvider>
      );
    }
    const { rerender } = render(<App />);

    await user.click(screen.getByRole("button", { name: "Ask Daily Signal AI" }));
    await user.type(screen.getByLabelText(INPUT), "remember me{Enter}");
    await screen.findByText(/Persisted answer/);

    // "Open full chat" closes the panel and navigates to /chat.
    await user.click(screen.getByRole("link", { name: "Open full chat" }));
    nav.pathname = "/chat";
    rerender(<App />);

    expect(screen.queryByRole("dialog")).toBeNull();
    expect(screen.getByText("remember me")).toBeTruthy();
    expect(screen.getByText(/Persisted answer/)).toBeTruthy();
    expect(screen.getByRole("link", { name: /Tech Ledger/ })).toBeTruthy();

    // The bubble stays on /chat and jumps to the full chat's input.
    await user.click(screen.getByRole("button", { name: "Ask Daily Signal AI" }));
    expect(document.activeElement!.id).toBe("chat-input-full");

    // Continue the conversation from the full chat; history carries over.
    await user.type(screen.getByLabelText(INPUT), "and then?{Enter}");
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(requestBody(fetchMock, 1).history).toEqual([
      { role: "user", content: "remember me" },
      { role: "assistant", content: "Persisted answer [1]" },
    ]);
    expect(requestBody(fetchMock, 1).conversation_id).toBe(requestBody(fetchMock, 0).conversation_id);

    // Back on a newspaper page, reopening the bubble shows the same conversation.
    nav.pathname = "/";
    rerender(<App />);
    await user.click(screen.getByRole("button", { name: "Ask Daily Signal AI" }));
    expect(screen.getByRole("dialog")).toBeTruthy();
    expect(screen.getByText("remember me")).toBeTruthy();
    expect(screen.getByText("and then?")).toBeTruthy();
  });

  it("continues with the last viewed page's context on the full chat page", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("ok")));
    const user = userEvent.setup();

    function App({ showStory }: { showStory: boolean }) {
      return (
        <ChatProvider>
          {showStory ? (
            <ChatPageContextSetter
              context={{ kind: "story", label: "Read story", storyId: "story-1" }}
            />
          ) : null}
          {nav.pathname === "/chat" ? <FullChat /> : null}
        </ChatProvider>
      );
    }

    const { rerender } = render(<App showStory />);
    nav.pathname = "/chat";
    rerender(<App showStory={false} />);

    expect(await screen.findByText("Read story")).toBeTruthy();
    await user.type(screen.getByLabelText(INPUT), "go on{Enter}");
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(requestBody(fetchMock, 0).context).toEqual({ story_id: "story-1" });
  });

  it("starts a fresh conversation with 'New chat'", async () => {
    fetchMock.mockImplementation(async () => sseResponse(answer("first answer")));
    const user = userEvent.setup();
    render(
      <ChatProvider>
        <ChatBubble />
      </ChatProvider>,
    );

    await user.click(screen.getByRole("button", { name: "Ask Daily Signal AI" }));
    await user.type(screen.getByLabelText(INPUT), "hello{Enter}");
    await screen.findByText("first answer");

    await user.click(screen.getByRole("button", { name: "New chat" }));
    expect(screen.queryByText("first answer")).toBeNull();

    await user.type(screen.getByLabelText(INPUT), "again{Enter}");
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(requestBody(fetchMock, 1).history).toEqual([]);
    expect(requestBody(fetchMock, 1).conversation_id).not.toBe(
      requestBody(fetchMock, 0).conversation_id,
    );
  });
});
