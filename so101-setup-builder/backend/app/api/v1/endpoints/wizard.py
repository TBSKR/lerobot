from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.wizard import (
    WizardStartResponse,
    WizardStepUpdate,
    WizardProfile,
    WizardSummary,
)
from app.config import get_settings
from app.db.database import get_db
from app.db.models import Setup

router = APIRouter()
settings = get_settings()

WIZARD_STEPS = {
    1: "experience",
    2: "budget",
    3: "use_case",
    4: "compute_platform",
    5: "camera_preference",
}


@router.post("/start", response_model=WizardStartResponse)
async def start_wizard(db: AsyncSession = Depends(get_db)):
    """Create a new setup session and start the wizard."""
    setup = Setup(
        wizard_profile={},
        current_step=1,
        expires_at=datetime.utcnow() + timedelta(days=settings.session_expiry_days),
    )
    db.add(setup)
    await db.commit()
    await db.refresh(setup)

    return WizardStartResponse(
        setup_id=setup.id,
        current_step=setup.current_step,
        created_at=setup.created_at,
    )


@router.put("/{setup_id}/step/{step_number}", response_model=WizardSummary)
async def update_wizard_step(
    setup_id: UUID,
    step_number: int,
    step_update: WizardStepUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Save answer for a wizard step."""
    if step_number < 1 or step_number > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step number must be between 1 and 5",
        )

    result = await db.execute(select(Setup).where(Setup.id == setup_id))
    setup = result.scalar_one_or_none()

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    # Update wizard profile with step data
    profile = setup.wizard_profile or {}
    profile.update(step_update.step_data)
    setup.wizard_profile = profile

    # Update current step (allow going back)
    if step_number >= setup.current_step:
        setup.current_step = min(step_number + 1, 6)

    # Mark as completed if all steps done
    if setup.current_step > 5:
        setup.wizard_completed = True

    # Handle arm_type from profile
    if "arm_type" in step_update.step_data:
        setup.arm_type = step_update.step_data["arm_type"]

    await db.commit()
    await db.refresh(setup)

    return WizardSummary(
        setup_id=setup.id,
        profile=WizardProfile(**setup.wizard_profile),
        current_step=setup.current_step,
        wizard_completed=setup.wizard_completed,
        created_at=setup.created_at,
        updated_at=setup.updated_at,
    )


@router.get("/{setup_id}/summary", response_model=WizardSummary)
async def get_wizard_summary(
    setup_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the full wizard profile and setup summary."""
    result = await db.execute(select(Setup).where(Setup.id == setup_id))
    setup = result.scalar_one_or_none()

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    return WizardSummary(
        setup_id=setup.id,
        profile=WizardProfile(**(setup.wizard_profile or {})),
        current_step=setup.current_step,
        wizard_completed=setup.wizard_completed,
        recommended_components=setup.recommendations,
        created_at=setup.created_at,
        updated_at=setup.updated_at,
    )


@router.delete("/{setup_id}")
async def delete_setup(
    setup_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a setup and all associated data."""
    result = await db.execute(select(Setup).where(Setup.id == setup_id))
    setup = result.scalar_one_or_none()

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    await db.delete(setup)
    await db.commit()

    return {"message": "Setup deleted successfully"}
