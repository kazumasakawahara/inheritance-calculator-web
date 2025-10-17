'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { casesApi, Case, CaseStatus } from '@/lib/cases'
import { useAuthStore } from '@/store/authStore'

export default function DashboardPage() {
  const router = useRouter()
  const { user, fetchCurrentUser, logout } = useAuthStore()
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const initialize = async () => {
      await fetchCurrentUser()
      await loadCases()
    }
    initialize()
  }, [])

  const loadCases = async () => {
    try {
      setLoading(true)
      const data = await casesApi.listCases()
      setCases(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'ケース一覧の取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  const getStatusLabel = (status: CaseStatus): string => {
    const labels: Record<CaseStatus, string> = {
      [CaseStatus.DRAFT]: '下書き',
      [CaseStatus.IN_PROGRESS]: '進行中',
      [CaseStatus.COMPLETED]: '完了',
      [CaseStatus.ARCHIVED]: 'アーカイブ',
    }
    return labels[status]
  }

  const getStatusColor = (status: CaseStatus): string => {
    const colors: Record<CaseStatus, string> = {
      [CaseStatus.DRAFT]: 'bg-gray-200 text-gray-800',
      [CaseStatus.IN_PROGRESS]: 'bg-blue-200 text-blue-800',
      [CaseStatus.COMPLETED]: 'bg-green-200 text-green-800',
      [CaseStatus.ARCHIVED]: 'bg-yellow-200 text-yellow-800',
    }
    return colors[status]
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">読み込み中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">相続計算機 Web</h1>
          <div className="flex items-center space-x-4">
            {user && (
              <span className="text-sm text-gray-600">
                {user.full_name || user.email}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              ログアウト
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">案件一覧</h2>
          <Link
            href="/cases/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            新規案件作成
          </Link>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4">
            <div className="text-sm text-red-800">{error}</div>
          </div>
        )}

        {cases.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">案件がまだありません</p>
            <Link
              href="/cases/new"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              新規案件を作成
            </Link>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {cases.map((caseItem) => (
              <Link
                key={caseItem.id}
                href={`/cases/${caseItem.id}`}
                className="block bg-white rounded-lg shadow hover:shadow-md transition p-6"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {caseItem.title}
                  </h3>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(
                      caseItem.status
                    )}`}
                  >
                    {getStatusLabel(caseItem.status)}
                  </span>
                </div>
                {caseItem.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {caseItem.description}
                  </p>
                )}
                <div className="text-xs text-gray-500">
                  更新: {new Date(caseItem.updated_at).toLocaleDateString('ja-JP')}
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
