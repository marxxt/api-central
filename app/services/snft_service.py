from adapters.base import AbstractStorageAdapter
from models.snft import SNFT
from typing import List, cast # Import cast
from fastapi import HTTPException # Import HTTPException for authorization errors
from services.wallet_service import WalletService # Import WalletService

class SnftService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter
        self.wallet_service = WalletService(adapter) # Instantiate WalletService with the same adapter

    async def get_snfts(self, authenticated_user_id: str) -> List[SNFT]:
        """
        Retrieves a list of SNFTs for the authenticated user using the configured adapter.
        """
        # Add any business logic related to fetching SNFTs here

        # Get the authenticated user's wallets
        user_wallets = await self.wallet_service.get_wallets(authenticated_user_id)

        # Extract wallet IDs
        # type: ignore comment to suppress Pylance error about missing 'id'
        user_wallet_ids = {str(wallet.id) for wallet in user_wallets} # type: ignore

        if not user_wallet_ids:
            # If the user has no wallets, they have no SNFTs
            return []

        # Use the generic list method to get all SNFTs (or a filtered list if adapter supports it)
        all_snfts = await self.adapter.list(SNFT) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        all_snfts = cast(List[SNFT], all_snfts)

        # Filter SNFTs to only include those whose wallet_id belongs to the authenticated user
        user_snfts = [
            snft for snft in all_snfts
            if str(snft.wallet_id) in user_wallet_ids # Assuming SNFT model has wallet_id
        ]

        return user_snfts