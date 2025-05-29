# data_seeding/fake_data_generators.py
import enum
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from faker import Faker
from faker_crypto import CryptoAddress
from app.models.snft import AssetType

# Assuming AssetType is defined in your types
# from your_project.types import AssetType # Adjust path as needed
# For this example, we'll use strings matching your AssetType enum values

ASSET_TYPE_VALUES = [e.value for e in list(AssetType)] if isinstance(AssetType, type) and issubclass(AssetType, enum.Enum) else [
    "SFR", "MULTIFAMILY", "OFFICE", "RETAIL", "INDUSTRIAL", "LAND",
    "AGRICULTURAL", "STORAGE", "HOTEL", "MIXED_USE"
]

def generate_user_payload(fake: Faker, existing_emails: set, existing_phones: set) -> Dict[str, Any]:
    """Generates data for a Supabase Auth user (email or phone)."""
    email = None
    phone = None

    # Try generating a unique email first
    try:
        email = fake.unique.email()
        if email in existing_emails: # Double check uniqueness locally
            email = None # Failed unique, try phone
    except: # Faker's unique can throw if it runs out of attempts
        email = None

    if email is None:
        # If email failed or not desired, try phone
        try:
            # Need to generate or format phone numbers for E.164 format
            # Faker's phone_number() often isn't E.164
            # Let's mock simple E.164: +1 followed by 10 digits
            mock_e164_phone = f"+1{random.randint(1000000000, 9999999999)}"
            # Add a check to prevent infinite loops on unique if only phone is possible
            phone_attempt_count = 0
            while mock_e164_phone in existing_phones and phone_attempt_count < 10:
                 mock_e164_phone = f"+1{random.randint(1000000000, 9999999999)}"
                 phone_attempt_count += 1

            if mock_e164_phone in existing_phones:
                print("Warning: Failed to generate unique phone number after retries.")
                # Fallback to email if phone generation is stuck
                return generate_user_payload(fake, existing_emails, existing_phones) # Recursive call (careful with depth)
            phone = mock_e164_phone

        except Exception as e:
             print(f"Error generating phone number: {e}")
             # If both failed, this user won't be creatable via Auth, let the seeder handle the error
             pass


    # Ensure at least email or phone is present
    if not email and not phone:
         # This case should ideally be rare if generation above works,
         # but we must ensure Auth creation has required fields.
         # As a final fallback, force an email if both failed.
         # Reset unique faker context for email if needed, or just generate non-unique here
         try:
            email = fake.email() # Not unique, might cause Supabase error, which is fine for seeder to catch
            print("Warning: Forced email generation as primary methods failed.")
         except Exception as e:
            print(f"Critical: Could not generate email even as fallback: {e}")
            return {} # Return empty if completely failed

    # Add the successfully generated email/phone to local sets for uniqueness tracking within this run
    if email:
        existing_emails.add(email)
    if phone:
        existing_phones.add(phone)

    # User metadata (stored in auth.users.user_metadata)
    user_metadata = {
        "display_name": fake.unique.name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "role": random.choice(["USER", "ADMIN"]),
        "avatar_url": fake.image_url(width=128, height=128), # Smaller image for avatar
        "bio": fake.sentence(),
        "website": fake.url(),
        "location": fake.city(),
        # Include other relevant metadata fields
    }

    payload: Dict[str, Any] = {
        "email": email, # Pass as top-level arg to create_user
        "phone": phone,   # Pass as top-level arg to create_user
        "user_metadata": user_metadata, # Pass metadata object
        # Password is NOT included here as we use admin creation without password
        # email_confirm / phone_confirm will be set by the seeder based on what's provided
    }

    # Remove None values before returning
    return {k: v for k, v in payload.items() if v is not None}


