# 🚀 DocuVault - Quick Start Guide

Get started with DocuVault in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Key

Create a `.env` file:

```bash
cp .env.template .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-key-here
```

## Step 3: Run the Application

```bash
streamlit run app.py
```

The app opens at: `http://localhost:8501`

## Step 4: Process Your First Document

1. **Upload**: Click "Browse files" in the sidebar
2. **Select**: Choose an invoice, receipt, or document
3. **Process**: Click "🚀 Process Documents"
4. **Wait**: Processing takes 5-15 seconds per document

## Step 5: Ask Questions

Navigate to the "💬 Chat" tab and ask:

- "What's the total amount?"
- "Who is the vendor?"
- "What items are listed?"
- "Show me the invoice number"

## Example Documents

Try these types of documents:

- 📄 **Invoices**: Business invoices with line items
- 🧾 **Receipts**: Store receipts, restaurant bills
- 📋 **Quotes**: Sales quotes, estimates
- 🛒 **Purchase Orders**: POs with vendor info
- 💰 **Bills**: Utility bills, service bills

## Tips for Best Results

### For Better OCR
- Use clear, high-resolution images (300+ DPI)
- Ensure good lighting and contrast
- Avoid skewed or rotated documents
- PDF files work great

### For Better Extraction
- Select the correct document type hint
- Ensure all important text is readable
- Process similar documents in batches

## Common Issues

### "No LLM API key configured"
➡️ Add `OPENAI_API_KEY` to your `.env` file

### "OCR failed"
➡️ Check image quality and format

### "Low confidence score"
➡️ Image might be blurry or low quality

## Next Steps

- 📚 View all documents in the "Documents" tab
- 💾 Export data as JSON or Excel
- 🔍 Check your search history
- 📊 View extraction statistics

## Need Help?

- Read the full README.md
- Check the troubleshooting section
- Submit an issue on GitHub

---

**Happy document processing! 📄✨**
