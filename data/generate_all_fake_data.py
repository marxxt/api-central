import os
import uuid # Added import for uuid
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

from config import supabase_admin  # <-- Reuse centralized config

# Import individual data generation modules
from users import generate_fake_users, insert_fake_users
from wallets import generate_fake_wallets, insert_fake_wallets
from db_collections import generate_fake_collections, insert_fake_collections
from properties import generate_fake_properties, insert_fake_properties
from daos import generate_fake_daos, insert_fake_daos
from snfts import generate_fake_snfts, insert_fake_snfts
from auctions import generate_fake_auctions, insert_fake_auctions
from trades import generate_fake_trades, insert_fake_trades
from trading_pairs import generate_fake_trading_pairs, insert_fake_trading_pairs
from ai_bot_configs import generate_fake_ai_bot_configs, insert_fake_ai_bot_configs
from orders import generate_fake_orders, insert_fake_orders
from user_investments import generate_fake_user_investments, insert_fake_user_investments
from bid_history import generate_fake_bid_history, insert_fake_bid_history
from transactions import generate_fake_transactions, insert_fake_transactions
from dao_proposals import generate_fake_dao_proposals, insert_fake_dao_proposals
from dao_votes import generate_fake_dao_votes, insert_fake_dao_votes
from user_stats import generate_fake_user_stats, insert_fake_user_stats
from snft_stats import generate_fake_snft_stats, insert_fake_snft_stats
from platform_metrics import generate_fake_platform_metrics, insert_fake_platform_metrics
from property_token_ownership import generate_fake_property_token_ownership, insert_fake_property_token_ownership
from property_token_transfers import generate_fake_property_token_transfers, insert_fake_property_token_transfers
from contractors import generate_fake_contractors, insert_fake_contractors
from dao_members import generate_fake_dao_members, insert_fake_dao_members
from dao_managers import generate_fake_dao_managers, insert_fake_dao_managers
from dao_contractors import generate_fake_dao_contractors, insert_fake_dao_contractors
from dao_token_holdings import generate_fake_dao_token_holdings, insert_fake_dao_token_holdings
from snft_balances import generate_fake_snft_balances, insert_fake_snft_balances
from snft_mint_events import generate_fake_snft_mint_events, insert_fake_snft_mint_events
from snft_events import generate_fake_snft_events, insert_fake_snft_events
from snft_metadata_retry_queue import generate_fake_snft_metadata_retry_queue, insert_fake_snft_metadata_retry_queue
from favorites import generate_fake_favorites, insert_fake_favorites
from stars import generate_fake_stars, insert_fake_stars
from comments import generate_fake_comments, insert_fake_comments
from shares import generate_fake_shares, insert_fake_shares
from daily_rollup_user_stats import generate_fake_daily_rollup_user_stats, insert_fake_daily_rollup_user_stats
from dao_stats import generate_fake_dao_stats, insert_fake_dao_stats
from kudos import generate_fake_kudos, insert_fake_kudos
from mentions import generate_fake_mentions, insert_fake_mentions
from notifications import generate_fake_notifications, insert_fake_notifications
from ip_event_log import generate_fake_ip_event_log, insert_fake_ip_event_log
from property_rewards import generate_fake_property_rewards, insert_fake_property_rewards
from dao_voting_epochs import generate_fake_dao_voting_epochs, insert_fake_dao_voting_epochs


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

            # # Update DAOs with SNFT IDs if snft_id is not nullable and you want to link them
            # # For now, it's nullable, so we proceed.

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