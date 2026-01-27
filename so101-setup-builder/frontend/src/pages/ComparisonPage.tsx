import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Trash2, Star, DollarSign } from 'lucide-react'
import { clsx } from 'clsx'
import { useComponentStore } from '../stores/componentStore'
import { comparisonApi } from '../api/client'

interface ComparisonData {
  components: Array<{
    id: number
    name: string
    slug: string
    category_name: string
    specifications: Record<string, unknown>
    lowest_price: number | null
    is_default_for_so101: boolean
    arm_type: string | null
  }>
  specifications: Array<{
    key: string
    display_name: string
    values: Record<number, unknown>
  }>
  best_value_id: number | null
  recommended_id: number | null
  common_specs: string[]
  differing_specs: string[]
}

export default function ComparisonPage() {
  const { compareList, removeFromCompare, clearCompare } = useComponentStore()
  const [comparison, setComparison] = useState<ComparisonData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (compareList.length >= 2) {
      fetchComparison()
    }
  }, [compareList])

  const fetchComparison = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await comparisonApi.compare(compareList)
      setComparison(response.data)
    } catch (err) {
      setError('Failed to load comparison')
    } finally {
      setIsLoading(false)
    }
  }

  if (compareList.length < 2) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Compare Components</h1>
          <p className="text-gray-600 mb-6">
            Select at least 2 components to compare. You currently have {compareList.length} selected.
          </p>
          <Link to="/components" className="btn btn-primary">
            Browse Components
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link to="/components" className="btn btn-outline p-2">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Compare Components</h1>
            <p className="text-gray-600">Comparing {compareList.length} components</p>
          </div>
        </div>
        <button
          onClick={clearCompare}
          className="btn btn-outline text-red-600 hover:bg-red-50"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Clear All
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-600">{error}</p>
          <button onClick={fetchComparison} className="btn btn-primary mt-4">
            Retry
          </button>
        </div>
      ) : comparison ? (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="text-left p-4 bg-gray-50 font-medium text-gray-700 min-w-[200px]">
                  Feature
                </th>
                {comparison.components.map((component) => (
                  <th key={component.id} className="p-4 bg-gray-50 min-w-[200px]">
                    <div className="text-left">
                      <div className="flex items-center gap-2 mb-1">
                        {component.is_default_for_so101 && (
                          <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                        )}
                        {comparison.best_value_id === component.id && (
                          <DollarSign className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                      <span className="font-semibold text-gray-900">{component.name}</span>
                      <p className="text-sm text-gray-500">{component.category_name}</p>
                      <button
                        onClick={() => removeFromCompare(component.id)}
                        className="text-xs text-red-600 hover:underline mt-1"
                      >
                        Remove
                      </button>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {/* Price row */}
              <tr className="border-t border-gray-200">
                <td className="p-4 font-medium text-gray-700">Price</td>
                {comparison.components.map((component) => (
                  <td
                    key={component.id}
                    className={clsx(
                      'p-4',
                      comparison.best_value_id === component.id && 'bg-green-50'
                    )}
                  >
                    {component.lowest_price ? (
                      <span className="text-lg font-bold text-gray-900">
                        ${component.lowest_price.toFixed(2)}
                      </span>
                    ) : (
                      <span className="text-gray-500">N/A</span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Arm type row */}
              <tr className="border-t border-gray-200">
                <td className="p-4 font-medium text-gray-700">Arm Type</td>
                {comparison.components.map((component) => (
                  <td key={component.id} className="p-4 text-gray-900">
                    {component.arm_type || 'Both'}
                  </td>
                ))}
              </tr>

              {/* Specification rows */}
              {(comparison.specifications || []).map((spec) => {
                const isDifferent = (comparison.differing_specs || []).includes(spec.key)
                return (
                  <tr
                    key={spec.key}
                    className={clsx(
                      'border-t border-gray-200',
                      isDifferent && 'bg-yellow-50'
                    )}
                  >
                    <td className="p-4 font-medium text-gray-700">
                      {spec.display_name}
                      {isDifferent && (
                        <span className="ml-2 text-xs text-yellow-600">Differs</span>
                      )}
                    </td>
                    {comparison.components.map((component) => (
                      <td key={component.id} className="p-4 text-gray-900">
                        {spec.values[component.id] !== undefined
                          ? String(spec.values[component.id])
                          : '-'}
                      </td>
                    ))}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      ) : null}

      {/* Legend */}
      <div className="mt-6 flex flex-wrap gap-4 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
          <span>SO-101 Default</span>
        </div>
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4 text-green-500" />
          <span>Best Value</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-50 border border-yellow-200 rounded" />
          <span>Differing Specs</span>
        </div>
      </div>
    </div>
  )
}
