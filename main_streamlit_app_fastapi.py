import streamlit as st
import requests
import json
import time

# Configure the Streamlit page
st.set_page_config(
    page_title="Database Query Assistant (FastAPI)",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
FASTAPI_URL = "http://localhost:8000"

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
    .api-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    .api-healthy {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .api-unhealthy {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if the FastAPI backend is healthy"""
    try:
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data.get("message", "API is healthy")
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to FastAPI backend. Make sure it's running on port 8000."
    except requests.exceptions.Timeout:
        return False, "API request timed out"
    except Exception as e:
        return False, f"Error checking API health: {str(e)}"


def query_api(message: str):
    """Send query to FastAPI backend"""
    try:
        response = requests.post(
            f"{FASTAPI_URL}/query",
            json={"message": message},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "result": "",
                "error": f"API returned status code: {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "result": "",
            "error": "Cannot connect to FastAPI backend"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "result": "",
            "error": "Request timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "result": "",
            "error": f"Error querying API: {str(e)}"
        }


def get_tables():
    """Get list of tables from API"""
    try:
        response = requests.get(f"{FASTAPI_URL}/tables", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "tables": "", "error": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"success": False, "tables": "", "error": str(e)}


# Main header
st.markdown('<h1 class="main-header">🗃️ Database Query Assistant (FastAPI)</h1>', unsafe_allow_html=True)

# Check API health
api_healthy, health_message = check_api_health()

# Display API status
if api_healthy:
    st.markdown(f'<div class="api-status api-healthy">✅ FastAPI Backend: {health_message}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="api-status api-unhealthy">❌ FastAPI Backend: {health_message}</div>', unsafe_allow_html=True)
    st.warning("⚠️ Please start the FastAPI backend by running: `python main_fastapi.py`")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This Streamlit app communicates with a FastAPI backend that uses AI to convert your natural language questions into SQL queries and execute them against a PostgreSQL database.
    
    **Architecture:**
    - **Frontend**: Streamlit UI (this app)
    - **Backend**: FastAPI server with LangGraph workflow
    - **AI**: Google Gemini for natural language processing
    - **Database**: PostgreSQL
    """)
    
    st.header("🔧 Backend Status")
    if api_healthy:
        st.success("✅ FastAPI backend is running")
        
        # Show backend info
        if st.button("🔄 Refresh Status"):
            st.rerun()
            
        # Get tables button
        if st.button("📋 Get Database Tables"):
            with st.spinner("Fetching tables..."):
                tables_result = get_tables()
                if tables_result["success"]:
                    st.text_area("Tables:", tables_result["tables"], height=150)
                else:
                    st.error(f"Error: {tables_result['error']}")
    else:
        st.error("❌ FastAPI backend is not available")
        st.info("Run: `python main_fastapi.py` to start the backend")
    
    st.header("💡 Example Questions")
    example_queries = [
        "How many actors are in the database?",
        "What is the name of the database?",
        "Show me all table names",
        "What's the database version?",
        "List the first 5 customers",
        "Count total number of orders",
        "What tables exist in the database?",
        "Show me the schema of the users table"
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
        submit_button = st.button("🚀 Submit Query", type="primary", use_container_width=True, disabled=not api_healthy)
    
    with col_btn2:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)
    
    # Process query
    if submit_button and query.strip() and api_healthy:
        with st.spinner("Processing your query via FastAPI backend..."):
            try:
                # Add query to chat history
                st.session_state.chat_history.append({
                    "type": "question", 
                    "content": query,
                    "timestamp": time.time()
                })
                
                # Query the API
                api_response = query_api(query)
                
                if api_response["success"]:
                    # Add successful result to chat history
                    st.session_state.chat_history.append({
                        "type": "answer", 
                        "content": api_response["result"],
                        "timestamp": time.time()
                    })
                else:
                    # Add error to chat history
                    st.session_state.chat_history.append({
                        "type": "error", 
                        "content": api_response["error"],
                        "timestamp": time.time()
                    })
                
                st.session_state.query_input = ""  # Clear the input
                st.rerun()
                
            except Exception as e:
                st.session_state.chat_history.append({
                    "type": "error", 
                    "content": f"Frontend error: {str(e)}",
                    "timestamp": time.time()
                })
                st.rerun()
    
    elif submit_button and not query.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    
    elif submit_button and not api_healthy:
        st.error("❌ Cannot submit query: FastAPI backend is not available.")
    
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
    
    # API Endpoints info
    st.subheader("🔗 API Endpoints")
    st.code(f"""
POST {FASTAPI_URL}/query
GET  {FASTAPI_URL}/health
GET  {FASTAPI_URL}/tables
GET  {FASTAPI_URL}/schema/{{table}}
    """)

# Display chat history
if st.session_state.chat_history:
    st.subheader("💬 Query History")
    
    # Reverse the history to show latest first
    for i, item in enumerate(reversed(st.session_state.chat_history)):
        if item["type"] == "question":
            st.markdown(f"""
            <div class="query-container">
                <strong>🤔 Question:</strong><br>
                {item['content']}
            </div>
            """, unsafe_allow_html=True)
            
        elif item["type"] == "answer":
            st.markdown(f"""
            <div class="result-container">
                <strong>✅ Answer (via FastAPI):</strong><br>
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
    <small>Database Query Assistant with FastAPI backend powered by LangGraph and Google Gemini AI</small><br>
    <small>Frontend: Streamlit | Backend: FastAPI | AI: Google Gemini | Database: PostgreSQL</small>
</div>
""", unsafe_allow_html=True)
