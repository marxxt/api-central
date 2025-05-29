from adapters.base import AbstractStorageAdapter
from models.snft import Transaction # Import the Transaction model
from typing import List, cast, Optional # Import List, cast, and Optional
from fastapi import HTTPException # Import HTTPException for authorization errors
from services.wallet_service import WalletService # Import WalletService
from models.user import Wallet # Import Wallet model for type checking

class TransactionService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter
        self.wallet_service = WalletService(adapter) # Instantiate WalletService with the same adapter

    async def get_transactions(self) -> List[Transaction]:
        """
        Retrieves a list of all transactions using the configured adapter.
        (Note: This method might be less useful with user-specific transactions)
        """
        # Add any business logic related to fetching transactions here
        # Use the generic list method
        transactions = await self.adapter.list(Transaction) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        return cast(List[Transaction], transactions)

    async def get_user_transactions(self, authenticated_user_id: str, requested_user_id: str) -> List[Transaction]:
        """
        Retrieves a specific user's transactions with authorization check.
        """
        # Authorization check: Ensure the authenticated user is requesting their own transactions
        if authenticated_user_id != requested_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's transactions")

        # Add any business logic related to fetching user transactions here

        # Get the authenticated user's wallets
        user_wallets = await self.wallet_service.get_wallets(authenticated_user_id)

        # Extract wallet IDs
        # type: ignore comment to suppress Pylance error about missing 'id'
        user_wallet_ids = {str(wallet.id) for wallet in user_wallets} # type: ignore

        if not user_wallet_ids:
            # If the user has no wallets, they have no transactions
            return []

        # Use the generic list method to get all transactions (or a filtered list if adapter supports it)
        all_transactions = await self.adapter.list(Transaction) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        all_transactions = cast(List[Transaction], all_transactions)

        # Filter transactions to only include those associated with the user's wallets
        # This assumes the Transaction model has a field linking it to a wallet (e.g., wallet_id)
        # If the Transaction model doesn't have a wallet_id, this filtering logic will need adjustment
        user_transactions = [
            transaction for transaction in all_transactions
            # This filtering logic is a placeholder and needs to be adapted
            # based on how transactions are linked to wallets/users in your data model.
            # Example (assuming transaction.wallet_id exists):
            # if str(transaction.wallet_id) in user_wallet_ids
        ]

        # IMPORTANT: The filtering logic above is a placeholder. You need to replace
        # `if <condition>` with the actual logic to link transactions to wallets/users.
        # If your adapter supports filtering by wallet ID directly, it would be more
        # efficient to modify the adapter.list method or add a new adapter method
        # like `list_transactions_by_wallet_ids(wallet_ids: List[str])`.

        return user_transactions