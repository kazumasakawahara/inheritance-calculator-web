'use client'

import { use, useEffect, useState } from 'react'
import Link from 'next/link'
import { calculateApi, CalculationResult } from '@/lib/calculate'

export default function CalculateResultPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const [result, setResult] = useState<CalculationResult | null>(null)
  const [asciiTree, setAsciiTree] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showTree, setShowTree] = useState(false)

  useEffect(() => {
    loadCalculation()
  }, [id])

  const loadCalculation = async () => {
    try {
      setLoading(true)
      const calcResult = await calculateApi.calculateInheritance(parseInt(id))
      setResult(calcResult)
    } catch (err: any) {
      setError(err.response?.data?.detail || '相続計算に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const loadAsciiTree = async () => {
    try {
      const tree = await calculateApi.getASCIITree(parseInt(id))
      setAsciiTree(tree)
      setShowTree(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || '家系図の生成に失敗しました')
    }
  }

  const formatFraction = (numerator: number, denominator: number): string => {
    return `${numerator}/${denominator}`
  }

  const formatPercentage = (percentage: number): string => {
    return `${percentage.toFixed(2)}%`
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">計算中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-2xl mx-auto p-6">
          <div className="rounded-md bg-red-50 p-4 mb-4">
            <div className="text-sm text-red-800">{error}</div>
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

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">計算結果が見つかりません</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link
            href={`/cases/${id}`}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← 案件詳細に戻る
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">相続計算結果</h1>

        {/* Decedent Info */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">被相続人</h2>
          <p className="text-gray-700">{result.decedent.name}</p>
        </div>

        {/* Heirs Table */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            相続人と相続割合
          </h2>

          {result.heirs.length === 0 ? (
            <p className="text-gray-600 text-center py-4">相続人がいません</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      氏名
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      続柄
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      順位
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      相続割合（分数）
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      相続割合（％）
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {result.heirs.map((heir, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {heir.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {heir.relationship}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {heir.rank === 0 ? '配偶者' : `第${heir.rank}順位`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {formatFraction(heir.share_numerator, heir.share_denominator)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {formatPercentage(heir.share_percentage)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Calculation Basis */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">計算根拠</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            {result.calculation_basis.map((basis, index) => (
              <li key={index}>{basis}</li>
            ))}
          </ul>
        </div>

        {/* ASCII Tree */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">家系図</h2>
            {!showTree && (
              <button
                onClick={loadAsciiTree}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
              >
                家系図を表示
              </button>
            )}
          </div>

          {showTree && asciiTree && (
            <div className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <pre className="text-sm font-mono whitespace-pre">{asciiTree}</pre>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
