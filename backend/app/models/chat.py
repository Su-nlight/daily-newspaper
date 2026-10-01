from pydantic import BaseModel, Field


class ChatContext(BaseModel):
    """What the frontend may already know when the user asks a question —
    e.g. they're reading a specific story. All optional: a general question
    on the homepage carries no context at all.
    """

    story_id: str | None = None
    edition_id: str | None = None
    category: str | None = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: ChatContext = Field(default_factory=ChatContext)


class ChatSourceRef(BaseModel):
    """A source the answer actually cited. `url` is only ever populated
    from a retrieved Article's own source_url — see
    app/graph/nodes/validate_format.py. Never taken from raw model output.
    """

    publisher: str
    url: str
    title: str | None = None


class ChatResponse(BaseModel):
    message: str
    sources: list[ChatSourceRef] = Field(default_factory=list)
    conversation_id: str
