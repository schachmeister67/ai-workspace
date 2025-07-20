import requests
import json

# Test the FastAPI SQL API
base_url = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_natural_language_query():
    """Test the natural language query endpoint"""
    print("Testing natural language query...")
    query_data = {
        "query": "How many actors are in the database?",
        "description": "Count of actors test"
    }
    
    response = requests.post(f"{base_url}/query", json=query_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Generated SQL: {result.get('sql_query')}")
    print(f"Result: {result.get('result')}")
    print(f"JSON Result: {result.get('json_result')}")
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    print()

def test_direct_sql():
    """Test the direct SQL execution endpoint"""
    print("Testing direct SQL execution...")
    sql_data = {
        "sql": "SELECT COUNT(*) as total_films FROM film;",
        "description": "Count films directly"
    }
    
    response = requests.post(f"{base_url}/execute", json=sql_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    print()

def test_schema_info():
    """Test the schema information endpoint"""
    print("Testing schema information...")
    response = requests.get(f"{base_url}/schema")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Database: {result.get('database')}")
    print(f"Tables: {result.get('tables')}")
    print(f"Statistics: {result.get('statistics')}")
    print()

def test_examples():
    """Test the examples endpoint"""
    print("Testing examples endpoint...")
    response = requests.get(f"{base_url}/examples")
    print(f"Status: {response.status_code}")
    result = response.json()
    print("Natural Language Examples:")
    for example in result.get('natural_language_examples', [])[:3]:
        print(f"  - {example}")
    print()

if __name__ == "__main__":
    print("=== DVD Rental SQL API Test Suite ===")
    print()
    
    try:
        test_health()
        test_schema_info()
        test_examples()
        test_direct_sql()
        test_natural_language_query()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")
