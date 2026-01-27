import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { wizardApi } from '../api/client'

export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced'
export type UseCase = 'learning' | 'research' | 'production'
export type ComputePlatform = 'cuda' | 'mps' | 'xpu' | 'cpu'
export type CameraPreference = 'basic' | 'realsense' | 'multiple' | 'phone'
export type ArmType = 'single' | 'dual'

export interface WizardProfile {
  experience?: ExperienceLevel
  budget?: number
  use_case?: UseCase
  compute_platform?: ComputePlatform
  camera_preference?: CameraPreference
  arm_type?: ArmType
}

interface WizardState {
  setupId: string | null
  currentStep: number
  profile: WizardProfile
  isLoading: boolean
  error: string | null
  wizardCompleted: boolean

  // Actions
  startWizard: () => Promise<void>
  updateStep: (step: number, data: Record<string, unknown>) => Promise<void>
  goToStep: (step: number) => void
  setProfile: (profile: Partial<WizardProfile>) => void
  reset: () => void
}

export const useWizardStore = create<WizardState>()(
  persist(
    (set, get) => ({
      setupId: null,
      currentStep: 1,
      profile: {},
      isLoading: false,
      error: null,
      wizardCompleted: false,

      startWizard: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await wizardApi.start()
          set({
            setupId: response.data.setup_id,
            currentStep: 1,
            profile: {},
            wizardCompleted: false,
            isLoading: false,
          })
        } catch (error) {
          set({
            error: 'Failed to start wizard',
            isLoading: false,
          })
        }
      },

      updateStep: async (step: number, data: Record<string, unknown>) => {
        const { setupId } = get()
        if (!setupId) {
          set({ error: 'No active setup' })
          return
        }

        set({ isLoading: true, error: null })
        try {
          const response = await wizardApi.updateStep(setupId, step, data)
          set({
            currentStep: response.data.current_step,
            profile: response.data.profile,
            wizardCompleted: response.data.wizard_completed,
            isLoading: false,
          })
        } catch (error) {
          set({
            error: 'Failed to save step',
            isLoading: false,
          })
        }
      },

      goToStep: (step: number) => {
        if (step >= 1 && step <= 5) {
          set({ currentStep: step })
        }
      },

      setProfile: (profile: Partial<WizardProfile>) => {
        set((state) => ({
          profile: { ...state.profile, ...profile },
        }))
      },

      reset: () => {
        set({
          setupId: null,
          currentStep: 1,
          profile: {},
          isLoading: false,
          error: null,
          wizardCompleted: false,
        })
      },
    }),
    {
      name: 'wizard-storage',
      partialize: (state) => ({
        setupId: state.setupId,
        currentStep: state.currentStep,
        profile: state.profile,
        wizardCompleted: state.wizardCompleted,
      }),
    }
  )
)
