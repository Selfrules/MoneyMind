"""
Base Repository Pattern for MoneyMind v4.0

Provides abstract interface for data operations, enabling:
- Clean separation between business logic and data access
- Future migration to different backends (API, PostgreSQL, etc.)
- Consistent error handling and logging
- Type-safe operations with dataclasses
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import TypeVar, Generic, Optional, List, Dict, Any
from datetime import date, datetime


T = TypeVar("T")


@dataclass
class Entity:
    """Base entity with common fields."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary, handling dates properly."""
        result = {}
        for key, value in asdict(self).items():
            if value is None:
                continue
            if isinstance(value, (date, datetime)):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository defining common operations.

    Subclasses must implement:
    - _entity_from_dict: Convert dict to entity
    - _entity_to_dict: Convert entity to dict for storage
    """

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve a single entity by its ID."""
        pass

    @abstractmethod
    def get_all(self, **filters) -> List[T]:
        """Retrieve all entities matching optional filters."""
        pass

    @abstractmethod
    def add(self, entity: T) -> int:
        """Add a new entity and return its ID."""
        pass

    @abstractmethod
    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update an entity with given changes."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete an entity by ID."""
        pass

    @abstractmethod
    def _entity_from_dict(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to entity object."""
        pass

    @abstractmethod
    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity object to dictionary for storage."""
        pass


class RepositoryError(Exception):
    """Base exception for repository operations."""
    pass


class EntityNotFoundError(RepositoryError):
    """Raised when an entity is not found."""
    def __init__(self, entity_type: str, entity_id: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class ValidationError(RepositoryError):
    """Raised when entity validation fails."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)
