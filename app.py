import streamlit as st
import json
import logging
from PIL import Image
from src.ocr_processor import OCRService
from src.extractor import FieldExtractor
from src.validate import DataValidator
from config.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="National Insurance Form Extractor",
    page_icon="📋",
    layout="wide"
)


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
        print(f"Processing uploaded file: {uploaded_file.name}, Size: {len(file_bytes)}")
        # Determine content type
        if uploaded_file.type == "application/pdf":
            content_type = "application/pdf"
        elif uploaded_file.type in ["image/jpeg", "image/jpg"]:
            content_type = "image/jpeg"
        elif uploaded_file.type == "image/png":
            content_type = "image/png"
        else:
            content_type = "application/pdf"  # Default

        return file_bytes, content_type
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise


def display_validation_results(validation_results):
    """Display validation results in a user-friendly format"""
    st.subheader(" Validation Results")

    # Overall metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Overall Score",
            f"{validation_results['overall_score']:.1f}%",
            delta=None
        )

    with col2:
        st.metric(
            "Completeness",
            f"{validation_results['completeness_score']:.1f}%",
            delta=None
        )

    with col3:
        st.metric(
            "Checks Passed",
            f"{validation_results['passed_checks']}/{validation_results['total_checks']}",
            delta=None
        )

    # Summary
    st.info(validation_results['summary'])

    # Detailed results
    with st.expander("📋 Detailed Validation Results"):
        for result in validation_results['validation_details']:
            status_icon = "✅" if result['valid'] else "❌"
            st.write(f"{status_icon} **{result['field']}**: {result['message']}")
            if result['value']:
                st.write(f"   *Value*: {result['value']}")


def display_extracted_data(data):
    """Display extracted data in a structured format"""
    st.subheader("📄 Extracted Information")
    logger.info("Displaying extracted data")
    if not data:
        logger.warning("No data to display")
    # Personal Information
    with st.expander(" Personal Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**First Name:** {data.get('firstName', 'N/A')}")
            st.write(f"**Last Name:** {data.get('lastName', 'N/A')}")
            st.write(f"**ID Number:** {data.get('idNumber', 'N/A')}")
        with col2:
            st.write(f"**Gender:** {data.get('gender', 'N/A')}")
            dob = data.get('dateOfBirth', {})
            st.write(f"**Date of Birth:** {dob.get('day', '')}/{dob.get('month', '')}/{dob.get('year', '')}")

    # Address Information
    with st.expander("🏠 Address Information"):
        address = data.get('address', {})
        st.write(f"**Street:** {address.get('street', 'N/A')}")
        st.write(f"**House Number:** {address.get('houseNumber', 'N/A')}")
        st.write(f"**Entrance:** {address.get('entrance', 'N/A')}")
        st.write(f"**Apartment:** {address.get('apartment', 'N/A')}")
        st.write(f"**City:** {address.get('city', 'N/A')}")
        st.write(f"**Postal Code:** {address.get('postalCode', 'N/A')}")
        st.write(f"**PO Box:** {address.get('poBox', 'N/A')}")

    # Contact Information
    with st.expander("📞 Contact Information"):
        st.write(f"**Landline Phone:** {data.get('landlinePhone', 'N/A')}")
        st.write(f"**Mobile Phone:** {data.get('mobilePhone', 'N/A')}")

    # Accident Information
    with st.expander("🚨 Accident Information"):
        st.write(f"**Job Type:** {data.get('jobType', 'N/A')}")

        doi = data.get('dateOfInjury', {})
        st.write(f"**Date of Injury:** {doi.get('day', '')}/{doi.get('month', '')}/{doi.get('year', '')}")

        st.write(f"**Time of Injury:** {data.get('timeOfInjury', 'N/A')}")
        st.write(f"**Accident Location:** {data.get('accidentLocation', 'N/A')}")
        st.write(f"**Accident Address:** {data.get('accidentAddress', 'N/A')}")
        st.write(f"**Injured Body Part:** {data.get('injuredBodyPart', 'N/A')}")

        if data.get('accidentDescription'):
            st.write("**Accident Description:**")
            st.write(data.get('accidentDescription', 'N/A'))

    # Form Information
    with st.expander("📋 Form Information"):
        st.write(f"**Signature:** {data.get('signature', 'N/A')}")

        ffd = data.get('formFillingDate', {})
        st.write(f"**Form Filling Date:** {ffd.get('day', '')}/{ffd.get('month', '')}/{ffd.get('year', '')}")

        frdc = data.get('formReceiptDateAtClinic', {})
        st.write(
            f"**Form Receipt Date at Clinic:** {frdc.get('day', '')}/{frdc.get('month', '')}/{frdc.get('year', '')}")

    # Medical Institution Fields
    with st.expander("🏥 Medical Institution Information"):
        medical = data.get('medicalInstitutionFields', {})
        st.write(f"**Health Fund Member:** {medical.get('healthFundMember', 'N/A')}")
        st.write(f"**Nature of Accident:** {medical.get('natureOfAccident', 'N/A')}")
        st.write(f"**Medical Diagnoses:** {medical.get('medicalDiagnoses', 'N/A')}")


