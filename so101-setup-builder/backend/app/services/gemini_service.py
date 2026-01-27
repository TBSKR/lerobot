import json
from typing import Any

from app.config import get_settings
from app.api.v1.schemas.recommendation import ComponentRecommendation, ChatMessage
from app.llm.client import GeminiClient
from app.llm.prompts import (
    RECOMMENDATION_SYSTEM_PROMPT,
    CHAT_SYSTEM_PROMPT,
)

settings = get_settings()


class GeminiService:
    """Service for AI-powered recommendations using Gemini."""

    def __init__(self):
        self.client = GeminiClient()

    async def generate_recommendations(
        self,
        profile: dict[str, Any],
        focus_areas: list[str] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate component recommendations based on user profile."""
        # Build prompt with profile context
        prompt = self._build_recommendation_prompt(profile, focus_areas, constraints)

        response = await self.client.generate(
            prompt=prompt,
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
        )

        # Parse response into structured recommendations
        return self._parse_recommendations(response, profile)

    async def chat(
        self,
        message: str,
        history: list[ChatMessage],
        profile: dict[str, Any] | None = None,
        current_recommendations: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Interactive chat for Q&A about the setup."""
        # Build context from history and profile
        context = self._build_chat_context(profile, current_recommendations)

        # Format history for Gemini
        messages = [{"role": m.role, "content": m.content} for m in history]

        response = await self.client.chat(
            message=message,
            history=messages,
            system_prompt=CHAT_SYSTEM_PROMPT.format(context=context),
        )

        return self._parse_chat_response(response)

    def _build_recommendation_prompt(
        self,
        profile: dict[str, Any],
        focus_areas: list[str] | None,
        constraints: dict[str, Any] | None,
    ) -> str:
        """Build the prompt for recommendation generation."""
        prompt = f"""
Based on the following user profile, recommend components for an SO-101 robot arm build:

**User Profile:**
- Experience Level: {profile.get('experience', 'Not specified')}
- Budget: ${profile.get('budget', 'Not specified')}
- Use Case: {profile.get('use_case', 'Not specified')}
- Compute Platform: {profile.get('compute_platform', 'Not specified')}
- Camera Preference: {profile.get('camera_preference', 'Not specified')}
- Arm Type: {profile.get('arm_type', 'single')} (single = follower only, dual = leader + follower)
"""

        if focus_areas:
            prompt += f"\n**Focus Areas:** {', '.join(focus_areas)}"

        if constraints:
            prompt += f"\n**Additional Constraints:** {json.dumps(constraints)}"

        prompt += """

Please provide:
1. A list of recommended components with quantities and reasons
2. A summary of the build
3. Any notes based on the user's experience level and budget
4. Estimated total cost if possible

Format your response as JSON with this structure:
{
    "components": [
        {
            "component_id": <int>,
            "component_name": "<name>",
            "category": "<category>",
            "reason": "<why this component>",
            "priority": "required|recommended|optional",
            "quantity": <int>,
            "alternatives": [<component_ids>]
        }
    ],
    "summary": "<build summary>",
    "estimated_total": <float or null>,
    "notes": ["<note1>", "<note2>"],
    "experience_notes": "<advice based on experience level>",
    "budget_notes": "<notes about budget allocation>",
    "use_case_notes": "<notes specific to use case>"
}
"""
        return prompt

    def _parse_recommendations(
        self,
        response: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Parse Gemini response into structured recommendations."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                # Convert to ComponentRecommendation objects
                components = []
                for comp in data.get("components", []):
                    components.append(
                        ComponentRecommendation(
                            component_id=comp.get("component_id", 0),
                            component_name=comp.get("component_name", "Unknown"),
                            category=comp.get("category", "other"),
                            reason=comp.get("reason", ""),
                            priority=comp.get("priority", "recommended"),
                            quantity=comp.get("quantity", 1),
                            alternatives=comp.get("alternatives", []),
                        )
                    )

                return {
                    "components": components,
                    "summary": data.get("summary", ""),
                    "estimated_total": data.get("estimated_total"),
                    "notes": data.get("notes", []),
                    "experience_notes": data.get("experience_notes"),
                    "budget_notes": data.get("budget_notes"),
                    "use_case_notes": data.get("use_case_notes"),
                }

        except (json.JSONDecodeError, KeyError, TypeError):
            pass

        # Return default if parsing fails
        return self._get_default_recommendations(profile)

    def _parse_chat_response(self, response: str) -> dict[str, Any]:
        """Parse chat response."""
        # Check if response contains JSON for actions
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return {
                    "message": data.get("message", response),
                    "suggested_actions": data.get("suggested_actions"),
                    "updated_recommendations": data.get("updated_recommendations"),
                }
        except (json.JSONDecodeError, KeyError):
            pass

        return {"message": response}

    def _build_chat_context(
        self,
        profile: dict[str, Any] | None,
        recommendations: dict[str, Any] | None,
    ) -> str:
        """Build context string for chat."""
        context_parts = []

        if profile:
            context_parts.append(f"User Profile: {json.dumps(profile)}")

        if recommendations:
            context_parts.append(f"Current Recommendations: {json.dumps(recommendations)}")

        return "\n".join(context_parts) if context_parts else "No context available."

    def _get_default_recommendations(
        self,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Return default SO-101 recommendations."""
        arm_type = profile.get("arm_type", "single")

        components = []

        if arm_type == "dual":
            components.extend([
                ComponentRecommendation(
                    component_id=1,
                    component_name="Feetech STS3215 (1/345)",
                    category="motors",
                    reason="Follower arm motors",
                    priority="required",
                    quantity=6,
                ),
                ComponentRecommendation(
                    component_id=2,
                    component_name="Feetech STS3215 (Mixed ratios)",
                    category="motors",
                    reason="Leader arm motors",
                    priority="required",
                    quantity=6,
                ),
            ])
        else:
            components.append(
                ComponentRecommendation(
                    component_id=1,
                    component_name="Feetech STS3215 (1/345)",
                    category="motors",
                    reason="All joints use same motor",
                    priority="required",
                    quantity=6,
                )
            )

        components.extend([
            ComponentRecommendation(
                component_id=5,
                component_name="Waveshare Servo Driver",
                category="electronics",
                reason="Motor controller",
                priority="required",
                quantity=2 if arm_type == "dual" else 1,
            ),
            ComponentRecommendation(
                component_id=6,
                component_name="12V 5A Power Supply",
                category="power",
                reason="Powers motors",
                priority="required",
                quantity=2 if arm_type == "dual" else 1,
            ),
        ])

        return {
            "components": components,
            "summary": f"Default SO-101 {arm_type}-arm build",
            "notes": ["Default configuration based on LeRobot documentation"],
        }
