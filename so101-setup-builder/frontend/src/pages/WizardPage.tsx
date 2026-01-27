import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Check, Loader2 } from 'lucide-react'
import { clsx } from 'clsx'
import { useWizardStore, WizardProfile, ExperienceLevel, UseCase, ComputePlatform, CameraPreference, ArmType } from '../stores/wizardStore'

const steps = [
  { number: 1, title: 'Experience', description: 'Your robotics background' },
  { number: 2, title: 'Budget', description: 'How much to spend' },
  { number: 3, title: 'Use Case', description: 'What you want to build' },
  { number: 4, title: 'Compute', description: 'Your hardware setup' },
  { number: 5, title: 'Camera', description: 'Visual input preference' },
]

export default function WizardPage() {
  const navigate = useNavigate()
  const {
    setupId,
    currentStep,
    profile,
    isLoading,
    wizardCompleted,
    startWizard,
    updateStep,
    goToStep,
    setProfile,
  } = useWizardStore()

  useEffect(() => {
    if (!setupId) {
      startWizard()
    }
  }, [setupId, startWizard])

  useEffect(() => {
    if (wizardCompleted && setupId) {
      navigate(`/setup/${setupId}`)
    }
  }, [wizardCompleted, setupId, navigate])

  const handleNext = async () => {
    let stepData: Record<string, unknown> = {}

    switch (currentStep) {
      case 1:
        stepData = { experience: profile.experience }
        break
      case 2:
        stepData = { budget: profile.budget }
        break
      case 3:
        stepData = { use_case: profile.use_case, arm_type: profile.arm_type }
        break
      case 4:
        stepData = { compute_platform: profile.compute_platform }
        break
      case 5:
        stepData = { camera_preference: profile.camera_preference }
        break
    }

    await updateStep(currentStep, stepData)
  }

  const handleBack = () => {
    if (currentStep > 1) {
      goToStep(currentStep - 1)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return !!profile.experience
      case 2:
        return profile.budget !== undefined
      case 3:
        return !!profile.use_case
      case 4:
        return !!profile.compute_platform
      case 5:
        return !!profile.camera_preference
      default:
        return false
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center">
              <button
                onClick={() => step.number < currentStep && goToStep(step.number)}
                disabled={step.number > currentStep}
                className={clsx(
                  'flex items-center justify-center w-10 h-10 rounded-full border-2 font-medium transition-colors',
                  step.number < currentStep
                    ? 'bg-primary-600 border-primary-600 text-white cursor-pointer'
                    : step.number === currentStep
                    ? 'border-primary-600 text-primary-600'
                    : 'border-gray-300 text-gray-400 cursor-not-allowed'
                )}
              >
                {step.number < currentStep ? <Check className="h-5 w-5" /> : step.number}
              </button>
              {index < steps.length - 1 && (
                <div
                  className={clsx(
                    'w-full h-1 mx-2',
                    step.number < currentStep ? 'bg-primary-600' : 'bg-gray-200'
                  )}
                  style={{ width: '60px' }}
                />
              )}
            </div>
          ))}
        </div>
        <div className="mt-4 text-center">
          <h2 className="text-xl font-semibold text-gray-900">
            {steps[currentStep - 1]?.title}
          </h2>
          <p className="text-gray-600">{steps[currentStep - 1]?.description}</p>
        </div>
      </div>

      {/* Step Content */}
      <div className="card p-6 mb-6">
        {currentStep === 1 && <ExperienceStep profile={profile} setProfile={setProfile} />}
        {currentStep === 2 && <BudgetStep profile={profile} setProfile={setProfile} />}
        {currentStep === 3 && <UseCaseStep profile={profile} setProfile={setProfile} />}
        {currentStep === 4 && <ComputeStep profile={profile} setProfile={setProfile} />}
        {currentStep === 5 && <CameraStep profile={profile} setProfile={setProfile} />}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleBack}
          disabled={currentStep === 1}
          className="btn btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="h-5 w-5" />
          Back
        </button>
        <button
          onClick={handleNext}
          disabled={!canProceed() || isLoading}
          className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : currentStep === 5 ? (
            <>
              Finish
              <Check className="h-5 w-5" />
            </>
          ) : (
            <>
              Next
              <ChevronRight className="h-5 w-5" />
            </>
          )}
        </button>
      </div>
    </div>
  )
}

