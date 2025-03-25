from supabase import create_client, Client, ClientOptions
from settings import (
    SUPABASE_URL,
    SUPABASE_KEY
)
# import psycopg2
# from psycopg2.extensions import connection

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
            # schema="development",
            schema="multitenancy",
        )
    )
    # client.postgrest.schema = "development"  # Set schema to 'development'
    return client

def get_supabase_pdp() -> Client:
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
            # schema="multitenancy",
        )
    )
    # client.postgrest.schema = "development"  # Set schema to 'development'
    return client

# def get_postgres_connection() -> connection:
#     """
#     Connect to the PostgreSQL database directly using psycopg2.
#     """
#     db_url = "your_database_url"
#     db_user = "your_username"
#     db_password = "your_password"
#     db_name = "your_database_name"

#     conn = psycopg2.connect(
#         host=db_url,
#         user=db_user,
#         password=db_password,
#         dbname=db_name
#     )
#     return conn

supabase: Client = get_supabase()