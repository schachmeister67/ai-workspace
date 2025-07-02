# Database Query Assistant - Streamlit UI

This is a Streamlit web interface for the Database Query Assistant that allows you to interact with your PostgreSQL database using natural language queries. The application provides both standalone Streamlit and FastAPI-based deployment options.

## Files Overview

### Standalone Streamlit App
- **`main_streamlit.py`**: Core backend logic with the LangGraph workflow for processing database queries
- **`streamlit_app.py`**: Streamlit web interface that provides a user-friendly UI
- **`start_streamlit.bat`**: Windows batch file to start the standalone Streamlit app

### FastAPI Integration
- **`main_fastapi.py`**: FastAPI backend server with REST API endpoints for database queries
- **`main_streamlit_app_fastapi.py`**: Streamlit frontend that connects to the FastAPI backend
- **`start_fastapi.bat`**: Windows batch file to start the FastAPI backend server
- **`start_streamlit_fastapi.bat`**: Windows batch file to start the Streamlit frontend for FastAPI

### Common Files
- **`requirements.txt`**: Python dependencies for all applications

## Features

### 🎯 Core Functionality
- **Natural Language to SQL**: Convert plain English questions to PostgreSQL queries
- **Query Validation**: Automatic query checking and correction
- **Query Execution**: Safe execution of SQL queries with error handling
- **Human-Readable Results**: Clear, formatted output of database results

### 🖥️ Streamlit UI Features
- **Interactive Chat Interface**: Ask questions and see results in a conversational format
- **Example Questions**: Click-to-use example queries in the sidebar
- **Query History**: Track all your questions and answers
- **Statistics Dashboard**: Monitor success rates and query counts
- **Error Handling**: Clear error messages and recovery suggestions

## Deployment Options Comparison

| Feature | Standalone Streamlit | FastAPI + Streamlit |
|---------|---------------------|---------------------|
| **Complexity** | Simple, single file | Moderate, two components |
| **Scalability** | Single user/session | Multiple concurrent users |
| **API Access** | No external API | REST API available |
| **Documentation** | Manual | Auto-generated OpenAPI/Swagger |
| **Deployment** | Single process | Two processes (backend + frontend) |
| **Use Case** | Development, personal use | Production, integration with other systems |
| **Startup** | One command | Two commands (backend first, then frontend) |

**Choose Standalone** if you want:
- Quick setup and testing
- Personal or development use
- Simple deployment

**Choose FastAPI + Streamlit** if you want:
- Production deployment
- API access for other applications
- Better scalability and performance
- Automatic API documentation

## How to Run

### Prerequisites
1. Python 3.8+ installed
2. PostgreSQL database with connection details
3. Google Gemini API key

### Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database_name
   GOOGLE_API_KEY=your_google_gemini_api_key
   ```

### Option 1: Standalone Streamlit App

3. **Run the Streamlit App**:
   ```bash
   streamlit run streamlit_app.py
   ```
   
   **Alternative methods:**
   ```bash
   # Run on specific port
   streamlit run streamlit_app.py --server.port 8501
   
   # Run the batch file (Windows)
   start_streamlit.bat
   ```

4. **Access the App**:
   Open your browser to `http://localhost:8501`

### Option 2: FastAPI + Streamlit Architecture

3. **Start the FastAPI Backend**:
   ```bash
   uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload
   
   # Or use the batch file (Windows)
   start_fastapi.bat
   ```

4. **Start the Streamlit Frontend** (in a separate terminal):
   ```bash
   streamlit run main_streamlit_app_fastapi.py --server.port 8501
   
   # Or use the batch file (Windows)
   start_streamlit_fastapi.bat
   ```

5. **Access the Applications**:
   - **Streamlit Frontend**: `http://localhost:8501`
   - **FastAPI Backend Documentation**: `http://localhost:8000/docs`
   - **FastAPI Health Check**: `http://localhost:8000/health`

### Stopping the Applications

5. **Stop the App(s)**:
   - Press **`Ctrl + C`** in the terminal(s) where the applications are running
   - Or close the terminal window(s)
   - Or use Task Manager to end Python processes

## Usage Examples

### Basic Queries
- "How many customers do we have?"
- "What tables are in the database?"
- "Show me the first 10 orders"

### System Information
- "What is the database name?"
- "What version of PostgreSQL are we using?"
- "List all table names"

