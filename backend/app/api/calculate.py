"""Inheritance Calculation API Endpoints"""
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.auth import current_active_user
from app.db import get_async_session
from app.models import User, Case, Person, PersonRelationship
from app.services.calculation_service import (
    CalculationService,
    get_calculation_service,
)

router = APIRouter()


@router.post("/{case_id}/calculate")
async def calculate_inheritance(
    case_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    calc_service: CalculationService = Depends(get_calculation_service),
) -> Dict[str, Any]:
    """
    Calculate inheritance for a case

    Returns:
        Dict with calculation results including heirs and their shares
    """
    # Verify case ownership
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Get all persons
    persons_result = await session.execute(
        select(Person).where(Person.case_id == case_id)
    )
    persons = list(persons_result.scalars().all())

    if not persons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No persons found in this case",
        )

    # Find decedent
    decedent = next((p for p in persons if p.is_decedent), None)
    if not decedent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No decedent (被相続人) specified in this case",
        )

    # Get all relationships
    rels_result = await session.execute(
        select(PersonRelationship).where(PersonRelationship.case_id == case_id)
    )
    relationships = list(rels_result.scalars().all())

    # Calculate inheritance
    try:
        calc_result = calc_service.calculate_inheritance(
            persons=persons,
            relationships=relationships,
            decedent_id=decedent.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}",
        )

    # Get summary
    summary = calc_service.get_calculation_summary(calc_result)

    return summary


@router.get("/{case_id}/ascii-tree")
async def get_ascii_tree(
    case_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    calc_service: CalculationService = Depends(get_calculation_service),
) -> Dict[str, str]:
    """
    Get ASCII family tree for a case

    Returns:
        Dict with ASCII tree string
    """
    # Verify case ownership
    result = await session.execute(
        select(Case).where(and_(Case.id == case_id, Case.user_id == user.id))
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Get all persons
    persons_result = await session.execute(
        select(Person).where(Person.case_id == case_id)
    )
    persons = list(persons_result.scalars().all())

    if not persons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No persons found in this case",
        )

    # Find decedent
    decedent = next((p for p in persons if p.is_decedent), None)
    if not decedent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No decedent (被相続人) specified in this case",
        )

    # Get all relationships
    rels_result = await session.execute(
        select(PersonRelationship).where(PersonRelationship.case_id == case_id)
    )
    relationships = list(rels_result.scalars().all())

    # Calculate inheritance first
    try:
        calc_result = calc_service.calculate_inheritance(
            persons=persons,
            relationships=relationships,
            decedent_id=decedent.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}",
        )

    # Generate ASCII tree
    try:
        ascii_tree = calc_service.generate_ascii_tree(calc_result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ASCII tree generation failed: {str(e)}",
        )

    return {"ascii_tree": ascii_tree}
