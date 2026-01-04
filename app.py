"""
Q.Invoice - Query Your Invoices Intelligently
Clean working version with preview and delete
"""
import streamlit as st
import tempfile
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Q.Invoice",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded so it's visible
)

# Clean CSS with good sidebar
st.markdown("""
<style>
    @import url('https://rsms.me/inter/inter.css');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide defaults */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Dark background */
    .main {
        background: #1a1a1a;
        padding: 0;
    }
    
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
        max-width: 1400px;
    }
    
    /* Header */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #333;
    }
    
    .app-header h1 {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .app-header .tagline {
        font-size: 14px;
        color: #888;
        margin-top: 4px;
        font-weight: 400;
    }
    
    .app-header .quick-stats {
        display: flex;
        gap: 3rem;
        font-size: 15px;
        color: #999;
        font-weight: 500;
    }
    
    .app-header .quick-stats .stat-item {
        text-align: center;
    }
    
    .app-header .quick-stats .stat-num {
        font-size: 24px;
        font-weight: 700;
        color: #fff;
        display: block;
        margin-bottom: 2px;
    }
    
    .app-header .quick-stats .stat-label {
        font-size: 11px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Hero */
    .hero {
        text-align: center;
        padding: 4rem 2rem;
        background: #222;
        border-radius: 16px;
        border: 2px dashed #444;
        margin: 2rem 0;
    }
    
    .hero h1 {
        font-size: 56px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    
    .hero .tagline {
        font-size: 20px;
        color: #888;
        margin-bottom: 2rem;
    }
    
    /* Sidebar - Rich and visible */
    section[data-testid="stSidebar"] {
        background: #1a1a1a;
        border-right: 1px solid #333;
        min-width: 320px !important;
        max-width: 320px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 1rem;
    }
    
    section[data-testid="stSidebar"] h3 {
        font-size: 13px;
        font-weight: 700;
        color: #999;
        margin: 1rem 0 0.75rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    section[data-testid="stSidebar"] hr {
        border: none;
        border-top: 1px solid #333;
        margin: 1rem 0;
    }
    
    /* Sidebar expanders */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        background: #222;
        border: 1px solid #333;
        border-radius: 6px;
        font-size: 12px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        border-color: #667eea;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        font-size: 13px;
        padding: 0.5rem;
    }
    
    /* Sidebar metrics */
    section[data-testid="stSidebar"] .stMetric {
        background: #222;
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid #333;
    }
    
    section[data-testid="stSidebar"] .stMetric label {
        font-size: 11px !important;
        color: #888 !important;
    }
    
    section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        font-size: 20px !important;
        color: #fff !important;
    }
    
    /* Force sidebar to always show */
    [data-testid="collapsedControl"] {
        display: block !important;
    }
    
    /* Sidebar toggle button */
    button[kind="header"] {
        color: #fff !important;
    }
    
    /* Cards */
    .card {
        background: #222;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    
    .card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid #333;
        padding: 0;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        color: #888;
        border: none;
        border-bottom: 2px solid transparent;
        font-weight: 500;
        font-size: 14px;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea;
        border-bottom-color: #667eea;
        background: transparent;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Stats */
    .stat-card {
        background: #222;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s;
    }
    
    .stat-card:hover {
        border-color: #667eea;
    }
    
    .stat-num {
        font-size: 36px;
        font-weight: 700;
        color: #fff;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stat-indicator {
        font-size: 13px;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .stat-good { color: #4ade80; }
    .stat-warning { color: #fbbf24; }
    .stat-bad { color: #f87171; }
    
    /* Chat */
    .chat-suggestions {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    
    .suggestion-chip {
        background: #222;
        border: 1px solid #444;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 13px;
        color: #ccc;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
    }
    
    .suggestion-chip:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Messages */
    .stChatMessage {
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        background: #222;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: #222;
        border: 1px solid #333;
        color: #e5e5e5;
    }
    
    /* Input */
    .stChatInput > div {
        border-radius: 12px;
        border: 2px solid #333;
        background: #222;
    }
    
    .stChatInput > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    
    .stChatInput input {
        background: #222 !important;
        color: #fff !important;
        font-size: 14px !important;
    }
    
    .stChatInput input::placeholder {
        color: #666 !important;
    }
    
    /* Document Item */
    .doc-item {
        background: #222;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
        display: flex;
        gap: 1rem;
    }
    
    .doc-item:hover {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }
    
    .doc-preview {
        width: 80px;
        height: 100px;
        background: #1a1a1a;
        border: 1px solid #444;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        flex-shrink: 0;
    }
    
    .doc-content {
        flex: 1;
        min-width: 0;
    }
    
    .doc-name {
        font-size: 16px;
        font-weight: 600;
        color: #fff;
        margin-bottom: 0.75rem;
        word-break: break-word;
    }
    
    .doc-meta {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .badge-success {
        background: rgba(74, 222, 128, 0.2);
        color: #4ade80;
        border: 1px solid #4ade80;
    }
    
    .badge-warning {
        background: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 1px solid #fbbf24;
    }
    
    .badge-danger {
        background: rgba(248, 113, 113, 0.2);
        color: #f87171;
        border: 1px solid #f87171;
    }
    
    .badge-info {
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        border: 1px solid #667eea;
    }
    
    .badge-secondary {
        background: rgba(255, 255, 255, 0.1);
        color: #ccc;
        border: 1px solid #444;
    }
    
    /* Status dot */
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .status-success { background: #4ade80; }
    .status-processing {
        background: #fbbf24;
        animation: pulse 1.5s infinite;
    }
    .status-failed { background: #f87171; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    
    /* Select */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid #333;
        background: #222;
        color: #fff;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #222;
        border: 1px solid #333;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        padding: 0.75rem 1rem;
        color: #fff;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #667eea;
    }
    
    /* Tabs in expander */
    .streamlit-expanderContent .stTabs [data-baseweb="tab-list"] {
        background: #222;
        border-bottom: 1px solid #444;
        padding: 0.5rem;
        gap: 0.5rem;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
    }
    
    .streamlit-expanderContent .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-size: 13px;
        background: transparent;
        border-radius: 6px;
    }
    
    .streamlit-expanderContent .stTabs [aria-selected="true"] {
        background: #667eea;
        color: white;
        border-bottom: none;
    }
    
    /* Images */
    .streamlit-expanderContent img {
        border-radius: 8px;
        border: 1px solid #333;
        margin: 1rem 0;
    }
    
    /* Text area */
    .stTextArea textarea {
        background: #1a1a1a !important;
        color: #ccc !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        font-family: 'Monaco', 'Menlo', monospace !important;
        font-size: 12px !important;
    }
    
    /* JSON viewer */
    .stJson {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
        border: none;
        font-size: 14px;
        background: #222;
        border: 1px solid #444;
        color: #fff;
    }
    
    /* Text colors */
    .text-muted {
        color: #888;
        font-size: 13px;
    }
    
    /* Metric labels */
    .stMetric label {
        color: #888 !important;
        font-size: 12px !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #fff !important;
        font-size: 24px !important;
    }
    
    /* Delete button style */
    .delete-btn {
        background: rgba(248, 113, 113, 0.2) !important;
        color: #f87171 !important;
        border: 1px solid #f87171 !important;
    }
    
    .delete-btn:hover {
        background: rgba(248, 113, 113, 0.3) !important;
        box-shadow: 0 4px 12px rgba(248, 113, 113, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

from core.config import Config
from core.processor import document_processor
from core.adaptive_query import adaptive_query_engine
from core.export import export_manager
from storage.database import db_manager, Document, SearchHistory

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = [
        "What's my total spending?",
        "Show invoices by vendor",
        "Any overdue payments?",
        "Monthly breakdown"
    ]

def load_documents():
    session = db_manager.get_session()
    try:
        return session.query(Document)\
            .filter(Document.is_archived == False)\
            .order_by(Document.processed_at.desc())\
            .all()
    finally:
        session.close()

def delete_document(doc_id):
    """Delete a document (soft delete)"""
    session = db_manager.get_session()
    try:
        doc = session.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.is_archived = True
            session.commit()
            
            # Try to delete physical file
            if doc.file_path and Path(doc.file_path).exists():
                try:
                    Path(doc.file_path).unlink()
                except:
                    pass
            
            return True
    except Exception as e:
        st.error(f"Error deleting document: {e}")
        return False
    finally:
        session.close()

def get_quality_indicator(confidence):
    if not confidence:
        return "N/A", "secondary"
    pct = confidence * 100
    if pct >= 90:
        return f"{pct:.0f}%", "success"
    elif pct >= 70:
        return f"{pct:.0f}%", "warning"
    else:
        return f"{pct:.0f}%", "danger"

def get_status_display(doc):
    if doc.status == "completed":
        return '<span class="status-dot status-success"></span>Ready', "success"
    elif doc.status == "processing":
        return '<span class="status-dot status-processing"></span>Processing', "warning"
    else:
        return '<span class="status-dot status-failed"></span>Failed', "danger"

def get_doc_icon(doc_type):
    icons = {
        "invoice": "🧾",
        "receipt": "🧾",
        "quote": "📝",
        "purchase_order": "📋",
        "bill": "💵",
        "statement": "📊",
        "lease": "📄",
        "contract": "📜"
    }
    return icons.get(doc_type, "📄")

def render_sidebar():
    """Render comprehensive sidebar with chat history"""
    with st.sidebar:
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #667eea; font-size: 24px; margin: 0;">Q.Invoice</h2>
            <p style="color: #888; font-size: 12px; margin: 0.5rem 0 0 0;">AI Document Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Upload Section
        st.markdown("### 📤 Upload")
        files = st.file_uploader(
            "Drop files or click to browse", 
            type=Config.SUPPORTED_FORMATS, 
            accept_multiple_files=True, 
            label_visibility="collapsed", 
            key="sidebar_upload"
        )
        
        if files:
            if st.button("🚀 Process Files", key="sidebar_process", width="stretch"):
                progress = st.progress(0)
                status_text = st.empty()
                
                for i, f in enumerate(files):
                    status_text.text(f"{i+1}/{len(files)}: {f.name[:20]}...")
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(f.name).suffix) as tmp:
                        tmp.write(f.getbuffer())
                        tmp_path = tmp.name
                    
                    try:
                        document_processor.process_document(tmp_path, f.name)
                    finally:
                        try:
                            Path(tmp_path).unlink()
                        except:
                            pass
                    
                    progress.progress((i + 1) / len(files))
                
                progress.empty()
                status_text.empty()
                st.success("✓ Uploaded!")
                st.rerun()
        
        st.markdown("---")
        
        # Chat History Section
        st.markdown("### 💬 Chat History")
        
        # Get chat history from database
        session = db_manager.get_session()
        try:
            history = session.query(SearchHistory)\
                .order_by(SearchHistory.created_at.desc())\
                .limit(10)\
                .all()
            
            if history:
                for entry in history:
                    # Create expandable for each history item
                    with st.expander(f"🔍 {entry.query[:40]}...", expanded=False):
                        st.markdown(f"**Question:**")
                        st.text(entry.query)
                        
                        st.markdown(f"**Answer:**")
                        st.markdown(entry.response[:200] + "..." if len(entry.response) > 200 else entry.response)
                        
                        st.caption(f"🕐 {entry.created_at.strftime('%b %d, %H:%M')}")
                        
                        # Delete button
                        if st.button("🗑️ Delete", key=f"del_hist_{entry.id}", width="stretch"):
                            try:
                                session.delete(entry)
                                session.commit()
                                st.success("Deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                # Clear all button
                if st.button("🗑️ Clear All History", key="clear_all_hist", width="stretch"):
                    try:
                        session.query(SearchHistory).delete()
                        session.commit()
                        st.success("History cleared!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("No chat history yet")
        finally:
            session.close()
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Stats")
        docs = load_documents()
        
        if docs:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Docs", len(docs))
            with col2:
                completed = sum(1 for d in docs if d.status == "completed")
                st.metric("Ready", completed)
            
            avg_q = sum(d.ocr_confidence or 0 for d in docs) / len(docs) * 100 if docs else 0
            st.metric("Quality", f"{avg_q:.0f}%")
        else:
            st.info("No documents")
        
        st.markdown("---")
        
        # About
        st.markdown("### ℹ️ About")
        st.markdown("""
        <div style="font-size: 11px; color: #666;">
        <b>Q.Invoice v1.0</b><br>
        AI-powered document processing<br>
        <br>
        Supported formats:<br>
        PDF, PNG, JPG, JPEG
        </div>
        """, unsafe_allow_html=True)

def main():
    # Render sidebar FIRST to ensure it shows
    render_sidebar()
    
    docs = load_documents()
    
    # Header
    if docs:
        completed = sum(1 for d in docs if d.status == "completed")
        avg_quality = sum(d.ocr_confidence or 0 for d in docs) / len(docs) * 100 if docs else 0
        
        st.markdown(f"""
        <div class="app-header">
            <div>
                <h1>Q.Invoice</h1>
                <div class="tagline">Query your invoices intelligently</div>
            </div>
            <div class="quick-stats">
                <div class="stat-item">
                    <span class="stat-num">{len(docs)}</span>
                    <span class="stat-label">Documents</span>
                </div>
                <div class="stat-item">
                    <span class="stat-num">{completed}</span>
                    <span class="stat-label">Processed</span>
                </div>
                <div class="stat-item">
                    <span class="stat-num">{avg_quality:.0f}%</span>
                    <span class="stat-label">Avg Quality</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero">
            <h1>Q.Invoice</h1>
            <p class="tagline">Query your invoices intelligently with AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main interface
    if not docs:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Get Started")
            st.markdown("Upload your first invoice to unlock intelligent querying")
            
            uploaded_files = st.file_uploader(
                "Drop files here or click to browse",
                type=Config.SUPPORTED_FORMATS,
                accept_multiple_files=True,
                key="main_upload"
            )
            
            if uploaded_files:
                if st.button("🚀 Process Documents", width="stretch"):
                    progress = st.progress(0)
                    status_text = st.empty()
                    
                    for i, f in enumerate(uploaded_files):
                        status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {f.name}")
                        
                        # Create temp file and close it before processing
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(f.name).suffix) as tmp:
                            tmp.write(f.getbuffer())
                            tmp_path = tmp.name
                        # File is now closed and can be accessed
                        
                        try:
                            document_processor.process_document(tmp_path, f.name)
                        finally:
                            # Clean up temp file
                            try:
                                Path(tmp_path).unlink()
                            except:
                                pass
                        
                        progress.progress((i + 1) / len(uploaded_files))
                    
                    progress.empty()
                    status_text.empty()
                    st.success(f"✓ Processed {len(uploaded_files)} documents")
                    st.rerun()
    else:
        tab1, tab2, tab3 = st.tabs(["💬 Query", "📚 Library", "📊 Analytics"])
        
        # TAB 1: Query
        with tab1:
            col1, col2 = st.columns([4, 1])
            with col1:
                doc_types = ["All documents"] + sorted(list(set(d.document_type for d in docs if d.document_type)))
                selected = st.selectbox("Query scope", doc_types, label_visibility="collapsed", key="chat_filter")
            with col2:
                if st.button("Clear", width="stretch"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            if not st.session_state.chat_history:
                st.markdown('<div class="text-muted mb-1">Quick queries:</div>', unsafe_allow_html=True)
                cols = st.columns(4)
                for i, suggestion in enumerate(st.session_state.suggested_questions):
                    with cols[i % 4]:
                        if st.button(suggestion, key=f"sug_{i}", width="stretch"):
                            st.session_state.chat_history.append({"role": "user", "content": suggestion})
                            with st.spinner("Analyzing..."):
                                result = adaptive_query_engine.query(suggestion, document_type=None if selected == "All documents" else selected)
                                st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})
                            st.rerun()
            
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            if question := st.chat_input("Ask anything about your invoices..."):
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        result = adaptive_query_engine.query(question, document_type=None if selected == "All documents" else selected)
                        st.markdown(result["answer"])
                st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})
                st.rerun()
        
        # TAB 2: Library with Preview & Delete
        with tab2:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                types = ["All"] + sorted(list(set(d.document_type for d in docs if d.document_type)))
                f_type = st.selectbox("Filter by type", types, key="lib_filter", label_visibility="visible")
            with col2:
                sort_opts = ["Newest first", "Oldest first", "Name A-Z", "Quality ↓"]
                sort = st.selectbox("Sort by", sort_opts, key="lib_sort", label_visibility="visible")
            with col3:
                st.metric("Total", len(docs))
            
            filtered = docs if f_type == "All" else [d for d in docs if d.document_type == f_type]
            if "Newest" in sort:
                filtered = sorted(filtered, key=lambda d: d.processed_at or datetime.min, reverse=True)
            elif "Oldest" in sort:
                filtered = sorted(filtered, key=lambda d: d.processed_at or datetime.min)
            elif "Name" in sort:
                filtered = sorted(filtered, key=lambda d: d.original_filename)
            else:
                filtered = sorted(filtered, key=lambda d: d.ocr_confidence or 0, reverse=True)
            
            st.markdown(f'<div class="text-muted mb-2">Showing {len(filtered)} documents</div>', unsafe_allow_html=True)
            
            for doc in filtered:
                with st.container():
                    col_preview, col_content, col_actions = st.columns([1, 6, 1])
                    
                    with col_preview:
                        icon = get_doc_icon(doc.document_type)
                        st.markdown(f'<div class="doc-preview">{icon}</div>', unsafe_allow_html=True)
                    
                    with col_content:
                        st.markdown(f'<div class="doc-name">{doc.original_filename}</div>', unsafe_allow_html=True)
                        
                        status_html, status_class = get_status_display(doc)
                        quality_text, quality_class = get_quality_indicator(doc.ocr_confidence)
                        date_str = doc.processed_at.strftime("%b %d, %Y") if doc.processed_at else "N/A"
                        
                        st.markdown(f"""
                        <div class="doc-meta">
                            <span class="badge badge-{status_class}">{status_html}</span>
                            <span class="badge badge-info">{doc.document_type or 'unknown'}</span>
                            <span class="badge badge-{quality_class}">{quality_text}</span>
                            <span class="text-muted">{date_str}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_actions:
                        # Simple delete button
                        if st.button("🗑️", key=f"del_{doc.id}", help="Delete document"):
                            if delete_document(doc.id):
                                st.success(f"✓ Deleted {doc.original_filename}")
                                st.rerun()
                    
                    # Expander for preview
                    with st.expander("📄 View Details", expanded=False):
                        preview_tab, data_tab = st.tabs(["Preview", "Data"])
                        
                        with preview_tab:
                            if doc.file_path and Path(doc.file_path).exists():
                                file_ext = Path(doc.file_path).suffix.lower()
                                
                                if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                                    st.image(doc.file_path, width="stretch")
                                
                                elif file_ext == '.pdf':
                                    try:
                                        import fitz
                                        pdf_doc = fitz.open(doc.file_path)
                                        page = pdf_doc[0]
                                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                                        img_bytes = pix.tobytes("png")
                                        st.image(img_bytes, width="stretch")
                                        
                                        if len(pdf_doc) > 1:
                                            st.caption(f"📄 Showing page 1 of {len(pdf_doc)}")
                                        
                                        pdf_doc.close()
                                    except Exception as e:
                                        st.warning("PDF preview unavailable")
                                
                                else:
                                    st.info("Preview not available for this file type")
                            else:
                                st.warning("Original file not found")
                        
                        with data_tab:
                            if doc.extracted_data:
                                st.json(doc.extracted_data)
                            else:
                                st.info("No data extracted")
                            
                            if doc.ocr_text:
                                with st.expander("📝 OCR Text", expanded=False):
                                    st.text_area(
                                        "Raw OCR output",
                                        doc.ocr_text,
                                        height=200,
                                        disabled=True,
                                        label_visibility="collapsed"
                                    )
        
        # TAB 3: Analytics
        with tab3:
            col1, col2, col3, col4 = st.columns(4)
            
            completed = sum(1 for d in docs if d.status == "completed")
            processing = sum(1 for d in docs if d.status == "processing")
            failed = sum(1 for d in docs if d.status == "failed")
            avg_quality = sum(d.ocr_confidence or 0 for d in docs) / len(docs) * 100 if docs else 0
            
            with col1:
                indicator = "✓ All processed" if completed == len(docs) else f"⏳ {processing} processing"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Documents</div>
                    <div class="stat-num">{len(docs)}</div>
                    <div class="stat-indicator text-muted">{indicator}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                indicator_class = "stat-good" if completed == len(docs) else "stat-warning"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Processed</div>
                    <div class="stat-num">{completed}</div>
                    <div class="stat-indicator {indicator_class}">{completed/len(docs)*100:.0f}% complete</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                quality_class = "stat-good" if avg_quality >= 90 else "stat-warning" if avg_quality >= 70 else "stat-bad"
                quality_text = "Excellent" if avg_quality >= 90 else "Good" if avg_quality >= 70 else "Needs review"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Avg Quality</div>
                    <div class="stat-num">{avg_quality:.0f}%</div>
                    <div class="stat-indicator {quality_class}">{quality_text}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                types_count = len(set(d.document_type for d in docs if d.document_type))
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Types</div>
                    <div class="stat-num">{types_count}</div>
                    <div class="stat-indicator text-muted">Detected</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if failed > 0 or avg_quality < 70:
                st.markdown("### ⚠️ Attention Required")
                if failed > 0:
                    st.warning(f"**{failed} documents failed** - Review and reprocess")
                if avg_quality < 70:
                    low_quality = [d for d in docs if d.ocr_confidence and d.ocr_confidence < 0.7]
                    st.warning(f"**{len(low_quality)} documents have low quality** - Consider re-scanning")
            
            st.markdown("### Export Data")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export JSON", width="stretch"):
                    with st.spinner("Exporting..."):
                        path = export_manager.export_to_json()
                        st.success(f"✓ {Path(path).name}")
            with col2:
                if st.button("📊 Export Excel", width="stretch"):
                    with st.spinner("Exporting..."):
                        path = export_manager.export_to_excel()
                        st.success(f"✓ {Path(path).name}")

if __name__ == "__main__":
    try:
        Config.validate()
        main()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.info("Please set your API keys in the .env file")