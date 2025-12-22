# AI Knowledge Assistant

## Interface reference
<img width="1382" height="1244" alt="image" src="https://github.com/user-attachments/assets/357991d4-c4ae-477c-8a7a-9dc8f833cb74" />

AI Knowledge Assistant is a document Q&A system based on FastAPI. It integrates Alibaba Cloud DashScope's natural language processing capabilities, allowing document uploads and intelligent Q&A based on the uploaded documents.

## Features

- **Document Upload**: Support for uploading TXT and PDF format documents
- **Smart Q&A**: Intelligent Q&A based on uploaded document content (RAG technology)
- **Vector Retrieval**: Efficient document retrieval using FAISS vector database
- **Web Interface**: Simple and user-friendly web interface
- **Multi-model Support**: Integration with multiple language models from Alibaba Cloud DashScope
- **Reference Tracking**: Show which documents were referenced in the answers

## Tech Stack

- **Framework**: FastAPI
- **Vector Database**: FAISS
- **Text Embedding**: DashScope text-embedding-v2
- **Language Model**: DashScope qwen-turbo
- **Frontend**: HTML + JavaScript
- **File Processing**: PyPDF2 (PDF parsing)

## Requirements

- Python 3.11+
- Alibaba Cloud DashScope API Key

## Installation & Deployment

### 1. Clone the Project

```bash
git clone <repository_url>
cd ai-knowledge-assistant
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Set environment variable:

```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"
```

### 5. Start the Application

```bash
uvicorn app:app --reload
```

The application will run at `http://localhost:8000`

## Usage

1. After starting the application, open your browser and visit `http://localhost:8000`
2. Upload TXT or PDF documents (multiple documents supported)
3. Enter questions in the chat box, the system will answer based on the uploaded document content
4. If no documents are uploaded, the system will call the large language model directly for answers

## API Endpoints

- `GET /` - Home page
- `POST /upload` - Upload documents
- `POST /chat` - Chat interface
- `POST /reset_index` - Reset vector database (for development)

## Project Structure

```
ai-knowledge-assistant/
├── app.py          # FastAPI application main file
├── requirements.txt # Dependencies list
├── web/            # Frontend template directory
│   └── index.html
├── static/         # Static assets directory
└── uploads/        # Upload files directory
```

## Development Notes

The project adopts RAG (Retrieval-Augmented Generation) architecture, processing user questions through the following steps:

1. Perform text embedding on user questions to generate vector representations
2. Retrieve relevant document fragments in the FAISS vector database
3. Combine retrieved document content with user questions to build prompts
4. Call the large language model to generate document-based answers

## FAQ

Q: Why is an API key required?
A: The project uses Alibaba Cloud DashScope's text embedding and language model services, which require a valid API key.

Q: What document formats are supported?
A: Currently supports TXT and PDF format documents.

## License

MIT License
