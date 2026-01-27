import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Download,
  FileJson,
  ShoppingCart,
  MessageSquare,
  Send,
  Loader2,
  AlertCircle,
  CheckCircle,
  Package,
} from 'lucide-react'
import { clsx } from 'clsx'
import { useSetupStore } from '../stores/setupStore'
import { useWizardStore } from '../stores/wizardStore'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function SetupPage() {
  const { setupId } = useParams<{ setupId: string }>()
  const { profile: rawProfile, wizardCompleted } = useWizardStore()
  const {
    recommendations: rawRecommendations,
    pricing: rawPricing,
    chatHistory: rawChatHistory,
    isLoading,
    error,
    generateRecommendations,
    fetchPricing,
    sendChatMessage,
    exportPdf,
    exportJson,
    exportShoppingList,
  } = useSetupStore()

  // Ensure all objects are safely initialized to prevent undefined errors
  const profile = rawProfile || {}
  const chatHistory = Array.isArray(rawChatHistory) ? rawChatHistory : []
  const recommendations = rawRecommendations ? {
    ...rawRecommendations,
    components: Array.isArray(rawRecommendations.components) ? rawRecommendations.components : [],
    notes: Array.isArray(rawRecommendations.notes) ? rawRecommendations.notes : [],
  } : null
  const pricing = rawPricing ? {
    ...rawPricing,
    cost_by_category: rawPricing.cost_by_category || {},
  } : null

  const [chatInput, setChatInput] = useState('')
  const [activeTab, setActiveTab] = useState<'recommendations' | 'chat' | 'export'>('recommendations')

  useEffect(() => {
    if (setupId && wizardCompleted && !recommendations) {
      generateRecommendations(setupId)
      fetchPricing(setupId)
    }
  }, [setupId, wizardCompleted, recommendations, generateRecommendations, fetchPricing])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatInput.trim() || !setupId) return

    const message = chatInput
    setChatInput('')
    await sendChatMessage(setupId, message)
  }

  const handleExportPdf = async () => {
    if (!setupId) return
    try {
      const blob = await exportPdf(setupId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `so101-setup-${setupId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('PDF export failed:', err)
    }
  }

  const handleExportJson = async () => {
    if (!setupId) return
    try {
      const data = await exportJson(setupId)
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `so101-setup-${setupId}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('JSON export failed:', err)
    }
  }

  if (!wizardCompleted) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Wizard Not Complete</h1>
          <p className="text-gray-600 mb-6">
            Please complete the setup wizard first to get personalized recommendations.
          </p>
          <Link to="/wizard" className="btn btn-primary">
            Go to Wizard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Your SO-101 Setup</h1>
        <p className="text-gray-600">
          Personalized recommendations based on your profile
        </p>
      </div>

      {/* Profile Summary */}
      <div className="card p-4 mb-6">
        <h2 className="font-semibold text-gray-900 mb-3">Your Profile</h2>
        <div className="flex flex-wrap gap-4 text-sm">
          {profile.experience && (
            <div className="bg-gray-100 px-3 py-1 rounded-full">
              <span className="text-gray-600">Experience:</span>{' '}
              <span className="font-medium capitalize">{profile.experience}</span>
            </div>
          )}
          {profile.budget !== undefined && (
            <div className="bg-gray-100 px-3 py-1 rounded-full">
              <span className="text-gray-600">Budget:</span>{' '}
              <span className="font-medium">${profile.budget}</span>
            </div>
          )}
          {profile.use_case && (
            <div className="bg-gray-100 px-3 py-1 rounded-full">
              <span className="text-gray-600">Use Case:</span>{' '}
              <span className="font-medium capitalize">{profile.use_case.replace('_', ' ')}</span>
            </div>
          )}
          {profile.compute_platform && (
            <div className="bg-gray-100 px-3 py-1 rounded-full">
              <span className="text-gray-600">Compute:</span>{' '}
              <span className="font-medium uppercase">{profile.compute_platform}</span>
            </div>
          )}
          {profile.arm_type && (
            <div className="bg-gray-100 px-3 py-1 rounded-full">
              <span className="text-gray-600">Arm Type:</span>{' '}
              <span className="font-medium capitalize">{profile.arm_type}</span>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('recommendations')}
          className={clsx(
            'px-4 py-2 font-medium text-sm border-b-2 -mb-px transition-colors',
            activeTab === 'recommendations'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          )}
        >
          <Package className="h-4 w-4 inline mr-2" />
          Recommendations
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={clsx(
            'px-4 py-2 font-medium text-sm border-b-2 -mb-px transition-colors',
            activeTab === 'chat'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          )}
        >
          <MessageSquare className="h-4 w-4 inline mr-2" />
          Chat Assistant
        </button>
        <button
          onClick={() => setActiveTab('export')}
          className={clsx(
            'px-4 py-2 font-medium text-sm border-b-2 -mb-px transition-colors',
            activeTab === 'export'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          )}
        >
          <Download className="h-4 w-4 inline mr-2" />
          Export
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'recommendations' && (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Recommendations List */}
          <div className="lg:col-span-2 space-y-4">
            {isLoading && !recommendations ? (
              <div className="card p-8 text-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
                <p className="text-gray-600">Generating recommendations...</p>
              </div>
            ) : error ? (
              <div className="card p-8 text-center">
                <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 mb-4">{error}</p>
                <button
                  onClick={() => setupId && generateRecommendations(setupId)}
                  className="btn btn-primary"
                >
                  Retry
                </button>
              </div>
            ) : recommendations ? (
              <>
                {/* Summary */}
                <div className="card p-4 bg-primary-50 border-primary-200">
                  <p className="text-primary-800">{recommendations.summary}</p>
                </div>

                {/* Component List */}
                {recommendations.components.map((comp, index) => (
                  <div key={index} className="card p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span
                            className={clsx(
                              'text-xs px-2 py-0.5 rounded',
                              comp.priority === 'required'
                                ? 'bg-red-100 text-red-700'
                                : comp.priority === 'recommended'
                                ? 'bg-blue-100 text-blue-700'
                                : 'bg-gray-100 text-gray-700'
                            )}
                          >
                            {comp.priority}
                          </span>
                          <span className="text-xs text-gray-500 capitalize">{comp.category}</span>
                        </div>
                        <h3 className="font-semibold text-gray-900">{comp.component_name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{comp.reason}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-lg font-bold text-gray-900">x{comp.quantity}</span>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Notes */}
                {recommendations.notes.length > 0 && (
                  <div className="card p-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Notes</h3>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {recommendations.notes.map((note, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {note}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : null}
          </div>

          {/* Cost Breakdown */}
          <div className="space-y-4">
            <div className="card p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Estimated Cost</h3>
              {recommendations?.estimated_total ? (
                <div className="text-center mb-4">
                  <span className="text-3xl font-bold text-primary-600">
                    ${recommendations.estimated_total.toFixed(2)}
                  </span>
                  <p className="text-sm text-gray-500">Total estimated</p>
                </div>
              ) : (
                <p className="text-gray-500 text-center">Pricing data unavailable</p>
              )}

              {/* Category breakdown chart */}
              {pricing?.cost_by_category && Object.keys(pricing.cost_by_category).length > 0 && (
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={Object.entries(pricing.cost_by_category).map(([name, value]) => ({
                          name,
                          value,
                        }))}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={60}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {Object.keys(pricing.cost_by_category).map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Quick actions */}
            <div className="card p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
              <div className="space-y-2">
                <Link to="/components" className="btn btn-outline w-full justify-center">
                  Browse Components
                </Link>
                <button
                  onClick={() => setupId && generateRecommendations(setupId)}
                  disabled={isLoading}
                  className="btn btn-outline w-full justify-center"
                >
                  Refresh Recommendations
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'chat' && (
        <div className="card">
          {/* Chat messages */}
          <div className="h-96 overflow-y-auto p-4 space-y-4">
            {chatHistory.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Ask questions about your SO-101 setup</p>
                <p className="text-sm mt-2">
                  Try: "What motors do I need?" or "How do I calibrate?"
                </p>
              </div>
            ) : (
              chatHistory.map((msg, index) => (
                <div
                  key={index}
                  className={clsx(
                    'max-w-[80%] p-3 rounded-lg',
                    msg.role === 'user'
                      ? 'ml-auto bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  )}
                >
                  {msg.content}
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Thinking...
              </div>
            )}
          </div>

          {/* Chat input */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask about your setup..."
                className="input flex-1"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || isLoading}
                className="btn btn-primary px-4"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </form>
        </div>
      )}

      {activeTab === 'export' && (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="card p-6">
            <Download className="h-8 w-8 text-primary-600 mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">PDF Export</h3>
            <p className="text-sm text-gray-600 mb-4">
              Download a printable PDF with your complete setup including recommendations and pricing.
            </p>
            <button
              onClick={handleExportPdf}
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Download PDF'}
            </button>
          </div>

          <div className="card p-6">
            <FileJson className="h-8 w-8 text-primary-600 mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">JSON Export</h3>
            <p className="text-sm text-gray-600 mb-4">
              Export as JSON for use with LeRobot or other tools. Includes all configuration data.
            </p>
            <button
              onClick={handleExportJson}
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Download JSON'}
            </button>
          </div>

          <div className="card p-6">
            <ShoppingCart className="h-8 w-8 text-primary-600 mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">Shopping List</h3>
            <p className="text-sm text-gray-600 mb-4">
              Generate a shopping list with direct links to vendors for easy purchasing.
            </p>
            <button
              onClick={() => setupId && exportShoppingList(setupId)}
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Generate List'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
