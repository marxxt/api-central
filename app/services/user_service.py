from adapters.base import AbstractStorageAdapter
from models.user import User
from typing import Optional
from fastapi import HTTPException # Import HTTPException for authorization errors

class UserService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter

    async def get_user(self, authenticated_user_id: str, requested_user_id: str) -> Optional[User]:
        """
        Retrieves a user by their ID using the configured adapter, with authorization check.
        """
        # Authorization check: Ensure the authenticated user is requesting their own data
        if authenticated_user_id != requested_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's data")

        # Add any business logic related to fetching a user here
        # Use the generic read method
        user = await self.adapter.read(User, requested_user_id)
        # The read method returns BaseModel or None, ensure it's a User if not None
        return user if isinstance(user, User) else None

    async def create_user(self, user: User) -> User:
        """
        Creates a new user using the configured adapter.
        (Authorization for creation might be handled differently, e.g., public signup)
        """
        # Add any business logic related to creating a user here
        # Use the generic create method
        created_user = await self.adapter.create(user)
        # Explicitly cast the result to the expected type for the type checker
        return created_user # type: ignore


    async def update_user(self, authenticated_user_id: str, user: User) -> User:
        """
        Updates an existing user using the configured adapter, with authorization check.
        """
        # Authorization check: Ensure the authenticated user is updating their own data
        # Assuming the User model instance has an 'id' attribute
        # type: ignore comment to suppress Pylance error about missing 'id'
        if authenticated_user_id != str(user.id): # type: ignore
            raise HTTPException(status_code=403, detail="Not authorized to update this user's data")

        # Add any business logic related to updating a user here
        # Use the generic update method
        updated_user = await self.adapter.update(user)
        # Explicitly cast the result to the expected type for the type checker
        return updated_user # type: ignore

    async def delete_user(self, authenticated_user_id: str, user_id: str) -> None:
        """
        Deletes a user using the configured adapter, with authorization check.
        """
        # Authorization check: Ensure the authenticated user is deleting their own profile
        if authenticated_user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this user's profile")

        # Add any business logic related to deleting a user here
        # Use the generic delete method
        await self.adapter.delete(User, user_id)