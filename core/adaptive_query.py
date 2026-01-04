"""
DocuVault - Adaptive Query Engine
Changes expert personality based on query type
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


class AdaptiveQueryEngine:
    """Adaptive query engine that changes personality based on question type"""
    
    def __init__(self, provider: str = "openai"):
        """Initialize adaptive query engine"""
        self.provider = provider
        
        if provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = "gpt-4o"
            
        elif provider == "anthropic":
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = "claude-3-5-sonnet-20241022"
            
        logger.info(f"Adaptive Query Engine initialized: {provider} / {self.model}")
    
    def get_documents(
        self, 
        document_ids: Optional[List[int]] = None,
        document_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Document]:
        """Retrieve documents from database"""
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
        """Build context from documents"""
        if not documents:
            return "No documents available."
        
        context_parts = []
        
        # Summary
        context_parts.append(f"=== SUMMARY ===")
        context_parts.append(f"Total documents: {len(documents)}")
        
        doc_types = {}
        for doc in documents:
            doc_type = doc.document_type or "unknown"
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        context_parts.append(f"Document types: {', '.join(f'{k}={v}' for k, v in doc_types.items())}")
        context_parts.append("")
        
        # Documents
        context_parts.append("=== DOCUMENTS ===")
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n--- Document {i} ---")
            context_parts.append(f"Filename: {doc.original_filename}")
            context_parts.append(f"Type: {doc.document_type or 'unknown'}")
            context_parts.append(f"Date: {doc.processed_at.strftime('%Y-%m-%d') if doc.processed_at else 'N/A'}")
            context_parts.append(f"OCR Confidence: {doc.ocr_confidence * 100:.0f}%" if doc.ocr_confidence else "N/A")
            
            if doc.extracted_data:
                context_parts.append("\nExtracted Data:")
                context_parts.append(json.dumps(doc.extracted_data, indent=2, ensure_ascii=False))
        
        return "\n".join(context_parts)
    
    def detect_query_type(self, question: str) -> str:
        """
        Detect the type of query to adapt personality
        
        Returns:
            Query type: calculator, analyst, finder, advisor, auditor, forecaster, assistant
        """
        q = question.lower()
        
        # Calculator
        if any(w in q for w in ['combien', 'total', 'somme', 'calcul', 'moyenne', 'pourcentage', '%', 'sum', 'calculate', 'average', 'count']):
            return "calculator"
        
        # Comparison
        if any(w in q for w in ['compar', 'versus', 'vs', 'différence', 'plus grand', 'plus petit', 'meilleur', 'compare', 'difference']):
            return "analyst"
        
        # Search/List
        if any(w in q for w in ['liste', 'montre', 'affiche', 'tous', 'quels', 'show', 'list', 'display', 'all', 'find', 'search']):
            return "finder"
        
        # Analysis/Insight
        if any(w in q for w in ['analys', 'tendance', 'insight', 'recommand', 'conseil', 'suggest', 'trend', 'pattern', 'overview']):
            return "analyst"
        
        # Financial Advisory
        if any(w in q for w in ['budget', 'dépense', 'économ', 'optimis', 'réduire', 'coût', 'spend', 'save', 'cost', 'expensive']):
            return "advisor"
        
        # Audit/Compliance
        if any(w in q for w in ['manque', 'manquant', 'erreur', 'problème', 'vérif', 'audit', 'missing', 'error', 'check', 'validate', 'issue']):
            return "auditor"
        
        # Forecasting
        if any(w in q for w in ['prévision', 'futur', 'projection', 'estim', 'forecast', 'predict', 'future', 'will', 'next']):
            return "forecaster"
        
        # Default
        return "assistant"
    
    def get_system_prompt(self, query_type: str) -> str:
        """Get system prompt based on query type"""
        
        prompts = {
            "calculator": """You are a Financial Calculator - precise, clear, and direct.

Your role:
- Calculate totals, sums, averages, percentages
- Show numbers clearly with currency
- Be concise and to the point
- No unnecessary fluff

Response format:
- Lead with the answer/number
- Show brief calculation if needed
- Keep it short and clear""",
            
            "analyst": """You are a Business Analyst - insightful and strategic.

Your role:
- Analyze patterns and trends
- Compare and contrast data
- Identify key insights
- Make strategic observations

Response format:
- Clear findings
- Data tables when useful
- Key insights highlighted
- Brief recommendations if relevant""",
            
            "finder": """You are a Document Finder - organized and efficient.

