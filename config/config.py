import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()


class Config:
    # Azure Document Intelligence
    DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
    DOCUMENT_INTELLIGENCE_KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2024-02-01")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    # Validation settings
    CONFIDENCE_THRESHOLD = 0.7

    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "DOCUMENT_INTELLIGENCE_ENDPOINT",
            "DOCUMENT_INTELLIGENCE_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_KEY"
        ]

        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        logger.info("Configuration validation completed successfully")
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        return True
