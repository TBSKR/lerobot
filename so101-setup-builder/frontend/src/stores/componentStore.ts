import { create } from 'zustand'
import { componentsApi } from '../api/client'

export interface ComponentPrice {
  vendor_id: number
  vendor_name: string
  price: number
  currency: string
  product_url?: string
  in_stock: boolean
}

export interface Component {
  id: number
  name: string
  slug: string
  description?: string
  category: {
    id: number
    name: string
    slug: string
    icon?: string
  }
  specifications: Record<string, unknown>
  is_default_for_so101: boolean
  quantity_per_arm: number
  arm_type?: string
  image_url?: string
  prices: ComponentPrice[]
  lowest_price?: number
}

export interface Category {
  id: number
  name: string
  slug: string
  icon?: string
}

export interface ComponentFilters {
  category_id?: number
  category_slug?: string
  search?: string
  min_price?: number
  max_price?: number
  is_default_for_so101?: boolean
  arm_type?: string
  in_stock_only?: boolean
  page: number
  page_size: number
}

interface ComponentState {
  components: Component[]
  categories: Category[]
  selectedComponents: Component[]
  compareList: number[]
  filters: ComponentFilters
  totalPages: number
  total: number
  isLoading: boolean
  error: string | null

  // Actions
  fetchComponents: () => Promise<void>
  fetchCategories: () => Promise<void>
  setFilters: (filters: Partial<ComponentFilters>) => void
  resetFilters: () => void
  addToCompare: (componentId: number) => void
  removeFromCompare: (componentId: number) => void
  clearCompare: () => void
  selectComponent: (component: Component) => void
  deselectComponent: (componentId: number) => void
}

const defaultFilters: ComponentFilters = {
  page: 1,
  page_size: 20,
}

export const useComponentStore = create<ComponentState>((set, get) => ({
  components: [],
  categories: [],
  selectedComponents: [],
  compareList: [],
  filters: defaultFilters,
  totalPages: 0,
  total: 0,
  isLoading: false,
  error: null,

  fetchComponents: async () => {
    set({ isLoading: true, error: null })
    try {
      const { filters } = get()
      const response = await componentsApi.list(filters as unknown as Record<string, unknown>)
      set({
        components: response.data.items,
        totalPages: response.data.total_pages,
        total: response.data.total,
        isLoading: false,
      })
    } catch (error) {
      set({
        error: 'Failed to load components',
        isLoading: false,
      })
    }
  },

  fetchCategories: async () => {
    try {
      const response = await componentsApi.getCategories()
      set({ categories: response.data })
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  },

  setFilters: (newFilters: Partial<ComponentFilters>) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters, page: newFilters.page || 1 },
    }))
    get().fetchComponents()
  },

  resetFilters: () => {
    set({ filters: defaultFilters })
    get().fetchComponents()
  },

  addToCompare: (componentId: number) => {
    set((state) => {
      if (state.compareList.length >= 5) {
        return state // Max 5 items
      }
      if (state.compareList.includes(componentId)) {
        return state
      }
      return { compareList: [...state.compareList, componentId] }
    })
  },

  removeFromCompare: (componentId: number) => {
    set((state) => ({
      compareList: state.compareList.filter((id) => id !== componentId),
    }))
  },

  clearCompare: () => {
    set({ compareList: [] })
  },

  selectComponent: (component: Component) => {
    set((state) => {
      if (state.selectedComponents.find((c) => c.id === component.id)) {
        return state
      }
      return { selectedComponents: [...state.selectedComponents, component] }
    })
  },

  deselectComponent: (componentId: number) => {
    set((state) => ({
      selectedComponents: state.selectedComponents.filter((c) => c.id !== componentId),
    }))
  },
}))
