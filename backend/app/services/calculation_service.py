"""Inheritance Calculation Service using inheritance-calculator-core"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from inheritance_calculator_core.models import (
    Person as CorePerson,
    Relationship as CoreRelationship,
    RelationshipType as CoreRelationshipType,
)
from inheritance_calculator_core.calculator import InheritanceCalculator
from inheritance_calculator_core.models.result import InheritanceResult

from app.models import Person, PersonRelationship, RelationshipType


class CalculationService:
    """Service for calculating inheritance using core library"""

    def __init__(self):
        """Initialize calculation service"""
        self.calculator = InheritanceCalculator()

    def _convert_to_core_person(self, person: Person) -> CorePerson:
        """Convert web Person model to core Person model"""
        return CorePerson(
            id=str(person.id),
            name=person.name,
            is_alive=person.is_alive,
            death_date=person.death_date,
            birth_date=person.birth_date,
            gender=person.gender,
        )

    def _convert_relationship_type(
        self, rel_type: RelationshipType
    ) -> CoreRelationshipType:
        """Convert web RelationshipType to core RelationshipType"""
        mapping = {
            RelationshipType.CHILD_OF: CoreRelationshipType.CHILD_OF,
            RelationshipType.SPOUSE_OF: CoreRelationshipType.SPOUSE_OF,
            RelationshipType.SIBLING_OF: CoreRelationshipType.SIBLING_OF,
        }
        return mapping[rel_type]

    def _convert_to_core_relationship(
        self,
        relationship: PersonRelationship,
        persons_map: Dict[int, CorePerson],
    ) -> CoreRelationship:
        """Convert web PersonRelationship to core Relationship"""
        return CoreRelationship(
            from_person=persons_map[relationship.from_person_id],
            to_person=persons_map[relationship.to_person_id],
            relationship_type=self._convert_relationship_type(
                relationship.relationship_type
            ),
            is_biological=relationship.is_biological,
            is_adopted=relationship.is_adopted,
            blood_type=relationship.blood_type,
        )

    def calculate_inheritance(
        self,
        persons: List[Person],
        relationships: List[PersonRelationship],
        decedent_id: int,
    ) -> InheritanceResult:
        """
        Calculate inheritance for a case

        Args:
            persons: List of Person models
            relationships: List of PersonRelationship models
            decedent_id: ID of the decedent (被相続人)

        Returns:
            InheritanceResult from core library
        """
        # Convert persons to core models
        persons_map: Dict[int, CorePerson] = {}
        core_persons: List[CorePerson] = []

        for person in persons:
            core_person = self._convert_to_core_person(person)
            persons_map[person.id] = core_person
            core_persons.append(core_person)

        # Convert relationships to core models
        core_relationships: List[CoreRelationship] = []
        for relationship in relationships:
            core_rel = self._convert_to_core_relationship(relationship, persons_map)
            core_relationships.append(core_rel)

        # Find decedent
        decedent = persons_map.get(decedent_id)
        if not decedent:
            raise ValueError(f"Decedent with ID {decedent_id} not found")

        # Calculate inheritance
        result = self.calculator.calculate(
            decedent=decedent,
            persons=core_persons,
            relationships=core_relationships,
        )

        return result

    def get_calculation_summary(
        self, result: InheritanceResult
    ) -> Dict[str, Any]:
        """
        Get a summary of calculation results

        Args:
            result: InheritanceResult from calculation

        Returns:
            Dict with summary information
        """
        summary = {
            "decedent": {
                "id": result.decedent.id,
                "name": result.decedent.name,
            },
            "heirs": [
                {
                    "id": heir.person.id,
                    "name": heir.person.name,
                    "relationship": heir.relationship,
                    "rank": heir.rank,
                    "share_numerator": heir.share.numerator,
                    "share_denominator": heir.share.denominator,
                    "share_decimal": float(heir.share.numerator) / float(heir.share.denominator),
                    "share_percentage": (
                        float(heir.share.numerator) / float(heir.share.denominator) * 100
                    ),
                }
                for heir in result.heirs
            ],
            "has_spouse": result.has_spouse,
            "has_children": result.has_children,
            "calculation_basis": result.calculation_basis,
        }

        return summary

    def generate_ascii_tree(self, result: InheritanceResult) -> str:
        """
        Generate ASCII family tree

        Args:
            result: InheritanceResult from calculation

        Returns:
            ASCII art family tree string
        """
        from inheritance_calculator_core.output.ascii_tree import ASCIITreeGenerator

        generator = ASCIITreeGenerator()
        tree = generator.generate(result)
        return tree


# Global calculation service instance
calculation_service = CalculationService()


def get_calculation_service() -> CalculationService:
    """Dependency for getting calculation service"""
    return calculation_service
