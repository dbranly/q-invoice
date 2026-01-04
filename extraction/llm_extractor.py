"""
DocuVault - LLM Extractor
Advanced document extraction using LLMs
"""
import json
import re
import time
from typing import Dict, Any, Optional, Tuple
from openai import OpenAI
from anthropic import Anthropic
from loguru import logger
from pydantic import ValidationError

from core.config import Config
from extraction.schema import ExtractedDocument, DOCUMENT_SCHEMA


class LLMExtractor:
    """Extract structured data from OCR text using LLMs"""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize LLM extractor
        
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
            
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info(f"LLM Extractor initialized: {provider} / {self.model}")
    
    def build_extraction_prompt(self, ocr_text: str, document_type: Optional[str] = None) -> str:
        """
        Build extraction prompt with schema
        
        Args:
            ocr_text: OCR extracted text
            document_type: Optional document type hint
            
        Returns:
            Formatted prompt
        """
        schema_example = {
            "document_type": "invoice",
            "document_number": "INV-001",
            "dates": {
                "issue_date": "2024-01-15",
                "due_date": "2024-02-15"
            },
            "vendor": {
                "name": "Acme Corp",
                "email": "billing@acme.com",
                "phone": "+1-555-0100"
            },
            "customer": {
                "name": "Tech Solutions Inc"
            },
            "items": [
                {
                    "description": "Consulting Services",
                    "quantity": 10,
                    "unit_price": "150.00",
                    "amount": "1500.00"
                }
            ],
            "amounts": {
                "subtotal": "1500.00",
                "tax": "150.00",
                "total": "1650.00",
                "currency": "USD"
            }
        }
        
        type_hint = f"\nDocument type hint: {document_type}" if document_type else ""
        
        prompt = f"""You are an expert document parser specialized in extracting structured data from invoices, receipts, and financial documents.

TASK: Extract ALL relevant information from the OCR text below into a structured JSON format.

RULES:
1. Return ONLY valid JSON - no markdown, no explanations, no preamble
2. Use null for missing/unknown fields
3. Extract ALL dates in YYYY-MM-DD format
4. For amounts, preserve the original format (e.g., "1,500.00" or "1500.00")
5. Extract all line items with their details
6. Identify document type: invoice, receipt, quote, purchase_order, bill, lease, etc.
7. Extract both vendor (seller) and customer (buyer) information
8. Include payment information if present
9. Calculate or extract totals, subtotals, taxes
10. Be thorough - capture ALL information present{type_hint}

EXPECTED JSON SCHEMA:
{json.dumps(schema_example, indent=2)}

IMPORTANT:
- "document_type" is REQUIRED
- Extract ALL information visible in the document
- For dates, try to parse into YYYY-MM-DD format
- For items array, include every line item found
- Preserve numerical precision in amounts

OCR TEXT:
{ocr_text}

Return the extracted data as JSON:"""
        
        return prompt
    
    def extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response
        
        Args:
            text: LLM response text
            
        Returns:
            Parsed JSON dict
        """
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try to find raw JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        raise ValueError("No valid JSON found in LLM response")
    
    def call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise document extraction system. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS
        )
        
        return response.choices[0].message.content or ""
    
    def call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.LLM_MAX_TOKENS,
            temperature=Config.LLM_TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text
    
    def extract(
        self, 
        ocr_text: str, 
        document_type: Optional[str] = None
    ) -> Tuple[ExtractedDocument, float]:
        """
        Extract structured data from OCR text
        
        Args:
            ocr_text: OCR extracted text
            document_type: Optional document type hint
            
        Returns:
            Tuple of (ExtractedDocument, processing_time)
        """
        start_time = time.time()
        
        try:
            # Build prompt
            prompt = self.build_extraction_prompt(ocr_text, document_type)
            
            # Call LLM
            logger.info(f"Calling {self.provider} for extraction...")
            if self.provider == "openai":
                response_text = self.call_openai(prompt)
            else:
                response_text = self.call_anthropic(prompt)
            
            # Extract JSON
            raw_json = self.extract_json_from_response(response_text)
            
            # Validate with Pydantic
            document = ExtractedDocument(**raw_json)
            
            processing_time = time.time() - start_time
            
            logger.success(
                f"Extraction completed: type={document.document_type}, "
                f"items={len(document.items)}, time={processing_time:.2f}s"
            )
            
            return document, processing_time
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            # Return minimal valid document
            processing_time = time.time() - start_time
            return ExtractedDocument(document_type="unknown"), processing_time
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            processing_time = time.time() - start_time
            return ExtractedDocument(document_type="unknown"), processing_time
    
    def extract_with_retry(
        self, 
        ocr_text: str, 
        document_type: Optional[str] = None,
        max_retries: int = 2
    ) -> Tuple[ExtractedDocument, float]:
        """
        Extract with retry logic
        
        Args:
            ocr_text: OCR extracted text
            document_type: Optional document type hint
            max_retries: Maximum number of retries
            
        Returns:
            Tuple of (ExtractedDocument, total_processing_time)
        """
        total_time = 0.0
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                document, processing_time = self.extract(ocr_text, document_type)
                total_time += processing_time
                
                # Check if extraction was successful
                if document.document_type != "unknown":
                    return document, total_time
                
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
        
        # All retries failed
        logger.error(f"All extraction attempts failed. Last error: {last_error}")
        return ExtractedDocument(document_type="unknown"), total_time


# Global extractor instance
try:
    llm_extractor = LLMExtractor(provider="openai")
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI extractor: {e}")
    try:
        llm_extractor = LLMExtractor(provider="anthropic")
    except Exception as e2:
        logger.error(f"Failed to initialize any LLM extractor: {e2}")
        llm_extractor = None
