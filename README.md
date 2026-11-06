# 🧠 AI Knowledge Assistant

An intelligent PDF question-answering application built using Python, Streamlit, LangChain, Gemini Embeddings, Groq, and ChromaDB.

Upload your PDF documents and interact with them through a conversational AI assistant. The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information and generate context-based answers with document and page references.

## ✨ Features

- 📄 **Multiple PDF Uploads** – Upload and process multiple PDF documents.
- 🔍 **Text Extraction** – Extract text from regular PDF documents.
- 👁️ **OCR Support** – Extract text from scanned and image-based PDFs using Tesseract OCR.
- ✂️ **Text Chunking** – Split extracted content into smaller, manageable chunks.
- 🧠 **Gemini Embeddings** – Generate document embeddings using Google's Gemini embedding model.
- 🗄️ **Vector Database** – Store and retrieve document embeddings using ChromaDB.
- 💬 **AI Question Answering** – Generate answers using Groq-powered language models.
- 🔗 **Source References** – Display source filenames and page numbers.
- 📝 **Conversation History** – Maintain chat context for follow-up questions.
- 🧹 **Knowledge Base Management** – Clear uploaded documents and stored knowledge.
- 🎨 **Simple Chat Interface** – Clean, minimal interface inspired by modern AI chat applications.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| LangChain | RAG application framework |
| Google Gemini API | Text embeddings |
| Groq API | AI answer generation |
| ChromaDB | Vector database |
| PyPDF | PDF text extraction |
| PyMuPDF | PDF page rendering |
| Tesseract OCR | Scanned document text extraction |
| Pytest | Automated testing |

## ⚙️ Project Architecture

The application follows a Retrieval-Augmented Generation (RAG) workflow.

```text
             PDF Upload
                 |
                 v
          Document Loader
                 |
          Text Extraction
                 |
           OCR (if needed)
                 |
                 v
            Text Splitter
                 |
                 v
          Gemini Embeddings
                 |
                 v
             ChromaDB
                 |
                 v
          User Question
                 |
                 v
        Similarity Search
                 |
                 v
          Relevant Context
                 |
                 v
          Groq LLM Model
                 |
                 v
          Generated Answer
                 |
                 v
       Answer + Source Pages
```

## 📁 Project Structure

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
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── rag_pipeline.py
│   └── error_handling.py
│
├── tests/
│   ├── test_document_loader.py
│   ├── test_text_splitter.py
│   ├── test_embeddings.py
│   ├── test_vector_store.py
│   ├── test_rag_pipeline.py
│   └── test_error_handling.py
│
└── data/
    └── uploaded_pdfs/
```

*Note: Uploaded PDFs, virtual environments, API keys, and generated ChromaDB files are excluded from the Git repository.*

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/MidhunM1/ai-knowledge-assistant.git
```

### 2. Navigate to the Project Directory

```bash
cd ai-knowledge-assistant
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```powershell
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Install Tesseract OCR

OCR functionality requires the Tesseract OCR application in addition to the Python packages.

Install Tesseract for your operating system and ensure its executable is accessible.

Windows installation: https://github.com/UB-Mannheim/tesseract/wiki

### 7. Configure API Keys

Create a `.env` file in the project root directory.

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

The Google API key is used for embeddings, while the Groq API key is used for answer generation.

**Important:** Never upload your `.env` file or expose your API keys on GitHub.

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to access the application.

## 🧪 Run Automated Tests

Execute the test suite:

```bash
python -m pytest tests -v
```

**Latest test result: 15 tests passed.**

## 🔐 Security

- API keys are stored in environment variables or Streamlit Secrets.
- Sensitive configuration files are excluded using `.gitignore`.
- Uploaded PDF documents and generated vector database files are not committed to GitHub.

## 🔮 Future Improvements

- Support additional document formats.
- Improve conversational retrieval and follow-up question handling.
- Add document preview functionality.
- Improve document management and user experience.
- Enhance deployment and cloud storage capabilities.

## 👨‍💻 Author

**Midhun**

B.Sc. Computer Science – Artificial Intelligence & Machine Learning  
VIT Chennai | 2024–2027

**Interests:** Artificial Intelligence, Machine Learning, Software Development, and Emerging Technologies.

---

⭐ If you find this project interesting, consider giving the repository a star.