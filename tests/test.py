import logging
from config import Config
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential


def get_prompt():
    with open("prompt.txt", "r", encoding="utf-8-sig") as file:
        return file.read().strip()


# test conncetion

def test_connection():
    import os
    from dotenv import load_dotenv
    from openai import AzureOpenAI

    # Load environment variables from .env file
    load_dotenv()

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")

    # Create Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-08-01-preview"  # Adjust if your deployment uses a different version
    )

    # Send test request
    response = client.chat.completions.create(
        model="gpt-4o",  # Replace with your Azure deployment name
        messages=[
            {"role": "system", "content": "You are a witty assistant that tells jokes."},
            {"role": "user", "content": "Tell me a short joke."}
        ],
        max_tokens=50
    )

    # Print the joke
    print(response.choices[0].message.content)


class OCRService:
    def __init__(self):
        """Initialize the OCR service with Azure Document Intelligence"""
        try:
            Config.validate_config()
            self.client = DocumentIntelligenceClient(
                endpoint=Config.DOCUMENT_INTELLIGENCE_ENDPOINT,
                credential=AzureKeyCredential(Config.DOCUMENT_INTELLIGENCE_KEY)
            )
            print("✅ OCR Service initialized successfully")
            logging.info("OCR Service initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize OCR Service: {str(e)}")
            raise

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document using Azure Document Intelligence
        Args:
            file_path: Path to the file (PDF, JPG, PNG, TIFF)
        Returns:
            str: Extracted text
        """
        try:
            with open(file_path, "rb") as f:
                print(f"file type: {f.name.split('.')[-1]}")
                poller = self.client.begin_analyze_document("prebuilt-layout", f)
                result = poller.result()

            # Concatenate recognized text from all lines
            text = []
            for page in result.pages:
                for line in page.lines:
                    text.append(line.content)

            return "\n".join(text)

        except Exception as e:
            logging.error(f"Failed to extract text: {str(e)}")
            raise


def test_ocr_service():
    logging.basicConfig(level=logging.INFO)

    ocr = OCRService()
    extracted_text = ocr.extract_text("sample.pdf")
    print(extracted_text)


def test_ocr_connection():
    Config.validate_config()
    client = DocumentIntelligenceClient(
        endpoint=Config.DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(Config.DOCUMENT_INTELLIGENCE_KEY)
    )
    print("✅ OCR Service initialized successfully")
    logging.info("OCR Service initialized successfully")
    file_path = "eval/sample.pdf"

    with open(file_path, "rb") as f:
        print(f"file type: {f.name.split('.')[-1]}")
        poller = client.begin_analyze_document("prebuilt-layout", f)
        result = poller.result()


import requests


def test_endpoint():
    headers = {
        'Ocp-Apim-Subscription-Key': Config.DOCUMENT_INTELLIGENCE_KEY,
        'Content-Type': 'application/json'
    }

    # Test if the endpoint is reachable
    test_url = f"{Config.DOCUMENT_INTELLIGENCE_ENDPOINT.rstrip('/')}/documentintelligence/documentModels/prebuilt-layout"

    try:
        response = requests.get(test_url, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")




import io

# Mock UploadedFile class


# Example usage for a single file (like accept_multiple_files=False)
# uploaded_file = MockUploadedFile("sample.pdf")

# uploaded_file and uploaded_files[0] behave like Streamlit's UploadedFile
# print(uploaded_file.read())

if __name__ == "__main__":
#     # prompt = get_prompt()
#     # print(prompt, type(prompt))
    test_connection()
#     # test_ocr_connection()
#     test_endpoint()
