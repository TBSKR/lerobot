from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UseCase(str, Enum):
    LEARNING = "learning"
    RESEARCH = "research"
    PRODUCTION = "production"


class ComputePlatform(str, Enum):
    CUDA = "cuda"
    MPS = "mps"
    XPU = "xpu"
    CPU = "cpu"


class CameraPreference(str, Enum):
    BASIC = "basic"  # USB webcam with OpenCV
    REALSENSE = "realsense"  # Intel RealSense depth camera
    MULTIPLE = "multiple"  # Multiple cameras
    PHONE = "phone"  # Phone camera via ZMQ


class ArmType(str, Enum):
    SINGLE = "single"  # Just follower arm
    DUAL = "dual"  # Leader + follower (teleoperation)


class WizardStartResponse(BaseModel):
    """Response when starting a new wizard session."""

    setup_id: UUID
    current_step: int = 1
    created_at: datetime


class WizardStepUpdate(BaseModel):
    """Update for a single wizard step."""

    step_data: dict[str, Any] = Field(
        ...,
        description="Step-specific data",
        examples=[
            {"experience": "beginner"},
            {"budget": 500},
            {"use_case": "learning"},
            {"compute_platform": "cuda"},
            {"camera_preference": "basic"},
        ],
    )


class WizardProfile(BaseModel):
    """Complete wizard profile with all answers."""

    experience: ExperienceLevel | None = None
    budget: int | None = Field(None, ge=200, le=2000)
    use_case: UseCase | None = None
    compute_platform: ComputePlatform | None = None
    camera_preference: CameraPreference | None = None
    arm_type: ArmType = ArmType.SINGLE


class WizardSummary(BaseModel):
    """Full setup summary after wizard completion."""

    setup_id: UUID
    profile: WizardProfile
    current_step: int
    wizard_completed: bool
    recommended_components: list[dict[str, Any]] | None = None
    estimated_cost: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