// Step Components
interface StepProps {
  profile: WizardProfile
  setProfile: (profile: Partial<WizardProfile>) => void
}

function ExperienceStep({ profile, setProfile }: StepProps) {
  const options: { value: ExperienceLevel; label: string; description: string }[] = [
    {
      value: 'beginner',
      label: 'Beginner',
      description: 'New to robotics and machine learning',
    },
    {
      value: 'intermediate',
      label: 'Intermediate',
      description: 'Some experience with robots or ML',
    },
    {
      value: 'advanced',
      label: 'Advanced',
      description: 'Experienced roboticist or ML engineer',
    },
  ]

  return (
    <div className="space-y-4">
      <h3 className="font-medium text-gray-900">What's your experience level?</h3>
      <div className="space-y-3">
        {options.map((option) => (
          <label
            key={option.value}
            className={clsx(
              'flex items-start p-4 rounded-lg border-2 cursor-pointer transition-colors',
              profile.experience === option.value
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            <input
              type="radio"
              name="experience"
              value={option.value}
              checked={profile.experience === option.value}
              onChange={() => setProfile({ experience: option.value })}
              className="mt-1 mr-3"
            />
            <div>
              <span className="font-medium text-gray-900">{option.label}</span>
              <p className="text-sm text-gray-600">{option.description}</p>
            </div>
          </label>
        ))}
      </div>
    </div>
  )
}

function BudgetStep({ profile, setProfile }: StepProps) {
  const [budget, setBudget] = useState(profile.budget || 500)

  const handleChange = (value: number) => {
    setBudget(value)
    setProfile({ budget: value })
  }

  return (
    <div className="space-y-6">
      <h3 className="font-medium text-gray-900">What's your budget?</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">$200</span>
          <span className="text-3xl font-bold text-primary-600">${budget}</span>
          <span className="text-sm text-gray-600">$2000</span>
        </div>
        <input
          type="range"
          min={200}
          max={2000}
          step={50}
          value={budget}
          onChange={(e) => handleChange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
        />
        <div className="grid grid-cols-3 gap-2 text-center text-sm">
          <button
            onClick={() => handleChange(300)}
            className="py-2 px-3 rounded border border-gray-200 hover:bg-gray-50"
          >
            Budget (~$300)
          </button>
          <button
            onClick={() => handleChange(500)}
            className="py-2 px-3 rounded border border-gray-200 hover:bg-gray-50"
          >
            Standard (~$500)
          </button>
          <button
            onClick={() => handleChange(1000)}
            className="py-2 px-3 rounded border border-gray-200 hover:bg-gray-50"
          >
            Premium (~$1000)
          </button>
        </div>
      </div>
    </div>
  )
}

function UseCaseStep({ profile, setProfile }: StepProps) {
  const useCases: { value: UseCase; label: string; description: string }[] = [
    {
      value: 'learning',
      label: 'Learning & Education',
      description: 'Learn robotics and ML concepts',
    },
    {
      value: 'research',
      label: 'Research & Experimentation',
      description: 'Academic or personal research',
    },
    {
      value: 'production',
      label: 'Production & Deployment',
      description: 'Build reliable systems',
    },
  ]

  const armTypes: { value: ArmType; label: string; description: string }[] = [
    {
      value: 'single',
      label: 'Single Arm (Follower)',
      description: 'One arm for autonomous tasks',
    },
    {
      value: 'dual',
      label: 'Dual Arm (Leader + Follower)',
      description: 'Teleoperation setup for data collection',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h3 className="font-medium text-gray-900">What will you use it for?</h3>
        <div className="space-y-3">
          {useCases.map((option) => (
            <label
              key={option.value}
              className={clsx(
                'flex items-start p-4 rounded-lg border-2 cursor-pointer transition-colors',
                profile.use_case === option.value
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              <input
                type="radio"
                name="use_case"
                value={option.value}
                checked={profile.use_case === option.value}
                onChange={() => setProfile({ use_case: option.value })}
                className="mt-1 mr-3"
              />
              <div>
                <span className="font-medium text-gray-900">{option.label}</span>
                <p className="text-sm text-gray-600">{option.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-medium text-gray-900">Arm configuration</h3>
        <div className="space-y-3">
          {armTypes.map((option) => (
            <label
              key={option.value}
              className={clsx(
                'flex items-start p-4 rounded-lg border-2 cursor-pointer transition-colors',
                profile.arm_type === option.value
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              <input
                type="radio"
                name="arm_type"
                value={option.value}
                checked={profile.arm_type === option.value}
                onChange={() => setProfile({ arm_type: option.value })}
                className="mt-1 mr-3"
              />
              <div>
                <span className="font-medium text-gray-900">{option.label}</span>
                <p className="text-sm text-gray-600">{option.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}

function ComputeStep({ profile, setProfile }: StepProps) {
  const options: { value: ComputePlatform; label: string; description: string }[] = [
    {
      value: 'cuda',
      label: 'NVIDIA GPU (CUDA)',
      description: 'Best for training - GTX/RTX cards',
    },
    {
      value: 'mps',
      label: 'Apple Silicon (MPS)',
      description: 'MacBook M1/M2/M3',
    },
    {
      value: 'xpu',
      label: 'Intel GPU (XPU)',
      description: 'Intel Arc or integrated graphics',
    },
    {
      value: 'cpu',
      label: 'CPU Only',
      description: 'No GPU acceleration (slower)',
    },
  ]

  return (
    <div className="space-y-4">
      <h3 className="font-medium text-gray-900">What compute platform will you use?</h3>
      <div className="space-y-3">
        {options.map((option) => (
          <label
            key={option.value}
            className={clsx(
              'flex items-start p-4 rounded-lg border-2 cursor-pointer transition-colors',
              profile.compute_platform === option.value
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            <input
              type="radio"
              name="compute"
              value={option.value}
              checked={profile.compute_platform === option.value}
              onChange={() => setProfile({ compute_platform: option.value })}
              className="mt-1 mr-3"
            />
            <div>
              <span className="font-medium text-gray-900">{option.label}</span>
              <p className="text-sm text-gray-600">{option.description}</p>
            </div>
          </label>
        ))}
      </div>
    </div>
  )
}

function CameraStep({ profile, setProfile }: StepProps) {
  const options: { value: CameraPreference; label: string; description: string }[] = [
    {
      value: 'basic',
      label: 'Basic USB Webcam',
      description: 'Simple OpenCV-compatible camera',
    },
    {
      value: 'realsense',
      label: 'Intel RealSense',
      description: 'Depth camera for 3D perception',
    },
    {
      value: 'multiple',
      label: 'Multiple Cameras',
      description: 'Multi-view setup for better coverage',
    },
    {
      value: 'phone',
      label: 'Phone Camera',
      description: 'Use your phone via ZMQ streaming',
    },
  ]

  return (
    <div className="space-y-4">
      <h3 className="font-medium text-gray-900">Camera preference</h3>
      <div className="space-y-3">
        {options.map((option) => (
          <label
            key={option.value}
            className={clsx(
              'flex items-start p-4 rounded-lg border-2 cursor-pointer transition-colors',
              profile.camera_preference === option.value
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            <input
              type="radio"
              name="camera"
              value={option.value}
              checked={profile.camera_preference === option.value}
              onChange={() => setProfile({ camera_preference: option.value })}
              className="mt-1 mr-3"
            />
            <div>
              <span className="font-medium text-gray-900">{option.label}</span>
              <p className="text-sm text-gray-600">{option.description}</p>
            </div>
          </label>
        ))}
      </div>
    </div>
  )
}
