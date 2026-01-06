# Q.Invoice - AI-Powered Invoice Processing System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Q.Invoice** is an intelligent document processing system that combines OCR, LLM extraction, and adaptive AI querying to transform invoices and financial documents into actionable intelligence.

![Q.Invoice Dashboard](docs/images/dashboard.png)

---

## Project Overview

### Problem Statement

Financial document management is a critical yet time-consuming task for businesses of all sizes. Traditional approaches to invoice processing suffer from:

- **Manual Data Entry**: Error-prone and labor-intensive
- **Lack of Intelligence**: No analytical insights from document data
- **Poor Accessibility**: Documents stored as images/PDFs without searchable content
- **Limited Querying**: Difficulty in extracting specific information across multiple documents

### Solution

Q.Invoice addresses these challenges through:

1. **Automated OCR**: Intelligent text extraction from documents using PaddleOCR
2. **LLM-Powered Extraction**: Structured data extraction using GPT-4o
3. **Adaptive Query Engine**: Natural language querying with context-aware AI responses
4. **Smart Analytics**: Automatic trend analysis, spending insights, and recommendations

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                        │
│  (Query Interface, Library, Analytics, Sidebar)         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│                  Core Processing Layer                  │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐     │
│  │ Document │  │ Adaptive │  │   Export Manager   │     │
│  │Processor │  │  Query   │  │  (JSON/Excel)      │     │
│  └──────────┘  └──────────┘  └────────────────────┘     │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              Extraction & Analysis Layer                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ PDF Convert │  │  OCR Engine  │  │     LLM      │    │
│  │  (PyMuPDF)  │  │(PaddleOCR)   │  │ Extractor    │    │
│  └─────────────┘  └──────────────┘  └──────────────┘    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│                  Storage Layer                          │
│  ┌─────────────────┐         ┌────────────────────┐     │
│  │  SQLite Database│         │   File System      │     │
│  │  (Metadata)     │         │   (Documents)      │     │
│  └─────────────────┘         └────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Upload → 2. PDF Conversion → 3. OCR Extraction → 4. LLM Processing → 5. Storage
                                                                              ↓
6. Query Interface ← 7. Adaptive AI ← 8. Context Building ← 9. Data Retrieval
```

---

## ✨ Key Features

### 1. Intelligent Document Processing
- **Multi-format Support**: PDF, PNG, JPG, JPEG
- **High-Quality OCR**: PaddleOCR with confidence scoring
- **Smart Extraction**: GPT-4o-mini extracts structured data (vendor, amount, date, items, etc.)
- **Automatic Classification**: Identifies document types (invoice, receipt, quote, etc.)

### 2. Adaptive Query Engine
The system adapts its personality based on query type:

| Query Type | Triggered By | Response Style |
|------------|--------------|----------------|
| **Calculator** | "combien", "total", "sum" | Direct numbers, calculations |
| **Analyst** | "compare", "analyze", "trend" | Tables, insights, patterns |
| **Finder** | "list", "show", "find" | Clean lists, essential info |
| **Advisor** | "budget", "optimize", "save" | Recommendations, opportunities |
| **Auditor** | "missing", "error", "check" | Issues, corrections |
| **Forecaster** | "forecast", "predict", "future" | Projections, confidence levels |

### 3. Rich User Interface
- **Query Tab**: Natural language querying with suggested questions
- **Library Tab**: Document management with preview and delete
- **Analytics Tab**: Stats, trends, and export options
- **Sidebar**: Upload, chat history, quick stats

### 4. Document Preview
- **PDF Rendering**: First page preview at 2x resolution
- **Image Display**: Direct image viewing
- **Data Tabs**: Preview and structured data views

### 5. Export Capabilities
- **JSON Export**: Complete data with metadata
- **Excel Export**: Formatted spreadsheets with multiple sheets

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- 2GB+ RAM recommended
- GPU optional (for faster OCR)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/qinvoice.git
cd qinvoice
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys**
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional
```

5. **Run the application**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## Docker Support

### Using Docker

1. **Build the image**
```bash
docker build -t qinvoice .
```

2. **Run the container**
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  qinvoice
```

3. **Using Docker Compose**
```bash
docker-compose up
```

---

## 📁 Project Structure

```
qinvoice/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── core/                      # Core business logic
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── processor.py          # Document processing pipeline
│   ├── adaptive_query.py     # Adaptive AI query engine
│   ├── export.py             # Export functionality
│   └── advanced_query.py     # Advanced query (legacy)
│
├── extraction/               # Data extraction modules
│   ├── __init__.py
│   ├── ocr.py               # OCR engine (PaddleOCR)
│   ├── pdf_converter.py     # PDF to image conversion
│   ├── llm_extractor.py     # LLM-based extraction
│   └── schema.py            # Data schemas
│
├── storage/                  # Data persistence
│   ├── __init__.py
│   └── database.py          # SQLite database models
│
├── data/                     # Data directory (auto-created)
│   ├── uploads/             # Uploaded documents
│   ├── exports/             # Export files
│   └── docuvault.db         # SQLite database
│
├── docs/                     # Documentation
│   ├── images/              # Screenshots
│   ├── architecture.md      # Architecture details
│   ├── api.md              # API documentation
│   └── user_guide.md       # User guide
│
└── tests/                    # Unit tests
    ├── test_ocr.py
    ├── test_extraction.py
    └── test_query.py
