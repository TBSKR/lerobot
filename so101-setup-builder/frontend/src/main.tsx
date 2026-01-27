console.log('[SO101] Starting app...')

import React from 'react'
console.log('[SO101] React loaded')

import ReactDOM from 'react-dom/client'
console.log('[SO101] ReactDOM loaded')

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
console.log('[SO101] React Query loaded')

import { ErrorBoundary } from './components/ErrorBoundary'
console.log('[SO101] ErrorBoundary loaded')

import App from './App'
console.log('[SO101] App loaded')

import './index.css'
console.log('[SO101] CSS loaded')

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)
