"""Case Management API Endpoints"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.auth import current_active_user
from app.db import get_async_session
from app.models import User, Case, Person, PersonRelationship
from app.schemas import (
    CaseRead,
    CaseCreate,
    CaseUpdate,
    CaseWithDetails,
    PersonRead,
    PersonCreate,
    PersonUpdate,
    RelationshipRead,
    RelationshipCreate,
    RelationshipUpdate,
)
from app.services import Neo4jService
from app.services.neo4j_service import get_neo4j_service

router = APIRouter()


# ==================== Case CRUD ====================


@router.get("/", response_model=List[CaseRead])
async def list_cases(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all cases for current user"""
    result = await session.execute(
        select(Case).where(Case.user_id == user.id).order_by(Case.updated_at.desc())
    )
    cases = result.scalars().all()
    return cases


@router.post("/", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new case"""
    case = Case(**case_data.model_dump(), user_id=user.id)
    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


@router.get("/{case_id}", response_model=CaseWithDetails)
async def get_case(
    case_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get case by ID with persons and relationships"""
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Get persons
    persons_result = await session.execute(
        select(Person).where(Person.case_id == case_id)
    )
    persons = persons_result.scalars().all()

    # Get relationships
    rels_result = await session.execute(
        select(PersonRelationship).where(PersonRelationship.case_id == case_id)
    )
    relationships = rels_result.scalars().all()

    return CaseWithDetails(
        **{k: v for k, v in case.__dict__.items() if not k.startswith("_")},
        persons=[PersonRead.model_validate(p) for p in persons],
        relationships=[RelationshipRead.model_validate(r) for r in relationships],
    )


@router.patch("/{case_id}", response_model=CaseRead)
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Update case"""
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    update_data = case_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(case, key, value)

    await session.commit()
    await session.refresh(case)
    return case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    neo4j: Neo4jService = Depends(get_neo4j_service),
):
    """Delete case and all related data"""
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Delete from Neo4j
    await neo4j.clear_case_graph(case_id)

    # Delete from PostgreSQL (cascade will handle persons and relationships)
    await session.delete(case)
    await session.commit()


# ==================== Person CRUD ====================


@router.post("/{case_id}/persons", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
async def create_person(
    case_id: int,
    person_data: PersonCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    neo4j: Neo4jService = Depends(get_neo4j_service),
):
    """Create a person in a case"""
    # Verify case ownership
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Create person in PostgreSQL
    person = Person(**person_data.model_dump(), case_id=case_id)
    session.add(person)
    await session.commit()
    await session.refresh(person)

    # Create node in Neo4j
    node_id = await neo4j.create_person_node(
        person_id=person.id,
        name=person.name,
        is_alive=person.is_alive,
        death_date=person.death_date,
        birth_date=person.birth_date,
        gender=person.gender,
        is_decedent=person.is_decedent,
        is_spouse=person.is_spouse,
    )

    # Update with Neo4j node ID
    person.neo4j_node_id = node_id
    await session.commit()
    await session.refresh(person)

    return person


@router.patch("/{case_id}/persons/{person_id}", response_model=PersonRead)
async def update_person(
    case_id: int,
    person_id: int,
    person_data: PersonUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    neo4j: Neo4jService = Depends(get_neo4j_service),
):
    """Update a person"""
    # Verify case ownership
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Get person
    person_result = await session.execute(
        select(Person).where(
            and_(Person.id == person_id, Person.case_id == case_id)
        )
    )
    person = person_result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )

    # Update PostgreSQL
    update_data = person_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(person, key, value)

    await session.commit()
    await session.refresh(person)

    # Update Neo4j
    if person.neo4j_node_id:
        await neo4j.update_person_node(person.neo4j_node_id, **update_data)

    return person


@router.delete("/{case_id}/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    case_id: int,
    person_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    neo4j: Neo4jService = Depends(get_neo4j_service),
):
    """Delete a person"""
    # Verify case ownership
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Get person
    person_result = await session.execute(
        select(Person).where(
            and_(Person.id == person_id, Person.case_id == case_id)
        )
    )
    person = person_result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )

    # Delete from Neo4j
    if person.neo4j_node_id:
        await neo4j.delete_person_node(person.neo4j_node_id)

    # Delete from PostgreSQL
    await session.delete(person)
    await session.commit()


# ==================== Relationship CRUD ====================


@router.post(
    "/{case_id}/relationships",
    response_model=RelationshipRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_relationship(
    case_id: int,
    relationship_data: RelationshipCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    neo4j: Neo4jService = Depends(get_neo4j_service),
):
    """Create a relationship between persons"""
    # Verify case ownership
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Verify both persons exist and belong to this case
    from_person_result = await session.execute(
        select(Person).where(
            and_(
                Person.id == relationship_data.from_person_id,
                Person.case_id == case_id,
            )
        )
    )
    from_person = from_person_result.scalar_one_or_none()

    to_person_result = await session.execute(
        select(Person).where(
            and_(
                Person.id == relationship_data.to_person_id,
                Person.case_id == case_id,
            )
        )
    )
    to_person = to_person_result.scalar_one_or_none()

    if not from_person or not to_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )

    # Create relationship in PostgreSQL
    relationship = PersonRelationship(
        **relationship_data.model_dump(), case_id=case_id
    )
    session.add(relationship)
    await session.commit()
    await session.refresh(relationship)

    # Create relationship in Neo4j
    if from_person.neo4j_node_id and to_person.neo4j_node_id:
        rel_id = await neo4j.create_relationship(
            from_node_id=from_person.neo4j_node_id,
            to_node_id=to_person.neo4j_node_id,
            relationship_type=relationship.relationship_type.value.upper(),
            properties={
                "is_biological": relationship.is_biological,
                "is_adopted": relationship.is_adopted,
                "blood_type": relationship.blood_type,
            },
        )
        relationship.neo4j_relationship_id = rel_id
        await session.commit()
        await session.refresh(relationship)

    return relationship


@router.delete("/{case_id}/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    case_id: int,
    relationship_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    neo4j: Neo4jService = Depends(get_neo4j_service),
):
    """Delete a relationship"""
    # Verify case ownership
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Get relationship
    rel_result = await session.execute(
        select(PersonRelationship).where(
            and_(
                PersonRelationship.id == relationship_id,
                PersonRelationship.case_id == case_id,
            )
        )
    )
    relationship = rel_result.scalar_one_or_none()

    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found"
        )

    # Delete from Neo4j
    if relationship.neo4j_relationship_id:
        await neo4j.delete_relationship(relationship.neo4j_relationship_id)

    # Delete from PostgreSQL
    await session.delete(relationship)
    await session.commit()