Your role:
- List relevant documents clearly
- Organize information logically
- Include essential details
- Be structured and scannable

Response format:
- Clean lists or tables
- Key info for each item
- Easy to scan
- No extra commentary""",
            
            "advisor": """You are a Financial Advisor - practical and strategic.

Your role:
- Analyze spending patterns
- Identify optimization opportunities
- Give actionable recommendations
- Focus on value and savings

Response format:
- Current situation
- Opportunities identified
- Specific recommendations
- Expected benefits""",
            
            "auditor": """You are an Auditor - meticulous and thorough.

Your role:
- Check for missing information
- Identify errors or issues
- Flag compliance problems
- Be precise and detailed

Response format:
- Issues found (if any)
- Details for each issue
- Severity or impact
- Recommended corrections""",
            
            "forecaster": """You are a Financial Forecaster - analytical and forward-thinking.

Your role:
- Analyze historical patterns
- Project future trends
- Estimate likely outcomes
- Explain your reasoning

Response format:
- Historical baseline
- Projection/forecast
- Key assumptions
- Confidence level or range""",
            
            "assistant": """You are Q.Invoice AI - intelligent, helpful, and adaptive.

Your role:
- Understand user intent
- Provide exactly what they need
- Be conversational but precise
- Match your response to the question

Guidelines:
- Simple question → Simple answer
- Complex question → Detailed response
- Always be helpful and clear"""
        }
        
        return prompts.get(query_type, prompts["assistant"])
    
    def build_user_prompt(self, question: str, context: str) -> str:
        """Build user prompt"""
        return f"""AVAILABLE DOCUMENTS:
{context}

USER QUESTION:
{question}

Respond according to your role. Be helpful, clear, and precise. Match your response style to the question - don't add unnecessary sections like "Analysis" or "Recommendations" unless they're relevant to what the user asked."""
    
    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM with adaptive prompts"""
        
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistency
                max_tokens=2000
            )
            return response.choices[0].message.content or ""
        
        else:  # anthropic
            # Anthropic doesn't have system messages, so prepend to user message
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.2,
                messages=[{"role": "user", "content": combined_prompt}]
            )
            return response.content[0].text
    
    def query(
        self, 
        question: str,
        document_ids: Optional[List[int]] = None,
        document_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Query documents with adaptive personality
        
        Args:
            question: User's question
            document_ids: Specific documents to query
            document_type: Filter by document type
            limit: Maximum documents to consider
            
        Returns:
            Dict with answer, query_type, documents, and metadata
        """
        start_time = time.time()
        
        try:
            # Get documents
            documents = self.get_documents(document_ids, document_type, limit)
            
            if not documents:
                return {
                    "answer": "Aucun document trouvé. Veuillez d'abord uploader et traiter des documents.",
                    "query_type": "assistant",
                    "documents": [],
                    "execution_time": time.time() - start_time,
                    "error": "no_documents"
                }
            
            # Detect query type
            query_type = self.detect_query_type(question)
            logger.info(f"Query type detected: {query_type}")
            
            # Build context
            context = self.build_context(documents)
            
            # Get adaptive prompts
            system_prompt = self.get_system_prompt(query_type)
            user_prompt = self.build_user_prompt(question, context)
            
            # Call LLM
            answer = self.call_llm(system_prompt, user_prompt)
            
            execution_time = time.time() - start_time
            
            # Save to history
            self.save_to_history(question, answer, [doc.id for doc in documents], execution_time)
            
            logger.success(
                f"Query completed: type={query_type}, docs={len(documents)}, "
                f"time={execution_time:.2f}s"
            )
            
            return {
                "answer": answer,
                "query_type": query_type,
                "documents": [{"id": d.id, "filename": d.original_filename} for d in documents],
                "num_documents": len(documents),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "answer": f"Erreur lors de l'exécution de la requête: {str(e)}",
                "query_type": "error",
                "documents": [],
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
    
    def save_to_history(self, query: str, response: str, document_ids: List[int], execution_time: float = 0):
        """Save query to search history"""
        session = db_manager.get_session()
        
        try:
            history_entry = SearchHistory(
                query=query,
                response=response,
                document_ids=document_ids,
                execution_time=execution_time
            )
            session.add(history_entry)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to save search history: {e}")
        finally:
            session.close()


# Global instance
adaptive_query_engine = AdaptiveQueryEngine()