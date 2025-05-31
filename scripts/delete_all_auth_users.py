from config import supabase_admin

def delete_all_users():
    try:
        print("Fetching all users...")
        users = supabase_admin.auth.admin.list_users()
        print("getting Users: ",users)
        # users = users_response..get("users", [])

        for user in users:
            user_id = user.id
            supabase_admin.auth.admin.delete_user(user_id)
            print(f"❌ Deleted: {user.email}")

        print("✅ All auth.users deleted.")
    except Exception as e:
        print(f"❌ Error deleting users: {e}")

if __name__ == "__main__":
    delete_all_users()
