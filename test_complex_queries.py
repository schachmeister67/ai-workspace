import requests
import json

# Test more complex queries to demonstrate DDL enhancement
base_url = "http://localhost:8000"

def test_complex_query(query, description):
    """Test a complex natural language query"""
    print(f"Testing: {description}")
    print(f"Query: {query}")
    print("-" * 60)
    
    query_data = {
        "query": query,
        "description": description
    }
    
    response = requests.post(f"{base_url}/query", json=query_data)
    result = response.json()
    
    print(f"Success: {result.get('success')}")
    print(f"Generated SQL:")
    print(result.get('sql_query'))
    print(f"Result:")
    print(result.get('result'))
    print(f"Raw Data: {result.get('json_result')}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    
    print("=" * 80)
    print()

if __name__ == "__main__":
    print("=== DDL-Enhanced AI SQL Agent - Complex Query Tests ===")
    print()
    
    # Test various complex queries that benefit from DDL knowledge
    test_queries = [
        ("What are the top 5 film categories by number of films?", "Category ranking with joins"),
        ("Which actors have appeared in action movies?", "Actor-film-category relationship"),
        ("Show me customers who have rented comedy films", "Multi-table join query"),
        ("What is the average rental price for each film category?", "Aggregation with joins"),
        ("Which store has more inventory?", "Store comparison query")
    ]
    
    try:
        for query, description in test_queries:
            test_complex_query(query, description)
        
        print("All complex query tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")
