import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from config.config import Config





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
                content_type=content_type,
                features=["keyValuePairs"]
            )

            result = poller.result()
            return result

        except Exception as e:
            logging.error(f"Failed to extract text from document: {str(e)}")
            raise

    def get_content_as_str(self, ocr_result) -> str:
        all_para = [para.content for para in ocr_result['paragraphs']]
        all_pages = [l.content for p in ocr_result['pages'] for l in p.lines]
        # {set(all_para) - set(all_pages)}")
        para_not_in_pages = [x for x in all_para if x not in all_pages]
        all_kv = []

        if ocr_result.key_value_pairs:
            for kv in ocr_result['keyValuePairs']:
                key = kv.key.content.strip() if kv.key else ""
                value = kv.value.content.strip() if kv.value else ""
                if key or value:
                    all_kv.append(f"{key} : {value}")

        all_content = ['*Key-Value Pairs:*'] + all_kv + ['*Pages:*'] + all_pages + [
            '*Paragraphs not in pages:*'] + para_not_in_pages
        all_content_str = "\n".join(all_content)
        return all_content_str

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
