"""
Test script for AI SQL Agent v2
Demonstrates the modular design with separated SQL generation and execution.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_sql_agent_v2 import (
    process_natural_language_query, 
    generate_sql_query, 
    check_api_availability,
    get_database_info
)

def test_sql_generation_only():
    """Test SQL generation without execution"""
    print("\n" + "="*60)
    print("TEST 1: SQL Generation Only (No Execution)")
    print("="*60)
    
    queries = [
        "Show me the top 5 actors by number of films",
        "What are the most popular film categories?",
        "Find customers who have never rented a movie"
    ]
    
    for query in queries:
        print(f"\nNatural Query: {query}")
        print("-" * 40)
        
        result = generate_sql_query(query, include_explanation=True)
        
        print(f"Generated SQL: {result.sql_query}")
        print(f"Validation: {result.validation_status}")
        if result.explanation:
            print(f"Explanation: {result.explanation}")
        if result.validation_message:
            print(f"Validation Note: {result.validation_message}")

def test_complete_pipeline():
    """Test complete pipeline with execution"""
    print("\n" + "="*60)
    print("TEST 2: Complete Pipeline (Generation + Execution)")
    print("="*60)
    
    if not check_api_availability():
        print("❌ SQL Execution API is not available!")
        print("Please start: python sql_execution_api.py")
        return
    
    queries = [
        "Count the total number of films",
        "Show me 3 customers from California", 
        "What is the database name?"
    ]
    
    for query in queries:
        print(f"\nNatural Query: {query}")
        print("-" * 40)
        
        result = process_natural_language_query(query)
        
        print(f"Generated SQL: {result.sql_query}")
        print(f"Success: {result.execution_success}")
        print(f"Execution Time: {result.execution_time_ms}ms")
        
        if result.execution_success:
            print(f"Result: {result.execution_result}")
            print(f"Rows: {result.rows_affected}")
        else:
            print(f"Error: {result.execution_error}")

def test_database_info():
    """Test database information retrieval"""
    print("\n" + "="*60)
    print("TEST 3: Database Information Retrieval")
    print("="*60)
    
    if not check_api_availability():
        print("❌ SQL Execution API is not available!")
        return
    
    db_info = get_database_info()
    
    if "error" in db_info:
        print(f"Error: {db_info['error']}")
    else:
        print(f"Database: {db_info.get('database', 'N/A')}")
        print(f"Total Tables: {db_info.get('table_count', 0)}")
        print("\nSample Tables:")
        for table in db_info.get('tables', [])[:5]:
            print(f"  - {table['table_name']}: {table['row_count']} rows")

def main():
    """Run all tests"""
    print("AI SQL Agent v2 - Comprehensive Test Suite")
    print("This demonstrates the modular design with separated concerns")
    
    # Test 1: SQL Generation Only
    test_sql_generation_only()
    
    # Test 2: Complete Pipeline
    test_complete_pipeline()
    
    # Test 3: Database Info
    test_database_info()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("\nKey Benefits of v2 Architecture:")
    print("- Clean separation of concerns")
    print("- LLM focuses only on SQL generation") 
    print("- Database execution handled by dedicated API")
    print("- Modular and maintainable design")
    print("- Easy to test individual components")

if __name__ == "__main__":
    main()
