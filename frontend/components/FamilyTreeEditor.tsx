'use client'

import { useCallback, useState } from 'react'
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'

import { Person, Relationship, RelationshipType } from '@/lib/cases'

interface FamilyTreeEditorProps {
  persons: Person[]
  relationships: Relationship[]
  onAddPerson: (person: Partial<Person>) => void
  onUpdatePerson: (personId: number, data: Partial<Person>) => void
  onDeletePerson: (personId: number) => void
  onAddRelationship: (relationship: Partial<Relationship>) => void
  onDeleteRelationship: (relationshipId: number) => void
}

export default function FamilyTreeEditor({
  persons,
  relationships,
  onAddPerson,
  onUpdatePerson,
  onDeletePerson,
  onAddRelationship,
  onDeleteRelationship,
}: FamilyTreeEditorProps) {
  // Convert persons to React Flow nodes
  const initialNodes: Node[] = persons.map((person, index) => ({
    id: person.id.toString(),
    type: 'default',
    data: {
      label: (
        <div className="text-center">
          <div className="font-bold">{person.name}</div>
          <div className="text-xs text-gray-600">
            {person.is_decedent && '被相続人'}
            {person.is_spouse && '配偶者'}
          </div>
          <div className="text-xs">
            {person.is_alive ? '存命' : '死亡'}
          </div>
        </div>
      ),
    },
    position: { x: (index % 3) * 250, y: Math.floor(index / 3) * 150 },
    style: {
      background: person.is_decedent
        ? '#fee2e2'
        : person.is_spouse
        ? '#ede9fe'
        : person.is_alive
        ? '#dcfce7'
        : '#f3f4f6',
      border: '2px solid',
      borderColor: person.is_decedent
        ? '#dc2626'
        : person.is_spouse
        ? '#7c3aed'
        : person.is_alive
        ? '#16a34a'
        : '#6b7280',
      borderRadius: '8px',
      padding: '10px',
      minWidth: '150px',
    },
  }))

  // Convert relationships to React Flow edges
  const initialEdges: Edge[] = relationships.map((rel) => ({
    id: rel.id.toString(),
    source: rel.from_person_id.toString(),
    target: rel.to_person_id.toString(),
    label: getRelationshipLabel(rel.relationship_type),
    type: 'smoothstep',
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
    style: { stroke: '#64748b', strokeWidth: 2 },
    labelStyle: { fontSize: 12, fill: '#475569' },
    labelBgStyle: { fill: '#f1f5f9' },
  }))

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const onConnect = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) return

      const newEdge = {
        ...connection,
        type: 'smoothstep',
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
      }

      setEdges((eds) => addEdge(newEdge, eds))

      // Create relationship in backend
      onAddRelationship({
        from_person_id: parseInt(connection.source),
        to_person_id: parseInt(connection.target),
        relationship_type: RelationshipType.CHILD_OF,
      })
    },
    [setEdges, onAddRelationship]
  )

  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.id)
  }, [])

  const handlePaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  return (
    <div className="h-screen w-full">
      <div className="h-full flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b p-4 flex items-center space-x-4">
          <h2 className="text-lg font-semibold">家系図エディター</h2>
          <button
            onClick={() => {
              const newPerson: Partial<Person> = {
                name: '新しい人物',
                is_alive: true,
                is_decedent: false,
                is_spouse: false,
              }
              onAddPerson(newPerson)
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            人物を追加
          </button>
          {selectedNode && (
            <button
              onClick={() => {
                onDeletePerson(parseInt(selectedNode))
                setSelectedNode(null)
              }}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              選択した人物を削除
            </button>
          )}
        </div>

        {/* React Flow Canvas */}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={handleNodeClick}
            onPaneClick={handlePaneClick}
            fitView
          >
            <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
            <Controls />
          </ReactFlow>
        </div>

        {/* Instructions */}
        <div className="bg-gray-50 border-t p-4 text-sm text-gray-600">
          <p>
            <strong>使い方:</strong>
            ノードをドラッグして移動 | ノードをクリックして選択 |
            ノードのハンドルをドラッグして関係性を作成
          </p>
        </div>
      </div>
    </div>
  )
}

function getRelationshipLabel(type: RelationshipType): string {
  const labels: Record<RelationshipType, string> = {
    [RelationshipType.CHILD_OF]: '子',
    [RelationshipType.SPOUSE_OF]: '配偶者',
    [RelationshipType.SIBLING_OF]: '兄弟姉妹',
  }
  return labels[type] || type
}
