"""
DocuVault - Export Module
Export documents to various formats
"""
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import pandas as pd
from loguru import logger

from core.config import Config
from storage.database import db_manager, Document


class ExportManager:
    """Export documents to various formats"""
    
    def __init__(self):
        """Initialize export manager"""
        self.export_dir = Config.EXPORTS_DIR
    
    def export_to_json(
        self, 
        document_ids: Optional[List[int]] = None,
        include_ocr: bool = False,
        pretty: bool = True
    ) -> str:
        """
        Export documents to JSON
        
        Args:
            document_ids: Specific document IDs (None = all)
            include_ocr: Include raw OCR text
            pretty: Pretty print JSON
            
        Returns:
            Path to exported file
        """
        session = db_manager.get_session()
        
        try:
            # Query documents
            query = session.query(Document).filter(Document.status == "completed")
            
            if document_ids:
                query = query.filter(Document.id.in_(document_ids))
            
            documents = query.all()
            
            # Build export data
            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_documents": len(documents),
                    "include_ocr": include_ocr
                },
                "documents": []
            }
            
            for doc in documents:
                doc_data = {
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "file_type": doc.file_type,
                    "document_type": doc.document_type,
                    "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                    "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
                    "extracted_data": doc.extracted_data,
                    "ocr_confidence": doc.ocr_confidence,
                    "tags": doc.tags
                }
                
                if include_ocr and doc.ocr_text:
                    doc_data["ocr_text"] = doc.ocr_text
                
                export_data["documents"].append(doc_data)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"docuvault_export_{timestamp}.json"
            filepath = self.export_dir / filename
            
            # Write JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    export_data, 
                    f, 
                    indent=2 if pretty else None,
                    ensure_ascii=False
                )
            
            logger.success(f"Exported {len(documents)} documents to: {filename}")
            
            return str(filepath)
            
        finally:
            session.close()
    
    def export_to_excel(
        self, 
        document_ids: Optional[List[int]] = None
    ) -> str:
        """
        Export documents to Excel
        
        Args:
            document_ids: Specific document IDs (None = all)
            
        Returns:
            Path to exported file
        """
        session = db_manager.get_session()
        
        try:
            # Query documents
            query = session.query(Document).filter(Document.status == "completed")
            
            if document_ids:
                query = query.filter(Document.id.in_(document_ids))
            
            documents = query.all()
            
            # Check if there are any documents
            if not documents:
                logger.warning("No completed documents found to export")
                raise ValueError("No completed documents found to export")
            
            # Prepare data for different sheets
            summary_data = []
            items_data = []
            
            for doc in documents:
                # Summary sheet - Initialize with safe defaults
                summary_row = {
                    "ID": doc.id,
                    "Filename": doc.original_filename or "Unknown",
                    "Document Type": doc.document_type or "unknown",
                    "Processed Date": doc.processed_at.strftime("%Y-%m-%d %H:%M") if doc.processed_at else "N/A",
                    "OCR Confidence": f"{(doc.ocr_confidence or 0.0) * 100:.1f}%"
                }
                
                # Extract key fields with comprehensive safety checks
                if doc.extracted_data and isinstance(doc.extracted_data, dict):
                    data = doc.extracted_data
                    
                    # Document number
                    summary_row["Document Number"] = data.get("document_number") or "N/A"
                    
                    # Dates - Handle None and check if dict
                    dates = data.get("dates")
                    if dates and isinstance(dates, dict):
                        summary_row["Issue Date"] = dates.get("issue_date") or "N/A"
                        summary_row["Due Date"] = dates.get("due_date") or "N/A"
                    else:
                        summary_row["Issue Date"] = "N/A"
                        summary_row["Due Date"] = "N/A"
                    
                    # Vendor - Handle None and check if dict
                    vendor = data.get("vendor")
                    if vendor and isinstance(vendor, dict):
                        summary_row["Vendor Name"] = vendor.get("name") or "N/A"
                        summary_row["Vendor Email"] = vendor.get("email") or "N/A"
                    else:
                        summary_row["Vendor Name"] = "N/A"
                        summary_row["Vendor Email"] = "N/A"
                    
                    # Customer - Handle None and check if dict
                    customer = data.get("customer")
                    if customer and isinstance(customer, dict):
                        summary_row["Customer Name"] = customer.get("name") or "N/A"
                    else:
                        summary_row["Customer Name"] = "N/A"
                    
                    # Amounts - Handle None and check if dict
                    amounts = data.get("amounts")
                    if amounts and isinstance(amounts, dict):
                        summary_row["Subtotal"] = amounts.get("subtotal") or "N/A"
                        summary_row["Tax"] = amounts.get("tax") or "N/A"
                        summary_row["Total"] = amounts.get("total") or "N/A"
                        summary_row["Currency"] = amounts.get("currency") or "N/A"
                    else:
                        summary_row["Subtotal"] = "N/A"
                        summary_row["Tax"] = "N/A"
                        summary_row["Total"] = "N/A"
                        summary_row["Currency"] = "N/A"
                    
                    # Items - Handle None, empty lists, and check if list
                    items = data.get("items")
                    if items and isinstance(items, list):
                        for item in items:
                            if item and isinstance(item, dict):
                                items_data.append({
                                    "Document ID": doc.id,
                                    "Filename": doc.original_filename or "Unknown",
                                    "Description": item.get("description") or "N/A",
                                    "Quantity": item.get("quantity") if item.get("quantity") is not None else "N/A",
                                    "Unit Price": item.get("unit_price") or "N/A",
                                    "Amount": item.get("amount") or "N/A"
                                })
                else:
                    # No extracted data - fill with N/A
                    summary_row.update({
                        "Document Number": "N/A",
                        "Issue Date": "N/A",
                        "Due Date": "N/A",
                        "Vendor Name": "N/A",
                        "Vendor Email": "N/A",
                        "Customer Name": "N/A",
                        "Subtotal": "N/A",
                        "Tax": "N/A",
                        "Total": "N/A",
                        "Currency": "N/A"
                    })
                
                summary_data.append(summary_row)
            
            # Create Excel file with multiple sheets
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"docuvault_export_{timestamp}.xlsx"
            filepath = self.export_dir / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet - always create
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Documents', index=False)
                
                # Items sheet - create even if empty
                if items_data:
                    df_items = pd.DataFrame(items_data)
                    df_items.to_excel(writer, sheet_name='Line Items', index=False)
                else:
                    # Create empty items sheet with headers
                    df_empty = pd.DataFrame(columns=[
                        "Document ID", "Filename", "Description", 
                        "Quantity", "Unit Price", "Amount"
                    ])
                    df_empty.to_excel(writer, sheet_name='Line Items', index=False)
            
            logger.success(f"Exported {len(documents)} documents to Excel: {filename}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
        finally:
            session.close()
    
    def export_single_document(
        self, 
        document_id: int,
        format: str = "json",
        include_ocr: bool = True
    ) -> str:
        """
        Export a single document
        
        Args:
            document_id: Document ID
            format: Export format ("json" or "txt")
            include_ocr: Include OCR text
            
        Returns:
            Path to exported file
        """
        session = db_manager.get_session()
        
        try:
            doc = session.query(Document).filter(Document.id == document_id).first()
            
            if not doc:
                raise ValueError(f"Document not found: {document_id}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(doc.original_filename).stem
            
            if format == "json":
                filename = f"{base_name}_{timestamp}.json"
                filepath = self.export_dir / filename
                
                export_data = {
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "document_type": doc.document_type,
                    "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
                    "extracted_data": doc.extracted_data,
                    "ocr_confidence": doc.ocr_confidence
                }
                
                if include_ocr and doc.ocr_text:
                    export_data["ocr_text"] = doc.ocr_text
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            else:  # txt
                filename = f"{base_name}_{timestamp}.txt"
                filepath = self.export_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Document: {doc.original_filename}\n")
                    f.write(f"Type: {doc.document_type}\n")
                    f.write(f"Processed: {doc.processed_at}\n")
                    f.write("\n" + "="*50 + "\n")
                    f.write("EXTRACTED DATA:\n")
                    f.write("="*50 + "\n\n")
                    
                    if doc.extracted_data:
                        f.write(json.dumps(doc.extracted_data, indent=2, ensure_ascii=False))
                    
                    if include_ocr and doc.ocr_text:
                        f.write("\n\n" + "="*50 + "\n")
                        f.write("OCR TEXT:\n")
                        f.write("="*50 + "\n\n")
                        f.write(doc.ocr_text)
            
            logger.success(f"Exported document {document_id} to: {filename}")
            
            return str(filepath)
            
        finally:
            session.close()


# Global export manager
export_manager = ExportManager()