def main():
    """Main application function"""
    st.title("📋 National Insurance Form Extractor")
    st.markdown("### Extract structured data from ביטוח לאומי forms using OCR and AI")

    # Initialize services
    with st.spinner("Initializing services..."):
        ocr_service, field_extractor, validator, error = init_services()

    if error:
        st.error(f" Initialization Error: {error}")
        st.info("Please check your environment variables and Azure credentials.")
        return

    st.success(" Services initialized successfully!")

    # File upload
    st.subheader("📎 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF or image file",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        help="Upload a National Insurance Institute form (PDF or image format)"
    )

    if uploaded_file is not None:
        # Display file information
        st.info(f" **File:** {uploaded_file.name} ({uploaded_file.size} bytes)")

        # Show image preview for image files
        if uploaded_file.type.startswith('image/'):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", width=900)
                uploaded_file.seek(0)  # Reset file pointer
            except Exception as e:
                st.warning(f"Could not display image preview: {str(e)}")

        # Process button
        if st.button(" Extract Information", type="primary"):
            try:
                # Process the file
                with st.spinner("Processing uploaded file..."):
                    file_bytes, content_type = process_uploaded_file(uploaded_file)

                # Step 1: OCR Processing
                with st.spinner(" Extracting text using OCR..."):
                    ocr_result = ocr_service.extract_text_from_document(file_bytes, content_type)
                    text_for_llm = ocr_service.get_content_as_str(ocr_result)


                # Step 2: Field Extraction
                with st.spinner(" Extracting structured fields using AI..."):
                    extracted_data = field_extractor.extract_fields(text_for_llm)
                    st.success(" Field extraction completed!")

                # Step 3: Validation
                with st.spinner("🔍 Validating extracted data..."):
                    validation_results = validator.validate_extracted_data(extracted_data)
                    st.success(" Validation completed!")

                # Display results
                col1, col2 = st.columns([2, 1])

                with col1:
                    display_extracted_data(extracted_data)

                with col2:
                    display_validation_results(validation_results)

                # JSON Output
                st.subheader("📤 JSON Output")
                json_str = json.dumps(extracted_data, ensure_ascii=False, indent=2)
                st.code(json_str, language='json')

                # Download button
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"extracted_data_{uploaded_file.name}.json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
                logger.error(f"Error in main processing: {str(e)}")

    # Information section
    with st.expander("ℹ️ About this tool"):
        st.markdown("""
        This tool extracts structured information from Israeli National Insurance Institute (ביטוח לאומי) forms using:

        - **Azure Document Intelligence** for OCR (Optical Character Recognition)
        - **Azure OpenAI GPT-4** for intelligent field extraction
        - **Data validation** to ensure accuracy and completeness

        **Supported formats:** PDF, JPG, JPEG, PNG

        **Supported languages:** Hebrew and English

        The tool extracts personal information, addresses, contact details, accident information, and medical data according to the standard form structure.
        """)

    # Environment check
    with st.expander("🔧 Environment Status"):
        st.write("**Configuration Status:**")
        try:
            Config.validate_config()
            st.success("✅ All environment variables are properly configured")
        except Exception as e:
            st.error(f"❌ Configuration issue: {str(e)}")

        st.write("**Required Environment Variables:**")
        st.code("""
DOCUMENT_INTELLIGENCE_ENDPOINT=your_doc_intel_endpoint
DOCUMENT_INTELLIGENCE_KEY=your_doc_intel_key
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
        """)


if __name__ == "__main__":
    main()