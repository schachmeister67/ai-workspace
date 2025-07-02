# Database Query Assistant - Streamlit UI

This is a Streamlit web interface for the Database Query Assistant that allows you to interact with your PostgreSQL database using natural language queries.

## Files Overview

- **`main_streamlit.py`**: Core backend logic with the LangGraph workflow for processing database queries
- **`streamlit_app.py`**: Streamlit web interface that provides a user-friendly UI
- **`requirements.txt`**: Python dependencies

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

5. **Stop the App**:
   - Press **`Ctrl + C`** in the terminal where Streamlit is running
   - Or close the terminal window
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

The application uses a three-stage LangGraph workflow:

1. **Query Generation** (`query_gen`): Converts natural language to SQL using database schema
2. **Query Checking** (`query_check`): Validates and corrects SQL syntax
3. **Query Execution** (`query_execute`): Safely executes queries and formats results

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
   - Try: `python -m streamlit run streamlit_app.py`
   - Check if port 8501 is available

### Development Tips

- **Debug Mode**: Check the terminal output for detailed error messages
- **Query Debugging**: Enable print statements in `main_streamlit.py` for debugging
- **Database Testing**: Use `main_streamlit.py` directly for testing without the UI

## Customization

### Adding New Features
- Modify `streamlit_app.py` for UI changes
- Update `main_streamlit.py` for backend logic changes
- Add new system prompts to improve AI responses

### Styling
- Update the CSS in the `st.markdown()` sections
- Modify colors, layouts, and components as needed

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
