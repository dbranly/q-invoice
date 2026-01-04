"""
DocuVault - Query Engine
Intelligent document search and question answering
"""
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from anthropic import Anthropic
from loguru import logger

from core.config import Config
from storage.database import db_manager, Document, SearchHistory


class QueryEngine:
    """Query documents using natural language"""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize query engine
        
        Args:
            provider: "openai" or "anthropic"
        """
        self.provider = provider
        
        if provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.DEFAULT_LLM_MODEL
            
        elif provider == "anthropic":
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = "claude-3-5-sonnet-20241022"
        
        logger.info(f"Query Engine initialized: {provider} / {self.model}")
    
    def get_documents(
        self, 
        document_ids: Optional[List[int]] = None,
        document_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Document]:
        """
        Retrieve documents from database
        
        Args:
            document_ids: Specific document IDs to retrieve
            document_type: Filter by document type
            limit: Maximum number of documents
            
        Returns:
            List of Document records
        """
        session = db_manager.get_session()
        
        try:
            query = session.query(Document).filter(
                Document.status == "completed",
                Document.is_archived == False
            )
            
            if document_ids:
                query = query.filter(Document.id.in_(document_ids))
            
            if document_type:
                query = query.filter(Document.document_type == document_type)
            
            query = query.order_by(Document.processed_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        finally:
            session.close()
    
    def build_context(self, documents: List[Document]) -> str:
        """
        Build context from documents for LLM
        
        Args:
            documents: List of Document records
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No documents available."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[DOCUMENT {i}]")
            context_parts.append(f"ID: {doc.id}")
            context_parts.append(f"Filename: {doc.original_filename}")
            context_parts.append(f"Type: {doc.document_type}")
            context_parts.append(f"Processed: {doc.processed_at}")
            
            if doc.extracted_data:
                context_parts.append(f"Extracted Data:")
                context_parts.append(json.dumps(doc.extracted_data, indent=2))
            
            if doc.ocr_text:
                context_parts.append(f"OCR Text:")
                context_parts.append(doc.ocr_text[:1000])  # Limit OCR text
            
            context_parts.append("")  # Blank line
        
        return "\n".join(context_parts)
    
    def build_query_prompt(self, question: str, context: str) -> str:
        """
        Build query prompt
        
        Args:
            question: User's question
            context: Document context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are DocuVault AI, an intelligent document assistant. Your role is to answer questions about documents accurately and helpfully.

INSTRUCTIONS:
1. Answer ONLY based on the provided document data below
2. Be specific - cite document IDs and filenames when relevant
3. For financial questions, use exact amounts from the documents
4. If information is not in the documents, clearly state "This information is not available in the documents"
5. Format numbers and dates clearly
6. For multiple documents, compare or aggregate data as requested
7. Be concise but complete

AVAILABLE DOCUMENTS:
{context}

USER QUESTION:
{question}

Provide a clear, accurate answer:"""
        
        return prompt
    
    def call_llm(self, prompt: str) -> str:
        """
        Call LLM for query
        
        Args:
            prompt: Query prompt
            
        Returns:
            LLM response
        """
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful document assistant. Answer questions accurately based only on provided documents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=2000
            )
            return response.choices[0].message.content or ""
        
        else:  # anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
    
    def query(
        self, 
        question: str,
        document_ids: Optional[List[int]] = None,
        document_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Query documents with natural language
        
        Args:
            question: User's question
            document_ids: Specific documents to query
            document_type: Filter by document type
            limit: Maximum documents to consider
            
        Returns:
            Dict with answer, documents used, and metadata
        """
        start_time = time.time()
        
        try:
            # Get relevant documents
            documents = self.get_documents(document_ids, document_type, limit)
            
            if not documents:
                return {
                    "answer": "No documents found. Please upload and process documents first.",
                    "documents": [],
                    "execution_time": time.time() - start_time,
                    "error": "no_documents"
                }
            
            # Build context
            context = self.build_context(documents)
            
            # Build prompt
            prompt = self.build_query_prompt(question, context)
            
            # Call LLM
            logger.info(f"Querying {len(documents)} documents: '{question}'")
            answer = self.call_llm(prompt)
            
            execution_time = time.time() - start_time
            
            # Save to history
            self._save_to_history(
                question, 
                answer, 
                [doc.id for doc in documents],
                execution_time
            )
            
            logger.success(f"Query completed in {execution_time:.2f}s")
            
            return {
                "answer": answer,
                "documents": [
                    {
                        "id": doc.id,
                        "filename": doc.original_filename,
                        "type": doc.document_type
                    }
                    for doc in documents
                ],
                "execution_time": execution_time,
                "document_count": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "answer": f"Error processing query: {str(e)}",
                "documents": [],
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
    
    def _save_to_history(
        self, 
        query: str, 
        response: str, 
        document_ids: List[int],
        execution_time: float
    ):
        """Save query to search history"""
        session = db_manager.get_session()
        
        try:
            history = SearchHistory(
                query=query,
                response=response,
                document_ids=document_ids,
                execution_time=execution_time
            )
            session.add(history)
            session.commit()
        except Exception as e:
            logger.warning(f"Failed to save search history: {e}")
        finally:
            session.close()
    
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent search history
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of search history records
        """
        session = db_manager.get_session()
        
        try:
            history = session.query(SearchHistory)\
                .order_by(SearchHistory.created_at.desc())\
                .limit(limit)\
                .all()
            
            return [
                {
                    "id": h.id,
                    "query": h.query,
                    "response": h.response,
                    "document_ids": h.document_ids,
                    "created_at": h.created_at.isoformat(),
                    "execution_time": h.execution_time
                }
                for h in history
            ]
        finally:
            session.close()


# Global query engine
try:
    query_engine = QueryEngine(provider="openai")
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI query engine: {e}")
    try:
        query_engine = QueryEngine(provider="anthropic")
    except Exception as e2:
        logger.error(f"Failed to initialize any query engine: {e2}")
        query_engine = None
