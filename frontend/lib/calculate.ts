/**
 * Calculation API Functions
 */
import apiClient from './api'

export interface Heir {
  id: string
  name: string
  relationship: string
  rank: number
  share_numerator: number
  share_denominator: number
  share_decimal: number
  share_percentage: number
}

export interface CalculationResult {
  decedent: {
    id: string
    name: string
  }
  heirs: Heir[]
  has_spouse: boolean
  has_children: boolean
  calculation_basis: string[]
}

export interface ASCIITreeResponse {
  ascii_tree: string
}

export const calculateApi = {
  async calculateInheritance(caseId: number): Promise<CalculationResult> {
    const response = await apiClient.post<CalculationResult>(
      `/api/cases/${caseId}/calculate`
    )
    return response.data
  },

  async getASCIITree(caseId: number): Promise<string> {
    const response = await apiClient.get<ASCIITreeResponse>(
      `/api/cases/${caseId}/ascii-tree`
    )
    return response.data.ascii_tree
  },
}
