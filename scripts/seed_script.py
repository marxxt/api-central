# data_seeding/seed_script.py
import sys
import os
import random
from faker import Faker
from typing import List, Dict, Any # Import List, Dict, Any

# Add the project root directory to the Python path
# This allows absolute imports from the project root
script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the initialized clients
from scripts.supabase_config import supabase, admin_auth_client

# Import the seeder functions
from scripts.user_seeder import seed_users
from scripts.table_seeder import seed_table

# Import the data generator functions
from scripts.fake_data_generators import (
    generate_wallet_payload,
    generate_reputation_payload,
    generate_collection_payload,
    generate_property_payload,
    generate_snft_payload,          # New import
    generate_auction_payload,       # New import
    generate_trade_payload,         # New import
    generate_bid_history_payload,   # New import
    generate_snft_transaction_payload, # New import
    generate_dao_proposal_payload,  # New import
    generate_dao_vote_payload,      # New import
)

# --- Configuration ---
NUM_USERS = 20 # Increased users for more variety
NUM_WALLETS_PER_USER = 1 # Usually 1 or few
NUM_REPUTATIONS_PER_USER = 1 # Usually 1
NUM_COLLECTIONS = 10 # Increased collections
NUM_PROPERTIES = 30 # Increased properties
NUM_SNFTS = 100 # Increased SNFTs
NUM_AUCTIONS = 15 # Number of auctions
NUM_TRADES = 50 # Number of trades
NUM_DAO_PROPOSALS = 10 # Number of DAO proposals
# Bid History and SNFT Transactions count will be derived from Auctions/SNFTs respectively


# --- Initialize Faker ---
fake = Faker()

# --- Seeding Process ---
print("--- Starting Supabase Seeding Script ---")

# 1. Seed Users (Special case using admin_auth_client)
user_ids = seed_users(NUM_USERS, admin_auth_client, fake)

# Initialize all ID lists to empty lists at the top level
wallet_ids: List[str] = []
reputation_ids: List[str] = []
collection_ids: List[str] = []
property_ids: List[str] = []
snft_ids: List[str] = []
auction_ids: List[str] = []
trade_ids: List[str] = []
dao_proposal_ids: List[str] = []

# Initialize shared_context outside the conditional block
shared_context: Dict[str, Any] = {"user_ids": user_ids} # Explicitly type shared_context

if not user_ids:
    print("\n--- No users created. Skipping dependent data seeding. ---")
    # Ensure dependent ID lists are empty if no users are created
    # These are already initialized at the top, so no need to re-assign here.
