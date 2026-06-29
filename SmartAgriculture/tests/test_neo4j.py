import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

def test_neo4j_connection():
    """Test Neo4j connection"""
    try:
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER')
        password = os.getenv('NEO4J_PASSWORD')
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection with a simple query
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            test_value = result.single()["test"]
            
            if test_value == 1:
                print("✓ Neo4j connection successful!")
                print(f"  Connected to: {uri}")
                print(f"  User: {user}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"✗ Neo4j connection failed: {e}")
        return False

if __name__ == "__main__":
    test_neo4j_connection()