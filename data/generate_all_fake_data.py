# data/generate_all_fake_data.py

import os
import uuid # Added import for uuid
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

from db_utils import supabase_admin  # <-- Reuse centralized config

# Import individual data generation modules
from data_generators.users_generator import generate_fake_users, insert_fake_users
from data_generators.wallets_generator import generate_fake_wallets, insert_fake_wallets
from data_generators.db_collections_generator import generate_fake_collections, insert_fake_collections
from data_generators.properties_generator import generate_fake_properties, insert_fake_properties
from data_generators.daos_generator import generate_fake_daos, insert_fake_daos
from data_generators.snfts_generator import generate_fake_snfts, insert_fake_snfts
from data_generators.auctions_generator import generate_fake_auctions, insert_fake_auctions
from data_generators.trades_generator import generate_fake_trades, insert_fake_trades
from data_generators.trading_pairs_generator import generate_fake_trading_pairs, insert_fake_trading_pairs
from data_generators.ai_bot_configs_generator import generate_fake_ai_bot_configs, insert_fake_ai_bot_configs
from data_generators.orders_generator import generate_fake_orders, insert_fake_orders
from data_generators.user_investments_generator import generate_fake_user_investments, insert_fake_user_investments
from data_generators.bid_history_generator import generate_fake_bid_history, insert_fake_bid_history
from data_generators.transactions_generator import generate_fake_transactions, insert_fake_transactions
from data_generators.dao_proposals_generator import generate_fake_dao_proposals, insert_fake_dao_proposals
from data_generators.dao_votes_generator import generate_fake_dao_votes, insert_fake_dao_votes
from data_generators.user_stats_generator import generate_fake_user_stats, insert_fake_user_stats
from data_generators.snft_stats_generator import generate_fake_snft_stats, insert_fake_snft_stats
from data_generators.platform_metrics_generator import generate_fake_platform_metrics, insert_fake_platform_metrics
from data_generators.property_token_ownership_generator import generate_fake_property_token_ownership, insert_fake_property_token_ownership
from data_generators.property_token_transfers_generator import generate_fake_property_token_transfers, insert_fake_property_token_transfers
from data_generators.contractors_generator import generate_fake_contractors, insert_fake_contractors
from data_generators.dao_members_generator import generate_fake_dao_members, insert_fake_dao_members
from data_generators.dao_managers_generator import generate_fake_dao_managers, insert_fake_dao_managers
from data_generators.dao_contractors_generator import generate_fake_dao_contractors, insert_fake_dao_contractors
from data_generators.dao_token_holdings_generator import generate_fake_dao_token_holdings, insert_fake_dao_token_holdings
from data_generators.snft_balances_generator import generate_fake_snft_balances, insert_fake_snft_balances
from data_generators.snft_mint_events_generator import generate_fake_snft_mint_events, insert_fake_snft_mint_events
from data_generators.snft_events_generator import generate_fake_snft_events, insert_fake_snft_events
from data_generators.snft_metadata_retry_queue_generator import generate_fake_snft_metadata_retry_queue, insert_fake_snft_metadata_retry_queue
from data_generators.favorites_generator import generate_fake_favorites, insert_fake_favorites
from data_generators.stars_generator import generate_fake_stars, insert_fake_stars
from data_generators.comments_generator import generate_fake_comments, insert_fake_comments
from data_generators.shares_generator import generate_fake_shares, insert_fake_shares
from data_generators.daily_rollup_user_stats_generator import generate_fake_daily_rollup_user_stats, insert_fake_daily_rollup_user_stats
from data_generators.dao_stats_generator import generate_fake_dao_stats, insert_fake_dao_stats
from data_generators.kudos_generator import generate_fake_kudos, insert_fake_kudos
from data_generators.mentions_generator import generate_fake_mentions, insert_fake_mentions
from data_generators.notifications_generator import generate_fake_notifications, insert_fake_notifications
from data_generators.ip_event_log_generator import generate_fake_ip_event_log, insert_fake_ip_event_log
from data_generators.property_rewards_generator import generate_fake_property_rewards, insert_fake_property_rewards
from data_generators.dao_voting_epochs_generator import generate_fake_dao_voting_epochs, insert_fake_dao_voting_epochs


# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_db_connection():
    """Establishes and returns a database connection."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set.")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def main():
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            print("--- Starting Fake Data Generation ---")

            # 1. Core Entities (no dependencies or minimal external dependencies)
            print("\n--- Generating Users ---")
            users_data = generate_fake_users(num_users=20)
            user_ids = insert_fake_users(supabase_admin, users_data)
            print("user_ids", user_ids)

            print("\n--- Generating Wallets ---")
            wallets_data = generate_fake_wallets(user_ids)
            wallet_ids = insert_fake_wallets(wallets_data)
            print("wallet_ids", wallet_ids)

            print("\n--- Generating Collections ---")
            collections_data = generate_fake_collections(user_ids)
            collection_ids = insert_fake_collections(collections_data)
            
            print("\n--- Generating Properties ---")
            properties_data = generate_fake_properties(user_ids)
            property_ids = insert_fake_properties(properties_data)
            
            print("\n--- Generating DAOs (initial, without SNFT link) ---")
            daos_data = generate_fake_daos(property_ids)
            dao_ids = insert_fake_daos(daos_data)
            
            # 2. Entities with dependencies on core entities
            print("\n--- Generating SNFTs ---")
            snfts_data = generate_fake_snfts(wallet_ids, user_ids, collection_ids, property_ids, dao_ids, num_snfts_per_property=1)
            snft_ids = insert_fake_snfts(snfts_data)

            # Update DAOs with SNFT IDs if snft_id is not nullable and you want to link them
            # For now, it's nullable, so we proceed.

            # print("\n--- Generating Auctions ---")
            # auctions_data = generate_fake_auctions(property_ids, user_ids)
            # insert_fake_auctions(auctions_data)
            # auction_ids = [auction["id"] for auction in auctions_data]

            # print("\n--- Generating Trades ---")
            # trades_data = generate_fake_trades(user_ids)
            # insert_fake_trades(trades_data)

            # print("\n--- Generating Trading Pairs ---")
            # trading_pairs_data = generate_fake_trading_pairs(property_ids)
            # insert_fake_trading_pairs(trading_pairs_data)
            # trading_pair_ids = [pair["id"] for pair in trading_pairs_data]

            # print("\n--- Generating AI Bot Configs ---")
            # ai_bot_configs_data = generate_fake_ai_bot_configs(user_ids, trading_pair_ids)
            # insert_fake_ai_bot_configs(ai_bot_configs_data)

            # print("\n--- Generating Orders ---")
            # orders_data = generate_fake_orders(user_ids, trading_pair_ids)
            # insert_fake_orders(orders_data)

            # print("\n--- Generating User Investments ---")
            # user_investments_data = generate_fake_user_investments(user_ids, property_ids)
            # insert_fake_user_investments(user_investments_data)

            # print("\n--- Generating Bid History ---")
            # bid_history_data = generate_fake_bid_history(auction_ids, user_ids)
            # insert_fake_bid_history(bid_history_data)

            # print("\n--- Generating Transactions ---")
            # transactions_data = generate_fake_transactions(snft_ids)
            # insert_fake_transactions(transactions_data)

            # print("\n--- Generating DAO Proposals ---")
            # dao_proposals_data = generate_fake_dao_proposals(num_proposals=10)
            # insert_fake_dao_proposals(dao_proposals_data)
            # dao_proposal_ids = [prop["id"] for prop in dao_proposals_data]

            # print("\n--- Generating DAO Votes ---")
            # dao_votes_data = generate_fake_dao_votes(dao_proposal_ids, user_ids)
            # insert_fake_dao_votes(dao_votes_data)

            # print("\n--- Generating User Stats ---")
            # user_stats_data = generate_fake_user_stats(user_ids)
            # insert_fake_user_stats(user_stats_data)

            # print("\n--- Generating SNFT Stats ---")
            # snft_stats_data = generate_fake_snft_stats(snft_ids)
            # insert_fake_snft_stats(snft_stats_data)

            # print("\n--- Generating Platform Metrics ---")
            # platform_metrics_data = generate_fake_platform_metrics(user_ids) # Using user_ids as entity_ids for some metrics
            # insert_fake_platform_metrics(platform_metrics_data)

            # print("\n--- Generating Property Token Ownership ---")
            # property_token_ownership_data = generate_fake_property_token_ownership(property_ids, wallet_ids)
            # insert_fake_property_token_ownership(property_token_ownership_data)

            # print("\n--- Generating Property Token Transfers ---")
            # property_token_transfers_data = generate_fake_property_token_transfers(property_ids, wallet_ids)
            # insert_fake_property_token_transfers(property_token_transfers_data)

            # print("\n--- Generating Contractors ---")
            # contractors_data = generate_fake_contractors(dao_ids)
            # insert_fake_contractors(contractors_data)
            # contractor_ids = [contractor["id"] for contractor in contractors_data]

            # print("\n--- Generating DAO Members ---")
            # dao_members_data = generate_fake_dao_members(dao_ids, user_ids)
            # insert_fake_dao_members(dao_members_data)

            # print("\n--- Generating DAO Managers ---")
            # dao_managers_data = generate_fake_dao_managers(dao_ids, user_ids)
            # insert_fake_dao_managers(dao_managers_data)

            # print("\n--- Generating DAO Contractors ---")
            # dao_contractors_data = generate_fake_dao_contractors(dao_ids, contractor_ids)
            # insert_fake_dao_contractors(dao_contractors_data)

            # print("\n--- Generating DAO Token Holdings ---")
            # dao_token_holdings_data = generate_fake_dao_token_holdings(dao_ids, user_ids)
            # insert_fake_dao_token_holdings(dao_token_holdings_data)

            # print("\n--- Generating SNFT Balances ---")
            # snft_balances_data = generate_fake_snft_balances(user_ids, snft_ids)
            # insert_fake_snft_balances(snft_balances_data)

            # print("\n--- Generating SNFT Mint Events ---")
            # snft_mint_events_data = generate_fake_snft_mint_events(snft_ids, user_ids)
            # insert_fake_snft_mint_events(snft_mint_events_data)

            # print("\n--- Generating SNFT Events ---")
            # snft_events_data = generate_fake_snft_events(snft_ids)
            # insert_fake_snft_events(snft_events_data)

            # print("\n--- Generating SNFT Metadata Retry Queue ---")
            # snft_metadata_retry_queue_data = generate_fake_snft_metadata_retry_queue(snft_ids)
            # insert_fake_snft_metadata_retry_queue(snft_metadata_retry_queue_data)

            # print("\n--- Generating Favorites ---")
            # # For favorites, we can use a mix of SNFT, Property, and User IDs as asset_ids
            # all_asset_ids = snft_ids + property_ids + user_ids
            # favorites_data = generate_fake_favorites(user_ids, all_asset_ids)
            # insert_fake_favorites(favorites_data)

            # print("\n--- Generating Stars ---")
            # # For stars, entities can be Users, DAOs, or SNFTs
            # all_entity_ids_for_stars = user_ids + dao_ids + snft_ids
            # stars_data = generate_fake_stars(user_ids, all_entity_ids_for_stars)
            # insert_fake_stars(stars_data)

            # print("\n--- Generating Comments ---")
            # # For comments, assets can be SNFTs, Properties, etc.
            # all_asset_ids_for_comments = snft_ids + property_ids
            # comments_data = generate_fake_comments(user_ids, all_asset_ids_for_comments)
            # insert_fake_comments(comments_data)

            # print("\n--- Generating Shares ---")
            # # For shares, assets can be SNFTs, Properties, etc.
            # all_asset_ids_for_shares = snft_ids + property_ids
            # shares_data = generate_fake_shares(user_ids, all_asset_ids_for_shares)
            # insert_fake_shares(shares_data)

            # print("\n--- Generating Daily Rollup User Stats ---")
            # daily_rollup_user_stats_data = generate_fake_daily_rollup_user_stats(user_ids)
            # insert_fake_daily_rollup_user_stats(daily_rollup_user_stats_data)

            # print("\n--- Generating DAO Stats ---")
            # dao_stats_data = generate_fake_dao_stats(dao_ids)
            # insert_fake_dao_stats(dao_stats_data)

            # print("\n--- Generating Kudos ---")
            # kudos_data = generate_fake_kudos(user_ids, user_ids) # from_user_id to to_user_id
            # insert_fake_kudos(kudos_data)

            # print("\n--- Generating Mentions ---")
            # mentions_data = generate_fake_mentions(user_ids, dao_ids, snft_ids)
            # insert_fake_mentions(mentions_data)

            # print("\n--- Generating Notifications ---")
            # notifications_data = generate_fake_notifications(user_ids)
            # insert_fake_notifications(notifications_data)

            # print("\n--- Generating IP Event Log ---")
            # ip_event_log_data = generate_fake_ip_event_log()
            # insert_fake_ip_event_log(ip_event_log_data)

            # print("\n--- Generating Property Rewards ---")
            # # For property rewards, we need badge_ids. Assuming badges are generated elsewhere or are static.
            # # For now, we'll use dummy badge IDs or skip if not available.
            # # You would typically fetch badge_ids from the database after generating them.
            # # For this script, let's assume some dummy badge IDs for now.
            # dummy_badge_ids = [uuid.uuid4() for _ in range(5)] # Replace with actual badge IDs if generated
            # property_rewards_data = generate_fake_property_rewards(user_ids, dummy_badge_ids, property_ids)
            # insert_fake_property_rewards(property_rewards_data)

            # print("\n--- Generating DAO Voting Epochs ---")
            # dao_voting_epochs_data = generate_fake_dao_voting_epochs(dao_ids, dao_proposal_ids)
            # insert_fake_dao_voting_epochs(dao_voting_epochs_data)

            print("\n--- All Fake Data Generation Completed ---")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()