def generate_wallet_payload(fake: Faker, user_id: str) -> Dict[str, Any]:
    """Generates data for a 'wallets' table row."""
    fake.add_provider(CryptoAddress)
    return {
        "user_id": user_id,
        "address": fake.ethereum_address(),
        "balance": round(random.uniform(100, 10000), 2),
        "currency": random.choice(["ETH", "USDC", "USDT"]), # Allow different currencies
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def generate_reputation_payload(fake: Faker, user_id: str) -> Dict[str, Any]:
    """Generates data for a 'reputations' table row."""
    return {
        "user_id": user_id,
        "score": round(random.uniform(0, 100), 2),
        "rank": random.choice(["SSS", "SS", "S", "A", "B", "C", "D", "F"]),
        "ranking_percentile": f"{random.randint(1, 100)}%",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        # Assuming these are strings in DB
        "adjusted_staking_yield": f"{random.randint(1, 15)}%",
        "forecast_access_level": random.choice(["low", "medium", "high"])
    }

def generate_collection_payload(fake: Faker, user_id: str) -> Dict[str, Any]:
    """Generates data for a 'collections' table row."""
    return {
        "user_id": user_id,
        "name": fake.word().capitalize() + " Collection",
        "color": fake.color_name(),
        "count": random.randint(1, 50), # More items per collection
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def generate_property_payload(fake: Faker, user_id: str) -> Dict[str, Any]:
    """Generates data for a 'properties' table row."""
    valuation = round(random.uniform(500000, 20000000), 2)
    total_tokens = random.choice([1000, 5000, 10000])

    # Pick a random AssetType string from your enum or a list
    property_type = random.choice([e.value for e in list(AssetType)]) if isinstance(AssetType, type) and issubclass(AssetType, enum.Enum) else random.choice(["SFR", "MULTIFAMILY", "OFFICE", "RETAIL", "INDUSTRIAL", "LAND", "AGRICULTURAL", "STORAGE", "HOTEL", "MIXED_USE"])


    return {
        "user_id": user_id, # Link to the owner user
        "name": fake.street_name() + " Property",
        # Generate a unique token symbol, maybe add a counter or hash if Faker unique fails
        "token_symbol": fake.unique.lexify(text="????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ").upper(),
        "address": fake.address().replace('\n', ', '),
        "property_type": property_type, # Use the selected type
        "valuation": valuation,
        # Only include totalTokens if valuation > 1M to simulate fractional ownership
        "total_tokens": total_tokens if valuation > 1000000 else None,
        "apy": round(random.uniform(4.0, 10.0), 2),
        "description": fake.paragraph(nb_sentences=3),
        "image_url": fake.image_url(width=640, height=480),
        "date_listed": datetime.now(timezone.utc).isoformat(),
        "status": random.choice(["For Sale", "Auction", "Rented", "Sold"]),
        "created_at": datetime.now(timezone.utc).isoformat(),
        # Add other fields from your PropertyAsset interface if they map directly to DB columns
        "underlying_snft_id": fake.uuid4() if random.random() < 0.5 else None, # Example optional field
    }

def generate_snft_payload(fake: Faker, context: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generates data for an 'snfts' table row."""
    wallet_ids = context.get("wallet_ids", [])
    collection_ids = context.get("collection_ids", [])

    if not wallet_ids or not collection_ids:
        print("Warning: Cannot generate SNFT payload, missing wallet_ids or collection_ids context.")
        return {}

    user_ids = context.get("user_ids", []) # Get user_ids from context
    if not user_ids:
        print("Warning: Cannot generate SNFT payload, missing user_ids context.")
        return {}

    return {
        "wallet_id": random.choice(wallet_ids),
        "owner_id": random.choice(user_ids), # Added owner_id
        "name": fake.word().capitalize() + " SNFT",
        "description": fake.sentence(),
        "image_url": fake.image_url(width=400, height=400),
        "price": round(random.uniform(0.1, 10), 2), # Numeric price is better
        "currency": random.choice(["ETH", "USDC", "USDT"]), # Currency of the price
        "created_at": datetime.now(timezone.utc).isoformat(),
        "address": fake.ethereum_address(), # Contract address? Or property address? Clarify schema. Using contract for now.
        "creator": fake.name(), # Or link to user_id if creators are users
        "status": random.choice(["listed", "sold", "transferred"]),
        "category": random.choice(ASSET_TYPE_VALUES), # Link to AssetType somehow
        "collection_id": random.choice(collection_ids),
        # Add any other fields your SNFT table has
    }

def generate_auction_payload(fake: Faker, context: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Generates data for an 'auctions' table row."""
    # Context should be a list of property dictionaries with 'id' and 'user_id'
    properties_with_user = context.get("properties_with_user", [])

    if not properties_with_user:
         print("Warning: Cannot generate Auction payload, missing properties_with_user context.")
         return {}

    prop_data = random.choice(properties_with_user)
    start_time = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7)) # Some auctions in the past
    end_time = start_time + timedelta(days=random.randint(1, 14)) # Auctions last 1-14 days
    starting_price = round(random.uniform(prop_data.get("valuation", 100000) * 0.8, prop_data.get("valuation", 100000) * 1.1), 2) # Starting price based on property valuation

    return {
        "property_id": prop_data["id"],
        "seller_id": prop_data["user_id"],
        "type": random.choice(["Whole Project", "Individual Tokens"]), # Based on your schema
        "status": random.choice(["active", "pending", "closed", "completed"]), # Add more statuses
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "starting_price": starting_price, # Store as number if possible
        "created_at": datetime.now(timezone.utc).isoformat(),
        # Add other fields from your Auction schema
    }

def generate_trade_payload(fake: Faker, context: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generates data for a 'trades' table row."""
    user_ids = context.get("user_ids", [])

    if not user_ids:
        print("Warning: Cannot generate Trade payload, missing user_ids context.")
        return {}

    trade_asset = random.choice(["USDC", "ETH", "USDT"])
    trade_amount = round(random.uniform(100, 10000) if trade_asset != "ETH" else random.uniform(0.01, 5), 6) # Smaller amount for ETH

    return {
        "user_id": random.choice(user_ids),
        "asset": trade_asset,
        "type": random.choice(["buy", "sell"]),
        "amount": trade_amount,
        "executed_at": fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.utc).isoformat(), # Spread trades over time
        # Add other fields like price, pair_id, etc. if your schema has them
    }

def generate_bid_history_payload(fake: Faker, context: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generates data for a 'bid_history' table row (a single bid)."""
    auction_ids = context.get("auction_ids", [])
    user_ids = context.get("user_ids", [])

    if not auction_ids or not user_ids:
        print("Warning: Cannot generate Bid History payload, missing auction_ids or user_ids context.")
        return {}

    # Note: This generator creates bids *per call*. The seeder needs to call it multiple times per auction.
    # Or, we adjust the generator to return multiple bids for one auction. Let's adjust the seeder to call it N times per auction.
    # So, this generator is for a *single* bid.
    # If we want bids tied to specific auctions, the seeder should iterate auctions and call this.
    # The simplest is to just pick a random auction and user here if calling seeder with total bid count.
    # Let's assume context provides the lists needed for random picking.

    bid_amount = random.randint(1000, 5000) # Numeric amount is better
    bid_time = fake.date_time_between(start_date='-7d', end_date='now', tzinfo=timezone.utc)

    return {
        # This assumes seeder is called with a list of ALL auction_ids
        "auction_id": random.choice(auction_ids),
        "bidder": random.choice(user_ids), # Changed to 'bidder' to match schema
        "amount": bid_amount,
        "time": bid_time.isoformat(), # ISO format for datetime
        "timestamp": int(bid_time.timestamp() * 1000), # Unix timestamp in milliseconds
        # Add other fields like status (winning, outbid)
    }

def generate_snft_transaction_payload(fake: Faker, context: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generates data for an 'snft_transactions' table row."""
    snft_ids = context.get("snft_ids", [])

    if not snft_ids:
         print("Warning: Cannot generate SNFT Transaction payload, missing snft_ids context.")
         return {}

    tx_type = random.choice(["BUY", "SELL", "TRANSFER", "MINT"])
    tx_amount = round(random.uniform(0.1, 10), 6) # Amount of SNFT tokens or value? Assuming value for now.

    payload = {
        "snft_id": random.choice(snft_ids),
        "type": tx_type,
        "amount": tx_amount,
        "timestamp": fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.utc).isoformat(),
        # Add other fields like buyer/seller IDs, price, currency, transaction_hash etc.
    }
    # Debug print
    # Debug print
    # print(f"DEBUG: Generated SNFT transaction payload for SNFT ID {payload.get('snft_id')}: {payload}")
    return payload


def generate_dao_proposal_payload(fake: Faker, context: Any = None) -> Dict[str, Any]:
    """Generates data for a 'dao_proposals' table row."""
    # DAO proposals often don't need a user_id link directly unless they have a creator
    # Assuming ID is generated by Supabase or UUID in schema
    return {
        # "id": str(fake.uuid4()), # If UUID is generated manually
        "title": fake.sentence(nb_words=6),
        "description": fake.paragraph(nb_sentences=5),
        "created_at": fake.date_time_between(start_date='-90d', end_date='-7d', tzinfo=timezone.utc).isoformat(), # Proposals are older
        # Add other fields like status (open, closed, passed, failed), end_time etc.
    }

def generate_dao_vote_payload(fake: Faker, context: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generates data for a 'dao_votes' table row."""
    proposal_ids = context.get("proposal_ids", [])
    user_ids = context.get("user_ids", [])

    if not proposal_ids or not user_ids:
         print("Warning: Cannot generate DAO Vote payload, missing proposal_ids or user_ids context.")
         return {}

    vote_time = fake.date_time_between(start_date='-6d', end_date='now', tzinfo=timezone.utc) # Votes happen after proposal is created

    return {
        "proposal_id": random.choice(proposal_ids),
        "user_id": random.choice(user_ids),
        "vote": random.choice(["yes", "no", "abstain"]),
        "voted_at": vote_time.isoformat(),
        # Add fields like voting_power if applicable
    }