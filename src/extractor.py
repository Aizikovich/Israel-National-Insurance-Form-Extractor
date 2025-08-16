import json
import logging
from openai import AzureOpenAI
from config.config import Config


class FieldExtractor:
    def __init__(self):
        """Initialize the field extractor with Azure OpenAI"""
        try:
            Config.validate_config()
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_KEY,
                api_version=Config.AZURE_OPENAI_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
            logging.info("Field Extractor initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Field Extractor: {str(e)}")
            raise

    def get_extraction_prompt(self):
        """Get the system prompt for field extraction"""
        with open("prompt.txt", "r", encoding="utf-8") as file:
            prompt = file.read()
        return prompt.strip()

    def extract_fields(self, ocr_text):
        try:
            # Prepare the text for extraction
            if isinstance(ocr_text, dict):
                text_to_process = ocr_text.get('full_text', '')
                if not text_to_process and ocr_text.get('pages'):
                    # Combine text from all pages
                    text_to_process = '\n'.join([page.get('text', '') for page in ocr_text['pages']])
            else:
                text_to_process = str(ocr_text)

            # Truncate text if too long (GPT-4 token limit consideration)
            if len(text_to_process) > 8000:
                text_to_process = text_to_process[:8000] + "..."

            response = self.client.chat.completions.create(
                model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": self.get_extraction_prompt()},
                    {"role": "user", "content": f"Extract the required fields from this OCR text:\n\n{text_to_process}"}
                ],
                temperature=0,
                max_tokens=2000
            )

            # Extract and parse the JSON response
            response_text = response.choices[0].message.content.strip()

            # Remove markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]

            # Parse JSON
            try:
                extracted_data = json.loads(response_text)
                logging.info("Successfully extracted fields from OCR text")
                return extracted_data
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {e}")
                logging.error(f"Raw response: {response_text}")
                return self._get_empty_structure()

        except Exception as e:
            logging.error(f"Error extracting fields: {str(e)}")
            return self._get_empty_structure()

    def _get_empty_structure(self):

        return {
            "lastName": "",
            "firstName": "",
            "idNumber": "",
            "gender": "",
            "dateOfBirth": {
                "day": "",
                "month": "",
                "year": ""
            },
            "address": {
                "street": "",
                "houseNumber": "",
                "entrance": "",
                "apartment": "",
                "city": "",
                "postalCode": "",
                "poBox": ""
            },
            "landlinePhone": "",
            "mobilePhone": "",
            "jobType": "",
            "dateOfInjury": {
                "day": "",
                "month": "",
                "year": ""
            },
            "timeOfInjury": "",
            "accidentLocation": "",
            "accidentAddress": "",
            "accidentDescription": "",
            "injuredBodyPart": "",
            "signature": "",
            "formFillingDate": {
                "day": "",
                "month": "",
                "year": ""
            },
            "formReceiptDateAtClinic": {
                "day": "",
                "month": "",
                "year": ""
            },
            "medicalInstitutionFields": {
                "healthFundMember": "",
                "natureOfAccident": "",
                "medicalDiagnoses": ""
            }
        }
