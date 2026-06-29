import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        mongo_host = os.getenv('MONGO_HOST')
        mongo_port = int(os.getenv('MONGO_PORT'))
        
        # Create MongoDB client
        client = MongoClient(f'mongodb://{mongo_host}:{mongo_port}/', serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        print("✓ MongoDB connection successful!")
        print(f"  Connected to: {mongo_host}:{mongo_port}")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ MongoDB connection error: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()