```

---

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM | - |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (alternative) | - |
| `MAX_FILE_SIZE_MB` | No | Maximum file size | 200 |
| `UPLOADS_DIR` | No | Upload directory | data/uploads |
| `EXPORTS_DIR` | No | Export directory | data/exports |

### Configuration File

Edit `core/config.py` to customize:
- Supported file formats
- OCR settings
- LLM model selection
- Database path

---

## Usage Examples

### Example 1: Simple Calculation
**Query:** "What's my total spending?"

**Response:**
```
Total: 1,693.85€

Breakdown:
- Franco Group: 1,054.10€
- Others: 639.75€
```

### Example 2: Vendor Analysis
**Query:** "Show invoices by vendor"

**Response:**
```
Invoices Grouped by Vendor

| Vendor          | Count | Total    | Avg     |
|-----------------|-------|----------|---------|
| Franco Group    | 1     | 1,054€   | 1,054€  |
| Chapman, Kim    | 1     | 212€     | 212€    |
| Zuniga and Sons | 1     | 214€     | 214€    |
...
```

### Example 3: Monthly Breakdown
**Query:** "Monthly breakdown"

**Response:**
```
January 2015: 2 invoices, 330.93€
March 2012: 3 invoices, 426.64€
July 2012: 3 invoices, 346.56€
...
```

---

## Testing

### Run Unit Tests
```bash
pytest tests/
```

### Test Coverage
```bash
pytest --cov=core --cov=extraction tests/
```

### Manual Testing
1. Upload sample invoices (provided in `tests/fixtures/`)
2. Test each query type
3. Verify exports
4. Check chat history

---

## Performance

### Benchmarks (on Intel i7, 16GB RAM)

| Operation | Time | Notes |
|-----------|------|-------|
| PDF Upload | ~0.5s | Per file |
| OCR Extraction | ~2-3s | Per page |
| LLM Extraction | ~1-2s | Per document |
| Query Processing | ~1-3s | Depends on complexity |

### Optimization Tips

1. **GPU Acceleration**: Install CUDA for faster OCR
2. **Batch Processing**: Upload multiple files at once
3. **Database Indexing**: Auto-indexed for common queries
4. **Caching**: LLM responses cached by default

---

## Development

### Setting Up Development Environment

1. **Install development dependencies**
```bash
pip install -r requirements-dev.txt
```

2. **Enable debug mode**
```bash
export DEBUG=true
streamlit run app.py
```

3. **Code formatting**
```bash
black .
flake8 .
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Troubleshooting

### Common Issues

**Issue**: "WinError 32: File is being used by another process"
- **Solution**: File locking issue resolved in v1.0. Update to latest version.

**Issue**: "OPENAI_API_KEY not set"
- **Solution**: Create `.env` file with your API key

**Issue**: "PDF preview unavailable"
- **Solution**: Install PyMuPDF: `pip install PyMuPDF`

**Issue**: OCR confidence low (<70%)
- **Solution**: Ensure documents are high resolution (300+ DPI)

---

## Technical Report

For detailed technical information, see:
- [Architecture Documentation](Technical_Report.pdf)

---

## Academic Context

This project was developed as part of a Master's program in AI/Data Science, focusing on:
- Document Intelligence
- Natural Language Processing
- Computer Vision (OCR)
- Large Language Models
- Full-Stack Application Development

### Key Learning Outcomes
1. Integration of multiple AI technologies (OCR + LLM)
2. Production-ready application architecture
3. User-centered design principles
4. Real-world problem solving

---

## Future Work

### Short Term
- [ ] Multi-language support (French, Spanish, German)
- [ ] Batch export functionality
- [ ] Email notification for processing
- [ ] Mobile-responsive design

### Medium Term
- [ ] Machine learning for vendor classification
- [ ] Automatic duplicate detection
- [ ] Integration with accounting software (QuickBooks, Xero)
- [ ] Advanced analytics dashboard

### Long Term
- [ ] Blockchain for document verification
- [ ] Multi-tenant SaaS platform
- [ ] API for third-party integrations
- [ ] Real-time collaborative features

---

## Acknowledgments

- **PaddleOCR** - Open-source OCR engine
- **OpenAI** - GPT-4o API for LLM extraction
- **Streamlit** - Web application framework
- **SQLAlchemy** - Database ORM
- Academic supervisors and mentors

---

## Contact

For questions or support:
- **Email**: branly.djime@gmail.com and katibimaria@gmail.com
- **Project Link**: https://github.com/dbranly/qinvoice

---

## Project Status

- **Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: January 2026
- **Maintenance**: Active

---

**Built with ❤️ by Maria & Branly**