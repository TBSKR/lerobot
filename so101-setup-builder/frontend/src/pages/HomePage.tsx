import { Link } from 'react-router-dom'
import { ArrowRight, Bot, Wand2, Package, GitCompare, DollarSign, FileDown } from 'lucide-react'

const features = [
  {
    icon: Wand2,
    title: 'Guided Setup Wizard',
    description: 'Answer a few questions about your experience, budget, and use case to get personalized recommendations.',
  },
  {
    icon: Package,
    title: 'Component Database',
    description: 'Browse all SO-101 compatible components with detailed specifications and real-time pricing.',
  },
  {
    icon: GitCompare,
    title: 'Side-by-Side Comparison',
    description: 'Compare up to 5 components to find the best fit for your needs.',
  },
  {
    icon: DollarSign,
    title: 'Multi-Vendor Pricing',
    description: 'See prices from AliExpress, Amazon, Waveshare, and more to find the best deals.',
  },
  {
    icon: FileDown,
    title: 'Export & Shopping Lists',
    description: 'Export your setup as PDF, JSON, or generate shopping lists with direct vendor links.',
  },
]

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-primary-100 rounded-2xl">
            <Bot className="h-16 w-16 text-primary-600" />
          </div>
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
          SO-101 Setup Builder
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Design and configure your SO-101 robot arm setup with intelligent recommendations,
          component comparison, and real-time pricing.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/wizard"
            className="btn btn-primary flex items-center justify-center gap-2 text-lg px-6 py-3"
          >
            <Wand2 className="h-5 w-5" />
            Start Building
            <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            to="/components"
            className="btn btn-outline flex items-center justify-center gap-2 text-lg px-6 py-3"
          >
            <Package className="h-5 w-5" />
            Browse Components
          </Link>
        </div>
      </div>

      {/* SO-101 Info Card */}
      <div className="card p-6 mb-16">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="md:w-1/3">
            <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
              <Bot className="h-24 w-24 text-gray-400" />
            </div>
          </div>
          <div className="md:w-2/3">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">About SO-101</h2>
            <p className="text-gray-600 mb-4">
              The SO-101 is a 6-DOF robot arm designed for learning robotics and machine learning.
              It uses Feetech STS3215 serial bus servos and is fully compatible with the LeRobot
              framework from Hugging Face.
            </p>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-900">Degrees of Freedom:</span>
                <span className="text-gray-600 ml-2">6</span>
              </div>
              <div>
                <span className="font-medium text-gray-900">Motors:</span>
                <span className="text-gray-600 ml-2">Feetech STS3215</span>
              </div>
              <div>
                <span className="font-medium text-gray-900">Control:</span>
                <span className="text-gray-600 ml-2">TTL Serial Bus</span>
              </div>
              <div>
                <span className="font-medium text-gray-900">Framework:</span>
                <span className="text-gray-600 ml-2">LeRobot</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="mb-16">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
          Everything You Need to Build
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <div key={feature.title} className="card p-6">
                <div className="p-3 bg-primary-50 rounded-lg w-fit mb-4">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            )
          })}
        </div>
      </div>

      {/* Quick Start Options */}
      <div className="card p-8 bg-gradient-to-r from-primary-50 to-blue-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Quick Start Options
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-6 border border-gray-200">
            <h3 className="font-semibold text-lg text-gray-900 mb-2">Single Arm (Follower)</h3>
            <p className="text-gray-600 text-sm mb-4">
              Start with a single follower arm for autonomous tasks. Perfect for learning
              and experimentation.
            </p>
            <ul className="text-sm text-gray-600 space-y-1 mb-4">
              <li>6x Feetech STS3215 motors (1/345 ratio)</li>
              <li>1x Waveshare Servo Driver</li>
              <li>1x 12V 5A Power Supply</li>
              <li>Estimated: ~$200-300</li>
            </ul>
            <Link to="/wizard" className="btn btn-primary w-full">
              Build Single Arm
            </Link>
          </div>
          <div className="bg-white rounded-lg p-6 border border-gray-200">
            <h3 className="font-semibold text-lg text-gray-900 mb-2">Dual Arm (Leader + Follower)</h3>
            <p className="text-gray-600 text-sm mb-4">
              Complete teleoperation setup with leader arm for data collection and
              follower arm for autonomous execution.
            </p>
            <ul className="text-sm text-gray-600 space-y-1 mb-4">
              <li>12x Feetech STS3215 motors (mixed ratios)</li>
              <li>2x Waveshare Servo Driver</li>
              <li>2x 12V 5A Power Supply</li>
              <li>Estimated: ~$400-600</li>
            </ul>
            <Link to="/wizard" className="btn btn-primary w-full">
              Build Dual Arm
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
