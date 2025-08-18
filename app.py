import streamlit as st
import json
import logging
from PIL import Image
from src.ocr_processor import OCRService
from src.extractor import FieldExtractor
from src.validate import DataValidator
from config.config import Config
from translation import translating
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Language translations
TRANSLATIONS = translating
# Page configuration with RTL support
st.set_page_config(
    page_title="National Insurance Form Extractor / מחלץ טפסי ביטוח לאומי",
    page_icon="📋",
    layout="wide"
)


def get_text(key, lang="en"):
    """Get translated text for the given key and language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def set_rtl_css():
    """Add CSS for RTL support when Hebrew is selected"""
    st.markdown("""
    <style>
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .rtl .stSelectbox > label {
        direction: rtl;
        text-align: right;
    }
    .rtl .stFileUploader > label {
        direction: rtl;
        text-align: right;
    }
    .rtl .stButton > button {
        direction: rtl;
    }
    .rtl .stExpanderHeader {
        direction: rtl;
        text-align: right;
    }
    .rtl .stExpanderContent {
        direction: rtl;
        text-align: right;
    }
    .hebrew-text {
        font-family: 'Arial Hebrew', 'Arial', sans-serif;
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)


def init_services():
    """Initialize all services with error handling"""
    try:
        Config.validate_config()
        ocr_service = OCRService()
        field_extractor = FieldExtractor()
        validator = DataValidator()
        logger.info("All services initialized successfully")
        return ocr_service, field_extractor, validator, None
    except Exception as e:
        error_msg = f"Failed to initialize services: {str(e)}"
        logger.error(error_msg)
        return None, None, None, error_msg


def process_uploaded_file(uploaded_file):
    """Process the uploaded file and determine content type"""
    logger.info(f"Processing uploaded file: {uploaded_file.name}")
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


def display_validation_results(validation_results, lang="en"):
    """Display validation results in a user-friendly format"""
    st.subheader(get_text("validation_results", lang))

    # Overall metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            get_text("overall_score", lang),
            f"{validation_results['overall_score']:.1f}%",
            delta=None
        )

    with col2:
        st.metric(
            get_text("completeness", lang),
            f"{validation_results['completeness_score']:.1f}%",
            delta=None
        )

    with col3:
        st.metric(
            get_text("checks_passed", lang),
            f"{validation_results['passed_checks']}/{validation_results['total_checks']}",
            delta=None
        )

    # Summary
    st.info(validation_results['summary'])

    # Detailed results
    with st.expander(get_text("detailed_validation", lang)):
        for result in validation_results['validation_details']:
            status_icon = "✅" if result['valid'] else "❌"
            st.write(f"{status_icon} **{result['field']}**: {result['message']}")
            if result['value']:
                st.write(f"   *Value*: {result['value']}")


