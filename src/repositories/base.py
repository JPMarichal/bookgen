"""
Base repository class with common CRUD operations
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def create(self, obj: ModelType) -> ModelType:
        """
        Create a new object
        
        Args:
            obj: Object to create
            
        Returns:
            Created object with ID
        """
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get object by ID
        
        Args:
            id: Object ID
            
        Returns:
            Object or None if not found
        """
        return self.db.get(self.model, id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all objects with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of objects
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing object
        
        Args:
            obj: Object to update
            
        Returns:
            Updated object
        """
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, obj: ModelType) -> None:
        """
        Delete an object
        
        Args:
            obj: Object to delete
        """
        self.db.delete(obj)
        self.db.commit()
    
    def delete_by_id(self, id: int) -> bool:
        """
        Delete object by ID
        
        Args:
            id: Object ID
            
        Returns:
            True if deleted, False if not found
        """
        obj = self.get_by_id(id)
        if obj:
            self.delete(obj)
            return True
        return False
    
    def count(self) -> int:
        """
        Count total objects
        
        Returns:
            Total count
        """
        stmt = select(self.model)
        result = self.db.execute(stmt)
        return len(list(result.scalars().all()))
