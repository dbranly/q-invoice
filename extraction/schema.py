"""
DocuVault - Document Schema
Comprehensive schema for various document types
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import date


class Address(BaseModel):
    """Address information"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class Party(BaseModel):
    """Party information (vendor/customer/etc)"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    tax_id: Optional[str] = None


class LineItem(BaseModel):
    """Line item in invoice/receipt"""
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[str] = None
    amount: Optional[str] = None
    tax: Optional[str] = None
    discount: Optional[str] = None


class Amounts(BaseModel):
    """Financial amounts"""
    subtotal: Optional[str] = None
    tax: Optional[str] = None
    discount: Optional[str] = None
    shipping: Optional[str] = None
    total: Optional[str] = None
    currency: Optional[str] = "USD"
    paid: Optional[str] = None
    due: Optional[str] = None


class Dates(BaseModel):
    """Document dates"""
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    delivery_date: Optional[str] = None
    payment_date: Optional[str] = None


class PaymentInfo(BaseModel):
    """Payment information"""
    method: Optional[str] = None  # cash, card, transfer, etc.
    card_last_four: Optional[str] = None
    transaction_id: Optional[str] = None
    bank_account: Optional[str] = None


class ExtractedDocument(BaseModel):
    """Main document structure"""
    document_type: str = Field(
        default="unknown",
        description="Type of document: invoice, receipt, quote, purchase_order, etc."
    )
    
    # Identifiers
    document_number: Optional[str] = None
    reference_number: Optional[str] = None
    po_number: Optional[str] = None
    
    # Dates
    dates: Dates = Field(default_factory=Dates)
    
    # Parties
    vendor: Optional[Party] = None
    customer: Optional[Party] = None
    
    # Line Items
    items: List[LineItem] = Field(default_factory=list)
    
    # Amounts
    amounts: Amounts = Field(default_factory=Amounts)
    
    # Payment
    payment: Optional[PaymentInfo] = None
    
    # Additional fields
    notes: Optional[str] = None
    terms: Optional[str] = None
    
    # Metadata
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Overall extraction confidence"
    )
    
    @validator('document_type')
    def validate_document_type(cls, v):
        """Validate document type"""
        valid_types = [
            "invoice", "receipt", "quote", "estimate", 
            "purchase_order", "delivery_note", "credit_note",
            "statement", "contract", "lease", "bill", "unknown"
        ]
        if v.lower() not in valid_types:
            return "unknown"
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "invoice",
                "document_number": "INV-2024-001",
                "dates": {
                    "issue_date": "2024-01-15",
                    "due_date": "2024-02-15"
                },
                "vendor": {
                    "name": "Acme Corp",
                    "email": "billing@acme.com"
                },
                "customer": {
                    "name": "Tech Solutions Inc"
                },
                "items": [
                    {
                        "description": "Professional Services",
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
        }


# JSONSchema for validation (legacy compatibility)
DOCUMENT_SCHEMA = {
    "type": "object",
    "required": ["document_type"],
    "properties": {
        "document_type": {"type": "string"},
        "document_number": {"type": ["string", "null"]},
        "reference_number": {"type": ["string", "null"]},
        
        "dates": {
            "type": "object",
            "properties": {
                "issue_date": {"type": ["string", "null"]},
                "due_date": {"type": ["string", "null"]},
                "delivery_date": {"type": ["string", "null"]},
                "payment_date": {"type": ["string", "null"]}
            }
        },
        
        "vendor": {
            "type": ["object", "null"],
            "properties": {
                "name": {"type": ["string", "null"]},
                "email": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]},
                "tax_id": {"type": ["string", "null"]}
            }
        },
        
        "customer": {
            "type": ["object", "null"],
            "properties": {
                "name": {"type": ["string", "null"]},
                "email": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]}
            }
        },
        
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": ["number", "null"]},
                    "unit_price": {"type": ["string", "null"]},
                    "amount": {"type": ["string", "null"]},
                    "tax": {"type": ["string", "null"]}
                }
            }
        },
        
        "amounts": {
            "type": "object",
            "properties": {
                "subtotal": {"type": ["string", "null"]},
                "tax": {"type": ["string", "null"]},
                "discount": {"type": ["string", "null"]},
                "total": {"type": ["string", "null"]},
                "currency": {"type": ["string", "null"]},
                "paid": {"type": ["string", "null"]},
                "due": {"type": ["string", "null"]}
            }
        },
        
        "payment": {
            "type": ["object", "null"],
            "properties": {
                "method": {"type": ["string", "null"]},
                "transaction_id": {"type": ["string", "null"]}
            }
        },
        
        "notes": {"type": ["string", "null"]},
        "confidence_score": {"type": ["number", "null"]}
    }
}
