'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { casesApi, CaseWithDetails, CaseStatus } from '@/lib/cases'

export default function CaseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const [caseData, setCaseData] = useState<CaseWithDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadCase()
  }, [id])

  const loadCase = async () => {
    try {
      setLoading(true)
      const data = await casesApi.getCase(parseInt(id))
      setCaseData(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '案件の取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('この案件を削除しますか？')) return

    try {
      await casesApi.deleteCase(parseInt(id))
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || '案件の削除に失敗しました')
    }
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">読み込み中...</div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">案件が見つかりません</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link
              href="/dashboard"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              ← ダッシュボードに戻る
            </Link>
            <div className="flex space-x-2">
              <button
                onClick={handleDelete}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700"
              >
                削除
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4">
            <div className="text-sm text-red-800">{error}</div>
          </div>
        )}

        {/* Case Info */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {caseData.title}
              </h1>
              <span className="px-3 py-1 text-sm font-medium rounded bg-blue-200 text-blue-800">
                {getStatusLabel(caseData.status)}
              </span>
            </div>
            <Link
              href={`/cases/${id}/calculate`}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              相続計算
            </Link>
          </div>

          {caseData.description && (
            <p className="text-gray-600 mb-4">{caseData.description}</p>
          )}

          <div className="text-sm text-gray-500">
            <div>作成: {new Date(caseData.created_at).toLocaleString('ja-JP')}</div>
            <div>更新: {new Date(caseData.updated_at).toLocaleString('ja-JP')}</div>
          </div>
        </div>

        {/* Persons Section */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">登録人物</h2>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm">
              人物を追加
            </button>
          </div>

          {caseData.persons.length === 0 ? (
            <p className="text-gray-600 text-center py-4">
              登録された人物がありません
            </p>
          ) : (
            <div className="space-y-2">
              {caseData.persons.map((person) => (
                <div
                  key={person.id}
                  className="flex justify-between items-center p-4 border border-gray-200 rounded-lg"
                >
                  <div>
                    <div className="font-medium text-gray-900">
                      {person.name}
                      {person.is_decedent && (
                        <span className="ml-2 px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                          被相続人
                        </span>
                      )}
                      {person.is_spouse && (
                        <span className="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                          配偶者
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600">
                      {person.is_alive ? '存命' : '死亡'}
                      {person.birth_date && ` | 生年月日: ${new Date(person.birth_date).toLocaleDateString('ja-JP')}`}
                    </div>
                  </div>
                  <button className="text-sm text-red-600 hover:text-red-700">
                    削除
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Relationships Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">関係性</h2>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm">
              関係性を追加
            </button>
          </div>

          {caseData.relationships.length === 0 ? (
            <p className="text-gray-600 text-center py-4">
              登録された関係性がありません
            </p>
          ) : (
            <div className="space-y-2">
              {caseData.relationships.map((rel) => {
                const fromPerson = caseData.persons.find(
                  (p) => p.id === rel.from_person_id
                )
                const toPerson = caseData.persons.find(
                  (p) => p.id === rel.to_person_id
                )

                const relationshipLabel: Record<string, string> = {
                  child_of: 'の子',
                  spouse_of: 'の配偶者',
                  sibling_of: 'の兄弟姉妹',
                }

                return (
                  <div
                    key={rel.id}
                    className="flex justify-between items-center p-4 border border-gray-200 rounded-lg"
                  >
                    <div className="text-gray-900">
                      {fromPerson?.name} → {toPerson?.name}
                      <span className="ml-2 text-gray-600">
                        ({relationshipLabel[rel.relationship_type] || rel.relationship_type})
                      </span>
                    </div>
                    <button className="text-sm text-red-600 hover:text-red-700">
                      削除
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
