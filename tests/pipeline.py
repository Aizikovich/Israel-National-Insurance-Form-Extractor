import io
import pickle
import streamlit as st
import json
import logging
from io import BytesIO
from PIL import Image
from ocr_processor import OCRService
from extractor import FieldExtractor
from validate import DataValidator
from config import Config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="National Insurance Form Extractor",
    page_icon="📋",
    layout="wide"
)

class MockUploadedFile(io.BytesIO):
    def __init__(self, file_path, name=None):
        with open(file_path, "rb") as f:
            data = f.read()
        super().__init__(data)
        self.name = name or file_path.split("/")[-1]
def init_services():
    """Initialize all services with error handling"""
    try:
        Config.validate_config()
        ocr_service = OCRService()
        field_extractor = FieldExtractor()
        validator = DataValidator()
        return ocr_service, field_extractor, validator, None
    except Exception as e:
        error_msg = f"Failed to initialize services: {str(e)}"
        logger.error(error_msg)
        return None, None, None, error_msg


def process_uploaded_file(uploaded_file):
    """Process the uploaded file and determine content type"""
    try:

        file_bytes = uploaded_file.read()
        print(f"Processing uploaded file: {uploaded_file.name}, Size: {len(file_bytes)}")  # Default
        return file_bytes, 'application/pdf'
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise



def save_ocr_as_pickle():
    """Main application function"""
    # Simulate uploading 'sample.pdf'
    # uploaded_file = MockUploadedFile("sample.pdf", name="sample.pdf")
    # ocr_service, field_extractor, validator, error = init_services()
    # file_bytes, content_type = process_uploaded_file(uploaded_file)
    #
    # # check ocr results
    # ocr_result = ocr_service.extract_text_from_document(file_bytes, content_type)
    # # save AnalyzeResult as pickle file
    # with open("analyze_result.pkl", "wb") as f:
    #     import pickle
    #     pickle.dump(ocr_result, f)

def main():
    # Initialize services
    ocr_service, field_extractor, validator, error = init_services()
    # read analyze_result.pkl

    #  # step 1 get data from OCR
    # with open("analyze_result.pkl", "rb") as f:
    #
    #     ocr_result = pickle.load(f)
    #
    # file_content = []
    # # with open("res.json", "w", encoding="utf-8-sig") as f:
    # #     json.dump(ocr_result.as_dict(), f,indent=4)
    #
    # # step 2 get text from OCR result
    # all_para = [para.content for para in ocr_result['paragraphs']]
    # all_pages = [l.content for p in ocr_result['pages'] for l in p.lines]
    # # {set(all_para) - set(all_pages)}")
    # para_not_in_pages = [x for x in all_para if x not in all_pages]
    # all_kv = []
    #
    # if ocr_result.key_value_pairs:
    #     for kv in ocr_result['keyValuePairs']:
    #         key = kv.key.content.strip() if kv.key else ""
    #         value = kv.value.content.strip() if kv.value else ""
    #         if key or value:
    #             all_kv.append(f"{key} : {value}")
    #
    # all_content = ['*Key-Value Pairs:*'] + all_kv + ['*Pages:*'] + all_pages + [
    #     '*Paragraphs not in pages:*'] + para_not_in_pages
    # all_content_str = "\n".join(all_content)
    # # print(all_content_str)

    # feild extraction
    # print("prompting field extraction with OpenAI...")
    # print(field_extractor.get_extraction_prompt())
    # extracted_fields = field_extractor.extract_fields(all_content_str)
    # print("extracted fields:", extracted_fields)
    # with open("extracted_fields.json", "w", encoding="utf-8-sig") as f:
    #     json.dump(extracted_fields, f, indent=4, ensure_ascii=False)

    # with open("extracted_fields1.json", "w") as f:
    #     json.dump(extracted_fields, f, indent=4)
    # step 3 get fields from LLM
    with open("../eval/extracted_fields1.json", "r") as f:
        extracted_fields = json.load(f)

    val = validator.validate_extracted_data(extracted_fields)
    print("Validation Result:", val)
    # step 4 validate fields

if __name__ == "__main__":
    main()
