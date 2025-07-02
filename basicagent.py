import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

response = llm.invoke(
    "What is the capital of France?"
)

print(response)
