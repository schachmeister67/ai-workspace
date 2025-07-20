import requests
import json

# Test the SQL Execution API
base_url = "http://localhost:8001"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_database_info():
    """Test the database info endpoint"""
    print("Testing database info...")
    try:
        response = requests.get(f"{base_url}/database-info")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Database: {result.get('database_name')}")
        print(f"Tables: {len(result.get('tables', []))} tables found")
        print(f"Connection: {result.get('connection_status')}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_sql_execution():
    """Test SQL execution with different types of queries"""
    test_queries = [
        {
            "description": "Simple count query",
            "sql": "SELECT COUNT(*) as total_actors FROM actor;",
        },
        {
            "description": "Select with limit",
            "sql": "SELECT first_name, last_name FROM actor LIMIT 5;",
        },
        {
            "description": "Join query",
            "sql": "SELECT c.name, COUNT(*) as film_count FROM category c JOIN film_category fc ON c.category_id = fc.category_id GROUP BY c.name ORDER BY film_count DESC LIMIT 3;",
        }
    ]
    
    for test in test_queries:
        print(f"Testing: {test['description']}")
        print(f"SQL: {test['sql']}")
        print("-" * 50)
        
        try:
            response = requests.post(f"{base_url}/execute", json=test)
            result = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Success: {result.get('success')}")
            print(f"Result: {result.get('result')}")
            print(f"Rows affected: {result.get('rows_affected')}")
            print(f"Execution time: {result.get('execution_time_ms')}ms")
            
            if result.get('error'):
                print(f"Error: {result.get('error')}")
                
        except Exception as e:
            print(f"Request Error: {e}")
        
        print("=" * 60)
        print()

def test_table_info():
    """Test table listing and schema endpoints"""
    print("Testing table information...")
    try:
        # Test tables list
        response = requests.get(f"{base_url}/tables")
        print(f"Tables endpoint status: {response.status_code}")
        tables_result = response.json()
        print(f"Found {tables_result.get('total_tables', 0)} tables")
        
        # Test schema for actor table
        response = requests.get(f"{base_url}/table-schema/actor")
        print(f"Actor table schema status: {response.status_code}")
        schema_result = response.json()
        print(f"Actor table has {schema_result.get('total_columns', 0)} columns")
        print(f"Primary keys: {schema_result.get('primary_keys', [])}")
        
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_examples():
    """Test the examples endpoint"""
    print("Testing examples endpoint...")
    try:
        response = requests.get(f"{base_url}/examples")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Basic queries: {len(result.get('basic_queries', []))}")
        print(f"Intermediate queries: {len(result.get('intermediate_queries', []))}")
        print(f"Advanced queries: {len(result.get('advanced_queries', []))}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_error_handling():
    """Test error handling with invalid SQL"""
    print("Testing error handling...")
    try:
        invalid_sql = {
            "sql": "SELECT * FROM nonexistent_table;",
            "description": "This should fail"
        }
        
        response = requests.post(f"{base_url}/execute", json=invalid_sql)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Success: {result.get('success')}")
        print(f"Error: {result.get('error')}")
        
    except Exception as e:
        print(f"Request Error: {e}")
    print()

if __name__ == "__main__":
    print("=== DVD Rental SQL Execution API Test Suite ===")
    print()
    
    try:
        test_health()
        test_database_info()
        test_table_info()
        test_examples()
        test_sql_execution()
        test_error_handling()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the SQL Execution API server is running on http://localhost:8001")
    except Exception as e:
        print(f"Error during testing: {e}")
