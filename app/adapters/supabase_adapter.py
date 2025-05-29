from supabase import create_client
from adapters.base import AbstractStorageAdapter
from config import settings
from pydantic import BaseModel
from typing import List, Optional, Type, Any

class SupabaseAdapter(AbstractStorageAdapter):
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def create(self, model_instance: BaseModel) -> BaseModel:
        """Creates a new record in Supabase."""
        table_name = model_instance.__class__.__name__.lower()
        response = self.client.table(table_name).insert(model_instance.model_dump()).execute()
        # Assuming Supabase returns the inserted data on success
        if response.data:
            return model_instance.__class__.model_validate(response.data[0])
        # Handle potential errors or no data returned
        # Check if response.error is not None
        if response.error is not None: # type: ignore
             raise Exception(f"Failed to create {table_name} record: {response.error.message}") # type: ignore
        raise Exception(f"Failed to create {table_name} record: Unknown error")


    async def read(self, model_type: Type[BaseModel], id: Any) -> Optional[BaseModel]:
        """Reads a record by ID from Supabase."""
        table_name = model_type.__name__.lower()
        response = self.client.table(table_name).select("*").eq("id", id).execute()
        if response.data:
            return model_type.model_validate(response.data[0])
        # Return None if no data is found
        return None

    async def update(self, model_instance: BaseModel) -> BaseModel:
        """Updates an existing record in Supabase."""
        table_name = model_instance.__class__.__name__.lower()
        # Assuming the model instance has an 'id' attribute for updating
        # type: ignore comment to suppress Pylance error about missing 'id'
        response = self.client.table(table_name).update(model_instance.model_dump()).eq("id", model_instance.id).execute() # type: ignore
        # Assuming Supabase returns the updated data on success
        if response.data:
            return model_instance.__class__.model_validate(response.data[0])
        # Handle potential errors or no data returned
        # Check if response.error is not None
        if response.error is not None: # type: ignore
             # type: ignore comment to suppress Pylance error about missing 'id' and 'error' attributes
             raise Exception(f"Failed to update {table_name} record with id {model_instance.id}: {response.error.message}") # type: ignore
        # type: ignore comment to suppress Pylance error about missing 'id' attribute
        raise Exception(f"Failed to update {table_name} record with id {model_instance.id}: Unknown error") # type: ignore


    async def delete(self, model_type: Type[BaseModel], id: Any) -> None:
        """Deletes a record by ID from Supabase."""
        table_name = model_type.__name__.lower()
        response = self.client.table(table_name).delete().eq("id", id).execute()
        # Optional: Check response for errors if needed
        # Check if response.error is not None
        if response.error is not None: # type: ignore
             raise Exception(f"Failed to delete {table_name} record with id {id}: {response.error.message}") # type: ignore


    async def list(self, model_type: Type[BaseModel]) -> List[BaseModel]:
        """Lists all records of a given type from Supabase."""
        table_name = model_type.__name__.lower()
        response = self.client.table(table_name).select("*").execute()
        if response.data:
            # Validate each item in the list with the specified model type
            return [model_type.model_validate(item) for item in response.data]
        # Return an empty list if no data is found
        return []
