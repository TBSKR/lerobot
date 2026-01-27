import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter, ChevronLeft, ChevronRight, GitCompare, Check, ExternalLink } from 'lucide-react'
import { clsx } from 'clsx'
import { useComponentStore, Component } from '../stores/componentStore'

export default function ComponentsPage() {
  const {
    components,
    categories,
    compareList,
    filters,
    totalPages,
    total,
    isLoading,
    fetchComponents,
    fetchCategories,
    setFilters,
    addToCompare,
    removeFromCompare,
  } = useComponentStore()

  const [searchInput, setSearchInput] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchCategories()
    fetchComponents()
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setFilters({ search: searchInput || undefined })
  }

  const handleCategoryFilter = (categorySlug: string | undefined) => {
    setFilters({ category_slug: categorySlug })
  }

  const handlePageChange = (page: number) => {
    setFilters({ page })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Components</h1>
          <p className="text-gray-600">Browse {total} SO-101 compatible components</p>
        </div>

        {/* Compare button */}
        {compareList.length > 0 && (
          <Link
            to="/comparison"
            className="btn btn-primary flex items-center gap-2"
          >
            <GitCompare className="h-5 w-5" />
            Compare ({compareList.length})
          </Link>
        )}
      </div>

      {/* Search and Filters */}
      <div className="card p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search components..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="input pl-10"
              />
            </div>
          </form>

          {/* Filter toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-outline flex items-center gap-2"
          >
            <Filter className="h-5 w-5" />
            Filters
          </button>
        </div>

        {/* Category filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleCategoryFilter(undefined)}
                className={clsx(
                  'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
                  !filters.category_slug
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                All
              </button>
              {categories.map((category) => (
                <button
                  key={category.slug}
                  onClick={() => handleCategoryFilter(category.slug)}
                  className={clsx(
                    'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
                    filters.category_slug === category.slug
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {category.name}
                </button>
              ))}
            </div>

            <div className="mt-4 flex flex-wrap gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={filters.is_default_for_so101 === true}
                  onChange={(e) =>
                    setFilters({
                      is_default_for_so101: e.target.checked ? true : undefined,
                    })
                  }
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">SO-101 Defaults Only</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={filters.in_stock_only}
                  onChange={(e) => setFilters({ in_stock_only: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">In Stock Only</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Components Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {components.map((component) => (
            <ComponentCard
              key={component.id}
              component={component}
              isInCompare={compareList.includes(component.id)}
              onAddToCompare={() => addToCompare(component.id)}
              onRemoveFromCompare={() => removeFromCompare(component.id)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => handlePageChange(filters.page - 1)}
            disabled={filters.page === 1}
            className="btn btn-outline p-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className="text-gray-600">
            Page {filters.page} of {totalPages}
          </span>
          <button
            onClick={() => handlePageChange(filters.page + 1)}
            disabled={filters.page === totalPages}
            className="btn btn-outline p-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  )
}

interface ComponentCardProps {
  component: Component
  isInCompare: boolean
  onAddToCompare: () => void
  onRemoveFromCompare: () => void
}

function ComponentCard({
  component,
  isInCompare,
  onAddToCompare,
  onRemoveFromCompare,
}: ComponentCardProps) {
  return (
    <div className="card overflow-hidden">
      {/* Image placeholder */}
      <div className="aspect-video bg-gray-100 flex items-center justify-center">
        {component.image_url ? (
          <img
            src={component.image_url}
            alt={component.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-gray-400 text-sm">No image</span>
        )}
      </div>

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div>
            <span className="text-xs text-primary-600 font-medium">
              {component.category.name}
            </span>
            {component.is_default_for_so101 && (
              <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                Default
              </span>
            )}
          </div>
        </div>

        <h3 className="font-semibold text-gray-900 mb-1">{component.name}</h3>
        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
          {component.description}
        </p>

        {/* Price */}
        <div className="flex items-center justify-between mb-4">
          {component.lowest_price ? (
            <span className="text-lg font-bold text-gray-900">
              ${component.lowest_price.toFixed(2)}
            </span>
          ) : (
            <span className="text-sm text-gray-500">Price unavailable</span>
          )}

          {component.arm_type && (
            <span className="text-xs text-gray-500">
              {component.arm_type === 'both' ? 'Both arms' : `${component.arm_type} arm`}
            </span>
          )}
        </div>

        {/* Specifications preview */}
        <div className="text-xs text-gray-500 space-y-1 mb-4">
          {Object.entries(component.specifications || {})
            .slice(0, 3)
            .map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                <span className="font-medium text-gray-700">{String(value)}</span>
              </div>
            ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={isInCompare ? onRemoveFromCompare : onAddToCompare}
            className={clsx(
              'flex-1 btn text-sm flex items-center justify-center gap-1',
              isInCompare ? 'btn-primary' : 'btn-outline'
            )}
          >
            {isInCompare ? (
              <>
                <Check className="h-4 w-4" />
                In Compare
              </>
            ) : (
              <>
                <GitCompare className="h-4 w-4" />
                Compare
              </>
            )}
          </button>
          {component.prices?.[0]?.product_url && (
            <a
              href={component.prices[0].product_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-outline p-2"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
