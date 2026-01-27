import { useEffect, useState } from 'react'
import { Search, Book, ExternalLink, ChevronRight } from 'lucide-react'
import { clsx } from 'clsx'
import { docsApi } from '../api/client'

interface DocItem {
  id: number
  title: string
  slug: string
  category?: string
  tags?: string[]
  excerpt: string
}

interface DocDetail {
  id: number
  title: string
  slug: string
  content: string
  content_html?: string
  category?: string
  tags?: string[]
  source_path: string
  updated_at: string
}

const externalDocs = [
  {
    title: 'LeRobot Documentation',
    description: 'Official documentation for the LeRobot framework',
    url: 'https://huggingface.co/docs/lerobot',
  },
  {
    title: 'SO-ARM100 GitHub',
    description: 'Hardware files and BOM for SO-ARM100/SO-101',
    url: 'https://github.com/TheRobotStudio/SO-ARM100',
  },
  {
    title: 'LeRobot GitHub',
    description: 'Source code and issues for LeRobot',
    url: 'https://github.com/huggingface/lerobot',
  },
  {
    title: 'Feetech STS3215 Datasheet',
    description: 'Technical specifications for the servo motors',
    url: 'https://www.feetechrc.com/sts3215.html',
  },
]

export default function DocsPage() {
  const [docs, setDocs] = useState<DocItem[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [selectedDoc, setSelectedDoc] = useState<DocDetail | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchDocs()
    fetchCategories()
  }, [selectedCategory])

  const fetchDocs = async () => {
    setIsLoading(true)
    try {
      const params: Record<string, unknown> = {}
      if (selectedCategory) params.category = selectedCategory
      const response = await docsApi.list(params)
      setDocs(response.data.items)
    } catch (err) {
      console.error('Failed to fetch docs:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await docsApi.getCategories()
      setCategories(response.data.categories)
    } catch (err) {
      console.error('Failed to fetch categories:', err)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) {
      fetchDocs()
      return
    }

    setIsLoading(true)
    try {
      const response = await docsApi.search(searchQuery)
      setDocs(response.data.results)
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const openDoc = async (slug: string) => {
    setIsLoading(true)
    try {
      const response = await docsApi.get(slug)
      setSelectedDoc(response.data)
    } catch (err) {
      console.error('Failed to fetch doc:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar */}
        <div className="lg:w-64 flex-shrink-0">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Documentation</h1>

          {/* Search */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search docs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-9 text-sm"
              />
            </div>
          </form>

          {/* Categories */}
          <div className="mb-6">
            <h2 className="font-medium text-gray-900 mb-2">Categories</h2>
            <div className="space-y-1">
              <button
                onClick={() => setSelectedCategory(null)}
                className={clsx(
                  'w-full text-left px-3 py-2 rounded text-sm transition-colors',
                  !selectedCategory
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                )}
              >
                All
              </button>
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={clsx(
                    'w-full text-left px-3 py-2 rounded text-sm transition-colors capitalize',
                    selectedCategory === category
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {/* External Links */}
          <div>
            <h2 className="font-medium text-gray-900 mb-2">External Resources</h2>
            <div className="space-y-2">
              {externalDocs.map((doc) => (
                <a
                  key={doc.url}
                  href={doc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-3 py-2 rounded text-sm text-gray-600 hover:bg-gray-100 transition-colors"
                >
                  <ExternalLink className="h-4 w-4 flex-shrink-0" />
                  {doc.title}
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {selectedDoc ? (
            // Document viewer
            <div className="card">
              <div className="p-4 border-b border-gray-200">
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="text-sm text-primary-600 hover:underline mb-2"
                >
                  &larr; Back to list
                </button>
                <h2 className="text-xl font-bold text-gray-900">{selectedDoc.title}</h2>
                {selectedDoc.category && (
                  <span className="text-sm text-gray-500 capitalize">{selectedDoc.category}</span>
                )}
              </div>
              <div className="p-6">
                {selectedDoc.content_html ? (
                  <div
                    className="prose max-w-none"
                    dangerouslySetInnerHTML={{ __html: selectedDoc.content_html }}
                  />
                ) : (
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {selectedDoc.content}
                  </pre>
                )}
              </div>
            </div>
          ) : (
            // Document list
            <>
              {docs.length === 0 && !isLoading ? (
                <div className="card p-8 text-center">
                  <Book className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h2 className="text-lg font-medium text-gray-900 mb-2">No Documentation Found</h2>
                  <p className="text-gray-600 mb-4">
                    Documentation will be synced from the LeRobot repository.
                  </p>
                  <p className="text-sm text-gray-500">
                    Check the external resources below for official documentation.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {isLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
                    </div>
                  ) : (
                    docs.map((doc) => (
                      <button
                        key={doc.id}
                        onClick={() => openDoc(doc.slug)}
                        className="card p-4 w-full text-left hover:border-primary-300 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-medium text-gray-900">{doc.title}</h3>
                            {doc.category && (
                              <span className="text-xs text-primary-600 capitalize">
                                {doc.category}
                              </span>
                            )}
                            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                              {doc.excerpt}
                            </p>
                          </div>
                          <ChevronRight className="h-5 w-5 text-gray-400 flex-shrink-0" />
                        </div>
                      </button>
                    ))
                  )}
                </div>
              )}

              {/* External resources cards */}
              <div className="mt-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">External Resources</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  {externalDocs.map((doc) => (
                    <a
                      key={doc.url}
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="card p-4 hover:border-primary-300 transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <ExternalLink className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <h3 className="font-medium text-gray-900">{doc.title}</h3>
                          <p className="text-sm text-gray-600">{doc.description}</p>
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
