from abc import ABC, abstractmethod
from typing import List, Optional, Type, Any # Import necessary types
from pydantic import BaseModel # Import BaseModel

class AbstractStorageAdapter(ABC):
    @abstractmethod
    async def create(self, model_instance: BaseModel) -> BaseModel:
        """Creates a new record."""
        pass

    @abstractmethod
    async def read(self, model_type: Type[BaseModel], id: Any) -> Optional[BaseModel]:
        """Reads a record by ID."""
        pass

    @abstractmethod
    async def update(self, model_instance: BaseModel) -> BaseModel:
        """Updates an existing record."""
        pass

    @abstractmethod
    async def delete(self, model_type: Type[BaseModel], id: Any) -> None:
        """Deletes a record by ID."""
        pass

    @abstractmethod
    async def list(self, model_type: Type[BaseModel]) -> List[BaseModel]:
        """Lists all records of a given type."""
        pass
