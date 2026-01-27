from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    ComponentRecommendation,
    ChatRequest,
    ChatResponse,
)
from app.db.database import get_db
from app.db.models import Setup
from app.services.gemini_service import GeminiService

router = APIRouter()


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate AI-powered component recommendations based on wizard profile."""
    result = await db.execute(select(Setup).where(Setup.id == request.setup_id))
    setup = result.scalar_one_or_none()

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    if not setup.wizard_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete the wizard first",
        )

    # Use Gemini service to generate recommendations
    gemini = GeminiService()

    try:
        recommendations = await gemini.generate_recommendations(
            profile=setup.wizard_profile,
            focus_areas=request.focus_areas,
            constraints=request.constraints,
        )

        # Save recommendations to setup
        setup.recommendations = {
            "components": [r.model_dump() for r in recommendations["components"]],
            "summary": recommendations["summary"],
            "notes": recommendations.get("notes", []),
        }
        await db.commit()

        return RecommendationResponse(
            setup_id=setup.id,
            recommendations=recommendations["components"],
            summary=recommendations["summary"],
            estimated_total=recommendations.get("estimated_total"),
            notes=recommendations.get("notes", []),
            experience_notes=recommendations.get("experience_notes"),
            budget_notes=recommendations.get("budget_notes"),
            use_case_notes=recommendations.get("use_case_notes"),
        )

    except Exception as e:
        # Return default recommendations if AI fails
        return await get_default_recommendations(setup.id, setup.wizard_profile, db)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Interactive Q&A about the setup."""
    result = await db.execute(select(Setup).where(Setup.id == request.setup_id))
    setup = result.scalar_one_or_none()

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    gemini = GeminiService()

    try:
        response = await gemini.chat(
            message=request.message,
            history=request.history,
            profile=setup.wizard_profile,
            current_recommendations=setup.recommendations,
        )

        return ChatResponse(
            message=response["message"],
            suggested_actions=response.get("suggested_actions"),
            updated_recommendations=response.get("updated_recommendations"),
        )

    except Exception as e:
        return ChatResponse(
            message=f"I'm having trouble processing your request. Error: {str(e)}",
            suggested_actions=[
                {"action": "retry", "label": "Try again"},
                {"action": "defaults", "label": "Use default recommendations"},
            ],
        )


async def get_default_recommendations(
    setup_id: UUID,
    profile: dict,
    db: AsyncSession,
) -> RecommendationResponse:
    """Return default SO-101 recommendations when AI is unavailable."""
    arm_type = profile.get("arm_type", "single")

    recommendations = []

    # Motors
    if arm_type == "dual":
        recommendations.extend([
            ComponentRecommendation(
                component_id=1,
                component_name="Feetech STS3215 (1/345 gear ratio)",
                category="motors",
                reason="Default follower arm motor for SO-101",
                priority="required",
                quantity=6,
            ),
            ComponentRecommendation(
                component_id=2,
                component_name="Feetech STS3215 (1/191 gear ratio)",
                category="motors",
                reason="Leader arm joints 1 and 3",
                priority="required",
                quantity=2,
            ),
            ComponentRecommendation(
                component_id=3,
                component_name="Feetech STS3215 (1/345 gear ratio)",
                category="motors",
                reason="Leader arm joint 2",
                priority="required",
                quantity=1,
            ),
            ComponentRecommendation(
                component_id=4,
                component_name="Feetech STS3215 (1/147 gear ratio)",
                category="motors",
                reason="Leader arm joints 4, 5, and 6",
                priority="required",
                quantity=3,
            ),
        ])
    else:
        recommendations.append(
            ComponentRecommendation(
                component_id=1,
                component_name="Feetech STS3215 (1/345 gear ratio)",
                category="motors",
                reason="Default motor for all SO-101 follower arm joints",
                priority="required",
                quantity=6,
            )
        )

    # Common components
    recommendations.extend([
        ComponentRecommendation(
            component_id=5,
            component_name="Waveshare Servo Driver Board",
            category="electronics",
            reason="Controls servo motors via USB",
            priority="required",
            quantity=2 if arm_type == "dual" else 1,
        ),
        ComponentRecommendation(
            component_id=6,
            component_name="12V 5A Power Supply",
            category="power",
            reason="Powers the servo motors",
            priority="required",
            quantity=2 if arm_type == "dual" else 1,
        ),
        ComponentRecommendation(
            component_id=7,
            component_name="3-Pin Servo Cables",
            category="cables",
            reason="Connects motors to driver board",
            priority="required",
            quantity=10 if arm_type == "dual" else 5,
        ),
    ])

    # Camera based on preference
    camera_pref = profile.get("camera_preference", "basic")
    if camera_pref == "basic":
        recommendations.append(
            ComponentRecommendation(
                component_id=8,
                component_name="USB Webcam (OpenCV compatible)",
                category="cameras",
                reason="Basic camera for visual feedback",
                priority="recommended",
                quantity=1,
            )
        )
    elif camera_pref == "realsense":
        recommendations.append(
            ComponentRecommendation(
                component_id=9,
                component_name="Intel RealSense D435",
                category="cameras",
                reason="Depth camera for 3D perception",
                priority="recommended",
                quantity=1,
            )
        )

    summary = f"Default SO-101 {'dual-arm (leader + follower)' if arm_type == 'dual' else 'single-arm (follower)'} build configuration."

    return RecommendationResponse(
        setup_id=setup_id,
        recommendations=recommendations,
        summary=summary,
        notes=[
            "These are the standard components recommended in the LeRobot documentation.",
            "Prices may vary by vendor - check multiple sources for best deals.",
        ],
    )
