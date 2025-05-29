import strawberry
from schema.types.wallet_type import WalletType
from services.wallet_service import WalletService # Import the WalletService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    # Access context via info argument
    async def wallets(self, info: Info) -> list[WalletType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        wallet_service = WalletService(adapter) # Instantiate the service
        # Pass the authenticated_user_id to the service method
        wallets = await wallet_service.get_wallets(authenticated_user_id) # Call the service method
        # Map the list of Wallet models to WalletType
        # Manually map the list of Wallet models to WalletType
        return [WalletType(**wallet.model_dump()) for wallet in wallets]