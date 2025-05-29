from adapters.base import AbstractStorageAdapter
from models.user import Wallet # Import the Wallet model
from typing import List, cast # Import cast
from fastapi import HTTPException # Import HTTPException for authorization errors

class WalletService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter

    async def get_wallets(self, authenticated_user_id: str) -> List[Wallet]:
        """
        Retrieves a list of wallets for the authenticated user using the configured adapter.
        """
        # Add any business logic related to fetching wallets here
        # Use the generic list method to get all wallets (or a filtered list if adapter supports it)
        all_wallets = await self.adapter.list(Wallet) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        all_wallets = cast(List[Wallet], all_wallets)

        # Filter wallets to only include those belonging to the authenticated user
        user_wallets = [wallet for wallet in all_wallets if str(wallet.user_id) == authenticated_user_id] # type: ignore # Assuming Wallet model has user_id

        return user_wallets