# AI Knowledge Assistant

An AI-powered document question-answering application built using Python, Streamlit, LangChain, Gemini API, and ChromaDB.

## Features

- Upload multiple PDF documents.
- Extract text from PDF pages.
- Split documents into smaller text chunks.
- Generate embeddings using Google's Gemini embedding model.
- Store document embeddings in ChromaDB.
- Retrieve relevant document sections using similarity search.
- Generate answers using Retrieval-Augmented Generation (RAG).
- Display source document names and page numbers.
- Maintain conversation history.
- Clear chat and knowledge base.

## Technology Stack

- Python
- Streamlit
- LangChain
- Google Gemini API
- ChromaDB
- PyPDF
- Pytest

## Project Structure

```text
AI-Knowledge-Assistant/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── rag_pipeline.py
│
├── tests/
│   ├── test_document_loader.py
│   ├── test_text_splitter.py
│   ├── test_embeddings.py
│   ├── test_vector_store.py
│   └── test_rag_pipeline.py
│
├── data/
│   └── uploaded_pdfs/
│
└── chroma_db/
```

## Installation

1. Clone the repository.

```bash
git clone https://github.com/MidhunM1/ai-knowledge-assistant
```

2. Navigate into the project folder.

```bash
cd AI-Knowledge-Assistant
```

3. Create a virtual environment.

```bash
python -m venv venv
```

4. Activate the environment.

```bash
venv\Scripts\activate
```

5. Install dependencies.

```bash
pip install -r requirements.txt
```

6. Create a `.env` file in the project root.

```text
GOOGLE_API_KEY=your_google_api_key
```

## Run the Application

```bash
streamlit run app.py
```

## Run Tests

```bash
python -m pytest tests -v
```

## Project Status

Core application workflow and 10 automated tests have been verified. Live Gemini answer generation still requires API verification.

## Future Improvements

- Improve conversational question retrieval.
- Add support for more document formats.
- Improve error handling and document management.
- Deploy the application publicly.

## Author

Midhun  
B.Sc. Computer Science (AI & ML)  
VIT Chennai (2024–2027)