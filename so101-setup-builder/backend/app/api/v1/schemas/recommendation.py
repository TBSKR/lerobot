from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request for AI-powered recommendations."""

    setup_id: UUID
    focus_areas: list[str] | None = Field(
        None,
        description="Specific areas to focus on: budget, performance, ease_of_use, expandability",
    )
    constraints: dict[str, Any] | None = Field(
        None,
        description="Additional constraints like max_price, required_features, etc.",
    )


class ComponentRecommendation(BaseModel):
    """A single component recommendation."""

    component_id: int
    component_name: str
    category: str
    reason: str
    priority: str  # required, recommended, optional
    quantity: int = 1
    alternatives: list[int] = []  # Alternative component IDs


class RecommendationResponse(BaseModel):
    """AI-generated recommendations response."""

    setup_id: UUID
    recommendations: list[ComponentRecommendation]
    summary: str
    estimated_total: float | None = None
    notes: list[str] = []

    # Based on profile
    experience_notes: str | None = None
    budget_notes: str | None = None
    use_case_notes: str | None = None


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str  # user, assistant
    content: str


class ChatRequest(BaseModel):
    """Request for interactive Q&A."""

    setup_id: UUID
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    """Response from chat interaction."""

    message: str
    suggested_actions: list[dict[str, Any]] | None = None
    updated_recommendations: list[ComponentRecommendation] | None = None
