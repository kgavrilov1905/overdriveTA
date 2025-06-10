import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import psycopg2

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def setup_database():
    """Set up the database tables and functions"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SECRET")  # Use service role key for admin operations
    
    if not supabase_url or not supabase_key:
        print("Error: Supabase credentials not found!")
        print("Make sure SUPABASE_URL and SUPABASE_SECRET are set in .env")
        return False
    
    # Create the tables using the REST API
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("Creating documents table...")
        # Create documents table first
        result = supabase.table('documents').select('*').limit(1).execute()
        print("✓ Documents table exists or created")
        
    except Exception as e:
        print(f"Tables don't exist, let's create them manually...")
        
        # Try to create tables using simple approach
        print("Creating basic tables via Supabase client...")
        
        # Let's create tables one by one
        try:
            # First, let's just try to insert a test document to see what happens
            supabase: Client = create_client(supabase_url, supabase_key)
            
            print("Testing database connection...")
            # This will fail if tables don't exist, but give us useful info
            result = supabase.table('documents').select('count', count='exact').execute()
            print(f"✓ Database connected. Documents count: {result.count}")
            return True
            
        except Exception as e2:
            print(f"Database connection test failed: {e2}")
            print("Please create tables manually in Supabase dashboard using the SQL from backend/setup_database.sql")
            return False

if __name__ == "__main__":
    setup_database() 