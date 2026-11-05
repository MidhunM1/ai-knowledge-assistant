
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import GEMINI_EMBEDDING_MODEL, GOOGLE_API_KEY


def get_embeddings():

    embeddings = GoogleGenerativeAIEmbeddings(
        model=GEMINI_EMBEDDING_MODEL,
        api_key=GOOGLE_API_KEY
    )

    return embeddings
