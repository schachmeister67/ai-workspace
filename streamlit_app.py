import streamlit as st
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the process_query function from main_streamlit
from main_streamlit import process_query

# Configure the Streamlit page
st.set_page_config(
    page_title="Database Query Assistant",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .query-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .result-container {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .error-container {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🗃️ Database Query Assistant</h1>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This application uses AI to convert your natural language questions into SQL queries and execute them against a PostgreSQL database.
    
    **How it works:**
    1. Enter your question in plain English
    2. AI generates the appropriate SQL query
    3. Query is validated and corrected if needed
    4. Results are displayed in a readable format
    """)
    
    st.header("💡 Example Questions")
    example_queries = [
        "How many actors are in the database?",
        "What is the name of the database?",
        "Show me all table names",
        "What's the database version?",
        "List the first 5 customers",
        "Count total number of orders"
    ]
    
    for example in example_queries:
        if st.button(f"📝 {example}", key=f"example_{example}", use_container_width=True):
            st.session_state.query_input = example

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Ask your database question")
    
    # Query input
    query = st.text_area(
        "Enter your question:",
        value=st.session_state.query_input,
        height=100,
        placeholder="e.g., How many customers do we have in the database?",
        help="Ask any question about your database in natural language"
    )
    
    # Buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    
    with col_btn1:
        submit_button = st.button("🚀 Submit Query", type="primary", use_container_width=True)
    
    with col_btn2:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)
    
    # Process query
    if submit_button and query.strip():
        with st.spinner("Processing your query..."):
            try:
                # Add query to chat history
                st.session_state.chat_history.append({
                    "type": "question", 
                    "content": query,
                    "timestamp": st.session_state.get("query_count", 0) + 1
                })
                
                # Process the query
                result = process_query(query)
                
                # Add result to chat history
                st.session_state.chat_history.append({
                    "type": "answer", 
                    "content": result,
                    "timestamp": st.session_state.get("query_count", 0) + 1
                })
                
                st.session_state.query_count = st.session_state.get("query_count", 0) + 1
                st.session_state.query_input = ""  # Clear the input
                
                st.rerun()
                
            except Exception as e:
                st.session_state.chat_history.append({
                    "type": "error", 
                    "content": f"Error: {str(e)}",
                    "timestamp": st.session_state.get("query_count", 0) + 1
                })
                st.rerun()
    
    elif submit_button and not query.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    
    # Clear chat history
    if clear_button:
        st.session_state.chat_history = []
        st.session_state.query_input = ""
        st.rerun()

with col2:
    st.subheader("📊 Quick Stats")
    
    # Display some quick stats
    total_queries = len([item for item in st.session_state.chat_history if item["type"] == "question"])
    successful_queries = len([item for item in st.session_state.chat_history if item["type"] == "answer"])
    error_queries = len([item for item in st.session_state.chat_history if item["type"] == "error"])
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("Total Queries", total_queries)
        st.metric("Successful", successful_queries)
    with col_stat2:
        st.metric("Errors", error_queries)
        if total_queries > 0:
            success_rate = (successful_queries / total_queries) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")

# Display chat history
if st.session_state.chat_history:
    st.subheader("💬 Query History")
    
    # Reverse the history to show latest first
    for i, item in enumerate(reversed(st.session_state.chat_history)):
        if item["type"] == "question":
            st.markdown(f"""
            <div class="query-container">
                <strong>🤔 Question #{item['timestamp']}:</strong><br>
                {item['content']}
            </div>
            """, unsafe_allow_html=True)
            
        elif item["type"] == "answer":
            st.markdown(f"""
            <div class="result-container">
                <strong>✅ Answer:</strong><br>
                {item['content']}
            </div>
            """, unsafe_allow_html=True)
            
        elif item["type"] == "error":
            st.markdown(f"""
            <div class="error-container">
                <strong>❌ Error:</strong><br>
                {item['content']}
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>Database Query Assistant powered by LangGraph and Google Gemini AI</small>
</div>
""", unsafe_allow_html=True)
