"""Case Model for Inheritance Calculation Cases"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.user import Base


class CaseStatus(str, enum.Enum):
    """Case status enum"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Case(Base):
    """Case model for managing inheritance calculation cases"""

    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[CaseStatus] = mapped_column(
        SQLEnum(CaseStatus),
        default=CaseStatus.DRAFT,
        nullable=False,
    )

    # Foreign key to user
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )

    # Neo4j graph ID (for linking to family tree graph)
    neo4j_graph_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    # user relationship will be added when we import User model
    # For now, we use string reference to avoid circular import
    # user: Mapped["User"] = relationship("User", back_populates="cases")


class Person(Base):
    """Person model for storing individual person data"""

    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_alive: Mapped[bool] = mapped_column(default=True, nullable=False)
    death_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    birth_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Special flags
    is_decedent: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_spouse: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Neo4j node ID
    neo4j_node_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class RelationshipType(str, enum.Enum):
    """Relationship type enum"""
    CHILD_OF = "child_of"
    SPOUSE_OF = "spouse_of"
    SIBLING_OF = "sibling_of"


class PersonRelationship(Base):
    """Person relationship model for storing family relationships"""

    __tablename__ = "person_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Source and target persons
    from_person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationship type
    relationship_type: Mapped[RelationshipType] = mapped_column(
        SQLEnum(RelationshipType), nullable=False
    )

    # Additional metadata
    is_biological: Mapped[Optional[bool]] = mapped_column(nullable=True)
    is_adopted: Mapped[Optional[bool]] = mapped_column(nullable=True)
    blood_type: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # "full" or "half" for siblings

    # Neo4j relationship ID
    neo4j_relationship_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
