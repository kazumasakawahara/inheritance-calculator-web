"""Case Schemas"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.case import CaseStatus, RelationshipType


# Person schemas
class PersonBase(BaseModel):
    """Base person schema"""
    name: str = Field(..., min_length=1, max_length=255)
    is_alive: bool = True
    death_date: Optional[datetime] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    is_decedent: bool = False
    is_spouse: bool = False


class PersonCreate(PersonBase):
    """Schema for creating a person"""
    pass


class PersonUpdate(BaseModel):
    """Schema for updating a person"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_alive: Optional[bool] = None
    death_date: Optional[datetime] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    is_decedent: Optional[bool] = None
    is_spouse: Optional[bool] = None


class PersonRead(PersonBase):
    """Schema for reading a person"""
    id: int
    case_id: int
    neo4j_node_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Relationship schemas
class RelationshipBase(BaseModel):
    """Base relationship schema"""
    from_person_id: int
    to_person_id: int
    relationship_type: RelationshipType
    is_biological: Optional[bool] = None
    is_adopted: Optional[bool] = None
    blood_type: Optional[str] = None


class RelationshipCreate(RelationshipBase):
    """Schema for creating a relationship"""
    pass


class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship"""
    relationship_type: Optional[RelationshipType] = None
    is_biological: Optional[bool] = None
    is_adopted: Optional[bool] = None
    blood_type: Optional[str] = None


class RelationshipRead(RelationshipBase):
    """Schema for reading a relationship"""
    id: int
    case_id: int
    neo4j_relationship_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Case schemas
class CaseBase(BaseModel):
    """Base case schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: CaseStatus = CaseStatus.DRAFT


class CaseCreate(CaseBase):
    """Schema for creating a case"""
    pass


class CaseUpdate(BaseModel):
    """Schema for updating a case"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[CaseStatus] = None


class CaseRead(CaseBase):
    """Schema for reading a case"""
    id: int
    user_id: int
    neo4j_graph_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseWithDetails(CaseRead):
    """Case with persons and relationships"""
    persons: List[PersonRead] = []
    relationships: List[RelationshipRead] = []
