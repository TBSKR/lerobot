import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { recommendationsApi, pricingApi, exportApi } from '../api/client'

export interface ComponentRecommendation {
  component_id: number
  component_name: string
  category: string
  reason: string
  priority: 'required' | 'recommended' | 'optional'
  quantity: number
  alternatives: number[]
}

export interface Recommendations {
  components: ComponentRecommendation[]
  summary: string
  estimated_total?: number
  notes: string[]
  experience_notes?: string
  budget_notes?: string
  use_case_notes?: string
}

export interface SetupPricing {
  setup_id: string
  subtotal: number
  total: number
  currency: string
  cost_by_category: Record<string, number>
  vendors_used: string[]
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface SetupState {
  recommendations: Recommendations | null
  pricing: SetupPricing | null
  chatHistory: ChatMessage[]
  isLoading: boolean
  error: string | null

  // Actions
  generateRecommendations: (setupId: string, focusAreas?: string[]) => Promise<void>
  fetchPricing: (setupId: string) => Promise<void>
  sendChatMessage: (setupId: string, message: string) => Promise<string>
  exportPdf: (setupId: string) => Promise<Blob>
  exportJson: (setupId: string) => Promise<unknown>
  exportShoppingList: (setupId: string) => Promise<unknown>
  clearChat: () => void
  reset: () => void
}

export const useSetupStore = create<SetupState>()(
  persist(
    (set, get) => ({
      recommendations: null,
      pricing: null,
      chatHistory: [],
      isLoading: false,
      error: null,

      generateRecommendations: async (setupId: string, focusAreas?: string[]) => {
        set({ isLoading: true, error: null })
        try {
          const response = await recommendationsApi.generate(setupId, focusAreas)
          set({
            recommendations: response.data,
            isLoading: false,
          })
        } catch (error) {
          set({
            error: 'Failed to generate recommendations',
            isLoading: false,
          })
        }
      },

      fetchPricing: async (setupId: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await pricingApi.getSetupPricing(setupId)
          set({
            pricing: response.data,
            isLoading: false,
          })
        } catch (error) {
          set({
            error: 'Failed to fetch pricing',
            isLoading: false,
          })
        }
      },

      sendChatMessage: async (setupId: string, message: string) => {
        const { chatHistory } = get()

        // Add user message
        const newHistory: ChatMessage[] = [...chatHistory, { role: 'user', content: message }]
        set({ chatHistory: newHistory, isLoading: true })

        try {
          const response = await recommendationsApi.chat(
            setupId,
            message,
            chatHistory.map((m) => ({ role: m.role, content: m.content }))
          )

          const assistantMessage = response.data.message
          set({
            chatHistory: [...newHistory, { role: 'assistant', content: assistantMessage }],
            isLoading: false,
          })

          return assistantMessage
        } catch (error) {
          const errorMessage = 'Sorry, I encountered an error. Please try again.'
          set({
            chatHistory: [...newHistory, { role: 'assistant', content: errorMessage }],
            isLoading: false,
            error: 'Chat request failed',
          })
          return errorMessage
        }
      },

      exportPdf: async (setupId: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await exportApi.pdf(setupId)
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({
            error: 'Failed to export PDF',
            isLoading: false,
          })
          throw error
        }
      },

      exportJson: async (setupId: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await exportApi.json(setupId)
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({
            error: 'Failed to export JSON',
            isLoading: false,
          })
          throw error
        }
      },

      exportShoppingList: async (setupId: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await exportApi.shoppingList(setupId)
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({
            error: 'Failed to generate shopping list',
            isLoading: false,
          })
          throw error
        }
      },

      clearChat: () => {
        set({ chatHistory: [] })
      },

      reset: () => {
        set({
          recommendations: null,
          pricing: null,
          chatHistory: [],
          isLoading: false,
          error: null,
        })
      },
    }),
    {
      name: 'setup-storage',
      partialize: (state) => ({
        recommendations: state.recommendations,
        chatHistory: state.chatHistory,
      }),
    }
  )
)
