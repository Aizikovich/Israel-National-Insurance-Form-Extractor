# National Insurance Form Extractor

A Streamlit-based application that extracts structured data from Israeli National Insurance Institute (ביטוח לאומי) forms using Azure Document Intelligence OCR and Azure OpenAI GPT-4 for intelligent field extraction.

## Features

- **OCR Processing**: Uses Azure Document Intelligence to extract text from PDF and image files
- **AI-Powered Field Extraction**: Leverages Azure OpenAI GPT-4 to intelligently extract structured information
- **Data Validation**: Comprehensive validation of extracted data including Israeli ID format, phone numbers, and dates
- **Multi-language Support**: Handles both Hebrew and English forms
- **Interactive user Interface**: User-friendly Streamlit interface for file upload and results display
- **JSON Export**: Download extracted data in structured JSON format

## Supported File Formats

- PDF
- JPEG/JPG



## Prerequisites

- Python 3.11
- Azure subscription with:
  - Azure Document Intelligence service
  - Azure OpenAI service with GPT-4 deployment

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aizikovich/Israel-National-Insurance-Form-Extractor.git
   cd Israel-National-Insurance-Form-Extractor
   ```

2. **Create a virtual environment**
   ```bash
   conda create -n nie python=3.11
   conda activate nie
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Azure Document Intelligence
   DOCUMENT_INTELLIGENCE_ENDPOINT=your_document_intelligence_endpoint
   DOCUMENT_INTELLIGENCE_KEY=your_document_intelligence_key

   # Azure OpenAI
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_KEY=your_azure_openai_key
   AZURE_OPENAI_VERSION=2024-02-01
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   ```

## Usage

### Running the Application

1. **Using the run script (recommended)**
   ```bash
   python run.py
   ```

2. **Using Streamlit directly**
   ```bash
   streamlit run app.py
   ```

3. **Access the application**
   
   Open your browser and navigate to `http://localhost:8501`

### Using the Interface

1. Upload a PDF or image file containing a National Insurance form
2. Click "Extract Information" to process the document
3. Review the extracted data and validation results
4. Download the results as JSON if needed

## Project Structure

```
├── app.py                          # Main Streamlit application
├── run.py                          # Application runner script
├── prompt.txt                      # System prompt for field extraction
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── config/
│   └── config.py                  # Configuration management
├── src/
│   ├── ocr_processor.py           # Azure Document Intelligence integration
│   ├── extractor.py               # OpenAI field extraction
│   └── validate.py                # Data validation logic
└── tests/
    ├── test.py                    # Connection and service tests
    └── pipeline.py                # Pipeline testing utilities
```

## Configuration

### Azure Services Setup

1. **Azure Document Intelligence**
   - Create a Document Intelligence resource in Azure Portal
   - Note the endpoint URL and access key

2. **Azure OpenAI**
   - Create an Azure OpenAI resource
   - Deploy a GPT-4 model (recommended: `gpt-4o`)
   - Note the endpoint URL, access key, and deployment name

### Environment Variables

All configuration is managed through environment variables in the `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Azure Document Intelligence endpoint URL | Yes |
| `DOCUMENT_INTELLIGENCE_KEY` | Azure Document Intelligence access key | Yes |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes |
| `AZURE_OPENAI_KEY` | Azure OpenAI access key | Yes |
| `AZURE_OPENAI_VERSION` | Azure OpenAI API version | No (default: 2024-02-01) |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | GPT-4 deployment name | No (default: gpt-4o) |

## Testing

Run the test suite to verify your setup:

```bash
# Test Azure connections
python tests/test.py

# Test the complete pipeline
python tests/pipeline.py
```

## Data Validation

The application includes comprehensive validation for:

- **Israeli ID Numbers**: Format validation
- **Phone Numbers**: Israeli landline and mobile format validation
- **Dates**: Valid date range and format checking
- **Completeness**: Field completion scoring
- **Address**: Street and city requirement validation

## Troubleshooting

### Common Issues

1. **Service Initialization Errors**
   - Verify your `.env` file contains all required variables
   - Check that your Azure services are properly configured
   - Ensure your Azure OpenAI deployment is active

2. **OCR Processing Errors**
   - Check that the file format is supported
   - Ensure the Document Intelligence service has sufficient quota

3. **Field Extraction Issues**
   - Check Azure OpenAI service availability
   - Verify your GPT-4 deployment name is correct
   - Monitor token usage and limits

### Environment Status Check

The application includes an environment status checker in the web interface. Access it through the "Environment Status" expandable section to verify your configuration.

## Extracted Information

The application extracts the following fields from insurance forms:

### Personal Information
- First Name (שם פרטי)
- Last Name (שם משפחה)
- ID Number (ת.ז.)
- Gender (מין)
- Date of Birth (תאריך לידה)

### Address Information
- Street (רחוב)
- House Number (מספר בית)
- Entrance (כניסה)
- Apartment (דירה)
- City (יישוב)
- Postal Code (מיקוד)
- PO Box (תא דואר)

### Contact Information
- Landline Phone (טלפון קווי)
- Mobile Phone (טלפון נייד)

### Accident Information
- Job Type (סוג העבודה)
- Date of Injury (תאריך הפגיעה)
- Time of Injury (שעת הפגיעה)
- Accident Location (מקום התאונה)
- Accident Address (כתובת מקום התאונה)
- Accident Description (נסיבות הפגיעה)
- Injured Body Part (האיבר שנפגע)

### Form Information
- Signature (חתימה)
- Form Filling Date (תאריך מילוי הטופס)
- Form Receipt Date at Clinic (תאריך קבלת הטופס בקופה)

### Medical Institution Fields
- Health Fund Member (חבר בקופת חולים)
- Nature of Accident (מהות התאונה)
- Medical Diagnoses (אבחנות רפואיות)

 