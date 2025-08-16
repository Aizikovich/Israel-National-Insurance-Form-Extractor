import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from config import Config


class OCRService:
    def __init__(self):
        """Initialize the OCR service with Azure Document Intelligence"""
        try:
            Config.validate_config()
            self.client = DocumentIntelligenceClient(
                endpoint=Config.DOCUMENT_INTELLIGENCE_ENDPOINT,
                credential=AzureKeyCredential(Config.DOCUMENT_INTELLIGENCE_KEY)
            )
            logging.info("OCR Service initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize OCR Service: {str(e)}")
            raise

    def extract_text_from_document(self, file_bytes, content_type="application/pdf"):
        """
        Extract text from document using Azure Document Intelligence

        Args:
            file_bytes: The document file as bytes
            content_type: MIME type of the document

        Returns:
            dict: Extracted text and metadata
        """
        try:
            # Analyze document using the layout model
            poller = self.client.begin_analyze_document(
                "prebuilt-layout",
                file_bytes,
                content_type=content_type
            )

            result = poller.result()

            # Extract text content
            extracted_data = {
                "full_text": result.content,
                "pages": [],
                "tables": [],
                "key_value_pairs": []
            }

            # Process pages
            if result.pages:
                for page in result.pages:
                    page_data = {
                        "page_number": page.page_number,
                        "text": "",
                        "lines": []
                    }

                    if page.lines:
                        for line in page.lines:
                            page_data["lines"].append({
                                "text": line.content,
                                "confidence": getattr(line, 'confidence', 1.0)
                            })
                            page_data["text"] += line.content + "\n"

                    extracted_data["pages"].append(page_data)

            # Process tables if any
            if result.tables:
                for table in result.tables:
                    table_data = {
                        "row_count": table.row_count,
                        "column_count": table.column_count,
                        "cells": []
                    }

                    for cell in table.cells:
                        table_data["cells"].append({
                            "content": cell.content,
                            "row_index": cell.row_index,
                            "column_index": cell.column_index,
                            "confidence": getattr(cell, 'confidence', 1.0)
                        })

                    extracted_data["tables"].append(table_data)

            # Process key-value pairs if any
            if result.key_value_pairs:
                for kv_pair in result.key_value_pairs:
                    if kv_pair.key and kv_pair.value:
                        extracted_data["key_value_pairs"].append({
                            "key": kv_pair.key.content,
                            "value": kv_pair.value.content,
                            "confidence": getattr(kv_pair, 'confidence', 1.0)
                        })

            logging.info(f"Successfully extracted text from document. Pages: {len(extracted_data['pages'])}")
            return extracted_data

        except Exception as e:
            logging.error(f"Error extracting text from document: {str(e)}")
            raise

    def get_text_summary(self, extracted_data):
        """
        Get a summary of extracted text for logging/debugging

        Args:
            extracted_data: Output from extract_text_from_document

        Returns:
            str: Summary of extracted content
        """
        summary = f"Document Analysis Summary:\n"
        summary += f"- Total pages: {len(extracted_data.get('pages', []))}\n"
        summary += f"- Total tables: {len(extracted_data.get('tables', []))}\n"
        summary += f"- Key-value pairs: {len(extracted_data.get('key_value_pairs', []))}\n"
        summary += f"- Text length: {len(extracted_data.get('full_text', ''))}\n"

        return summary