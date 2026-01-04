"""
DocuVault - Advanced Query Engine
Intelligent document search with analytics, calculations, and insights
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


class AdvancedQueryEngine:
    """Advanced query engine with analytical capabilities"""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize advanced query engine
        
        Args:
            provider: "openai" or "anthropic"
        """
        self.provider = provider
        
        if provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = "gpt-4o"  # Using GPT-4o for better analysis
            
        elif provider == "anthropic":
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = "claude-3-5-sonnet-20241022"
            
        logger.info(f"Advanced Query Engine initialized: {provider} / {self.model}")
    
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
    
    def build_advanced_context(self, documents: List[Document]) -> str:
        """
        Build enriched context from documents for advanced analysis
        
        Args:
            documents: List of Document records
            
        Returns:
            Formatted context string with analytical metadata
        """
        if not documents:
            return "No documents available."
        
        context_parts = []
        
        # Summary statistics
        context_parts.append("=== DOCUMENT SUMMARY ===")
        context_parts.append(f"Total documents: {len(documents)}")
        
        doc_types = {}
        for doc in documents:
            doc_type = doc.document_type or "unknown"
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        context_parts.append(f"Document types: {json.dumps(doc_types)}")
        context_parts.append("")
        
        # Individual documents with full data
        context_parts.append("=== DOCUMENTS DATA ===")
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n[DOCUMENT {i}]")
            context_parts.append(f"ID: {doc.id}")
            context_parts.append(f"Filename: {doc.original_filename}")
            context_parts.append(f"Type: {doc.document_type}")
            context_parts.append(f"Processed: {doc.processed_at}")
            context_parts.append(f"OCR Confidence: {doc.ocr_confidence:.2%}" if doc.ocr_confidence else "OCR Confidence: N/A")
            
            if doc.extracted_data:
                context_parts.append(f"\nExtracted Data:")
                context_parts.append(json.dumps(doc.extracted_data, indent=2, ensure_ascii=False))
            
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def build_advanced_prompt(self, question: str, context: str) -> str:
        """
        Build advanced analysis prompt
        
        Args:
            question: User's question
            context: Document context
            
        Returns:
            Formatted prompt for advanced analysis
        """
        prompt = f"""You are DocuVault AI Assistant, an intelligent financial document analyst with advanced capabilities.

Your role is to:
1. **Analyze documents thoroughly** - Extract insights, patterns, and trends
2. **Perform calculations** - Sum totals, calculate averages, percentages, differences
3. **Aggregate data** - Group by vendor, date, category, etc.
4. **Create summaries** - Generate tables, lists, comparisons
5. **Provide recommendations** - Suggest actions, identify issues, give financial advice
6. **Answer naturally** - Be conversational, helpful, and insightful

CAPABILITIES YOU HAVE:
✓ Mathematical calculations (sum, average, min, max, percentages)
✓ Data aggregation and grouping
✓ Trend analysis and pattern detection
✓ Financial recommendations and insights
✓ Table and chart data generation
✓ Comparative analysis
✓ Anomaly detection
✓ Multi-document synthesis

INSTRUCTIONS:
1. **Go beyond literal answers** - Don't just say "Document X contains Y"
2. **Calculate when needed** - If asked about totals, compute them
3. **Aggregate smartly** - Group data logically (by month, vendor, category...)
4. **Present clearly** - Use tables, bullet points, or structured formats when helpful
5. **Give context** - Explain what the numbers mean
6. **Offer insights** - Point out interesting patterns or concerns
7. **Make recommendations** - Suggest actions based on the data
8. **Be proactive** - Anticipate related questions

EXAMPLES OF GOOD RESPONSES:

Question: "Combien j'ai dépensé en total ?"
Bad: "Le document 1 montre 500€, le document 2 montre 300€"
Good: "Vous avez dépensé un total de 800€ sur les 2 documents analysés :
- Document 1 (Facture Acme): 500€
- Document 2 (Reçu TechStore): 300€

💡 Insight: La majorité de vos dépenses (62.5%) provient d'Acme Corp."

Question: "Quelles sont mes plus grosses dépenses ?"
Bad: "Document 1 a le montant le plus élevé"
Good: "Voici vos dépenses classées par ordre décroissant :

| Rang | Fournisseur | Montant | % du Total |
|------|-------------|---------|------------|
| 1    | Acme Corp   | 1,500€  | 45%        |
| 2    | TechStore   | 1,200€  | 36%        |
| 3    | Office+     | 650€    | 19%        |

💡 Recommandation: Acme Corp représente presque la moitié de vos dépenses. Envisagez de négocier des tarifs préférentiels."

Question: "Analyse mes dépenses du mois"
Bad: "Il y a 5 documents ce mois-ci"
Good: "📊 Analyse de vos dépenses de janvier 2025:

**Total dépensé: 3,250€**

Répartition par catégorie:
- Fournitures bureau: 1,200€ (37%)
- Services IT: 1,500€ (46%)
- Autres: 550€ (17%)

Tendances:
- Hausse de 23% vs décembre 2024
- Pic de dépenses la 2ème semaine (1,400€)
- Principal fournisseur: TechCorp (1,500€)

⚠️ Alertes:
- Facture TechCorp en retard de paiement (échéance: 15/01)
- 3 factures sans numéro de PO

💡 Recommandations:
1. Régulariser le paiement TechCorp rapidement
2. Ajouter les numéros PO manquants
3. Considérer un contrat annuel avec TechCorp pour réduire les coûts"

AVAILABLE DOCUMENTS CONTEXT:
{context}

USER QUESTION:
{question}

Provide a comprehensive, analytical, and helpful response. Don't just list facts - analyze, calculate, aggregate, and recommend!"""
        
        return prompt
    
    def call_llm(self, prompt: str) -> str:
        """
        Call LLM for advanced query
        
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
                        "content": "You are DocuVault AI Assistant, an intelligent document analyst. You provide detailed analysis, calculations, insights, and recommendations - not just literal answers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Slightly higher for more natural responses
                max_tokens=3000   # More tokens for detailed analysis
            )
            return response.choices[0].message.content or ""
        
        else:  # anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.3,
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
        limit: int = 50  # Increased limit for better analysis
    ) -> Dict[str, Any]:
        """
        Query documents with advanced analytical capabilities
        
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
                    "answer": "Aucun document trouvé. Veuillez d'abord uploader et traiter des documents.",
                    "documents": [],
                    "execution_time": time.time() - start_time,
                    "error": "no_documents"
                }
            
            # Build enriched context
            context = self.build_advanced_context(documents)
            
            # Build advanced prompt
            prompt = self.build_advanced_prompt(question, context)
            
            # Call LLM for analysis
            logger.info(f"Analyzing {len(documents)} documents: '{question}'")
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
                "answer": f"Erreur lors du traitement de la requête: {str(e)}",
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


# Global advanced query engine
try:
    advanced_query_engine = AdvancedQueryEngine(provider="openai")
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI query engine: {e}")
    try:
        advanced_query_engine = AdvancedQueryEngine(provider="anthropic")
    except Exception as e2:
        logger.error(f"Failed to initialize any query engine: {e2}")
        advanced_query_engine = None