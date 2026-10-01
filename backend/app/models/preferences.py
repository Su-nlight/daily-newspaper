from pydantic import BaseModel, Field


class TopicPreference(BaseModel):
    id: str
    weight: float = Field(ge=0, le=1)


class UserPreferences(BaseModel):
    """Mirrors the frontend's UserPreferences shape (Module 05). Not
    persisted or consumed by any endpoint yet — included so the graph's
    future personalization-aware nodes have a typed shape to build against.
    """

    topics: list[TopicPreference] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    content_types: list[str] = Field(default_factory=list)
    reading_time: int = 10
