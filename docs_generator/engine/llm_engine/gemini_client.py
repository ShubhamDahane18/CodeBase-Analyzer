import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def generate_documentation(prompt: str) -> str:
    """
    Generates documentation using Groq LLaMA 3.2 model.
    Returns STRICT JSON string.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")

    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",   # Recommended stable model
        temperature=0.2,
        max_tokens=4096
    )

    response = llm.invoke(prompt)

    return response.content