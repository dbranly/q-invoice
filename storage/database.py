"""
DocuVault - Database Models
SQLAlchemy models for document storage
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from core.config import Config

Base = declarative_base()


class Document(Base):
    """Document metadata and storage"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)  # bytes
    file_type = Column(String(50))
    
    # Processing
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # OCR Results
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    ocr_processing_time = Column(Float, nullable=True)  # seconds
    
    # Extracted Data
    document_type = Column(String(100), nullable=True)
    extracted_data = Column(JSON, nullable=True)  # Full JSON extraction
    
    # LLM Processing
    llm_model = Column(String(100), nullable=True)
    llm_processing_time = Column(Float, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # User-defined tags
    notes = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', type='{self.document_type}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "status": self.status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "document_type": self.document_type,
            "extracted_data": self.extracted_data,
            "ocr_confidence": self.ocr_confidence,
            "tags": self.tags,
            "is_archived": self.is_archived
        }


class SearchHistory(Base):
    """Search/query history"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    document_ids = Column(JSON, nullable=True)  # List of document IDs used
    created_at = Column(DateTime, default=datetime.utcnow)
    execution_time = Column(Float, nullable=True)


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.engine = create_engine(
            f"sqlite:///{Config.DB_PATH}",
            echo=Config.DB_ECHO
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created/verified")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def reset_database(self):
        """Drop and recreate all tables (USE WITH CAUTION)"""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        logger.warning("Database reset completed")


# Global instance
db_manager = DatabaseManager()
