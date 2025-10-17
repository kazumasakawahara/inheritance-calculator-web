"""Neo4j Service for Family Tree Graph Management"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import ServiceUnavailable

from app.config import settings


class Neo4jService:
    """Service for managing family tree data in Neo4j"""

    def __init__(self):
        """Initialize Neo4j driver"""
        self.driver: Optional[AsyncDriver] = None

    async def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            # Verify connectivity
            await self.driver.verify_connectivity()
        except ServiceUnavailable as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")

    async def close(self):
        """Close Neo4j driver"""
        if self.driver:
            await self.driver.close()

    async def create_person_node(
        self,
        person_id: int,
        name: str,
        is_alive: bool = True,
        death_date: Optional[datetime] = None,
        birth_date: Optional[datetime] = None,
        gender: Optional[str] = None,
        is_decedent: bool = False,
        is_spouse: bool = False,
    ) -> str:
        """
        Create a person node in Neo4j
        Returns: Neo4j node ID
        """
        async with self.driver.session() as session:
            query = """
            CREATE (p:Person {
                person_id: $person_id,
                name: $name,
                is_alive: $is_alive,
                death_date: $death_date,
                birth_date: $birth_date,
                gender: $gender,
                is_decedent: $is_decedent,
                is_spouse: $is_spouse
            })
            RETURN elementId(p) as node_id
            """
            result = await session.run(
                query,
                person_id=person_id,
                name=name,
                is_alive=is_alive,
                death_date=death_date.isoformat() if death_date else None,
                birth_date=birth_date.isoformat() if birth_date else None,
                gender=gender,
                is_decedent=is_decedent,
                is_spouse=is_spouse,
            )
            record = await result.single()
            return record["node_id"]

    async def update_person_node(
        self,
        node_id: str,
        **properties: Dict[str, Any],
    ) -> bool:
        """
        Update a person node in Neo4j
        Returns: True if successful
        """
        async with self.driver.session() as session:
            # Build SET clause dynamically
            set_clauses = []
            params = {"node_id": node_id}

            for key, value in properties.items():
                if value is not None:
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    set_clauses.append(f"p.{key} = ${key}")
                    params[key] = value

            if not set_clauses:
                return True

            query = f"""
            MATCH (p:Person)
            WHERE elementId(p) = $node_id
            SET {', '.join(set_clauses)}
            RETURN p
            """
            result = await session.run(query, **params)
            record = await result.single()
            return record is not None

    async def delete_person_node(self, node_id: str) -> bool:
        """
        Delete a person node and all its relationships
        Returns: True if successful
        """
        async with self.driver.session() as session:
            query = """
            MATCH (p:Person)
            WHERE elementId(p) = $node_id
            DETACH DELETE p
            """
            await session.run(query, node_id=node_id)
            return True

    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a relationship between two persons
        Returns: Neo4j relationship ID
        """
        async with self.driver.session() as session:
            props = properties or {}
            query = f"""
            MATCH (from:Person), (to:Person)
            WHERE elementId(from) = $from_node_id AND elementId(to) = $to_node_id
            CREATE (from)-[r:{relationship_type} $props]->(to)
            RETURN elementId(r) as rel_id
            """
            result = await session.run(
                query,
                from_node_id=from_node_id,
                to_node_id=to_node_id,
                props=props,
            )
            record = await result.single()
            return record["rel_id"]

    async def delete_relationship(self, relationship_id: str) -> bool:
        """
        Delete a relationship
        Returns: True if successful
        """
        async with self.driver.session() as session:
            query = """
            MATCH ()-[r]->()
            WHERE elementId(r) = $relationship_id
            DELETE r
            """
            await session.run(query, relationship_id=relationship_id)
            return True

    async def get_family_tree(self, case_id: int) -> Dict[str, Any]:
        """
        Get complete family tree for a case
        Returns: Dict with nodes and relationships
        """
        async with self.driver.session() as session:
            # Get all persons for this case
            persons_query = """
            MATCH (p:Person {case_id: $case_id})
            RETURN elementId(p) as id, p
            """
            persons_result = await session.run(persons_query, case_id=case_id)
            persons = [
                {"id": record["id"], **dict(record["p"])}
                async for record in persons_result
            ]

            # Get all relationships
            rels_query = """
            MATCH (from:Person {case_id: $case_id})-[r]->(to:Person)
            RETURN elementId(r) as id, elementId(from) as from_id,
                   elementId(to) as to_id, type(r) as type, properties(r) as props
            """
            rels_result = await session.run(rels_query, case_id=case_id)
            relationships = [
                {
                    "id": record["id"],
                    "from_id": record["from_id"],
                    "to_id": record["to_id"],
                    "type": record["type"],
                    "properties": dict(record["props"]),
                }
                async for record in rels_result
            ]

            return {"persons": persons, "relationships": relationships}

    async def clear_case_graph(self, case_id: int) -> bool:
        """
        Clear all nodes and relationships for a case
        Returns: True if successful
        """
        async with self.driver.session() as session:
            query = """
            MATCH (p:Person {case_id: $case_id})
            DETACH DELETE p
            """
            await session.run(query, case_id=case_id)
            return True


# Global Neo4j service instance
neo4j_service = Neo4jService()


async def get_neo4j_service() -> Neo4jService:
    """Dependency for getting Neo4j service"""
    if not neo4j_service.driver:
        await neo4j_service.connect()
    return neo4j_service
