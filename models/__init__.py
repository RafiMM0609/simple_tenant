from supabase import create_client, Client, ClientOptions
from settings import (
    SUPABASE_URL,
    SUPABASE_KEY
)
def get_supabase() -> Client:
    supabase_url: str = SUPABASE_URL
    supabase_key: str = SUPABASE_KEY
    # client = create_client(supabase_url, supabase_key)
    client = create_client(
        SUPABASE_URL, 
        SUPABASE_KEY,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="development",
        )
    )
    # client.postgrest.schema = "development"  # Set schema to 'development'
    return client


supabase: Client = get_supabase()