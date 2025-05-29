from schema.resolvers.user_resolver import Query as UserQuery, Mutation as UserMutation
from schema.resolvers.trade_resolver import Query as TradeQuery
from schema.resolvers.auction_resolver import Query as AuctionQuery
from schema.resolvers.snft_resolver import Query as SNFTQuery
from schema.resolvers.property_resolver import Query as PropertyQuery
from schema.resolvers.reputation_resolver import Query as ReputationQuery
from schema.resolvers.wallet_resolver import Query as WalletQuery
from schema.resolvers.transaction_resolver import Query as TransactionQuery
from schema.resolvers.seller_resolver import Query as SellerQuery
from schema.resolvers.webhook_resolver import WebhookQuery, WebhookMutation # Import WebhookQuery and WebhookMutation

import strawberry
import strawberry.federation as federation # Import strawberry.federation

@strawberry.type
class Query(
    UserQuery,
    TradeQuery,
    AuctionQuery,
    SNFTQuery,
    PropertyQuery,
    ReputationQuery,
    WalletQuery,
    TransactionQuery,
    SellerQuery,
    WebhookQuery, # Add WebhookQuery
):
    pass

@strawberry.type
class Mutation(
    UserMutation,
    WebhookMutation, # Add WebhookMutation
):
    pass

# Enable Federation in the schema
# Enable Federation in the schema
schema = federation.Schema(query=Query, mutation=Mutation) # Use federation.Schema