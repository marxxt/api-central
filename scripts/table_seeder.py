# data_seeding/table_seeder.py
from typing import List, Dict, Any, Callable
from faker import Faker
from supabase.client import Client # Type hint for standard client

def seed_table(
    table_name: str,
    count: int,
    data_generator_func: Callable[[Faker, Any], Dict[str, Any]], # Function that takes Faker and context (like user_id) and returns payload
    supabase_client: Client,
    fake: Faker,
    # Allow passing extra context needed by the generator function
    generator_context: Any = None
) -> List[str]:
    """
    Creates multiple rows in a standard Supabase table.

    Args:
        table_name: The name of the table to insert into.
        count: The number of rows to create.
        data_generator_func: A function that takes a Faker instance and
                             generator_context and returns a dictionary payload for insertion.
        supabase_client: The initialized standard Supabase client (with service role key for seeding).
        fake: The Faker instance.
        generator_context: Optional context to pass to the data_generator_func
                           (e.g., a user_id or list of user_ids).

    Returns:
        A list of IDs of the successfully created rows.
    """
    created_ids: List[str] = []
    data_to_insert: List[Dict[str, Any]] = []

    print(f"\n--- Generating {count} rows for table '{table_name}' ---")

    for i in range(count):
        try:
            # Generate the data payload using the provided function and context
            payload = data_generator_func(fake, generator_context)
            if payload:
                data_to_insert.append(payload)
            else:
                 print(f"⚠️ Generator function returned empty payload for row {i+1}.")
        except Exception as e:
            print(f"❌ Exception generating data for row {i+1} in table '{table_name}': {e}")

    if not data_to_insert:
         print(f"⚠️ No valid data generated for table '{table_name}'. Skipping insertion.")
         return []

    print(f"--- Inserting {len(data_to_insert)} rows into table '{table_name}' ---")

    # Supabase client allows inserting multiple rows at once
    # This is generally more efficient than inserting one by one in a loop
    try:
        result = supabase_client.table(table_name).insert(data_to_insert).execute()

        if result.data:
            # Assuming your table has a primary key like 'id' that is returned
            # Filter out None values and ensure IDs are strings
            created_ids = [str(row["id"]) for row in result.data if row and "id" in row and row["id"] is not None]
            print(f"✅ Successfully inserted {len(created_ids)} rows into '{table_name}'.")
            return created_ids
        else:
            print(f"⚠️ Insert operation succeeded for '{table_name}' but returned no data (IDs not available). This might indicate an issue or a table without returning IDs.")
            return [] # Return empty list if no data was returned

    except Exception as e:
        # Catch any exceptions raised by .execute() (e.g., APIError, HTTPError)
        print(f"❌ Exception during bulk insert into '{table_name}': {e}")
        return []