### Data Analysis
- "What's the average order value?"
- "How many products were sold last month?"
- "Show me the top 5 customers by revenue"

## Architecture

### Standalone Streamlit Application
The standalone application uses a three-stage LangGraph workflow:

1. **Query Generation** (`query_gen`): Converts natural language to SQL using database schema
2. **Query Checking** (`query_check`): Validates and corrects SQL syntax
3. **Query Execution** (`query_execute`): Safely executes queries and formats results

### FastAPI + Streamlit Architecture
The FastAPI-based architecture separates the backend and frontend:

**Backend (FastAPI)**:
- REST API endpoints for query processing (`main_fastapi.py`)
- Same LangGraph workflow as standalone version
- Interactive API documentation at `/docs`
- Health check and table listing endpoints

**Frontend (Streamlit)**:
- User interface that communicates with FastAPI backend via HTTP requests (`main_streamlit_app_fastapi.py`)
- Real-time API status checking
- Same user experience as standalone version

**Benefits of FastAPI Architecture**:
- **Scalability**: Backend can handle multiple concurrent requests
- **API Access**: Can be used by other applications or services
- **Separation of Concerns**: Frontend and backend can be deployed independently
- **Documentation**: Automatic OpenAPI/Swagger documentation

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check your `DATABASE_URL` in the `.env` file
   - Ensure PostgreSQL server is running
   - Verify network connectivity

2. **API Key Error**:
   - Confirm `GOOGLE_API_KEY` is set correctly
   - Check API key permissions and quotas

3. **Import Errors**:
   - Run `pip install -r requirements.txt`
   - Ensure you're using the correct Python environment

4. **Streamlit Not Starting**:
   - Try: `python -m streamlit run streamlit_app.py` (standalone) or `python -m streamlit run main_streamlit_app_fastapi.py` (FastAPI version)
   - Check if port 8501 is available

5. **FastAPI Backend Issues**:
   - Ensure port 8000 is available
   - Check FastAPI logs in the terminal
   - Visit `http://localhost:8000/health` to verify backend is running
   - Try: `python -m uvicorn main_fastapi:app --port 8000`

6. **FastAPI Frontend Connection Issues**:
   - Ensure FastAPI backend is running first
   - Check that frontend is configured to connect to `http://localhost:8000`
   - Verify CORS settings if accessing from different domains

### Development Tips

- **Debug Mode**: Check the terminal output for detailed error messages
- **Query Debugging**: 
  - Standalone version: Enable print statements in `main_streamlit.py`
  - FastAPI version: Check `main_fastapi.py` logs and enable debugging in the backend
- **Database Testing**: 
  - Standalone version: Use `main_streamlit.py` directly for testing without the UI
  - FastAPI version: Use the `/docs` endpoint at `http://localhost:8000/docs` for direct API testing
- **API Testing**: Use the interactive documentation at `http://localhost:8000/docs` to test `main_fastapi.py` endpoints

## Customization

### Adding New Features

**Standalone Version**:
- Modify `streamlit_app.py` for UI changes
- Update `main_streamlit.py` for backend logic changes

**FastAPI Version**:
- Modify `main_streamlit_app_fastapi.py` for frontend UI changes
- Update `main_fastapi.py` for backend API changes and workflow logic
- Add new REST API endpoints to `main_fastapi.py` as needed

**Common**:
- Add new system prompts to improve AI responses in either `main_streamlit.py` or `main_fastapi.py`
- Update the LangGraph workflow for enhanced query processing

### Styling
- **Standalone Version**: Update the CSS in `streamlit_app.py`
- **FastAPI Version**: Update the CSS in `main_streamlit_app_fastapi.py`
- Modify colors, layouts, and components as needed
- FastAPI version (`main_streamlit_app_fastapi.py`) includes additional API status indicators

### API Extensions (FastAPI Version)
- Add new REST endpoints in `main_fastapi.py`
- Implement authentication middleware in `main_fastapi.py`
- Add request logging and monitoring to `main_fastapi.py`
- Create custom response models using Pydantic in `main_fastapi.py`
- Extend the frontend in `main_streamlit_app_fastapi.py` to use new API features

## Security Notes

- Never expose database credentials in code
- Use environment variables for sensitive information
- The app runs queries in read-only mode by default
- Consider adding authentication for production use

## Support

For issues or questions:
1. Check the terminal output for error details
2. Verify database connectivity
3. Ensure all dependencies are installed correctly
