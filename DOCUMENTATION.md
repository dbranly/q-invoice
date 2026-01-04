# 📘 DocuVault - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Customization Guide](#customization-guide)
6. [Deployment](#deployment)

---

## Architecture Overview

DocuVault follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│           Streamlit UI Layer            │
│         (app.py - User Interface)       │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│         Core Business Logic             │
├─────────────────────────────────────────┤
│  • DocumentProcessor (orchestration)    │
│  • QueryEngine (Q&A)                    │
│  • ExportManager (data export)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│        Extraction Services              │
├─────────────────────────────────────────┤
│  • OCREngine (PaddleOCR)                │
│  • LLMExtractor (GPT-4/Claude)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│         Storage & Data Layer            │
├─────────────────────────────────────────┤
│  • DatabaseManager (SQLAlchemy)         │
│  • Document Models                      │
│  • File System Storage                  │
└─────────────────────────────────────────┘
```

---

## Core Components

### 1. Configuration (`core/config.py`)

Centralized configuration management using environment variables.

**Key Features:**
- Environment variable loading
- Directory setup
- Validation
- Logging configuration

**Usage:**
```python
from core.config import Config

# Access configuration
api_key = Config.OPENAI_API_KEY
max_size = Config.MAX_FILE_SIZE_MB

# Initialize
Config.initialize()
```

### 2. Document Processor (`core/processor.py`)

Orchestrates the document processing pipeline.

**Pipeline Steps:**
1. File validation
2. File storage
3. OCR extraction
4. LLM-based structured extraction
5. Database storage

**Usage:**
```python
from core.processor import document_processor

# Process single document
doc = document_processor.process_document(
    file_path="/path/to/invoice.pdf",
    original_filename="invoice.pdf",
    document_type_hint="invoice"
)

# Process batch
docs = document_processor.process_batch([
    ("/path/to/file1.pdf", "file1.pdf"),
    ("/path/to/file2.png", "file2.png")
])
```

### 3. OCR Engine (`extraction/ocr.py`)

PaddleOCR-based text extraction with preprocessing.

**Features:**
- Image preprocessing (denoising, thresholding)
- Confidence scoring
- Fallback strategy
- Multi-language support

**Usage:**
```python
from extraction.ocr import ocr_engine

# Extract text
text, confidence, metadata = ocr_engine.extract_with_fallback(
    "/path/to/document.pdf"
)

print(f"Extracted: {len(text)} characters")
print(f"Confidence: {confidence:.2%}")
```

### 4. LLM Extractor (`extraction/llm_extractor.py`)

Structured data extraction using LLMs.

**Features:**
- GPT-4 and Claude support
- Schema validation with Pydantic
- Retry logic
- Prompt engineering

**Usage:**
```python
from extraction.llm_extractor import llm_extractor

# Extract structured data
document, processing_time = llm_extractor.extract_with_retry(
    ocr_text="Invoice text...",
    document_type="invoice"
)

print(document.document_type)
print(document.amounts.total)
```

### 5. Query Engine (`core/query.py`)

Natural language query interface for documents.

**Features:**
- Context building from multiple documents
- LLM-powered Q&A
- Search history
- Document filtering

**Usage:**
```python
from core.query import query_engine

# Query documents
result = query_engine.query(
    question="What's the total of all invoices?",
    document_type="invoice",
    limit=10
)

print(result["answer"])
print(f"Used {result['document_count']} documents")
```

### 6. Export Manager (`core/export.py`)

Export documents to various formats.

**Usage:**
```python
from core.export import export_manager

# Export to JSON
json_path = export_manager.export_to_json(
    include_ocr=True,
    pretty=True
)

# Export to Excel
excel_path = export_manager.export_to_excel()

# Export single document
file_path = export_manager.export_single_document(
    document_id=1,
    format="json"
)
```

---

## API Reference

### DocumentProcessor

#### `process_document(file_path, original_filename, document_type_hint=None)`
Process a single document through the full pipeline.

**Parameters:**
- `file_path` (str): Path to document file
- `original_filename` (str): Original filename
- `document_type_hint` (str, optional): Document type hint

**Returns:**
- `Document`: Database record or None if failed

#### `process_batch(file_paths, document_type_hint=None)`
Process multiple documents in batch.

**Parameters:**
- `file_paths` (list): List of (file_path, original_filename) tuples
- `document_type_hint` (str, optional): Document type hint

**Returns:**
- `list[Document]`: List of processed documents

### QueryEngine

#### `query(question, document_ids=None, document_type=None, limit=10)`
Query documents with natural language.

**Parameters:**
- `question` (str): User's question
- `document_ids` (list, optional): Specific document IDs
- `document_type` (str, optional): Filter by type
- `limit` (int): Maximum documents to consider

**Returns:**
- `dict`: Query result with answer, documents, and metadata

### ExportManager

#### `export_to_json(document_ids=None, include_ocr=False, pretty=True)`
Export documents to JSON.

**Parameters:**
- `document_ids` (list, optional): Specific IDs or None for all
- `include_ocr` (bool): Include raw OCR text
- `pretty` (bool): Pretty print JSON

**Returns:**
- `str`: Path to exported file

---

## Database Schema

### Document Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| filename | String | Unique filename |
| original_filename | String | Original uploaded name |
| file_path | String | Path to stored file |
| file_size | Integer | Size in bytes |
| file_type | String | File extension |
| status | String | processing, completed, failed |
| uploaded_at | DateTime | Upload timestamp |
| processed_at | DateTime | Processing completion time |
| ocr_text | Text | Raw OCR output |
| ocr_confidence | Float | OCR confidence (0-1) |
| ocr_processing_time | Float | OCR duration in seconds |
| document_type | String | invoice, receipt, etc. |
| extracted_data | JSON | Structured extraction |
| llm_model | String | LLM model used |
| llm_processing_time | Float | LLM duration in seconds |
| tags | JSON | User-defined tags |
| notes | Text | User notes |
| is_archived | Boolean | Archive status |

### SearchHistory Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| query | Text | User question |
| response | Text | System answer |
| document_ids | JSON | Documents used |
| created_at | DateTime | Query timestamp |
| execution_time | Float | Query duration |

---

## Customization Guide

### Adding New Document Types

1. Update schema in `extraction/schema.py`:

```python
class CustomDocument(BaseModel):
    # Add custom fields
    special_field: Optional[str] = None
```

2. Update prompt in `extraction/llm_extractor.py`:

```python
def build_extraction_prompt(self, ocr_text, document_type):
    # Add custom extraction logic
    if document_type == "custom":
        # Custom prompt
```

### Adding New Export Formats

1. Create exporter in `core/export.py`:

```python
def export_to_custom_format(self, document_ids=None):
    # Custom export logic
```

### Custom OCR Preprocessing

1. Modify `extraction/ocr.py`:

```python
def preprocess_image(self, image_path):
    # Add custom preprocessing steps
```

### Custom Query Templates

1. Extend `core/query.py`:

```python
def query_with_template(self, template_name, params):
    # Custom query logic
```

---

## Deployment

### Local Deployment

```bash
# Clone and install
git clone https://github.com/yourusername/docuvault.git
cd docuvault
pip install -r requirements.txt

# Configure
cp .env.template .env
# Edit .env with your API keys

# Run
streamlit run app.py
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### Cloud Deployment (Streamlit Cloud)

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in Streamlit dashboard
4. Deploy

### Production Considerations

**Security:**
- Use secrets management (e.g., AWS Secrets Manager)
- Enable HTTPS
- Implement authentication
- Rate limiting

**Performance:**
- Use GPU for OCR in production
- Enable caching
- Use CDN for static assets
- Consider horizontal scaling

**Monitoring:**
- Log aggregation (ELK, CloudWatch)
- Error tracking (Sentry)
- Performance monitoring (New Relic)
- Usage analytics

---

## Best Practices

1. **Error Handling**: Always use try-except blocks
2. **Logging**: Use loguru for structured logging
3. **Validation**: Validate all inputs
4. **Testing**: Write unit tests for core functionality
5. **Documentation**: Keep docs updated
6. **Security**: Never commit API keys
7. **Performance**: Monitor processing times

---

## Support & Contributing

- **Issues**: Report bugs on GitHub
- **Features**: Request features via discussions
- **Contributing**: Submit pull requests
- **Documentation**: Help improve docs

---

*Last updated: January 2025*
