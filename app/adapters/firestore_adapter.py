from google.cloud.firestore_v1 import AsyncClient
from adapters.base import AbstractStorageAdapter
from pydantic import BaseModel
from typing import List, Optional, Type, Any
from strawberry import ID # Keep ID import if used by models

class FirestoreAdapter(AbstractStorageAdapter):
    def __init__(self):
        # Initialize Firestore client. Project ID is typically inferred from the environment.
        self.client = AsyncClient()

    async def create(self, model_instance: BaseModel) -> BaseModel:
        """Creates a new record in Firestore."""
        collection_name = model_instance.__class__.__name__.lower()
        # Add a new document with a Firestore-generated ID
        doc_ref = await self.client.collection(collection_name).add(model_instance.model_dump())
        # Retrieve the created document to get the generated ID and full data
        doc = await doc_ref[0].get() # add() returns a tuple (DocumentReference, dict)
        if doc.exists:
            # Update the model instance with the generated ID before returning
            created_data = doc.to_dict()
            if created_data is not None: # Check if data is not None
                created_data['id'] = doc.id # Assuming Pydantic model has an 'id' field
                return model_instance.__class__.model_validate(created_data)
        raise Exception(f"Failed to create {collection_name} record.")

    async def read(self, model_type: Type[BaseModel], id: Any) -> Optional[BaseModel]:
        """Reads a record by ID from Firestore."""
        collection_name = model_type.__name__.lower()
        doc_ref = self.client.collection(collection_name).document(str(id)) # Ensure ID is string
        doc = await doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data is not None: # Check if data is not None
                data['id'] = doc.id # Include document ID in data
                return model_type.model_validate(data)
        return None

    async def update(self, model_instance: BaseModel) -> BaseModel:
        """Updates an existing record in Firestore."""
        collection_name = model_instance.__class__.__name__.lower()
        # Assuming the model instance has an 'id' attribute
        # type: ignore comment to suppress Pylance error about missing 'id'
        doc_ref = self.client.collection(collection_name).document(str(model_instance.id)) # type: ignore
        # Use set with merge=True to update fields without overwriting
        await doc_ref.set(model_instance.model_dump(), merge=True)
        # Retrieve the updated document to return the latest state
        doc = await doc_ref.get()
        if doc.exists:
             updated_data = doc.to_dict()
             if updated_data is not None: # Check if data is not None
                 updated_data['id'] = doc.id # Include document ID in data
                 return model_instance.__class__.model_validate(updated_data)
        # type: ignore comment to suppress Pylance error about missing 'id' attribute
        raise Exception(f"Failed to retrieve updated {collection_name} record with id {model_instance.id}.") # type: ignore


    async def delete(self, model_type: Type[BaseModel], id: Any) -> None:
        """Deletes a record by ID from Firestore."""
        collection_name = model_type.__name__.lower()
        doc_ref = self.client.collection(collection_name).document(str(id)) # Ensure ID is string
        await doc_ref.delete()


    async def list(self, model_type: Type[BaseModel]) -> List[BaseModel]:
        """Lists all records of a given type from Firestore."""
        collection_name = model_type.__name__.lower()
        stream = self.client.collection(collection_name).stream()
        items = []
        async for doc in stream:
            data = doc.to_dict()
            if data is not None: # Check if data is not None
                data['id'] = doc.id # Include document ID in data
                items.append(model_type.model_validate(data))
        return items