def display_extracted_data(data, lang="en"):
    """Display extracted data in a structured format"""
    st.subheader(get_text("extracted_info", lang))
    logger.info("Displaying extracted data")
    if not data:
        logger.warning("No data to display")

    # Personal Information
    with st.expander(get_text("personal_info", lang), expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{get_text('firstName', lang)}:** {data.get('firstName', 'N/A')}")
            st.write(f"**{get_text('lastName', lang)}:** {data.get('lastName', 'N/A')}")
            st.write(f"**{get_text('idNumber', lang)}:** {data.get('idNumber', 'N/A')}")
        with col2:
            st.write(f"**{get_text('gender', lang)}:** {data.get('gender', 'N/A')}")
            dob = data.get('dateOfBirth', {})
            st.write(
                f"**{get_text('dateOfBirth', lang)}:** {dob.get('day', '')}/{dob.get('month', '')}/{dob.get('year', '')}")

    # Address Information
    with st.expander(get_text("address_info", lang)):
        address = data.get('address', {})
        st.write(f"**{get_text('street', lang)}:** {address.get('street', 'N/A')}")
        st.write(f"**{get_text('houseNumber', lang)}:** {address.get('houseNumber', 'N/A')}")
        st.write(f"**{get_text('entrance', lang)}:** {address.get('entrance', 'N/A')}")
        st.write(f"**{get_text('apartment', lang)}:** {address.get('apartment', 'N/A')}")
        st.write(f"**{get_text('city', lang)}:** {address.get('city', 'N/A')}")
        st.write(f"**{get_text('postalCode', lang)}:** {address.get('postalCode', 'N/A')}")
        st.write(f"**{get_text('poBox', lang)}:** {address.get('poBox', 'N/A')}")

    # Contact Information
    with st.expander(get_text("contact_info", lang)):
        st.write(f"**{get_text('landlinePhone', lang)}:** {data.get('landlinePhone', 'N/A')}")
        st.write(f"**{get_text('mobilePhone', lang)}:** {data.get('mobilePhone', 'N/A')}")

    # Accident Information
    with st.expander(get_text("accident_info", lang)):
        st.write(f"**{get_text('jobType', lang)}:** {data.get('jobType', 'N/A')}")

        doi = data.get('dateOfInjury', {})
        st.write(
            f"**{get_text('dateOfInjury', lang)}:** {doi.get('day', '')}/{doi.get('month', '')}/{doi.get('year', '')}")

        st.write(f"**{get_text('timeOfInjury', lang)}:** {data.get('timeOfInjury', 'N/A')}")
        st.write(f"**{get_text('accidentLocation', lang)}:** {data.get('accidentLocation', 'N/A')}")
        st.write(f"**{get_text('accidentAddress', lang)}:** {data.get('accidentAddress', 'N/A')}")
        st.write(f"**{get_text('injuredBodyPart', lang)}:** {data.get('injuredBodyPart', 'N/A')}")

        if data.get('accidentDescription'):
            st.write(f"**{get_text('accidentDescription', lang)}:**")
            st.write(data.get('accidentDescription', 'N/A'))

    # Form Information
    with st.expander(get_text("form_info", lang)):
        st.write(f"**{get_text('signature', lang)}:** {data.get('signature', 'N/A')}")

        ffd = data.get('formFillingDate', {})
        st.write(
            f"**{get_text('formFillingDate', lang)}:** {ffd.get('day', '')}/{ffd.get('month', '')}/{ffd.get('year', '')}")

        frdc = data.get('formReceiptDateAtClinic', {})
        st.write(
            f"**{get_text('formReceiptDateAtClinic', lang)}:** {frdc.get('day', '')}/{frdc.get('month', '')}/{frdc.get('year', '')}")

    # Medical Institution Fields
    with st.expander(get_text("medical_info", lang)):
        medical = data.get('medicalInstitutionFields', {})
        st.write(f"**{get_text('healthFundMember', lang)}:** {medical.get('healthFundMember', 'N/A')}")
        st.write(f"**{get_text('natureOfAccident', lang)}:** {medical.get('natureOfAccident', 'N/A')}")
        st.write(f"**{get_text('medicalDiagnoses', lang)}:** {medical.get('medicalDiagnoses', 'N/A')}")


def main():
    """Main application function"""

    # Language selection in sidebar
    st.sidebar.markdown("### Language / שפה")
    language = st.sidebar.selectbox(
        "Select Language / בחר שפה",
        options=["en", "he"],
        format_func=lambda x: "English" if x == "en" else "עברית",
        index=0
    )

    # Apply RTL CSS if Hebrew is selected
    if language == "he":
        set_rtl_css()
        st.markdown('<div class="rtl hebrew-text">', unsafe_allow_html=True)

    st.title(get_text("title", language))
    st.markdown(f"### {get_text('subtitle', language)}")

    # Initialize services
    with st.spinner(get_text("init_services", language)):
        ocr_service, field_extractor, validator, error = init_services()

    if error:
        st.error(f"{get_text('init_error', language)} {error}")
        st.info(get_text("check_env", language))
        return

    st.success(get_text("init_success", language))

    # File upload
    st.subheader(get_text("upload_title", language))
    uploaded_file = st.file_uploader(
        get_text("upload_help", language),
        type=['pdf', 'jpg', 'jpeg', 'png'],
        help=get_text("upload_help", language)
    )

    if uploaded_file is not None:
        # Display file information
        st.info(f"{get_text('file_info', language)} {uploaded_file.name} ({uploaded_file.size} bytes)")

        # Show image preview for image files
        if uploaded_file.type.startswith('image/'):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", width=900)
                uploaded_file.seek(0)  # Reset file pointer
            except Exception as e:
                st.warning(f"Could not display image preview: {str(e)}")

        # Process button
        if st.button(get_text("extract_btn", language), type="primary"):
            try:
                # Process the file
                with st.spinner(get_text("processing", language)):
                    file_bytes, content_type = process_uploaded_file(uploaded_file)

                # Step 1: OCR Processing
                with st.spinner(get_text("ocr_processing", language)):
                    ocr_result = ocr_service.extract_text_from_document(file_bytes, content_type)
                    text_for_llm = ocr_service.get_content_as_str(ocr_result)
                logger.info(f"Processing uploaded file: {uploaded_file.name}")

                # Step 2: Field Extraction
                with st.spinner(get_text("field_extraction", language)):
                    extracted_data = field_extractor.extract_fields(text_for_llm)
                    st.success(get_text("field_complete", language))
                logger.info("Field extraction completed")

                # Step 3: Validation
                with st.spinner(get_text("validation", language)):
                    validation_results = validator.validate_extracted_data(extracted_data)
                    st.success(get_text("validation_complete", language))
                logger.info("Data validation completed")

                # Display results
                col1, col2 = st.columns([2, 1])

                with col1:
                    display_extracted_data(extracted_data, language)

                with col2:
                    display_validation_results(validation_results, language)

                # JSON Output
                st.subheader(get_text("json_output", language))
                json_str = json.dumps(extracted_data, ensure_ascii=False, indent=2)
                st.code(json_str, language='json')

                # Download button
                st.download_button(
                    label=get_text("download_json", language),
                    data=json_str,
                    file_name=f"extracted_data_{uploaded_file.name}.json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"{get_text('error_processing', language)} {str(e)}")
                logger.error(f"Error in main processing: {str(e)}")

    # Information section
    with st.expander(get_text("about_tool", language)):
        st.markdown(get_text("about_desc", language))

    # Environment check
    with st.expander(get_text("env_status", language)):
        st.write(f"**{get_text('config_status', language)}**")
        try:
            Config.validate_config()
            st.success(get_text("config_success", language))
        except Exception as e:
            st.error(f"{get_text('config_error', language)} {str(e)}")

        st.write(f"**{get_text('required_vars', language)}**")
        st.code("""
                DOCUMENT_INTELLIGENCE_ENDPOINT=your_doc_intel_endpoint
                DOCUMENT_INTELLIGENCE_KEY=your_doc_intel_key
                AZURE_OPENAI_ENDPOINT=your_openai_endpoint
                AZURE_OPENAI_KEY=your_openai_key
                AZURE_OPENAI_VERSION=2024-02-01
                AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
        """)

    # Close RTL div if Hebrew was selected
    if language == "he":
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()