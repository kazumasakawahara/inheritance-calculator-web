"""Case Management API Functions"""
import apiClient from './api'

export enum CaseStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export enum RelationshipType {
  CHILD_OF = 'child_of',
  SPOUSE_OF = 'spouse_of',
  SIBLING_OF = 'sibling_of',
}

export interface Person {
  id: number
  case_id: number
  name: string
  is_alive: boolean
  death_date?: string
  birth_date?: string
  gender?: string
  is_decedent: boolean
  is_spouse: boolean
  neo4j_node_id?: string
  created_at: string
  updated_at: string
}

export interface Relationship {
  id: number
  case_id: number
  from_person_id: number
  to_person_id: number
  relationship_type: RelationshipType
  is_biological?: boolean
  is_adopted?: boolean
  blood_type?: string
  neo4j_relationship_id?: string
  created_at: string
  updated_at: string
}

export interface Case {
  id: number
  title: string
  description?: string
  status: CaseStatus
  user_id: number
  neo4j_graph_id?: string
  created_at: string
  updated_at: string
}

export interface CaseWithDetails extends Case {
  persons: Person[]
  relationships: Relationship[]
}

export interface CreateCaseData {
  title: string
  description?: string
  status?: CaseStatus
}

export interface UpdateCaseData {
  title?: string
  description?: string
  status?: CaseStatus
}

export interface CreatePersonData {
  name: string
  is_alive?: boolean
  death_date?: string
  birth_date?: string
  gender?: string
  is_decedent?: boolean
  is_spouse?: boolean
}

export interface CreateRelationshipData {
  from_person_id: number
  to_person_id: number
  relationship_type: RelationshipType
  is_biological?: boolean
  is_adopted?: boolean
  blood_type?: string
}

export const casesApi = {
  // Case CRUD
  async listCases(): Promise<Case[]> {
    const response = await apiClient.get<Case[]>('/api/cases/')
    return response.data
  },

  async getCase(caseId: number): Promise<CaseWithDetails> {
    const response = await apiClient.get<CaseWithDetails>(`/api/cases/${caseId}`)
    return response.data
  },

  async createCase(data: CreateCaseData): Promise<Case> {
    const response = await apiClient.post<Case>('/api/cases/', data)
    return response.data
  },

  async updateCase(caseId: number, data: UpdateCaseData): Promise<Case> {
    const response = await apiClient.patch<Case>(`/api/cases/${caseId}`, data)
    return response.data
  },

  async deleteCase(caseId: number): Promise<void> {
    await apiClient.delete(`/api/cases/${caseId}`)
  },

  // Person CRUD
  async createPerson(caseId: number, data: CreatePersonData): Promise<Person> {
    const response = await apiClient.post<Person>(
      `/api/cases/${caseId}/persons`,
      data
    )
    return response.data
  },

  async updatePerson(
    caseId: number,
    personId: number,
    data: Partial<CreatePersonData>
  ): Promise<Person> {
    const response = await apiClient.patch<Person>(
      `/api/cases/${caseId}/persons/${personId}`,
      data
    )
    return response.data
  },

  async deletePerson(caseId: number, personId: number): Promise<void> {
    await apiClient.delete(`/api/cases/${caseId}/persons/${personId}`)
  },

  // Relationship CRUD
  async createRelationship(
    caseId: number,
    data: CreateRelationshipData
  ): Promise<Relationship> {
    const response = await apiClient.post<Relationship>(
      `/api/cases/${caseId}/relationships`,
      data
    )
    return response.data
  },

  async deleteRelationship(
    caseId: number,
    relationshipId: number
  ): Promise<void> {
    await apiClient.delete(
      `/api/cases/${caseId}/relationships/${relationshipId}`
    )
  },
}