else:
    # 2. Seed Wallet and Reputation (1-to-1 with users)
    print("\n--- Seeding Wallets and Reputations ---")
    for user_id in user_ids:
        # Pass individual user_id to the generator context
        wallet_ids.extend(seed_table(
            table_name="wallets",
            count=1, # Create one wallet per user
            data_generator_func=lambda f, ctx: generate_wallet_payload(f, ctx["user_id"]), # Extract user_id from context
            supabase_client=supabase,
            fake=fake,
            generator_context={"user_id": user_id} # Pass single user_id
        ))
        reputation_ids.extend(seed_table(
            table_name="reputations",
            count=1, # Create one reputation per user
            data_generator_func=lambda f, ctx: generate_reputation_payload(f, ctx["user_id"]), # Extract user_id from context
            supabase_client=supabase,
            fake=fake,
            generator_context={"user_id": user_id} # Pass single user_id
        ))
    shared_context["wallet_ids"] = wallet_ids # Update context with actual wallet IDs
    shared_context["reputation_ids"] = reputation_ids # Update context with actual reputation IDs
    print(f"Successfully created {len(wallet_ids)} wallets.")
    print(f"Successfully created {len(reputation_ids)} reputations.")

    # 3. Seed Collections (linked to random users)
    collection_ids.extend(seed_table( # Use extend as seed_table returns a list
        table_name="collections",
        count=NUM_COLLECTIONS,
        data_generator_func=lambda f, ctx: generate_collection_payload(f, random.choice(ctx["user_ids"])), # Extract random user_id from context
        supabase_client=supabase,
        fake=fake,
        generator_context=shared_context # Generator needs user_ids
    ))
    shared_context["collection_ids"] = collection_ids # Add to context for SNFTs

    # 4. Seed Properties (linked to random users)
    # Need property IDs AND user_ids for auctions later
    property_ids.extend(seed_table( # Use extend as seed_table returns a list
        table_name="properties",
        count=NUM_PROPERTIES,
        data_generator_func=lambda f, ctx: generate_property_payload(f, random.choice(ctx["user_ids"])), # Extract random user_id from context
        supabase_client=supabase,
        fake=fake,
        generator_context=shared_context # Generator needs user_ids
    ))

    # --- Step 2: Seed Entities Dependent on Core Entities ---

    # Fetch properties with user_id for auction linking
    # We need to refetch after seeding properties to get their generated IDs and linked user_ids
    print("\n--- Fetching Properties with User IDs for Dependencies ---")
    try:
        properties_with_user_result = supabase.table("properties").select("id, user_id, valuation").in_("id", property_ids).execute()
        
        if properties_with_user_result.data:
            # Ensure IDs are strings
            properties_with_user = [{"id": str(p["id"]), "user_id": str(p["user_id"]), "valuation": p["valuation"]} for p in properties_with_user_result.data]
            print(f"✅ Fetched {len(properties_with_user)} properties with user IDs.")
        else:
            print(f"⚠️ Fetching properties with user IDs returned no data.")
            properties_with_user = []
    except Exception as e:
        print(f"❌ Exception fetching properties with user IDs: {e}")
        properties_with_user = []

    # Also fetch wallets if we didn't fully capture their IDs before (table_seeder returns them, but double check)
    # Or ensure wallet_ids collected from step 2 is correct.
    # Let's assume wallet_ids from step 2 is correct and contains all created wallet IDs.

    # Update context with new required IDs
    shared_context["properties_with_user"] = properties_with_user
    # wallet_ids is already in shared_context implicitly if collected in step 2 loop,
    # but let's explicitly add it if the wallet seeding approach changed.
    shared_context["wallet_ids"] = wallet_ids # Ensure wallet_ids is in context

    # 5. Seed SNFTs (needs wallets and collections)
    if shared_context.get("wallet_ids") and shared_context.get("collection_ids"):
        snft_ids.extend(seed_table( # Use extend
            table_name="snfts",
            count=NUM_SNFTS,
            data_generator_func=generate_snft_payload,
            supabase_client=supabase,
            fake=fake,
            generator_context={**shared_context, "user_ids": shared_context["user_ids"]} # Needs wallet_ids, collection_ids, and user_ids
        ))
        shared_context["snft_ids"] = snft_ids # Add to context for transactions
    else:
        print("\n--- Skipping SNFT seeding: Not enough wallets or collections created. ---")
        snft_ids = []
        shared_context["snft_ids"] = []


    # 6. Seed Auctions (needs properties with user_id)
    if shared_context.get("properties_with_user"):
        auction_ids.extend(seed_table( # Use extend
            table_name="auctions",
            count=NUM_AUCTIONS,
            data_generator_func=generate_auction_payload,
            supabase_client=supabase,
            fake=fake,
            generator_context=shared_context # Needs properties_with_user
        ))
        shared_context["auction_ids"] = auction_ids # Add to context for bid history
    else:
        print("\n--- Skipping Auction seeding: No properties with user IDs found. ---")
        auction_ids = []
        shared_context["auction_ids"] = []


    # 7. Seed Trades (needs users)
    # No dependency on previously created *seeded* data, just needs the user_ids list
    trade_ids.extend(seed_table( # Use extend
        table_name="trades",
        count=NUM_TRADES,
        data_generator_func=generate_trade_payload,
        supabase_client=supabase,
        fake=fake,
        generator_context=shared_context # Needs user_ids
    ))

    # 8. Seed DAO Proposals (no dependencies in this simplified model)
    dao_proposal_ids.extend(seed_table( # Use extend
        table_name="dao_proposals",
        count=NUM_DAO_PROPOSALS,
        data_generator_func=generate_dao_proposal_payload,
        supabase_client=supabase,
        fake=fake,
        # No specific context needed by generator
    ))
    shared_context["proposal_ids"] = dao_proposal_ids # Add to context for votes


    # --- Step 3: Seed Entities Dependent on Step 2 Entities ---

    # 9. Seed Bid History (needs auctions and users)
    # Generate multiple bids per auction, or just a total number linked to random auctions?
    # The original script loops auctions and adds 2-5 bids. Let's do that here.
    if shared_context.get("auction_ids") and shared_context.get("user_ids"):
        print("\n--- Seeding Bid History ---")
        total_bids_seeded = 0
        # Loop through each created auction ID
        for auction_id in shared_context["auction_ids"]:
            num_bids_for_auction = random.randint(2, 5) # 2-5 bids per auction
            bids_for_auction_payloads = [
                 generate_bid_history_payload(fake, {"auction_ids": [auction_id], "user_ids": shared_context["user_ids"]}) # Pass single auction ID list and all user IDs
                 for _ in range(num_bids_for_auction)
            ]
            # Filter out any empty payloads if generator had issues
            valid_bids = [p for p in bids_for_auction_payloads if p]

            if valid_bids:
                 # Use seed_table for bulk insert of bids for THIS auction
                 seeded_bids_ids = seed_table(
                      table_name="bid_history",
                      count=len(valid_bids), # Insert the number of valid bids generated
                      data_generator_func=lambda f, ctx: valid_bids.pop(0), # Serve pre-generated payloads
                      supabase_client=supabase,
                      fake=fake,
                      generator_context=None # Not needed for this serving lambda
                  )
                 total_bids_seeded += len(seeded_bids_ids) # Track total seeded bids
        print(f"✅ Successfully seeded {total_bids_seeded} bids across {len(shared_context['auction_ids'])} auctions.")
    else:
        print("\n--- Skipping Bid History seeding: Not enough auctions or users created. ---")


    # 10. Seed SNFT Transactions (needs SNFTs)
    # Original script loops SNFTs and adds 1-3 txns. Let's do that here.
    print(f"\n--- SNFT IDs available for transactions: {len(shared_context.get('snft_ids', []))} ---") # Debug print
    if shared_context.get("snft_ids"):
        print("\n--- Seeding SNFT Transactions ---")
        total_snft_txns_seeded = 0
        # Loop through each created SNFT ID
        for snft_id in shared_context["snft_ids"]:
            num_txns_for_snft = random.randint(1, 3) # 1-3 transactions per SNFT
            txns_for_snft_payloads = [
                 generate_snft_transaction_payload(fake, {"snft_ids": [snft_id]}) # Pass single SNFT ID list
                 for _ in range(num_txns_for_snft)
            ]
            valid_txns = [p for p in txns_for_snft_payloads if p]

            if valid_txns:
                seeded_txn_ids = seed_table(
                     table_name="transactions", # Corrected table name from "snft_transactions" to "transactions"
                     count=len(valid_txns),
                     data_generator_func=lambda f, ctx: valid_txns.pop(0),
                     supabase_client=supabase,
                     fake=fake,
                     generator_context=None
                )
                total_snft_txns_seeded += len(seeded_txn_ids)
        print(f"✅ Successfully seeded {total_snft_txns_seeded} SNFT transactions across {len(shared_context['snft_ids'])} SNFTs.")
    else:
        print("\n--- Skipping SNFT Transactions seeding: No SNFTs created. ---")

    # 11. Seed DAO Votes (needs DAO Proposals and Users)
    # Original script loops users for each proposal. Let's generate vote payloads
    # for all users for all proposals and do one bulk insert.
    if shared_context.get("proposal_ids") and shared_context.get("user_ids"):
        print("\n--- Seeding DAO Votes ---")
        all_vote_payloads = []
        # For each proposal, have each user vote (simplistic model)
        for proposal_id in shared_context["proposal_ids"]:
             for user_id in shared_context["user_ids"]:
                  vote_payload = generate_dao_vote_payload(fake, {"proposal_ids": [proposal_id], "user_ids": [user_id]}) # Pass single ID lists
                  if vote_payload:
                       all_vote_payloads.append(vote_payload)

        if all_vote_payloads:
             seed_table(
                  table_name="dao_votes",
                  count=len(all_vote_payloads),
                  data_generator_func=lambda f, ctx: all_vote_payloads.pop(0),
                  supabase_client=supabase,
                  fake=fake,
                  generator_context=None
              )
        else:
            print("⚠️ No valid vote payloads generated.")

    else:
        print("\n--- Skipping DAO Votes seeding: Not enough proposals or users created. ---")


# --- Final Summary ---
print("\n--- Supabase Seeding Summary ---")
print(f"Attempted to create {NUM_USERS} users.")
print(f"Successfully created {len(user_ids)} users.")
# Use length of IDs list for success count if seed_table returns IDs
print(f"Successfully created {len(wallet_ids)} wallets.")
print(f"Successfully created {len(reputation_ids)} reputations.")
print(f"Successfully created {len(collection_ids)} collections.")
print(f"Successfully created {len(property_ids)} properties.")
print(f"Successfully created {len(snft_ids)} SNFTs.")
print(f"Successfully created {len(auction_ids)} auctions.")
print(f"Successfully created {len(trade_ids)} trades.")
print(f"Successfully created {len(dao_proposal_ids)} DAO Proposals.")
# Bid history and SNFT txns counts are printed within their seeding blocks
# DAO votes count is implicit if all_vote_payloads was used


print("\n✅ Supabase seeding script finished.")