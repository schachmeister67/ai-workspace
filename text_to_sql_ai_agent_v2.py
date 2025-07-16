import os
import boto3
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.language_models.llms import LLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from typing import Literal, List, Optional, Any, Dict

load_dotenv()


class LambdaBedrockChat(BaseChatModel):
    """Custom chat model that invokes Bedrock through AWS Lambda function"""
    
    lambda_function_name: str = "ml-discovery-test_beedrock"
    aws_region: str = "us-east-1"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lambda_client = boto3.client(
            'lambda',
            region_name=os.getenv("AWS_DEFAULT_REGION", self.aws_region),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response by invoking Lambda function"""
        
        # Convert messages to the format expected by Lambda
        lambda_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                lambda_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                lambda_messages.append({"role": "assistant", "content": msg.content})
            else:
                lambda_messages.append({"role": "user", "content": msg.content})
        
        # Prepare payload for Lambda function
        payload = {
            "messages": lambda_messages,
            "model_kwargs": {
                "maxTokenCount": 4096,
                "temperature": 0.1,
                "topP": 0.9
            }
        }
        
        try:
            # Invoke Lambda function
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Parse Lambda response
            response_payload = json.loads(response['Payload'].read())
            
            # Handle Lambda errors
            if 'errorMessage' in response_payload:
                raise Exception(f"Lambda error: {response_payload['errorMessage']}")
            
            # Extract the generated text from Lambda response
            generated_text = response_payload.get('response', {}).get('content', '')
            
            if not generated_text:
                generated_text = str(response_payload.get('body', ''))
            
            # Create chat generation
            generation = ChatGeneration(message=AIMessage(content=generated_text))
            return ChatResult(generations=[generation])
            
        except Exception as e:
            # Fallback response in case of error
            error_message = f"Error invoking Lambda function: {str(e)}"
            generation = ChatGeneration(message=AIMessage(content=error_message))
            return ChatResult(generations=[generation])
    
    def with_structured_output(self, schema):
        """Return a wrapper that handles structured output"""
        return StructuredOutputWrapper(self, schema)
    
    @property
    def _llm_type(self) -> str:
        return "lambda_bedrock_chat"


class StructuredOutputWrapper:
    """Wrapper to handle structured output for the Lambda Bedrock chat model"""
    
    def __init__(self, llm: LambdaBedrockChat, schema):
        self.llm = llm
        self.schema = schema
    
    def invoke(self, prompt: str, **kwargs) -> Any:
        """Invoke the LLM and parse the response according to the schema"""
        # Create a human message from the prompt
        messages = [HumanMessage(content=prompt)]
        
        # Get response from Lambda
        result = self.llm._generate(messages, **kwargs)
        response_text = result.generations[0].message.content
        
        # Try to parse the response as the expected schema
        try:
            # For QueryChecker, extract just the SQL query
            if hasattr(self.schema, '__name__') and self.schema.__name__ == 'QueryChecker':
                # Clean up the response to extract just the SQL
                sql_query = response_text.strip()
                # Remove any markdown formatting
                sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
                return self.schema(query=sql_query)
            else:
                # For other schemas, try to parse directly
                return self.schema(query=response_text.strip())
        except Exception as e:
            # Fallback: return the raw response wrapped in the schema
            return self.schema(query=response_text.strip())


# Initialize the custom Lambda Bedrock chat model
llm = LambdaBedrockChat()

db = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()
list_tables_tool = next(
    (tool for tool in tools if tool.name == "sql_db_list_tables"), None
)
get_schema_tool = next((tool for tool in tools if tool.name == "sql_db_schema"), None)


@tool
def db_exec_tool(query: str) -> str:
    """
    Execute a SQL query against the database and return the result.
    If the query is invalid or returns no result, an error message will be returned.
    In case of an error, the user is advised to rewrite the query and try again.
    """
    # Remove ```sql and ``` if present
    query = query.replace("```sql", "").replace("```", "").strip()

    # print("Executing query:")
    # print(query)

    result = db.run_no_throw(query)

    # print("Query result:")
    # print(result)

    return {"result": result}


# Global variable to store the raw database result for JSON formatting
_raw_db_result = None


@tool
def db_exec_tool_with_capture(query: str) -> str:
    """
    Execute a SQL query against the database and return the result.
    Also captures the raw result for JSON formatting.
    If the query is invalid or returns no result, an error message will be returned.
    In case of an error, the user is advised to rewrite the query and try again.
    """
    global _raw_db_result
    
    # Remove ```sql and ``` if present
    query = query.replace("```sql", "").replace("```", "").strip()

    # print("Executing query:")
    # print(query)

    result = db.run_no_throw(query)
    
    # Store the raw result for JSON formatting
    _raw_db_result = result

    # print("Query result:")
    # print(result)

    return {"result": result}


class QueryChecker(BaseModel):
    query: str = Field(description="The corrected postgres query generated by the LLm")


def query_gen(state: MessagesState) -> Command[Literal["query_check"]]:
    """
    Query Generation Node to convert natural language database queries into PostgreSQL queries.

    Args:
        state (MessagesState): The current state containing the conversation history with a natural language database query.

    Returns:
        Command: A command to update the state with the generated PostgreSQL query.
    """
    # print("query_generator")
    # print(state["messages"][-1].content)

    if not list_tables_tool or not get_schema_tool:
        raise ValueError(
            "Required database tools (list_tables_tool, get_schema_tool) are not available"
        )

    # Create a system message for the agent
    system_prompt = (
        "You are an expert database query generator specialized in PostgreSQL. "
        "You are provided with tools to list the tables in the database and get the schema of specific tables. "
        "Always use the list_tables_tool first to get an overview of available tables. "
        "Then, for any relevant table(s), use the get_schema_tool to retrieve their schema before constructing the query. "
        "You can generate SQL queries for ANY database operation including: "
        "- Counting records, getting database metadata (current_database(), version(), etc.) "
        "- Selecting data from tables, aggregating data, joining tables "
        "- Getting system information about the database "
        "Ensure that the SQL query you generate is syntactically correct and follows PostgreSQL standards. "
        "Your final output should only be the SQL query, without any additional explanation or commentary. "
        "If a user asks for database name, use SELECT current_database(); "
        "If a user asks for database version, use SELECT version(); "
        "Be creative and use appropriate PostgreSQL system functions and queries to answer any question."
    )
    
    query_agent = create_react_agent(
        llm,  # The language model instance used by the agent
        tools=[
            list_tables_tool,
            get_schema_tool,
        ],  # List of database tools the agent can utilize
    )

    # Add system message to the state
    state_with_system = {
        "messages": [
            HumanMessage(content=system_prompt, name="system"),
            *state["messages"]
        ]
    }

    # Invoke the agent with the system prompt included
    result = query_agent.invoke(state_with_system)
    # print(result)
    return Command(
        update={
            "messages": [
                # Append the result to the state, tagged with "supervisor"
                HumanMessage(content=result["messages"][-1].content, name="supervisor")
            ]
        }
    )


def query_check(state: MessagesState) -> Command[Literal["query_execute"]]:
    """
    This tool checks if the provided SQL query is correct.
    If incorrect, it returns the corrected query; otherwise, it returns the original query.
    """
    query_check_system = """You are a SQL expert with a strong attention to detail.
    You work with PostgreSQL, SQLite, and other relational databases.
    Your task is to carefully review the provided SQL query for any mistakes, including:
    - Quoting identifiers correctly (e.g., "Snippet" vs Snippet in PostgreSQL)
    - Data type mismatches
    - Using the correct number of arguments in functions
    - Ensuring joins use valid columns
    - Checking for NULL handling issues
    - Ensuring correct usage of UNION vs UNION ALL
    - Proper casting and type usage
    Make sure that the final query is in a postgres acceptable format
    If there is an issue, respond with the **corrected query only**.
    If the query is already correct, simply return the **original query**.
    """
    query = state["messages"][-1].content

    full_prompt = f"{query_check_system}\n\nQuery:\n{query}"

    # LLM invocation
    response = llm.with_structured_output(QueryChecker).invoke(full_prompt)

    # print("query_Check")
    # print(response)
    
    return Command(
        update={
            "messages": [
                # Append the corrected query to the state, tagged with "supervisor"
                HumanMessage(content=response.query, name="supervisor")
            ]
        }
    )


def query_execute(state: MessagesState):
    """
    This tool executes the provided SQL query and return the response.
    It returns the response in simple human understandable format.
    """
    # print("state from query execute")
    # print(state)
    # Create a system message for the executing agent
    system_prompt = (
        "You are an expert PostgreSQL query executor. "
        "You can use db_exec_tool_with_capture for execution of any SQL query including system queries. "
        "Your primary task is to execute the provided SQL query accurately and return the result. "
        "You can execute any type of PostgreSQL query including: "
        "- Data selection queries (SELECT) "
        "- System information queries (current_database(), version(), etc.) "
        "- Aggregate queries (COUNT, SUM, etc.) "
        "- Metadata queries about tables, schemas, etc. "
        "Execute the query exactly as provided and return the result in a clear, human-understandable format. "
        "Always provide the actual data/results, not just explanations. "
        "If the query returns system information like database name or version, present it clearly to the user."
    )
    
    executing_agent = create_react_agent(
        llm,  # The language model instance used by the agent
        tools=[db_exec_tool_with_capture],  # List of database tools the agent can utilize
    )
    
    # Add system message to the state
    state_with_system = {
        "messages": [
            HumanMessage(content=system_prompt, name="system"),
            *state["messages"]
        ]
    }

    final_result = executing_agent.invoke(state_with_system)
    # parsed_result = QueryExecutor(result=final_result)  # Assuming `QueryExecutor` is a Pydantic model with a 'result' field
    # print(parsed_result)
    print(final_result["messages"][-1].content)
    return Command(
        update={
            "messages": [
                # Append the final result to the state, tagged with "supervisor"
                HumanMessage(
                    content=final_result["messages"][-1].content, name="supervisor"
                )
            ]
        }
    )


builder = StateGraph(MessagesState)

# Add edges and nodes to define the workflow of the graph
builder.add_node("query_gen", query_gen)
builder.add_node("query_check", query_check)
builder.add_node("query_execute", query_execute)

builder.add_edge(START, "query_gen")
builder.add_edge("query_gen", "query_check")
builder.add_edge("query_check", "query_execute")
builder.add_edge("query_execute", END)

graph = builder.compile()


# Main function for processing queries - can be imported by other modules
def process_query(message: str) -> dict:
    """
    Process a natural language query and return both the SQL query and database result.
    
    Args:
        message (str): The natural language query to process
        
    Returns:
        dict: A dictionary containing:
            - 'sql_query': The SQL query generated by query_gen
            - 'result': The final result from the database in human-readable format
            - 'json_result': The raw database result in JSON-friendly format
    """
    global _raw_db_result
    _raw_db_result = None  # Reset the global variable
    
    inputs = {"messages": [("user", message)]}
    sql_query = ""
    final_output = ""

    for output in graph.stream(inputs):
        for key, value in output.items():
            if value is not None:
                if key == "query_gen":
                    # Capture the SQL query from query_gen step
                    sql_query = value["messages"][-1].content
                elif key == "query_execute":
                    # Capture the final result from query_execute step
                    final_output = value["messages"][-1].content
                
    return {
        "sql_query": sql_query,
        "result": final_output,
        "json_result": _raw_db_result
    }


if __name__ == "__main__":
    # Simple test when run directly
    test_query = "How many actors are in the database?"
    print(f"Testing with query: {test_query}")
    result = process_query(test_query)
    print(f"Generated SQL: {result['sql_query']}")
    print(f"Result: {result['result']}")
    print(f"JSON Result: {result['json_result']}")
