'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { casesApi, CaseWithDetails, Person, Relationship } from '@/lib/cases'

// Dynamically import React Flow to avoid SSR issues
const FamilyTreeEditor = dynamic(
  () => import('@/components/FamilyTreeEditor'),
  {
    ssr: false,
    loading: () => <div className="h-screen flex items-center justify-center">読み込み中...</div>,
  }
)

export default function FamilyTreeEditorPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
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

  const handleAddPerson = async (personData: Partial<Person>) => {
    try {
      await casesApi.createPerson(parseInt(id), personData as any)
      await loadCase() // Reload to get updated data
    } catch (err: any) {
      setError(err.response?.data?.detail || '人物の追加に失敗しました')
    }
  }

  const handleUpdatePerson = async (
    personId: number,
    data: Partial<Person>
  ) => {
    try {
      await casesApi.updatePerson(parseInt(id), personId, data as any)
      await loadCase()
    } catch (err: any) {
      setError(err.response?.data?.detail || '人物の更新に失敗しました')
    }
  }

  const handleDeletePerson = async (personId: number) => {
    try {
      await casesApi.deletePerson(parseInt(id), personId)
      await loadCase()
    } catch (err: any) {
      setError(err.response?.data?.detail || '人物の削除に失敗しました')
    }
  }

  const handleAddRelationship = async (
    relationshipData: Partial<Relationship>
  ) => {
    try {
      await casesApi.createRelationship(parseInt(id), relationshipData as any)
      await loadCase()
    } catch (err: any) {
      setError(err.response?.data?.detail || '関係性の追加に失敗しました')
    }
  }

  const handleDeleteRelationship = async (relationshipId: number) => {
    try {
      await casesApi.deleteRelationship(parseInt(id), relationshipId)
      await loadCase()
    } catch (err: any) {
      setError(err.response?.data?.detail || '関係性の削除に失敗しました')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">読み込み中...</div>
      </div>
    )
  }

  if (error || !caseData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-2xl mx-auto p-6">
          <div className="rounded-md bg-red-50 p-4 mb-4">
            <div className="text-sm text-red-800">{error || '案件が見つかりません'}</div>
          </div>
          <Link
            href={`/cases/${id}`}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← 案件詳細に戻る
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link
              href={`/cases/${id}`}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              ← 戻る
            </Link>
            <h1 className="text-xl font-bold text-gray-900">
              {caseData.title} - 家系図エディター
            </h1>
          </div>
          <Link
            href={`/cases/${id}/calculate`}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            相続計算
          </Link>
        </div>
      </header>

      {/* Editor */}
      <div className="flex-1">
        <FamilyTreeEditor
          persons={caseData.persons}
          relationships={caseData.relationships}
          onAddPerson={handleAddPerson}
          onUpdatePerson={handleUpdatePerson}
          onDeletePerson={handleDeletePerson}
          onAddRelationship={handleAddRelationship}
          onDeleteRelationship={handleDeleteRelationship}
        />
      </div>
    </div>
  )
}
