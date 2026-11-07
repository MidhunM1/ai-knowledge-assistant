
# AI Knowledge Assistant

An AI-powered application that allows users to upload PDF documents and ask questions about their content. The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from uploaded documents and generate context-aware answers.

## Features

- User registration and email login using Supabase Authentication
- Multiple PDF document uploads
- PDF text extraction
- OCR support for scanned documents using Tesseract
- Text splitting into smaller chunks
- Gemini embeddings for document vectorization
- ChromaDB for vector storage and similarity search
- Groq LLM for AI-generated answers
- Relevant document context and source references
- Conversation history management
- Create and delete conversations
- Knowledge base management
- Streamlit-based interactive interface

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | User interface |
| LangChain | RAG application framework |
| Gemini | Text embeddings |
| Groq | AI answer generation |
| ChromaDB | Vector database |
| Supabase | User authentication and conversation storage |
| PyMuPDF / PyPDF | PDF processing |
| Tesseract OCR | Text extraction from scanned documents |

## Project Architecture

1. User uploads PDF documents.
2. Document loader extracts text from PDFs.
3. OCR processes scanned documents when required.
4. Text splitter divides extracted text into chunks.
5. Gemini generates embeddings for the chunks.
6. ChromaDB stores the embeddings.
7. User submits a question.
8. Similarity search retrieves relevant document chunks.
9. Retrieved context is passed to the Groq language model.
10. The application generates an answer using the retrieved context.
11. The answer and relevant source information are displayed.

## Project Structure

```text
AI-Knowledge-Assistant/
│
├── app.py
├── config.py
├── requirements.txt
├── packages.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── rag_pipeline.py
│   ├── error_handling.py
│   ├── auth.py
│   ├── chat_history.py
│   └── supabase_client.py
│
├── tests/
│   └── test_supabase.py
│
├── data/
│   └── uploaded_pdfs/
│
└── chroma_db/
```

Local runtime folders such as `chroma_db/` and uploaded PDF storage are not included in the GitHub repository.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/MidhunM1/ai-knowledge-assistant.git
```

### 2. Open the project directory

```bash
cd ai-knowledge-assistant
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a `.env` file in the project root directory.

Add your own API credentials:

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
```

Do not upload your `.env` file or expose your API credentials on GitHub.

### 7. Configure Tesseract OCR

Install Tesseract OCR on your system if OCR functionality is required.

Windows installation:
https://github.com/UB-Mannheim/tesseract/wiki

### 8. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Running Tests

Run the test suite using:

```bash
python -m pytest tests -v
```

## Deployment

The application can be deployed using Streamlit Community Cloud.

Configure the required API credentials in the application's Streamlit Secrets settings instead of uploading a `.env` file.

## Security

- API credentials are stored in environment variables or Streamlit Secrets.
- User authentication is handled through Supabase.
- Authenticated sessions are used for user-specific operations.
- Secret files and local databases should not be committed to GitHub.

## Author

**Midhun**

B.Sc. Computer Science – Artificial Intelligence and Machine Learning  
VIT Chennai | 2024–2027
