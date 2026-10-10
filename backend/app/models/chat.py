from typing import Literal

from pydantic import BaseModel, Field


class ChatContext(BaseModel):
    """What the frontend already knows about where the user is — the story
    they're reading, today's edition, a category page, or the current
    search results. All optional: a chat opened on a page with no context
    carries none.
    """

    story_id: str | None = None
    edition_id: str | None = None
    category: str | None = None
    search_query: str | None = None
    search_result_ids: list[str] | None = None


class ChatTurn(BaseModel):
    """One prior message in the conversation, sent by the frontend so
    follow-up questions ("how does that affect my research?") make sense."""

    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: ChatContext = Field(default_factory=ChatContext)
    history: list[ChatTurn] = Field(default_factory=list)


class ChatSourceRef(BaseModel):
    """A source the answer actually cited. `url` is only ever populated
    from a retrieved Article's own source_url — see
    app/graph/nodes/validate_format.py. Never taken from raw model output.
    """

    publisher: str
    url: str
    title: str | None = None
    # The [n] citation number the model used for this source, so the
    # frontend can link inline [n] markers to the right entry even when
    # only some of the retrieved documents were cited.
    index: int | None = None


class ChatResponse(BaseModel):
    message: str
    sources: list[ChatSourceRef] = Field(default_factory=list)
    conversation_id: str
